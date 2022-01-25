import torch as tr
from abc import abstractmethod
from pathlib import Path
from typing import List, Optional, Dict, Iterable, Callable
from nwgraph import Graph, Edge, Node, Message
from overrides import overrides
from ..nodes import *
from ..voting_algorithms import simpleMean, simpleMedian, NetworkSelection
from ..logger import logger

class NGC(Graph):
    def __init__(self, nodes: List[Node], cfg: Dict):
        self.cfg = cfg
        self.nodes = nodes
        edges = self.getNGCEdges()
        # Edge and node hyperparameters are set by graph constructor
        hyperParameters = {
            "nodeTypes": cfg["nodeTypes"],
            "voteFunction": cfg["voteFunction"]
        }
        super().__init__(edges, hyperParameters)
        assert len(edges) == len(self.edges)
        self.voteFn = self.setupVoteFn()

    def setupVoteFn(self):
        """Setup the voting function for each node, read from the cfg file """
        def getVoteFn(vote):
            if vote == "simpleMean":
                return simpleMean
            elif vote == "simpleMedian":
                return simpleMedian
            elif isinstance(vote, list) and vote[0] == "networkSelection":
                return NetworkSelection(vote)
            else:
                assert False, f"Unknown vote type: {vote}"

        vote = self.cfg["voteFunction"]
        nodeNames = [x.name for x in self.nodes]
        # We can give just one string for all nodes, or we can instantiate all of them
        if not isinstance(vote, dict):
            vote = {k: vote for k in nodeNames}

        res = {}
        for node, nodeName in zip(self.nodes, nodeNames):
            assert nodeName in vote, f"Node {nodeName} ({node}) not in vote list: {list(vote.keys())}"
            res[node] = getVoteFn(vote[nodeName])
        return res

    @overrides
    def aggregate(self):
        for node in self.nodes:
            messages = node.getMessages()
            assert len(messages) > 0
            # Concatenate all messages into one tensor
            trMessages = tr.stack([x.output for x in messages], dim=0)
            oldPath = "|".join([str(x.path[-1]) for x in messages])
            newPath = [oldPath, "Vote"]
            voteOutput = self.voteFn[node](node, trMessages)
            newMessage = Message(newPath, trMessages, voteOutput)
            node.clearMessages()
            node.addMessage(newMessage)

    @abstractmethod
    def getNGCEdges(self) -> List[Edge]:
        pass

    def getTrainedEdges(self, weightsDir: Path, getEdgeDirNameFn: Callable[[Edge], str]) -> List[Edge]:
        def isTrained(edgeWeightDir: Path) -> bool:
            if not edgeWeightDir.exists():
                return False
            # It's impossible to know if a model was fully trained or not. Thus, if this file exists, we assume that
            #  the edge is trained properly. If we want to update the edge somehow, we must retraine it separately
            #  and plug it into ngcdir.
            weightsFile = edgeWeightDir / "model_best_Loss.pkl"
            return weightsFile.exists()

        edges = []
        logger.info("Checking which edges are trained.")
        for edge in self.edges:
            if isTrained(weightsDir / getEdgeDirNameFn(edge)):
                edges.append(edge)
        logger.info(f"Trained edges: {len(edges)} out of {len(self.edges)}")
        return edges

    def loadAllEdges(self, weightsDir: Optional[Path], getEdgeDirNameFn: Callable[[Edge], str]):
        if weightsDir is None:
            logger.debug("Weights dir not set, assuming cwd()")
            weightsDir = Path.cwd()
        num_trained_edges = len(self.getTrainedEdges(weightsDir, getEdgeDirNameFn))
        assert num_trained_edges == len(self.edges), f"{num_trained_edges} vs. {len(self.edges)}"

        for edge in self.edges:
            weightsFile = weightsDir / getEdgeDirNameFn(edge) / "model_best_Loss.pkl"
            logger.debug(f"Edge: {edge}. Loading weights from '{weightsFile}'.")
            edge.setTrainableWeights(True)
            edge.loadWeights(weightsFile, yolo=True)

    def getNumParams(self):
        return "Do you really wanna know ? (laggy)", 0
        # return getNumParams(self)

    def trainReader(self, reader: Iterable, numEpochs: int, validationReader: Optional[Iterable] = None):
        from ..trainer import NGCTrainer
        assert False, "TODO: Train all automagically"

    def __str__(self):
        Str = super().__str__()
        Str += f"\nNGC:"
        Str += f"\n  - Graph type: {str(type(self)).split('.')[-1][:-2]}"
        Str += f"\n  - Vote function: {self.cfg['voteFunction']}"
        return Str
