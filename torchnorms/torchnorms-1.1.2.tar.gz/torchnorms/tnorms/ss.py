# -*- coding: utf-8 -*-

import torch
from torch import nn, Tensor

from torchnorms.tnorms.base import BaseTNorm

from typing import Optional


class SchweizerSklarTNorm(BaseTNorm):
    def __init__(self,
                 p: Optional[Tensor] = None,
                 default_p: float = 1.0) -> None:
        super().__init__()
        self.p = p
        if self.p is None:
            self.p = nn.Parameter(torch.tensor(default_p))
        assert len(self.p.shape) == 0

    def __call__(self,
                 a: Tensor,
                 b: Tensor) -> Tensor:
        res: Optional[Tensor] = None
        if self.p.item() < 0.0:
            res: Tensor = (a ** self.p + b ** self.p - 1.0) ** (1.0 / self.p)
        elif self.p.item() == 0.0:
            res: Tensor = a * b
        elif self.p.item() > 0.0:
            res: Tensor = (a ** self.p + b ** self.p - 1.0)
            res: Tensor = torch.max(res, torch.tensor(0.0))
            res: Tensor = res ** (1.0 / self.p)
        assert res is not None
        return res
