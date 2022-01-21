import sys
import yaml
import importlib
import torch as tr
from typing import List
from pathlib import Path
from nwmodule import NWModule
from nwgraph import Node
from ..logger import logger

device = tr.device("cuda") if tr.cuda.is_available() else tr.device("cpu")

class NetworkSelection:
    def __init__(self, vote:List):
        assert len(vote) == 5
        assert vote[0] == "networkSelection"
        assert Path(vote[2]).exists(), f"Vote: Path to model module '{vote[2]}' doesn't exist"
        assert Path(vote[3]).exists(), f"Vote: Path to model cfg '{vote[3]}' doesn't exist"
        assert Path(vote[4]).exists(), f"Vote: Path to model weights '{vote[4]}' doesn't exist"
        logger.debug(f"Loading model from module '{vote[2]}', model '{vote[1]}', cfg '{vote[3]}', weights '{vote[4]}'")
        self.vote = vote
        self.model = self.getModel(vote)

    def getModel(self, vote:List) -> NWModule:
        _, modelName, modelModulePath, modelCfg, modelWeights = vote
        spec = importlib.util.spec_from_file_location("module.name", modelModulePath)
        sys.path.append(str(Path(modelModulePath).parents[0]))
        foo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(foo)
        modelType = getattr(foo, modelName)
        model = modelType(yaml.safe_load(open(modelCfg, "r")))
        model.setTrainableWeights(True)
        model.loadWeights(modelWeights)
        model.eval()
        model.to(device)
        return model

    def __call__(self, node:Node, messages:tr.Tensor):
        return self.model(node, messages)
