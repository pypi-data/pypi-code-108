from copy import deepcopy
from typing import Dict, List
import torch as tr
from pathlib import Path
from overrides import overrides
from torch import nn
from nwmodule import NWModule
from nwutils.nwmodule import trModuleWrapper
from nwutils.torch import trGetData
from nwgraph import Edge, Node
from .two_hops_nogt import TwoHopsSerializer
from .ngc_edge import NGCEdge
from ...logger import logger

class TwoHopsResidualNoGT(NGCEdge):
    def __init__(self, singleLinkEdge: Edge, residualNode: Node, \
            inputNode: Node, outputNode: Node, hyperParameters: Dict={}):
        singleLinkNode = singleLinkEdge.inputNode
        name = f"Two Hops NoGT ({inputNode} -> {outputNode}) (Single Link Node: {singleLinkNode}. " \
            f"Residual Node: {residualNode})"
        prefix = "THR_NOGT"
        hyperParameters["singleLinkNode"] = singleLinkNode
        hyperParameters["residualNode"] = residualNode
        super().__init__(prefix, inputNode, outputNode, name, hyperParameters)

        self.singleLinkNode = singleLinkNode
        self.residualNode = residualNode
        self.singleLinkEdge = deepcopy(singleLinkEdge).to(self.getDevice())
        self.serializer = TwoHopsSerializer(model=self)
        logger.debug(f"Setting single link of {self.name}: '{self.singleLinkEdge}'")

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
    def setup(self, **kwargs):
        weightsFile = f"{kwargs['singleLinkDir']}/model_best_Loss.pkl" 
        logger.debug(f"Loading single link of {self.name}: {self.singleLinkEdge} from '{weightsFile}'")
        self.singleLinkEdge.setTrainableWeights(True)
        self.singleLinkEdge.loadWeights(weightsFile)
        self.singleLinkEdge.eval()

    @overrides
    def networkAlgorithm(self, trInputs, trLabels, isTraining, isOptimizing):
        """Called at train time, graph is not passed, but we have access to proper GT (SL input). """
        assert not self.singleLinkEdge is None
        assert not self.getCriterion() is None, "Set criterion before training or testing"
        # Pass through the single link of this two hops edge
        residual = trInputs[self.residualNode.name]
        with tr.no_grad():
            slOutput, _ = self.singleLinkEdge.networkAlgorithm(trInputs, trLabels, False, False)
        concatenated = tr.cat([slOutput, residual], dim=-1)
        trResults = self.model.forward(concatenated)
        trLoss = 0
        if isTraining:
            trLoss = self.getCriterion()(trResults, trLabels)
            self.updateOptimizer(trLoss, isTraining, isOptimizing)
        return trResults, trLoss

    def forward(self, x: tr.Tensor):
        """Called only at inference time, so graph is passed. """
        assert len(self.residualNode.messages) == 1
        slInput = trGetData(tuple(self.residualNode.messages)[0].input)
        concatenated = tr.cat([x, slInput], dim=-1)
        y = super().forward(concatenated)
        return y

    @overrides
    def getInKeys(self) -> List[str]:
        return self.singleLinkEdge.getInKeys()

