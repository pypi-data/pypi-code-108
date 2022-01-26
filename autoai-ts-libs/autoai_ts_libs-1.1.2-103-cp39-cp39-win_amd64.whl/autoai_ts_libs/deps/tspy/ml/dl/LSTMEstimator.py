from sklearn.base import BaseEstimator
import numpy as np
from autoai_ts_libs.deps.tspy.ml import feature_vectors
from autoai_ts_libs.deps.tspy.ml.dl.config import Config
from autoai_ts_libs.deps.tspy.ml.dl.lstm_forecasting import LSTMForecasting
import autoai_ts_libs.deps.tspy


class LSTMEstimator(BaseEstimator):

    def __init__(self, num_features, sampling_rate, interpolator, seq_len, config):
        self.sampling_rate = sampling_rate
        self.interpolator = interpolator
        self.seq_len = seq_len
        self.config = config
        self.model = None
        self.num_feats = num_features

    def fit(self, ts):
        pred_len = 1
        ts_resampled = ts.resample(self.sampling_rate, self.interpolator)
        feats = feature_vectors.prepare_predictions(data_time_series=ts_resampled,
                                                    left_delta=self.sampling_rate * (self.seq_len - 1),
                                                    right_delta=self.sampling_rate,
                                                    label_range=(
                                                        self.sampling_rate * (self.seq_len - pred_len) + 1,
                                                        self.sampling_rate * self.seq_len),
                                                    feature_range=(0, self.sampling_rate * (self.seq_len - 1)))

        features = np.asarray([f[2] for f in feats if len(f[2]) == self.seq_len and len(f[1]) == pred_len]).astype(
            np.float32).reshape(-1, self.seq_len, self.num_feats)
        labels = np.asarray([f[1] for f in feats if len(f[1]) == pred_len and len(f[2]) == self.seq_len]).astype(
            np.float32).reshape(
            -1, pred_len, self.num_feats)

        forecaster = LSTMForecasting(self.config)
        forecaster.train(features, labels, batch_size=100, epochs=5, shuffle=True)
        self.model = forecaster

    def predict(self, ts, num_predictions):
        pred_len = 1
        ts_resampled = ts.resample(self.sampling_rate, self.interpolator)
        feats = feature_vectors.prepare_predictions(data_time_series=ts_resampled,
                                                    left_delta=self.sampling_rate * (self.seq_len - 1),
                                                    right_delta=self.sampling_rate,
                                                    label_range=(
                                                        self.sampling_rate * (self.seq_len - pred_len) + 1,
                                                        self.sampling_rate * self.seq_len),
                                                    feature_range=(0, self.sampling_rate * (self.seq_len - 1)))
        features = np.asarray([f[2] for f in feats if len(f[2]) == self.seq_len and len(f[1]) == pred_len]).astype(
            np.float32).reshape(-1, self.seq_len, self.num_feats)

        prediction_tt = ts.materialize().last().time_tick + self.sampling_rate
        last_feature = features[len(features) - 1, :, :].reshape(-1, self.seq_len, self.num_feats)
        predictions = self.model.predict(last_feature)
        ts_builder = autoai_ts_libs.deps.tspy.builder()
        ts_builder.add((prediction_tt, predictions[0][len(predictions[0]) - 1].tolist()))
        for i in range(1, num_predictions):
            new_prediction = self.model.predict(np.concatenate((last_feature[:, i:, :], predictions), axis=1))
            predictions = np.append(predictions, new_prediction, axis=1)
            prediction_tt = prediction_tt + self.sampling_rate
            ts_builder.add((prediction_tt, predictions[0][len(predictions[0]) - 1].tolist()))

        return ts_builder.result()
