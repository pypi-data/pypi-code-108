"""A simply parameterized model for predicting the mean and std of a time-varying gaussian."""

import dataclasses as dc

from forecast.models import ForecastingModel
from forecast.models.backbone.base import MultilevelType
from forecast.models.backbone.cell.residual_tcn_cell import CausalConvResidConfig
from forecast.models.backbone.repeated_cell import RepeatedCellBackboneConfig, RepeatMode
from forecast.models.forecast_head import StrictlyPositiveScalarForecastHeadConfig, UnboundedScalarForecastHeadConfig
from forecast.models.premix import ConvPremixConfig


def create_tcn_gaussian_forecaster(input_channels: int,
                                   num_cells_per_block: int, multilevel: str,
                                   horizon: int,
                                   num_channels: int, num_blocks: int, dropout_rate: float,
                                   init_dilation: int = 2) -> ForecastingModel:
    """This function creates a simply parameterized model which forecasts a time-varying gaussian.

    Parameters
    ----------
    input_channels: int
        The number of input channels in the data passed to the model
    num_cells_per_block: int
        The number of cells per cell block
    multilevel: str (one of 'cell', 'none', 'cell_list')
        How the output of the backbone is passed to the forecast heads (see `MultilevelType` for further details)
    horizon: int
        The number of samples to forecast
    num_channels: int
        The number of channels in the intermediate layers of the model
    num_blocks: int
        The depth scale factor (how many cell blocks are created)
    dropout_rate: float
        The rate at which dropout is applied
    init_dilation: int
        The dilation of the first TCN cell. Defaults to 2.

    Returns
    -------
    ForecastingModel
        A model which outputs a time-varying (mean, std) estimate

    Notes:
    ------
    The model DOES NOT sample from the gaussian defined by the parameters the model outputs.

    """
    premix_config = ConvPremixConfig(input_channels=input_channels,
                                     kernel_size=1,
                                     dilation=1,
                                     stride=1)

    base_cell = CausalConvResidConfig(num_prev_cell_inputs=1,
                                      kernel_size=2,
                                      dilation=init_dilation,
                                      stride=1)

    cell_configs = [dc.replace(base_cell, dilation=(2**i) * base_cell.dilation) for i in range(1, num_cells_per_block)]
    cell_configs = [base_cell] + cell_configs

    try:
        ml = MultilevelType[multilevel.upper()]
    except KeyError:
        raise ValueError(f'`multilevel` must be one of {[m.name for m in MultilevelType]}')
    backbone_config = RepeatedCellBackboneConfig(cell_configs=cell_configs,
                                                 multilevel=ml.name,
                                                 repeat_mode=RepeatMode.OUTER.name)

    mean_head_config = UnboundedScalarForecastHeadConfig(horizon)
    std_head_config = StrictlyPositiveScalarForecastHeadConfig(horizon)

    return ForecastingModel(premix_config,
                            backbone_config,
                            [mean_head_config, std_head_config],
                            num_channels, num_blocks, dropout_rate)
