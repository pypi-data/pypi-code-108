"""
    monasca-predictor main loop
"""

import copy
import logging
import signal
import sys
import time
from datetime import timedelta, datetime

import pandas as pd

import monasca_agent.common.metrics as metrics
from monasca_agent.common.emitter import http_emitter

import monasca_predictor.common.util as util
import monasca_predictor.inference.model as inf_mod
from monasca_predictor.api.monasca_api import MonascaAPI
from monasca_predictor.common.config import PredictorConfig


log = logging.getLogger(__name__)
prediction_config_list = []


class PredictorProcess:
    def __init__(self):
        self._api_endpoint = None
        self._forwarder_endpoint = None
        self.run_forever = True

    def _handle_sigterm(self, signum, frame):
        log.debug("Caught SIGTERM")
        self.stop(0)

    def stop(self, exit_code):
        log.info("Stopping predictor run loop...")
        self.run_forever = False
        sys.exit(exit_code)

    def run(self, config):
        # Gracefully exit on sigterm.
        signal.signal(signal.SIGTERM, self._handle_sigterm)

        # Handle Keyboard Interrupt
        signal.signal(signal.SIGINT, self._handle_sigterm)

        if not self._api_endpoint:
            self._api_endpoint = MonascaAPI(config)

        inference_frequency = config.get("inference_frequency_seconds")

        # NOTE: take start time here so that absolute timing can be used and
        # cumulative delays mitigated.
        inference_start = time.time()

        while self.run_forever:
            now = datetime.utcfromtimestamp(inference_start)

            for prediction_id, prediction_config in enumerate(prediction_config_list):
                total_overhead_start = time.time()
                in_metric_list = prediction_config.get("metrics")

                if not in_metric_list:
                    log.info(
                        "No input metrics specified for prediction %d, skipping...",
                        prediction_id,
                    )
                    continue

                # Get config parameters
                tenant_id = prediction_config.get("tenant_id")
                instance_id = prediction_config.get("instance_id")
                dimensions = prediction_config.get("dimensions")

                lookback_period_seconds = prediction_config.get(
                    "lookback_period_seconds"
                )
                prediction_offset_seconds = prediction_config.get(
                    "prediction_offset_seconds"
                )

                time_aggregation_statistics = prediction_config.get(
                    "time_aggregation_statistics"
                )
                time_aggregation_period_seconds = prediction_config.get(
                    "time_aggregation_period_seconds"
                )
                space_aggregation_statistics = prediction_config.get(
                    "space_aggregation_statistics"
                )

                group_by = prediction_config.get("group_by")
                merge_metrics = prediction_config.get("merge_metrics")

                out_metric_name = prediction_config.get("out_metric")

                start_time = util.format_datetime_str(
                    now - timedelta(seconds=lookback_period_seconds)
                )
                expected_input_shape = (
                    lookback_period_seconds // time_aggregation_period_seconds
                )

                # Fetch measurements (by metric) from Monasca API.
                metrics_df = pd.DataFrame()
                for metric in in_metric_list:
                    log.info(
                        "Getting '%s' measurements for prediction %d...",
                        metric,
                        prediction_id,
                    )

                    get_measurement_resp = self._api_endpoint.get_measurements(
                        metric=metric,
                        start_time=start_time,
                        instance_id=instance_id,
                        tenant=tenant_id,
                        dimensions=dimensions,
                        group_by=group_by,
                        merge_metrics=merge_metrics,
                        statistics=time_aggregation_statistics,
                        aggregation_period_seconds=time_aggregation_period_seconds,
                    )

                    log.debug(
                        "Received the following response:\n%s",
                        util.format_object_str(get_measurement_resp),
                    )

                    for instance in get_measurement_resp:
                        instance_id = instance["dimensions"]["resource_id"]
                        instance_data = copy.deepcopy(instance["dimensions"])

                        if time_aggregation_statistics:
                            measurement_list = instance["statistics"]
                        else:
                            measurement_list = instance["measurements"]

                        # NOTE: value list must be checked such that it matches the
                        # expected input shape of the model. It could be the case that
                        # the retrieved metrics are too few (because the collection has
                        # just started and the lookback period is too long) or too
                        # much (because of the effect of cumulative delays in the
                        # collection process).
                        if not measurement_list:
                            log.info(
                                "No measurements were retrieved for instance '%s'. "
                                "Skipping...",
                                instance_id,
                            )
                            continue

                        elif len(measurement_list) > expected_input_shape:
                            log.info(
                                "Retrieved measurements for instance '%s' are more than expected"
                                "(expected: %d, actual: %d). Retaining newest only...",
                                instance_id,
                                expected_input_shape,
                                len(measurement_list),
                            )

                            measurement_list = measurement_list[-expected_input_shape:]

                        elif len(measurement_list) < expected_input_shape:
                            # NOTE: In case of spatially-aggregated
                            # predictions, retain measurements even though they
                            # are not as much as expected. This is to avoid
                            # feeding the predictor with inconsistent data.
                            # E.g., the count metric would not take into
                            # account the nodes that failed to match the
                            # expected shape; the predictor would infer the
                            # target metric based on incomplete info; the
                            # rescaling would be done on fewer nodes than those
                            # that are actually running.
                            log.info(
                                "Retrieved measurements for instance '%s' are fewer than expected"
                                "(expected: %d, actual: %d).",
                                instance_id,
                                expected_input_shape,
                                len(measurement_list),
                            )

                            if not space_aggregation_statistics:
                                log.info(
                                    "Instance '%s' will not be considered for "
                                    "prediction in this round.",
                                    instance_id,
                                )
                                continue

                        log.debug(
                            "Value list for metric '%s' of instance '%s' is:\n%s",
                            metric,
                            instance_id,
                            measurement_list,
                        )

                        for measurement in measurement_list:
                            instance_data["timestamp"] = measurement[0]
                            instance_data[metric] = measurement[1]
                            metrics_df = metrics_df.append(
                                instance_data, ignore_index=True
                            )

                processing_overhead_start = time.time()
                if metrics_df.empty:
                    log.debug("Not enough data available, skipping...")
                    continue

                # cast index to DateTimeIndex
                metrics_df.set_index(["timestamp"], inplace=True)
                metrics_df.index = pd.to_datetime(
                    metrics_df.index, format=util.DEFAULT_TIMESTAMP_FORMAT
                )

                log.debug(
                    "Retrieved following data from Monasca API:\n%s",
                    str(metrics_df),
                )

                # Feed predictor with retrieved measurements
                model_type = prediction_config.get("model_type")
                prediction_steps = (
                    prediction_offset_seconds // time_aggregation_period_seconds
                )
                if model_type and model_type == "linear":
                    model = inf_mod.LinearModel()
                else:
                    model = inf_mod.Model()
                    model.load(
                        model_dump=prediction_config.get("model_path"),
                        scaler_dump=prediction_config.get("scaler_path"),
                    )

                # NOTE: associate predictor output with last input measurement
                # timestamp. Having a temporal relation between the two is
                # useful for plotting and time-series analysis in general. The
                # (future) timestamp that the prediction refer to will be
                # included in the dimensions.
                #
                # Consider that, if the *inference* frequency is lower than the
                # *collection* frequency (30 secs, by default), some predictor
                # outputs will be overridden, as the last input measurement
                # timestamp (actually, the whole input) will be the same for
                # multiple consecutive inference runs. However, setting an
                # inference frequency that low makes sense only for debugging.
                if space_aggregation_statistics:
                    # TODO: handle measurements coming from multiple input metrics.
                    # Currently assuming only one input metric is specified.
                    table = pd.pivot_table(
                        metrics_df,
                        values=in_metric_list[0],
                        index=["timestamp"],
                        columns=["hostname"],
                    )
                    raw_data_cols = list(table.columns)

                    log.debug("raw_data_cols: %s", str(raw_data_cols))
                    log.debug("pivot table:\n%s", str(table))

                    if table.shape[0] > expected_input_shape:
                        # NOTE: assuming that, if the table contains more rows
                        # than the expected number of input samples, there is a
                        # time-shift among the individual traces of the involved
                        # nodes. In that case, fill NaNs with the value of the
                        # previous sample and retain the expected number of
                        # (newest) samples only.
                        log.debug("The pivot table has more rows than expected.")

                        table = table.fillna(method="ffill", axis=0).iloc[
                            -expected_input_shape:, :
                        ]
                    elif table.shape[0] < expected_input_shape:
                        # NOTE: if the table contains less rows than expected,
                        # then replicate the oldest measure to cover the
                        # difference.
                        log.debug("The pivot table has fewer rows than expected.")

                        difference = expected_input_shape - table.shape[0]
                        new_row = table.iloc[0].copy()
                        new_row.name = pd.to_datetime(new_row.name) - timedelta(
                            minutes=1
                        )
                        table = pd.concat(
                            [pd.DataFrame(new_row).transpose()] * difference + [table]
                        )
                    else:
                        # NOTE: even though the table has the expected shape,
                        # there could be the case that some columns exhibit
                        # NaNs. This is caused either by some computing
                        # instances being turned off at some point during the
                        # time period, or by possible delays in Monasca
                        # measurements persistence. In the latter case, we
                        # assume the existence of a single NaN occurring at the
                        # end of the sequence that, if left as is, would throw
                        # off the calculations of the spatially-aggregated
                        # values and possible post-processing steps that rely
                        # on the last known size of the cluster. To overcome
                        # this issue, we fill 1-sample gaps in the sequences,
                        # using the value of the previous sample.
                        log.debug("The pivot table has the expected number of rows.")

                        table.fillna(method="ffill", axis=0, limit=1, inplace=True)

                    # compute spatial statistics
                    table["count"] = table[raw_data_cols].count(axis=1)
                    for stat in space_aggregation_statistics:
                        if stat == "avg":
                            table["avg"] = (
                                table[raw_data_cols].sum(axis=1) / table["count"]
                            )
                        elif stat == "sum":
                            table["sum"] = table[raw_data_cols].sum(axis=1)

                    log.debug("augmented pivot table:\n%s", str(table))

                    predictor_input = table[space_aggregation_statistics].values

                    log.debug("predictor input:\n%s", str(predictor_input))

                    prediction_value_raw = model.predict(
                        predictor_input, prediction_steps
                    )
                    node_count = table["count"][-1]
                    prediction_value = prediction_value_raw / node_count

                    log.debug("prediction_value_raw: %s", str(prediction_value_raw))
                    log.debug("node_count: %s", str(node_count))
                    log.debug("prediction_value: %s", str(prediction_value))

                    last_datetime = table.index[-1]
                    prediction_timestamp = last_datetime.timestamp()

                    log.debug("Last input measurement datetime: %s", last_datetime)
                    log.debug("Predictor output timestamp: %f", prediction_timestamp)

                    # Build predictor output dimensions
                    prediction_dimensions = copy.deepcopy(dimensions)
                    prediction_dimensions["component"] = "cluster"

                    log.debug(
                        "prediction dimensions:\n%s",
                        util.format_object_str(prediction_dimensions),
                    )

                    log.info(
                        "Sending '%s' measurement to forwarder...",
                        out_metric_name,
                    )

                    self._send_to_forwarder(
                        out_metric_name,
                        prediction_value,
                        prediction_timestamp,
                        prediction_dimensions,
                        tenant_id=tenant_id,
                        forwarder_endpoint=config["forwarder_url"],
                    )
                else:
                    for instance_id, instance_data in metrics_df.groupby("resource_id"):
                        # TODO: handle measurements coming from multiple input metrics.
                        # Currently assuming only one input metric is specified.
                        prediction_value = model.predict(
                            instance_data[in_metric_list[0]].values, prediction_steps
                        )

                        last_datetime = instance_data.index[-1]
                        prediction_timestamp = last_datetime.timestamp()

                        log.debug("Last input measurement datetime: %s", last_datetime)
                        log.debug(
                            "Predictor output timestamp: %f", prediction_timestamp
                        )

                        # Build predictor output dimensions
                        prediction_dimensions = dict(
                            instance_data[
                                instance_data.columns.difference(in_metric_list)
                            ].iloc[0, :]
                        )

                        log.debug(
                            "prediction dimensions:\n%s",
                            util.format_object_str(prediction_dimensions),
                        )

                        if not out_metric_name:
                            out_metric_name = f"pred.{in_metric_list[0]}"

                        log.info(
                            "Sending '%s' measurement for instance '%s' to forwarder...",
                            out_metric_name,
                            instance_id,
                        )

                        self._send_to_forwarder(
                            out_metric_name,
                            prediction_value,
                            prediction_timestamp,
                            prediction_dimensions,
                            tenant_id=tenant_id,
                            forwarder_endpoint=config["forwarder_url"],
                        )

                total_overhead_end = time.time()
                total_overhead_elapsed_time = total_overhead_end - total_overhead_start
                processing_overhead_elapsed_time = (
                    total_overhead_end - processing_overhead_start
                )
                log.debug("Total overhead [sec]: %s", total_overhead_elapsed_time)
                log.debug(
                    "Processing overhead [sec]: %s", processing_overhead_elapsed_time
                )

            # Only plan for the next loop if we will continue,
            # otherwise just exit quickly.
            if self.run_forever:
                inference_elapsed_time = time.time() - inference_start
                if inference_elapsed_time < inference_frequency:
                    # TODO: something like C's clock_nanosleep() should be
                    # used, instead of sleep(), to have a more precise timing
                    # and be more robust to cumulative delays
                    time.sleep(inference_frequency - inference_elapsed_time)

                    inference_start += inference_frequency
                else:
                    log.info(
                        "Inference took %f which is as long or longer then the configured "
                        "inference frequency of %d. Starting inference again without waiting "
                        "in result...",
                        inference_elapsed_time,
                        inference_frequency,
                    )
        self.stop(0)

    @staticmethod
    def _send_to_forwarder(
        metric_name, value, timestamp, dimensions, tenant_id, forwarder_endpoint
    ):
        out_metric = metrics.Metric(
            name=metric_name,
            dimensions=dimensions,
            tenant=tenant_id,
        )
        envelope = out_metric.measurement(value, timestamp)

        log.debug(
            "The following envelope will be sent to forwarder:\n%s",
            util.format_object_str(envelope),
        )

        http_emitter([envelope], log, forwarder_endpoint)


def main():
    options, args = util.get_parsed_args()
    predictor_config = PredictorConfig().get_config(["Main", "Api", "Logging"])

    log.debug(
        "monasca-predictor started with the following configs:\n%s",
        util.format_object_str(predictor_config),
    )

    global prediction_config_list
    prediction_config_list = predictor_config["predictions"]

    predictor = PredictorProcess()
    predictor.run(predictor_config)

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        try:
            log.exception("Uncaught error during monasca-predictor execution.")
        except Exception:  # pylint: disable=broad-except
            pass
        raise
