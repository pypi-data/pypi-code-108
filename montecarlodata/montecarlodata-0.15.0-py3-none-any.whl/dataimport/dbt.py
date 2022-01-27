import json
from typing import Optional, List, Tuple, Any, Union, Dict

import click
import requests
from box import Box
from requests import HTTPError

from montecarlodata.common.common import chunks
from montecarlodata.config import Config
from montecarlodata.errors import complain_and_abort, manage_errors, echo_error
from montecarlodata.queries.catalog import IMPORT_DBT_MANIFEST
from montecarlodata.utils import GqlWrapper


class DbtImportService:
    def __init__(self,
                 config: Config,
                 dbt_manifest: Union[str, Dict],
                 gql_wrapper: Optional[GqlWrapper] = None,
                 disable_handle_errors: Optional[bool] = False):
        self._gql_wrapper = gql_wrapper or GqlWrapper(
            mcd_id=config.mcd_id,
            mcd_token=config.mcd_token,
            disable_handle_errors=True
        )

        if isinstance(dbt_manifest, str):
            with open(dbt_manifest, 'r') as f:
                self._dbt_manifest = Box(json.load(f))
        else:
            self._dbt_manifest = Box(dbt_manifest)

        self._disable_handle_errors = disable_handle_errors

    @manage_errors
    def import_dbt_manifest(self, project_name: Optional[str] = None, batch_size: int = 10):
        try:
            dbt_schema_version = self._dbt_manifest.metadata.dbt_schema_version
            nodes = self._dbt_manifest.nodes
        except KeyError:
            complain_and_abort("Unexpected format of input file. Ensure that input file is a valid DBT manifest.json file")

        node_items = list(nodes.items())
        click.echo(f"\nImporting {len(node_items)} DBT objects into Monte Carlo catalog. please wait...")

        node_ids_imported = []
        all_bad_responses = []
        for nodes_items in chunks(node_items, batch_size):
            node_ids, bad_responses = self._do_make_request(dbt_schema_version, nodes_items, project_name)
            if len(node_ids) > 0:
                click.echo(f"Imported {len(node_ids)} DBT objects.")
            node_ids_imported.extend(node_ids)
            all_bad_responses.extend(bad_responses)

        if all_bad_responses:
            echo_error("\nEncountered invalid responses.", all_bad_responses)

        click.echo(f"\nImported a total of {len(node_ids_imported)} DBT objects into Monte Carlo catalog.\n")

        return node_ids_imported

    def _do_make_request(self, dbt_schema_version: str, nodes_items_list: List, project_name: Optional[str]) -> Tuple[List[str], List[Any]]:
        try:
            response = self._gql_wrapper.make_request_v2(
                query=IMPORT_DBT_MANIFEST,
                operation='importDbtManifest',
                variables=dict(
                    dbtSchemaVersion=dbt_schema_version,
                    manifestNodesJson=json.dumps(dict(nodes_items_list)),
                    projectName=project_name
                )
            )

            try:
                return response.data.response.nodeIdsImported, []
            except KeyError:
                return [], [response]

        except HTTPError as e:
            if e.response.status_code == requests.codes.gateway_timeout:
                click.echo(f"Import timed out, trying again with smaller batches.")

                if len(nodes_items_list) == 1:
                    complain_and_abort("Could not split batch any further, exiting!")

                # Possible for the request to time out if there is too much data
                # Just send each one-by-one
                all_node_ids, all_bad_requests = [], []
                for single_nodes_items in chunks(nodes_items_list, 1):
                    node_ids, bad_requests = self._do_make_request(dbt_schema_version, single_nodes_items, project_name)
                    all_node_ids.extend(node_ids)
                    all_bad_requests.extend(all_bad_requests)

                return all_node_ids, all_bad_requests
            else:
                raise