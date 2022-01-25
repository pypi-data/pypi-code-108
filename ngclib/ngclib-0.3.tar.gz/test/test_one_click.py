import yaml
import shutil
import tempfile
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
nodeTypes: [RGB, Semantic, Depth]
nodeNames: [rgb, semantic, depth]
inputNodes: [rgb]
edges: [ # Edges are defined using the names of the nodes
    [rgb, semantic],
    [rgb, depth],
    [depth, semantic]
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
  depth:
    maxDepthMeters: 1
"""

graphV2CfgStr = """
graphConfig: NGC-V2-Residual
nodeTypes: [RGB, HSV, Semantic, Depth]
nodeNames: [rgb, hsv, semantic, depth]
inputNodes: [rgb, hsv]
residualNode: rgb
edges: [
  [rgb, depth],
  [rgb, semantic],
  [hsv, depth],
  [rgb, semantic, depth],
  [hsv, depth, semantic]
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
  depth:
    maxDepthMeters: 1
"""

trainCfgStr = """
seed: 42
batchSize: 10
numEpochs: 3
optimizer:
  type: adamw
  args:
    lr: 0.01
scheduler:
  type: ReduceLRAndBacktrackOnPlateau
  args:
    metricName: Loss
    patience: 10
    factor: 2
EarlyStopping:
  metricName: Loss
  min_delta: 0
  patience: 10
  percentage: False
"""

def generateData():
    # Generate data
    global tmpDirName
    if tmpDirName is None:
        if __name__ == "__main__":
            tmpDirName = Path("/tmp/tmp8mddpuw9")
        else:
            tmpDirName = Path(tempfile.TemporaryDirectory().name)
    print(tmpDirName)
    if not (tmpDirName / "iter1/data").exists():
        generateRandomData(baseDir=tmpDirName / "iter1/data", representations=["rgb", "hsv", "depth", "semantic"], \
            dims=[3, 3, 1, 12], types=["float", "float", "float", "categorical"], resolution=(240, 426), \
            N=80, prefix="train_")
    if not (tmpDirName / "validation").exists():
        generateRandomData(baseDir=tmpDirName / "validation", representations=["rgb", "hsv", "depth", "semantic"], \
            dims=[3, 3, 1, 12], types=["float", "float", "float", "categorical"], resolution=(240, 426), N=20)
    if not (tmpDirName / "semisupervised").exists():
        generateRandomData(baseDir=tmpDirName / "semisupervised", representations=["rgb", "hsv"], dims=[3, 3], \
            types=["float", "float"], resolution=(240, 426), N=100)
    return tmpDirName

def cleanup(baseDir: Path):
    shutil.rmtree(baseDir/"iter1/models") if (baseDir/"iter1/models").exists() else None
    shutil.rmtree(baseDir/"iter2") if (baseDir/"iter2").exists() else None
    shutil.rmtree(baseDir/"iter3") if (baseDir/"iter3").exists() else None

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

class _HSV(HSV, IdentityNode):
    def __init__(self, numDims, *args, **kwargs):
        HSV.__init__(self, *args, **kwargs)
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
        if nodeName == "rgb":
            node = _RGB(3, **nodeParams)
        elif nodeName == "hsv":
            node = _HSV(3, **nodeParams)
        elif nodeName == "depth":
            node = _Depth(1, **nodeParams)
        elif nodeName == "semantic":
            node = _Semantic(nodeParams["semanticClasses"], **nodeParams)
        else:
            assert False, nodeName
        nodes.append(node)
    return nodes

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

    del model
    cleanup(baseDir)

class TestOneClick:
    def test_one_click_v1(self):
        trainCfg = yaml.safe_load(trainCfgStr)
        graphCfg = yaml.safe_load(graphV1CfgStr)
        train(trainCfg, graphCfg)

    def test_one_click_v2(self):
        trainCfg = yaml.safe_load(trainCfgStr)
        graphCfg = yaml.safe_load(graphV2CfgStr)
        train(trainCfg, graphCfg)

if __name__ == "__main__":
    TestOneClick().test_one_click_v1()
    TestOneClick().test_one_click_v2()
