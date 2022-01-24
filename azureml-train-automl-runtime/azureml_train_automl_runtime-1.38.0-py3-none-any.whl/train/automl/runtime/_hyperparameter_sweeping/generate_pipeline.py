# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import argparse
import json
from typing import Any, Dict

from azureml.train.automl.runtime._hyperparameter_sweeping._argument_parser import make_arg, \
    add_preprocessor_parameters, clean_args, process_models_args
from azureml.train.automl.runtime._hyperparameter_sweeping.util import _strip_first_last_double_quotes, \
    _convert_string_to_bool


def generate_pipeline_spec(
        automl_settings: str,
        pipeline_id: str,
) -> str:
    """
    Generate valid pipeline spec from passed in hyperparameters.
    """
    parser = argparse.ArgumentParser(description="hyperparameter tuning config", allow_abbrev=False)
    parser.add_argument(make_arg("model_name"), type=str,
                        help="model name",
                        default=None)

    add_preprocessor_parameters(parser)

    args, unknown_args = parser.parse_known_args()
    cleaned_unkown_args_dict = dict(zip(clean_args(unknown_args[::2]), unknown_args[1::2]))
    additional_hp = process_models_args(cleaned_unkown_args_dict)

    pipeline_spec_dict = {}  # type: Dict[str, Any]

    known_args_dict = vars(args)  # type: Dict[str, Any]
    print("known_args_dict is {}".format(known_args_dict))

    # generate preprocessor and model
    preprocessor_dict = {"spec_class": "preproc",
                         "class_name": _strip_first_last_double_quotes(
                             known_args_dict["preprocessor_name"])}  # type: Dict[str, Any]
    print("args.preprocessor_name is {}".format(known_args_dict["preprocessor_name"]))

    preprocessor_dict["module"] = "sklearn.preprocessing"
    preprocessor_dict["param_args"] = []
    preprocessor_dict["param_kwargs"] = {}

    # add preprocessor argument if any
    if known_args_dict["with_std"] is not None:
        preprocessor_dict["param_kwargs"]["with_std"] = _convert_string_to_bool(known_args_dict["with_std"])
    if known_args_dict["with_mean"] is not None:
        preprocessor_dict["param_kwargs"]["with_mean"] = _convert_string_to_bool(known_args_dict["with_mean"])
    if known_args_dict["with_centering"] is not None:
        preprocessor_dict["param_kwargs"]["with_centering"] = \
            _convert_string_to_bool(known_args_dict["with_centering"])
    if known_args_dict["with_scaling"] is not None:
        preprocessor_dict["param_kwargs"]["with_scaling"] = \
            _convert_string_to_bool(known_args_dict["with_scaling"])

    model_dict = \
        {"spec_class": "sklearn", "class_name": _strip_first_last_double_quotes(known_args_dict["model_name"]),
         "module": "automl.client.core.common.model_wrappers", "param_args": [],
         "param_kwargs": {}}  # type: Dict[str, Any]

    model_dict["param_kwargs"].update(additional_hp)

    # construct object and other parameters
    pipeline_spec_dict["objects"] = [preprocessor_dict, model_dict]

    pipeline_spec_dict["pipeline_id"] = pipeline_id
    pipeline_spec_dict["module"] = "sklearn.pipeline"
    pipeline_spec_dict["class_name"] = "Pipeline"

    # convert to json string
    pipeline_spec_to_return = json.dumps(pipeline_spec_dict)
    print(pipeline_spec_to_return)
    return pipeline_spec_to_return
