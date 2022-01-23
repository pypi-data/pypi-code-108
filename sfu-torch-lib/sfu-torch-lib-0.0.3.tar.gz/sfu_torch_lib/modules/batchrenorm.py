import torch

from torch import Tensor
from torch.nn import Module


class BatchRenorm(Module):
    def __init__(
        self,
        num_features: int,
        epsilon: float = 1e-3,
        momentum: float = 0.01,
        affine: bool = True,
    ) -> None:

        super().__init__()

        self.register_buffer('running_mean', torch.zeros(num_features, dtype=torch.float32))
        self.register_buffer('running_std', torch.ones(num_features, dtype=torch.float32))
        self.register_buffer('num_batches_tracked', torch.tensor(0, dtype=torch.int64))

        self.weight = torch.nn.Parameter(torch.ones(num_features, dtype=torch.float32))
        self.bias = torch.nn.Parameter(torch.zeros(num_features, dtype=torch.float32))

        self.affine = affine
        self.epsilon = epsilon
        self.step = 0
        self.momentum = momentum

    def _check_input_dim(self, x):
        raise NotImplementedError()

    @property
    def rmax(self):
        return (2 / 35000 * self.num_batches_tracked + 25 / 35).clamp_(1.0, 3.0)

    @property
    def dmax(self):
        return (5 / 20000 * self.num_batches_tracked - 25 / 20).clamp_(0.0, 5.0)

    def forward(self, x):
        self._check_input_dim(x)

        if x.dim() > 2:
            x = x.transpose(1, -1)

        if self.training:
            dims = [i for i in range(x.dim() - 1)]
            batch_mean = x.mean(dims)
            batch_std = x.std(dims, unbiased=False) + self.epsilon
            r = (
                batch_std.detach() / self.running_std.view_as(batch_std)
            ).clamp_(1 / self.rmax, self.rmax)
            d = (
                (batch_mean.detach() - self.running_mean.view_as(batch_mean)) / self.running_std.view_as(batch_std)
            ).clamp_(-self.dmax, self.dmax)
            x = (x - batch_mean) / batch_std * r + d
            self.running_mean += self.momentum * (batch_mean.detach() - self.running_mean)
            self.running_std += self.momentum * (batch_std.detach() - self.running_std)
            self.num_batches_tracked += 1
        else:
            x = (x - self.running_mean) / self.running_std

        if self.affine:
            x = self.weight * x + self.bias

        if x.dim() > 2:
            x = x.transpose(1, -1)

        return x


class BatchRenorm1d(BatchRenorm):
    def _check_input_dim(self, x: Tensor) -> None:
        if x.dim() not in [2, 3]:
            raise ValueError(f'expected 2D or 3D input (got {x.dim()}D input)')


class BatchRenorm2d(BatchRenorm):
    def _check_input_dim(self, x: Tensor) -> None:
        if x.dim() != 4:
            raise ValueError(f'expected 4D input (got {x.dim()}D input)')


class BatchRenorm3d(BatchRenorm):
    def _check_input_dim(self, x: Tensor) -> None:
        if x.dim() != 5:
            raise ValueError(f'expected 5D input (got {x.dim()}D input)')
