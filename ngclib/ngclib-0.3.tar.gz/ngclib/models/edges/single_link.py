from typing import List, Dict
from overrides import overrides
from nwgraph import Node
from .ngc_edge import NGCEdge

class SingleLink(NGCEdge):
    """Simple Single Link edge. Defined by a regular forward pass."""
    def __init__(self, inputNode: Node, outputNode: Node, hyperParameters: Dict = {}):
        name = f"Single Link ({inputNode} -> {outputNode})"
        prefix = "SL"
        super().__init__(prefix, inputNode, outputNode, name, hyperParameters)

    @overrides
    def networkAlgorithm(self, trInputs, trLabels, isTraining, isOptimizing):
        """Called at train time, graph is not passed, but we have access to proper GT (SL input). """
        assert not self.getCriterion() is None, "Set criterion before training or testing"
        # Pass through the single link of this two hops edge
        edgeInput = trInputs[self.inputNode]
        trResults = self.model.forward(edgeInput)
        trLoss = 0
        if isTraining:
            trLoss = self.getCriterion()(trResults, trLabels)
            self.updateOptimizer(trLoss, isTraining, isOptimizing)
        return trResults, trLoss

    @overrides
    def getInKeys(self) -> List[str]:
        return [self.inputNode.name]
