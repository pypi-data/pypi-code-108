import torch
from torch.autograd import Function
import copy

import numpy as np
from skimage.transform import resize
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import indexedconv.utils as ic_utils
from ctapipe.instrument import CameraGeometry
import astropy.units as u

from gammalearn import utils as utils


# Utils
class IndexedUnpool(torch.nn.Module):
    """
    Unpool images based on indices used to pool the images in a first place.
    """
    def __init__(self, indices):
        super(IndexedUnpool, self).__init__()
        position_per_pixel = [
            torch.where(indices == i)[1] for i in torch.unique(indices) if i != -1
        ]

        max_position_per_pixel = np.max([len(p) for p in position_per_pixel])
        self.indices = torch.full((len(position_per_pixel), max_position_per_pixel), -1.)
        for i, pos in enumerate(position_per_pixel):
            for j, p in enumerate(pos):
                self.indices[i, j] = p
            # We duplicate the data if the unpooled pixel was use less than the max during the pooling
            if j < max_position_per_pixel:
                self.indices[i, j + 1:] = self.indices[i, j]

    def forward(self, x):
        out = x[..., self.indices.long()]
        return out.mean(-1)


def reorganize_hexagonal_pixels(image, in_matrix, out_matrix):
    """
    Reorganize pixels in a vectorized image relying on the present and the desired index matrices.

    Parameters
    ----------
    image (tensor): vectorized image to reorganize
    in_matrix (tensor): index matrix corresponding to the input image
    out_matrix (tensor): indexed matrix corresponding to the desired reorganization

    Returns
    -------
    The reorganized image
    """
    inj_table = np.full(image.shape[-1], -1)
    for i in range(out_matrix.shape[2]):
        for j in range(out_matrix.shape[3]):
            out_ind = out_matrix[0, 0, i, j].long()
            if out_ind > -1:
                inj_table[out_ind] = in_matrix[0, 0, i, j].long()
    return image[..., inj_table]


def resize_hexagonal_image(feature, net, camera_geometry):
    """Upsize the feature maps of a network implemented with indexed convolutions to the input size.

    Parameters
    ----------
    feature (tensor): image to reorganize
    net (nn.Module): network implemented with indexed convolutions
    camera_geometry (`ctapipe.instrument.CameraGeometry`): contains information about the camera frame

    Returns
    -------
    Upsized features

    """
    # Index matrix of the images that fed the network

    initial_matrix, _ = utils.get_camera_layout_from_geom(camera_geometry)

    # Look for index matrices in the backbone of the net
    matrices = [
        child.pooled_matrix
        for child in net.feature.children()
        if hasattr(child, 'pooled_matrix')
    ]

    matrix_set = set(matrices)
    # Sort matrices by size
    sorted_matrices = list(matrix_set)
    sorted_matrices.sort(key=lambda x: torch.tensor(x.shape).prod())

    for matrix in sorted_matrices[1:]:
        if matrix.ge(0).sum() > feature.shape[-1]:
            indices = ic_utils.neighbours_extraction(matrix, stride=2)
            unpool = IndexedUnpool(indices)
            feature = unpool(feature)

    return reorganize_hexagonal_pixels(feature, matrices[0], initial_matrix)


class SaveOutput:
    def __init__(self):
        self.outputs = []

    def __call__(self, module, module_in, module_out):
        self.outputs.append(module_out.detach().to('cpu'))

    def clear(self):
        self.outputs = []


# Saliency maps
class OpenBlackBox:
    """Base class for network analysis methods"""

    def __init__(self, net, class_index=0, cuda=True, camera_geometry=CameraGeometry.from_name('LSTCam')):

        self.device = torch.device('cuda') if cuda else torch.device('cpu')
        self.class_index = class_index

        self.camera_geometry = camera_geometry
        self.net = copy.deepcopy(net)
        self.image = None
        self.true_signal = None
        self.activations = {}
        self.activations_max = {}

        self.net.to(self.device)

    def __call__(self, image):
        raise NotImplementedError

    @staticmethod
    def _blend_on_image(img, activation):
        if img.dim() == 2:
            heatmap = plt.cm.jet(activation)[:, :, :-1]
            img_norm = Normalize(vmin=img.min(), vmax=img.max())(img)
            img_map = plt.cm.magma_r(img_norm)[:, :, :-1]
            mask = np.array([activation, activation, activation], dtype=np.float64).transpose(1, 2, 0)
        elif img.dim() == 1:
            heatmap = plt.cm.jet(activation)[:, :-1]
            img_norm = Normalize(vmin=img.min(), vmax=img.max())(img)
            img_map = plt.cm.magma_r(img_norm)[:, :-1]
            mask = np.array([activation, activation, activation], dtype=np.float64).transpose(1, 0)
        else:
            print('Unknown image dimension, should be 1 or 2')
            raise ValueError
        heatmap *= mask
        img_map *= (1 - mask)
        return heatmap + img_map

    def _prepare_activation(self, activation, image, threshold=0.08, blend=True):
        activ = np.copy(activation)
        activ -= activ.min()
        activ /= activ.max()
        limit = (activ.max() - activ.min()) * threshold + activ.min()
        if blend:
            activ[activ < limit] = 0
            activ = self._blend_on_image(image, activ)
        else:
            activ[activ < limit] = -1
            m_jet = copy.copy(plt.cm.jet)
            m_jet.set_under('lightgrey')
            activ = m_jet(activ)

        return activ

    def plot_activation(self, tasks=None, threshold=0.0, blend=True, pixel_size=10, normalize=True, cmap=None):
        if cmap is not None:
            plt.set_cmap(cmap)
        elif plt.get_cmap() != plt.cm.magma_r:
            plt.set_cmap(plt.cm.magma_r)
        if tasks is None:
            tasks = self.activations.keys()

        col_true_signal = 1 if self.true_signal is not None else 0

        f, axes = plt.subplots(2, 1 + len(tasks) + col_true_signal, figsize=(4 + 3 * (len(tasks) + col_true_signal), 6))

        if self.image.dim() == 3:
            im = axes[0, 0].imshow(self.image[0])
            peak = axes[1, 0].imshow(self.image[1])
        elif self.image.dim() == 2:
            im = axes[0, 0].scatter(self.camera_geometry.pix_x,
                                    self.camera_geometry.pix_y,
                                    s=pixel_size,
                                    c=self.image[0],
                                    marker=(6, 0, 0))
            axes[0, 0].axis('equal')
            peak = axes[1, 0].scatter(self.camera_geometry.pix_x,
                                      self.camera_geometry.pix_y,
                                      s=pixel_size,
                                      c=self.image[1],
                                      marker=(6, 0, 0))
            axes[1, 0].axis('equal')
        else:
            print('Unknown image dimension, should be 2 or 3')
            raise ValueError

        axes[0, 0].set_title('Charge')
        f.colorbar(im, ax=axes[0, 0])
        axes[1, 0].set_title('Peak position')
        f.colorbar(peak, ax=axes[1, 0])

        if self.true_signal is not None:
            if self.true_signal.dim() == 3:
                im = axes[0, 1].imshow(self.true_signal[0])
                peak = axes[1, 1].imshow(self.true_signal[1])
            elif self.true_signal.dim() == 2:
                im = axes[0, 1].scatter(self.camera_geometry.pix_x,
                                        self.camera_geometry.pix_y,
                                        s=pixel_size,
                                        c=self.true_signal[0],
                                        marker=(6, 0, 0))
                axes[0, 1].axis('equal')
                peak = axes[1, 1].scatter(self.camera_geometry.pix_x,
                                          self.camera_geometry.pix_y,
                                          s=pixel_size,
                                          c=self.true_signal[1],
                                          marker=(6, 0, 0))
                axes[1, 1].axis('equal')
            else:
                print('Unknown image dimension, should be 2 or 3')
                raise ValueError

            axes[0, 1].set_title('True Charge')
            f.colorbar(im, ax=axes[0, 1])
            axes[1, 1].set_title('True Peak position')
            f.colorbar(peak, ax=axes[1, 1])

        m_jet = copy.copy(plt.cm.jet)
        m_jet.set_under('lightgrey')
        plt.set_cmap(m_jet)
        for i, task in enumerate(tasks, start=1+col_true_signal):
            if blend or normalize:
                charge_activation = self._prepare_activation(self.activations[task][0], self.image[0], threshold, blend)
                peakpos_activation = self._prepare_activation(self.activations[task][1], self.image[1], threshold, blend)
            else:
                charge_activation = self.activations[task][0]
                peakpos_activation = self.activations[task][1]
            if self.image.dim() == 3:
                im = axes[0, i].imshow(charge_activation)
                peak = axes[1, i].imshow(peakpos_activation)
            elif self.image.dim() == 2:
                im = axes[0, i].scatter(self.camera_geometry.pix_x,
                                        self.camera_geometry.pix_y,
                                        s=pixel_size,
                                        c=charge_activation,
                                        marker=(6, 0, 0))
                axes[0, i].axis('equal')
                peak = axes[1, i].scatter(self.camera_geometry.pix_x,
                                          self.camera_geometry.pix_y,
                                          s=pixel_size,
                                          c=peakpos_activation,
                                          marker=(6, 0, 0))
                axes[1, i].axis('equal')
            else:
                print('Unknown image dimension, should be 2 or 3')
                raise ValueError

            axes[0, i].set_xlabel('Max activation: {:.4f}'.format(self.activations_max[task][0]))
            f.colorbar(im, ax=axes[0, i])
            axes[1, i].set_xlabel('Max activation: {:.4f}'.format(self.activations_max[task][1]))
            f.colorbar(peak, ax=axes[1, i])
            axes[0, i].set_title(task)

        f.tight_layout()
        f.subplots_adjust(top=0.88)


class GradCam(OpenBlackBox):
    """
    Implementation of GradCam method for CTA data. Works with both hexagonal and resampled images.
    For details on the method see https://arxiv.org/pdf/1610.02391.pdf.

    Parameters
    ----------
    net (nn.Module): network to analyze
    class_index (int): class to analyse for the classification task
    cuda (bool): whether or not to use GPU
    camera_geometry (`ctapipe.instrument.CameraGeometry`): camera type of input images

    """
    def __init__(self, net, class_index=0, cuda=True, camera_geometry=CameraGeometry.from_name('LSTCam')):

        super(GradCam, self).__init__(net, class_index=class_index, cuda=cuda, camera_geometry=camera_geometry)

        self.feature_activation = None

        # Hook to get the backbone output on the forward pass
        def get_feature_activation(m, input, output):
            self.feature_activation = output

        self.net.feature.last_ReLU.register_forward_hook(get_feature_activation)

    def __call__(self, image, true_signal=None):
        self.image = image
        self.true_signal = true_signal
        outputs = self.net(image.unsqueeze(0).to(self.device))

        # class
        if 'class' in outputs:
            class_grad_activation = torch.autograd.grad(outputs['class'][:, self.class_index],
                                                        self.feature_activation,
                                                        retain_graph=True
                                                        )[0].squeeze(0)
            class_activation_weights = class_grad_activation.mean(dim=tuple(range(class_grad_activation.dim()))[1:])
            class_activation_weights = class_activation_weights.view(
                (class_activation_weights.shape[0],) + tuple(1 for _ in range(self.feature_activation.dim() - 2)))
            class_weighted_activation = torch.nn.functional.relu(self.feature_activation[0] * class_activation_weights)
            self.activations['Class'] = class_weighted_activation.sum(dim=0).to('cpu').detach().numpy()

        # energy
        if 'energy' in outputs:
            energy_grad_activation = torch.autograd.grad(outputs['energy'],
                                                         self.feature_activation,
                                                         retain_graph=True)[0].squeeze(0)
            energy_activation_weights = energy_grad_activation.mean(dim=tuple(range(energy_grad_activation.dim()))[1:])
            energy_activation_weights = energy_activation_weights.view(
                (energy_activation_weights.shape[0],) + tuple(1 for _ in range(self.feature_activation.dim() - 2)))
            energy_weighted_activation = torch.nn.functional.relu(self.feature_activation[0] * energy_activation_weights)
            self.activations['Energy'] = energy_weighted_activation.sum(dim=0).to('cpu').detach().numpy()

        # direction
        if 'direction' in outputs:
            # altitude
            altitude_grad_activation = torch.autograd.grad(outputs['direction'][:, 0],
                                                           self.feature_activation,
                                                           retain_graph=True)[0].squeeze(0)
            altitude_activation_weights = altitude_grad_activation.mean(
                dim=tuple(range(altitude_grad_activation.dim()))[1:])
            altitude_activation_weights = altitude_activation_weights.view(
                (altitude_activation_weights.shape[0],) + tuple(1 for _ in range(self.feature_activation.dim() - 2)))
            altitude_weighted_activation = torch.nn.functional.relu(
                self.feature_activation[0] * altitude_activation_weights)
            self.activations['Altitude'] = altitude_weighted_activation.sum(dim=0).to('cpu').detach().numpy()

            # azimuth
            azimuth_grad_activation = torch.autograd.grad(outputs['direction'][:, 1],
                                                          self.feature_activation,
                                                          )[0].squeeze(0)
            mean_dims = tuple(range(azimuth_grad_activation.dim()))[1:]
            azimuth_activation_weights = azimuth_grad_activation.mean(dim=mean_dims)
            azimuth_activation_weights = azimuth_activation_weights.view(
                (azimuth_activation_weights.shape[0],) + tuple(1 for _ in range(self.feature_activation.dim() - 2)))
            azimuth_weighted_activation = torch.nn.functional.relu(self.feature_activation[0] * azimuth_activation_weights)
            self.activations['Azimuth'] = azimuth_weighted_activation.sum(dim=0).to('cpu').detach().numpy()

        for task, activation in self.activations.items():
            self.activations_max[task] = [activation.max(), activation.max()]
            activation = self._resize_image(activation)
            # activation -= activation.min()
            # activation /= activation.max()
            self.activations[task] = [activation, activation]

        self.feature_activation = self.feature_activation[0].to('cpu').detach().numpy()

    def _resize_image(self, cam):
        if self.image.dim() == 3:
            return resize(cam, self.image.shape[1:])
        elif self.image.dim() == 2:
            return resize_hexagonal_image(cam, self.net, self.camera_geometry)

    def plot_feature(self, pixel_size=50):
        if plt.get_cmap() != plt.cm.magma_r:
            plt.set_cmap(plt.cm.magma_r)
        nrow = int(np.sqrt(self.feature_activation.shape[0]))
        f, axes = plt.subplots(nrow, nrow, figsize=(2 * nrow, 2 * nrow))

        max_feature = self.feature_activation.max()
        min_feature = self.feature_activation.min()

        for ax, feature in zip(f.get_axes(), self.feature_activation):
            if feature.ndim == 2:
                im = ax.imshow(feature, vmin=min_feature, vmax=max_feature)
            elif feature.ndim == 1:
                # Look for index matrices in the backbone of the net
                matrices = [
                    child.pooled_matrix
                    for child in self.net.feature.children()
                    if hasattr(child, 'pooled_matrix')
                ]

                matrix_set = set(matrices)
                # # Sort matrices by size
                sorted_matrices = list(matrix_set)
                sorted_matrices.sort(key=lambda x: torch.tensor(x.shape).prod())
                # Get index matrix corresponding to feature map
                matrix_dict = {int(torch.sum(torch.ge(matrix[0, 0], 0)).data): matrix[0, 0] for matrix in sorted_matrices}
                # Compute pixel positions
                pix_pos = np.array(ic_utils.build_hexagonal_position(matrix_dict[len(feature)]))

                im = ax.scatter(pix_pos[:, 0], pix_pos[:, 1], c=feature, marker='h', s=pixel_size,
                                vmin=min_feature, vmax=max_feature)
                ax.axis('equal')
            else:
                print('Unknown feature dimension, should be 1 or 2')
                raise ValueError
            plt.colorbar(im, ax=ax)
        f.tight_layout()


class GuidedBackpropReLU(Function):
    """Source https://github.com/jacobgil/pytorch-grad-cam/blob/master/gradcam.py"""

    @staticmethod
    def forward(self, input):
        positive_mask = (input > 0).type_as(input)
        output = torch.addcmul(torch.zeros(input.size()).type_as(input), input, positive_mask)
        self.save_for_backward(input, output)
        return output

    @staticmethod
    def backward(self, grad_output):
        input, output = self.saved_tensors
        grad_input = None

        positive_mask_1 = (input > 0).type_as(grad_output)
        positive_mask_2 = (grad_output > 0).type_as(grad_output)
        grad_input = torch.addcmul(torch.zeros(input.size()).type_as(input),
                                   torch.addcmul(torch.zeros(input.size()).type_as(input), grad_output,
                                                 positive_mask_1), positive_mask_2)

        return grad_input


class GuidedBackprop(OpenBlackBox):
    """

    Parameters
    ----------
    net (nn.Module): network to analyze
    class_index (int): class to analyse for the classification task
    cuda (bool): whether or not to use GPU
    camera_geometry (`ctapipe.instrument.CameraGeometry`): camera type of input images

    """
    def __init__(self, net, class_index=0, cuda=True, camera_geometry=CameraGeometry.from_name('LSTCam')):

        super(GuidedBackprop,  self).__init__(net, class_index=class_index, cuda=cuda, camera_geometry=camera_geometry)

        def recursive_relu_apply(module_top):
            for idx, module in module_top._modules.items():
                recursive_relu_apply(module)
                if module.__class__.__name__ == 'ReLU':
                    module_top._modules[idx] = GuidedBackpropReLU.apply

        # replace ReLU with GuidedBackpropReLU
        recursive_relu_apply(self.net)

    def __call__(self, image, true_signal=None):
        self.true_signal = true_signal
        self.image = image.unsqueeze(0).to(self.device)
        self.image.requires_grad = True
        outputs = self.net(self.image)

        # class
        if 'class' in outputs:
            self.activations['Class'] = torch.nn.functional.relu(
                torch.autograd.grad(outputs['class'][:, self.class_index],
                                    self.image,
                                    retain_graph=True
                                    )[0].squeeze(0)).detach().to('cpu').numpy()

        # energy
        if 'energy' in outputs:
            self.activations['Energy'] = torch.nn.functional.relu(torch.autograd.grad(outputs['energy'],
                                                                                      self.image,
                                                                                      retain_graph=True)[0].squeeze(
                0)).detach().to('cpu').numpy()

        # direction
        if 'direction' in outputs:
            # altitude
            self.activations['Altitude'] = torch.nn.functional.relu(torch.autograd.grad(outputs['direction'][:, 0],
                                                                                        self.image,
                                                                                        retain_graph=True)[
                                                                        0].squeeze(0)).detach().to('cpu').numpy()

            # azimuth
            self.activations['Azimuth'] = torch.nn.functional.relu(torch.autograd.grad(outputs['direction'][:, 1],
                                                                                       self.image)[0].squeeze(
                0)).detach().to('cpu').numpy()

        self.image = self.image.detach().to('cpu').squeeze(0)

        for task, activation in self.activations.items():
            if self.image.dim() == 3:
                activation_max = activation.max(axis=(1, 2))
            elif self.image.dim() == 2:
                activation_max = activation.max(axis=1)
            else:
                print('Unknown image dimension, should be 2 or 3')
                raise ValueError
            self.activations_max[task] = activation_max
            activation[0] -= activation[0].min()
            activation[0] /= activation[0].max()
            activation[1] -= activation[1].min()
            activation[1] /= activation[1].max()
            self.activations[task] = activation


class GuidedGradCam(OpenBlackBox):
    """
    Implementation of Guided-GradCam method for CTA data. Works with both hexagonal and resampled images.
    For details on the method see https://arxiv.org/pdf/1610.02391.pdf.

    Parameters
    ----------
    net (nn.Module): network to analyze
    class_index (int): class to analyse for the classification task
    cuda (bool): whether or not to use GPU
    camera_geometry (`ctapipe.instrument.CameraGeometry`): camera type of input images

    """
    def __init__(self, net, class_index=0, cuda=True, camera_geometry=CameraGeometry.from_name('LSTCam')):

        super(GuidedGradCam, self).__init__(net, class_index=class_index, cuda=cuda, camera_geometry=camera_geometry)
        self.camera_geometry = camera_geometry
        self.guided_backprop = GuidedBackprop(net, class_index=class_index, cuda=cuda, camera_geometry=camera_geometry)
        self.gradcam = GradCam(net, class_index=class_index, cuda=cuda, camera_geometry=camera_geometry)

    def __call__(self, image, true_signal=None):

        self.image = image
        self.true_signal = true_signal

        self.guided_backprop(image)
        self.gradcam(image)

        for task in self.guided_backprop.activations.keys():
            guided_gradcam = self.guided_backprop.activations[task] * self.gradcam.activations[task]
            guided_gradcam /= guided_gradcam.max()
            self.activations[task] = guided_gradcam
        self.activations_max = self.guided_backprop.activations_max


class AttentionMaps(OpenBlackBox):
    """
    Implementation of spatial attention map observation method for CTA data. Works with both hexagonal and resampled images.
    For details on the method see https://arxiv.org/abs/2001.07645.

    Parameters
    ----------
    net (nn.Module): network to analyze
    class_index (int): class to analyse for the classification task
    cuda (bool): whether or not to use GPU
    camera_geometry (`ctapipe.instrument.CameraGeometry`): camera type of input images

    """
    def __init__(self, net, class_index=0, cuda=True, camera_geometry=CameraGeometry.from_name('LSTCam')):

        super(AttentionMaps, self).__init__(net, class_index=class_index, cuda=cuda, camera_geometry=camera_geometry)

        self.save_output = SaveOutput()

        # Hook to get the spatial attention maps output on the forward pass
        for name, layer in self.net.named_modules():
            if name.split('.')[-1] == 'spa_module':
                layer.register_forward_hook(self.save_output)

    def __call__(self, image, true_signal=None):
        self.image = image
        self.true_signal = true_signal
        self.net(image.unsqueeze(0).to(self.device))

        for i, attention_map in enumerate(self.save_output.outputs):
            if i == 0:
                self.activations['Combined'] = np.full_like(attention_map, 1.).squeeze(0).squeeze(0)
            self.activations['Stage {}'.format(i)] = self._resize_image(attention_map + 1).squeeze(0).squeeze(0).numpy()
            self.activations['Combined'] *= self.activations['Stage {}'.format(i)]
        for task, activation in self.activations.items():
            self.activations_max[task] = [activation.max(), activation.max()]
            # activation -= activation.min()
            # activation /= activation.max()
            self.activations[task] = [activation, activation]

        self.save_output.clear()

    def _resize_image(self, cam):
        if self.image.dim() == 3:
            return resize(cam, self.image.shape[1:])
        elif self.image.dim() == 2:
            return resize_hexagonal_image(cam, self.net, self.camera_geometry)


# Translation maps
def translate_and_infer(sample, index_matrix, max_translation, experiment, device):
    """Function to translate a batch of images with a step of 1 pixel and produce inference for every step."""
    experiment.net.to(device)
    with torch.no_grad():
        translated = []
        for v in range(max_translation + 1):
            for h in range(max_translation + 1):
                img_upleft = torch.zeros_like(sample['image'])
                img_downright = torch.zeros_like(sample['image'])
                img_upright = torch.zeros_like(sample['image'])
                img_downleft = torch.zeros_like(sample['image'])
                # We need to apply a correction to h for the vertical move to be in a almost cartesian grid
                # every even row, we must slide the index matrix by 1 px on the left
                h_correction = v // 2

                if v == 0 and h == 0:
                    translated.append([-v, h, {k: v.to('cpu').detach()
                                               for k, v in experiment.net(sample['image'].to(device)).items()}])
                else:

                    for i in range(index_matrix.shape[2]):
                        for j in range(index_matrix.shape[3]):
                            former_idx = index_matrix[0, 0, i, j]

                            if former_idx != -1:
                                # upper left
                                ul_i = i - v
                                ul_j = j - h_correction - h
                                if 0 <= ul_i < index_matrix.shape[2] and 0 <= ul_j < index_matrix.shape[3]:
                                    idx_upleft = index_matrix[0, 0, ul_i, ul_j]
                                else:
                                    idx_upleft = -1
                                if idx_upleft != -1:
                                    img_upleft[:, :, int(former_idx)] = sample['image'][:, :, int(idx_upleft)]
                                # down left
                                dl_i = i + v
                                dl_j = j + h_correction - h
                                if 0 <= dl_i < index_matrix.shape[2] and 0 <= dl_j < index_matrix.shape[3]:
                                    idx_downleft = index_matrix[0, 0, dl_i, dl_j]
                                else:
                                    idx_downleft = -1
                                if idx_downleft != -1:
                                    img_downleft[:, :, int(former_idx)] = sample['image'][:, :, int(idx_downleft)]
                                # upper right
                                ur_i = i - v
                                ur_j = j - h_correction + h
                                if 0 <= ur_i < index_matrix.shape[2] and 0 <= ur_j < index_matrix.shape[3]:
                                    idx_upright = index_matrix[0, 0, ur_i, ur_j]
                                else:
                                    idx_upright = -1
                                if idx_upright != -1:
                                    img_upright[:, :, int(former_idx)] = sample['image'][:, :, int(idx_upright)]
                                # down right
                                dr_i = i + v
                                dr_j = j + h_correction + h
                                if 0 <= dr_i < index_matrix.shape[2] and 0 <= dr_j < index_matrix.shape[3]:
                                    idx_downright = index_matrix[0, 0, dr_i, dr_j]
                                else:
                                    idx_downright = -1
                                if idx_downright != -1:
                                    img_downright[:, :, int(former_idx)] = sample['image'][:, :, int(idx_downright)]
                    if v == 0:
                        translated.append(
                            [v, h, {k: v.to('cpu').detach()
                                    for k, v in experiment.net(img_downright.to(device)).items()}])
                        translated.append(
                            [v, -h, {k: v.to('cpu').detach()
                                     for k, v in experiment.net(img_downleft.to(device)).items()}])
                    elif h == 0:
                        translated.append(
                            [-v, h, {k: v.to('cpu').detach()
                                     for k, v in experiment.net(img_upright.to(device)).items()}])
                        translated.append(
                            [v, h, {k: v.to('cpu').detach()
                                    for k, v in experiment.net(img_downright.to(device)).items()}])
                    else:
                        translated.append(
                            [-v, h, {k: v.to('cpu').detach()
                                     for k, v in experiment.net(img_upright.to(device)).items()}])
                        translated.append(
                            [v, h, {k: v.to('cpu').detach()
                                    for k, v in experiment.net(img_downright.to(device)).items()}])
                        translated.append(
                            [-v, -h, {k: v.to('cpu').detach()
                                      for k, v in experiment.net(img_upleft.to(device)).items()}])
                        translated.append(
                            [v, -h, {k: v.to('cpu').detach()
                                     for k, v in experiment.net(img_downleft.to(device)).items()}])

                del img_upleft
                del img_downright
                del img_upright
                del img_downleft
    return translated
