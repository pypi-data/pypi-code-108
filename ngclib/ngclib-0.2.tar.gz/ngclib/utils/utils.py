from functools import lru_cache
from typing import List, Tuple, Any, Dict
from collections import OrderedDict 
import numpy as np
from pathlib import Path
from nwgraph import Node
from ..logger import drange, logger
from ..nodes import *


@lru_cache
def loadNpz(path: Path) -> np.ndarray:
    """Loads a NPZ given a path. Caveats for VRE exported npz."""
    try:
        item = np.load(path, allow_pickle=True)["arr_0"]
    except Exception as e:
        print(f"Error at reading file '{path}'.")
        raise Exception(e)
    # For items exported using VRE.
    if item.dtype == object:
        item = item.item()
        assert isinstance(item, dict)
        assert "data" in item
        item = item["data"]
    assert item.dtype in (np.uint8, np.uint32, np.float16, np.float32, np.float64), f"Got {item.dtype} for {path}"
    if item.shape[0] == 1:
        item = item[0]
    if item.shape[-1] == 1:
        item = item[..., 0]
    return item

def loadNpzFromList(paths: List[Path]) -> np.ndarray:
    """Loads a list of npz given a list of paths using loadNpz function."""
    items = []
    for i in drange(len(paths), desc="Loading Npz"):
        item = loadNpz(paths[i])
        items.append(item)
    items = np.array(items).astype(np.float32)
    return items

def generateRandomData(baseDir: Path, representations: List[str], dims: List[int], types: List[str], \
        resolution: Tuple[int, int], N: int, prefix: str=""):
    """Generates a dataset in ngcdir format"""
    baseDir.mkdir(exist_ok=False, parents=True)
    for i in drange(len(representations)):
        representation = representations[i]
        H, W, D = resolution[0], resolution[1], dims[i]
        (baseDir / representation).mkdir()
        if types[i] == "float":
            data = np.random.rand(N, H, W, D).astype(np.float32)
        elif types[i] == "categorical":
            data = np.random.randint(0, D-1, size=(N, H, W)).astype(np.uint32)
        else:
            assert False
        for j in drange(N, desc=representation):
            outFile = baseDir / representation / (f"{prefix}{j}.npz")
            np.savez_compressed(outFile, data[j])

def getFakeNodeType(nodeType: type) -> type:
    """Given a non-instantaible node from this library, create a fake node that implements the getEncoder and
    getDecoder methods.
    """
    class FakeNode(nodeType):
        def getEncoder(self, outputNode):
            pass
        def getDecoder(self, inputNode):
            pass
    return FakeNode

def instantiateNodes(names: List[str], types: List[str],
        nodesHyperparameters: Dict[str, Dict[str, Any]]={}) -> List[Node]:
    """Instantiates a list of nodes, given names and types and, optionally, hyperparameters"""

    res = OrderedDict()
    resList = []
    for name, type in zip(names, types):
        nodeType = globals()[type]
        nodeParams = {} if (nodesHyperparameters is None or name not in nodesHyperparameters.keys()) \
            else nodesHyperparameters[name]
        if name in res:
            logger.debug(f"Node '{name}' already instantiated! Copying.")
            node = res[name]
            assert isinstance(node, nodeType), "Instantaited node has different type."
        else:
            try:
                node = nodeType(**nodeParams)
            except Exception:
                logger.debug(f"Cannot instantaite '{name}' (type: {nodeType}). "
                    "Creating a fake node and trying again.")
                node = getFakeNodeType(nodeType)(**nodeParams)
        res[name] = node
        resList.append(node)
    return resList
