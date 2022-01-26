from sklearn.preprocessing import StandardScaler

from autoai_ts_libs.deps.tspy.data_structures.ml.data_preparation import FeatureVectors
import json
import numpy as np
import tensorflow as tf
from tensorflow_core.python import keras
import tensorflow.keras.layers as layers
from autoai_ts_libs.deps.tspy.ml.dl.attention import LSTMAttention, BiLSTMAttention
from autoai_ts_libs.deps.tspy.ml.dl.config import Config


class MTSAttention:
    """
    - get attention for each timestep for each of the individual univariate timeseries
    - get attention for each timestep for all the multivariate timeseries
    - get attention for each feature across all timesteps
    """

    def __init__(self, mts, num_timesteps, mts_sampling_rate, config=None):
        """

        :param mts: a autoai_ts_libs.deps.tspy mts (multi-timeseries). Each timeseries will later be considered as contributing one feature
        for training a LSTM Prediction/Attention model
        :param num_timesteps: the number of history timesteps to consider when creating feature vectors for prediction
        :param mts_sampling_rate: The time granularity at which the input mts are sampled
        :param config: model architecture configuration
        """
        self.mts = mts
        self.timesteps = num_timesteps
        self.sampling_rate = mts_sampling_rate
        self.prepared_features = FeatureVectors.prepare_predictions(data_time_series=mts,
                                                                    left_delta=self.sampling_rate * (
                                                                            self.timesteps - 1),
                                                                    right_delta=self.sampling_rate,
                                                                    label_range=(
                                                                        self.sampling_rate * (self.timesteps - 1) + 1,
                                                                        self.sampling_rate * self.timesteps),
                                                                    feature_range=(
                                                                        0, self.sampling_rate * (self.timesteps - 1)))
        if config is not None:
            self.config = config
        else:
            # use a default architecture
            self.config = MTSAttention.__get_default_config__()

    def get_univariate_attention(self, batch_size=None, epochs=None):
        """

        :return: list of attentions for each of the values in the input timeseries
        """
        attentions = []
        keys = self.mts.keys
        for key in keys:
            feat = np.asarray(
                [f[2] for f in self.prepared_features if
                 f[0] == key and len(f[2]) == self.timesteps and len(f[1]) == 1]).astype(
                np.float32)
            label = np.asarray([f[1] for f in self.prepared_features if
                                f[0] == key and len(f[1]) == 1 and len(f[2]) == self.timesteps]).astype(np.float32)
            if batch_size is None:
                batch_size = int(feat.shape[0] / 10)
            if epochs is None:
                epochs = 5
            # scale the data
            scaler = StandardScaler()
            x = scaler.fit_transform(feat.reshape(-1, 1)).reshape(-1, self.timesteps, 1)
            y = scaler.transform(label.reshape(-1, 1)).reshape(-1, 1, 1)
            input = keras.Input(shape=(self.timesteps, 1))
            out = MTSAttention.__build_model_layers__(self.config, input, 1, 1)
            model = keras.Model(input, out)
            model.compile(optimizer="adam", loss="mse")
            model.fit(x, y, batch_size=batch_size, epochs=epochs, shuffle=True)
            attentions.append(self.get_attention_map(model, x))
        return attentions

    def get_mts_temporal_attention(self, batch_size=None, epochs=None):
        """

        :return:
        """
        num_features = len(self.mts.keys)

        features, labels = self.__flatten_mts__()
        features = features.reshape(-1, self.timesteps, num_features)
        labels = labels.reshape(-1, 1, num_features)

        if batch_size is None:
            batch_size = int(features.shape[0] / 10)
        if epochs is None:
            epochs = 5

        scaler = StandardScaler()
        x = scaler.fit_transform(features.reshape(-1, num_features)).reshape(-1, self.timesteps, num_features)
        y = scaler.transform(labels.reshape(-1, num_features)).reshape(-1, 1, num_features)

        input = keras.Input(shape=(self.timesteps, num_features))
        out = MTSAttention.__build_model_layers__(self.config, input, 1, num_features)
        model = keras.Model(input, out)
        model.compile(optimizer="adam", loss="mse")
        model.fit(x, y, batch_size=batch_size, epochs=epochs, shuffle=True)

        return self.get_attention_map(model, x)

    def get_mts_spatial_attention(self, batch_size=None, epochs=None):
        """

        :return:
        """
        num_features = len(self.mts.keys)

        features, labels = self.__flatten_mts__()
        features = features.reshape(-1, self.timesteps, num_features)
        labels = labels.reshape(-1, 1, num_features)

        if batch_size is None:
            batch_size = int(features.shape[0] / 10)
        if epochs is None:
            epochs = 5

        scaler = StandardScaler()
        x = scaler.fit_transform(features.reshape(-1, num_features)).reshape(-1, self.timesteps, num_features)
        x = np.transpose(x, (0, 2, 1))
        y = scaler.transform(labels.reshape(-1, num_features)).reshape(-1, 1, num_features)

        input = keras.Input(shape=(num_features, self.timesteps))
        out = MTSAttention.__build_model_layers__(self.config, input, 1, num_features)
        model = keras.Model(input, out)
        model.compile(optimizer="adam", loss="mse")
        model.fit(x, y, batch_size=batch_size, epochs=epochs, shuffle=True)

        return self.get_attention_map(model, x)

    @staticmethod
    def __build_model_layers__(config, input, pred_len, num_features):
        x = input
        for layer_n in range(len(config.layers)):
            x = MTSAttention.__get_layer__(config.layers[layer_n])(x)
        # if 'attention_units' is specified, use Attention else use BiLSTMAttention
        if 'attention_units' in config.configs:
            x, attn = LSTMAttention(units=config.configs['attention_units'])(x)
        else:
            x, attn = BiLSTMAttention(return_attention=True)(x)
        x = layers.Dropout(0.5)(x)
        dense = layers.Dense(units=pred_len * num_features, activation="linear")(x)
        out = layers.Reshape((pred_len, num_features))(dense)
        return out

    @staticmethod
    def __get_layer__(layer):
        if layer.type == 'LSTM':
            return layers.LSTM(layer.units, return_sequences=True)
        if layer.type == 'BidirectionalLSTM':
            return layers.Bidirectional(layers.LSTM(layer.units, return_sequences=True))

    @staticmethod
    def __get_default_config__():
        json_str = """
        {
          "layers": [
            {
              "type": "LSTM",
              "units": 128
            },
            {
              "type": "LSTM",
              "units": 240
            },
            {
              "type": "LSTM",
              "units": 128
            }
          ],
          "attention_units": 20,
          "prediction_type": "attention"
        }
        """
        config = Config()
        config.from_json_dict(json.loads(json_str))
        return config

    def __flatten_mts__(self):
        feats_by_key = {}
        for f in self.prepared_features:
            if f[0] not in feats_by_key:
                feats_by_key[f[0]] = []
            feats_by_key[f[0]].append((f[1], f[2]))

        all_f = []
        all_l = []
        for k in feats_by_key:
            feats = feats_by_key[k]
            f = np.asarray([f[1] for f in feats if len(f[1]) == self.timesteps and len(f[0]) == 1]).astype(np.float32)
            all_f.append(f)
            l = np.asarray([f[0] for f in feats if len(f[0]) == 1 and len(f[1]) == self.timesteps]).astype(np.float32)
            all_l.append(l)
        return np.array(all_f), np.array(all_l)

    def get_attention_map(self, model, input):
        # modify this if architecture is changes.
        # For example, if we remove the last dropout, should change slice to [0:-1]
        att_model_output = model.layers[0:-3]
        att_model = keras.Model(att_model_output[0].input, att_model_output[-1].output)
        att_model.compile(optimizer=tf.keras.optimizers.Adam(),
                          loss="mse")
        return att_model.predict(input)[1]
