import torch as tr
from overrides import overrides
from typing import Dict, List
from copy import deepcopy
from nwgraph import Node, Edge
from nwmodule.serializer import NWModuleSerializer
from .ngc_edge import NGCEdge
from ...logger import logger

device = tr.device("cuda") if tr.cuda.is_available() else tr.device("cpu")

class TwoHopsSerializer(NWModuleSerializer):
    @overrides
    def doSaveWeights(self):
        # Guarantee that the single link is not trainable at save time, so it's not saved.
        isTrainable = self.model.singleLinkEdge.isTrainable()
        self.model.singleLinkEdge.setTrainableWeights(False)
        parametersState = super().doSaveWeights()
        self.model.singleLinkEdge.setTrainableWeights(isTrainable)
        return parametersState

    @overrides
    def doLoadWeights(self, loadedParams, allowNamedMismatch=False):
        # Temporarily remove the reference to the single link edge from the two hops model so we can load w/o these
        #  names missing from the state_dict.
        slEdge = self.model.singleLinkEdge
        self.model.singleLinkEdge = None
        super().doLoadWeights(loadedParams, allowNamedMismatch)
        self.model.singleLinkEdge = slEdge

class TwoHopsNoGT(NGCEdge):
    def __init__(self, singleLinkEdge: Edge, inputNode: Node, outputNode: Node, hyperParameters: Dict={}):
        singleLinkNode = singleLinkEdge.inputNode
        name = f"Two Hops NoGT ({inputNode} -> {outputNode}) (Single Link Node: {singleLinkNode})"
        prefix = "TH_NOGT"
        hyperParameters["singleLinkNode"] = singleLinkNode
        super().__init__(prefix, inputNode, outputNode, name, hyperParameters)
        self.singleLinkNode = singleLinkNode
        self.singleLinkEdge = deepcopy(singleLinkEdge).to(self.getDevice())
        self.serializer = TwoHopsSerializer(model=self)
        logger.debug(f"Setting single link of {self.name}: '{self.singleLinkEdge}'")

    @overrides
    def setup(self, **kwargs):
        weightsFile = f"{kwargs['singleLinkDir']}/model_best_Loss.pkl" 
        logger.debug(f"Loading single link of {self.name}: {self.singleLinkEdge} from '{weightsFile}'")
        self.singleLinkEdge.setTrainableWeights(True)
        self.singleLinkEdge.loadWeights(weightsFile)
        self.singleLinkEdge.eval()

    @overrides
    def networkAlgorithm(self, trInputs, trLabels, isTraining, isOptimizing):
        assert not self.singleLinkEdge is None
        assert not self.getCriterion() is None, "Set criterion before training or testing"
        # Pass through the single link of this two hops edge
        # slInput = trInputs[self.singleLinkNode.name]
        with tr.no_grad():
            slOutput, _ = self.singleLinkEdge.networkAlgorithm(trInputs, trLabels, False, False)
        trResults = self.forward(slOutput)
        trLoss = 0
        if isTraining:
            trLoss = self.getCriterion()(trResults, trLabels)
            self.updateOptimizer(trLoss, isTraining, isOptimizing)
        return trResults, trLoss

    @overrides
    def getInKeys(self) -> List[str]:
        return self.singleLinkEdge.getInKeys()
