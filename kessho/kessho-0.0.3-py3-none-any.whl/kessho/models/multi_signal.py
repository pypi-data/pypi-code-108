from typing import Dict, Union, Tuple

import tensorflow as tf
from tensorflow.keras import layers


class MultiSignalModel(tf.keras.Model):
    """
    A Keras model ready to take a tf.Dataset with the 3 categories of financial features
    for the naive modeling.
    """

    def call(self, inputs, training=None, mask=None):
        return super().call(inputs, training, mask)

    def get_config(self):
        return super().get_config()

    def __init__(self, name: str, shapes: Dict[str, Union[Tuple, int]], model_fn=None):
        """
        :param name: a name for the model. Must obey restrictions for tf.keras naming.
        :param shapes: must be a dict containing
            - a 3-dim shape for FINGERPRINT: n_days x n_hours x n_observables,
            - a 2-dim shape for TRENDS     : n_indicators x n_frequencies
            - an int        for SEASONALITY: n_buckets of the year
        :param model_fn: A function that takes any number of input tensors and returns the resulting output tensor.
        """

        inputs, signals = self.create_inputs_and_signals(shapes)

        model_fn = model_fn or self.assemble_network

        output_layer = model_fn(**signals)
        super().__init__(inputs=inputs, outputs=output_layer, name=name)

    @staticmethod
    def assemble_network(FINGERPRINT, SEASONALITY, TRENDS):

        # Fingerprint feature
        conv1 = layers.Conv2D(6, (2, 2), activation='relu')(FINGERPRINT)
        mp = layers.MaxPool2D(2, 2)(conv1)
        f1 = layers.Flatten()(mp)
        d1 = layers.Dense(5)(f1)

        # Flatten and process the trend signal
        f2 = layers.Flatten()(TRENDS)
        d2 = layers.Dense(16)(f2)

        # Process the seasonality signal
        d3 = layers.Dense(6)(SEASONALITY)

        # combine the three signals and feed into a last dense layer
        combined = tf.concat([d1, d2, d3], axis=1)
        d4 = layers.Dense(32)(combined)
        output_layer = layers.Dense(3)(d4)
        return output_layer

    @staticmethod
    def create_inputs_and_signals(shapes: Dict[str, Union[Tuple, int]]):
        inputs = {}
        features_flat = {}
        signals = {}
        for key, shape in shapes.items():
            col = tf.feature_column.numeric_column(key, shape=shape)
            features_flat[key] = tf.keras.layers.DenseFeatures([col])
            inputs[key] = tf.keras.layers.Input(shape=shape)

        for key, shape in shapes.items():
            if not isinstance(shape, int):
                reshape = tf.keras.layers.Reshape(target_shape=shape)
                signal = reshape(features_flat[key](inputs))
                signals[key] = signal
            else:
                signal = features_flat[key](inputs)
                signals[key] = signal

        return inputs, signals
