from copy import deepcopy
from typing import Dict, List
import torch as tr
from overrides import overrides
from torch import nn
from nwmodule import NWModule
from nwutils.nwmodule import trModuleWrapper
from nwutils.torch import trGetData
from nwgraph import Node
from ..edges import NGCEdge
from ...logger import logger

class SingleLinkResidual(NGCEdge):
    def __init__(self, residualNode: Node, inputNode: Node, outputNode: Node, hyperParameters: Dict={}):
        hyperParameters["residualNode"] = residualNode
        name = f"Single Link Residual ({inputNode} -> {outputNode}) (Residual Node: {residualNode})"
        prefix = "SLR"
        super().__init__(prefix, inputNode, outputNode, name, hyperParameters)
        self.residualNode = residualNode

    @overrides
    def getModel(self) -> NWModule:
        if hasattr(self, "model"):
            logger.info("Model already instantiated, returning early.")
            return self.model
        A, B = self.inputNode, self.outputNode
        # Create a new intermediate node where we append the SL's (RGB) numbers of dimensions to instantaite the model
        #  properly.
        _A = deepcopy(A)
        _A.numDims += self.hyperParameters["residualNode"].numDims
        encoder = _A.getEncoder(B)
        decoder = B.getDecoder(A)
        model = trModuleWrapper(nn.Sequential(encoder, decoder))
        self.addMetrics(B.getNodeMetrics())
        return model

    @overrides
    def networkAlgorithm(self, trInputs, trLabels, isTraining, isOptimizing):
        """Called at train time, graph is not passed, but we have access bot to SL input as well as residual. """
        assert not self.residualNode is None
        assert not self.getCriterion() is None, "Set criterion before training or testing"
        # Pass through the single link of this two hops edge
        residual = trInputs[self.residualNode]
        edgeInput = trInputs[self.inputNode]
        concatenated = tr.cat([edgeInput, residual], dim=-1)
        breakpoint()
        trResults = self.model.forward(concatenated)
        trLoss = 0
        if isTraining:
            trLoss = self.getCriterion()(trResults, trLabels)
            self.updateOptimizer(trLoss, isTraining, isOptimizing)
        return trResults, trLoss

    def forward(self, x: tr.Tensor):
        """Called only at inference time, so graph is passed. """
        assert len(self.residualNode.messages) == 1
        residualInput = trGetData(tuple(self.residualNode.messages)[0].input)
        concatenated = tr.cat([x, residualInput], dim=-1)
        y = super().forward(concatenated)
        return y

    @overrides
    def getInKeys(self) -> List[str]:
        return [self.inputNode.name, self.residualNode.name]
