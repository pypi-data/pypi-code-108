# -*- coding: utf-8 -*-

import torch
from torch import nn, Tensor

from torchnorms.tnorms.base import BaseTNorm

from typing import Optional


class WeberTNorm(BaseTNorm):
    def __init__(self,
                 p: Optional[Tensor] = None,
                 default_p: float = -0.8) -> None:
        super().__init__()
        self.p = p
        if self.p is None:
            assert default_p >= -1.0
            self.p = nn.Parameter(torch.tensor(default_p))
        else:
            assert self.p >= -1.0

        assert len(self.p.shape) == 0

    def __call__(self,
                 a: Tensor,
                 b: Tensor) -> Tensor:
        res: Optional[Tensor] = None

        p_1 = (1.0 + self.p) * ( a + b - 1.0)
        p_2 = p_1 - self.p * a * b
        res = torch.maximum(p_2, torch.tensor(0))

        return res
