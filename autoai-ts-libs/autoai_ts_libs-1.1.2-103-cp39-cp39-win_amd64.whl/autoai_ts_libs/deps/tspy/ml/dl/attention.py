from tensorflow_core.python.keras import backend as K
from tensorflow_core.python.keras import initializers
from tensorflow_core.python.keras.engine.base_layer import Layer, InputSpec
import tensorflow as tf

"""
Both the following layers should actually work on LSTMs as well as Bidirectional LSTMs. But currently they are
kept distinct
"""


class BiLSTMAttention(Layer):
    """
    Computes a weighted average attention mechanism from:
        Zhou, Peng, Wei Shi, Jun Tian, Zhenyu Qi, Bingchen Li, Hongwei Hao and Bo Xu,
        â€œAttention-Based Bidirectional Long Short-Term Memory Networks for Relation Classification.â€
        ACL (2016). http://www.aclweb.org/anthology/P16-2034
    """

    def __init__(self, return_attention=False, **kwargs):
        self.init = initializers.get('uniform')
        self.supports_masking = True
        self.return_attention = return_attention
        super(BiLSTMAttention, self).__init__(**kwargs)

    def build(self, input_shape):
        self.input_spec = [InputSpec(ndim=3)]
        assert len(input_shape) == 3

        self.w = self.add_weight(shape=(input_shape[2], 1),
                                 name='{}_w'.format(self.name),
                                 initializer=self.init)
        self.trainable_weights.append(self.w)
        super(BiLSTMAttention, self).build(input_shape)

    def call(self, h, mask=None):
        """
        Performs the following operations
        M = tanh(H)
        Î± = softmax(wTM)
        r = HÎ±T
        hâˆ— = tanh(r)
        :param h: hidden states from the output of the last BiLSTM
        :param mask: mask to ignore padded values
        :return:
        """
        h_shape = K.shape(h)
        batch_size, timesteps = h_shape[0], h_shape[1]

        m = K.tanh(h)
        logits = K.dot(m, self.w)  # w^T M
        logits = K.reshape(logits, (batch_size, timesteps))

        # softmax is performed in a 2 step manner to apply the mask
        alpha = K.exp(logits - K.max(logits, axis=-1, keepdims=True))  # exp for softmax

        # masked timesteps have zero weight
        if mask is not None:
            mask = K.cast(mask, K.floatx())
            alpha = alpha * mask

        alpha = alpha / K.sum(alpha, axis=1, keepdims=True)  # softmax

        r = K.sum(h * K.expand_dims(alpha), axis=1)  # r = h*alpha^T
        h_star = K.tanh(r)  # h^* = tanh(r)
        if self.return_attention:
            return [h_star, alpha]
        return h_star


class LSTMAttention(Layer):
    """
    Attention mechanism from:
     Dzmitry Bahdanau, Kyunghyun Cho, Yoshua Bengio,
     "NEURAL MACHINE TRANSLATION BY JOINTLY LEARNING TO ALIGN AND TRANSLATE"
     https://arxiv.org/abs/1409.0473
    """

    def __init__(self, units=10, **kwargs):
        super(LSTMAttention, self).__init__(**kwargs)
        self.units = units
        self.W = tf.keras.layers.Dense(self.units)
        self.V = tf.keras.layers.Dense(1)

    def call(self, values, mask=None):
        shp = tf.shape(values)
        batch_size, timesteps = shp[0], shp[1]

        # score shape == (batch_size, max_length, 1)
        # we get 1 at the last axis because we are applying score to self.V
        # the shape of the tensor before applying self.V is (batch_size, max_length, units)
        score = self.V(tf.nn.tanh(self.W(values)))

        # attention_weights shape == (batch_size, max_length)

        # softmax is performed in a 2 step manner to apply the mask
        exp = tf.exp(score)
        if mask is not None:
            mask = tf.cast(mask, tf.float32)
            exp = tf.reshape(exp, (batch_size, timesteps)) * mask
        attention_weights = exp / tf.reduce_sum(exp, keepdims=True, axis=1)

        # context_vector shape after sum == (batch_size, hidden_size)
        context_vector = tf.reshape(attention_weights, (batch_size, timesteps, 1)) * values
        context_vector = tf.reduce_sum(context_vector, axis=1)

        return context_vector, attention_weights

    def get_config(self):
        config = super(LSTMAttention, self).get_config()
        config.update({"units": self.units})
        return config
