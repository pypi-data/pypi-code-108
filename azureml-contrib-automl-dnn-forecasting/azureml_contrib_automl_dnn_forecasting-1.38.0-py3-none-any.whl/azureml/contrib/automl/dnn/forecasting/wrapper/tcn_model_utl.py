# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module for creating a model based on TCN."""
import math
import random
import logging
from typing import Sequence, List

import dataclasses as dc
from .forecast_wrapper import DNNParams
from ..datasets.timeseries_datasets import EmbeddingColumnInfo
from ..constants import TCNForecastParameters
from forecast.data.sources.data_source import DataSourceConfig
from forecast.models import ForecastingModel
from forecast.models.canned import create_tcn_quantile_forecaster
from forecast.models.backbone.base import MultilevelType
from forecast.models.backbone.cell.residual_tcn_cell import CausalConvResidConfig
from forecast.models.backbone.repeated_cell import RepeatedCellBackboneConfig, RepeatMode
from forecast.models.forecast_head import UnboundedScalarForecastHeadConfig
from forecast.models.premix import EmbeddingConfig, EmbeddingPremixConfig

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.core.shared.exceptions import ClientException
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    TCNEmbeddingInvalidFactor,
    TCNEmbeddingInvalidMultilevel,
    TCNEmbeddingUnsupportCalcType
)


logger = logging.getLogger(__name__)


def create_tcn_embedded_forecaster(input_channels: int,
                                   num_cells_per_block: int, multilevel: str,
                                   horizon: int, num_quantiles: int,
                                   num_channels: int, num_blocks: int, dropout_rate: float,
                                   dilation: int, embedding_configs: Sequence[EmbeddingConfig]) -> ForecastingModel:
    """
    Create a tcn model with grain embedding which forecasts the quantiles of a time-varying series.

    :param input_channels: The number of input channels in the data passed to the model
    :type:int

    :param num_cells_per_block: The number of cells per cell block
    :type:int

    :param multilevel: How the output of the backbone is passed to the forecast heads
    (see `MultilevelType` for further details)
    :type:str

    :param horizon: forecast horizon
    :type:int

    :param num_quantiles: number of quantiles predictions to make.
    :type:int

    :param num_channels: The number of channels in the intermediate layers of the model
    :type:int

    :param num_blocks: The depth scale factor (how many cell blocks are created)
    :type:int

    :param dropout_rate: The rate at which dropout is applied
    :type:float

    :param dilation: The dilation of the first TCN cell.
    :type:int

    :param embedding_configs: embedding configuration for each grain column.
    :type:Sequence[EmbeddingConfig]

    :return: a forecaster model.
    :rtype: ForecastingModel
    """
    premix_config = EmbeddingPremixConfig(input_channels=input_channels,
                                          embeddings=embedding_configs)

    base_cell = CausalConvResidConfig(num_prev_cell_inputs=1,
                                      kernel_size=2,
                                      dilation=dilation,
                                      stride=1)
    cell_configs = [dc.replace(base_cell, dilation=(2**i) * base_cell.dilation) for i in range(1, num_cells_per_block)]
    cell_configs = [base_cell] + cell_configs

    try:
        ml = MultilevelType[multilevel.upper()]
    except KeyError as e:
        raise ClientException._with_error(AzureMLError.create(
            TCNEmbeddingInvalidMultilevel, target="embed_factor",
            multilevel=multilevel.upper(),
            multi_levels=[m.name for m in MultilevelType],
            reference_code=ReferenceCodes._TCN_EMBEDDING_INVALID_MULTILEVEL)
        ) from e
    backbone_config = RepeatedCellBackboneConfig(cell_configs=cell_configs,
                                                 multilevel=ml.name,
                                                 repeat_mode=RepeatMode.OUTER.name)

    head_configs = [UnboundedScalarForecastHeadConfig(horizon) for _ in range(num_quantiles)]

    return ForecastingModel(premix_config,
                            backbone_config,
                            head_configs,
                            num_channels, num_blocks, dropout_rate)


def get_embedding_dim(grain_count: int, embed_calc_type: str, embed_factor: float) -> int:
    """
    Get the output embedding dim.

    :param grain_count: The number of items in the grain
    :type:int

    :param embed_calc_type: type of calculations to find embedding size
    :type:str

    :param embed_factor: The factor used in calculations
    :type:float

    :return: Target embedding size for the grain.
    :rtype: int
    """
    if embed_calc_type not in TCNForecastParameters.ROOT:
        raise ClientException._with_error(AzureMLError.create(
            TCNEmbeddingUnsupportCalcType, target="embed_calc_type", embed_calc_type=embed_calc_type,
            reference_code=ReferenceCodes._TCN_EMBEDDING_UNSUPPORTED_CALC_TYPE)
        )
    if embed_factor <= 0:
        raise ClientException._with_error(AzureMLError.create(
            TCNEmbeddingInvalidFactor, target="embed_factor", embed_factor=embed_factor,
            reference_code=ReferenceCodes._TCN_EMBEDDING_INVALID_FACTOR)
        )

    target_dim = grain_count ** (1 / embed_factor)

    target_dim = min(TCNForecastParameters.MAX_EMBEDDING_DIM, target_dim)
    return math.ceil(max(TCNForecastParameters.MIN_EMBEDDING_DIM, target_dim))


def build_canned_model(params: DNNParams, dset_config: DataSourceConfig, horizon: int, num_quantiles: int,
                       embedding_column_info: List[EmbeddingColumnInfo]) -> ForecastingModel:
    """
    Build a model based on config.

    :param params:  DNN parameters for the model.
    :type:DNNParams

    :param dset_config:  configuration for the model.
    :type:DataSourceConfig

    :param horizon: forecast horizon
    :type:int

    :param num_quantiles: number of quantiles predictions to make.
    :type:int

    :param embedding_column_info: List of each grain column details.
    :type:List[EmbeddingColumnInfo]

    :return: a forecaster model.
    :rtype: ForecastingModel
    """
    if dset_config.encodings:
        input_channels = dset_config.feature_channels + dset_config.forecast_channels +\
            sum(e.num_vals for e in dset_config.encodings) - len(dset_config.encodings)
    else:
        input_channels = dset_config.feature_channels + dset_config.forecast_channels

    # backbone architecture
    num_cells = params.get_value(TCNForecastParameters.NUM_CELLS, random.randint(3, 6))
    multilevel = params.get_value(TCNForecastParameters.MULTILEVEL, random.choice(list(MultilevelType)).name)

    # model hyper-parameters
    depth = params.get_value(TCNForecastParameters.DEPTH, random.randint(1, 3))
    num_channels = params.get_value(TCNForecastParameters.NUM_CHANNELS, random.choice([64, 128, 256]))
    dropout_rate = params.get_value(TCNForecastParameters.DROPOUT_RATE,
                                    random.choice([0, 0.1, 0.25, 0.4, 0.5]))
    dilation = params.get_value(TCNForecastParameters.DILATION, TCNForecastParameters.DILATION_DEFAULT)
    logger.info('Model used the following hyperparameters:'
                ' num_cells={}, multilevel={}, depth={}, num_channels={}, dropout_rate={},'
                ' dilation={}'.format(num_cells, multilevel, depth, num_channels, dropout_rate, dilation))

    embedding_needed = False
    embed_calc_type = params.get_value(TCNForecastParameters.EMBEDDING_TARGET_CALC_TYPE,
                                       TCNForecastParameters.EMBEDDING_TARGET_CALC_TYPE_DEFAULT)
    if embed_calc_type in TCNForecastParameters.ROOT and embedding_column_info:
        embedding_needed = True
        embed_factor = params.get_value(TCNForecastParameters.EMBEDDING_ROOT,
                                        TCNForecastParameters.EMBEDDING_ROOT_DEFAULT)
        embed_factor = float(embed_factor)
    if embedding_needed:
        embed_configs = []
        logger.info('Embedding on categorical columns in effect')
        for col in embedding_column_info:
            embedding_out_dim = get_embedding_dim(col.distinct_values, embed_calc_type, embed_factor)
            embed_config = EmbeddingConfig(col.index, col.distinct_values, embedding_out_dim)
            print(col.index, col.distinct_values, embedding_out_dim)
            logger.info(f'Embedding dimensions:feature_index={embed_config.feature_index}')
            logger.info(f'Embedding dimensions:input_dim={embed_config.input_dim}')
            logger.info(f'Embedding dimensions:output_dim={embed_config.output_dim}')
            embed_configs.append(embed_config)
        canned_model = create_tcn_embedded_forecaster(input_channels, num_cells, multilevel, horizon,
                                                      num_quantiles, num_channels, depth, dropout_rate,
                                                      dilation, embed_configs)
    else:
        canned_model = create_tcn_quantile_forecaster(input_channels, num_cells, multilevel, horizon,
                                                      num_quantiles, num_channels, depth, dropout_rate, dilation)
    return canned_model
