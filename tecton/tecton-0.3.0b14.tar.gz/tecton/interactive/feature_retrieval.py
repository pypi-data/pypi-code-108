from typing import Mapping
from typing import Optional
from typing import Sequence
from typing import Union

import numpy as np
import pandas as pd
from pyspark.sql import DataFrame as pysparkDF

from tecton._internals import errors
from tecton._internals.feature_retrieval_internal import find_dependent_feature_set_items
from tecton._internals.utils import infer_timestamp
from tecton._internals.utils import is_bfc_mode_single
from tecton.interactive.data_frame import DataFrame
from tecton.interactive.data_frame import FeatureVector
from tecton.interactive.feature_service import FeatureService
from tecton.interactive.feature_view import FeatureView
from tecton.tecton_errors import TectonValidationError
from tecton_spark.feature_definition_wrapper import FeatureDefinitionWrapper as FeatureDefinition
from tecton_spark.feature_set_config import FeatureSetConfig
from tecton_spark.logger import get_logger

logger = get_logger("Tecton")


def get_online_features(
    features: Union[FeatureService, Sequence[FeatureView]],
    join_keys: Optional[Mapping[str, Union[int, np.int_, str, bytes]]] = None,
    include_join_keys_in_response: bool = False,
    request_data: Optional[Mapping[str, Union[int, np.int_, str, bytes, float]]] = None,
) -> FeatureVector:
    logger.warning(
        "Deprecated. Use 'FeatureService.get_online_features' or 'FeatureView.get_online_features' directly on the Feature Service or Feature View objects instead to fetch features from the Online Store. "
        + "See the api reference: https://docs.tecton.ai/api-reference/stubs/tecton.interactive.FeatureService.html#tecton.interactive.FeatureService.get_online_features"
    )
    if isinstance(features, FeatureService):
        return features.get_feature_vector(
            join_keys=join_keys,
            include_join_keys_in_response=include_join_keys_in_response,
            request_context_map=request_data,
        )
    elif isinstance(features, list):
        features_vector = FeatureVector([], [], [])
        for fv in features:
            features_vector._update(
                fv.get_feature_vector(
                    join_keys=join_keys,
                    include_join_keys_in_response=include_join_keys_in_response,
                    request_context_map=request_data,
                )
            )
        return features_vector
    else:
        raise TectonValidationError(f"Unexpected data type for features: {type(features)}")


def get_historical_features(
    features: Union[Sequence[FeatureView], FeatureService],
    spine: Union[pysparkDF, pd.DataFrame],
    from_source: bool = False,
    save: bool = False,
    save_as: str = None,
    timestamp_key: Optional[str] = None,
) -> DataFrame:
    logger.warning(
        "Deprecated. Use 'FeatureService.get_historical_features' or 'FeatureView.get_historical_features' directly on the Feature Service or Feature View objects instead to view historical values. "
        + "See the api reference: https://docs.tecton.ai/api-reference/stubs/tecton.interactive.FeatureService.html#tecton.interactive.FeatureService.get_historical_features"
    )
    if not timestamp_key:
        timestamp_key = infer_timestamp(spine)

    if isinstance(features, FeatureService):
        return features.get_historical_features(
            spine=spine, timestamp_key=timestamp_key, from_source=from_source, save=save, save_as=save_as
        )
    elif isinstance(features, list):
        for feature in features:
            if not isinstance(feature, FeatureView):
                raise TectonValidationError(
                    "The `features` parameter can only be a FeatureService, or a List of FeatureViews"
                )

        feature_set_config = FeatureSetConfig()
        for feature in features:
            fd = FeatureDefinition(feature._proto, feature._fco_container)

            if from_source and is_bfc_mode_single(fd):
                raise errors.FV_BFC_SINGLE_FROM_SOURCE

            if feature._proto.HasField("on_demand_feature_view"):
                inputs = find_dependent_feature_set_items(
                    feature._fco_container,
                    feature._proto.pipeline.root,
                    visited_inputs={},
                    fv_id=feature.id,
                    workspace_name=feature.workspace,
                )
                feature_set_config._definitions_and_configs = feature_set_config._definitions_and_configs + inputs
            feature_set_config._add(fd)
        return FeatureService._get_feature_dataframe_internal(
            feature_set_config, spine, timestamp_key, use_materialized_data=not from_source
        )
    else:
        raise TectonValidationError(
            "The `features` parameter can only be " "a FeatureService, or a List of FeatureViews"
        )
