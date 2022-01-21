from pathlib import Path
from typing import Dict
from natsort import natsorted
from functools import partial
from media_processing_lib.image import CollageMaker
from .node_plot_functions import buildNodePlotFn
from .utils import loadNpz
from ..nodes import *

class NGCCollageMaker(CollageMaker):
    def __init__(self, baseDir:Path, graphCfg:Dict, outputDir:Path):
        self.baseDir = Path(baseDir)
        self.graphCfg = graphCfg
        files, plotFns, names = self.setup()
        super().__init__(files=files, plotFns=plotFns, outputDir=outputDir, loadFns=loadNpz)

    def setup(self):
        files, names, plotFns = [], [], []
        for name, type in zip(self.graphCfg["nodeNames"], self.graphCfg["nodeTypes"]):
            nodeDir = self.baseDir / name
            assert nodeDir.exists(), f"Not found: '{nodeDir}'"
            nodeFiles = natsorted([str(x.absolute()) for x in nodeDir.glob("*.npz")])
            files.append(nodeFiles)

            # Hack a fake class so we can isntantiate the abstract classes
            Type = globals()[type]
            class _Node(Type):
                def getEncoder():
                    pass
                def getDecoder():
                    pass

            nodeParams = {} if not name \
                in self.graphCfg["hyperParameters"] else self.graphCfg["hyperParameters"][name]
            node = _Node(**nodeParams)
            names.append(name)
            plotFn = buildNodePlotFn(node)
            plotFns.append(plotFn)
        return files, plotFns, names
