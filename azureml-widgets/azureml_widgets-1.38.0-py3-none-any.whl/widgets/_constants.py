# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Constants used in the widgets."""

WIDGET_MODULE_NAME = "azureml_widgets"

WIDGET_REFRESH_TIME_OVERRIDE = "AZUREML_OVERRIDE_ALL_WIDGET_REFRESH_TIME"

# Maximum sleep time (in seconds) between widget refresh
WIDGET_MAXIMUM_REFRESH_SLEEP_TIME = 60
MULTIRUN_WIDGET_MAXIMUM_REFRESH_SLEEP_TIME = 60
AUTOML_WIDGET_MAXIMUM_REFRESH_SLEEP_TIME = 60
WIDGET_REFRESH_MAXIMUM_SLEEP_TIME_DATABRICKS = 120

# Starting sleep time (in seconds between widget refresh)
WIDGET_STARTING_REFRESH_SLEEP_TIME = 5
MULTIRUN_WIDGET_STARTING_REFRESH_SLEEP_TIME = 20
AUTOML_WIDGET_STARTING_REFRESH_SLEEP_TIME = 30
WIDGET_STARTING_REFRESH_SLEEP_TIME_DATABRICKS = 120

# ParallelRunStep constants
PRS_REFRESH_INTERVAL_IN_SECONDS = 30
