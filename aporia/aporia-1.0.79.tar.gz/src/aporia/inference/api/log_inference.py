import logging
from typing import List

from aporia.core.http_client import HttpClient
from aporia.core.logging_utils import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)


async def log_inference_fragments(
    http_client: HttpClient,
    model_id: str,
    model_version: str,
    environment: str,
    serialized_fragments: List[dict],
    await_insert: bool,
):
    """Reports a batch of inference fragments.

    Args:
        http_client: Http client
        model_id: Model ID
        model_version: Model version
        environment: Environment in which aporia is running.
        serialized_fragments: List of serialized fragment dicts.
        await_insert: True if the server should wait for the fragments
            to be stored before responding to the sdk.
    """
    query = """
        mutation LogPredict(
            $modelId: String!,
            $modelVersion: String!,
            $environment: String!,
            $predictions: [Prediction]!
            $isSync: Boolean!
        ) {
            logPredictions(
                modelId: $modelId,
                modelVersion: $modelVersion,
                environment: $environment,
                predictions: $predictions
                isSync: $isSync
            ) {
                warnings
            }
        }
    """

    variables = {
        "modelId": model_id,
        "modelVersion": model_version,
        "environment": environment,
        "predictions": serialized_fragments,
        "isSync": await_insert,
    }

    result = await http_client.graphql(query, variables)
    for warning in result["logPredictions"]["warnings"]:
        logger.warning(warning)
