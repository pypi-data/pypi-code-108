# -*- coding: utf-8 -*-

from torch import nn, Tensor

from abc import abstractmethod

import logging

logger = logging.getLogger(__name__)


class BaseNegation(nn.Module):
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def __call__(self,
              a: Tensor) -> Tensor:
        raise NotImplementedError
