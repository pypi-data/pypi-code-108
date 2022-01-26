import tensorflow as tf
import tensorflow.keras.layers as layers
import tensorflow.keras.models as models


class LSTMForecasting:
    def __init__(self, config):
        """

        :param config: Object of type Config that specifies the structure for the model that needs to be built
        """
        self.model = self.__build_model__(config)

    @staticmethod
    def __build_model__(config):
        model = tf.keras.Sequential()
        for layer_n in range(len(config.layers) - 1):
            model.add(LSTMForecasting.__get_layer__(config.layers[layer_n]))
        model.add(LSTMForecasting.__get_layer__(config.layers[len(config.layers) - 1], last=True))
        if config.prediction_type == 'ad':
            model.add(layers.Dense(2, activation='sigmoid'))
            model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
        elif config.prediction_type == "classification":
            model.add(layers.Dense(config.num_classes, activation='softmax'))
            model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
        elif config.prediction_type == 'value':
            model.add(layers.Dense(config.num_features * config.prediction_length, activation='linear'))
            model.add(layers.Reshape((config.prediction_length, config.num_features)))
            model.compile(optimizer="adam", loss="mse")
        elif config.prediction_type == 'distribution':
            model.add(layers.Dense(config.num_features * config.distribution_buckets * config.prediction_length))
            model.add(layers.Reshape((config.prediction_length, config.num_features, config.distribution_buckets)))
            model.add(layers.Activation('softmax'))
            model.compile(optimizer="adam", loss='categorical_crossentropy')
        else:
            raise ValueError('Please specify a valid prediction type (one of : {ad, value, distribution}')
        return model

    def train(self, x, y, batch_size, epochs, shuffle=True):
        """
        Train the model as specified by the configuration
        :param x: normalized (0 mean, unit variance) input feature vectors
        :param y: normalized (0 mean, unit variance) label vectors. The dimensions will depend on the task being
        trained for (see Config.prediction_type)
        :param batch_size: batch size to use for training
        :param epochs: number of epochs to train for
        :param shuffle: boolean indicating whether or not to shuffle the data
        :return:
        """
        self.model.fit(x, y, batch_size, epochs, shuffle)

    def predict(self, x):
        """
        Predict the output given input features using the trained model
        :param x: normalized (0 mean, unit variance) input feature vectors
        :return: the predicted value given the input features. The dimensions will depend on the task being
        trained for (see Config.prediction_type)
        """
        pred = self.model.predict(x)
        return pred

    def eval(self, x, y, batch_size):
        """
        Evaluate the model
        :param x: normalized (0 mean, unit variance) input feature vectors
        :param y: normalized (0 mean, unit variance) label vectors. The dimensions will depend on the task being
        trained for (see Config.prediction_type)
        :param batch_size: batch size to use for evaluation
        :return:
        """
        return self.model.evaluate(x, y, batch_size)

    def save(self, path):
        """
        Save the model to the path provided
        :param path: path to save the model
        :return:
        """
        self.model.save(path)

    @staticmethod
    def load(path):
        """

        :param path: load the model from the provided path
        :return:
        """
        models.load_model(path)

    def get_model(self):
        return self.model

    @staticmethod
    def __get_layer__(layer, last=False):
        dropout = 0.0
        rec_dropout = 0.0
        if layer.dropout is not None:
            dropout = layer.dropout
        if layer.recurrent_dropout is not None:
            rec_dropout = layer.recurrent_dropout
        if layer.type == 'LSTM':
            if last:
                return layers.LSTM(layer.units, dropout=dropout, recurrent_dropout=rec_dropout)
            return layers.LSTM(layer.units, return_sequences=True, dropout=dropout, recurrent_dropout=rec_dropout)
        if layer.type == 'BidirectionalLSTM':
            if last:
                return layers.Bidirectional(layers.LSTM(layer.units, dropout=dropout,
                                                        recurrent_dropout=rec_dropout))
            return layers.Bidirectional(layers.LSTM(layer.units, return_sequences=True,
                                                    dropout=dropout, recurrent_dropout=rec_dropout))
