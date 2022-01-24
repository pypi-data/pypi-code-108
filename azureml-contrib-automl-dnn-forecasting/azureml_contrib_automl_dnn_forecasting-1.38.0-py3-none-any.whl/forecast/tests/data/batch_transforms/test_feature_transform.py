import copy
from functools import partial, reduce
from typing import Sequence

import pytest

import torch

from forecast.data import FUTURE_DEP_KEY, FUTURE_IND_KEY, PAST_DEP_KEY, PAST_IND_KEY
from forecast.data.batch_transforms import BatchFeatureTransform, FeatureTransform
from forecast.data.batch_transforms.common import make_int_list


@pytest.mark.parametrize("funcs", [
    (torch.log, torch.exp),
    ([torch.log, lambda t: torch.add(t, 2)], [torch.exp, lambda t: torch.sub(t, 2)]),
])
@pytest.mark.parametrize("feature_indices", [0, 1, [1, 2]])
@pytest.mark.parametrize("inplace", [True, False])
def test_transform(funcs, feature_indices, inplace):
    torch.manual_seed(0)
    n_feat = 4

    x = torch.rand(8, n_feat, 12) + 1
    orig_x = x.clone().detach()
    lfi = [feature_indices] if isinstance(feature_indices, int) else list(feature_indices)
    orig_indices = _get_orig_inds(lfi, n_feat)
    tf_list = list(funcs[0]) if isinstance(funcs[0], Sequence) else [funcs[0]]

    ft = FeatureTransform(feature_indices, funcs[0], funcs[1])
    y = ft.apply(x, inplace=inplace)

    assert torch.equal(orig_x[:, orig_indices, :], y[:, orig_indices, :])
    assert torch.allclose(
        y[:, feature_indices, :],
        reduce(lambda r, f: f(r), tf_list, orig_x[:, feature_indices, :]),
        rtol=1e-4
    )
    if inplace:
        assert x is y

    z = ft.undo(y, inplace=inplace)
    assert torch.equal(orig_x[:, orig_indices, :], z[:, orig_indices, :])
    assert torch.allclose(orig_x[:, feature_indices, :], z[:, feature_indices, :], rtol=1e-4)
    if inplace:
        assert y is z
        assert x is z


@pytest.mark.parametrize("f_ind", [1, [1, 2]])
def test_transform_vals(f_ind):
    torch.manual_seed(0)
    tf = FeatureTransform(f_ind, lambda x: x+1, lambda x: x-1)
    x = torch.rand(8, 3, 12) * 100

    y = tf.apply(x, inplace=False)
    assert torch.equal(y[:, f_ind, :], x[:, f_ind, :] + 1)
    z = tf.undo(y, inplace=False)
    assert torch.allclose(x, z)


@pytest.mark.parametrize("past_regressor", [True, False])
@pytest.mark.parametrize("past_regressand", [True, False])
@pytest.mark.parametrize("future_regressor", [True, False])
@pytest.mark.parametrize("future_regressand", [True, False])
@pytest.mark.parametrize("inplace", [True, False])
def test_batch_transform(past_regressor, past_regressand, future_regressor, future_regressand, inplace):
    # data properties
    torch.manual_seed(0)
    n_xp_feat = 4
    n_yp_feat = 1
    n_xf_feat = 3
    n_yf_feat = 1
    scale = 100

    # create the data
    xp = torch.rand(8, n_xp_feat, 12) * scale
    xf = torch.rand(8, n_xf_feat, 8) * scale
    yp = torch.rand(8, n_yp_feat, 12) * scale
    yf = torch.rand(8, n_yf_feat, 8) * scale

    # featurized and original indices
    xp_tfi = [0, 2]
    xp_oi = _get_orig_inds(xp_tfi, n_xp_feat)
    yp_tfi = 0
    yp_oi = _get_orig_inds(yp_tfi, n_yp_feat)
    xf_tfi = [0, 1]
    xf_oi = _get_orig_inds(xf_tfi, n_xf_feat)
    yf_tfi = 0
    yf_oi = _get_orig_inds(yf_tfi, n_yf_feat)

    # the transforms
    p_or = FeatureTransform(xp_tfi, lambda t: t + 1, lambda t: t - 1) if past_regressor else None
    p_and = FeatureTransform(yp_tfi, lambda t: t + 2, lambda t: t - 2) if past_regressand else None
    f_or = FeatureTransform(
        xf_tfi,
        [lambda t: t + 3, lambda t: t * 2],
        [lambda t: t - 3, lambda t: t / 2],
    ) if future_regressor else None
    f_and = FeatureTransform(
        yf_tfi,
        [lambda t: t * 2, lambda t: t - 1],
        [lambda t: t / 2, lambda t: t + 1],
    ) if future_regressand else None

    # sanity check that each works
    for tf in [p_or, p_and, f_or, f_and]:
        if tf:
            foo = torch.rand(8, max(n_xp_feat, n_yp_feat, n_xf_feat, n_yf_feat), 12) * scale
            foo2 = tf.apply(foo, inplace=False)
            foo3 = tf.undo(foo2, inplace=False)
            assert torch.allclose(foo, foo3)

    # create the batch transform
    if all(n is None for n in [p_or, p_and, f_or, f_and]):
        with pytest.raises(ValueError):
            _ = BatchFeatureTransform(p_or, p_and, f_or, f_and)
        return
    else:
        batch_transform = BatchFeatureTransform(p_or, p_and, f_or, f_and)

    # create the batch and apply the transform
    batch = {PAST_IND_KEY: xp, PAST_DEP_KEY: yp, FUTURE_IND_KEY: xf, FUTURE_DEP_KEY: yf}
    orig_batch = copy.deepcopy(batch)
    tf_batch = batch_transform.apply(batch, inplace=inplace)

    # ensure the shapes haven't changed
    for k in [PAST_IND_KEY, PAST_DEP_KEY, FUTURE_IND_KEY, FUTURE_IND_KEY]:
        assert tf_batch[k].shape == orig_batch[k].shape

    # ensure a native, out of place application matches the results
    if past_regressor:
        assert torch.allclose(
            tf_batch[PAST_IND_KEY][:, xp_tfi, :],
            reduce(lambda r, tf: tf.apply(r, inplace=False), batch_transform.past_regressor, orig_batch[PAST_IND_KEY])[:, xp_tfi, :],
        )
        assert torch.equal(batch[PAST_IND_KEY][:, xp_oi, :], orig_batch[PAST_IND_KEY][:, xp_oi, :])
    else:
        assert torch.equal(batch[PAST_IND_KEY], orig_batch[PAST_IND_KEY])
    if past_regressand:
        assert torch.allclose(
            tf_batch[PAST_DEP_KEY],
            reduce(lambda r, tf: tf.apply(r, inplace=False), batch_transform.past_regressand, orig_batch[PAST_DEP_KEY]),
        )
    else:
        assert torch.equal(batch[PAST_DEP_KEY], orig_batch[PAST_DEP_KEY])
    if future_regressor:
        assert torch.allclose(
            tf_batch[FUTURE_IND_KEY][:, xf_tfi, :],
            reduce(lambda r, tf: tf.apply(r, inplace=False), batch_transform.future_regressor, orig_batch[FUTURE_IND_KEY])[:, xf_tfi, :],
        )
        assert torch.equal(batch[FUTURE_IND_KEY][:, xf_oi, :], orig_batch[FUTURE_IND_KEY][:, xf_oi, :])
    else:
        assert torch.equal(batch[FUTURE_IND_KEY], orig_batch[FUTURE_IND_KEY])
    if future_regressand:
        assert torch.allclose(
            tf_batch[FUTURE_DEP_KEY],
            reduce(lambda r, tf: tf.apply(r, inplace=False), batch_transform.future_regressand, orig_batch[FUTURE_DEP_KEY]),
        )
    else:
        assert torch.equal(batch[FUTURE_DEP_KEY], orig_batch[FUTURE_DEP_KEY])

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

    utf_batch = batch_transform.undo(tf_batch, inplace=inplace)

    # ensure the shapes haven't changed
    for k in [PAST_IND_KEY, PAST_DEP_KEY, FUTURE_IND_KEY, FUTURE_IND_KEY]:
        assert utf_batch[k].shape == tf_batch[k].shape

    # ensure a native, out of place application matches the results
    if past_regressor:
        assert torch.allclose(utf_batch[PAST_IND_KEY][:, xp_tfi, :], orig_batch[PAST_IND_KEY][:, xp_tfi, :])
        assert torch.equal(utf_batch[PAST_IND_KEY][:, xp_oi, :], orig_batch[PAST_IND_KEY][:, xp_oi, :])
    else:
        assert torch.equal(utf_batch[PAST_IND_KEY], orig_batch[PAST_IND_KEY])
    if past_regressand:
        assert torch.allclose(utf_batch[PAST_DEP_KEY], orig_batch[PAST_DEP_KEY])
    else:
        assert torch.equal(utf_batch[PAST_DEP_KEY], orig_batch[PAST_DEP_KEY])
    if future_regressor:
        assert torch.allclose(utf_batch[FUTURE_IND_KEY][:, xf_tfi, :], orig_batch[FUTURE_IND_KEY][:, xf_tfi, :])
        assert torch.equal(utf_batch[FUTURE_IND_KEY][:, xf_oi, :], orig_batch[FUTURE_IND_KEY][:, xf_oi, :])
    else:
        assert torch.equal(utf_batch[FUTURE_IND_KEY], orig_batch[FUTURE_IND_KEY])
    if future_regressand:
        assert torch.allclose(utf_batch[FUTURE_DEP_KEY], orig_batch[FUTURE_DEP_KEY])
    else:
        assert torch.equal(utf_batch[FUTURE_DEP_KEY], orig_batch[FUTURE_DEP_KEY])

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

    # test undo y
    if future_regressand:
        batch = copy.deepcopy(orig_batch)
        out = batch_transform.apply(batch)
        utf_y = batch_transform.undo_y(out[FUTURE_DEP_KEY], inplace=inplace)
        torch.allclose(utf_y, orig_batch[FUTURE_DEP_KEY])

        if past_regressor:
            assert not torch.allclose(out[PAST_IND_KEY], orig_batch[PAST_IND_KEY])
        if past_regressand:
            assert not torch.allclose(out[PAST_DEP_KEY], orig_batch[PAST_DEP_KEY])
        if future_regressor:
            assert  not torch.allclose(out[FUTURE_IND_KEY], orig_batch[FUTURE_IND_KEY])


def _get_orig_inds(feat_inds, num_feat):
    feat_inds = make_int_list(feat_inds)
    return [i for i in range(num_feat) if i not in feat_inds]