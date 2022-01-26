#!/usr/bin/env python

"""Mean signal diffusion kurtosis imaging (i.e., "powder kurtosis")."""

# Parameter array elements are:
#
# params[..., 0] = log(S0)
# params[..., 1] = MSD
# params[..., 2] = MSK


def _msk_fit(data, bvals, bvecs, mask=None):
    """Estimate mean signal model parameters with non-linear least squares.

    Parameters
    ----------
    data : numpy.ndarray
        Floating-point array with shape (..., number of acquisitions).
    bvals : numpy.ndarray
        Floating-point array with shape (number of acquisitions,).
    bvecs : numpy.ndarray
        Floating-point array with shape (number of acquisitions, 3).
    mask : numpy.ndarray, optional
        Boolean array.

    Returns
    -------
    numpy.ndarray
    """

    if mask is None:
        mask = np.ones(data.shape[0:-1]).astype(bool)

    bs = np.unique(bvals)
    pa_data = np.zeros(data.shape[0:-1] + (len(bs),))
    for i, b in enumerate(bs):
        pa_data[..., i] = np.mean(data[..., np.where(bvals == b)[0]], axis=-1)
    pa_data_flat = pa_data[mask]
    size = len(pa_data_flat)

    design_matrix = np.zeros((3, 3))
    design_matrix[:, 0] = 1
    design_matrix[:, 1] = -bs
    design_matrix[:, 2] = bs ** 2 / 6
    x0_flat = (
        np.linalg.pinv(design_matrix.T @ design_matrix)
        @ design_matrix.T
        @ np.log(pa_data_flat)[..., np.newaxis]
    )[..., 0]

    x0_flat = jnp.asarray(x0_flat)
    design_matrix = jnp.asarray(design_matrix)
    pa_data_flat = jnp.asarray(pa_data_flat)

    def cost(params, design_matrix, y):
        return jnp.mean((jnp.exp(design_matrix @ params) - y) ** 2)

    @jax.jit
    def jit_minimize(i):
        return jaxminimize(
            fun=cost,
            x0=x0_flat[i],
            args=(design_matrix, pa_data_flat[i]),
            method="BFGS",
            options={"line_search_maxiter": 100},
        )

    msk_params_flat = np.zeros((size, 3))
    for i in range(size):
        results = jit_minimize(i)
        msk_params_flat[i] = results.x
        # if not results.success:
        #    print(f"Fit was not successful in voxel {i} (status = {results.status})")

    msk_params = np.zeros(mask.shape + (3,))
    msk_params[mask] = msk_params_flat
    msk_params[mask, 2] /= msk_params[mask, 1] ** 2

    return msk_params
