import dataclasses as dc
import contextlib
import random

import pytest
import torch

from forecast.models import premix as premix
from forecast.models.common import TensorShapeException


@pytest.mark.parametrize('input_channels', [1, 5, 10, 20])
@pytest.mark.parametrize('kernel_size', [1, 2, 3])
@pytest.mark.parametrize('dilation', [1, 2, 3, 4, 8])
@pytest.mark.parametrize('stride', [1, 2])
@pytest.mark.parametrize('output_channels', [1, 4])
def test_premix_conv_config(input_channels, kernel_size, dilation, stride, output_channels):
    config = premix.ConvPremixConfig(input_channels=input_channels,
                                     kernel_size=kernel_size,
                                     dilation=dilation,
                                     stride=stride)
    d = dc.asdict(config)

    for cls in [premix.ConvPremixConfig, premix.AbstractPremixConfig]:
        config_new = cls.fromdict(d)
        assert config == config_new


def test_premix_conv_config_failure_0_input_channel():
    with pytest.raises(ValueError):
        config = premix.ConvPremixConfig(input_channels=0, kernel_size=1, dilation=1, stride=1)


def test_premix_conv_config_failure_invalid_stride():
    with pytest.raises(ValueError):
        config = premix.ConvPremixConfig(input_channels=3, kernel_size=1, dilation=1, stride=0)


@pytest.mark.parametrize('kernel_size', [-1, 0, 1])
@pytest.mark.parametrize('dilation', [-1, 0, 1])
@pytest.mark.parametrize('stride', [1])
def test_premix_conv_config_failure_invalid_input(kernel_size, dilation, stride):
    params = [kernel_size, dilation, stride]
    if any([el < 1 for el in params]):
        cm = pytest.raises(ValueError)
    else:
        cm = contextlib.nullcontext()

    with cm:
        config = premix.ConvPremixConfig(input_channels=1,
                                         kernel_size=kernel_size,
                                         dilation=dilation,
                                         stride=stride
                                         )


@pytest.mark.parametrize('input_channels', [1, 16])
@pytest.mark.parametrize('kernel_size', [1, 2])
@pytest.mark.parametrize('dilation', [1, 4])
@pytest.mark.parametrize('stride', [1])  # to be expanded later once we support non-unity stride
@pytest.mark.parametrize('output_channels', [1, 8])
@pytest.mark.parametrize('batch_size', [1, 32])
@pytest.mark.parametrize('ts_offset', [0, 1, 3])
def test_premix_conv_shape(input_channels, kernel_size, dilation, stride, output_channels, batch_size, ts_offset):
    config = premix.ConvPremixConfig(input_channels=input_channels,
                                     kernel_size=kernel_size,
                                     dilation=dilation,
                                     stride=stride)
    conv = config.create_premix(output_channels=output_channels)
    assert conv.output_channels == output_channels

    # we assume the TS len > window size
    window_size = conv.receptive_field + ts_offset
    tensor = torch.rand(batch_size, input_channels, window_size)
    out = conv(tensor)

    assert out.size() == torch.Size((batch_size, output_channels, window_size))


def test_premix_conv_too_short_time():
    batch_size = 1
    input_channels = 1
    kernel_size = 2
    dilation = 8
    output_channels = 1
    config = premix.ConvPremixConfig(input_channels=input_channels,
                                     kernel_size=kernel_size,
                                     dilation=dilation,
                                     stride=1)
    conv = config.create_premix(output_channels)
    tensor_len = random.randint(1, conv.receptive_field - 1)
    tensor = torch.rand(batch_size, input_channels, tensor_len)

    with pytest.raises(TensorShapeException):
        conv(tensor)


@pytest.mark.parametrize('output_channels', [-5, -1, 0])
def test_premix_conv_invalid_output_channels(output_channels):
    input_channels = 1
    kernel_size = 2
    dilation = 8
    config = premix.ConvPremixConfig(input_channels=input_channels,
                                     kernel_size=kernel_size,
                                     dilation=dilation,
                                     stride=1)
    with pytest.raises(ValueError):
        conv = config.create_premix(output_channels)
