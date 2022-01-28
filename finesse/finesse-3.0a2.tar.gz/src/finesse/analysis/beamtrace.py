"""Tasks involving tracing beams and computing ABCD matrices."""

import logging
from .actions import ABCD, BeamTrace, PropagateBeam, PropagateAstigmaticBeam

LOGGER = logging.getLogger(__name__)


def abcd(model, **kwargs):
    """Executes a :class:`.ABCD` analysis on a model.

    Other Parameters
    ----------------
    **kwargs
        Arguments to pass to the ABCD routine. See :meth:`~.Model.ABCD` for the available options.

    Returns
    -------
    out : :class:`.ABCDSolution`
        The solution object for the ABCD matrix calculation.
    """
    analysis = ABCD(**kwargs)
    return model.run(analysis)


def beam_trace(model, **kwargs):
    """Executes a :class:`.BeamTrace` analysis on a model.

    Other Parameters
    ----------------
    **kwargs
        Arguments to pass to the beam trace routine. See :meth:`.Model.beam_trace` for the
        available options.

    Returns
    -------
    out : :class:`.BeamTraceSolution`
        The solution object for the model beam trace.
    """
    analysis = BeamTrace(**kwargs)
    return model.run(analysis)


def propagate_beam(model, **kwargs):
    """Executes a :class:`.PropagateBeam` analysis on a model.

    Other Parameters
    ----------------
    **kwargs
        Arguments to pass to the routine. See :meth:`.Model.propagate_beam` for the
        available options.

    Returns
    -------
    out : :class:`.BeamTraceSolution`
        The solution object for the single plane beam propagation.
    """
    analysis = PropagateBeam(**kwargs)
    return model.run(analysis)


def propagate_beam_astig(model, **kwargs):
    """Executes a :class:`.PropagateAstigmaticBeam` analysis on a model.

    Other Parameters
    ----------------
    **kwargs
        Arguments to pass to the routine. See :meth:`.Model.propagate_beam_astig` for the
        available options.

    Returns
    -------
    out : :class:`.BeamTraceSolution`
        The solution object for the astigmatic beam propagation.
    """
    analysis = PropagateAstigmaticBeam(**kwargs)
    return model.run(analysis)
