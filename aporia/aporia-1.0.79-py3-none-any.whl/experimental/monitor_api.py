from enum import Enum
from typing import Union

from aporia.core.context import get_context
from aporia.core.core_api import safe_api_function


class MonitorType(Enum):
    """The monitors implemented by Aporia."""

    MODEL_ACTIVITY = "model_activity"
    MISSING_VALUES = "missing_values"
    DATA_DRIFT = "data_drift"
    PREDICTION_DRIFT = "prediction_drift"
    VALUES_RANGE = "values_range"
    NEW_VALUES = "new_values"
    MODEL_STALENESS = "model_staleness"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    METRIC_CHANGE = "metric_change"
    CUSTOM_METRIC = "custom_metric"


@safe_api_function("Creating monitor failed, error: {}")
def create_monitor(
    name: str,
    monitor_type: Union[MonitorType, str],
    scheduling: str,
    configuration: dict,
    is_active: bool = True,
    custom_alert_description: str = None,
) -> str:
    """Creates a new monitor.

    Args:
        name: A name for the new monitor, which will be displayed in Aporia's dashboard
        monitor_type: The type of monitor to create
        scheduling: A cron expression that indicates how often the monitor will run
        configuration: The monitor's configuration
        is_active: Whether or not the new monitor should be created as active
        custom_alert_description: A custom description for the monitor's alerts

    Returns:
        Created Monitor ID.
    """
    context = get_context()

    response = context.event_loop.run_coroutine(
        context.http_client.post(
            url="/monitors",
            data={
                "name": name,
                "type": MonitorType(monitor_type).value,
                "scheduling": scheduling,
                "configuration": configuration,
                "is_active": is_active,
                "custom_alert_description": custom_alert_description,
            },
        )
    )

    return response["id"]


@safe_api_function("Deleting monitor failed, error: {}")
def delete_monitor(monitor_id: str):
    """Deletes a monitor.

    Args:
        monitor_id: ID of the monitor to delete
    """
    context = get_context()
    context.event_loop.run_coroutine(context.http_client.delete(url=f"/monitors/{monitor_id}"))
