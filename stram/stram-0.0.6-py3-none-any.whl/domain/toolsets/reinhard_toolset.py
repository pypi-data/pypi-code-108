import numpy as np
import tensorflow as tf


def exchange_stats(content_lab, style_lab, content_mask, style_mask):
    """
    Compute the mean and standard deviation for each channel independently from the
    lab images `content_lab` and `style_lab. The images can be separated into clusters
    according to `content_mask` and `style_mask` and the stats are computed for each
    cluster separately. After that, the stats from the content image are set to match
    the stats from the style image.

    Args:
        content_lab (tf.Tensor): content image in lab space
        style_lab (tf.Tensor): style image in lab space
        content_mask (np.ndarray): mask with the colour cluster regions for the
            content image
        style_mask (np.ndarray): mask with the colour cluster regions for the
            style image
    Returns:
        synthesized_lab (tf.Tensor): resulted image in lab space
    """
    eps = tf.keras.backend.epsilon()
    channel_offset = tf.constant([0, 0, 0, 1], dtype=tf.int64)

    synthesized_lab = tf.identity(content_lab)
    content_mask_tf = tf.expand_dims(content_mask, axis=0)
    style_mask_tf = tf.expand_dims(style_mask, axis=0)

    for cluster in np.setdiff1d(np.unique(content_mask), [0]):
        where_c = tf.where(content_mask_tf == cluster)
        where_s = tf.where(style_mask_tf == cluster)

        for channel in range(content_lab.shape[-1]):
            channel_where_c = where_c + channel * channel_offset
            channel_where_s = where_s + channel * channel_offset
            values_c = tf.gather_nd(content_lab, channel_where_c)
            values_s = tf.gather_nd(style_lab, channel_where_s)

            means_c = tf.math.reduce_mean(values_c)
            means_s = tf.math.reduce_mean(values_s)
            stds_c = tf.math.reduce_std(values_c)
            stds_s = tf.math.reduce_std(values_s)

            new_values = (values_c - means_c) * stds_s / (stds_c + eps) + means_s
            synthesized_lab = tf.tensor_scatter_nd_update(
                synthesized_lab, channel_where_c, new_values
            )

    return synthesized_lab
