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
#  This file can not be copied and/or distributed without
#  the express permission of Comet ML Inc.
# *******************************************************

import logging
import time

from ._typing import Any, Dict, List, Optional, Tuple, Union
from .config import get_config
from .connection import (
    LowLevelHTTPClient,
    get_optimizer_api_client,
    sanitize_url,
    url_join,
)
from .exceptions import INVALID_OPTIMIZATION_ID, CometRestApiException

LOGGER = logging.getLogger(__name__)


class Predictor(object):
    """
    Please email lcp-beta@comet.ml for comments or questions.
    """

    def __init__(
        self,
        experiment,
        mode=None,
        loss_name="loss",
        patience=10,
        best_callback=None,
        threshold=0.1,
        api=None,
        optimizer_id=None,
        start_step=10,
        time_interval=300,
        n_init_experiments=0,
        advanced_config=None,
    ):
        LOGGER.warning(
            "DEPRECATED: The Predictor service is deprecated and will be fully removed on February 2022."
        )
        """
        Please email lcp-beta@comet.ml for comments or questions.
        """
        self.config = get_config()
        self.experiment = experiment

        self.loss_name = loss_name
        self.patience = patience
        self.best_callback = best_callback
        self.step = None
        self.done = None
        self.wait = 0
        self.defaults = {
            "experiment_key": self.experiment.id,
            "api_key": self.experiment.api_key,
            "HP_samples": float("nan"),
            "AP_no_parameters": float("nan"),
            "HP_epochs": float("nan"),
            "HP_learning_rate": float("nan"),
            "HP_batch_size": float("nan"),
            "HP_curr_step": float("nan"),
        }

        if advanced_config is not None:
            self.set_defaults(**advanced_config)

        self.losses = []  # type: List[float]
        self.threshold = threshold
        if not 0.0 < self.threshold <= 1.0:
            raise ValueError("Threshold must be set between 0.0 and 1.0")

        if not self.patience > 0:
            raise ValueError("Patience must to be set to greater than 0")

        # The minimum number of data points from a loss curve
        # required to make a prediction
        self.min_samples = 10

        self.n_init_experiments = n_init_experiments
        self.start_step = start_step

        # The timestamp of the last call to the predictor server
        self.last_prediction_timestamp = 0.0

        self.stop_step = None
        self.stop_val = None
        self.stop_min = None

        self.time_interval = time_interval
        self.predictor_url = sanitize_url(self.config["comet.predictor_url"])

        self.predictor_ping_url = url_join(self.predictor_url, "isAlive/ping")
        self.predictor_predict_url = url_join(
            self.predictor_url, "lc_predictor/predict/"
        )
        self._low_level_http_client = LowLevelHTTPClient(
            self.predictor_url,
            self.config["comet.timeout.predictor"],
            verify_tls=self.config.get_bool(
                None, "comet.internal.check_tls_certificate"
            ),
        )

        try:
            status = self.status()
            self.experiment.log_other("predictor_id", status["model_id"])
        except Exception:
            LOGGER.error(
                "Failed to contact Predictor at %s; ignoring" % self.predictor_url,
                exc_info=True,
            )

        self.experiment.log_other("predictor_loss_name", self.loss_name)

        self.MAX_TRIES = 5  # TODO: how many get_optimizer_best() retries are needed

        self.latest_prediction = {
            "min": None,
            "mean": None,
            "max": None,
            "probability_of_improvement": None,
        }

        self._allowed_modes = [None, "global", "local"]
        if mode not in self._allowed_modes:
            msg = "{} mode not supported. Please set mode to global, local or None"
            raise ValueError(msg.format(mode))

        if mode is None:
            self._set_mode(optimizer_id)
        elif mode == "global":
            self._setup_global_mode(optimizer_id)
        elif mode == "local":
            LOGGER.warning("Predictor Local Mode is still experimental.")
            self.mode = "local"

        # We need an API client in global mode
        if self.mode == "global":
            self.api = api if api else get_optimizer_api_client(self.experiment.api_key)

    def _set_mode(self, optimizer_id=None):
        """Try to use the global mode but fallback on the local mode if not optimizer_id could be found. Show a WARNING in that case."""
        try:
            self._setup_global_mode(optimizer_id)

        except ValueError:
            LOGGER.warning(
                "A valid optimizer_id has not been set. Comet Predictor will default to Local Mode"
            )
            LOGGER.warning("Comet Predictor Local Mode is still experimental.")
            self.mode = "local"
        else:
            assert self.mode == "global"

    def _setup_global_mode(self, optimizer_id=None):
        if optimizer_id is None:
            if self.experiment.optimizer is None:
                raise ValueError(
                    "Please set an optimizer_id, or use the Comet Predictor with the "
                    "Comet Optimizer in order to use Global Mode"
                )
            else:
                self.optimizer_id = self.experiment.optimizer["optimizer"].id
                LOGGER.info(
                    "Using optimizer_id %r found on experiment with Global mode",
                    self.optimizer_id,
                )

        else:
            self.optimizer_id = optimizer_id
            self.experiment.log_other("optimizer_id", self.optimizer_id)
            LOGGER.info(
                "Using optimizer_id %r explicitly given with Global mode",
                self.optimizer_id,
            )

        self.mode = "global"

    def reset(self):
        """
        Please email lcp-beta@comet.ml for comments or questions.
        """
        self.step = -1
        self.wait = 0
        self.losses = []

    def set_defaults(self, **defaults):
        """
        Please email lcp-beta@comet.ml for comments or questions.
        """
        self.defaults.update(defaults)

    def status(self):
        # type: () -> Dict[str, Any]
        """
        Please email lcp-beta@comet.ml for comments or questions.
        """
        response = self._low_level_http_client.get(self.predictor_ping_url, retry=False)
        response.raise_for_status()
        response_data = response.json()  # type: Dict[str, Any]
        return response_data

    def report_loss(self, loss, step=None):
        """
        Please email lcp-beta@comet.ml for comments or questions.
        """
        try:
            try:
                loss = float(loss)
            except Exception:
                LOGGER.error(
                    "Predictor.report_loss() requires a single number; ignoring %r",
                    loss,
                )
                return

            self.step = step if step is not None else self.experiment.curr_step
            self.losses.append(loss)
            self.experiment.log_metric("predictor_tracked_loss", loss, step=self.step)

        except Exception:
            LOGGER.error("Error reporting loss", exc_info=True)

    def _elapsed_time(self):
        return time.time() - self.last_prediction_timestamp

    def _set_and_log_stopping_metrics(self):
        self.stop_step = self.step
        self.stop_val = self.losses[-1]
        self.stop_min = min(self.losses)

        self.experiment.log_other("predictor_stop_step", self.stop_step)
        self.experiment.log_metric("predictor_wait", self.wait)
        msg = (
            "Predicted probability of improvement failed"
            " to exceed threshold {} for {} evaluations".format(
                self.threshold, self.patience
            )
        )
        self.stop_reason = msg
        self.experiment.log_other("predictor_stop_reason", msg)

    def _local_stop_early(self, **data):
        # type: (Any) -> bool
        current_loss = self.losses[-1]
        lowest_min = min(self.losses[:-1])

        current_best = min(lowest_min, current_loss)

        if self.step is None:
            step = float("nan")
        else:
            step = self.step

        data.update({"best_metric": current_best, "HP_curr_step": step})
        lmup = self.get_prediction(data)

        if lmup is None:
            return False

        (lower, mean, upper, p_improvement) = lmup
        self.experiment.log_metrics(
            {
                "predictor_mean": mean,
                "predictor_upper": upper,
                "predictor_lower": lower,
                "predictor_p_improvement": p_improvement,
                "predictor_threshold": self.threshold,
                "predictor_patience": self.patience,
            },
            step=self.step,
        )

        if p_improvement <= self.threshold:
            self.wait += 1

        # If the loss is improving, reset the wait count
        if current_loss < lowest_min:
            self.wait = 0

        # If patience is exceeded, stop training
        if self.wait >= self.patience:
            if self.stop_step is None:
                self._set_and_log_stopping_metrics()
            if self.best_callback:
                try:
                    self.best_callback(self, current_best)
                except Exception:
                    LOGGER.error(
                        "Error calling best callback with best value: %r",
                        current_best,
                        exc_info=True,
                    )

            return True

        return False

    def _global_stop_early(self, **data):
        # type: (Any) -> bool
        state = self._get_trial_state(data)

        if state is None:
            return False

        experiment_count = state.get("experiment_count")
        best_metric_experiment_key = state.get("best_metric_experiment_key")
        best_metric = state.get("best_metric")

        lower = state.get("lower")
        mean = state.get("mean")
        upper = state.get("upper")

        p_improvement = state.get("prob_improvement")
        self.experiment.log_metrics(
            {
                "predictor_mean": mean,
                "predictor_upper": upper,
                "predictor_lower": lower,
                "predictor_p_improvement": p_improvement,
                "predictor_threshold": self.threshold,
                "predictor_patience": self.patience,
            },
            step=self.step,
        )

        # If the current experiment has the best metric
        # Do not stop
        if best_metric_experiment_key == self.experiment.id:
            return False

        if experiment_count > self.n_init_experiments:
            if p_improvement <= self.threshold:
                self.wait += 1

        if self.wait >= self.patience:
            if self.stop_step is None:
                self._set_and_log_stopping_metrics()
            if self.best_callback:
                try:
                    self.best_callback(self, best_metric)
                except Exception:
                    LOGGER.error(
                        "Error calling best callback with best value: %r",
                        best_metric,
                        exc_info=True,
                    )

            return True

        return False

    def _get_trial_metrics(self):
        # type: () -> Optional[Tuple[Optional[int], Optional[str], Optional[float]]]
        count = 0
        while count <= self.MAX_TRIES:
            try:
                LOGGER.debug("Calling get_optimizer_best()...")
                response_data = self.api.get_optimizer_best(
                    self.experiment.id, self.optimizer_id, self.loss_name, maximum=False
                )
            except Exception as exc:
                if count == self.MAX_TRIES:
                    LOGGER.error(
                        "Max retries exceeded while trying to fetch "
                        "experiments with current optimizer id",
                        exc_info=True,
                    )
                    return None

                sdk_error_code = None
                if isinstance(exc, CometRestApiException) and exc.safe_json_response:
                    sdk_error_code = exc.safe_json_response.get("sdk_error_code", 0)

                if sdk_error_code != INVALID_OPTIMIZATION_ID:
                    LOGGER.debug(
                        "Error while getting the optimizer best %s", exc, exc_info=True
                    )

                count += 1
                time.sleep(1)
                continue
            break

        experiment_count = response_data.get("experimentCount")
        experiment_key = response_data.get("experimentKey")
        best_metric = response_data.get("metricValue")

        return experiment_count, experiment_key, best_metric

    def _get_trial_state(self, data):
        # type: (Dict[str, Any]) -> Optional[Dict[str, Union[str, float]]]
        """
        Internal method only used in global mode to retrieve best metric
        in an optimizer run
        :param data:
        :return:
        """
        trial_metrics = self._get_trial_metrics()

        if trial_metrics is None:
            return None

        experiment_count, experiment_key, best_metric = trial_metrics
        if (experiment_count is None) or (best_metric is None):
            return None

        data.update({"best_metric": best_metric, "HP_curr_step": self.step})
        lmup = self.get_prediction(data)

        if lmup is None:
            return None

        lower, mean, upper, p_improvement = lmup
        return {
            "lower": lower,
            "mean": mean,
            "upper": upper,
            "prob_improvement": p_improvement,
            "experiment_count": experiment_count,
            "best_metric_experiment_key": experiment_key,
            "best_metric": best_metric,
        }

    def stop_early(self, **data):
        # type: (Any) -> bool
        """
        Please email lcp-beta@comet.ml for comments or questions.
        """
        # These checks should be performed in the order. Changing the order will
        # produce unwanted behaviour

        try:
            # Check for cases where model is not stopped after stop_early returns True
            if self.wait >= self.patience:
                LOGGER.debug(
                    "Patience Exceeded: %s >= %s; stopping", self.wait, self.patience
                )
                return True

            # If the step has not been set yet or the Experiment curr_step is None
            if self.step is None:
                LOGGER.debug("We don't have a step; not stopping")
                return False

            # Check if we have passed the start_step
            if self.step < self.start_step:
                LOGGER.debug(
                    "Step %r < configured started step %r; not stopping",
                    self.step,
                    self.start_step,
                )
                return False

            #  Check if we have the min number of samples necessary to make a prediction
            if len(self.losses) < self.min_samples:
                LOGGER.debug(
                    "Number of epochs %r < configured min_samples %r; not stopping",
                    len(self.losses),
                    self.min_samples,
                )
                return False

            # Check if enough time has passed between predictor evaluations
            if self._elapsed_time() < self.time_interval:
                LOGGER.debug(
                    "Elapsed time since last call %r < configured time interval %r; not stopping",
                    self._elapsed_time,
                    self.time_interval,
                )
                return False

            if self.mode == "global":
                return self._global_stop_early(**data)
            else:
                return self._local_stop_early(**data)

        except Exception:
            LOGGER.error(
                "Error calling Predictor.stop_early, not stopping", exc_info=True
            )
            return False

    def get_prediction(self, request_data):
        # type: (Dict[str, Any]) -> Optional[Tuple[float, float, float, float]]
        """
        Please email lcp-beta@comet.ml for comments or questions.
        """

        # Copy default fields
        prediction_data = self.defaults.copy()
        prediction_data["TS"] = self.losses

        # Update fields
        prediction_data.update(request_data)
        prediction_request = {"data": prediction_data}

        LOGGER.debug(
            "Get prediction on url %r with data %r",
            self.predictor_predict_url,
            prediction_request,
        )

        response = self._low_level_http_client.post(
            self.predictor_predict_url, payload=prediction_request, retry=False
        )

        if response.status_code == 200:
            # Update timestamp to latest successful call to predictor server
            self.last_prediction_timestamp = time.time()

            response_data = response.json().get("response")
            self._set_prediction(response_data)
            return (
                response_data["min"],
                response_data["mean"],
                response_data["max"],
                response_data["probability_of_improvement"],
            )

        elif response.status_code == 201:
            return None
        else:
            raise Exception(
                "Failed Predictor request for {}: {}".format(
                    prediction_request, response
                )
            )

    def _set_prediction(self, prediction):
        self.latest_prediction.update(prediction)

    def get_notification_message(self):
        msg = {
            "stop-min": self.stop_min,
            "stop-val": self.stop_val,
            "stop-step": self.stop_step if self.stop_step else self.step,
            "predicted-min": self.latest_prediction.get("mean"),
            "predicted-min-lower_bound": self.latest_prediction.get("min"),
            "predicted-min-upper_bound": self.latest_prediction.get("max"),
        }

        if self.mode == "global":
            trial_metrics = self._get_trial_metrics()

            if trial_metrics is not None:
                _, _, best_metric = trial_metrics
                msg["best-sweep-value"] = best_metric

            return msg

        return msg
