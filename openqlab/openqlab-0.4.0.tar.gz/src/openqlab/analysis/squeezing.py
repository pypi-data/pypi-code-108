"""Simple squeezing calculations."""

import logging
from typing import Union

import numpy as np

from openqlab.conversion import db

log = logging.getLogger(__name__)


try:
    from uncertainties import ufloat, umath, core

    _DATA_TYPES = Union[float, list, np.ndarray, ufloat]
    UNCERTAINTIES = True
    log.info("uncertainties imported")
except ImportError:
    _DATA_TYPES = Union[float, list, np.array]  # type: ignore
    UNCERTAINTIES = False
    log.info("uncertainties not imported")


def losses(sqz: _DATA_TYPES, anti_sqz: _DATA_TYPES):
    """Calculate losses from known squeezing and anti-squeezing levels.

    Parameters
    ----------
    sqz : float, :obj:`numpy.array`
        The squeezing level (negative value, because it is below vacuum).
    anti_sqz : float, :obj:`numpy.array`
        The anti-squeezing level (positive value, because it is above vacuum).
    """
    sqz = _ensure_np_array(sqz)
    anti_sqz = _ensure_np_array(anti_sqz)

    L = (1 - db.to_lin(sqz) * db.to_lin(anti_sqz)) / (
        2 - db.to_lin(sqz) - db.to_lin(anti_sqz)
    )
    return L


def initial(sqz: _DATA_TYPES, anti_sqz: _DATA_TYPES):
    """Calculate the initial squeezing level from known squeezing and anti-squeezing levels.

    Parameters
    ----------
    sqz : float, :obj:`numpy.array`
        The squeezing level (negative value, because it is below vacuum).
    anti_sqz : float, :obj:`numpy.array`
        The anti-squeezing level (positive value, because it is above vacuum).
    """
    log.debug(f"UNCERTAINTIES: {UNCERTAINTIES}")
    if (
        UNCERTAINTIES
        and isinstance(sqz, (core.Variable, core.AffineScalarFunc))
        and isinstance(anti_sqz, (core.Variable, core.AffineScalarFunc))
    ):
        log10 = umath.log10  # pylint: disable=no-member
        log.debug("umath.log10")
    else:
        log10 = np.log10
        log.debug("np.log10")

    sqz = _ensure_np_array(sqz)
    anti_sqz = _ensure_np_array(anti_sqz)

    L = losses(sqz, anti_sqz)
    initial_sqz = 10 * log10((db.to_lin(anti_sqz) - L) / (1 - L))
    return initial_sqz


def max(loss: _DATA_TYPES, initial: _DATA_TYPES = -20, antisqz: bool = False):
    """Calculate the maximum possible squeezing level with given loss.

    Parameters
    ----------
    loss : float, :obj:`numpy.array`
        Level of losses (number, relative to 1).
    initial : float, :obj:`numpy.array`
        Initial squeezing level.
    antisqz : bool
        Include antisqueezing in the result: [sqz, antisqz]
        or as list of arrays, if loss is an array.
    """
    loss = _ensure_np_array(loss)
    initial = _ensure_np_array(initial)

    if initial > 0:
        raise ValueError("initial should be <= 0.")

    sqz = db.from_lin(db.to_lin(initial) * (1 - loss) + loss)

    if antisqz:
        antisqz_ = db.from_lin(db.to_lin(-initial) * (1 - loss) + loss)
        return [sqz, antisqz_]
    else:
        return sqz


def _ensure_np_array(value):
    if isinstance(value, list):
        return np.asarray(value)
    return value
