# -*- coding: utf-8 -*-

import torch
from torch import nn, Tensor

from torchnorms.tnorms.base import BaseTNorm

from typing import Optional


class AczelAlsinaTNorm(BaseTNorm):
    def __init__(self,
                 p: Optional[Tensor] = None,
                 default_p: float = 0.1) -> None:
        super().__init__()
        self.p = p
        if self.p is None:
            self.p = nn.Parameter(torch.tensor(default_p))

        else:
            assert self.p > 0
            assert self.p != float('inf')

        assert len(self.p.shape) == 0

    def __call__(self,
                 a: Tensor,
                 b: Tensor) -> Tensor:
        res: Optional[Tensor] = None

        p_1 = torch.pow(torch.abs(torch.log(a)), self.p)
        p_2 = torch.pow(torch.abs(torch.log(b)), self.p)
        res = torch.exp(-torch.pow(p_1 + p_2, 1.0 / self.p))

        return res
