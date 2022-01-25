import numpy as np
import tensorflow as tf
from scipy.sparse import coo_matrix
from numpy.lib.stride_tricks import as_strided


def get_num_levels(layer_name):
    """
    Identify the number of resolution levels in the network based on the name of
    the bottleneck feature extraction layer of the VGG19.

    Args:
        layer_name (str): name of the VGG19 bottleneck layer for the encoder
    Returns:
        num_levels (int): the number of resolution levels
    """
    return int(layer_name[5:6])


def compute_input_paddings(input_shape, num_levels):
    """
    Compute the amount required for padding the input so that the encoding-decoding
    process does not lose pixels on the way.

    Args:
        input_shape (tuple): shape of the input tensor
        num_levels (int): number of resolution levels
    Returns:
        paddings (list): number of pixels to pad in each dimension
    """
    paddings = [[0, 0], [0, 0], [0, 0], [0, 0]]

    for d in range(1, 3):
        # both width and height have to be a multiple of 2 ^ (number of poolings)
        # in order for the downsampling to not deteriorate the shape
        divisor = 2 ** (num_levels - 1)
        full_paddings = (divisor - input_shape[d]) % divisor
        side_paddings = full_paddings // 2
        paddings[d] = [side_paddings, full_paddings - side_paddings]

    return paddings


def compute_mask(mask, features):
    """
    Compute a downsampled mask that matches the shape of `features`.

    Args:
        mask (np.ndarray): mask for the mapped feature extraction of shape [H, W, 1]
        features (tf.Tensor): extracted features of shape [H', W', C']
    Returns:
        mask (tf.Tensor): downsampled mask of shape [H', W']
    """
    mask_resized = tf.image.resize(
        mask,
        features.shape[:2],
        method=tf.image.ResizeMethod.NEAREST_NEIGHBOR,
    )
    return tf.squeeze(mask_resized, axis=-1)


def whitening_transform(fc, min_sv=1e-5, eps=1e-8):
    """
    Center the feature maps to 0 and apply whitening transform to remove the
    correlations between channels.

    Args:
        fc (tf.Tensor): flat content image feature maps
        min_sv (float): threshold for singular values
        eps (float): small constant for numerical stability
    Returns:
        fc_hat (tf.Tensor): whitened fc
    """
    # mean center the vectors
    mc = tf.reduce_mean(fc, axis=0, keepdims=True)
    X = fc - mc
    num_pixels, num_channels = tf.shape(X).numpy()

    # compute and decompose the covariance matrix
    cov = (
        tf.linalg.matmul(a=X, b=X, transpose_a=True)
        / (tf.cast(num_pixels, tf.float32) - 1.0)
        + tf.eye(num_channels) * eps
    )
    S, U, _ = tf.linalg.svd(cov)

    # filter small singular values
    S_size = len(S.numpy())
    num_sv = S_size
    for i in range(S_size):
        if S[i] < min_sv:
            num_sv = i
            break

    # trim matrices and compute Dw
    S = S[:num_sv]
    U = U[:, :num_sv]
    Dw = tf.linalg.diag(tf.pow(S, -0.5))

    # apply the set of matrix multiplications to obtain uncorrelated fc
    W = tf.linalg.matmul(a=tf.linalg.matmul(a=U, b=Dw), b=U, transpose_b=True)
    fc_hat = tf.linalg.matmul(a=X, b=W)

    return fc_hat


def colouring_transform(fc_hat, fs, min_sv=1e-5, eps=1e-8):
    """
    Apply colouring transform to make the correlations between `fc_hat`
    channels match the correlations between `fs` channels.

    Args:
        fc_hat (tf.Tensor): flat whitened content image feature maps
        fs (tf.Tensor): flat style image feature maps
        min_sv (float): threshold for singular values
        eps (float): small constant for numerical stability
    Returns:
        fcs (tf.Tensor): fc_hat coloured after fs
    """
    # mean center the fs vectors
    ms = tf.reduce_mean(fs, axis=0, keepdims=True)
    X = fs - ms
    num_pixels, num_channels = tf.shape(X).numpy()

    # compute and decompose the covariance matrix for fs
    cov = (
        tf.linalg.matmul(a=X, b=X, transpose_a=True)
        / (tf.cast(num_pixels, tf.float32) - 1.0)
        + tf.eye(num_channels) * eps
    )
    S, U, _ = tf.linalg.svd(cov)

    # filter small singular values
    S_size = len(S.numpy())
    num_sv = S_size
    for i in range(S_size):
        if S[i] < min_sv:
            num_sv = i
            break

    # trim matrices and compute Dw
    S = S[:num_sv]
    U = U[:, :num_sv]
    Dc = tf.linalg.diag(tf.pow(S, 0.5))

    # apply the set of matrix multiplications to obtain fs-correlated fcs
    C = tf.linalg.matmul(a=tf.linalg.matmul(a=U, b=Dc), b=U, transpose_b=True)
    fcs = tf.linalg.matmul(a=fc_hat, b=C)

    # shift back using the previously subtracted mean vectors
    fcs += ms

    return fcs


def _rolling_block(A, block=(3, 3)):
    """
    Applies a sliding window to given matrix.

    Args:
        A (np.ndarray): input matrix
        block (tuple): block shape
    Returns:
        A_strided (np.ndarray): strided output matrix
    """
    shape = (A.shape[0] - block[0] + 1, A.shape[1] - block[1] + 1) + block
    strides = A.strides + A.strides
    return as_strided(A, shape=shape, strides=strides)


def matting_affinity_laplacian(image, eps=1e-7, window_radius=1):
    """
    Create the Laplacian for the so cold "matting affinity" from the given image
    More details in equation (15) from:
    https://people.csail.mit.edu/alevin/papers/Matting-Levin-Lischinski-Weiss-CVPR06.pdf.

    Args:
        image (np.ndarray): the input rgb image
        eps (float): regularization parameter controlling smoothness
        window_radius (int): radius of the window used to build the Laplacian
    Returns:
        L (np.ndarray): the matting affinity Laplacian
    """
    window_diameter = window_radius * 2 + 1
    window_size = window_diameter ** 2
    height, width, channels = image.shape
    centers_h = height - 2 * window_radius
    centers_w = width - 2 * window_radius

    ravel_image = image.reshape(height * width, channels)
    image_indices = np.arange(height * width).reshape((height, width))
    window_indices = _rolling_block(image_indices, (window_diameter, window_diameter))
    window_indices = window_indices.reshape(centers_h, centers_w, window_size)

    windowed_values = ravel_image[window_indices]
    windowed_mu = np.mean(windowed_values, axis=2, keepdims=True)
    windowed_var = np.einsum(
        '...ji,...jk ->...ik', windowed_values, windowed_values
    ) / window_size - np.einsum('...ji,...jk ->...ik', windowed_mu, windowed_mu)

    inv = np.linalg.inv(windowed_var + (eps / window_size) * np.eye(3))
    X = np.einsum('...ij,...jk->...ik', windowed_values - windowed_mu, inv)
    Z = np.einsum('...ij,...kj->...ik', X, windowed_values - windowed_mu)
    values = (1 + Z) / window_size

    col_indices = np.tile(window_indices, window_size).ravel()
    row_indices = np.repeat(window_indices, window_size).ravel()
    val_indices = values.ravel()

    return coo_matrix(
        (val_indices, (row_indices, col_indices)), shape=(height * width, height * width)
    )
