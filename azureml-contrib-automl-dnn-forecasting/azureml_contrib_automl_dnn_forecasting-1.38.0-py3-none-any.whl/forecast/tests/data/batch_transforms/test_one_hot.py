import copy

import pytest
import torch

from forecast.data import FUTURE_DEP_KEY, FUTURE_IND_KEY, PAST_DEP_KEY, PAST_IND_KEY
from forecast.data.batch_transforms import BatchOneHotEncoder, OneHotEncoder


@pytest.mark.parametrize("n_features", [4, 5])
def test_one_hot(n_features):
    batch_size = 8
    length = 12
    encoder = OneHotEncoder([1, 3], [5, 2])

    x = torch.rand(batch_size, n_features, length)
    x[:, 1, :] = torch.randint(0, 5, (batch_size,))[:, None]
    x[:, 3, :] = torch.randint(0, 2, (batch_size,))[:, None]

    out = encoder.encode(x)
    assert torch.equal(x[:, 0, :], out[:, 0, :])
    assert torch.equal(x[:, 2, :], out[:, 6, :])
    if n_features > 4:
        assert torch.equal(x[:, 4:, :], out[:, 9:, :])

    assert torch.equal(out[:, 1:6, :].argmax(1).float(), x[:, 1, :])
    assert torch.equal(out[:, [7, 8], :].argmax(1).float(), x[:, 3, :])

    y = encoder.decode(out)
    assert torch.equal(x, y)


@pytest.mark.parametrize("n_features", [4, 5])
@pytest.mark.parametrize("past_regressor", [True, False])
@pytest.mark.parametrize("future_regressor", [True, False])
@pytest.mark.parametrize("inplace", [True, False])
def test_batch(n_features, past_regressor, future_regressor, inplace):
    batch_size = 8
    length = 12
    encoder = OneHotEncoder([1, 3], [5, 2])

    x = torch.rand(batch_size, n_features, length)
    x[:, 1, :] = torch.randint(0, 5, (batch_size,))[:, None]
    x[:, 3, :] = torch.randint(0, 2, (batch_size,))[:, None]

    x_fut = torch.rand(batch_size, n_features, length)
    x_fut[:, 1, :] = x[:, 1, :]
    x_fut[:, 3, :] = x[:, 3, :]

    kwargs = {
        "past_regressor": encoder if past_regressor else None,
        "future_regressor": encoder if future_regressor else None,
    }
    if not past_regressor and not future_regressor:
        with pytest.raises(ValueError):
            _ = BatchOneHotEncoder(**kwargs)
        return
    else:
        batch_encoder = BatchOneHotEncoder(**kwargs)

    y_past = torch.rand(batch_size, 1, length)
    y_fut = torch.rand(batch_size, 1, length)

    batch = {PAST_IND_KEY: x, PAST_DEP_KEY: y_past, FUTURE_IND_KEY: x_fut, FUTURE_DEP_KEY: y_fut}
    orig_batch = copy.deepcopy(batch)
    encoded = batch_encoder.encode(batch, inplace=inplace)
    assert (encoded is batch) == inplace

    for field, key, val in zip([past_regressor, future_regressor], [PAST_IND_KEY, FUTURE_IND_KEY], [x, x_fut]):
        if field:
            assert torch.equal(val[:, 0, :], encoded[key][:, 0, :])
            assert torch.equal(val[:, 2, :], encoded[key][:, 6, :])
            if n_features > 4:
                assert torch.equal(val[:, 4:, :], encoded[key][:, 9:, :])

            assert torch.equal(encoded[key][:, 1:6, :].argmax(1).float(), val[:, 1, :])
            assert torch.equal(encoded[key][:, [7, 8], :].argmax(1).float(), val[:, 3, :])

    decoded = batch_encoder.decode(encoded)
    for k in batch:
        assert torch.equal(decoded[k], orig_batch[k])
