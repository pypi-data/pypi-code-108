from typing import Callable
from functools import partial
import numpy as np
from matplotlib.cm import plasma
from media_processing_lib.image import to_image
from nwgraph import Node
from ..nodes import *

# Semantic data may come as argmaxed or one-hot, depending on how we store them (raw predictions
#  or compressed results).
def semanticToImage(x: np.ndarray, node: Semantic) -> np.ndarray:
	assert len(node.semanticClasses) == len(node.semanticColors)
	if len(x.shape) == 3 and x.shape[-1] != 1:
		assert len(node.semanticClasses) == x.shape[-1], f"{len(node.semanticClasses)} vs {x.shape}"
		x = np.argmax(x, axis=-1)
	nClasses = len(node.semanticClasses)
	assert x.max() < nClasses
	newImage = np.zeros((*x.shape, 3), dtype=np.uint8)
	for i in range(nClasses):
		newImage[x == i] = node.semanticColors[i]
	newImage = to_image(newImage)
	return newImage

def depthToImage(x: np.ndarray, node: Depth) -> np.ndarray:
	a = np.clip(x, 0, 1).squeeze()
	b = plasma(a)[..., 0 : 3]
	c = to_image(b)
	return c

def normalToImage(x: np.ndarray, node: Normal) -> np.ndarray:
	# TODO: if normals are not just unit vectors, but sin/cos or w/e else is predicted.
	return default(x, x)

def default(x: np.ndarray, node: Node) -> np.ndarray:
	x = np.clip(x, 0, 1)
	x = to_image(x)
	return x

def nullToBlackImage(x: np.ndarray, node: NullNode) -> np.ndarray:
	assert len(x.shape) == 3
	return np.zeros((x.shape[0], x.shape[1], 3), dtype=np.uint8)

def buildNodePlotFn(node: Node) -> Callable:
	if isinstance(node, RGB):
		fn = default
	elif isinstance(node, Depth):
		fn = depthToImage
	elif isinstance(node, Semantic):
		fn = semanticToImage
	elif isinstance(node, Normal):
		fn = normalToImage
	elif isinstance(node, NullNode):
		fn = nullToBlackImage
	else:
		assert False, f"Unknown node: '{node}' (type: {type(node)})"
	fn = partial(fn, node=node)
	return fn
