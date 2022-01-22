from typing import *

import pytorch_lightning as pl
import torch
from torch import nn
from torch.nn import functional as F

from df2d.util import heatmap2points, tensorboard_plot_image

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


class Drosophila2DPose(pl.LightningModule):
    def __init__(
        self,
        checkpoint_path: str,
        stacks,
        blocks,
        num_classes,
        features,
        inplanes,
        stride,
        **args
    ):
        super().__init__()

        self.model = hg(
            num_stacks=stacks,
            num_blocks=blocks,
            num_classes=num_classes,
            num_feats=features,
            inplanes=inplanes,
            init_stride=stride,
        )

        if checkpoint_path is not None:
            pretrained = {
                k.replace("module.", ""): v
                for (k, v) in torch.load(checkpoint_path, map_location=device)[
                    "state_dict"
                ].items()
            }
            _ = self.model.load_state_dict(pretrained, strict=False)

    def forward(self, x):
        return self.model(x.float().to(device))[-1]

    def mse(self, hm_hat, y):
        y_hat, _ = heatmap2points(hm_hat).cuda()
        mse = torch.norm(y_hat - y, dim=2)
        return mse.mean()

    def configure_optimizers(self):
        optimizer = torch.optim.RMSprop(
            self.parameters(),
            lr=1e-4,
            weight_decay=1e-5,
        )
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            optimizer, verbose=True, patience=5
        )
        return {
            "optimizer": optimizer,
            "lr_scheduler": scheduler,
            "monitor": "train/loss",
        }

    def loss(self, hm_hat, hm):
        # fmt: off
        # missing joint predictions are set to all zeros, which is the same of the gt heatmap
        #   therefore giving zero loss
        missing_joints = torch.all(torch.flatten(hm, 2) == 0, dim=2, keepdim=True)
        missing_joints = missing_joints.float()
        missing_joints = missing_joints.unsqueeze(-1)
        hm_hat = hm_hat * (1 - missing_joints)
        # fmt: on
        return F.mse_loss(hm, hm_hat)

    def training_step(self, train_batch, batch_idx):
        x, d, y, hm = train_batch
        x = x.to(device).float()
        hm = hm.to(device).float()
        hm_hat = self.model(x)

        loss = self.loss(hm_hat[0], hm)
        for idx in range(1, len(hm_hat)):
            loss += self.loss(hm_hat[idx], hm)
        self.log("train/loss", loss, on_step=True)

        # log images
        if batch_idx == 0:
            tensorboard_plot_image(
                self.logger.experiment,
                torch.cat([x[:, [0], ::4, ::4], hm.sum(dim=1, keepdims=True)], dim=2),
                name="data",
                epoch=self.current_epoch,
                scale_each=True,
            )

            # log mse loss
            self.log(name="train/mse", value=self.mse(hm_hat[-1], d), prog_bar=True)

        return loss

    def validation_step(self, val_batch, batch_idx):
        x, d, y, hm = val_batch
        x = x.to(device).float()
        hm = hm.to(device).float()
        hm_hat = self.model(x.float())

        loss = self.loss(hm_hat[0], hm)
        for idx in range(1, len(hm_hat)):
            loss += self.loss(hm_hat[idx], hm)
        self.log("val/loss", loss, on_step=True)

        # log mse loss
        self.log(name="val/mse", value=self.mse(hm_hat[-1], d), prog_bar=True)

        return loss


"""
Hourglass network inserted in the pre-activated Resnet
"""
import torch.nn as nn
import torch.nn.functional as F


class Bottleneck(nn.Module):
    expansion = 2

    def __init__(self, inplanes, planes, stride=1, downsample=None):
        super(Bottleneck, self).__init__()

        self.bn1 = nn.BatchNorm2d(inplanes)
        self.conv1 = nn.Conv2d(inplanes, planes, kernel_size=1, bias=True)
        self.bn2 = nn.BatchNorm2d(planes)
        self.conv2 = nn.Conv2d(
            planes, planes, kernel_size=3, stride=stride, padding=1, bias=True
        )
        self.bn3 = nn.BatchNorm2d(planes)
        self.conv3 = nn.Conv2d(planes, planes * 2, kernel_size=1, bias=True)
        self.relu = nn.ReLU(inplace=True)
        self.downsample = downsample
        self.stride = stride

    def forward(self, x):
        residual = x

        out = self.bn1(x)
        out = self.relu(out)
        out = self.conv1(out)

        out = self.bn2(out)
        out = self.relu(out)
        out = self.conv2(out)

        out = self.bn3(out)
        out = self.relu(out)
        out = self.conv3(out)

        if self.downsample is not None:
            residual = self.downsample(x)

        out += residual

        return out


class Hourglass(nn.Module):
    def __init__(self, block, num_blocks, planes, depth):
        super(Hourglass, self).__init__()
        self.depth = depth
        self.block = block
        self.upsample = nn.Upsample(scale_factor=2)
        self.hg = self._make_hour_glass(block, num_blocks, planes, depth)

    def _make_residual(self, block, num_blocks, planes):
        layers = []
        for i in range(0, num_blocks):
            layers.append(block(planes * block.expansion, planes))
        return nn.Sequential(*layers)

    def _make_hour_glass(self, block, num_blocks, planes, depth):
        hg = []
        for i in range(depth):
            res = []
            for j in range(3):
                res.append(self._make_residual(block, num_blocks, planes))
            if i == 0:
                res.append(self._make_residual(block, num_blocks, planes))
            hg.append(nn.ModuleList(res))
        return nn.ModuleList(hg)

    def _hour_glass_forward(self, n, x):
        up1 = self.hg[n - 1][0](x)
        low1 = F.max_pool2d(x, 2, stride=2)
        low1 = self.hg[n - 1][1](low1)

        if n > 1:
            low2 = self._hour_glass_forward(n - 1, low1)
        else:
            low2 = self.hg[n - 1][3](low1)
        low3 = self.hg[n - 1][2](low2)
        up2 = self.upsample(low3)
        out = up1 + up2
        return out

    def forward(self, x):
        return self._hour_glass_forward(self.depth, x)


class HourglassNet(nn.Module):
    """Hourglass model from Newell et al ECCV 2016"""

    def __init__(
        self,
        block,
        num_stacks=2,
        num_blocks=4,
        num_classes=16,
        inplanes=64,
        num_feats=128,
        init_stride=2,
    ):
        super(HourglassNet, self).__init__()

        self.inplanes = inplanes
        self.num_feats = num_feats
        self.num_stacks = num_stacks
        self.conv1 = nn.Conv2d(
            3, self.inplanes, kernel_size=7, stride=init_stride, padding=3, bias=True
        )
        self.bn1 = nn.BatchNorm2d(self.inplanes)
        self.relu = nn.ReLU(inplace=True)
        self.layer1 = self._make_residual(block, self.inplanes, 1)
        self.layer2 = self._make_residual(block, self.inplanes, 1)
        self.layer3 = self._make_residual(block, self.num_feats, 1)
        self.maxpool = nn.MaxPool2d(2, stride=2)

        # build hourglass modules
        ch = self.num_feats * block.expansion
        hg, res, fc, score, fc_, score_ = [], [], [], [], [], []
        for i in range(num_stacks):
            hg.append(Hourglass(block, num_blocks, self.num_feats, 4))
            res.append(self._make_residual(block, self.num_feats, num_blocks))
            fc.append(self._make_fc(ch, ch))
            score.append(nn.Conv2d(ch, num_classes, kernel_size=1, bias=True))
            if i < num_stacks - 1:
                fc_.append(nn.Conv2d(ch, ch, kernel_size=1, bias=True))
                score_.append(nn.Conv2d(num_classes, ch, kernel_size=1, bias=True))
        self.hg = nn.ModuleList(hg)
        self.res = nn.ModuleList(res)
        self.fc = nn.ModuleList(fc)
        self.score = nn.ModuleList(score)
        self.fc_ = nn.ModuleList(fc_)
        self.score_ = nn.ModuleList(score_)

    def _make_residual(self, block, planes, blocks, stride=1):
        downsample = None
        if stride != 1 or self.inplanes != planes * block.expansion:
            downsample = nn.Sequential(
                nn.Conv2d(
                    self.inplanes,
                    planes * block.expansion,
                    kernel_size=1,
                    stride=stride,
                    bias=True,
                ),
            )

        layers = []
        layers.append(block(self.inplanes, planes, stride, downsample))
        self.inplanes = planes * block.expansion
        for i in range(1, blocks):
            layers.append(block(self.inplanes, planes))

        return nn.Sequential(*layers)

    def _make_fc(self, inplanes, outplanes):
        bn = nn.BatchNorm2d(inplanes)
        conv = nn.Conv2d(inplanes, outplanes, kernel_size=1, bias=True)
        return nn.Sequential(
            conv,
            bn,
            self.relu,
        )

    def forward(self, x):
        out = []
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)

        x = self.layer1(x)
        x = self.maxpool(x)
        x = self.layer2(x)
        x = self.layer3(x)

        for i in range(self.num_stacks):
            y = self.hg[i](x)
            y = self.res[i](y)
            y = self.fc[i](y)
            score = self.score[i](y)
            out.append(score)
            if i < self.num_stacks - 1:
                fc_ = self.fc_[i](y)
                score_ = self.score_[i](score)
                x = x + fc_ + score_

        return out


def hg(**kwargs):
    model = HourglassNet(
        Bottleneck,
        num_stacks=kwargs["num_stacks"],
        num_blocks=kwargs["num_blocks"],
        num_classes=kwargs["num_classes"],
        num_feats=kwargs["num_feats"],
        inplanes=kwargs["inplanes"],
        init_stride=kwargs["init_stride"],
    )
    return model
