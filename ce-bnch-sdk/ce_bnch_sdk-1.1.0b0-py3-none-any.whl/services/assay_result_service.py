from datetime import datetime
from typing import Iterable, List, Optional

from benchling_api_client.api.assay_results import (
    abort_assay_results_transaction,
    archive_assay_results,
    bulk_get_assay_results,
    commit_assay_results_transaction,
    create_assay_results,
    create_assay_results_in_transaction,
    create_assay_results_transaction,
    get_assay_result,
    list_assay_results,
    unarchive_assay_results,
)
from benchling_api_client.types import Response

from benchling_sdk.helpers.decorators import api_method
from benchling_sdk.helpers.pagination_helpers import NextToken, PageIterator
from benchling_sdk.helpers.response_helpers import model_from_detailed
from benchling_sdk.helpers.serialization_helpers import (
    array_query_param,
    none_as_unset,
    optional_array_query_param,
)
from benchling_sdk.helpers.transaction_manager import TransactionManager
from benchling_sdk.models import (
    AssayResult,
    AssayResultCreate,
    AssayResultIdsRequest,
    AssayResultIdsResponse,
    AssayResultsArchive,
    AssayResultsBulkCreateRequest,
    AssayResultsCreateResponse,
    AssayResultsPaginatedList,
    AssayResultTransactionCreateResponse,
)
from benchling_sdk.services.base_service import BaseService


class AssayResultService(BaseService):
    """
    Assay Results.

    Results represent the output of assays that have been performed. You can customize the schemas of results to
    fit your needs. Results can link to runs, batches, and other types.

    See https://benchling.com/api/reference#/Assay%20Results
    """

    @api_method
    def get_by_id(self, assay_result_id: str) -> AssayResult:
        """
        Get a result.

        See https://benchling.com/api/reference#/Assay%20Results/getAssayResult
        """
        response = get_assay_result.sync_detailed(client=self.client, assay_result_id=assay_result_id)
        return model_from_detailed(response)

    @api_method
    def _assay_results_page(
        self,
        schema_id: str,
        min_created_time: Optional[datetime] = None,
        max_created_time: Optional[datetime] = None,
        entity_ids: Optional[Iterable[str]] = None,
        assay_run_ids: Optional[Iterable[str]] = None,
        next_token: NextToken = None,
        page_size: Optional[int] = None,
        ids: Optional[Iterable[str]] = None,
        storage_ids: Optional[Iterable[str]] = None,
    ) -> Response[AssayResultsPaginatedList]:
        entity_ids_string = optional_array_query_param(entity_ids)
        assay_run_ids_string = optional_array_query_param(assay_run_ids)
        return list_assay_results.sync_detailed(
            client=self.client,
            schema_id=schema_id,
            min_created_time=none_as_unset(min_created_time),
            max_created_time=none_as_unset(max_created_time),
            entity_ids=none_as_unset(entity_ids_string),
            assay_run_ids=none_as_unset(assay_run_ids_string),
            ids=none_as_unset(optional_array_query_param(ids)),
            storage_ids=none_as_unset(optional_array_query_param(storage_ids)),
            next_token=none_as_unset(next_token),
            page_size=none_as_unset(page_size),
        )

    def list(
        self,
        schema_id: str,
        min_created_time: Optional[datetime] = None,
        max_created_time: Optional[datetime] = None,
        entity_ids: Optional[Iterable[str]] = None,
        assay_run_ids: Optional[Iterable[str]] = None,
        page_size: Optional[int] = None,
        ids: Optional[Iterable[str]] = None,
        storage_ids: Optional[Iterable[str]] = None,
    ) -> PageIterator[AssayResult]:
        """
        List results.

        See https://benchling.com/api/reference#/Assay%20Results/listAssayResults
        """

        def api_call(next_token: NextToken) -> Response[AssayResultsPaginatedList]:
            return self._assay_results_page(
                schema_id=schema_id,
                min_created_time=min_created_time,
                max_created_time=max_created_time,
                entity_ids=entity_ids,
                assay_run_ids=assay_run_ids,
                ids=ids,
                storage_ids=storage_ids,
                next_token=next_token,
                page_size=page_size,
            )

        def results_extractor(body: AssayResultsPaginatedList) -> Optional[List[AssayResult]]:
            return body.assay_results

        return PageIterator(api_call, results_extractor)

    @api_method
    def bulk_get(self, assay_result_ids: Iterable[str]) -> Optional[List[AssayResult]]:
        """
        Bulk get assay results.

        Up to 200 IDs can be specified at once.

        See https://benchling.com/api/reference#/Assay%20Results/bulkGetAssayResults
        """
        result_ids_string = array_query_param(assay_result_ids)
        response = bulk_get_assay_results.sync_detailed(
            client=self.client, assay_result_ids=result_ids_string
        )
        results_list = model_from_detailed(response)
        return results_list.assay_results

    @api_method
    def create(self, assay_results: Iterable[AssayResultCreate]) -> AssayResultsCreateResponse:
        """
        Create 1 or more results.

        See https://benchling.com/api/reference#/Assay%20Results/createAssayResults
        """
        create_results = AssayResultsBulkCreateRequest(assay_results=list(assay_results))
        response = create_assay_results.sync_detailed(client=self.client, json_body=create_results)
        return model_from_detailed(response)

    @api_method
    def archive(self, assay_result_ids: Iterable[str]) -> AssayResultIdsResponse:
        """
        Archive assay results.

        Only results that have not been added to a Notebook Entry can be Archived.
        Once results are attached to a notebook entry, they are tracked in the
        history of that notebook entry, and cannot be archived.

        See https://benchling.com/api/reference#/Assay%20Results/archiveAssayResults
        """
        archive_request = AssayResultsArchive(assay_result_ids=list(assay_result_ids))
        response = archive_assay_results.sync_detailed(client=self.client, json_body=archive_request)
        return model_from_detailed(response)

    @api_method
    def unarchive(self, assay_result_ids: Iterable[str]) -> AssayResultIdsResponse:
        """
        Unarchive assay results.

        See https://benchling.com/api/reference#/Assay%20Results/unarchiveAssayResults
        """
        unarchive_request = AssayResultIdsRequest(assay_result_ids=list(assay_result_ids))
        response = unarchive_assay_results.sync_detailed(client=self.client, json_body=unarchive_request)
        return model_from_detailed(response)

    @api_method
    def create_transaction(self) -> AssayResultTransactionCreateResponse:
        """
        Create a transaction.

        See https://benchling.com/api/reference#/Assay%20Results/createAssayResultsTransaction
        """
        response = create_assay_results_transaction.sync_detailed(client=self.client)
        return model_from_detailed(response)

    @api_method
    def create_results_in_transaction(
        self, transaction_id: str, assay_results: Iterable[AssayResultCreate]
    ) -> AssayResultsCreateResponse:
        """
        Create results in a transaction.

        See https://benchling.com/api/reference#/Assay%20Results/createAssayResultsInTransaction
        """
        create_request = AssayResultsBulkCreateRequest(assay_results=list(assay_results))
        response = create_assay_results_in_transaction.sync_detailed(
            client=self.client, transaction_id=transaction_id, json_body=create_request
        )
        return model_from_detailed(response)

    @api_method
    def commit_transaction(self, transaction_id: str) -> AssayResultTransactionCreateResponse:
        """
        Commit results in an active transaction.

        Committing a transaction will cause all results that have been uploaded to be saved and visible to others.

        See https://benchling.com/api/reference#/Assay%20Results/commitAssayResultsTransaction
        """
        response = commit_assay_results_transaction.sync_detailed(
            client=self.client, transaction_id=transaction_id
        )
        return model_from_detailed(response)

    @api_method
    def abort_transaction(self, transaction_id: str) -> AssayResultTransactionCreateResponse:
        """
        Abort a transaction.

        Aborting a transaction will discard all uploaded results.

        See https://benchling.com/api/reference#/Assay%20Results/abortAssayResultsTransaction
        """
        response = abort_assay_results_transaction.sync_detailed(
            client=self.client, transaction_id=transaction_id
        )
        return model_from_detailed(response)

    def transaction_manager(self) -> TransactionManager:
        """
        Create a Python context manager for adding results within a transaction.

        When the context exits, the transaction manager will attempt to commit
        the transaction.

        If an unhandled error occurs within the context, the transaction manager
        will automatically attempt to abort the transaction.

        :return: A Python context manager for the transaction
        :rtype: TransactionManager
        """

        def create_trans() -> str:
            return self.create_transaction().id

        def abort_trans(transaction_id: str) -> str:
            return self.abort_transaction(transaction_id=transaction_id).id

        def commit_trans(transaction_id: str) -> str:
            return self.commit_transaction(transaction_id=transaction_id).id

        def append_rows(transaction_id: str, rows: Iterable[AssayResultCreate]) -> List[str]:
            return self.create_results_in_transaction(
                transaction_id=transaction_id, assay_results=rows
            ).assay_results

        return TransactionManager(
            create_transaction_call=create_trans,
            abort_transaction_call=abort_trans,
            commit_transaction_call=commit_trans,
            append_row_call=append_rows,
        )
