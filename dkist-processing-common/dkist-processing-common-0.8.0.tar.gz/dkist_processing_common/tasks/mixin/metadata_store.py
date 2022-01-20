"""
Mixin for a WorkflowDataTaskBase subclass which implements Metadata Store data access functionality
"""
import json
import logging
from typing import List
from typing import Union

from dkist_processing_common._util.config import get_mesh_config
from dkist_processing_common._util.graphql import GraphQLClient
from dkist_processing_common.models.graphql import CreateRecipeRunStatusResponse
from dkist_processing_common.models.graphql import DatasetCatalogReceiptAccountMutation
from dkist_processing_common.models.graphql import QualityReportMutation
from dkist_processing_common.models.graphql import RecipeRunMutation
from dkist_processing_common.models.graphql import RecipeRunProvenanceMutation
from dkist_processing_common.models.graphql import RecipeRunQuery
from dkist_processing_common.models.graphql import RecipeRunResponse
from dkist_processing_common.models.graphql import RecipeRunStatusMutation
from dkist_processing_common.models.graphql import RecipeRunStatusQuery
from dkist_processing_common.models.graphql import RecipeRunStatusResponse
from dkist_processing_common.models.json_encoder import QualityReportEncoder


logger = logging.getLogger(__name__)


class MetadataStoreMixin:
    @property
    def metadata_store_client(self) -> GraphQLClient:
        mesh_config = get_mesh_config()
        return GraphQLClient(
            f'http://{mesh_config["internal-api-gateway"]["mesh_address"]}:{mesh_config["internal-api-gateway"]["mesh_port"]}/graphql'
        )

    def metadata_store_change_recipe_run_to_inprogress(self):
        """
        Set the recipe run status to "INPROGRESS"
        """
        self._metadata_store_change_status(status="INPROGRESS", is_complete=False)

    def metadata_store_change_recipe_run_to_completed_successfully(self):
        """
        Set the recipe run status to "COMPLETEDSUCCESSFULLY"
        """
        self._metadata_store_change_status(status="COMPLETEDSUCCESSFULLY", is_complete=True)

    def metadata_store_add_dataset_receipt_account(
        self, dataset_id: str, expected_object_count: int
    ):
        self.metadata_store_client.execute_gql_mutation(
            mutation_base="createDatasetCatalogReceiptAccount",
            mutation_parameters=DatasetCatalogReceiptAccountMutation(
                datasetId=dataset_id, expectedObjectCount=expected_object_count
            ),
        )

    def metadata_store_record_provenance(self, is_task_manual: bool, library_versions: str):
        params = RecipeRunProvenanceMutation(
            inputDatasetId=self.metadata_store_input_dataset_id,
            isTaskManual=is_task_manual,
            recipeRunId=self.recipe_run_id,
            taskName=self.task_name,
            libraryVersions=library_versions,
            workflowVersion=self.workflow_version,
        )
        self.metadata_store_client.execute_gql_mutation(
            mutation_base="createRecipeRunProvenance", mutation_parameters=params
        )

    def metadata_store_add_quality_report(self, dataset_id: str, quality_report: List[dict]):
        quality_report_json = json.dumps(quality_report, cls=QualityReportEncoder, allow_nan=False)
        params = QualityReportMutation(datasetId=dataset_id, qualityReport=quality_report_json)
        self.metadata_store_client.execute_gql_mutation(
            mutation_base="createQualityReport", mutation_parameters=params
        )

    def metadata_store_recipe_run_configuration(self) -> dict:
        configuration_json = self._metadata_store_recipe_run().configuration
        if configuration_json is None:
            return {}
        try:
            configuration = json.loads(configuration_json)
            if not isinstance(configuration, dict):
                raise ValueError(
                    f"Invalid recipe run configuration format.  "
                    f"Expected json encoded dictionary, received json encoded {type(configuration)}"
                )
            return configuration
        except (json.JSONDecodeError, ValueError, TypeError, UnicodeDecodeError) as e:
            logger.error(f"Invalid recipe run configuration")
            raise e

    @property
    def metadata_store_input_dataset_document(self) -> str:
        return self._metadata_store_recipe_run().recipeInstance.inputDataset.inputDatasetDocument

    @property
    def metadata_store_input_dataset_id(self) -> int:
        return self._metadata_store_recipe_run().recipeInstance.inputDataset.inputDatasetId

    @property
    def metadata_store_recipe_instance_id(self) -> int:
        return self._metadata_store_recipe_run().recipeInstanceId

    @property
    def metadata_store_recipe_id(self) -> int:
        return self._metadata_store_recipe_run().recipeInstance.recipeId

    def _metadata_store_recipe_run(self, allow_cache: bool = True) -> RecipeRunResponse:
        is_cached = bool(getattr(self, "_recipe_run_cache", False))
        if is_cached and allow_cache:
            return self._recipe_run_cache
        response = self.metadata_store_client.execute_gql_query(
            query_base="recipeRuns",
            query_response_cls=RecipeRunResponse,
            query_parameters=RecipeRunQuery(recipeRunId=self.recipe_run_id),
        )
        self._recipe_run_cache = response[0]
        return self._recipe_run_cache

    def _metadata_store_change_status(self, status: str, is_complete: bool):
        """
        Change the recipe run status of a recipe run to the given status
        """
        recipe_run_status_id = self._metadata_store_recipe_run_status_id(status=status)
        if not recipe_run_status_id:
            recipe_run_status_id = self._metadata_store_create_recipe_run_status(
                status=status, is_complete=is_complete
            )
        self._metadata_store_update_status(recipe_run_status_id=recipe_run_status_id)

    def _metadata_store_recipe_run_status_id(self, status: str) -> Union[None, int]:
        """
        Find the id of a recipe run status
        """
        response = self.metadata_store_client.execute_gql_query(
            query_base="recipeRunStatuses",
            query_response_cls=RecipeRunStatusResponse,
            query_parameters=RecipeRunStatusQuery(recipeRunStatusName=status),
        )
        if len(response) > 0:
            return response[0].recipeRunStatusId

    def _metadata_store_create_recipe_run_status(self, status: str, is_complete: bool) -> int:
        """
        Add a new recipe run status to the db
        :param status: name of the status to add
        :param is_complete: does the new status correspond to an accepted completion state
        """
        recipe_run_statuses = {
            "INPROGRESS": "Recipe run is currently undergoing processing",
            "COMPLETEDSUCCESSFULLY": "Recipe run processing completed with no errors",
        }

        if not isinstance(status, str):
            raise TypeError(f"status must be of type str: {status}")
        if not isinstance(is_complete, bool):
            raise TypeError(f"is_complete must be of type bool: {is_complete}")
        recipe_run_status_response = self.metadata_store_client.execute_gql_mutation(
            mutation_base="createRecipeRunStatus",
            mutation_response_cls=CreateRecipeRunStatusResponse,
            mutation_parameters=RecipeRunStatusMutation(
                recipeRunStatusName=status,
                isComplete=is_complete,
                recipeRunStatusDescription=recipe_run_statuses[status],
            ),
        )
        return recipe_run_status_response.recipeRunStatus.recipeRunStatusId

    def _metadata_store_update_status(
        self,
        recipe_run_status_id: int,
    ):
        """
        Change the status of a given recipe run id
        :param recipe_run_status_id: the new status to use
        :param recipe_run_id: id of the recipe run to have the status changed
        """
        self.metadata_store_client.execute_gql_mutation(
            mutation_base="updateRecipeRun",
            mutation_parameters=RecipeRunMutation(
                recipeRunId=self.recipe_run_id, recipeRunStatusId=recipe_run_status_id
            ),
        )
