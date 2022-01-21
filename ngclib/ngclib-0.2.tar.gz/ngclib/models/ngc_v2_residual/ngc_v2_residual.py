from typing import List, Dict
from overrides import overrides
from nwgraph import Edge, Node
from ..edges import SingleLink, TwoHopsResidualNoGT, SingleLinkResidual
from ..ngc_v1 import NGCV1
from ...logger import logger

class NGCV2Residual(NGCV1):
    """
    NGCV2 is an NGCV1 with the following changes:
        - there is a single residual node in the cfg, that is also an input node
        - all edges starting with the residual node, are regular single links
        - all edges starting with another input node (not residual), are single link residual edges
        - all two hops are two hops residuals no gt
        - there is no two hop no gt (non-residual)
    """
    def __init__(self, nodes: List[Node], cfg: Dict):
        assert "residualNode" in cfg
        assert cfg["residualNode"] in cfg["inputNodes"]
        super().__init__(nodes, cfg)

    @overrides
    def _getNGCEdgesFromList(self, edgesList: List[List[str]]) -> List[Edge]:
        logger.debug(f"Creating edges from a list of edges ({len(edgesList)}).")
        edges = []
        gtKeyToNode = {node.name: node for node in self.nodes}
        # Only one residual node allowed in this implementation. Both for SLR and THR.
        residualNode = gtKeyToNode[self.cfg["residualNode"]]
        singleLinks = {}

        # Pass once to create single links (residual and not)
        for edge in edgesList:
            edgeNodes = [gtKeyToNode[nodeStr] for nodeStr in edge]
            if len(edge) == 2:
                key = (edgeNodes[0], edgeNodes[1])
                assert key not in singleLinks
                if edge[0] == self.cfg["residualNode"]:
                    edge = SingleLink(edgeNodes[0], edgeNodes[1])
                else:
                    edge = SingleLinkResidual(residualNode, edgeNodes[0], edgeNodes[1])
                singleLinks[key] = edge
            elif len(edge) == 3:
                continue
            else:
                assert False
            edges.append(edge)

        # Pass again to create two hops residual
        for edge in edgesList:
            edgeNodes = [gtKeyToNode[nodeStr] for nodeStr in edge]
            if len(edge) == 2:
                continue
            elif len(edge) == 3:
                key = (edgeNodes[0], edgeNodes[1])
                assert key in singleLinks
                edge = TwoHopsResidualNoGT(singleLinks[key], residualNode, edgeNodes[1], edgeNodes[2])
            else:
                assert False
            edges.append(edge)

        return edges
