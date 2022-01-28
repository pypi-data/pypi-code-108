from typing import Iterable, List, Optional

from benchling_api_client.api.assay_runs import (
    archive_assay_runs,
    bulk_get_assay_runs,
    create_assay_runs,
    get_assay_run,
    list_assay_runs,
    list_automation_input_generators,
    list_automation_output_processors_deprecated,
    unarchive_assay_runs,
    update_assay_run,
)
from benchling_api_client.types import Response

from benchling_sdk.helpers.decorators import api_method
from benchling_sdk.helpers.logging_helpers import log_deprecation
from benchling_sdk.helpers.pagination_helpers import NextToken, PageIterator
from benchling_sdk.helpers.response_helpers import model_from_detailed
from benchling_sdk.helpers.serialization_helpers import none_as_unset, optional_array_query_param
from benchling_sdk.models import (
    AssayRun,
    AssayRunCreate,
    AssayRunsArchivalChange,
    AssayRunsArchive,
    AssayRunsArchiveReason,
    AssayRunsBulkCreateRequest,
    AssayRunsBulkCreateResponse,
    AssayRunsPaginatedList,
    AssayRunsUnarchive,
    AssayRunUpdate,
    AutomationFileInputsPaginatedList,
    AutomationInputGenerator,
    AutomationOutputProcessor,
    AutomationOutputProcessorsPaginatedList,
)
from benchling_sdk.services.base_service import BaseService


class AssayRunService(BaseService):
    """
    Assay Runs.

    Runs capture the details / parameters of a run that was performed. Results are usually nested under a run.

    See https://benchling.com/api/reference#/Assay%20Runs
    """

    @api_method
    def get_by_id(self, assay_run_id: str) -> AssayRun:
        """
        Get a run.

        See https://benchling.com/api/reference#/Assay%20Runs/getAssayRun
        """
        response = get_assay_run.sync_detailed(client=self.client, assay_run_id=assay_run_id)
        return model_from_detailed(response)

    @api_method
    def _assay_runs_page(
        self,
        schema_id: str,
        min_created_time: Optional[int] = None,
        max_created_time: Optional[int] = None,
        next_token: NextToken = None,
        page_size: Optional[int] = None,
        ids: Optional[Iterable[str]] = None,
    ) -> Response[AssayRunsPaginatedList]:
        return list_assay_runs.sync_detailed(
            client=self.client,
            schema_id=schema_id,
            min_created_time=none_as_unset(min_created_time),
            max_created_time=none_as_unset(max_created_time),
            ids=none_as_unset(optional_array_query_param(ids)),
            next_token=none_as_unset(next_token),
            page_size=none_as_unset(page_size),
        )

    def list(
        self,
        schema_id: str,
        min_created_time: Optional[int] = None,
        max_created_time: Optional[int] = None,
        page_size: Optional[int] = None,
        ids: Optional[Iterable[str]] = None,
    ) -> PageIterator[AssayRun]:
        """
        List runs.

        See https://benchling.com/api/reference#/Assay%20Runs/listAssayRuns
        """

        def api_call(next_token: NextToken) -> Response[AssayRunsPaginatedList]:
            return self._assay_runs_page(
                schema_id=schema_id,
                min_created_time=min_created_time,
                max_created_time=max_created_time,
                ids=ids,
                next_token=next_token,
                page_size=page_size,
            )

        def results_extractor(body: AssayRunsPaginatedList) -> Optional[List[AssayRun]]:
            return body.assay_runs

        return PageIterator(api_call, results_extractor)

    @api_method
    def bulk_get(self, assay_run_ids: Iterable[str]) -> Optional[List[AssayRun]]:
        """
        Bulk get runs by ID.

        See https://benchling.com/api/reference#/Assay%20Runs/bulkGetAssayRuns
        """
        response = bulk_get_assay_runs.sync_detailed(client=self.client, assay_run_ids=list(assay_run_ids))
        runs_list = model_from_detailed(response)
        return runs_list.assay_runs

    @api_method
    def create(self, assay_runs: Iterable[AssayRunCreate]) -> AssayRunsBulkCreateResponse:
        """
        Create 1 or more runs.

        See https://benchling.com/api/reference#/Assay%20Runs/createAssayRuns
        """
        create_runs = AssayRunsBulkCreateRequest(assay_runs=list(assay_runs))
        response = create_assay_runs.sync_detailed(client=self.client, json_body=create_runs)
        return model_from_detailed(response)

    @api_method
    def update(self, assay_run_id: str, assay_run: AssayRunUpdate) -> AssayRun:
        """
        Update a run.

        See https://benchling.com/api/reference#/Assay%20Runs/updateAssayRun
        """
        response = update_assay_run.sync_detailed(
            client=self.client, assay_run_id=assay_run_id, json_body=assay_run
        )
        return model_from_detailed(response)

    @api_method
    def _automation_input_generators_page(
        self,
        assay_run_id: str,
        modified_at: Optional[str] = None,
        next_token: NextToken = None,
    ) -> Response[AutomationFileInputsPaginatedList]:
        return list_automation_input_generators.sync_detailed(  # type: ignore
            client=self.client,
            assay_run_id=assay_run_id,
            modified_at=none_as_unset(modified_at),
            next_token=none_as_unset(next_token),
        )

    def automation_input_generators(
        self, assay_run_id: str, modified_at: Optional[str] = None
    ) -> PageIterator[AutomationInputGenerator]:
        """
        List AutomationInputGenerators by Run.

        See https://benchling.com/api/reference#/Assay%20Runs/listAutomationInputGenerators
        """

        def api_call(next_token: NextToken) -> Response[AutomationFileInputsPaginatedList]:
            return self._automation_input_generators_page(
                assay_run_id=assay_run_id, modified_at=modified_at, next_token=next_token
            )

        def results_extractor(body: AutomationFileInputsPaginatedList) -> List[AutomationInputGenerator]:
            return body.automation_input_generators

        return PageIterator(api_call, results_extractor)

    @api_method
    def _automation_output_processors_page(
        self,
        assay_run_id: str,
        next_token: NextToken = None,
    ) -> Response[AutomationOutputProcessorsPaginatedList]:
        """Deprecated in favor of lab_automation.automation_output_processors."""
        log_deprecation(
            "assay_runs.automation_output_processors_page", "lab_automation.automation_output_processors"
        )
        return list_automation_output_processors_deprecated.sync_detailed(  # type: ignore
            client=self.client,
            assay_run_id=assay_run_id,
            next_token=none_as_unset(next_token),
        )

    def automation_output_processors(self, assay_run_id: str) -> PageIterator[AutomationOutputProcessor]:
        """
        List AutomationOutputProcessors by Run.

        Deprecated in favor of lab_automation.automation_output_processors.

        See https://benchling.com/api/reference#/Assay%20Runs/listAutomationOutputProcessorsDeprecated
        """
        log_deprecation(
            "assay_runs.automation_output_processors", "lab_automation.automation_output_processors"
        )

        def api_call(next_token: NextToken) -> Response[AutomationOutputProcessorsPaginatedList]:
            return self._automation_output_processors_page(assay_run_id=assay_run_id, next_token=next_token)

        def results_extractor(
            body: AutomationOutputProcessorsPaginatedList,
        ) -> List[AutomationOutputProcessor]:
            return body.automation_output_processors

        return PageIterator(api_call, results_extractor)

    @api_method
    def archive(
        self, assay_run_ids: Iterable[str], reason: AssayRunsArchiveReason
    ) -> AssayRunsArchivalChange:
        """
        Archive Assay Runs.

        See https://benchling.com/api/reference#/Assay%20Runs/archiveAssayRuns
        """
        archive_request = AssayRunsArchive(assay_run_ids=list(assay_run_ids), reason=reason)
        response = archive_assay_runs.sync_detailed(client=self.client, json_body=archive_request)
        return model_from_detailed(response)

    @api_method
    def unarchive(self, assay_run_ids: Iterable[str]) -> AssayRunsArchivalChange:
        """
        Unarchive Assay Runs.

        See https://benchling.com/api/reference#/Assay%20Runs/unarchiveAssayRuns
        """
        unarchive_request = AssayRunsUnarchive(assay_run_ids=list(assay_run_ids))
        response = unarchive_assay_runs.sync_detailed(client=self.client, json_body=unarchive_request)
        return model_from_detailed(response)
