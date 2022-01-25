import torch as tr
from typing import Dict, List
from .ngc import NGC
from .ngc_v1 import NGCAAAI2020, NGCV1
from .ngc_v2_residual import NGCV2Residual
from nwgraph import Node

device = tr.device("cuda") if tr.cuda.is_available() else tr.device("cpu")

def getModel(nodes:List[Node], cfg:Dict) -> NGC:
	modelType = cfg["graphConfig"]
	if modelType == "NGC_AAAI2020":
		model = NGCAAAI2020(nodes=nodes, cfg=cfg)
	elif modelType == "NGC-V1":
		model = NGCV1(nodes=nodes, cfg=cfg)
	elif modelType == "NGC-V2-Residual":
		model = NGCV2Residual(nodes=nodes, cfg=cfg)
	else:
		assert False, f"Unknown model: {modelType}"
	model.setTrainableWeights(True)
	model = model.to(device)
	return model
