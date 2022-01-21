from copy import copy
from typing import List, Dict, List
from nwgraph import Node
from ..ngc_v1 import NGCV1

class NGCAAAI2020(NGCV1):
    """
    This is the original implementation. The CFG file contains the edges given manually in the format: 'nodeA_nodeB'
    It also has only one 'inputNode' entry, instead of a list on 'inputNodes' as in the NGCV1 code.
    Thus, we must convert the original cfg file to this new format.
    """
    def __init__(self, nodes:List[Node], cfg: Dict):
        assert not "inputNodes" in cfg
        cfg = NGCAAAI2020._convertCfgToV1Format(cfg)
        super().__init__(nodes, cfg)
        self.hyperParameters["inputNode"] = cfg["inputNode"]

    @staticmethod
    def _convertCfgToV1Format(cfg: Dict):
        cfg = copy(cfg)
        cfg["inputNodes"] = [cfg["inputNode"]]
        edges = cfg["edges"]
        newEdges = []
        for edge in edges:
            nodeA, nodeB = edge.split("_")
            if nodeA == cfg["inputNode"]:
                # Single Link
                newEdges.append([nodeA, nodeB])
            else:
                # Two Hops No GT
                newEdges.append([cfg["inputNode"], nodeA, nodeB])
        cfg["edges"] = newEdges
        return cfg
