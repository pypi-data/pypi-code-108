from dataclasses import asdict
from dbt.node_types import NodeType
from dbt.contracts.results import (
    RunResult,
    SourceFreshnessResult,
    NodeStatus,
    NodeResult,
)

from .node import parse_node
from ..logger import dbt_to_log_status
from ..types import Freshness, Message, Reporting
from ..utils.tools import freshness_age_to_unit, get_full_db_id


class Formatter:
    @classmethod
    def _get_freshness(cls, result: SourceFreshnessResult) -> Freshness:
        fresh = result.node.freshness
        is_warning = result.status == NodeStatus.Warn
        unit = fresh.warn_after.period if is_warning else fresh.error_after.period
        threshold = fresh.warn_after.count if is_warning else fresh.error_after.count

        return Freshness(
            unit=unit,
            threshold=threshold,
            loader=result.node.loader,
            age=freshness_age_to_unit(result.age, unit),
        )

    @classmethod
    def _get_reporting(cls, result: NodeResult) -> Reporting:
        rows, freshness = None, None
        if isinstance(result, SourceFreshnessResult):
            freshness = cls._get_freshness(result)

        if isinstance(result, RunResult):
            rows = result.adapter_response.get("rows_affected", None)

        return Reporting(
            rows=rows,
            freshness=freshness,
            timing=result.timing,
            execution_time=result.execution_time,
        )

    @classmethod
    def _get_source_components(cls, result: SourceFreshnessResult) -> Message:
        reporting = cls._get_reporting(result)
        freshness = reporting.freshness

        is_error = result.status in (NodeStatus.Error or NodeStatus.RuntimeErr)
        is_warning = result.status == NodeStatus.Warn

        db_id = get_full_db_id(
            result.node.database, result.node.schema, result.node.name
        )

        title_id = "out of date" if (is_error or is_warning) else "up to date"
        title = f"Source freshness {title_id}."

        error = None
        message = f"Source `{db_id}` is up to date"
        if is_error or is_warning:
            modifier = "failure" if is_error else "warning"
            message = f"Source `{db_id}` is out of date, {modifier} threshold exceeded"

            error = (
                f"Freshness of {freshness.age} {freshness.unit}(s) exceeded the"
                + f" {modifier} threshold of {freshness.threshold} {freshness.unit}(s)"
            )

        error = result.message if result.message else error

        return Message(
            title=title,
            message=message,
            error=error,
            reporting=reporting,
            context={**parse_node(result), **asdict(freshness)},
            level=dbt_to_log_status(result.status),
        )

    @classmethod
    def _get_model_components(cls, result: RunResult) -> Message:
        reporting = cls._get_reporting(result)

        depends_on = ", ".join(set(result.node.depends_on.nodes)).upper()
        title = f"{result.node.config.materialized.capitalize()} model {result.status}."
        target = get_full_db_id(
            result.node.database, result.node.schema, result.node.name
        )
        message = f"*[{result.status.upper()}]* model `{target}` that depends on `{depends_on}`"

        return Message(
            title=title,
            message=message,
            error=result.message,
            reporting=reporting,
            context=parse_node(result),
            level=dbt_to_log_status(result.status),
        )

    @classmethod
    def _get_test_components(cls, result: RunResult) -> Message:
        reporting = cls._get_reporting(result)

        error = None
        test_name = result.node.name
        test_database = result.node.database
        title = f"[{result.status.upper()}] Test {test_name}"
        message = (
            f"*[{result.status.upper()}]* Test {test_name} in `{test_database.upper()}`"
        )

        if result.status in (NodeStatus.Warn, NodeStatus.Fail, NodeStatus.Error):
            error = f"Got {result.message} results, expected 0"

        return Message(
            title=title,
            message=message,
            error=error,
            reporting=reporting,
            context=parse_node(result),
            level=dbt_to_log_status(result.status),
        )

    @classmethod
    def _get_snapshot_components(cls, result: RunResult) -> Message:
        reporting = cls._get_reporting(result)
        target = get_full_db_id(
            result.node.database, result.node.schema, result.node.name
        )

        is_error = result.status in (NodeStatus.Error, NodeStatus.Skipped)

        title = f'Snapshot {"failed" if is_error else "completed"}'
        message = f"*[{result.status.upper()}]* snapshot with target `{target}`"

        return Message(
            title=title,
            message=message,
            error=result.message,
            reporting=reporting,
            context=parse_node(result),
            level=dbt_to_log_status(result.status),
        )

    @classmethod
    def format(cls, result: NodeResult) -> Message:
        resource_type = result.node.resource_type
        switcher = {
            NodeType.Source: cls._get_source_components,
            NodeType.Model: cls._get_model_components,
            NodeType.Test: cls._get_test_components,
            NodeType.Snapshot: cls._get_snapshot_components,
        }
        return switcher.get(resource_type, cls._get_model_components)(result)
