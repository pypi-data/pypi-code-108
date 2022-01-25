import torch as tr
import numpy as np
from pathlib import Path
from natsort import natsorted
from typing import List, Dict
from nwgraph import Node
from torch.utils.data import Dataset, DataLoader, Subset
from collections import OrderedDict
from media_processing_lib.image import image_resize
from .transforms import defaultTransform, semanticSegmentationTransform, depthTransform
from ..nodes import *
from ..logger import logger
from ..utils import loadNpz

def getDataTransform(node):
	if isinstance(node, RGB):
		return defaultTransform
	elif isinstance(node, Depth):
		return depthTransform
	elif isinstance(node, Semantic):
		return semanticSegmentationTransform
	elif isinstance(node, CameraNormal):
		return defaultTransform
	elif isinstance(node, Normal):
		return defaultTransform
	assert False, f"Unknown node: '{node}'"

class NGCNpzReader(Dataset):
	def __init__(self, path: Path, nodes: List[Node], gtNodes: List[Node]):
		self.path = Path(path).absolute()
		self.inFiles = self.buildDataset(self.path, nodes)
		self.transforms = {x.name: getDataTransform(x) for x in nodes}
		self.nodes = nodes
		self.gtNodes = gtNodes
		self.nameToNode = {x.name: x for x in nodes}

	# For Npy reader, we expect a structure of:
	# baseDir/
	#   dataDim1/0.npz, ..., N.npz
	#   ...
	#   dataDimM/0.npz, ..., N.npz
	def buildDataset(self, path: Path, nodes: List[Node]) -> Dict[str, List[Path]]:
		logger.debug(f"Building dataset from: '{path}'")
		logger.debug(f"Nodes: {nodes}")
		inFiles = OrderedDict()
		for node in nodes:
			Dir = path / node.name
			items = [x for x in Dir.glob("*.npz")]
			items = natsorted([str(x) for x in items])
			inFiles[node.name] = items
		Lens = [len(x) for x in inFiles.values()]
		assert np.std(Lens) == 0, f"Lens: {dict(zip(nodes, Lens))}"
		assert len(inFiles) > 0
		logger.debug(f"Found {Lens[0]} images")
		return inFiles

	def getNodeItem(self, node: Node, index: int) -> np.ndarray:
		item = loadNpz(self.inFiles[node.name][index])
		item = image_resize(item, height=240, width=426, only_uint8=False)
		transformedItem = self.transforms[node.name](item, node)
		return transformedItem

	def __getitem__(self, index: int):
		result = {}
		# By default we put all nodes' data in "data" key
		for node in self.nodes:
			result[node.name] = self.getNodeItem(node, index)
		return result

	def __len__(self) -> int:
		return len(self.inFiles[list(self.nodes)[0].name])

	def mergeFn(self, x):
		# Basic merge function. Just stack all arrays received from __getitem__(ix) and return same thing in data and
		#  labels dicts for further use.
		Keys = x[0].keys()
		res = {k: np.array([y[k] for y in x], dtype=np.float32) for k in Keys}
		return {"data": res, "labels": res}

	def toDataLoader(self, batchSize: int=1, randomize: bool=False, numWorkers: int=None, \
			debug: bool=False, seed: int=None):
		reader = self
		numWorkers = 4 if numWorkers is None and debug is False else 0
		g = None
		if debug:
			reader = Subset(reader, list(range(0, 5)))
		if seed is not None:
			g = tr.Generator()
			g.manual_seed(seed)
		loader = DataLoader(reader, batch_size=batchSize, shuffle=randomize, \
			collate_fn=self.mergeFn, num_workers=numWorkers, generator=g)
		return loader
