from typing import Dict
from functools import partial
import numpy as np
from pathlib import Path
from nwgraph import Edge
from nwmodule.trainer import setup_module_for_train
from nwmodule.callbacks import RandomPlotEachEpoch
from media_processing_lib.image import image_write
from nwutils.torch import trGetData, trToDevice, npGetData

from ..models.edges import TwoHopsNoGT, TwoHopsResidualNoGT, SingleLink, SingleLinkResidual
from ..utils import buildNodePlotFn

def edge_plot_fn(x: np.ndarray, y: np.ndarray, t: np.ndarray, workingDirectory: Path, edge: Edge):
    cnt = 0
    MB = len(t)
    A, B = edge.getNodes()
    if isinstance(edge, (SingleLink, SingleLinkResidual)):
        """For single links, we have access to the input data, so we plot that."""
        x = x[edge.inputNode.name]
    elif isinstance(edge, (TwoHopsNoGT, TwoHopsResidualNoGT)):
        """For TwoHops, we need to propagate through the single link first, so we get intermediate the prediction."""
        x = trToDevice(trGetData(x), edge.getDevice())
        x = edge.singleLinkEdge.networkAlgorithm(x, None, False, False)[0]
    else:
        assert False, f"Unknown edge: {edge}."

    x, y, t = npGetData([x, y, t])
    for i in range(MB):
        xImage = buildNodePlotFn(A)(x[i])
        yImage = buildNodePlotFn(B)(y[i])
        tImage = buildNodePlotFn(B)(t[i])

        stack = np.concatenate([xImage, yImage, tImage], axis=1)
        image_write(stack, f"{workingDirectory}/{cnt}.png")
        cnt += 1

def setup_edge(edge: Edge, trainCfg: Dict, weightsDir: Path):
    setup_module_for_train(edge, trainCfg)
    if isinstance(edge, (TwoHopsNoGT, TwoHopsResidualNoGT)):
        from .edge_trainer import EdgeTrainer
        edge.setup(singleLinkDir = weightsDir / EdgeTrainer.getEdgeDirName(edge.singleLinkEdge))
    assert edge.getNumParams()[1] > 0, f"Edge '{edge}' has no trainable params."

    edge.addCallback(RandomPlotEachEpoch(partial(edge_plot_fn, edge=edge)))
