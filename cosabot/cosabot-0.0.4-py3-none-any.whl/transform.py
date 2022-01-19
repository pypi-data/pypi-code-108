import random
import numpy as np
from sklearn.cluster import KMeans
from PIL import Image
from scipy.ndimage.filters import gaussian_filter
from scipy.ndimage.interpolation import map_coordinates


def k_representative_pallette(image, num_clusters=random.randint(4, 5)):
    """Cluster pixels into num_clusters representative colors
    and transform image into to this discrete palette
    """
    ysize = image.shape[0]
    xsize = image.shape[1]
    new_image = np.reshape(image, (xsize * ysize, 3))
    model = KMeans(n_clusters=num_clusters, random_state=42).fit(new_image)
    colors = []
    for i in range(num_clusters):
        colors.append(np.median(new_image[model.labels_ == i], axis=0))
        colors[i] = colors[i] / 255
    new_image = np.zeros((xsize * ysize, 3))
    for i in range(num_clusters):
        slicer = model.labels_ == i
        new_image[slicer] = colors[i]
    new_image = np.reshape(new_image, (ysize, xsize, 3))
    new_image = Image.fromarray((new_image * 255).astype(np.uint8))
    return new_image


def elastic_transform(
    image,
    alpha=random.randint(900, 1000),
    sigma=random.randint(4, 8),
    random_state=None,
):
    """Elastic deformation of images as described in [Simard2003]
    Simard, Steinkraus and Platt, "Best Practices for
    Convolutional Neural Networks applied to Visual Document
    Analysis", in Proc. of the International Conference on
    Document Analysis and Recognition, 2003.
    """
    if random_state is None:
        random_state = np.random.RandomState(None)
    shape = image.shape
    dx = (
        gaussian_filter(
            (random_state.rand(*shape) * 2 - 1), sigma, mode="constant", cval=0
        )
        * alpha
    )
    dy = (
        gaussian_filter(
            (random_state.rand(*shape) * 2 - 1), sigma, mode="constant", cval=0
        )
        * alpha
    )
    x, y, z = np.meshgrid(
        np.arange(shape[1]),
        np.arange(shape[0]),
        np.arange(shape[2]),
    )
    indices = (
        np.reshape(y + dy, (-1, 1)),
        np.reshape(x + dx, (-1, 1)),
        np.reshape(z, (-1, 1)),
    )
    distored_image = map_coordinates(image, indices, order=1, mode="reflect")
    dist_reshaped = distored_image.reshape(image.shape)
    dist_reshaped = Image.fromarray(dist_reshaped)
    return dist_reshaped
