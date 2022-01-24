import copy

import torch
import pytest

from forecast.data import FUTURE_DEP_KEY, FUTURE_IND_KEY, PAST_DEP_KEY, PAST_IND_KEY
from forecast.data.batch_transforms.normalizer import BatchNormalizer, Normalizer, NormalizationMode


@pytest.mark.parametrize("inplace", [True, False])
def test_identity(inplace):
    x = torch.rand(8, 4, 12)
    norm = Normalizer(0, torch.tensor([0]), torch.tensor([1]), NormalizationMode.GLOBAL)
    y = x.detach().clone()
    z = norm.normalize(y, inplace=inplace)
    assert torch.equal(z, x)
    if not inplace:
        assert z is not y
    z2 = norm.denormalize(z, inplace=inplace)
    if not inplace:
        assert z2 is not z


@pytest.mark.parametrize("inplace", [True, False])
def test_positive_offset(inplace):
    f_ind = 0
    x, orig_inds = _get_tensor_and_inds(f_ind)
    norm = Normalizer(f_ind, torch.tensor([-2]), torch.tensor([1]), NormalizationMode.GLOBAL)
    y = x.detach().clone()
    y = norm.normalize(y, inplace=inplace)
    assert torch.all(y[:, f_ind, :] > x[:, f_ind, :])
    assert torch.equal(y[:, orig_inds, :], x[:, orig_inds, :])
    y = norm.denormalize(y, inplace=inplace)
    assert torch.allclose(x[:, f_ind, :], y[:, f_ind, :], rtol=1e-4)
    assert torch.equal(y[:, 1:, :], x[:, 1:, :])


@pytest.mark.parametrize("inplace", [True, False])
def test_negative_offset(inplace):
    f_ind = 1
    x, orig_inds = _get_tensor_and_inds(f_ind)
    norm = Normalizer(f_ind, torch.tensor([2]), torch.tensor([1]), NormalizationMode.GLOBAL)
    y = x.detach().clone()
    y = norm.normalize(y, inplace=inplace)
    assert torch.all(y[:, f_ind, :] < x[:, f_ind, :])
    assert torch.equal(y[:, orig_inds, :], x[:, orig_inds, :])
    y = norm.denormalize(y, inplace=inplace)
    try:
        assert torch.allclose(x[:, f_ind, :], y[:, f_ind, :], rtol=1e-4)
    except AssertionError:
        print(torch.abs(x[:, f_ind, :] - y[:, f_ind, :]).max())
        raise
    assert torch.equal(x[:, orig_inds, :], y[:, orig_inds, :])


@pytest.mark.parametrize("inplace", [True, False])
def test_positive_scalar(inplace):
    f_ind = 2
    x, orig_inds = _get_tensor_and_inds(f_ind)
    norm = Normalizer(f_ind, torch.tensor([0]), torch.tensor([10]), NormalizationMode.GLOBAL)
    y = x.detach().clone()
    y = norm.normalize(y, inplace=inplace)
    assert torch.all(y[:, f_ind, :] < x[:, f_ind, :])
    assert torch.equal(x[:, orig_inds, :], y[:, orig_inds, :])
    y = norm.denormalize(y, inplace=inplace)
    assert torch.allclose(x[:, f_ind, :], y[:, f_ind, :], rtol=1e-4)
    assert torch.equal(x[:, orig_inds, :], y[:, orig_inds, :])


@pytest.mark.parametrize("inplace", [True, False])
def test_multi_normalizer(inplace):
    x = torch.rand(8, 4, 12)
    min_= x[:, 1:, :].min(0)[0].min(1)[0]
    max_ = x[:, 1:, :].max(0)[0].max(1)[0]

    norm = Normalizer([1, 2, 3], min_, max_ - min_, NormalizationMode.GLOBAL)
    x_copy = x.detach().clone()
    y = norm.normalize(x_copy, inplace=inplace)
    assert torch.equal(x[:, 0, :], y[:, 0, :])

    ymin = y[:, 1:, :].min(0)[0].min(1)[0]
    ymax = y[:, 1:, :].max(0)[0].max(1)[0]
    assert torch.all(ymin == 0)
    assert torch.all(ymax == 1)
    assert ymin.shape == (3,)
    if not inplace:
        assert y is not x_copy

    y2 = norm.denormalize(y, inplace=inplace)
    assert torch.allclose(x[:, 1:, :], y2[:, 1:, :], rtol=1e-4)
    assert torch.equal(x[:, 0, :], y2[:, 0, :])
    if not inplace:
        assert y2 is not y


@pytest.mark.parametrize("inplace", [True, False])
def test_multi_series(inplace):
    f_ind = 1
    x, orig_inds = _get_tensor_and_inds(f_ind)
    series_ids = torch.tensor([0]*4 + [1]*4).long()

    norm = Normalizer(
        f_ind,
        torch.tensor([2, -2])[:, None],
        torch.tensor([1, 1])[:, None],
        NormalizationMode.PER_SERIES,
    )
    x_copy = x.detach().clone()
    y = norm.normalize(x_copy, series_ids, inplace=inplace)
    assert torch.all(y[:4, f_ind, :] < 0)
    assert torch.all(y[4:, f_ind, :] > 0)
    assert torch.equal(x[:, orig_inds, :], y[:, orig_inds, :])
    if not inplace:
        assert y is not x_copy

    y2 = norm.denormalize(y, series_ids)
    assert torch.allclose(x[:, f_ind, :], y2[:, f_ind, :], rtol=1e-4)
    assert torch.equal(x[:, orig_inds, :], y2[:, orig_inds, :])
    if not inplace:
        assert y2 is not y


@pytest.mark.parametrize("past_regressor", [True, False])
@pytest.mark.parametrize("past_regressand", [True, False])
@pytest.mark.parametrize("future_regressor", [True, False])
@pytest.mark.parametrize("future_regressand", [True, False])
@pytest.mark.parametrize("inplace", [True, False])
def test_batch_normalizer(past_regressor, past_regressand, future_regressor, future_regressand, inplace):
    torch.manual_seed(0)
    x = torch.rand(8, 4, 12)
    x_fut = torch.rand(8, 2, 8)
    y = torch.rand(8, 1, 12)
    y_fut = torch.rand(8, 1, 8)

    ng = NormalizationMode.GLOBAL
    p_or = Normalizer([0, 2], torch.tensor([2, -2]), torch.tensor([1, 1]), mode=ng) if past_regressor else None
    p_and = Normalizer(0, torch.tensor([2]), torch.tensor([1]), mode=ng) if past_regressand else None
    f_or = Normalizer(1, torch.tensor([-2]), torch.tensor([1]), mode=ng) if future_regressor else None
    f_and = Normalizer(0, torch.tensor([2]), torch.tensor([1]), mode=ng) if future_regressand else None

    if all(n is None for n in [p_or, p_and, f_or, f_and]):
        with pytest.raises(ValueError):
            _ = BatchNormalizer(p_or, p_and, f_or, f_and)
        return
    else:
        batch_normalizer = BatchNormalizer(p_or, p_and, f_or, f_and)

    batch = {PAST_IND_KEY: x, PAST_DEP_KEY: y, FUTURE_IND_KEY: x_fut, FUTURE_DEP_KEY: y_fut}
    orig_batch = copy.deepcopy(batch)
    tf_batch = batch_normalizer.normalize(batch, inplace=inplace)

    # check batch/tensor identity to ensure inplace is respected
    if inplace:
        assert batch is tf_batch
        assert batch[PAST_IND_KEY] is tf_batch[PAST_IND_KEY]
        assert batch[PAST_DEP_KEY] is tf_batch[PAST_DEP_KEY]
        assert batch[FUTURE_IND_KEY] is tf_batch[FUTURE_IND_KEY]
        assert batch[FUTURE_IND_KEY] is tf_batch[FUTURE_IND_KEY]
    else:
        assert batch is not tf_batch
        assert (batch[PAST_IND_KEY] is not tf_batch[PAST_IND_KEY]) == past_regressor
        assert (batch[PAST_DEP_KEY] is not tf_batch[PAST_DEP_KEY]) == past_regressand
        assert (batch[FUTURE_IND_KEY] is not tf_batch[FUTURE_IND_KEY]) == future_regressor
        assert (batch[FUTURE_DEP_KEY] is not tf_batch[FUTURE_DEP_KEY]) == future_regressand

    if past_regressor:
        assert torch.all(tf_batch[PAST_IND_KEY][:, 0, :] < 0)
        assert torch.all(tf_batch[PAST_IND_KEY][:, 2, :] > 0)
        assert torch.equal(tf_batch[PAST_IND_KEY][:, [1, 3], :], orig_batch[PAST_IND_KEY][:, [1, 3], :])
    else:
        assert torch.equal(tf_batch[PAST_IND_KEY], orig_batch[PAST_IND_KEY])
    if past_regressand:
        assert torch.all(tf_batch[PAST_DEP_KEY] < orig_batch[PAST_DEP_KEY])
    else:
        assert torch.equal(tf_batch[PAST_DEP_KEY], orig_batch[PAST_DEP_KEY])
    if future_regressor:
        assert torch.all(tf_batch[FUTURE_IND_KEY][:, 1, :] > orig_batch[FUTURE_IND_KEY][:, 1, :])
        assert torch.equal(tf_batch[FUTURE_IND_KEY][:, 0, :], orig_batch[FUTURE_IND_KEY][:, 0, :])
    else:
        assert torch.equal(tf_batch[FUTURE_IND_KEY], orig_batch[FUTURE_IND_KEY])
    if future_regressand:
        assert torch.all(tf_batch[FUTURE_DEP_KEY] < orig_batch[FUTURE_DEP_KEY])
    else:
        assert torch.equal(tf_batch[FUTURE_DEP_KEY], orig_batch[FUTURE_DEP_KEY])

    if future_regressand:
        temp = tf_batch[FUTURE_DEP_KEY].detach().clone()
        utf_y = batch_normalizer.denormalize_prediction(temp, inplace=inplace)
        torch.allclose(temp, utf_y, rtol=1e-4)

    utf_batch = batch_normalizer.denormalize(tf_batch, inplace=inplace)

    # check batch/tensor identity to ensure inplace is respected
    if inplace:
        assert tf_batch is utf_batch
        assert tf_batch[PAST_IND_KEY] is utf_batch[PAST_IND_KEY]
        assert tf_batch[PAST_DEP_KEY] is utf_batch[PAST_DEP_KEY]
        assert tf_batch[FUTURE_IND_KEY] is utf_batch[FUTURE_IND_KEY]
        assert tf_batch[FUTURE_IND_KEY] is utf_batch[FUTURE_IND_KEY]
    else:
        assert tf_batch is not utf_batch
        assert (tf_batch[PAST_IND_KEY] is not utf_batch[PAST_IND_KEY]) == past_regressor
        assert (tf_batch[PAST_DEP_KEY] is not utf_batch[PAST_DEP_KEY]) == past_regressand
        assert (tf_batch[FUTURE_IND_KEY] is not utf_batch[FUTURE_IND_KEY]) == future_regressor
        assert (tf_batch[FUTURE_DEP_KEY] is not utf_batch[FUTURE_DEP_KEY]) == future_regressand

    if past_regressor:
        assert torch.allclose(utf_batch[PAST_IND_KEY][:, [0, 2], :], orig_batch[PAST_IND_KEY][:, [0, 2], :], rtol=1e-4)
        assert torch.equal(utf_batch[PAST_IND_KEY][:, [1, 3], :], orig_batch[PAST_IND_KEY][:, [1, 3], :])
    else:
        assert torch.equal(utf_batch[PAST_IND_KEY], orig_batch[PAST_IND_KEY])
    if past_regressand:
        assert torch.allclose(utf_batch[PAST_DEP_KEY], orig_batch[PAST_DEP_KEY], rtol=1e-4)
    else:
        assert torch.equal(utf_batch[PAST_DEP_KEY], orig_batch[PAST_DEP_KEY])
    if future_regressor:
        assert torch.equal(utf_batch[FUTURE_IND_KEY][:, 0, :], orig_batch[FUTURE_IND_KEY][:, 0, :])
        assert torch.allclose(utf_batch[FUTURE_IND_KEY][:, 1, :], orig_batch[FUTURE_IND_KEY][:, 1, :], rtol=1e-4)
    else:
        assert torch.equal(utf_batch[FUTURE_IND_KEY], orig_batch[FUTURE_IND_KEY])
    if future_regressand:
        assert torch.allclose(utf_batch[FUTURE_DEP_KEY], orig_batch[FUTURE_DEP_KEY], rtol=1e-4)
    else:
        assert torch.equal(utf_batch[FUTURE_DEP_KEY], orig_batch[FUTURE_DEP_KEY])


def _get_tensor_and_inds(ind):
    torch.manual_seed(0)
    x = torch.rand(8, 4, 12)
    orig_inds = [i for i in range(4) if i != ind]
    return x, orig_inds
