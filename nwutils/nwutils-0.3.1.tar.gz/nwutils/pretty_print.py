import h5py
import numpy as np
from typing import Dict
from collections import OrderedDict

def prettyPrint(d:Dict, depth:int=0):
	def prettyPrintDict(d:Dict, depth:int=0):
		pre = ("  " + "| "  * (depth - 1)) if depth > 1 else ("  " * depth)
		for k in d:
			if isinstance(d[k], dict):
				print(f"{pre}{k}")
				prettyPrint(d[k], depth + 1)
			elif isinstance(d[k], (tuple, list)):
				Len = len(d[k])
				# [1, 2, 3, ..., N-2, N-1, N]
				Str = d[k] if Len < 7 else "[" + f"{', '.join([str(x) for x in d[k][0 : 3]])}" + \
					'..., ' + f"{', '.join([str(x) for x in d[k][-3 :]])}" + "]"
				print(f"{pre}{k} -> {Str}. List. Length: {Len}")
			elif isinstance(d[k], np.ndarray):
				print(f"{pre}{k} -> {d[k]}. Array [{d[k].dtype}]. Shape: {d[k].shape}")
			elif isinstance(d[k], str):
				Len = len(d[k])
				print(f"{pre}{k} -> {d[k] if Len < 7 else d[k][0:3] + '...' + d[k][-3:]}. String. Length: {Len}")
			else:
				assert False

	def prettyPrintH5(data, depth:int=0):
		if type(data) in (h5py._hl.files.File, h5py._hl.group.Group):
			for key in data:
				print("\n%s- %s" % ("  " * level, key), end="")
				prettyPrintH5(data[key], level=level+1)
		elif type(data) == h5py._hl.dataset.Dataset:
			print("Shape: %s. Type: %s" % (data.shape, data.dtype), end="")
		else:
			assert False, "Unexpected type %s" % (type(data))

	if isinstance(d, (dict, OrderedDict)):
		prettyPrintDict(d, depth)
	elif isinstance(h5py._hl.files.File, h5py._hl.group.Group, h5py._hl.dataset.Dataset):
		prettyPrintH5(d, depth)
	else:
		assert False, "TODO"
