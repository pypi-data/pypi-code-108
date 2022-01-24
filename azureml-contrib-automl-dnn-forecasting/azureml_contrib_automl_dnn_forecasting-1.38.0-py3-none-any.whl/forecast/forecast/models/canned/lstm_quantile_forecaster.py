"""Creates a sample LSTM-based model which forecasts N quantiles."""

from forecast.models import ForecastingModel
from forecast.models.backbone.base import MultilevelType
from forecast.models.backbone.lstm import LSTMBackboneConfig
from forecast.models.forecast_head import UnboundedScalarForecastHeadConfig
from forecast.models.premix import ConvPremixConfig


def create_lstm_quantile_forecaster(input_channels: int,
                                    hidden_to_input_channel_ratio: float, multilevel: str, receptive_field: int,
                                    horizon: int, num_quantiles: int,
                                    num_channels: int, depth: int, dropout_rate: float) -> ForecastingModel:
    """Creates a Forecasting model with a `ConvPremix`, `LSTMBackbone`, and N `UnboundedScalarForecastHead`s.

    Parameters
    ----------
    input_channels: int
        The number of channels in the input data
    hidden_to_input_channel_ratio: float
        The ratio of channels in a hidden layer to input channels
    multilevel: str
        One of 'CELL` or `NONE`
    receptive_field: int
        The number of samples prior to the forecasting horizon which must be supplied
    horizon: int
        The number of samples the model should predict (currently must be 1)
    num_quantiles: int
        The number of quantiles (i.e., forecast heads) the model should predict
    num_channels: int
        The number of channels passed as input to the backbone
    depth: int
        The depth multiplier of the backbone
    dropout_rate: float
        The rate at which dropout is applied to the backbone

    Returns
    -------
    ForecastingModel

    """
    premix_config = ConvPremixConfig(input_channels=input_channels,
                                     kernel_size=1,
                                     dilation=1,
                                     stride=1)

    try:
        ml = MultilevelType[multilevel.upper()]
    except KeyError:
        raise ValueError(f'`multilevel` must be one of {[m.name for m in MultilevelType]}')
    backbone_config = LSTMBackboneConfig(multilevel=ml.name,
                                         hidden_to_input_channel_ratio=hidden_to_input_channel_ratio,
                                         receptive_field=receptive_field)

    head_configs = [UnboundedScalarForecastHeadConfig(horizon) for _ in range(num_quantiles)]
    return ForecastingModel(premix_config, backbone_config, head_configs, num_channels, depth, dropout_rate)
