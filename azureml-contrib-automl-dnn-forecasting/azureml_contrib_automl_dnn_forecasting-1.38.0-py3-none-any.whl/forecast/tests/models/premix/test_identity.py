import dataclasses as dc
import random

import pytest
import torch

import forecast.models.premix as premix
from forecast.models.common import TensorShapeException


@pytest.mark.parametrize('input_channels', [1, 5, 10, 20])
def test_premix_identity_config(input_channels):
    config = premix.IdentityPremixConfig(input_channels=input_channels)
    iden = config.create_premix(input_channels)  # ensure we can create premix
    assert iden.receptive_field == 1
    assert iden.output_channels == input_channels
    assert iden.is_future_conditioned == False

    d = dc.asdict(config)

    for cls in [premix.IdentityPremixConfig, premix.AbstractPremixConfig]:
        config_new = cls.fromdict(d)
        assert config == config_new


# test 0 input channels and output != input for identity
def test_premix_identity_config_failure_0_input_channel():
    with pytest.raises(ValueError):
        config = premix.IdentityPremixConfig(input_channels=0)


# test different input & output channels
@pytest.mark.parametrize('input_channels', [1, 5, 10, 20])
@pytest.mark.parametrize('output_offset', [-1, 1, 3])
def test_premix_identity_config_failure_diff_input_output(input_channels, output_offset):
    config = premix.IdentityPremixConfig(input_channels=input_channels)
    with pytest.raises(ValueError):
        config.create_premix(input_channels + output_offset)


@pytest.mark.parametrize('input_channels', [1, 5, 10, 20])
@pytest.mark.parametrize('batch_size', [1, 4, 128])
@pytest.mark.parametrize('ts_len', [1, 90])
def test_premix_identity(input_channels, batch_size, ts_len):
    config = premix.IdentityPremixConfig(input_channels=input_channels)
    iden = config.create_premix(input_channels)

    tensor = torch.rand(batch_size, input_channels, ts_len)
    out = iden(tensor)
    assert torch.all(out == tensor)


@pytest.mark.skip('Skip until shape verification of tensor shape is implemented.')
@pytest.mark.parametrize('dim', [1, 2, 4, 5])
def test_premix_identify_shape_error(dim):
    with pytest.raises(TensorShapeException):
        shape = [random.randint(1, 8) for _ in range(dim)]
        tensor = torch.rand(*shape)

        num_chan = shape[-2] if dim > 1 else dim[0]
        config = premix.IdentityPremixConfig(input_channels=num_chan)
        iden = config.create_premix(num_chan)
        out = iden(tensor)
