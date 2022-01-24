# -*- coding: utf-8 -*-

from torch import nn, Tensor

from abc import abstractmethod

import logging

logger = logging.getLogger(__name__)


class BaseTCoNorm(nn.Module):
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def __call__(self,
              a: Tensor,
              b: Tensor) -> Tensor:
        raise NotImplementedError

    def norm(self,
               a: Tensor,
               b: Tensor) -> Tensor:
        return 1.0 - self(1.0 - a, 1.0 - b)
