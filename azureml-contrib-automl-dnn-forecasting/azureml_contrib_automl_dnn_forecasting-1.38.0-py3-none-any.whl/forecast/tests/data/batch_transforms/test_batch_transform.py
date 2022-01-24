import copy

import pytest
import torch

import forecast.data.batch_transforms
from forecast.data import FUTURE_DEP_KEY, FUTURE_IND_KEY, PAST_DEP_KEY, PAST_IND_KEY
from forecast.data.batch_transforms import (
    BatchFeatureTransform,
    BatchNormalizer,
    BatchSubtractOffset,
    BatchOneHotEncoder,
    FeatureTransform,
    GenericBatchTransform,
    NormalizationMode,
    Normalizer,
    OneHotEncoder,
)

BATCH_SIZE = 8
NUM_PAST_REGRESSORS = 5
NUM_FUTURE_REGRESSORS = 4
SEQ_LEN = 12
NUM_SERIES = 10


@pytest.mark.parametrize("feature_transform_past_regressor", [
    None,
    FeatureTransform([0, 2], [torch.sqrt, torch.exp], [torch.square, torch.log]),
])
@pytest.mark.parametrize("feature_transform_past_regressand", [
    None,
    FeatureTransform(0, lambda x: torch.log(1+x), lambda x: torch.exp(x) - 1),
])
@pytest.mark.parametrize("feature_transform_future_regressor", [
    None,
    FeatureTransform(1, [lambda x: x * 2, lambda x: x + 1], [lambda x: x / 2, lambda x: x - 1]),
])
@pytest.mark.parametrize("feature_transform_future_regressand", [
    None,
    FeatureTransform(0, lambda x: torch.log(1+x), lambda x: torch.exp(x) - 1),
])
@pytest.mark.parametrize("normalize_past_regressors", [None, list(range(NUM_PAST_REGRESSORS // 2))])
@pytest.mark.parametrize("normalize_future_regressors", [None, list(range(NUM_FUTURE_REGRESSORS // 2))])
@pytest.mark.parametrize("normalize_regressands", [False, True])
@pytest.mark.parametrize("normalize_per_series", [False, True])
@pytest.mark.parametrize("offset_regressand_index", [None, 0, -1, slice(None, None)])
@pytest.mark.parametrize("one_hot_encode", [None,]) # PAST_IND_KEY, [PAST_IND_KEY, FUTURE_IND_KEY]])
@pytest.mark.parametrize("num_regressands", [1, 2])
@pytest.mark.parametrize("inplace", [True, False])
def test_batch_transform(
    feature_transform_past_regressor,
    feature_transform_past_regressand,
    feature_transform_future_regressor,
    feature_transform_future_regressand,
    normalize_past_regressors,
    normalize_future_regressors,
    normalize_regressands,
    normalize_per_series,
    offset_regressand_index,
    one_hot_encode,
    num_regressands,
    inplace,
):
    # only run once if all normalizers are disabled
    if normalize_per_series and normalize_past_regressors is None and normalize_future_regressors is None and normalize_regressands is False:
        return

    # safety for OHE
    if feature_transform_past_regressor:
        assert NUM_PAST_REGRESSORS - 1 not in feature_transform_past_regressor.feature_indices, "bad test"
    if feature_transform_future_regressor:
        assert NUM_FUTURE_REGRESSORS - 1 not in feature_transform_future_regressor.feature_indices, "bad test"

    # create the batch
    torch.manual_seed(0)
    scale = 100
    rtol = 1e-4

    batch_keys = [PAST_IND_KEY, PAST_DEP_KEY, FUTURE_IND_KEY, FUTURE_DEP_KEY]
    orig_batch = {
        PAST_IND_KEY: torch.rand(BATCH_SIZE, NUM_PAST_REGRESSORS, SEQ_LEN) * scale,
        PAST_DEP_KEY: torch.rand(BATCH_SIZE, num_regressands, SEQ_LEN) * scale,
        FUTURE_IND_KEY: torch.rand(BATCH_SIZE, NUM_FUTURE_REGRESSORS, SEQ_LEN) * scale,
        FUTURE_DEP_KEY: torch.rand(BATCH_SIZE, num_regressands, SEQ_LEN) * scale,
    }
    orig_batch[PAST_IND_KEY][:, -1, :] = torch.randint(low=0, high=NUM_SERIES, size=[BATCH_SIZE, 1])
    orig_batch[FUTURE_IND_KEY][:, -1, :] = orig_batch[PAST_IND_KEY][:, -1, 0][:, None]

    # build the feature transform
    if not feature_transform_past_regressor and not feature_transform_past_regressand and not feature_transform_future_regressor and not feature_transform_future_regressand:
        batch_feature_transform = None
    else:
        batch_feature_transform = BatchFeatureTransform(
            feature_transform_past_regressor,
            feature_transform_past_regressand,
            feature_transform_future_regressor,
            feature_transform_future_regressand,
        )

    # build the normalizer
    get_min = lambda x: x.min(axis=0)[0].min(axis=1)[0] if x.numel() > 0 else None
    get_max = lambda x: x.max(axis=0)[0].max(axis=1)[0] if x.numel() > 0 else None
    if normalize_past_regressors is None and normalize_future_regressors is None and not normalize_regressands:
        batch_normalizer = None
    else:
        norm_inds = [
            normalize_past_regressors,
            list(range(num_regressands)) if num_regressands is not None else None,
            normalize_future_regressors,
            list(range(num_regressands)) if num_regressands is not None else None,
        ]
        if normalize_per_series:
            series_inds = orig_batch[PAST_IND_KEY][:, -1, 0].long()
            mins = {k: [get_min(orig_batch[k][series_inds == i, :, :]) for i in range(NUM_SERIES)] for k in batch_keys}
            maxes = {k: [get_max(orig_batch[k][series_inds == i, :, :]) for i in range(NUM_SERIES)] for k in batch_keys}
            for k in batch_keys:
                mins[k] = [m if m is not None else torch.zeros_like(orig_batch[k][0, :, 0]) for m in mins[k]]
                maxes[k] = [m if m is not None else torch.zeros_like(orig_batch[k][0, :, 0]) for m in maxes[k]]
            mins = {k: torch.stack(mins[k], dim=0) for k in mins}
            maxes = {k: torch.stack(maxes[k], dim=0) for k in maxes}
            ranges = {k: maxes[k] - mins[k] for k in mins}

            for k, k2 in zip(batch_keys, norm_inds):
                mins[k] = mins[k][:, k2] if k2 is not None else None
                ranges[k] = ranges[k][:, k2] if k2 is not None else None

            mode = NormalizationMode.PER_SERIES
        else:
            series_inds = None
            mode = NormalizationMode.GLOBAL
            mins = {k: get_min(orig_batch[k]) for k in batch_keys}
            ranges = {k: get_max(orig_batch[k]) - mins[k] for k in batch_keys}

            mins = {k: mins[k][k2] if k2 is not None else None for k, k2 in zip(batch_keys, norm_inds)}
            ranges = {k: ranges[k][k2] if k2 is not None else None for k, k2 in zip(batch_keys, norm_inds)}

        batch_normalizer = BatchNormalizer(
            Normalizer(
                normalize_past_regressors,
                mins[PAST_IND_KEY],
                ranges[PAST_IND_KEY],
                mode,
            ) if normalize_past_regressors else None,
            Normalizer(
                list(range(num_regressands)),
                mins[PAST_DEP_KEY],
                ranges[PAST_DEP_KEY],
                mode,
            ) if normalize_regressands else None,
            Normalizer(
                normalize_future_regressors,
                mins[FUTURE_IND_KEY],
                ranges[FUTURE_IND_KEY],
                mode,
            ) if normalize_future_regressors else None,
            Normalizer(
                list(range(num_regressands)),
                mins[FUTURE_DEP_KEY],
                ranges[FUTURE_DEP_KEY],
                mode,
            ) if normalize_regressands else None,
        )

    # build the offset object
    if offset_regressand_index is None:
        batch_subtract_offset = None
    else:
        offset_index = list(range(num_regressands))[offset_regressand_index]
        batch_subtract_offset = BatchSubtractOffset(offset_index)

    # build the OHE
    if not one_hot_encode:
        batch_onehot_encoder = None
    else:
        one_hot_encode = [one_hot_encode] if isinstance(one_hot_encode, str) else list(one_hot_encode)
        batch_onehot_encoder = BatchOneHotEncoder(
            past_regressor=OneHotEncoder(NUM_PAST_REGRESSORS-1, NUM_SERIES) if PAST_IND_KEY in one_hot_encode else None,
            future_regressor=OneHotEncoder(NUM_FUTURE_REGRESSORS-1, NUM_SERIES) if FUTURE_IND_KEY in one_hot_encode else None,
        )

    # create the batch transformer
    if not batch_feature_transform and not batch_subtract_offset and not batch_onehot_encoder and not batch_normalizer:
        return
    else:
        batch_transform = GenericBatchTransform(
            feature_transforms=batch_feature_transform,
            normalizer=batch_normalizer,
            subtract_offset=batch_subtract_offset,
            one_hot=batch_onehot_encoder,
            series_indexer=lambda x: x[:, -1, 0].long(),
        )

    # are the tensors modified by a non_ohe transform (ohe always modifies)
    was_modified = {
        PAST_IND_KEY: feature_transform_past_regressor is not None or normalize_past_regressors is not None,
        PAST_DEP_KEY: feature_transform_past_regressand is not None or normalize_regressands or offset_regressand_index is not None,
        FUTURE_IND_KEY: feature_transform_future_regressor is not None or normalize_future_regressors is not None,
        FUTURE_DEP_KEY: feature_transform_future_regressand is not None or normalize_regressands or offset_regressand_index is not None,
    }

    # sanity check on the feature transform op
    if batch_feature_transform:
        batch = copy.deepcopy(orig_batch)
        utf_batch = batch_feature_transform.undo(batch_feature_transform.apply(batch, inplace=inplace), inplace=inplace)
        assert (utf_batch is batch) == inplace
        assert (utf_batch[PAST_IND_KEY] is batch[PAST_IND_KEY]) == (inplace or not feature_transform_past_regressor)
        assert (utf_batch[PAST_DEP_KEY] is batch[PAST_DEP_KEY]) == (inplace or not feature_transform_past_regressand)
        assert (utf_batch[FUTURE_IND_KEY] is batch[FUTURE_IND_KEY]) == (inplace or not feature_transform_future_regressor)
        assert (utf_batch[FUTURE_DEP_KEY] is batch[FUTURE_DEP_KEY]) == (inplace or not feature_transform_future_regressand)
        for k in batch_keys:
            assert torch.allclose(utf_batch[k], orig_batch[k])

    # sanity check on the normalizer op
    if batch_normalizer:
        batch = copy.deepcopy(orig_batch)
        utf_batch = batch_normalizer.denormalize(
            batch_normalizer.normalize(batch, series_inds, inplace=inplace),
            series_inds,
            inplace=inplace
        )
        assert (utf_batch is batch) == inplace
        assert (utf_batch[PAST_IND_KEY] is batch[PAST_IND_KEY]) == (inplace or not normalize_past_regressors)
        assert (utf_batch[PAST_DEP_KEY] is batch[PAST_DEP_KEY]) == (inplace or not normalize_regressands)
        assert (utf_batch[FUTURE_IND_KEY] is batch[FUTURE_IND_KEY]) == (inplace or not normalize_future_regressors)
        assert (utf_batch[FUTURE_DEP_KEY] is batch[FUTURE_DEP_KEY]) == (inplace or not normalize_regressands)
        for k in batch_keys:
            assert torch.allclose(utf_batch[k], orig_batch[k])

    # sanity check on the subtract offset op
    if batch_subtract_offset:
        batch = copy.deepcopy(orig_batch)
        utf_batch = batch_subtract_offset.undo(batch_subtract_offset.do(batch, inplace=inplace), inplace=inplace)
        assert (utf_batch is batch) == inplace
        assert utf_batch[PAST_IND_KEY] is batch[PAST_IND_KEY]
        assert (utf_batch[PAST_DEP_KEY] is batch[PAST_DEP_KEY]) == inplace
        assert utf_batch[FUTURE_IND_KEY] is batch[FUTURE_IND_KEY]
        assert (utf_batch[FUTURE_DEP_KEY] is batch[FUTURE_DEP_KEY]) == inplace
        for k in batch_keys:
            assert torch.allclose(utf_batch[k], orig_batch[k], rtol=rtol)

    # sanity check on the identity the OHE op
    if batch_onehot_encoder:
        batch = copy.deepcopy(orig_batch)
        utf_batch = batch_onehot_encoder.decode(batch_onehot_encoder.encode(batch, inplace=inplace), inplace=inplace)
        assert (utf_batch is batch) == inplace
        assert utf_batch[PAST_IND_KEY] is not batch[PAST_IND_KEY]
        assert utf_batch[PAST_DEP_KEY] is batch[PAST_DEP_KEY]
        assert utf_batch[FUTURE_IND_KEY] is not batch[FUTURE_IND_KEY]
        assert utf_batch[FUTURE_DEP_KEY] is batch[FUTURE_DEP_KEY]
        for k in batch_keys:
            assert torch.equal(utf_batch[k], orig_batch[k])

    batch = copy.deepcopy(orig_batch)
    tf_batch = batch_transform.do(batch, inplace=inplace)
    assert (tf_batch is batch) == inplace
    for k in batch_keys:
        if (inplace or not was_modified[k]) and (one_hot_encode is None or k not in one_hot_encode):
            assert tf_batch[k] is batch[k]
        else:
            assert tf_batch[k] is not batch[k]

    y = copy.deepcopy(tf_batch[FUTURE_DEP_KEY])
    utf_y = batch_transform.undo_y(y, tf_batch, inplace=inplace)
    assert (utf_y is y) == inplace
    assert torch.allclose(utf_y, orig_batch[FUTURE_DEP_KEY], rtol=rtol)

    utf_batch = batch_transform.undo(tf_batch, inplace=inplace)
    assert (tf_batch is utf_batch) == inplace
    for k in batch_keys:
        if inplace or not was_modified[k] and (one_hot_encode is None or k not in one_hot_encode):
            assert tf_batch[k] is utf_batch[k]
        else:
            assert tf_batch[k] is not utf_batch[k]

    for k in batch_keys:
        assert torch.allclose(utf_batch[k], orig_batch[k], rtol=rtol)

    batch = copy.deepcopy(orig_batch)
    del batch[FUTURE_DEP_KEY]  # simulate prediction w/o ground truth data
    tf_batch = batch_transform.do(batch, inplace=inplace)
    assert (tf_batch is batch) == inplace

    utf_batch = batch_transform.undo(tf_batch, inplace=inplace)
    for k in [PAST_IND_KEY, PAST_DEP_KEY, FUTURE_IND_KEY]:
        assert torch.allclose(utf_batch[k], orig_batch[k], rtol=rtol)

    batch = copy.deepcopy(orig_batch)
    tf_batch = batch_transform.do(batch, inplace=inplace)
    tf_y = tf_batch[FUTURE_DEP_KEY].detach().clone()
    del tf_batch[FUTURE_DEP_KEY]
    utf_y = batch_transform.undo_y(tf_y, tf_batch, inplace=inplace)
    assert (utf_y is tf_y) == inplace
    assert torch.allclose(utf_y, orig_batch[FUTURE_DEP_KEY], rtol=rtol)
