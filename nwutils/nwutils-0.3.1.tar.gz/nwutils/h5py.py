import h5py
import numpy as np
from typing import Any, Dict
from .index import smartIndexWrapper

# @brief Used by H5BatchedDataset for default dimGetter when it's not provided for some data dim.
def defaultH5DimGetter(dataset:h5py._hl.group.Group, index:Any, dim:str):
	if isinstance(index, (range, slice)):
		return dataset[dim][index.start:index.stop][()]
	elif isinstance(index, (np.ndarray, list, tuple)):
		return smartIndexWrapper(dataset[dim], index)
	assert False, "Unknown type: %s" % type(index)

def h5ExportToFile(filepath:str, results:Dict):
    file = h5py.File(filepath, "w")
    h5StoreDict(file, results)
    file.flush()
    return file

def h5StoreDict(file, data):
	assert type(data) == dict
	for key in data:
		# If key is int, we need to convert it to Str, so we can store it in h5 file.
		sKey = str(key) if type(key) == int else key

		if type(data[key]) == dict:
			file.create_group(sKey)
			h5StoreDict(file[sKey], data[key])
		else:
			file[sKey] = data[key]

def h5ReadDict(data, N=None):
	if type(data) in (h5py._hl.files.File, h5py._hl.group.Group):
		res = {}
		for key in data:
			res[key] = h5ReadDict(data[key], N=N)
	elif type(data) == h5py._hl.dataset.Dataset:
		if N is None:
			res = data[()]
		elif type(N) is int:
			res = data[0 : N]
		elif type(N) in (list, np.ndarray):
			res = smartIndexWrapper(data, N)
	else:
		assert False, "Unexpected type %s" % (type(data))
	return res
