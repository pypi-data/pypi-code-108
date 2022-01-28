"""Collection of Actions that involve beam tracing."""

from .base import Action

import logging

LOGGER = logging.getLogger(__name__)


class ABCD(Action):
    """Computation of an ABCD matrix over a path.

    See :func:`.compute_abcd` for details.
    """

    def __init__(self, name="abcd", **kwargs):
        super().__init__(name)
        self.kwargs = kwargs

    def _requests(self, model, memo, first=True):
        pass

    def _do(self, state):
        return state.model.ABCD(solution_name=self.name, **self.kwargs)


class BeamTrace(Action):
    """Full beam tracing on a complete model.

    See :meth:`.Model.beam_trace` for details.
    """

    def __init__(self, name="beam_trace", **kwargs):
        super().__init__(name)
        self.kwargs = kwargs

    def _requests(self, model, memo, first=True):
        pass

    def _do(self, state):
        return state.model.beam_trace(solution_name=self.name, **self.kwargs)


class PropagateBeam(Action):
    """Propagation of a beam, in a single plane, through a given path.

    See :meth:`.Model.propagate_beam` for details.
    """

    def __init__(self, name="propagation", **kwargs):
        super().__init__(name)
        self.kwargs = kwargs

    def _requests(self, model, memo, first=True):
        pass

    def _do(self, state):
        return state.model.propagate_beam(solution_name=self.name, **self.kwargs)


class PropagateAstigmaticBeam(Action):
    """Propagation of a beam, in both planes, through a given path.

    See :meth:`.Model.propagate_beam_astig` for details.
    """

    def __init__(self, name="astig_propagation", **kwargs):
        super().__init__(name)
        self.kwargs = kwargs

    def _requests(self, model, memo, first=True):
        pass

    def _do(self, state):
        return state.model.propagate_beam_astig(solution_name=self.name, **self.kwargs)
