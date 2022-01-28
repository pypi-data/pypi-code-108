import numpy as np
import tensorflow as tf
from tensorflow.python.keras.losses import LossFunctionWrapper
from tensorflow.python.keras.utils import losses_utils


def weighted_loss(y_true, y_pred, baseloss, sample_weights, sample_weights_bias, output_weights, **kwargs):
    baseloss_fn = tf.keras.losses.get(baseloss)
    loss = baseloss_fn(y_true[..., None], y_pred[..., None], **kwargs)

    if sample_weights is not None:
        ww = tf.tensordot(y_true, tf.cast(sample_weights, y_true.dtype), axes=[3, 0]) + tf.cast(sample_weights_bias,
                                                                                                y_true.dtype)
        ww = tf.clip_by_value(ww, 0, np.inf)
        loss = loss * ww

    if output_weights is not None:
        loss = tf.tensordot(loss, output_weights, axes=1)

    return loss


class WeightedLossV2(LossFunctionWrapper):
    def __init__(self,
                 baseloss="binary_crossentropy",
                 sample_weights=None,
                 sample_weights_bias=None,
                 output_weights=None,
                 from_logits=False,
                 label_smoothing=0,
                 reduction=losses_utils.ReductionV2.AUTO,
                 name='weighted_loss'):

        if sample_weights is not None:
            sample_weights = tf.constant(sample_weights, tf.float32)

        if sample_weights_bias is not None:
            sample_weights_bias = tf.constant(sample_weights_bias, tf.float32)

        if output_weights is not None:
            output_weights = tf.constant(output_weights, tf.float32)

        super().__init__(
            weighted_loss,
            baseloss=baseloss,
            name=name,
            reduction=reduction,
            from_logits=from_logits,
            label_smoothing=label_smoothing,
            sample_weights=sample_weights,
            sample_weights_bias=sample_weights_bias,
            output_weights=output_weights,
        )