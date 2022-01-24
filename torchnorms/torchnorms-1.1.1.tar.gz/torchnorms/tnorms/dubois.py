# -*- coding: utf-8 -*-

import torch
from torch import nn, Tensor

from torchnorms.tnorms.base import BaseTNorm

from typing import Optional


class DuboisTNorm(BaseTNorm):
    def __init__(self,
                 p: Optional[Tensor] = None,
                 default_p: float = 0.1) -> None:
        super().__init__()
        self.p = p
        if self.p is None:
            self.p = nn.Parameter(torch.tensor(default_p))
        assert len(self.p.shape) == 0

    def __call__(self,
                 a: Tensor,
                 b: Tensor) -> Tensor:
        res: Optional[Tensor] = None
        res = (a * b) / torch.maximum(torch.maximum(a,b), self.p)

        return res
