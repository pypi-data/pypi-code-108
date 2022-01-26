from typing import List

from aporia.core.context import get_context
from aporia.core.core_api import safe_api_function
from aporia.core.errors import AporiaError


class ModelVersion:
    """Model version."""

    def __init__(self, id: str, name: str, model_id: str, model_type: str):
        """Initializes a ModelVersion object.

        Args:
            id: Model Version ID.
            name: Model version name (e.g v1).
            model_id: Model identifier, as received from the Aporia dashboard.
            model_type: Model type (also known as objective - see notes).

        Notes:
            * The supported model types are:
                * "regression" - for regression models
                * "binary" - for binary classification models
                * "multiclass" - for multiclass classification models
        """
        self.id = id
        self.model_id = model_id
        self.model_type = model_type
        self.name = name

    @staticmethod
    def from_dict(data: dict) -> "ModelVersion":
        """Initializes a ModelVersion object from a Python dictionary.

        Args:
            data: Python dictionary to deserialize.

        Returns:
            ModelVersion object
        """
        return ModelVersion(
            id=data["id"],
            name=data["name"],
            model_id=data["model_id"],
            model_type=data["model_type"],
        )


@safe_api_function("Get model versions failed, error: {}")
def get_model_versions(model_id: str) -> List[ModelVersion]:
    """Retrieve all versions of a model.

    Args:
        model_id: The ID of the model to retrieve versions for.

    Returns:
        List of model versions.
    """
    query = """
        query($modelID: String!) {
            model_versions(where: { model_id: { _eq: $modelID } }) {
                id
                model_id
                model_type
                name
            }
        }
    """

    variables = {
        "modelID": model_id,
    }

    context = get_context()
    response = context.event_loop.run_coroutine(
        context.http_client.graphql(query, variables, graphql_url="/v1/tenant-hasura/v1/graphql")
    )

    return [ModelVersion.from_dict(model_version) for model_version in response["model_versions"]]


@safe_api_function("Deleting model version failed, error: {}")
def delete_model_version(model_id: str, model_version: str):
    """Delete a model version by name.

    Args:
        model_id: Model identifier, as received from the Aporia dashboard.
        model_version: The name of the model version to delete.
    """
    model_versions = get_model_versions(model_id)
    if len(model_versions) == 1:
        raise AporiaError("Cannot delete model version if there is only one version for a model")

    model_version_to_delete = next(
        filter(lambda item: item.name == model_version, model_versions), None
    )
    if model_version_to_delete is None:
        raise AporiaError(f"Couldn't find model version: {model_version}")

    context = get_context()

    response = context.event_loop.run_coroutine(
        context.http_client.graphql(
            query="""
                mutation deleteESIndex(
                    $modelId: String,
                    $modelVersionId: String,
                    $environmentId: String,
                    $dataTimestamp: DateTime,
                    $indexType: String
                ) {
                    deleteESIndex(
                        modelId: $modelId,
                        modelVersionId: $modelVersionId,
                        environmentId: $environmentId,
                        dataTimestamp: $dataTimestamp,
                        indexType: $indexType
                    ) {
                        acknowledged
                    }
                }
            """,
            variables={"modelVersionId": model_version_to_delete.id, "indexType": None},
            graphql_url="/v1/tenant-hasura/v1/graphql",
        )
    )

    if not response["deleteESIndex"].get("acknowledged"):
        raise AporiaError(
            f"Could not delete data for model version: {model_version}. This might be a temporary issue. Please try again later."
        )

    response = context.event_loop.run_coroutine(
        context.http_client.graphql(
            query="""
                mutation deleteModelVersion($modelVersionId: UUID!) {
                    deleteModelVersion(modelVersionId: $modelVersionId) {
                        deleted
                    }
                }
            """,
            variables={"modelVersionId": model_version_to_delete.id},
            graphql_url="/v1/tenant-hasura/v1/graphql",
        )
    )

    if not response["deleteModelVersion"]["deleted"]:
        raise AporiaError(f"Failed to delete model version: {model_version}")
