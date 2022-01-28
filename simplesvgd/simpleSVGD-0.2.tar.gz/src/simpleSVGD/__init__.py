from enum import auto
import numpy as _numpy
import tqdm.auto as _tqdm_auto
from scipy.spatial.distance import pdist as _pdist, squareform as _squareform
import matplotlib.pyplot as _plt
import matplotlib.figure as _figure
from typing import Callable as _Callable, List as _List, Tuple as _Tuple


def _rbf_kernel(theta, h=-1):
    """Radial basis function kernel."""
    sq_dist = _pdist(theta)
    pairwise_dists = _squareform(sq_dist) ** 2
    if h < 0:  # if h < 0, using median trick
        h = _numpy.median(pairwise_dists)
        h = _numpy.sqrt(0.5 * h / _numpy.log(theta.shape[0] + 1))

    # compute the rbf kernel
    Kxy = _numpy.exp(-pairwise_dists / h ** 2 / 2)

    dxkxy = -_numpy.matmul(Kxy, theta)
    sumkxy = _numpy.sum(Kxy, axis=1)
    for i in range(theta.shape[1]):
        dxkxy[:, i] = dxkxy[:, i] + _numpy.multiply(theta[:, i], sumkxy)
    dxkxy = dxkxy / (h ** 2)
    return (Kxy, dxkxy)


def update(
    x0: _numpy.array,
    gradient_fn: _Callable,
    # All following parameters are tuning parameters
    n_iter: int = 1000,
    stepsize: float = 1e-3,
    bandwidth: float = -1,
    alpha: float = 0.9,
    fudge_factor=1e-3,
    historical_grad=1,
    # All following parameter only concern animation
    animate: bool = False,
    figure: _figure.Figure = None,
    dimensions_to_plot: _List[float] = [0, 1],
    background: _Tuple[_numpy.array] = None,
):
    """
    Function to update a collection of samples using the SVGD algorithm.

    x0
        The initial samples are given to the function using x0, which has shape
        (n_samples, function_dimensionality).

    gradient_fn
        A callable which computes the gradients of the function to approximate.
        No values of the actual function are needed. Should accept multiple
        points in input space (i.e. the shape of x0) and return a gradient of
        the same shape as its input. In a Bayesian context; the actual
        gradients to pass are those of the negative log likelihood.

    n_iter
        Number of iterations to do on the samples. Default is 1000.

    stepsize
        Stepsize of the SVGD algorithm. Default is 1e-3.

    bandwidth
        Bandwidth of the radial basis functions. Omitting this (or passing -1)
        automatically computes it based on the distribution of samples. This is
        more likely to produce good results, but will slow the algorithm down.
        Default is -1.

    alpha
        Parameter with which to dampen gradient changes in the target function
        during SVGD updating. Default is 0.9.

    animate
        A boolean to animate the algorithm. Only works for functions of at
        least two dimensions. Default is False.

    figure
        A figure object in which to use the current axis for the animation.
        Passing None will create a new figure. Default is None.

    dimensions_to_plot
        An array of two ints which describe which two dimensions to animate of
        any higher dimensional function. Default is [0, 1].

    background
        A tuple of three arrays, used for the first three arguments of
        matplotlib.pyplot.contour, to make plotting a background easier.
    """
    # Check input
    if x0 is None or gradient_fn is None:
        raise ValueError("x0 or gradient_fn cannot be None!")

    if animate:
        if figure is None:
            figure = _plt.figure(figsize=(8, 8))
        axis = _plt.gca()

    # To make sure we don't accidentally update a variable we're not supposed
    # to (i.e. avoid changing a variable by reference)
    x0_updated = _numpy.copy(x0)

    # adagrad with momentum
    if animate:
        if background is not None:
            x1s, x2s, background_image = background

            axis.contour(
                x1s,
                x2s,
                _numpy.exp(-background_image),
                levels=20,
                alpha=0.5,
                zorder=0,
            )

        scatter = axis.scatter(
            x0_updated[:, dimensions_to_plot[0]],
            x0_updated[:, dimensions_to_plot[1]],
        )

        if background is not None:
            _plt.xlim([x1s.min(), x1s.max()])
            _plt.ylim([x2s.min(), x2s.max()])

        axis.set_aspect(1)

        figure.canvas.draw()
        _plt.pause(0.00001)

    # The Try/Except allows on to interrupt the algorithm using CTRL+C while
    # still getting x0_updated at the point of interruption.
    try:
        for iter in _tqdm_auto.trange(n_iter):

            # Calculate all the gradients of the -log(p)
            grad_neglogp = -gradient_fn(x0_updated)

            # calculating the kernel matrix
            kxy, dxkxy = _rbf_kernel(x0_updated, h=bandwidth)
            grad_theta = (_numpy.matmul(kxy, grad_neglogp) + dxkxy) / x0.shape[
                0
            ]

            # adagrad
            if iter == 0:
                historical_grad = historical_grad + grad_theta ** 2
            else:
                historical_grad = alpha * historical_grad + (1 - alpha) * (
                    grad_theta ** 2
                )
            adj_grad = _numpy.divide(
                grad_theta, fudge_factor + _numpy.sqrt(historical_grad)
            )
            x0_updated = x0_updated + stepsize * adj_grad

            if animate:
                scatter.set_offsets(
                    _numpy.hstack(
                        (
                            x0_updated[:, dimensions_to_plot[0], None],
                            x0_updated[:, dimensions_to_plot[1], None],
                        )
                    )
                )
                figure.canvas.draw()
                _plt.pause(0.00001)

    except KeyboardInterrupt:
        pass

    return x0_updated


def gradient_vectorizer(non_vectorized_gradient: _Callable):
    def grd(m: _numpy.array) -> _numpy.array:
        return _numpy.hstack(
            [
                non_vectorized_gradient(m[idm, :, None])
                for idm in range(m.shape[0])
            ]
        ).T

    return grd

from . import _version
__version__ = _version.get_versions()['version']
