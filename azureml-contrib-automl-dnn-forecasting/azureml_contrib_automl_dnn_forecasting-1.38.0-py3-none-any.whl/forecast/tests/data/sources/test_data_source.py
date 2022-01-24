import pytest

from forecast.data.sources.data_source import AbstractDataSource, DataSourceConfig, EncodingSpec


@pytest.mark.parametrize('num_values', [1, 0, -3])
def test_encoding_spec_bad_num_vals(num_values):
    with pytest.raises(ValueError):
        EncodingSpec(feature_index=0, num_vals=num_values)


@pytest.mark.parametrize('index', [-1, -3])
def test_encoding_spec_bad_feature_index(index):
    with pytest.raises(ValueError):
        EncodingSpec(feature_index=index, num_vals=8)


@pytest.mark.parametrize('feature_index', [0, 1, 4, 9])
@pytest.mark.parametrize('num_values', [2, 5, 9, 10000])
def test_encoding_spec_creation(feature_index, num_values):
    EncodingSpec(feature_index=feature_index, num_vals=num_values)


@pytest.mark.parametrize('feature_channels', [8, 13, 42])
@pytest.mark.parametrize('forecast_channels', [1, 4, 1000])
@pytest.mark.parametrize('encodings', [None, [EncodingSpec(feature_index=0, num_vals=10000)]])
def test_data_source_config_creation(feature_channels, forecast_channels, encodings):
    DataSourceConfig(feature_channels=feature_channels, forecast_channels=forecast_channels, encodings=encodings)


@pytest.mark.parametrize('feature_channels,feature_index', [(1,1), (8,8), (1, 8)])
def test_data_source_config_invalid_feature_index(feature_channels, feature_index):
    with pytest.raises(ValueError):
        DataSourceConfig(feature_channels=feature_channels,
                         forecast_channels=1,
                         encodings=[EncodingSpec(feature_index=feature_index, num_vals=8)]
                         )


def test_abstract_data_source_fails():
    with pytest.raises(TypeError):
        ds = AbstractDataSource()
