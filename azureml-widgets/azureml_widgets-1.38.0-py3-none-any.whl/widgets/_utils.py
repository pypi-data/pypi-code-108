# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azureml.widgets._constants import (WIDGET_MAXIMUM_REFRESH_SLEEP_TIME,
                                        WIDGET_STARTING_REFRESH_SLEEP_TIME,
                                        AUTOML_WIDGET_MAXIMUM_REFRESH_SLEEP_TIME,
                                        AUTOML_WIDGET_STARTING_REFRESH_SLEEP_TIME,
                                        MULTIRUN_WIDGET_MAXIMUM_REFRESH_SLEEP_TIME,
                                        MULTIRUN_WIDGET_STARTING_REFRESH_SLEEP_TIME,
                                        WIDGET_REFRESH_MAXIMUM_SLEEP_TIME_DATABRICKS,
                                        WIDGET_STARTING_REFRESH_SLEEP_TIME_DATABRICKS)


def _update_widget_refresh_sleep_time(alpha=None):
    if alpha is None:
        return WIDGET_STARTING_REFRESH_SLEEP_TIME
    return (1 - alpha) * WIDGET_STARTING_REFRESH_SLEEP_TIME + alpha * WIDGET_MAXIMUM_REFRESH_SLEEP_TIME


def _update_automl_widget_refresh_sleep_time(alpha=None):
    if alpha is None:
        return AUTOML_WIDGET_STARTING_REFRESH_SLEEP_TIME
    return (1 - alpha) * AUTOML_WIDGET_STARTING_REFRESH_SLEEP_TIME + alpha * AUTOML_WIDGET_MAXIMUM_REFRESH_SLEEP_TIME


def _update_multirun_widget_refresh_sleep_time(alpha=None):
    if alpha is None:
        return MULTIRUN_WIDGET_STARTING_REFRESH_SLEEP_TIME
    interval = (1 - alpha) * MULTIRUN_WIDGET_STARTING_REFRESH_SLEEP_TIME
    interval += alpha * MULTIRUN_WIDGET_MAXIMUM_REFRESH_SLEEP_TIME
    return interval


def _update_databricks_widget_refresh_sleep_time(alpha=None):
    if alpha is None:
        return WIDGET_STARTING_REFRESH_SLEEP_TIME_DATABRICKS
    interval = (1 - alpha) * WIDGET_STARTING_REFRESH_SLEEP_TIME_DATABRICKS
    interval += alpha * WIDGET_REFRESH_MAXIMUM_SLEEP_TIME_DATABRICKS
    return interval


def _get_tag_value(run, tagName):
    if run is None:
        return None

    tags = run.get('tags') if isinstance(run, dict) else run.tags

    if tags is None or not isinstance(tags, dict):
        return None

    return tags.get("_aml_system_" + tagName, tags.get(tagName))
