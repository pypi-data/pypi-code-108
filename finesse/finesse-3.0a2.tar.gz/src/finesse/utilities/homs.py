"""Functions for manipulating Higher Order Modes."""

import logging
import numbers

import numpy as np

from ..env import warn
from ..exceptions import ContextualValueError


LOGGER = logging.getLogger(__name__)


def make_modes(select=None, maxtem=None):
    """Construct a 2D :class:`numpy.ndarray` of HOM indices.

    Parameters
    ----------
    select : sequence, str, optional; default: None
        Identifier for the mode indices to generate. This can be:

        - An iterable of mode indices, where each element in the iterable
          must unpack to two integer convertible values.
        - A string identifying the type of modes to include, must be
          one of "even", "odd", "tangential" (or "x") or "sagittal" (or "y").

    maxtem : int, optional; default: None
        Optional maximum mode order, applicable only for when `select` is
        a string. This is ignored if `select` is not a string.

    Returns
    -------
    modes : :class:`numpy.ndarray`
        An array of mode indices.

    Raises
    ------
    ValueError
        If either of the arguments `select`, `maxtem` are invalid or non-unique.

    See Also
    --------
    insert_modes : Add modes to an existing mode indices array at the correct positions.

    Examples
    --------

    Modes up to a maximum order of 2:

    >>> make_modes(maxtem=2)
    array([[0, 0], [0, 1], [0, 2], [1, 0], [1, 1], [2, 0]], dtype=int32)

    Even modes up to order 4:

    >>> make_modes("even", maxtem=4)
    array([[0, 0], [0, 2], [0, 4], [2, 0], [2, 2], [4, 0]], dtype=int32)

    Sagittal modes up to order 3:

    >>> make_modes("y", maxtem=3)
    array([[0, 0], [0, 1], [0, 2], [0, 3]], dtype=int32)

    Modes from a list of strings:

    >>> make_modes(["00", "11", "22"])
    array([[0, 0], [1, 1], [2, 2]], dtype=int32)
    """
    if select is None and maxtem is None:
        raise ContextualValueError(
            {
                "select": ContextualValueError.empty,
                "maxtem": ContextualValueError.empty,
            },
            "cannot both be empty",
        )

    if select is None:
        _check_maxtem(maxtem)

        limit = 1 + int(maxtem)
        N = int(limit * (1 + limit) / 2)
        modes = np.zeros(N, dtype=(np.intc, 2))
        count = 0
        for i in range(0, limit):
            for j in range(0, i + 1):
                modes[count] = (i - j, j)
                count += 1

    elif isinstance(select, str):
        switch = {
            "even": _make_even_modes,
            "odd": _make_odd_modes,
            "tangential": _make_tangential_modes,
            "sagittal": _make_sagittal_modes,
            "x": _make_tangential_modes,
            "y": _make_sagittal_modes,
        }

        if select.casefold() not in switch:
            msg = f"""
            Mode arument (= {select}) not recognised as a valid identifier. It must be:

    - "even" for generating even modes up to the given maxtem,
    - "odd" for generating odd modes up to the given maxtem,
    - "tangential" or "x" for generating tangential modes up to maxtem,
    - or "sagittal" or "y" for generating sagittal modes up to maxtem.
            """
            raise ValueError(msg.strip())

        modes = switch[select.casefold()](maxtem)

    else:
        if maxtem is not None:
            warn(
                "Ignoring maxtem argument given to make_modes as an iterable has "
                "already been provided."
            )

        modes = np.zeros(len(select), dtype=(np.intc, 2))
        for i, mode in enumerate(select):
            try:
                mode = list(mode)
            except TypeError:
                raise ValueError("Expected mode list to be a two-dimensional list")

            if len(mode) != 2:
                msg = (
                    f"Expected element {mode} of mode list to be an iterable of "
                    f"length 2 but instead got an iterable of size {len(mode)}."
                )
                raise ValueError(msg)

            try:
                n, m = mode
                n = int(n)
                m = int(m)

                if n < 0 or m < 0:
                    raise ValueError()

                modes[i] = (n, m)
            except (TypeError, ValueError):
                msg = (
                    f"Expected n (= {n}) and m (= {m}) of element {mode} "
                    f"of mode list to be convertible to non-negative integers."
                )
                raise TypeError(msg)

    (_, counts) = np.unique(modes, axis=0, return_counts=True)
    if np.any(counts > 1):
        raise ValueError(f"Mode array has non-unique values: {modes}")

    return modes


def _make_even_modes(maxtem):
    all_modes = make_modes(maxtem=maxtem)

    return np.array([(n, m) for n, m in all_modes if not n % 2 and not m % 2])


def _make_odd_modes(maxtem):
    all_modes = make_modes(maxtem=maxtem)

    return np.array(
        [(n, m) for n, m in all_modes if (n % 2 or not n) and (m % 2 or not m)]
    )


def _make_tangential_modes(maxtem):
    _check_maxtem(maxtem)

    N = 1 + maxtem
    modes = np.zeros(N, dtype=(np.intc, 2))

    for n in range(N):
        modes[n] = (n, 0)

    return modes


def _make_sagittal_modes(maxtem):
    _check_maxtem(maxtem)

    N = 1 + maxtem
    modes = np.zeros(N, dtype=(np.intc, 2))

    for m in range(N):
        modes[m] = (0, m)

    return modes


def insert_modes(modes, new_modes):
    """Inserts the mode indices in `new_modes` into the `modes` array at the correct
    (sorted) position(s).

    Parameters
    ----------
    modes : :class:`numpy.ndarray`
        An array of HOM indices.

    new_modes : sequence, str
        A single mode index pair or an iterable of mode indices. Each
        element must unpack to two integer convertible values.

    Returns
    -------
    out : :class:`numpy.ndarray`
        A sorted array of HOM indices consisting of the original contents
        of `modes` with the mode indices from `new_modes` included.

    Raises
    ------
    ValueError
        If `new_modes` is not a mode index pair or iterable of mode indices.

    See Also
    --------
    make_modes

    Examples
    --------
    Make an array of even modes and insert new modes into this:

    >>> modes = make_modes("even", 2)
    >>> modes
    array([[0, 0], [0, 2], [2, 0]], dtype=int32)
    >>> insert_modes(modes, ["11", "32"])
    array([[0, 0], [0, 2], [1, 1], [2, 0], [3, 2]], dtype=int32)
    """
    if not hasattr(new_modes, "__getitem__"):
        raise ValueError(
            "Argument 'new_modes' must be a single mode index pair "
            "or an iterable of mode index pairs."
        )
    if not hasattr(new_modes[0], "__getitem__") or isinstance(new_modes, str):
        new_modes = [new_modes]

    new = np.array([(int(n), int(m)) for n, m in new_modes], dtype=np.intc)
    return np.unique(np.vstack((modes, new)), axis=0)


def remove_modes(modes, remove):
    if not hasattr(remove, "__getitem__"):
        raise ValueError(
            "Argument remove must be a single mode index pair "
            "or an iterable of mode index pairs."
        )
    if not hasattr(remove[0], "__getitem__") or isinstance(remove, str):
        remove = [remove]

    for n, m in remove:
        ni = int(n)
        mi = int(m)
        index = np.where(np.bitwise_and(modes[:, 0] == ni, modes[:, 1] == mi))
        modes = np.delete(modes, index, axis=0)

    return modes


def surface_diopt_to_roc(roc, d):
    """Convert a dioptre shift, at a surface, to a radius of curvature.

    Parameters
    ----------
    roc : float
        The initial radius of curvature of the surface.

    d : float, array-like
        A value or array of values representing the dioptre shift.

    Returns
    -------
    out : float, array-like
        The new values of the radius of curvature.
    """
    return 2 / (d + 2 / roc)


def lens_diopt_to_f(f, d):
    """Convert a dioptre shift, at a lens, to a focal length.

    Parameters
    ----------
    f : float
        The initial focal length of the lens.

    d : float, array-like
        A value or array of values representing the dioptre shift.

    Returns
    -------
    out : float, array-like
        The new value(s) of the focal length.
    """
    return 1 / (d + 1 / f)


def _check_maxtem(maxtem):
    if (
        not isinstance(maxtem, numbers.Number)
        or maxtem < 0
        or (
            hasattr(maxtem, "is_integer")
            and not maxtem.is_integer()
            and not isinstance(maxtem, numbers.Integral)
        )
    ):
        raise ValueError("Argument maxtem must be a non-negative integer.")
