import numpy as np
import pytest
import torch

from forecast.data.transforms import OneHotEncode


NUM_VALS1 = (8, 4, 2)
NUM_VALS2 = (9, 3)
EMBED_INDICES = [2, 3, 4, 6, 7]

TS_LEN = 90
TEST_ARRAYS = [np.vstack([np.random.rand(2, 90).astype(np.float32),
                          *[np.random.randint(max_val, size=(1, TS_LEN)) for max_val in NUM_VALS1],
                          np.random.rand(1, 90).astype(np.float32),
                          *[np.random.randint(max_val, size=(1, TS_LEN)) for max_val in NUM_VALS2]]) for _ in range(5)]
TEST_TENSORS = [torch.cat([torch.rand(2, 90),
                           *[torch.randint(max_val, size=(1, TS_LEN)).type(torch.float32) for max_val in NUM_VALS1],
                           torch.rand(1, 90),
                           *[torch.randint(max_val, size=(1, TS_LEN)).type(torch.float32) for max_val in NUM_VALS2]],
                          dim=0) for _ in range(5)]


@pytest.mark.parametrize('x', TEST_ARRAYS + TEST_TENSORS)
@pytest.mark.parametrize('drop_first', [False, True])
def test_consistency(x, drop_first):
    key = 'FOO'
    encode = OneHotEncode(EMBED_INDICES, NUM_VALS1+NUM_VALS2, drop_first=drop_first, key=key)
    sample = {key: x}
    print(len(x))
    assert (encode.undo(encode(sample))[key] == sample[key]).all()
