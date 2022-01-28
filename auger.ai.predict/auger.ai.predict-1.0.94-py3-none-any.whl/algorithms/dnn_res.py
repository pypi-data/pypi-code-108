from celery.utils.log import get_task_logger
logging = get_task_logger(__name__)

from tensorflow.compat.v1.keras.models import Model
from tensorflow.compat.v1.keras.layers import Input, Dense, Dropout, Embedding, Reshape, concatenate, ZeroPadding1D, add

from auger_ml.algorithms.dnn_base import DeepNeuralNetworkBase, DeepNeuralNetworkClassifier, DeepNeuralNetworkRegressor
from auger_ml.algorithms.dnn_shaped import ShapedDeepNeuralNetworkBase


class ResNetBase(DeepNeuralNetworkBase):
    def _create_model(self, model_inputs, input_layer, input_layer_shape):
        # Create internal layer structure of the network

        layer = input_layer
        prev_size = input_layer_shape

        # Stack fully connected layers on top
        for s, a, d, ki in zip(self.layer_sizes, self.layer_acts, self.layer_drops, self.layer_initializers):
            clean = layer
            transformed = Dense(units=s,
                                activation=a,
                                kernel_initializer=ki)(
                Dropout(rate=d)(layer)
            )

            if s > prev_size:
                clean = pad_to(clean, s - prev_size)
            elif s < prev_size:
                transformed = pad_to(transformed, prev_size - s)

            layer = add([transformed, clean])
            prev_size = max(s, prev_size)

        layer = Dense(units=self.last_layer_size_,
                      activation=self.last_layer_act_)(
            Dropout(rate=self.dropout_rate_final_layer)(layer)
        )

        model = Model(inputs=model_inputs,
                      outputs=layer)
        return model


def pad_to(x, delta):
    x = Reshape([-1, 1])(x)
    x = ZeroPadding1D(padding=(0, delta))(x)
    x = Reshape([-1])(x)

    return x


class ResNetClassifier(ResNetBase, DeepNeuralNetworkClassifier):
    pass


class ResNetRegressor(ResNetBase, DeepNeuralNetworkRegressor):
    pass


class ShapedResNetBase(ShapedDeepNeuralNetworkBase, ResNetBase):
    pass


class ShapedResNetClassifier(ShapedResNetBase, DeepNeuralNetworkClassifier):
    pass


class ShapedResNetRegressor(ShapedResNetBase, DeepNeuralNetworkRegressor):
    pass
