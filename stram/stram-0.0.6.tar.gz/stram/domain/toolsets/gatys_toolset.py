import numpy as np
import tensorflow as tf
import tensorflow.keras as keras
from static_variables import resolve_static


def compute_mask_set(mask, features):
    """
    Compute the set of downsampled masks that correspond to the feature levels.

    Args:
        mask (np.ndarray): the mask for the mapped feature extraction
        features (dict): maps layer name to extracted features
    Returns:
        mask_set (dict): maps layer name to corresponding mask
    """
    mask_original = tf.expand_dims(mask, axis=0)
    return {
        layer: tf.image.resize(
            mask_original,
            feature.shape[1:3],
            method=tf.image.ResizeMethod.NEAREST_NEIGHBOR,
        )
        for layer, feature in features.items()
    }


def gram_matrix(input_tensor, boolean_mask):
    """
    Compute the gram matrix on the last dimension of the input tensor using
    only locations selected by the `boolean_mask`.

    Args:
        input_tensor (tf.Tensor): tensor of rank 4
        boolean_mask (tf.Tensor): masks locations of interest
    Returns:
        gram_matrix (tf.Tensor): tensor of rank 2
    """
    selected = input_tensor[boolean_mask]
    result = tf.linalg.einsum('nc,nd->cd', selected, selected)
    num_locations = tf.reduce_sum(tf.cast(boolean_mask, tf.float32))
    return result / num_locations


def compute_gram_matrices(input_tensor, mask):
    """
    Compute a set of gram matrices using all labels found in `mask`.

    Args:
        input_tensor (tf.Tensor): tensor of rank 4
        mask (np.ndarray): maps locations to style labels
    Returns:
        gram_matrices (dict): maps style label to gram matrix
    """
    gram_matrices = {}

    for label in np.setdiff1d(np.unique(mask), [0]):
        boolean_mask = tf.squeeze(mask == label, axis=-1)
        gram_matrices[label] = gram_matrix(input_tensor, boolean_mask)

    return gram_matrices


def _get_magnitude_normalisation_factors(power=1.0):
    """
    Get a dict with custom normalisation factors for each layer in the VGG19.
    The values have been computed by averaging the activations of the entire
    unlabelled dataset of COCO 2017 when passing the data through the network.

    Args:
        power (float): exponent for base values based on further usage
    Returns:
        normalisation_factors (dict): maps layer name to normalisation value
    """
    average_vgg19_layer_activation = dict(
        block1_conv1=21.3766174316406,
        block1_conv2=98.0979156494141,
        block2_conv1=123.892250061035,
        block2_conv2=111.009941101074,
        block3_conv1=127.140815734863,
        block3_conv2=164.742660522461,
        block3_conv3=345.452362060547,
        block3_conv4=509.229614257812,
        block4_conv1=526.813049316406,
        block4_conv2=346.448577880859,
        block4_conv3=193.982391357422,
        block4_conv4=47.8912048339844,
        block5_conv1=51.1512794494629,
        block5_conv2=21.5614013671875,
        block5_conv3=8.86503982543945,
        block5_conv4=1.11896836757660,
    )
    return {key: value ** power for key, value in average_vgg19_layer_activation.items()}


@resolve_static(
    static_variables={
        'mse': keras.losses.MeanSquaredError(),
        'normalisation_factors': _get_magnitude_normalisation_factors(2.0),
    }
)
def content_loss(content_features, synthesized_features, weights):
    """
    Compute the weighted mean squared error between two dictionaries of
    corresponding tensors.

    Args:
        content_features (dict): maps layer name to extracted features
        synthesized_features (dict): maps layer name to extracted features
        weights (dict): maps layer name to corresponding loss weight
    Returns:
        loss_value (tf.float32): the loss value
    """
    loss_value = 0.0

    for layer, features in content_features.items():
        weight = weights[layer] / normalisation_factors[layer]
        loss_value += weight * mse(features, synthesized_features[layer])

    return loss_value


@resolve_static(
    static_variables={
        'mse': keras.losses.MeanSquaredError(),
        'normalisation_factors': _get_magnitude_normalisation_factors(4.0),
    }
)
def style_loss(style_gram_matrices, synthesized_features, content_mask_set, weights):
    """
    Compute the weighted mean squared error between two dictionaries of gram
    matrices from corresponding tensors while mapping the loss regions given by
    `content_mask_set` and `style_gram_matrices`.

    Args:
        style_gram_matrices (dict): maps layer name to gram matrices set
        synthesized_features (dict): maps layer name to extracted features
        content_mask_set (dict): maps layer name to label mask for content image
        weights (dict): maps layer name to corresponding loss weight
    Returns:
        loss_value (tf.float32): the loss value
    """
    loss_value = 0.0

    for layer, gram_matrix_set in style_gram_matrices.items():
        weight = weights[layer] / normalisation_factors[layer]

        for label, true_gm in gram_matrix_set.items():
            boolean_mask = tf.squeeze(content_mask_set[layer] == label, axis=-1)
            gm = gram_matrix(synthesized_features[layer], boolean_mask)
            loss_value += weight * mse(true_gm, gm)

    return loss_value
