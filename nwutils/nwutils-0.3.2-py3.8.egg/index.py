import numpy as np
from typing import List, Union

# Flatten the indexes [[1, 3], [15, 13]] => [1, 3, 15, 13] and then calls f(data, 1), f(data, 3), ..., step by step
def smartIndexWrapper(data:Union[List, np.ndarray], indexes:List[int], f = lambda data, index : data[index]):
	# Flatten the indexes [[1, 3], [15, 13]] => [1, 3, 15, 13]
	indexes = np.array(indexes, dtype=np.uint32)
	flattenedIndexes = indexes.flatten()
	N = len(flattenedIndexes)
	assert N > 0

	result = []
	for i in range(N):
		result.append(f(data, flattenedIndexes[i]))
	finalShape = (*indexes.shape, *result[0].shape)
	result = np.array(result).reshape(finalShape)
	return result