import numpy as np
from nwgraph import Node

def defaultTransform(x: np.ndarray, node: Node) -> np.ndarray:
    x = np.float32(x)
    if len(x.shape) == 2:
        x = np.expand_dims(x, axis=-1)
    return x

def depthTransform(x: np.ndarray, node: Node) -> np.ndarray:
    if x.shape[-1] != 1:
        x = np.expand_dims(x, axis=-1)
    return np.float32(x)

def wireframeTransform(x: np.ndarray, node: Node) -> np.ndarray:
    x = x[..., 0 : 1]
    x = np.float32(x > 0)
    return x

def semanticSegmentationTransform(x: np.ndarray, node: Node) -> np.ndarray:
    semanticClasses = node.semanticClasses
    semanticClasses = semanticClasses if isinstance(semanticClasses, list) else list(range(semanticClasses))
    assert x.dtype in (np.uint8, np.uint16, np.uint32, np.int), x.dtype
    assert x.max() <= len(semanticClasses) - 1, f"{x.max()} vs {len(semanticClasses)}"
    if x.shape[-1] == 1:
        x = x[..., 0]
    # toCategorical
    y = np.eye(len(semanticClasses))[x]
    y = np.float32(y)
    return y
