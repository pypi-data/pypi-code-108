from abc import abstractmethod, ABC
from typing import Dict
from nwgraph import Edge
from torch.utils.data import DataLoader

from ..readers import NGCNpzReader, EdgeReader
from ..models import NGC
from ..readers.augmentation import get_augmentation
from ..models.edges import SingleLink, TwoHopsNoGT, SingleLinkResidual, TwoHopsResidualNoGT

def get_loader(reader: NGCNpzReader, edge: Edge, train_cfg: Dict, randomize: bool, \
               debug: bool, augmentation: bool) -> DataLoader:
    """Gets a DataLoader from an NGCNpzReader, an edge and a train cfg"""
    general_augmentation = []
    node_specific_augmentation = None
    if augmentation and "augmentation" in train_cfg and "general" in train_cfg["augmentation"]:
        for name, args in train_cfg["augmentation"]["general"].items():
            general_augmentation.append(get_augmentation(name, **args))

    edge_reader = EdgeReader(reader.path, reader.nodes, edge, edge.getInKeys(), \
        general_augmentation, node_specific_augmentation)
    edge_loader = edge_reader.toDataLoader(batchSize=train_cfg["batchSize"], \
        randomize=randomize, debug=debug, seed=train_cfg["seed"])
    return edge_loader

class EdgeTrainer(ABC):
    def __init__(self, model: NGC):
        self.model = model

    @staticmethod
    def getEdgeDirName(edge: Edge) -> str:
        if isinstance(edge, SingleLink):
            suffix = f"{edge.inputNode}_{edge.outputNode}"
        elif isinstance(edge, TwoHopsNoGT):
            suffix = f"{edge.singleLinkNode}_{edge.inputNode}_{edge.outputNode}"
        elif isinstance(edge, SingleLinkResidual):
            suffix = f"{edge.residualNode}+{edge.inputNode}_{edge.outputNode}"
        elif isinstance(edge, TwoHopsResidualNoGT):
            suffix = f"{edge.residualNode}+{edge.singleLinkNode}_{edge.inputNode}_{edge.outputNode}"
        else:
            assert False, f"Unknown edge {edge} of type {type(edge)}."
        name = f"{edge.prefix}_{suffix}"
        return name

    @abstractmethod
    def run(self, trainCfg: Dict, trainReader: NGCNpzReader, validationReader: NGCNpzReader, debug: bool):
        pass
    
    def __call__(self, *args, **kwargs):
        self.run(*args, **kwargs)
