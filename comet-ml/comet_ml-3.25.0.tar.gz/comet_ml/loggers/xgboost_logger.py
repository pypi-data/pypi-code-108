# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at http://www.comet.ml
#  Copyright (C) 2015-2021 Comet ML INC
#  This file can not be copied and/or distributed without the express
#  permission of Comet ML Inc.
# *******************************************************

import copy
import logging
from functools import partial

from .._typing import Any, Dict, Generator, List, Set, Tuple
from ..experiment import BaseExperiment
from ..monkey_patching import check_module

LOGGER = logging.getLogger(__name__)

XGBOOST_PARAMS_EXCLUDE = {"model", "evaluation_result_list", "iteration"}
XGBOOST_BOOSTER_ATTRS_EXCLUDE = {"handle"}


def _filter_attributes(obj, exclude_set):
    # type: (Any, Set[int]) -> Generator[Tuple[str, Any], None, None]
    for attribute_name in dir(obj):
        if attribute_name.startswith("_"):
            continue

        if attribute_name in exclude_set:
            continue

        attribute_value = getattr(obj, attribute_name)

        if callable(attribute_value):
            continue

        if attribute_value is None:
            continue

        yield (attribute_name, attribute_value)


def _get_env_params(env):
    # type: (Any) -> Generator[Tuple[str, Any], None, None]
    for attribute in _filter_attributes(env, XGBOOST_PARAMS_EXCLUDE):
        yield attribute


def _get_env_model_params(booster):
    # type: (Any) -> Generator[Tuple[str, Any], None, None]
    for attribute in _filter_attributes(booster, XGBOOST_BOOSTER_ATTRS_EXCLUDE):
        yield attribute


def _get_env_metrics(evaluation_result_list):
    # type: (List[Tuple[str, float]]) -> Dict[str, Dict[str, float]]
    dict_per_context = {}  # type: Dict[str, Dict[str, float]]
    for context_metric_name, metric_value in evaluation_result_list:
        context, metric_name = context_metric_name.split("-", 1)
        dict_per_context.setdefault(context, {})[metric_name] = metric_value

    return dict_per_context


def _get_booster_graph(booster):
    # type: (Any) -> str
    from xgboost import to_graphviz

    graphviz_source = to_graphviz(booster).source  # type: str
    return graphviz_source


def _comet_xgboost_callback(experiment, env):
    # type: (BaseExperiment, Any) -> None

    # First log the step
    try:
        experiment.set_step(env.iteration)
    except Exception:
        LOGGER.debug("Failed to log the XGBoost step", exc_info=True)

    # Then log the parameters
    try:
        if experiment.auto_param_logging:
            if not experiment._storage["xgboost"]["env_parameter_set"]:
                for attribute_name, attribute_value in _get_env_params(env):
                    experiment._log_parameter(
                        attribute_name, attribute_value, framework="xgboost"
                    )

                # Set only once the parameters
                experiment._storage["xgboost"]["env_parameter_set"] = True
    except Exception:
        LOGGER.debug("Failed to log the XGBoost params", exc_info=True)

    # Then log the model attributes
    try:
        if experiment.auto_param_logging:
            if not experiment._storage["xgboost"]["env_model_parameter_set"]:

                booster = env.model
                for attribute_name, attribute_value in _get_env_model_params(booster):
                    experiment._log_parameter(
                        attribute_name, attribute_value, framework="xgboost"
                    )

                # Set only once the model parameters
                experiment._storage["xgboost"]["env_model_parameter_set"] = True
    except Exception:
        LOGGER.debug("Failed to log the XGBoost booster attributes", exc_info=True)

    # Then the metrics
    try:
        if experiment.auto_metric_logging:
            xgboost_metrics = env.evaluation_result_list
            for context, metrics in _get_env_metrics(xgboost_metrics).items():
                with experiment.context_manager(context):
                    experiment._log_metrics(metrics, framework="xgboost")
    except Exception:
        LOGGER.debug("Failed to log the XGBoost metrics", exc_info=True)

    # And finally the model
    try:
        if experiment.log_graph:
            if not experiment._storage["xgboost"]["model_graph_set"]:
                booster = env.model

                booster_graph = _get_booster_graph(booster)

                experiment._set_model_graph(booster_graph, framework="xgboost")

                experiment._storage["xgboost"]["model_graph_set"] = True
    # xgboost.to_graphviz can raises ImportError if optional dependencies are not installed
    except ImportError as exc:
        experiment._log_once_at_level(logging.WARNING, str(exc), exc_info=True)
    except Exception:
        LOGGER.debug("Failed to log the XGBoost metrics", exc_info=True)


def _safe_comet_xgboost_callback(experiment, env):
    # type: (BaseExperiment, Any) -> None
    try:
        _comet_xgboost_callback(experiment, env)
    except Exception:
        LOGGER.debug("Unknown error calling XGBoost callback", exc_info=True)


def _log_xgboost_train_parameters(experiment, xgboost_params):
    # type: (BaseExperiment, Dict[str, Any]) -> None
    # Log XGBoost parameters
    if not experiment._storage["xgboost"]["train_parameter_set"]:
        params = {
            key: value for key, value in xgboost_params.items() if value is not None
        }
        experiment._log_parameters(params)
        experiment._storage["xgboost"]["train_parameter_set"] = True


def _xgboost_train(experiment, original, *args, **kwargs):
    # Positional args
    if len(args) >= 12:
        callbacks = args[11]

        if callbacks is None:
            callbacks = []
        else:
            # Copy callbacks list to avoid in-place mutation, it's gonna be the default behavior in
            # XGBoost anyway https://github.com/dmlc/xgboost/pull/6320
            callbacks = copy.copy(callbacks)

        # Inject or replace callbacks in new args
        args = args[:11] + (callbacks,) + args[12:]
    # Keyword args
    else:
        callbacks = kwargs.get("callbacks", None)
        if callbacks is None:
            callbacks = []
        else:
            # Copy callbacks list to avoid in-place mutation, it's gonna be the default behavior in
            # XGBoost anyway https://github.com/dmlc/xgboost/pull/6320
            callbacks = copy.copy(callbacks)

        # Inject or replace callbacks in new kwargs
        kwargs["callbacks"] = callbacks

    callbacks.append(partial(_safe_comet_xgboost_callback, experiment))

    # Log params passed to training.train
    if experiment.auto_param_logging:
        try:
            if len(args) >= 1:
                booster_params = args[0]
            elif "params" in kwargs:
                booster_params = kwargs["params"]
            else:
                raise ValueError("Couldn't find booster params")
            _log_xgboost_train_parameters(experiment, booster_params)
        except Exception:
            LOGGER.debug("Error auto-logging xgboost parameters", exc_info=True)

    return (args, kwargs)


def patch(module_finder):
    check_module("xgboost")
    module_finder.register_before("xgboost.training", "train", _xgboost_train)


check_module("xgboost")
