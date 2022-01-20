import logging
import math
import torch
from torch.nn.functional import upsample
from torchvision.models import resnet18
import torch.nn as nn
import torch.nn.functional as F
import indexedconv.utils as cvutils
from indexedconv.engine import IndexedConv, IndexedMaxPool2d, IndexedAveragePool2d
from gammalearn.utils import get_camera_layout_from_geom


class SqueezeExcite(nn.Module):
    """Squeeze and excite the output of a convolution as described in the paper https://arxiv.org/abs/1709.01507


    """
    def __init__(self, num_channels, ratio):
        super(SqueezeExcite, self).__init__()
        reducted_channels = int(num_channels / ratio)
        self.reduction = nn.Linear(num_channels, reducted_channels)
        self.expand = nn.Linear(reducted_channels, num_channels)

    def forward(self, x):
        out = x.mean(dim=tuple(range(x.dim())[2:]))

        out = F.relu(self.reduction(out))
        out = torch.sigmoid(self.expand(out))

        out_size = out.size() + tuple(1 for _ in range(x.dim() - 2))
        out = x * out.view(out_size)

        return out


class SelfAttention(nn.Module):
    """Self attention layer as described in the SAGAN paper https://arxiv.org/abs/1805.08318

    """
    def __init__(self, channels, ratio):
        super(SelfAttention, self).__init__()
        self.conv_f = nn.Conv1d(channels, channels // ratio, kernel_size=1, bias=False)
        self.conv_g = nn.Conv1d(channels, channels // ratio, kernel_size=1, bias=False)
        self.conv_h = nn.Conv1d(channels, channels, kernel_size=1, bias=False)

        self.gamma = nn.Parameter(torch.tensor(0.))

    def forward(self, x):
        batch = x.shape[0]
        channel = x.shape[1]
        f = self.conv_f(x.view(batch, channel, -1))
        g = self.conv_g(x.view(batch, channel, -1))
        h = self.conv_h(x.view(batch, channel, -1))

        s = torch.matmul(f.permute(0, 2, 1), g)

        beta = nn.functional.softmax(s, dim=-1)

        o = torch.matmul(beta, h.permute(0, 2, 1)).permute(0, 2, 1)

        return (self.gamma * o.view(x.shape) + x).contiguous()


# TODO check if it  works
class SelfAttention2d(nn.Module):
    """Self attention layer as described in the SAGAN paper https://arxiv.org/abs/1805.08318

    """
    def __init__(self, channels, ratio):
        super(SelfAttention2d, self).__init__()
        self.conv_f = nn.Conv2d(channels, channels // ratio, kernel_size=1, bias=False)
        self.conv_g = nn.Conv2d(channels, channels // ratio, kernel_size=1, bias=False)
        self.conv_h = nn.Conv2d(channels, channels, kernel_size=1, bias=False)

        self.gamma = nn.Parameter(torch.tensor(0.))

    def forward(self, x):
        batch = x.shape[0]
        channel = x.shape[1]
        f = self.conv_f(x.view(batch, channel, -1))
        g = self.conv_g(x.view(batch, channel, -1))
        h = self.conv_h(x.view(batch, channel, -1))

        s = torch.matmul(f.permute(0, 2, 3, 1), g)

        beta = nn.functional.softmax(s, dim=(-2, -1))

        o = torch.matmul(beta, h.permute(0, 2, 3, 1)).permute(0, 2, 3, 1)

        return (self.gamma * o.view(x.shape) + x).contiguous()


class SpatialAttention(nn.Module):
    """
    Spatial attention layer as described in https://arxiv.org/pdf/2001.07645.pdf and implemented in
    https://github.com/sunjesse/shape-attentive-unet/blob/master/models/attention_blocks.py
    """
    def __init__(self, channels):
        super(SpatialAttention, self).__init__()
        self.down = nn.Conv1d(channels, channels // 2, kernel_size=1, bias=False)
        self.phi = nn.Conv1d(channels // 2, 1, kernel_size=1, bias=True)
        self.bn = nn.BatchNorm1d(channels // 2)

        for m in self.modules():
            if isinstance(m, nn.Conv1d):
                n = m.out_channels
                m.weight.data.normal_(0, math.sqrt(2. / n))
            elif isinstance(m, nn.BatchNorm1d):
                m.weight.data.fill_(1)
                m.bias.data.zero_()

    def forward(self, x):
        out = F.relu(self.bn(self.down(x.view(x.shape[0], x.shape[1], -1))))
        out = torch.sigmoid(self.phi(out))
        return out.reshape((x.shape[0], 1,) + x.shape[2:])


class DualAttention(nn.Module):
    """
    Dual attention layer as described in https://arxiv.org/pdf/2001.07645.pdf and implemented in
    https://github.com/sunjesse/shape-attentive-unet/blob/master/models/attention_blocks.py
    """
    def __init__(self, in_channels, ratio):
        super(DualAttention, self).__init__()
        self.se_module = SqueezeExcite(in_channels, ratio)
        self.spa_module = SpatialAttention(in_channels)

    def forward(self, x):
        se = self.se_module(x)
        spa = self.spa_module(x)
        return se * (spa + 1)


class _ResidualLayer(nn.Module):
    def __init__(self, in_features, out_features, index_matrix, downsample=False, pre_act=True, kernel_type='Hex',
                 batch_norm=True, non_linearity=nn.ReLU):
        super(_ResidualLayer, self).__init__()
        self.conv = nn.Sequential()
        if downsample:
            indices_cv1 = cvutils.neighbours_extraction(index_matrix, stride=2)
            self.pooled_matrix = cvutils.pool_index_matrix(index_matrix, kernel_type=kernel_type)
            self.shortcut = nn.Sequential()
            if batch_norm:
                self.shortcut.add_module('bn_shortcut', nn.BatchNorm1d(in_features))
            self.shortcut.add_module(non_linearity.__name__ + '_shortcut', non_linearity())
            self.shortcut.add_module('cv_shortcut', IndexedConv(in_features, out_features, indices_cv1))
        else:
            indices_cv1 = cvutils.neighbours_extraction(index_matrix)
            self.pooled_matrix = index_matrix
            self.shortcut = None

        indices_cv2 = cvutils.neighbours_extraction(self.pooled_matrix)

        if pre_act:
            if batch_norm:
                self.conv.add_module('bn1', nn.BatchNorm1d(in_features))
            self.conv.add_module(non_linearity.__name__ + '1', non_linearity())
        self.conv.add_module('cv1', IndexedConv(in_features, out_features, indices_cv1))
        if batch_norm:
            self.conv.add_module('bn2', nn.BatchNorm1d(out_features))
        self.conv.add_module(non_linearity.__name__ + '2', non_linearity())
        self.conv.add_module('cv2', IndexedConv(out_features, out_features, indices_cv2))

    def forward(self, x):
        new_features = self.conv(x)
        if self.shortcut is not None:
            res = self.shortcut(x)
        else:
            res = x
        return new_features + res


class _ResidualLayerCartesian(nn.Module):
    def __init__(self, in_features, out_features, downsample=False, pre_act=True, batch_norm=True,
                 non_linearity=nn.ReLU):
        super(_ResidualLayerCartesian, self).__init__()
        self.conv = nn.Sequential()
        if downsample:
            self.shortcut = nn.Sequential()
            if batch_norm:
                self.shortcut.add_module('bn_shortcut', nn.BatchNorm2d(in_features))
            self.shortcut.add_module(non_linearity.__name__ + '_shortcut', non_linearity())
            self.shortcut.add_module('cv_shortcut', nn.Conv2d(in_features, out_features, 3, stride=2, padding=1))
        else:
            self.shortcut = None

        if pre_act:
            if batch_norm:
                self.conv.add_module('bn1', nn.BatchNorm2d(in_features))
            self.conv.add_module(non_linearity.__name__ + '1', non_linearity())
        if downsample:
            self.conv.add_module('cv1', nn.Conv2d(in_features, out_features, 3, padding=1, stride=2))
        else:
            self.conv.add_module('cv1', nn.Conv2d(in_features, out_features, 3, padding=1, stride=1))
        if batch_norm:
            self.conv.add_module('bn2', nn.BatchNorm2d(out_features))
        self.conv.add_module(non_linearity.__name__ + '2', non_linearity())
        self.conv.add_module('cv2', nn.Conv2d(out_features, out_features, 3, padding=1))

    def forward(self, x):
        new_features = self.conv(x)
        if self.shortcut is not None:
            res = self.shortcut(x)
        else:
            res = x
        return new_features + res


class _IndexedConvLayer(nn.Sequential):
    def __init__(self, layer_id, index_matrix, num_input, num_output, non_linearity=nn.ReLU,
                 pooling=IndexedAveragePool2d, pooling_kernel='Hex', pooling_radius=1, pooling_stride=2,
                 pooling_dilation=1, pooling_retina=False,
                 batchnorm=True, drop_rate=0, bias=True,
                 kernel_type='Hex', radius=1, stride=1, dilation=1, retina=False):
        super(_IndexedConvLayer, self).__init__()
        self.drop_rate = drop_rate
        indices = cvutils.neighbours_extraction(index_matrix, kernel_type, radius, stride, dilation, retina)
        self.index_matrix = cvutils.pool_index_matrix(index_matrix, kernel_type=pooling_kernel, stride=1)
        self.add_module('cv'+layer_id, IndexedConv(num_input, num_output, indices, bias))
        if pooling is not None:
            p_indices = cvutils.neighbours_extraction(self.index_matrix, pooling_kernel, pooling_radius, pooling_stride,
                                                      pooling_dilation, pooling_retina)
            self.index_matrix = cvutils.pool_index_matrix(self.index_matrix, kernel_type=pooling_kernel,
                                                          stride=pooling_stride)
            self.add_module('pool'+layer_id, pooling(p_indices))
        if batchnorm:
            self.add_module('bn'+layer_id, nn.BatchNorm1d(num_output))
        if non_linearity is not None:
            self.add_module(non_linearity.__name__ + layer_id, non_linearity())

    def forward(self, x):
        new_features = super(_IndexedConvLayer, self).forward(x)
        if self.drop_rate > 0:
            new_features = F.dropout(new_features, p=self.drop_rate, training=self.training)
        return new_features


class _Regressor(nn.Module):
    def __init__(self, tasks_name, tasks_output, num_features, num_layers, factor, non_linearity=nn.ReLU,
                 batchnorm=True, drop_rate=0):
        super(_Regressor, self).__init__()
        for i, (task, output) in enumerate(zip(tasks_name, tasks_output)):
            t = nn.Sequential()
            for l in range(1, num_layers):
                if l == 1:
                    t.add_module('lin' + str(l) + '_' + task, nn.Linear(num_features, num_features // factor))
                else:
                    t.add_module('lin' + str(l) + '_' + task, nn.Linear(num_features // ((l - 1) * factor),
                                                                        num_features // (l * factor)))
                if batchnorm:
                    t.add_module('bn' + str(l) + '_' + task, nn.BatchNorm1d(num_features // (l * factor)))
                t.add_module(non_linearity.__name__ + str(l) + '_' + task, non_linearity())

                if drop_rate > 0:
                    t.add_module('drop' + str(l) + '_' + task, nn.Dropout(p=drop_rate))
            if num_layers > 1:
                t.add_module('output_' + task, nn.Linear(num_features // ((num_layers - 1) * factor), output))
            else:
                t.add_module('output_' + task, nn.Linear(num_features, output))
            self.add_module(task, t)

    def forward(self, x):
        out = []
        for t in self.children():
            out.append(t(x))
        return torch.cat(out, dim=1)


class GammaPhysNet(nn.Module):
    """
        Gamma-PhysNet with ResNet like Network with indexed convolutions as backbone.
        Please cite and see details: https://www.scitepress.org/Link.aspx?doi=10.5220/0010297405340544 
        Backbone based on https://arxiv.org/abs/1603.05027, CIFAR version
        full pre-activation
    """

    def __init__(self, net_parameters_dic, camera_geometry):
        """

        Parameters
        ----------
        net_parameters_dic (dict): a dictionary describing the parameters of the network
        camera_geometry (CameraGeometry)
        """
        super(GammaPhysNet, self).__init__()
        self.logger = logging.getLogger(__name__ + '.GammaPhysNet')

        index_matrix0, camera_layout = get_camera_layout_from_geom(camera_geometry)

        num_layers = net_parameters_dic['num_layers']
        num_channels = [net_parameters_dic['num_channels']]
        attention = net_parameters_dic['attention_layer']
        num_channels.extend(net_parameters_dic['block_features'])
        fc_width = net_parameters_dic['fc_width']
        non_linearity = net_parameters_dic['non_linearity']
        last_bias_init = net_parameters_dic['last_bias_init']

        if 'class' in net_parameters_dic['targets'].keys():
            num_class = net_parameters_dic['targets']['class']
        else:
            num_class = 0
        regressor = {t: net_parameters_dic['targets'][t] for t in net_parameters_dic['targets'].keys() if
                     t != 'class'}
        if len(regressor) == 0:
            regressor = None
        if 'init' in net_parameters_dic.keys():
            init = net_parameters_dic['init']
        else:
            init = 'kaiming'
        if 'batch_norm' in net_parameters_dic.keys():
            batch_norm = net_parameters_dic['batch_norm']
        else:
            batch_norm = True

        # ResNet backbone
        self.feature = nn.Sequential()

        # Layer 0
        indices_conv0 = cvutils.neighbours_extraction(index_matrix0,
                                                      kernel_type=camera_layout)
        self.feature.add_module('cv0', IndexedConv(num_channels[0], 16, indices_conv0))
        self.feature.add_module(non_linearity.__name__ + '0', non_linearity())
        # Rearrange index matrix
        index_matrix1 = cvutils.pool_index_matrix(index_matrix0, stride=1, kernel_type=camera_layout)

        # blocks
        for i, (n_in, n_out) in enumerate(zip(num_channels[:-1], num_channels[1:])):
            if i == 0:
                for n in range(1, num_layers + 1):
                    if n == 1:
                        self.feature.add_module('block' + str(i) + '_layer' + str(n),
                                                _ResidualLayer(n_out, n_out, index_matrix1, pre_act=False,
                                                               batch_norm=batch_norm, non_linearity=non_linearity))
                    else:
                        self.feature.add_module('block' + str(i) + '_layer' + str(n),
                                                _ResidualLayer(n_out, n_out, index_matrix1,
                                                               batch_norm=batch_norm, non_linearity=non_linearity))
            else:
                for n in range(1, num_layers + 1):
                    if n == 1:
                        layer = _ResidualLayer(n_in, n_out, index_matrix1, downsample=True, batch_norm=batch_norm,
                                               non_linearity=non_linearity)
                        self.feature.add_module('block' + str(i) + '_layer' + str(n), layer)
                        index_matrix1 = layer.pooled_matrix
                    else:
                        self.feature.add_module('block' + str(i) + '_layer' + str(n),
                                                _ResidualLayer(n_out, n_out, index_matrix1,
                                                               batch_norm=batch_norm, non_linearity=non_linearity))
            if attention is not None:
                self.feature.add_module('attention_block' + str(i), attention[0](n_out, **attention[1]))

        self.feature.add_module('last_' + non_linearity.__name__, non_linearity())

        # Compute the number of pixels (where idx is not -1 in the index matrix) of the last features
        n_pixels = int(torch.sum(torch.ge(index_matrix1[0, 0], 0)).data)
        self.logger.info('num pixels after last pooling : {}'.format(n_pixels))

        # Multitasking block
        if regressor is not None:
            if 'energy' in regressor:
                self.energy = nn.Sequential()
                self.energy.add_module('en_layer1', nn.Linear(num_channels[-1], fc_width))
                self.energy.add_module(non_linearity.__name__ + '1', non_linearity())
                self.energy.add_module('en_out', nn.Linear(fc_width, regressor['energy']))
                if last_bias_init is not None and 'energy' in last_bias_init:
                    self.energy.en_out.bias = nn.Parameter(torch.tensor(last_bias_init['energy']))
            else:
                self.energy = None
            if 'impact' in regressor or 'direction' in regressor:
                self.fusion = nn.Linear(n_pixels * num_channels[-1], fc_width)
                if 'impact' in regressor:
                    self.impact = nn.Linear(fc_width, regressor['impact'])
                    if last_bias_init is not None and 'impact' in last_bias_init:
                        self.impact.bias = nn.Parameter(torch.tensor(last_bias_init['impact']))
                else:
                    self.impact = None
                if 'direction' in regressor:
                    self.direction = nn.Linear(fc_width, regressor['direction'])
                    if last_bias_init is not None and 'direction' in last_bias_init:
                        self.direction.bias = nn.Parameter(torch.tensor(last_bias_init['direction']))
                else:
                    self.direction = None
            else:
                self.fusion = None
        else:
            self.energy = None
            self.fusion = None
            self.direction = None
            self.impact = None
        if num_class > 0:
            self.classifier = nn.Linear(n_pixels * num_channels[-1], num_class)
            if last_bias_init is not None and 'class' in last_bias_init:
                self.classifier.bias = nn.Parameter(torch.tensor(last_bias_init['class']))
        else:
            self.classifier = None

        self.non_linearity = non_linearity()

        for m in self.modules():
            if isinstance(m, IndexedConv):
                if init == 'orthogonal':
                    nn.init.orthogonal_(m.weight)
                elif init == 'kaiming':
                    nn.init.kaiming_uniform_(m.weight, mode='fan_out')
                else:
                    self.logger.warning('Unknown initialization, use default one')

    def forward(self, x):
        out = self.feature(x)
        out_e = torch.mean(out, 2)  # Global average pooling
        out = out.view(out.size(0), -1)
        out_tot = {}
        if self.energy is not None:
            out_tot['energy'] = self.energy(out_e)
        if self.fusion is not None:
            out_f = self.non_linearity(self.fusion(out))
            if self.impact is not None:
                out_tot['impact'] = self.impact(out_f)
            if self.direction is not None:
                out_tot['direction'] = self.direction(out_f)
        if self.classifier is not None:
            out_tot['class'] = nn.LogSoftmax(1)(self.classifier(out))
        return out_tot


class GammaPhysNetCartesian(nn.Module):
    """
        Gamma-PhysNet with ResNet like Network with indexed convolutions as backbone.
        Please cite and see details: https://www.scitepress.org/Link.aspx?doi=10.5220/0010297405340544
        Backbone based on https://arxiv.org/abs/1603.05027, CIFAR version
        full pre-activation
    """

    def __init__(self, net_parameters_dic, *args, **kwargs):
        """

        Parameters
        ----------
        net_parameters_dic (dict): a dictionary describing the parameters of the network
        camera_parameters (dict): a dictionary containing the parameters of the camera used with this network
        """
        super(GammaPhysNetCartesian, self).__init__()
        self.logger = logging.getLogger(__name__ + '.GammaPhysNetCartesian')

        num_layers = net_parameters_dic['num_layers']
        num_channels = [net_parameters_dic['num_channels']]
        attention = net_parameters_dic['attention_layer']
        num_channels.extend(net_parameters_dic['block_features'])
        fc_width = net_parameters_dic['fc_width']
        non_linearity = net_parameters_dic['non_linearity']
        last_bias_init = net_parameters_dic['last_bias_init']

        if 'class' in net_parameters_dic['targets'].keys():
            num_class = net_parameters_dic['targets']['class']
        else:
            num_class = 0
        regressor = {t: net_parameters_dic['targets'][t] for t in net_parameters_dic['targets'].keys() if
                     t != 'class'}
        if len(regressor) == 0:
            regressor = None
        if 'init' in net_parameters_dic.keys():
            init = net_parameters_dic['init']
        else:
            init = 'kaiming'
        if 'batch_norm' in net_parameters_dic.keys():
            batch_norm = net_parameters_dic['batch_norm']
        else:
            batch_norm = True

        # ResNet backbone
        self.feature = nn.Sequential()

        # Layer 0
        self.feature.add_module('cv0', nn.Conv2d(num_channels[0], 16, 3, padding=1))
        self.feature.add_module(non_linearity.__name__ + '0', non_linearity())

        # blocks
        for i, (n_in, n_out) in enumerate(zip(num_channels[:-1], num_channels[1:])):
            if i == 0:
                for n in range(1, num_layers + 1):
                    if n == 1:
                        self.feature.add_module('block' + str(i) + '_layer' + str(n),
                                                _ResidualLayerCartesian(n_out, n_out, pre_act=False,
                                                                        batch_norm=batch_norm,
                                                                        non_linearity=non_linearity))
                    else:
                        self.feature.add_module('block' + str(i) + '_layer' + str(n),
                                                _ResidualLayerCartesian(n_out, n_out,
                                                                        batch_norm=batch_norm,
                                                                        non_linearity=non_linearity))
            else:
                for n in range(1, num_layers + 1):
                    if n == 1:
                        layer = _ResidualLayerCartesian(n_in, n_out, downsample=True, batch_norm=batch_norm,
                                                        non_linearity=non_linearity)
                        self.feature.add_module('block' + str(i) + '_layer' + str(n), layer)
                    else:
                        self.feature.add_module('block' + str(i) + '_layer' + str(n),
                                                _ResidualLayerCartesian(n_out, n_out,
                                                                        batch_norm=batch_norm,
                                                                        non_linearity=non_linearity))
            if attention is not None:
                self.feature.add_module('attention_block' + str(i), attention[0](n_out, **attention[1]))

        self.feature.add_module('last_' + non_linearity.__name__, non_linearity())
        self.adaptive_pooling = nn.AdaptiveAvgPool2d((14, 14))
        self.feature.add_module('adaptive_pooling2D', self.adaptive_pooling)

        # Compute the number of pixels (where idx is not -1 in the index matrix) of the last features
        n_pixels = 14*14
        self.logger.info('num pixels after last pooling : {}'.format(n_pixels))

        # Multitasking block
        if regressor is not None:
            if 'energy' in regressor:
                self.energy = nn.Sequential()
                self.energy.add_module('en_layer1', nn.Linear(num_channels[-1], fc_width))
                self.energy.add_module(non_linearity.__name__ + '1', non_linearity())
                self.energy.add_module('en_out', nn.Linear(fc_width, regressor['energy']))
                if last_bias_init is not None and 'energy' in last_bias_init:
                    self.energy.en_out.bias = nn.Parameter(torch.tensor(last_bias_init['energy']))
            else:
                self.energy = None
            if 'impact' in regressor or 'direction' in regressor:
                self.fusion = nn.Linear(n_pixels * num_channels[-1], fc_width)
                if 'impact' in regressor:
                    self.impact = nn.Linear(fc_width, regressor['impact'])
                    if last_bias_init is not None and 'impact' in last_bias_init:
                        self.impact.bias = nn.Parameter(torch.tensor(last_bias_init['impact']))
                else:
                    self.impact = None
                if 'direction' in regressor:
                    self.direction = nn.Linear(fc_width, regressor['direction'])
                    if last_bias_init is not None and 'direction' in last_bias_init:
                        self.direction.bias = nn.Parameter(torch.tensor(last_bias_init['direction']))
                else:
                    self.direction = None
            else:
                self.fusion = None
        else:
            self.energy = None
            self.fusion = None
            self.direction = None
            self.impact = None
        if num_class > 0:
            self.classifier = nn.Linear(n_pixels * 64, num_class)
            if last_bias_init is not None and 'class' in last_bias_init:
                self.classifier.bias = nn.Parameter(torch.tensor(last_bias_init['class']))
        else:
            self.classifier = None

        self.non_linearity = non_linearity()

        for m in self.modules():
            if isinstance(m, IndexedConv):
                if init == 'orthogonal':
                    nn.init.orthogonal_(m.weight)
                elif init == 'kaiming':
                    nn.init.kaiming_uniform_(m.weight, mode='fan_out')
                else:
                    self.logger.warning('Unknown initialization, use default one')

    def forward(self, x):
        out = self.feature(x)
        out_e = torch.mean(out, dim=tuple(range(out.dim())[2:]))  # Global average pooling
        out = out.view(out.size(0), -1)
        out_tot = {}
        if self.energy is not None:
            out_tot['energy'] = self.energy(out_e)
        if self.fusion is not None:
            out_f = self.non_linearity(self.fusion(out))
            if self.impact is not None:
                out_tot['impact'] = self.impact(out_f)
            if self.direction is not None:
                out_tot['direction'] = self.direction(out_f)
        if self.classifier is not None:
            out_tot['class'] = nn.LogSoftmax(1)(self.classifier(out))
        return out_tot


class ConvAutoEncoder(nn.Module):
    def __init__(self, net_parameters_dic, camera_geometry, mode='train'):
        super(ConvAutoEncoder, self).__init__()
        self.logger = logging.getLogger(__name__ + '.GLNetIndexConv42')
        self.targets = net_parameters_dic['targets']

        # encoder layers
        # conv layer (depth from 2 --> 16), 3x3 kernels
        self.conv1 = nn.Conv2d(2, 16, 3, padding=1)
        self.relu1 = nn.ReLU()
        self.pool1 = nn.MaxPool2d(2, 2)
        # conv layer (depth from 16 --> 8), 3x3 kernels
        self.conv2 = nn.Conv2d(16, 4, 3, padding=1)
        self.relu2 = nn.ReLU()
        self.pool2 = nn.MaxPool2d(2, 2)

        # decoder layers
        self.upsample1 = nn.Upsample(scale_factor=2, mode='nearest')
        self.conv3 = nn.Conv2d(4, 16, 3, padding=1)
        self.relu3 = nn.ReLU()

        self.upsample2 = nn.Upsample(scale_factor=2, mode='nearest')
        self.conv4 = nn.Conv2d(16, 2, 3, padding=1)

    def forward(self, x):
        # encoder
        x = self.conv1(x)
        x = self.relu1(x)
        x = self.pool1(x)

        x = self.conv2(x)
        x = self.relu2(x)
        x = self.pool2(x)  # compressed representation

        # decoder
        x = self.upsample1(x)
        x = self.conv3(x)
        x = self.relu3(x)

        x = self.upsample2(x)
        x = self.conv4(x)

        return x


class GLNetIndexConv42(nn.Module):
    """
        Network with indexed convolutions and pooling.
        4 CL (after each conv layer, pooling is executed)
        2 FC
    """
    def __init__(self, net_parameters_dic, camera_geometry, mode='train'):
        """
        Parameters
        ----------
        net_parameters_dic (dict): a dictionary describing the parameters of the network
        camera_parameters (dict): a dictionary containing the parameters of the camera used with this network
        mode (str): explicit mode to use the network (different from the nn.Module.train() or evaluate()). For GANs
        """
        super(GLNetIndexConv42, self).__init__()
        self.logger = logging.getLogger(__name__ + '.GLNetIndexConv42')
        self.targets = net_parameters_dic['targets']

        index_matrix1, camera_layout = get_camera_layout_from_geom(camera_geometry)
        pooling_kernel = camera_layout

        # Channels
        num_outputs = sum(net_parameters_dic['targets'].values())
        self.num_channel = n1 = net_parameters_dic['num_channels']
        n_features = net_parameters_dic['n_features']
        n2 = n_features*2
        n3 = n2*2
        n4 = n3 * 2

        self.drop_rate = net_parameters_dic['drop_rate']

        # Layer 1 : IndexedConv
        indices_conv1 = cvutils.neighbours_extraction(index_matrix1,
                                                      kernel_type=camera_layout)
        # After the first convolution we need to reorganize the index matrix
        index_matrix1 = cvutils.pool_index_matrix(index_matrix1, kernel_type=pooling_kernel, stride=1)
        indices_pool1 = cvutils.neighbours_extraction(index_matrix1, kernel_type=pooling_kernel, stride=2)
        self.cv1 = IndexedConv(n1, n_features, indices_conv1)
        self.max_pool1 = IndexedMaxPool2d(indices_pool1)
        self.relu1 = nn.ReLU()
        self.bn1 = nn.BatchNorm1d(n_features)

        # Layer 2 : IndexedConv
        index_matrix2 = cvutils.pool_index_matrix(index_matrix1, kernel_type=pooling_kernel, stride=2)
        indices_conv2 = cvutils.neighbours_extraction(index_matrix2,
                                                      kernel_type=camera_layout)
        indices_pool2 = cvutils.neighbours_extraction(index_matrix2, kernel_type=pooling_kernel, stride=2)
        self.cv2 = IndexedConv(n_features, n2, indices_conv2)
        self.max_pool2 = IndexedMaxPool2d(indices_pool2)
        self.relu2 = nn.ReLU()
        self.bn2 = nn.BatchNorm1d(n2)

        # Layer 3 : IndexedConv
        index_matrix3 = cvutils.pool_index_matrix(index_matrix2, kernel_type=pooling_kernel, stride=2)
        indices_conv3 = cvutils.neighbours_extraction(index_matrix3,
                                                      kernel_type=camera_layout)
        indices_pool3 = cvutils.neighbours_extraction(index_matrix3, kernel_type=pooling_kernel, stride=2)
        self.cv3 = IndexedConv(n2, n3, indices_conv3)
        self.max_pool3 = IndexedMaxPool2d(indices_pool3)
        self.relu3 = nn.ReLU()
        self.bn3 = nn.BatchNorm1d(n3)

        # Layer 4 : IndexedConv
        index_matrix4 = cvutils.pool_index_matrix(index_matrix3, kernel_type=pooling_kernel, stride=2)
        indices_conv4 = cvutils.neighbours_extraction(index_matrix4,
                                                      kernel_type=camera_layout)
        indices_pool4 = cvutils.neighbours_extraction(index_matrix4, kernel_type=pooling_kernel, stride=2)
        self.cv4 = IndexedConv(n3, n4, indices_conv4)
        self.max_pool4 = IndexedMaxPool2d(indices_pool4)
        self.relu4 = nn.ReLU()
        self.bn4 = nn.BatchNorm1d(n4)

        index_matrix5 = cvutils.pool_index_matrix(index_matrix4, kernel_type=pooling_kernel, stride=2)

        # Compute the number of pixels (where idx is not -1 in the index matrix) of the last features
        n_pixels = int(torch.sum(torch.ge(index_matrix5[0, 0], 0)).data)
        self.logger.debug('num pixels after last conv : {}'.format(n_pixels))

        self.lin1 = nn.Linear(n_pixels*n4, (n_pixels*n4) // 2)
        self.relu5 = nn.ReLU()
        self.bn5 = nn.BatchNorm1d((n_pixels*n4) // 2)

        self.lin2 = nn.Linear((n_pixels*n4)//2, num_outputs)

        for m in self.modules():
            if isinstance(m, IndexedConv):
                nn.init.kaiming_uniform_(m.weight.data, mode='fan_out')

    def forward(self, x):
        drop = nn.Dropout(p=self.drop_rate)
        out_conv = []
        # In case of stereo, average convolutions output per telescope
        for i in range(int(x.shape[-2] / self.num_channel)):
            out = self.cv1(x[..., i*self.num_channel:(i+1)*self.num_channel, :])
            out = self.max_pool1(out)
            out = self.bn1(out)
            out = drop(self.relu1(out))
            out = self.cv2(out)
            out = self.max_pool2(out)
            out = self.bn2(out)
            out = drop(self.relu2(out))
            out = self.cv3(out)
            out = self.max_pool3(out)
            out = self.bn3(out)
            out = drop(self.relu3(out))
            out = self.cv4(out)
            out = self.max_pool4(out)
            out = self.bn4(out)
            out_conv.append(drop(self.relu4(out)))
        out = torch.stack(out_conv, 1)
        out = out.mean(1)
        out = out.view(out.size(0), -1)
        out = self.lin1(out)
        out = self.bn5(out)
        out = drop(self.relu5(out))

        out_linear2 = self.lin2(out)
        i = 0
        output = {}
        for t, v in self.targets.items():
            if t == 'class':
                output[t] = nn.LogSoftmax(1)(out_linear2[:, i:i + v])
            else:
                output[t] = out_linear2[:, i:i+v]
            i += v

        return output


class ResNet18MT(nn.Module):
    """
        ResNet18 for multitask IACT reco
    """
    def __init__(self, net_parameters_dic, camera_geometry):
        """
        Parameters
        ----------
        net_parameters_dic (dict): a dictionary describing the parameters of the network
        camera_parameters (dict): a dictionary containing the parameters of the camera used with this network
        mode (str): explicit mode to use the network (different from the nn.Module.train() or evaluate()). For GANs
        """
        super(ResNet18MT, self).__init__()
        self.logger = logging.getLogger(__name__ + '.ResNet18MT')
        self.targets = net_parameters_dic['targets']

        self.model = resnet18(pretrained=False)

        # Channels
        num_outputs = sum(net_parameters_dic['targets'].values())
        num_channel = net_parameters_dic['num_channels']
        self.model.conv1 = torch.nn.Conv2d(num_channel, 64, kernel_size=(3, 3), padding=(1, 1))
        self.drop_rate = net_parameters_dic['drop_rate']
        self.model.fc = nn.Linear(512, 256)
        self.relu5 = nn.ReLU()
        self.bn5 = nn.BatchNorm1d(256)
        self.lin2 = nn.Linear(256, num_outputs)

        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_uniform_(m.weight.data, mode='fan_out')

    def forward(self, x):
        drop = nn.Dropout(p=self.drop_rate)
        out = self.model(x)
        out = self.bn5(out)
        out = drop(self.relu5(out))

        out_linear2 = self.lin2(out)
        i = 0
        output = {}
        for t, v in self.targets.items():
            if t == 'class':
                output[t] = nn.LogSoftmax(1)(out_linear2[:, i:i + v])
            else:
                output[t] = out_linear2[:, i:i+v]
            i += v

        return output
