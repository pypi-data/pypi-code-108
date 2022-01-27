import json
from typing import Optional, Union, Dict

import click
from box import Box

from montecarlodata.config import Config
from montecarlodata.errors import complain_and_abort, manage_errors
from montecarlodata.queries.catalog import IMPORT_DBT_RUN_RESULTS
from montecarlodata.utils import GqlWrapper


class DbtRunResultsImportService:
    def __init__(self,
                 config: Config,
                 dbt_run_results: Union[str, Dict],
                 gql_wrapper: Optional[GqlWrapper] = None,
                 disable_handle_errors: Optional[bool] = False):
        self._gql_wrapper = gql_wrapper or GqlWrapper(
            mcd_id=config.mcd_id,
            mcd_token=config.mcd_token,
            disable_handle_errors=True
        )

        if isinstance(dbt_run_results, str):
            with open(dbt_run_results, 'r') as f:
                self._dbt_run_results = Box(json.load(f))
        else:
            self._dbt_run_results = Box(dbt_run_results)

        self._disable_handle_errors = disable_handle_errors

    @manage_errors
    def import_run_results(self,
                           project_name: Optional[str] = None,
                           run_id: Optional[str] = None,
                           run_logs: Optional[str] = None):
        try:
            dbt_schema_version = self._dbt_run_results.metadata.dbt_schema_version
        except KeyError:
            complain_and_abort(
                "Unexpected format of input file. Ensure that input file is a valid DBT run_results.json file")

        num_results_imported = self._do_make_request(dbt_schema_version, project_name, run_id, run_logs)
        click.echo(f"\nImported a total of {num_results_imported} DBT run results into Monte Carlo\n")

        return num_results_imported

    def _do_make_request(self,
                         dbt_schema_version: str,
                         project_name: str,
                         run_id: Optional[str] = None,
                         run_logs: Optional[str] = None) -> int:
        response = self._gql_wrapper.make_request_v2(
            query=IMPORT_DBT_RUN_RESULTS,
            operation='importDbtRunResults',
            variables=dict(
                dbtSchemaVersion=dbt_schema_version,
                runResultsJson=json.dumps(self._dbt_run_results),
                projectName=project_name,
                runId=run_id,
                runLogs=run_logs
            )
        )

        try:
            return response.data.response.numResultsImported
        except KeyError:
            return 0
