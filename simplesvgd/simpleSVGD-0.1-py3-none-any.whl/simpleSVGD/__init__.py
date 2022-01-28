import numpy as _np
import tqdm as _tqdm
from scipy.spatial.distance import pdist as _pdist, squareform as _squareform
import matplotlib.pyplot as _plt


def _rbf_kernel(theta, h=-1):
    """Radial basis function kernel."""
    sq_dist = _pdist(theta)
    pairwise_dists = _squareform(sq_dist) ** 2
    if h < 0:  # if h < 0, using median trick
        h = _np.median(pairwise_dists)
        h = _np.sqrt(0.5 * h / _np.log(theta.shape[0] + 1))

    # compute the rbf kernel
    Kxy = _np.exp(-pairwise_dists / h ** 2 / 2)

    dxkxy = -_np.matmul(Kxy, theta)
    sumkxy = _np.sum(Kxy, axis=1)
    for i in range(theta.shape[1]):
        dxkxy[:, i] = dxkxy[:, i] + _np.multiply(theta[:, i], sumkxy)
    dxkxy = dxkxy / (h ** 2)
    return (Kxy, dxkxy)


def update(x0, gradient_fn, n_iter=1000, stepsize=1e-3, bandwidth=-1, alpha=0.9, h=-1):
    # Check input
    if x0 is None or gradient_fn is None:
        raise ValueError("x0 or gradient_fn cannot be None!")

    theta = _np.copy(x0)

    # adagrad with momentum
    fudge_factor = 1e-6
    historical_grad = 0
    try:
        for iter in _tqdm.trange(n_iter):

            lnpgrad = gradient_fn(theta)
            # calculating the kernel matrix
            kxy, dxkxy = _rbf_kernel(theta, h=h)
            grad_theta = (_np.matmul(kxy, lnpgrad) + dxkxy) / x0.shape[0]

            # adagrad
            if iter == 0:
                historical_grad = historical_grad + grad_theta ** 2
            else:
                historical_grad = alpha * historical_grad + (1 - alpha) * (
                    grad_theta ** 2
                )
            adj_grad = _np.divide(grad_theta, fudge_factor + _np.sqrt(historical_grad))
            theta = theta + stepsize * adj_grad
    except KeyboardInterrupt:
        pass

    return theta


def update_visual(
    x0,
    lnprob,
    n_iter=1000,
    stepsize=1e-3,
    bandwidth=-1,
    alpha=0.9,
    figure=None,
    dimensions_to_plot=[0, 1],
    background=None,
):

    if figure is None:
        figure = _plt.figure(figsize=(8, 8))

    axis = _plt.gca()

    # Check input
    if x0 is None or lnprob is None:
        raise ValueError("x0 or lnprob cannot be None!")

    theta = _np.copy(x0)

    # adagrad with momentum
    fudge_factor = 1e-6
    historical_grad = 0

    if background is not None:
        x1s, x2s, background_image = background

        axis.contour(
            x1s,
            x2s,
            _np.exp(-background_image),
            levels=20,
            alpha=0.5,
            zorder=0,
        )

    scatter = axis.scatter(
        theta[:, dimensions_to_plot[0]], theta[:, dimensions_to_plot[1]]
    )

    if background is not None:
        _plt.xlim([x1s.min(), x1s.max()])
        _plt.ylim([x2s.min(), x2s.max()])

    axis.set_aspect(1)

    figure.canvas.draw()
    _plt.pause(0.00001)

    try:
        for iter in _tqdm.trange(n_iter):

            lnpgrad = lnprob(theta)
            # calculating the kernel matrix
            kxy, dxkxy = _rbf_kernel(theta, h=-1)
            grad_theta = (_np.matmul(kxy, lnpgrad) + dxkxy) / x0.shape[0]

            # adagrad
            if iter == 0:
                historical_grad = historical_grad + grad_theta ** 2
            else:
                historical_grad = alpha * historical_grad + (1 - alpha) * (
                    grad_theta ** 2
                )
            adj_grad = _np.divide(grad_theta, fudge_factor + _np.sqrt(historical_grad))
            theta = theta + stepsize * adj_grad

            scatter.set_offsets(
                _np.hstack(
                    (
                        theta[:, dimensions_to_plot[0], None],
                        theta[:, dimensions_to_plot[1], None],
                    )
                )
            )
            figure.canvas.draw()
            _plt.pause(0.00001)

    except KeyboardInterrupt:
        pass

    return theta
