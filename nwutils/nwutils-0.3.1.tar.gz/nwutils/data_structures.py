import numpy as np
from typing import Any
from collections import OrderedDict

# Deep check if two items are equal. Dicts are checked value by value and numpy array are compared using np.allclose
def deepCheckEqual(a, b) -> bool:
	assert type(a) == type(b), f"Types {type(a)} and {type(b)} differ."

	Type = type(a)
	if isinstance(a, (dict, OrderedDict)):
		for key in a:
			if not deepCheckEqual(a[key], b[key]):
				return False
		return True
	elif isinstance(a, np.ndarray):
		if not len(a) == len(b):
			return False

		if np.issubdtype(a.dtype, np.number):
			return np.allclose(a, b)

		for i in range(len(a)):
			if not deepCheckEqual(a[i], b[i]):
				return False
		return True
	elif isinstance(a, (list, tuple)):
		if not len(a) == len(b):
			return False

		for i in range(len(a)):
			if not deepCheckEqual(a[i], b[i]):
				return False
		return True
	return a == b
