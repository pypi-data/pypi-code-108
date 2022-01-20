import numpy as np
from typing import List, Dict

def batchIndexFromBatchSizes(batchSizes:List[int]) -> List[slice]:
    # batchSizes = [4, 1, 2, 3], so batch[0] has a size of 4, batch[2] a size of 2 etc.
    # actual batches are obtained by cumsum on lens: [0, 4, 5, 7, 10]. cumsum[0] = [0, 4), cumsum[1] = [4, 5) etc.
    cumsum = np.insert(np.cumsum(batchSizes), 0, 0)
    # We can further slice these batches for faster access
    batches = [slice(cumsum[i], cumsum[i + 1]) for i in range(len(cumsum) - 1)]
    return batches

def getBatchIndexLen(batchIndex) -> int:
    if isinstance(batchIndex, slice):
        step = batchIndex.step if not batchIndex.step is None else 1
        N = batchIndex.stop - batchIndex.start
        B = N // step + (N % step != 0)
        return B
    else:
        try:
            return len(batchIndex)
        except Exception as e:
            assert False, f"Provide a way to find length of batches... Type: {type(batchIndex)}. Error: {e}"

def getBatchLens(batches:List):
    return [getBatchIndexLen(x) for x in batches]

def getBatchesAsIndices(batches):
    res = []
    for item in batches:
        if isinstance(item, slice):
            assert item.step is None
            item = np.arange(item.start, item.stop).astype(np.int32)
        if isinstance(item, (list, tuple)):
            item = np.array(item, dtype=np.int32)
        res.append(item)
    res = np.concatenate(res)
    return res

def defaultBatchFn(x:List[Dict]) -> Dict:
    def _merge(x:List):
        if isinstance(x[0], (int, float, complex, np.ndarray, np.number, list)):
            return mergeFinal(x)
        elif isinstance(x[0], dict):
            return mergeDict(x)
        elif isinstance(x[0], type(None)):
            return None
        else:
            assert False, f"Unknown type {type(x[0])}"

    def mergeFinal(x:List):
        return np.stack(x, axis=0)

    def mergeDict(x:List[Dict]):
        assert isinstance(x[0], dict)
        Keys = list(x[0].keys())
        N = len(x)
        res = {k: _merge([x[i][k] for i in range(N)]) for k in Keys}
        return res

    return _merge(x)
