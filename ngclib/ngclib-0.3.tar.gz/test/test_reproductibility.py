import yaml
import shutil
import os
import tempfile
import numpy as np
from typing import Dict, List
from pathlib import Path
from torch import nn
from ngclib import NGCDir
from ngclib.utils import generateRandomData
from ngclib.trainer import NGCTrainer
from ngclib.nodes import *
from ngclib.models import getModel
from nwgraph import Node

tmpDirName = None

graphV1CfgStr = """
graphConfig: NGC-V1
nodeTypes: [RGB, RGB, RGB, RGB, Semantic]
nodeNames: [rgb1, rgb2, rgb3, rgb4, semantic]
inputNodes: [rgb1, rgb2, rgb3, rgb4]
edges: [ # Edges are defined using the names of the nodes
    [rgb1, semantic],
    [rgb2, semantic],
    [rgb3, semantic],
    [rgb4, semantic],
]
voteFunction: simpleMean
hyperParameters:
  semantic:
    semanticClasses: 12
    semanticColors: [
      [0, 0, 0],
      [0, 0, 1],
      [0, 0, 2],
      [0, 0, 3],
      [0, 0, 4],
      [0, 0, 5],
      [0, 0, 6],
      [0, 0, 7],
      [0, 0, 8],
      [0, 0, 9],
      [0, 0, 10],
      [0, 0, 11],
    ]
"""

trainCfgStr = """
seed: 42
cudnn_determnisim: True
batchSize: 10
numEpochs: 3
optimizer:
  type: adamw
  args:
    lr: 0.01
scheduler:
  type: ReduceLROnPlateau
  args:
    metric: Loss
    patience: 10
    factor: 2
"""

def generateData():
    # Generate data
    global tmpDirName
    if tmpDirName is None:
        if __name__ == "__main__":
            tmpDirName = Path("/tmp/tmp8mddpuw8")
        else:
            tmpDirName = Path(tempfile.TemporaryDirectory().name)
    print(tmpDirName)
    if not (tmpDirName / "iter1/data").exists():
        generateRandomData(baseDir=tmpDirName / "iter1/data", representations=["rgb1", "semantic"], \
            dims=[3, 12], types=["float", "categorical"], resolution=(240, 426), N=20, prefix="train_")
    if not (tmpDirName / "validation").exists():
        generateRandomData(baseDir=tmpDirName / "validation", representations=["rgb1", "semantic"], \
            dims=[3, 12], types=["float", "categorical"], resolution=(240, 426), N=5)
    if not (tmpDirName / "semisupervised").exists():
        generateRandomData(baseDir=tmpDirName / "semisupervised", representations=["rgb1"], dims=[3, 3], \
            types=["float"], resolution=(240, 426), N=10)

    def f(a, b):
        if not (tmpDirName / b).exists():
            os.symlink(str(tmpDirName / a), str(tmpDirName / b))
    f((tmpDirName / "iter1/data/rgb1"), (tmpDirName / "iter1/data/rgb2"))
    f((tmpDirName / "iter1/data/rgb1"), (tmpDirName / "iter1/data/rgb3"))
    f((tmpDirName / "iter1/data/rgb1"), (tmpDirName / "iter1/data/rgb4"))
    f((tmpDirName / "validation/rgb1"), (tmpDirName / "validation/rgb2"))
    f((tmpDirName / "validation/rgb1"), (tmpDirName / "validation/rgb3"))
    f((tmpDirName / "validation/rgb1"), (tmpDirName / "validation/rgb4"))
    f((tmpDirName / "semisupervised/rgb1"), (tmpDirName / "semisupervised/rgb2"))
    f((tmpDirName / "semisupervised/rgb1"), (tmpDirName / "semisupervised/rgb3"))
    f((tmpDirName / "semisupervised/rgb1"), (tmpDirName / "semisupervised/rgb4"))
    return tmpDirName

class IdentityNode(Node):
    def __init__(self, numDims: int):
        self.numDims = numDims

    def getEncoder(self, decoderNode):
        return nn.Linear(in_features = self.numDims, out_features = decoderNode.numDims)

    def getDecoder(self, encoderNode):
        return nn.Identity()

class _RGB(RGB, IdentityNode):
    def __init__(self, numDims, *args, **kwargs):
        RGB.__init__(self, *args, **kwargs)
        IdentityNode.__init__(self, numDims)

class _Semantic(Semantic, IdentityNode):
    def __init__(self, numDims, *args, **kwargs):
        Semantic.__init__(self, *args, **kwargs)
        IdentityNode.__init__(self, numDims)

class _Depth(Depth, IdentityNode):
    def __init__(self, numDims, *args, **kwargs):
        Depth.__init__(self, *args, **kwargs)
        IdentityNode.__init__(self, numDims)

def getNodes(cfg: Dict) -> List[Node]:
    """Basic implementation of getNodes, creating a subtype for all required types by adding a linear projection
    for the encoder and identity for decoder.
    """
    nodes = []
    for i in range(len(cfg["nodeNames"])):
        nodeName = cfg["nodeNames"][i]
        nodeParams = {} if not nodeName in cfg["hyperParameters"] else cfg["hyperParameters"][nodeName]
        nodeParams["name"] = nodeName
        if nodeName in ("rgb1", "rgb2", "rgb3", "rgb4"):
            node = _RGB(3, **nodeParams)
        elif nodeName == "semantic":
            node = _Semantic(nodeParams["semanticClasses"], **nodeParams)
        else:
            assert False, nodeName
        nodes.append(node)
    return nodes

def cleanup(baseDir: Path):
    shutil.rmtree(baseDir/"iter1/models") if (baseDir/"iter1/models").exists() else None
    shutil.rmtree(baseDir/"iter2") if (baseDir/"iter2").exists() else None
    shutil.rmtree(baseDir/"iter3") if (baseDir/"iter3").exists() else None

def train(trainCfg, graphCfg):
    baseDir = generateData()
    cleanup(baseDir)
    ngcDir = NGCDir(baseDir, graphCfg)
    print(ngcDir)

    nodes = getNodes(graphCfg)
    print(f"Nodes: {nodes}")

    model = getModel(nodes, graphCfg)
    print(model.summary())

    trainer = NGCTrainer(model=model, ngcDirPath=baseDir, method="export_new_dataset_every_iteration", \
        trainCfg=trainCfg, trainDir=baseDir / "iter1/data", validationDir=baseDir / "validation", \
        semisupervisedDirs=[baseDir / "semisupervised"])
    trainer.run(startIteration=1, endIteration=2, parallelization=False, debug=False)

    cleanup(baseDir)
    return model

class TestReproductibility:
    def test_reproductibility_1(self):
        trainCfg = yaml.safe_load(trainCfgStr)
        graphCfg = yaml.safe_load(graphV1CfgStr)
        model = train(trainCfg, graphCfg)

        new_data = np.random.randn(10, 240, 426, 3).astype(np.float32)
        res = [edge.npForward(new_data) for edge in model.edges]
        assert np.std(res, axis=0).sum() <= 1e-3

if __name__ == "__main__":
    TestReproductibility().test_reproductibility_1()
