import tensorflow as tf


class Triangular(tf.keras.layers.Layer):
    """
    Autoregressive layer with triangular (or triangular-like) kernel.
    """
    def __init__(self, expansion=1, upper=True, mirror_activation=False):
        super(Triangular, self).__init__()
        self.expansion = expansion
        self.upper = tf.constant(upper)
        self.mirror_activation = tf.constant(mirror_activation)

        ##
        self.w = None
        self.b = None

    @staticmethod
    @tf.function
    def fill_triangular(vector):
        "Simple implementation to avoid depending on tensorflow_probability. tfp.math.fill_triangular"
        n = int((8 * vector.shape[-1] + 1) ** 0.5 - 1) // 2
        ret = tf.stack(
            [tf.concat((vector[(i * (i + 1)) // 2:(i * (i + 1) // 2 + i + 1)], tf.zeros(n - i - 1)), axis=0)
             for i in range(n)]
        )
        return ret

    def build(self, input_shape):
        self.w = [self.add_weight(
            shape=(input_shape[-1] * (input_shape[-1] + 1) // 2), initializer="zeros", trainable=True
        ) for i in range(self.expansion)]
        self.b = self.add_weight(shape=(input_shape[-1] * self.expansion,), initializer="zeros", trainable=True)

    def call(self, inputs, *args, **kwargs):
        alpha = 0.1
        if self.upper:
            matrices = [tf.eye(inputs.shape[-1]) + self.fill_triangular(w) for w in self.w]
        else:
            matrices = [tf.eye(inputs.shape[-1]) + tf.transpose(self.fill_triangular(w)) for w in self.w]

        matrix = tf.concat(matrices, axis=-1)
        ret = tf.matmul(inputs, matrix) + self.b

        if self.mirror_activation:
            return tf.where(ret < 0, ret, alpha * ret + 1 - tf.exp(-(1 - alpha) * ret))
        else:
            return tf.where(ret > 0, ret, alpha * ret + tf.exp((1 - alpha) * ret) - 1)

    def get_config(self):
        return dict (
            expansion=self.expansion,
            upper=self.upper,
            mirror_activation=self.mirror_activation,
        )