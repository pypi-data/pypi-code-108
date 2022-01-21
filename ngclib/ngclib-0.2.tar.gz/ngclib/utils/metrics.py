import numpy as np
import torch as tr
import torch.nn.functional as F
from typing import Dict
from collections import OrderedDict
from sklearn.metrics import f1_score, jaccard_score
from torchmetrics.functional import accuracy
from nwgraph import Node
from nwutils.torch import npToTrCall

from ..nodes import Semantic

# For a given node with a set of predictions and GT, return all the node's metrics.
# Some hardcoded stuff for Semantic, until we figure out if we can generalize it better.
def getMetrics(y:np.ndarray, t:np.ndarray, node:Node) -> Dict:
    if isinstance(node, Semantic):
        if y.shape[-1] == node.numClasses:
            argMaxY = np.argmax(y, -1)
        else:
            argMaxY = y
        argMaxY = argMaxY.astype(np.uint8).flatten()
        oneHotY = F.one_hot(tr.from_numpy(argMaxY).type(tr.int64), node.numClasses).type(tr.float32)

        if t.shape[-1] == node.numClasses:
            argMaxT = np.argmax(t, -1).astype(np.uint8)
        else:
            argMaxT = t.astype(np.uint8)
        argMaxT = argMaxT.astype(np.uint8).flatten()
        oneHotT = F.one_hot(tr.from_numpy(argMaxT).type(tr.int64), node.numClasses).type(tr.float32)

        Loss = node.getNodeCriterion()(oneHotY, oneHotT)
        metrics = {
            "Accuracy": lambda y, t: float(accuracy(tr.from_numpy(argMaxY), tr.from_numpy(argMaxT))),
			"Mean IoU": lambda y, t : jaccard_score(argMaxY, argMaxT, average=None, labels=range(node.numClasses)),
			"F1 Score": lambda y, t : f1_score(argMaxY, argMaxT, average=None, labels=range(node.numClasses)),
        }
    else:
        Loss = npToTrCall(node.getNodeCriterion(), y, t)
        metrics = node.getNodeMetrics()
    res = {k:metrics[k](y, t) for k in metrics.keys()}
    newRes = OrderedDict()
    newRes["Loss"] = float(Loss)
    for k in res:
        if isinstance(res[k], np.ndarray):
            newRes[k] = list(res[k])
            newRes[f"{k} (mean)"] = res[k].mean()
        else:
            newRes[k] = res[k]
    return newRes
