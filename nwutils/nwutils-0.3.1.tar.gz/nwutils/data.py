from numbers import Number
from typing import Optional
import numpy as np

def minMax(x:np.ndarray, Min:Optional[Number]=None, Max:Optional[Number]=None) -> np.ndarray:
	x = x.astype(np.float32)
	if Min is None:
		Min = x.min()
	if Max is None:
		Max = x.max()
	return (x - Min) / (Max - Min + np.spacing(1))

def minMaxPercentile(x:np.ndarray, low:int=0, high:int=100) -> np.ndarray:
	Min, Max = np.percentile(x, [low, high])
	x = np.clip(x, Min, Max)
	return minMax(x)

def standardize(x:np.ndarray, Mean:Optional[Number]=None, Std:Optional[Number]=None) -> np.ndarray:
	x = x.astype(np.float32)
	if Mean is None:
		Mean = x.mean()
	if Std is None:
		Std = x.std()
	return (x - Mean) / (Std + np.spacing(1))

def standardizePercentile(x, low:int=0, high:int=100) -> np.ndarray:
	Min, Max = np.percentile(x, [low, high])
	x = np.clip(x, Min, Max)
	return standardize(x)

def toCategorical(data:np.ndarray, numClasses:int) -> np.ndarray:
	data = np.array(data)
	y = np.eye(numClasses)[data.reshape(-1)].astype(np.uint8)
	# Some bugs for (1, 1) shapes return (1, ) instead of (1, NC)
	MB = data.shape[0]
	y = np.squeeze(y)
	if MB == 1:
		y = np.expand_dims(y, axis=0)
	y = y.reshape(*data.shape, numClasses)
	return y
