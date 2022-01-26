# -*- coding: utf-8 -*-

import torch
from torch import nn, Tensor

from torchnorms.tconorms.base import BaseTCoNorm

from typing import Optional


class SchweizerSklarTCoNorm(BaseTCoNorm):
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
            p_1 = torch.pow(1.0 - a, self.p)
            p_2 = torch.pow(1.0 - b, self.p)
            p_1 = torch.maximum(torch.tensor(0), p_1 + p_2 - 1.0)
            res = torch.pow(p_1, 1.0 / self.p)
            res = 1.0 - res

            return res
