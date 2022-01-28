import numpy as np
from .others import tryFn

# @brief A more detailed printer about numpy arrays.
def npGetInfo(data:np.ndarray) -> str:
	return "Shape: %s. Min: %s. Max: %s. Mean: %s. Std: %s. Dtype: %s" % \
		(data.shape, np.min(data), np.max(data), np.mean(data), np.std(data), data.dtype)

# @brief Pad the last dimension of a list (of lists) to the highest member of those outer lists.
# Example:
# a = [[[1,2], [1,2,3]], [[1,2,3,4], [1,2,3]], [[1,2], [1]]]
# This list has a shape of 2x2xVariable length. This is a prerequisite, only the last dimension must be paddable.
# This array can be converted to a numpy array of shape 2x2xMaxLastDim
# First we compute the max on the last dim, by flattening the entire array.
# We get the following lengths: [2 3 4 3 2 1]. Therefore, our array will have shape 2x2x4.
def npPadToHighestLastDim(l:np.ndarray) -> np.ndarray:
	l2 = np.array(l)
	# If arrays match well, no need to do anything.
	if l2.dtype != np.object:
		return l2.astype(np.float32)

	l2Flattened = l2.flatten()
	lengths = np.zeros((len(l2Flattened)), dtype=np.int32)

	for i in range(len(l2Flattened)):
		assert type(l2Flattened[i]) in (list, np.ndarray)
		lengths[i] = len(l2Flattened[i])

	maxLength = lengths.max()
	newArray = np.zeros((*l2Flattened.shape, maxLength), dtype=np.float32)
	for i in range(len(lengths)):
		newArray[i, 0 : lengths[i]] = l2Flattened[i]
	newArray = newArray.reshape((*l2.shape, maxLength))
	return newArray

# @bried Tries to read a npy file multiple times.
def tryReadNpy(file:str, allow_pickle:bool=False, count:int=5):
	return tryFn(np.load, N=count, file=file, allow_pickle=False)
