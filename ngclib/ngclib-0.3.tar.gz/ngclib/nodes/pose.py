import numpy as np
import torch as tr
from nwgraph import CriterionType
from torchmetrics import Metric
from typing import Dict
from overrides import overrides

from .vector_node import VectorNode

class PositionMetric(Metric):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_state("result", default=tr.tensor(0), dist_reduce_fx="sum")
        self.add_state("total", default=tr.tensor(0), dist_reduce_fx="sum")

    def update(self, y: tr.Tensor, gt: tr.Tensor):
        assert y.shape == gt.shape
        y, gt = y[:, 0:3], gt[:, 0:3]
        error = tr.norm(y - gt, dim=-1)
        self.result += error
        self.total += y.numel()

    def compute(self):
        return self.result.float() / self.total

class OrientationMetric(Metric):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_state("result", default=tr.tensor(0), dist_reduce_fx="sum")
        self.add_state("total", default=tr.tensor(0), dist_reduce_fx="sum")

    def update(self, y: tr.Tensor, gt: tr.Tensor):
        assert y.shape == gt.shape
        y, gt = y[:, 3:], gt[:, 3:]

        # [0 : 1] => [-1 : 1]
        y = y * 2 - 1
        gt = gt * 2 - 1

        # https://stackoverflow.com/questions/1878907/the-smallest-difference-between-2-angles
        # [-1 : 1] => [0 : 1]
        error = tr.abs((y - gt + 1) % 2 - 1)
        # error :: [0 : 1] => [0 : 180]
        error = error * 180
        self.result += error
        self.total += y.numel()

    def compute(self):
        return self.result.float() / self.total

class Pose(VectorNode):
    def __init__(self, name: str="pose"):
        super().__init__(name=name, numDims=6)

    @overrides
    def getNodeMetrics(self) -> Dict[str, Metric]:
        return {
            "Position": PositionMetric(),
            "Orientation (deg)": OrientationMetric()
        }

    @overrides
    def getNodeCriterion(self) -> CriterionType:
        return Pose.lossFn

    def lossFn(y, t):
        return ((y - t)**2).mean()
