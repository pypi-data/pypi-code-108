import pandas as pd
import requests

from typing import Dict, List, Optional, Tuple

from .auth import TransformAuth
from .models import (
    INF,
    NEGATIVE_ONE,
    CacheMode,
    Dimension,
    HealthReportStatus,
    Materialization,
    Metric,
    MqlMaterializeResp,
    MqlQueryStatusResp,
    MQLServer,
    MQLServerImage,
    ModelKey,
    PercentChange,
    Query,
    ServerHealthReport,
    TimeGranularity,
    UserState,
)
from .interfaces import MQLInterface


class MQLClient:
    """Wrapper that exposes MQLInterface and BackendInterface"""

    def __init__(  # noqa: D
        self, api_key: Optional[str] = None, mql_server_url: Optional[str] = None, override_config: bool = True
    ) -> None:
        self.context = TransformAuth(api_key, mql_server_url, override_config)

    def create_query(  # noqa: D
        self,
        metrics: List[str],
        dimensions: List[str],
        model_key_id: Optional[int] = None,
        where: Optional[str] = None,
        time_constraint: Optional[str] = None,
        time_granularity: Optional[str] = None,
        time_comparison: Optional[str] = None,
        order: Optional[List[str]] = None,
        limit: Optional[str] = None,
        cache_mode: Optional[str] = None,
        as_table: Optional[str] = None,
        allow_dynamic_cache: bool = True,
    ) -> MqlQueryStatusResp:
        """Builds a query in MQL and returns a MqlQueryStatusResp detailing the results."""
        model_key = self.get_model_key(model_key_id) if model_key_id else None
        query_id = self.context.mql_client.create_query(
            metrics,
            dimensions,
            model_key,
            where,
            time_constraint,
            TimeGranularity(time_granularity) if time_granularity else None,
            PercentChange(time_comparison) if time_comparison else None,
            order,
            None if limit in [INF, NEGATIVE_ONE, int(NEGATIVE_ONE)] else limit,
            CacheMode(cache_mode) if cache_mode else None,
            as_table,
            allow_dynamic_cache,
        )
        return self.context.mql_client.get_query_status(query_id)

    def query(  # noqa: D
        self,
        metrics: List[str],
        dimensions: List[str],
        model_key_id: Optional[int] = None,
        where: Optional[str] = None,
        time_constraint: Optional[str] = None,
        time_granularity: Optional[str] = None,
        time_comparison: Optional[str] = None,
        order: Optional[List[str]] = None,
        limit: Optional[str] = None,
        cache_mode: Optional[str] = None,
        as_table: Optional[str] = None,
        allow_dynamic_cache: bool = True,
        timeout: Optional[int] = None,
    ) -> pd.DataFrame:
        """Builds a query in MQL and returns pandas dataframe of queried result.

        TODO: Now that MQL optionally returns synchronous results on query creation,
        the python interface should support opportunistically returning these rather
        than having to always poll for results
        """
        model_key = self.get_model_key(model_key_id) if model_key_id else None
        query_id = self.context.mql_client.create_query(
            metrics,
            dimensions,
            model_key,
            where,
            time_constraint,
            TimeGranularity(time_granularity) if time_granularity else None,
            PercentChange(time_comparison) if time_comparison else None,
            order,
            None if limit in [INF, NEGATIVE_ONE, int(NEGATIVE_ONE)] else limit,
            CacheMode(cache_mode) if cache_mode else None,
            as_table,
            allow_dynamic_cache,
        )
        return self.get_query_dataframe(query_id, timeout)

    def list_queries(self, active_only: bool, limit: Optional[int] = None) -> List[Query]:
        """Retrieve a list of queries from MQL server."""
        return self.context.mql_client.get_queries(active_only=active_only, limit=limit)

    def list_metrics(self, model_key_id: Optional[int] = None) -> Dict[str, Metric]:
        """Returns a dictionary {metric_name: Metric}."""
        model_key = self.get_model_key(model_key_id) if model_key_id else None
        metrics = {m.name: m for m in self.context.mql_client.get_metrics(model_key)}
        metrics_metadata = self.context.backend_client.get_metrics_metadata()
        for data in metrics_metadata:
            metrics[data["name"]].input_metadata(data)
        return metrics

    def get_metric(self, metric_name: str, model_key_id: Optional[int] = None) -> Metric:
        """Retrieve a Metric Object by name."""
        model_key = self.get_model_key(model_key_id) if model_key_id else None
        metric = self.context.mql_client.get_metric_by_name(metric_name, model_key=model_key)
        metric.input_metadata(self.context.backend_client.get_metric_metadata_by_name(metric_name))
        return metric

    def create_materialization(  # noqa: D
        self,
        materialization_name: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        model_key_id: Optional[int] = None,
        output_table: Optional[str] = None,
        force: bool = False,
    ) -> MqlQueryStatusResp:
        """Implements Materialize (new) mutation in MQL/GQL and returns MqlQueryStatusResp object. Can be very expensive if a large time range is provided.

        Note: This is an asynchronous function (for synchronous function, see materialize)
        """
        model_key = self.get_model_key(model_key_id) if model_key_id else None
        query_id = self.context.mql_client.create_materialization(
            materialization_name, start_time, end_time, model_key, output_table, force
        )
        return self.context.mql_client.get_query_status(query_id)

    def materialize(  # noqa: D
        self,
        materialization_name: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        model_key_id: Optional[int] = None,
        output_table: Optional[str] = None,
        force: bool = False,
        timeout: Optional[int] = None,
    ) -> MqlMaterializeResp:
        """Builds materilization and returns MqlMaterializeResp object. Can be very expensive if a large time range is provided.

        Note: This is a synchronous function (for asynchronous function, see create_materialization)
        """
        model_key = self.get_model_key(model_key_id) if model_key_id else None
        query_id = self.context.mql_client.create_materialization(
            materialization_name, start_time, end_time, model_key, output_table, force
        )
        schema, table = self.get_materialization_result(query_id, timeout)
        return MqlMaterializeResp(table=table, schema=schema, query_id=query_id)

    def drop_materialization(  # noqa: D
        self,
        materialization_name: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        model_key_id: Optional[int] = None,
    ) -> MqlQueryStatusResp:
        """Implements drop materialization mutation in MQL/GQL. Can be very expensive if a large time range is provided.

        Note: This is an asynchronous function, the query may not be completed after the function returns.
        """
        model_key = self.get_model_key(model_key_id) if model_key_id else None
        query_id = self.context.mql_client.drop_materialization(materialization_name, start_time, end_time, model_key)
        return self.context.mql_client.get_query_status(query_id)

    def list_materializations(self, model_key_id: Optional[int] = None) -> List[Materialization]:
        """List the materializations for the Organization with their available metrics and dimensions."""
        model_key = self.get_model_key(model_key_id) if model_key_id else None
        return sorted(self.context.mql_client.get_materializations(model_key), key=lambda m: m.name)

    def commit_configs(self, config_dir: str, is_validation: bool = False) -> ModelKey:
        """Validates and commits yaml transform configs in the provided directory. Returns a ModelKey object."""
        return self.context.backend_client.commit_configs(config_dir=config_dir, is_validation=is_validation)

    def validate_configs(self, config_dir: str) -> ModelKey:
        """Finds and validates yaml transform configs in the provided directory. Returns a tuple (repo, branch, commit)"""
        return self.context.backend_client.validate_configs(config_dir)

    def promote_model(self, model_key: ModelKey) -> None:
        """Promotes a given model key to be the current/primary model for the organization"""
        return self.context.backend_client.promote_model_with_key(model_key=model_key)

    def health_report(self) -> List[ServerHealthReport]:
        """Performs a health check on all mql servers within the organization and returns List[ServerHealthReport]."""
        servers = self.context.backend_client.get_org_mql_servers()
        # in the case where the user has a local override, we still want to run a health report
        if self.context.mql_client.rest_api_url not in [s.url for s in servers]:
            servers.append(
                MQLServer(id=0, name="Local Override", url=self.context.mql_client.rest_api_url, is_org_default=False)
            )
        result = []
        for s in servers:
            test_server = MQLInterface(self.context.auth_header, s.url)
            try:
                version, health = test_server.get_health_report()
                result.append(
                    ServerHealthReport(
                        name=s.name, status=HealthReportStatus.SUCCESS.value, url=s.url, version=version, servers=health
                    )
                )
            except Exception as e:  # noqa: D
                result.append(
                    ServerHealthReport(
                        name=s.name,
                        status=HealthReportStatus.FAIL.value,
                        url=s.url,
                        error_message="Unable to connect to MQL server",
                    )
                )
        return result

    def drop_cache(self) -> bool:
        """Drops the entire MQL cache. Only do this is the cache is somehow corrupt. Returns boolean about operation result."""
        return self.context.mql_client.drop_cache()

    def identify(self) -> UserState:
        """Returns a UserState object describing current user."""
        return self.context.user_state

    def ping(self) -> requests.Response:
        """Returns ping response from currently selected MQL server."""
        return self.context.mql_client.ping()

    def list_servers(self) -> List[MQLServer]:
        """Returns a list of MQL servers within the organization."""
        return self.context.backend_client.get_org_mql_servers()

    def poll_for_query_completion(self, query_id: str, timeout: Optional[int] = None) -> MqlQueryStatusResp:
        """Poll for query completion, displaying some progress indication."""
        return self.context.mql_client.poll_for_query_completion(query_id, timeout)

    def get_materialization_result(self, query_id: str, timeout: Optional[int] = None) -> Tuple[str, str]:
        """Retrieves materialized table resulting from successful materialization query."""
        return self.context.mql_client.get_materialization_result(query_id, timeout)

    def get_query_dataframe(self, query_id: str, timeout: Optional[int] = None) -> pd.DataFrame:
        """Retrieves query results in Pandas DataFrame format.

        Includes logic for:
        1. Polling for completion
        2. Paging through results
        3. Converting JSON to a Pandas DataFrame
        """
        return self.context.mql_client.get_query_dataframe(query_id, timeout)

    def get_model_key(self, model_key_id: int) -> ModelKey:
        """Retrieves ModelKey object given the id."""
        return self.context.backend_client.get_model_key(model_key_id)

    def get_current_model_key(self) -> ModelKey:
        """Retrieves the current ModelKey object for the user's organization"""
        return self.context.backend_client.get_current_model_key()

    def latest_mql_image(self) -> MQLServerImage:
        """Retrieves the latest MQL server image."""
        return self.context.backend_client.get_latest_mql_server_image()

    def get_dimension_values(
        self,
        metric_name: str,
        dimension_name: str,
        model_key_id: Optional[int] = None,
        page_number: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> List[str]:
        """Retrieves a list of dimension values given a [metric_name, dimension_name]."""
        model_key = self.get_model_key(model_key_id) if model_key_id else None
        return self.context.mql_client.get_dimension_values(
            metric_name, dimension_name, model_key=model_key, page_number=page_number, page_size=page_size
        )

    def list_dimensions(self, model_key_id: Optional[int] = None) -> Dict[str, Dimension]:
        """Retrieves a list of all Dimension objects."""
        model_key = self.get_model_key(model_key_id) if model_key_id else None
        dimensions = self.context.mql_client.get_dimensions(model_key)
        return {dim.name: dim for dim in dimensions}

    def validate_model_against_data_warehouse(self, model_key_id: Optional[int] = None) -> List[str]:
        """Retrieves a list of any and all data warehosue validation issues with the model."""
        model_key = self.get_model_key(model_key_id) if model_key_id else None
        issues = self.context.mql_client.get_all_data_warehouse_validation_issues(model_key)
        return issues
