"""Temporary actions allow for temporary state changes to perform some chosen set of
actions with, then returning to the original state."""

from .base import Action, convert_str_to_parameter
from ...parameter import GeometricParameter
import logging


LOGGER = logging.getLogger(__name__)


def temporary(action):
    """Converts an action into a temporary action.

    This function takes a target action, and returns an action that
    takes multiple actions as arguments. When the returned action is
    run, it will first run the target action, then all actions passed to
    it, then restore the changes made by the target action, e.g.

        temporary(Change({'m1.phi': 10}))(
            Xaxis(l1.P, 'lin', 0, 10, 100)
        )

    will first set the parameter `m1.phi` to 10, then run a sweep of
    `l1.P`, then restore `m1.phi` to its previous value.

    Parameters
    ----------
    action : Action
        The action to make temporary.

    Returns
    -------
    action
        An action that temporarily applies the passed action when run.
    """

    def func(*args, **kwargs):
        return Temporary(action, *args, **kwargs)

    return func


class Temporary(Action):
    """Make the first action in a series of actions temporary, i.e. restore its
    parameters after the rest of the actions are complete."""

    def __init__(self, temp_action, *actions):
        super().__init__("series", True)
        self.temp_action = temp_action
        self.actions = actions

    def _do(self, state):
        rq = self.temp_action.get_requests(state.model)
        params = {
            convert_str_to_parameter(state.model, p): convert_str_to_parameter(
                state.model, p
            ).value
            for p in rq["changing_parameters"]
        }

        state.apply(self.temp_action)

        curr_sol = None
        for i, action in enumerate(self.actions):
            next_sol = state.apply(action)
            if next_sol and not curr_sol:
                first = next_sol  # need to return the first one
            if next_sol:
                if curr_sol:
                    curr_sol.add(next_sol)
                curr_sol = next_sol

        for param, value in params.items():
            param.value = value
            param._reset_cvalue()

        return first

    def _requests(self, model, memo, first=True):
        self.temp_action._requests(model, memo, False)
        for action in self.actions:
            action._requests(model, memo, False)


class TemporaryParameters(Action):
    """An action that will revert any changed parameters back to their values before
    this action was called. Options exist to include or exclude certain Parameters from
    this reversion. This action does not generate any Solution.

    Parameters
    ----------
    action : :class:`Action`
        Action to perform followed by reverting requested Parameters in the model

    include : [iterable|str], optional
        Parameters that *should* be included.

        If a single string is given it can be a Unix file style wildcard (See ``fnmatch``).
        A value of None means everything is included.

        If an iterable is provided it must be a list of names or Parameter objects.

    exclude : [iterable|str], optional
        Parameters that *should not* be included.

        If a single string is given it can be a Unix file style wildcard (See ``fnmatch``).
        A value of None means nothing is excluded.

        If an iterable is provided it must be a list of names or Parameter objects.
    """

    def __init__(self, action, *, include=None, exclude=None):
        if action is None:
            raise ValueError("Action must be provided")

        super().__init__("temp_param")
        self.action = action
        self.include = include
        self.exclude = exclude

    def _do(self, state):
        params = state.sim.model.get_parameters(
            include=self.include,
            exclude=self.exclude,
            are_changing=True,
            are_symbolic=False,
        )
        initial = {p: p.value for p in params}
        # apply the action
        sol = state.apply(self.action)

        # Start resetting parameter values and updating things
        for param, prev in initial.items():
            param.value = prev
        # Ensure the __cvalue of each symbolic parameter gets reset accordingly
        for param in state.sim.changing_parameters:
            param._reset_cvalue()

        if any(
            type(p) is GeometricParameter and p.is_symbolic
            for p in state.sim.changing_parameters
        ):
            state.model._update_symbolic_abcds()

        return sol

    def _requests(self, model, memo, first=True):
        self.action._requests(model, memo)
