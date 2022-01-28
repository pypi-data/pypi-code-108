"""Parallel Action."""

from finesse.solutions import BaseSolution
from .base import Action, convert_str_to_parameter
import logging

LOGGER = logging.getLogger(__name__)


class ParallelSolution(BaseSolution):
    pass


class Parallel(Action):
    def __init__(self, *actions):
        super().__init__("parallel", True)
        self.actions = actions

    def _do(self, state):
        sols = ParallelSolution("parallel")
        for action in self.actions:
            # Need to loop through all the actions that we want to run
            # And build new states to feed into them.
            newstate = state._split()
            if not action.analysis_state_manager:
                # If the next action is managing the state then it should either
                # be building a simulation or passing the state on to something that
                # does. If the next action isn't, like an Xaxis, we should build it
                # so that it can work with it.
                rq = action.get_requests(newstate.model)
                params = tuple(
                    convert_str_to_parameter(newstate.model, _)
                    for _ in rq["changing_parameters"]
                )
                newstate.build_model(params, rq["keep_nodes"])
            sol = newstate.apply(action)
            if sol is not None:
                sols.add(sol)

        return sols

    def _requests(self, model, memo, first=True):
        # Parallel by it's nature has to deepcopy the model
        # that has been passed into it, otherwise there will
        # be all sort of clashes that will be hard to resolve.
        pass
