from typing import Dict

from aporia.core.http_client import HttpClient
from aporia.core.types.field import FieldCategory, FieldType


async def get_model_version(
    http_client: HttpClient, model_id: str, model_version: str
) -> Dict[FieldCategory, Dict[str, FieldType]]:
    """Fetches model version schema.

    Args:
        http_client: Http client
        model_id: Model ID
        model_version: Model version

    Notes:
        * This only fetches field categories that can be used
          when reporting training data (features, predictions, raw_inputs)

    Returns:
        Model version schema
    """
    query = """
        query GetModelVersion(
            $modelId: String!,
            $modelVersion: String!,
        ) {
            modelVersionSchema(
                modelId: $modelId,
                modelVersion: $modelVersion,
            ) {
                features {
                    name
                    type
                }
                predictions {
                    name
                    type
                }
                rawInputs {
                    name
                    type
                }
            }
        }
    """

    variables = {"modelId": model_id, "modelVersion": model_version}

    result = await http_client.graphql(query, variables)
    return _build_model_version_schema(result["modelVersionSchema"])


def _build_model_version_schema(
    model_version_data: dict,
) -> Dict[FieldCategory, Dict[str, FieldType]]:
    schema = {}
    for category, fields in model_version_data.items():
        if fields is not None:
            schema[FieldCategory.from_camel_case(category)] = {
                field["name"]: FieldType(field["type"]) for field in fields
            }

    return schema
