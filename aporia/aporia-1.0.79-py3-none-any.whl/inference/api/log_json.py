import logging
from typing import Any

from aporia.core.http_client import HttpClient
from aporia.core.logging_utils import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)


async def log_json(
    http_client: HttpClient, model_id: str, model_version: str, environment: str, data: Any
):
    """Reports arbitrary data.

    Args:
        http_client: Http client
        model_id: Model ID
        model_version: Model version
        environment: Environment in which aporia SDK is running
        data: Data to report
    """
    query = """
    mutation LogArbitraryData(
        $modelId: String!,
        $modelVersion: String!,
        $environment: String!,
        $data: GenericScalar!
    ) {
        logArbitraryData(
            modelId: $modelId,
            modelVersion: $modelVersion,
            environment: $environment,
            data: $data
        ) {
            warnings
        }
    }
    """

    variables = {
        "modelId": model_id,
        "modelVersion": model_version,
        "environment": environment,
        "data": data,
    }

    result = await http_client.graphql(query, variables)
    for warning in result["logArbitraryData"]["warnings"]:
        logger.warning(warning)
