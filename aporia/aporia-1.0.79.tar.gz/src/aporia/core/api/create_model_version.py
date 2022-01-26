import logging
from typing import Dict, List, Optional, Union

from aporia.core.errors import AporiaError
from aporia.core.http_client import HttpClient
from aporia.core.logging_utils import LOGGER_NAME
from aporia.core.types.field import FieldCategory, FieldType

VALID_FIELD_TYPES = [field_type.value for field_type in FieldType]

logger = logging.getLogger(LOGGER_NAME)


async def run_create_model_version_query(
    http_client: HttpClient,
    model_id: str,
    model_version: str,
    model_type: str,
    features: Dict[str, str],
    predictions: Dict[str, str],
    raw_inputs: Optional[Dict[str, str]] = None,
    metrics: Optional[Dict[str, str]] = None,
    model_data_type: Optional[str] = None,
    multiclass_labels: Optional[List[str]] = None,
    feature_importance: Optional[Dict[str, float]] = None,
):
    """Defines the schema for a specific model version.

    Args:
        http_client: Http client
        model_id: Model ID
        model_version: Model Version
        model_type: Model type
        features: Feature fields
        predictions: Prediction fields
        raw_inputs: Raw input fields.
        metrics: Prediction metric fields.
        model_data_type: Model data type.
        multiclass_labels: Labels of multiclass or binary model.
        feature_importance: Features' importance.
    """

    model_version_input = {
        "name": model_version,
        "model_type": model_type,
        "version_schema": {
            "features": features,
            "predictions": predictions,
            "raw_inputs": raw_inputs,
            "metrics": metrics,
            "feature_positions": generate_feature_positions(features),
            "model_data_type": model_data_type,
            "multiclass_labels": multiclass_labels
        },
        "feature_importance": feature_importance
    }

    await http_client.post(
        url=f"/models/{model_id}/versions",
        data=model_version_input,
    )


def generate_feature_positions(features: Dict[str, str]) -> List[Dict[str, Union[str, int]]]:
    """Generate features' position from a features dict.

    Args:
        features: features dict

    Returns:
        Features to positions dictionary.
    """
    return {field_name: index for index, field_name in enumerate(features.keys())}
