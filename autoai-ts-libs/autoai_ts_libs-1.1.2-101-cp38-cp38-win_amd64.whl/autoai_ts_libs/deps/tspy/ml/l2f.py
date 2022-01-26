from sklearn.base import BaseEstimator

import autoai_ts_libs.deps.tspy
from autoai_ts_libs.deps.tspy.functions import expressions as e
from autoai_ts_libs.deps.tspy.functions import transformers, reducers


class L2FEstimator(BaseEstimator):

    def __init__(self, estimator):
        self.estimator = estimator

    def fit(self, ts):
        features = len(ts.materialize().first().value)

        ts_dict = {}
        for i in range(0, features):
            ts_dict[i] = ts.map(e.id(key=i))

        mts = autoai_ts_libs.deps.tspy.multi_time_series(ts_dict)

        diff_mts = mts.transform(transformers.difference())

        self.__avg_diff_map = diff_mts.reduce(reducers.average())
        self.__sd_diff_map = diff_mts.reduce(reducers.standard_deviation())

        z_score_mts = diff_mts.transform(transformers.z_score())

        zscore_vector_ts = z_score_mts.aggregate_series(lambda x: x)

        self.estimator.fit(zscore_vector_ts)

    def predict(self, ts, num_predictions):
        collected = ts.materialize()
        features = len(collected.first().value)

        ts_dict = {}
        for i in range(0, features):
            ts_dict[str(i)] = ts.map(e.id(key=i))

        mts = autoai_ts_libs.deps.tspy.multi_time_series(ts_dict)

        diff_mts = mts.transform(transformers.difference())
        z_score_mts = diff_mts.transform(transformers.z_score())
        zscore_vector_ts = z_score_mts.aggregate_series(lambda x: x)

        predictions_ts = self.estimator.predict(zscore_vector_ts, num_predictions).to_time_series()

        ts_dict = {}
        for i in range(0, features):
            ts_dict[i] = predictions_ts.map(e.id(key=i))

        z_score_prediction_mts = autoai_ts_libs.deps.tspy.multi_time_series(ts_dict)

        def reverse_z_score(key, series):
            return series.to_time_series().map(
                lambda d: d * self.__sd_diff_map[key] + self.__avg_diff_map[key]).materialize()

        def reverse_diff(key, series):
            agg_sum = collected.last().value[key]
            ts_builder = autoai_ts_libs.deps.tspy.builder()
            for o in series:
                agg_sum = agg_sum + o.value
                ts_builder.add((o.time_tick, agg_sum))
            return ts_builder.result()

        raw_predictions = z_score_prediction_mts \
            .map_series_with_key(reverse_z_score) \
            .map_series_with_key(reverse_diff)

        return raw_predictions.aggregate_series(lambda l: l).materialize()
