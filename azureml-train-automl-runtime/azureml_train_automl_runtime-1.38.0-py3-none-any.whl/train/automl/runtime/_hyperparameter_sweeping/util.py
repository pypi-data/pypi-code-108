# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.core import Run


def _convert_string_to_bool(input: str) -> bool:
    return input.lower() in ["true"]


def _is_bool(arg: str) -> bool:
    return arg.lower() in ["true", "false"]


def _strip_first_last_double_quotes(arg_value: str) -> str:
    if arg_value.startswith('"') and arg_value.endswith('"'):
        arg_value = arg_value[1:-1]
    return arg_value


def prepare_properties(
        run: Run,
        pipeline_spec: str) -> None:
    Contract.assert_value(run, "run")
    run.add_properties({
        "runTemplate": "automl_child",
        "pipeline_spec": pipeline_spec})
