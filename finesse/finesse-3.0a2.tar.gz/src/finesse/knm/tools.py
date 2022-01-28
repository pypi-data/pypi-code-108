"""Tools for calculating coupling coefficients and modal scattering matrices of
different types."""

from .bayerhelms import make_bayerhelms_matrix


# TODO (sjr) Create functions corresponding to different scattering
#            matrix types as they are implemented in the code (i.e.
#            things like aperture and map knm matrix computations)
def make_scatter_matrix(mtype, *args, **kwargs):
    """Constructs and computes a coupling coefficient scattering matrix of the specified
    type (via `mtype`).

    Parameters
    ----------
    mtype : str
        Type of scattering matrix to compute.

        The valid options are:

          - "bayerhelms" --- computes a Bayer-Helms scattering matrix,
                             see :func:`.make_bayerhelms_matrix`.

    *args : positional arguments
        The positional arguments to pass to the relevant scatter matrix function.

    **kwargs : keyword arguments
        The keyword arguments to pass to the relevant scatter matrix function.

    Returns
    -------
    kmat : :class:`.KnmMatrix`
        The resulting scattering matrix as a :class:`.KnmMatrix` object.

    Examples
    --------
    See :ref:`arbitrary_scatter_matrices`.
    """
    mtype_to_func = {"bayerhelms": make_bayerhelms_matrix}

    func = mtype_to_func.get(mtype.casefold())
    if func is None:
        raise ValueError(f"Unrecognised / not-yet-implemented mtype argument: {mtype}")

    return func(*args, **kwargs)
