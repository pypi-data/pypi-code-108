# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import torch
import torch.nn as nn
import torch.nn.functional as F


class GhostBatchNorm1d(nn.BatchNorm1d):
    """A PyTorch implementation of GhostBatchNorm heavily inspired by https://github.com/davidcpage/cifar10-fast/."""

    def __init__(self, num_features: int, num_virtual_batches: int, **kwargs):
        """Instantiates a GhostBatchNorm1d.

        Parameters
        ----------
        num_features: int
            The size of the feature dimension
        num_virtual_batches: int
            The number of virtual batches into which the tensor should be split

        """
        super().__init__(num_features, **kwargs)
        self.num_virtual_batches = num_virtual_batches
        self.register_buffer("running_mean", torch.zeros(num_virtual_batches, num_features))
        self.register_buffer("running_var", torch.ones(num_virtual_batches, num_features))

    def train(self, mode: bool = True):  # -> GhostBatchNorm1d:
        """Mark model as in train or eval mode.

        When switching to eval mode, average the various virtual batch statistics so they're uniform.

        Parameters
        ----------
        mode: bool, optional
            Whether to mark the module as in training or eval mode, default is True (training)

        Returns
        -------
        GhostBatchNorm1d

        """
        if self.training and not mode:
            self.running_mean = self.running_mean.mean(dim=0, keepdim=True).repeat([self.num_virtual_batches, 1])
            self.running_var = self.running_var.mean(dim=0, keepdim=True).repeat([self.num_virtual_batches, 1])
        super().train(mode)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Applies Ghost BatchNorm to the given tensor.

        Parameters
        ----------
        x: torch.Tensor
            The tensor to which Ghost BatchNorm is applied.

        Returns
        -------
        torch.Tensor
            The Ghost BatchNorm'd tensor

        """
        if self.training or not self.track_running_stats:
            xs = x.chunk(self.num_virtual_batches)
            bn = [
                F.batch_norm(
                    xc,
                    self.running_mean[i, :],
                    self.running_var[i, :],
                    self.weight,
                    self.bias,
                    True,
                    self.momentum,
                    self.eps,
                )
                for i, xc in enumerate(xs)
            ]
            return torch.cat(bn)
        else:
            # only use the first copy of the feature statistics as they've already been averaged in the switch from
            # train to eval
            return F.batch_norm(
                x,
                self.running_mean[0, :],
                self.running_var[0, :],
                self.weight,
                self.bias,
                False,
                self.momentum,
                self.eps,
            )
