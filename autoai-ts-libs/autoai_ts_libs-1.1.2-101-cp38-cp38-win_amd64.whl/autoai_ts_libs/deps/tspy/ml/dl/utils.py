import numpy as np
import math


def transform_labels_to_distribution(labels, num_buckets):
    """
    Transfrom labels to a distribution
    :param labels:
    :param num_buckets:
    :return:
    """
    transformed = []
    # convert [num_preds, num_feats] label to [num_preds, num_feats, num_buckets]
    for sample in labels:
        ns = []
        for timestep in sample:
            tf = []
            for feature in timestep:
                tf.append(__get_hist__(feature, num_buckets))
            ns.append(tf)
        transformed.append(ns)
    transformed_arr = np.array(transformed)
    return transformed_arr


def __get_hist__(feature, num_buckets):
    hist = [0] * num_buckets
    per_bucket_range = 2.0 / num_buckets
    # number/ per_bucket_range + 0(if neg) + buckets/2 (if pos) followed by floor
    abs_feat = math.fabs(feature)
    add = num_buckets / 2.0
    ind = math.floor((abs_feat / per_bucket_range) + add)
    if ind >= num_buckets:
        ind = num_buckets - 1
    non_zero_index = num_buckets - 1 - ind if feature < 0 else ind
    hist[non_zero_index] = 1.0
    return hist


def transform_distribution_to_labels(distribution):
    """
    Given the distribution prediction, get the actual value (approximate value)
    :param distribution:
    :return:
    """
    # assuming distribution shape is [num_samples, num_preds, num_features, num_buckets]
    num_buckets = distribution.shape[3]
    transformed = []
    # convert [num_preds, num_feats] label to [num_preds, num_feats, num_buckets]
    for sample in distribution:
        new_sample = []
        for step in sample:
            transformed_feats = []
            for feat in step:
                transformed_feats.append(__hist_to_feature__(feat, num_buckets))
            new_sample.append(transformed_feats)
        transformed.append(new_sample)
    transformed_arr = np.array(transformed)
    return transformed_arr


def __hist_to_feature__(feat, num_buckets):
    per_bucket_range = 2.0 / num_buckets
    ind = np.argmax(feat)
    range_start = -1.0 + per_bucket_range * ind
    range_end = range_start + per_bucket_range
    return (range_start + range_end) / 2
