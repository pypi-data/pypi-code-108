"""Serial Action."""
import finesse.config
from finesse.solutions import BaseSolution
from .base import Action, convert_str_to_parameter
import logging
from tqdm.auto import tqdm

LOGGER = logging.getLogger(__name__)


class Series(Action):
    def __init__(self, *actions, flatten=True):
        super().__init__("series", True)
        self.actions = actions
        self.flatten = flatten

    def _do(self, state):
        rq = self.get_requests(state.model)
        params = tuple(
            convert_str_to_parameter(state.model, _) for _ in rq["changing_parameters"]
        )
        if state.sim is None:
            state.build_model(params, rq["keep_nodes"])

        if self.flatten:
            first = BaseSolution(self.name)
        else:
            first = None

        curr_sol = None
        pbar = tqdm(
            self.actions,
            disable=len(self.actions) <= 1 or (not finesse.config.show_progress_bars),
            leave=False,
        )

        for action in pbar:
            pbar.set_description_str(self.name)
            next_sol = state.apply(action)
            if self.flatten and next_sol is not None:
                first.add(next_sol)
            else:
                if next_sol and not curr_sol:
                    first = next_sol  # need to return the first one
                if next_sol:
                    if curr_sol:
                        curr_sol.add(next_sol)
                    curr_sol = next_sol
        return first

    def _requests(self, model, memo, first=True):
        if not first:
            return

        for action in self.actions:
            action._requests(model, memo, False)


class For(Action):
    """An action changes a parameter value and runs a set of actions for each value in
    the array. Essentially the same as `Series` combined with `Change`. The parameter
    value is not reset to its original value once this action has finished.

    Examples
    --------
    A simple example printing some a varied laser power output.
    >>> import finesse
    >>> model = finesse.Model()
    >>> model.parse('''
    ... l l1
    ... pd P l1.p1.o
    ... ''')
    >>> model.run('for(l1.P, [0, 1, 2, 3], print(l1.P))')
    0.0 W
    1.0 W
    2.0 W
    3.0 W

    Parameters
    ----------
    param : str|Parameter
        Parameter to change in the model
    values : array_like
        Array of values to use for the parameter
    *actions : tuple(Action)
        Actions to run for each parameter value.
    """

    def __init__(self, param, values, *actions, flatten=True):
        super().__init__("for", True)
        self.param = param
        self.values = values
        self.actions = actions
        self.flatten = flatten

    def _do(self, state):
        rq = self.get_requests(state.model)
        for_param = convert_str_to_parameter(state.model, self.param)
        params = tuple(
            [
                for_param,
                *(
                    convert_str_to_parameter(state.model, _)
                    for _ in rq["changing_parameters"]
                ),
            ]
        )
        if state.sim is None:
            state.build_model(params, rq["keep_nodes"])

        if self.flatten:
            first = BaseSolution(self.name)
        else:
            first = None

        curr_sol = None
        pbar = tqdm(
            self.actions,
            disable=len(self.actions) <= 1 or (not finesse.config.show_progress_bars),
            leave=False,
        )
        for for_param.value in self.values:
            state.sim.update_all_parameter_values()
            for action in pbar:
                pbar.set_description_str(self.name)
                next_sol = state.apply(action)
                if self.flatten and next_sol is not None:
                    first.add(next_sol)
                else:
                    if next_sol and not curr_sol:
                        first = next_sol  # need to return the first one
                    if next_sol:
                        if curr_sol:
                            curr_sol.add(next_sol)
                        curr_sol = next_sol
        return first

    def _requests(self, model, memo, first=True):
        if not first:
            return

        for action in self.actions:
            action._requests(model, memo, False)
