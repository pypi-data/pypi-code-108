from typing import Callable
import torch as tr

CriterionType = Callable[[tr.Tensor, tr.Tensor, dict], tr.Tensor]
