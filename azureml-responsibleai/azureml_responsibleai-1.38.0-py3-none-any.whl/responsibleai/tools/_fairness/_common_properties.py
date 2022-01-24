# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
import uuid

from ._constants import AssetPropertyKeys
from ._constants import FairlearnDashboardKeys
from ._constants import FairnessAssetTypes
from ._constants import PredictionTypeConvertors


_logger = logging.getLogger(__file__)
logging.basicConfig(level=logging.INFO)


def extract_common_properties(dashboard_dict,
                              dashboard_name,
                              experiment_id,
                              dataset_name=None,
                              dataset_id=None):
    """Fetch the common properties for all Assets.

    In a given upload, there are several properties set
    which are the same for all Assets. These include:
    - The name of the dashboard
    - The prediction type (e.g. 'binary_classification' or 'regression')
    - The upload_id
    - The experiment_id
    - The schema version
    - The name and id of the dataset used (both optional)
    - That this is a collection of dashboard metrics

    The generated dictionary can then be a base for uploads
    of specific Assets, which add their particular properties.
    Note that the upload_id is generated in this routine.
    """

    dashboard_prediction_type = dashboard_dict[FairlearnDashboardKeys.PREDICTION_TYPE]
    common_dict = {
        AssetPropertyKeys.DASHBOARD_NAME: dashboard_name,
        AssetPropertyKeys.UPLOAD_ID: str(uuid.uuid4()),
        AssetPropertyKeys.EXPERIMENT_ID: experiment_id,
        AssetPropertyKeys.FAIRNESS_ASSET_TYPE: FairnessAssetTypes.DASHBOARD_METRICS,
        AssetPropertyKeys.VERSION: dashboard_dict[FairlearnDashboardKeys.SCHEMA_VERSION],
        AssetPropertyKeys.PREDICTION_TYPE: PredictionTypeConvertors.DASHBOARD_TO_ASSET[dashboard_prediction_type]
    }

    if dataset_id is not None:
        common_dict[AssetPropertyKeys.DATASET_ID] = dataset_id
    if dataset_name is not None:
        common_dict[AssetPropertyKeys.DATASET_NAME] = dataset_name

    return common_dict
