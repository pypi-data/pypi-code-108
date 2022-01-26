import base64
from typing import Any, Dict

from aporia.core.http_client import HttpClient
from aporia.inference.types.model_artifact import ModelArtifactType


async def upload_model_artifact(
    http_client: HttpClient,
    model_id: str,
    model_version: str,
    model_artifact: bytes,
    artifact_type: ModelArtifactType,
):
    """Logs fitted model object.

    Args:
        http_client: Http client
        model_id: Model ID.
        model_version: Model version.
        model_artifact: Binary model artifact
        artifact_type: Model artifact type
    """
    artifact_base64 = base64.b64encode(model_artifact).decode("ascii")
    await http_client.post(
        url=f"/models/{model_id}/versions/{model_version}/model_artifact",
        data={"artifact_base64": artifact_base64, "artifact_type": artifact_type.value},
    )


async def log_index_to_word_mapping(
    http_client: HttpClient,
    model_id: str,
    model_version: str,
    index_to_word_mapping: Dict[Any, Any],
):
    """Logs index to word mapping.

    Args:
        http_client: Http client
        model_id: Model ID.
        model_version: Model version.
        index_to_word_mapping: A mapping between a numeric index to a word.
    """
    mapping_list = list(index_to_word_mapping.items())
    try:
        int(mapping_list[0][0])  # If there's no error after this line, the key is a number
    except ValueError:
        # If the keys are not int, we need to flip the dictionary so that they will be
        mapping_list = [(value, key) for key, value in mapping_list]

    index_to_word_mapping_before_serialization = {str(key): value for key, value in mapping_list}

    await http_client.post(
        url=f"/models/{model_id}/versions/{model_version}/index_to_word_mapping",
        data={"index_to_word_mapping": index_to_word_mapping_before_serialization},
    )


async def set_feature_importance(
    http_client: HttpClient,
    model_id: str,
    model_version: str,
    feature_importance: Dict[str, float]
):
    """Logs fitted model object.

    Args:
        http_client: Http client
        model_id: Model ID.
        model_version: Model version.
        feature_importance: Feature name to importance mapping.
    """
    await http_client.post(
        url=f"/models/{model_id}/versions/{model_version}/feature_importance",
        data={"feature_importance": feature_importance},
    )
