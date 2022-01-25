from typing import List
from streng.ppp.model2d.input_classes import Node


class Model:
    def __init__(self, nodes: List[Node]):
        self.nodes = nodes

    @property
    def nodes_x_levels(self):
        xs = [n.X for n in self.nodes]
        return {(k+1): v for k, v in enumerate(sorted(set(xs)))}

    @property
    def nodes_y_levels(self):
        ys = [n.Y for n in self.nodes]
        return {k: v for k, v in enumerate(sorted(set(ys)))}


