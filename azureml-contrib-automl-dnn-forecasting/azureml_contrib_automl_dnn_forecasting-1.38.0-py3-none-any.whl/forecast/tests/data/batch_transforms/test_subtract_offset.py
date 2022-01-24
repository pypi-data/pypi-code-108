import copy

import pytest
import torch

from forecast.data.batch_transforms import BatchSubtractOffset
from forecast.data import FUTURE_DEP_KEY, FUTURE_IND_KEY, PAST_DEP_KEY, PAST_IND_KEY


@pytest.mark.parametrize("f_ind", [0, 2, [0, 1, 2], {0:0, 1:1}, [1, 2], {0: 1, 1: 2}])
@pytest.mark.parametrize("inplace", [True, False])
def test_batch_subtract_offset(f_ind, inplace):
    torch.manual_seed(0)
    batch_size = 8
    forecast_window = 12
    forecast_horizon = 6
    regressands = 3
    scale = 1
    batch = {
        PAST_IND_KEY: torch.rand(batch_size, 4, forecast_window) * scale,
        PAST_DEP_KEY: torch.rand(batch_size, regressands, forecast_window) * scale,
        FUTURE_IND_KEY: torch.rand(batch_size, 2, forecast_horizon) * scale,
        FUTURE_DEP_KEY: torch.rand(batch_size, regressands, forecast_horizon) * scale,
    }
    orig_batch = copy.deepcopy(batch)

    batch_so = BatchSubtractOffset(f_ind)
    tf_batch = batch_so.do(batch, inplace=inplace)

    assert (tf_batch is batch) == inplace
    assert (batch[PAST_DEP_KEY] is tf_batch[PAST_DEP_KEY]) == inplace
    assert (batch[FUTURE_DEP_KEY] is tf_batch[FUTURE_DEP_KEY]) == inplace
    assert batch[PAST_IND_KEY] is tf_batch[PAST_IND_KEY]
    assert batch[FUTURE_IND_KEY] is tf_batch[FUTURE_IND_KEY]
    assert batch_so._offset_key in tf_batch

    assert tf_batch[PAST_DEP_KEY].shape == orig_batch[PAST_DEP_KEY].shape
    assert tf_batch[FUTURE_DEP_KEY].shape == orig_batch[FUTURE_DEP_KEY].shape

    p_keys = list(batch_so.index_mapping.keys())
    f_keys = list(batch_so.index_mapping.values())
    np_keys = [i for i in range(regressands) if i not in p_keys]
    nf_keys = [i for i in range(regressands) if i not in f_keys]

    assert (tf_batch[PAST_DEP_KEY][:, p_keys, -1] == 0).all()
    assert (tf_batch[PAST_DEP_KEY][:, p_keys, :] < orig_batch[PAST_DEP_KEY][:, p_keys, :]).all()
    assert torch.equal(tf_batch[PAST_DEP_KEY][:, np_keys, :], orig_batch[PAST_DEP_KEY][:, np_keys, :])
    assert torch.allclose(
        tf_batch[PAST_DEP_KEY][:, p_keys, :] + orig_batch[PAST_DEP_KEY][:, p_keys, -1].unsqueeze(-1),
        orig_batch[PAST_DEP_KEY][:, p_keys, :],
    )

    assert (tf_batch[FUTURE_DEP_KEY][:, f_keys, :] < orig_batch[FUTURE_DEP_KEY][:, f_keys, :]).all()
    assert torch.equal(tf_batch[FUTURE_DEP_KEY][:, nf_keys, :], orig_batch[FUTURE_DEP_KEY][:, nf_keys, :])
    assert torch.allclose(
        tf_batch[FUTURE_DEP_KEY][:, f_keys, :] + orig_batch[PAST_DEP_KEY][:, p_keys, -1].unsqueeze(-1),
        orig_batch[FUTURE_DEP_KEY][:, f_keys, :],
    )

    tmp = copy.deepcopy(tf_batch)
    tf_y = tmp[FUTURE_DEP_KEY]
    utf_y = batch_so.undo_y(tf_y, tmp, inplace=inplace)
    assert (utf_y is tf_y) == inplace
    assert torch.allclose(utf_y, orig_batch[FUTURE_DEP_KEY], rtol=1e-3)

    utf_batch = batch_so.undo(tf_batch, inplace=inplace)
    assert (utf_batch is tf_batch) == inplace
    assert (utf_batch[PAST_DEP_KEY] is tf_batch[PAST_DEP_KEY]) == inplace
    assert (utf_batch[FUTURE_DEP_KEY] is tf_batch[FUTURE_DEP_KEY]) == inplace
    assert batch[PAST_IND_KEY] is tf_batch[PAST_IND_KEY]
    assert batch[FUTURE_IND_KEY] is tf_batch[FUTURE_IND_KEY]

    assert torch.allclose(utf_batch[PAST_DEP_KEY][:, p_keys, :], orig_batch[PAST_DEP_KEY][:, p_keys, :])
    assert torch.equal(utf_batch[PAST_DEP_KEY][:, np_keys, :], orig_batch[PAST_DEP_KEY][:, np_keys, :])
    assert torch.allclose(utf_batch[FUTURE_DEP_KEY][:, f_keys, :], orig_batch[FUTURE_DEP_KEY][:, f_keys, :])
    assert torch.equal(utf_batch[FUTURE_DEP_KEY][:, nf_keys, :], orig_batch[FUTURE_DEP_KEY][:, nf_keys, :])
