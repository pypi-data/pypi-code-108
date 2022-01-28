"""Base level Actions utilities and classes."""

# Allow generics in type hints (PEP 585). This can be removed once Finesse requires at
# least Python 3.9.
from __future__ import annotations

import abc
import logging
import time
from collections import defaultdict
import finesse
from finesse.tree import TreeNode
from finesse.solutions import BaseSolution
from finesse.utilities.components import names_to_nodes


LOGGER = logging.getLogger(__name__)


def convert_str_to_parameter(model, attr):
    """Converts names `component.parameter` or `component` to a parameter object. Will
    return default parameter when component name is given.

    Parameters
    ----------
    model : Model
        Model object to look for parameter in
    attr : [str | Parameter]
        String value for the name of an element or a parameters full name. If
        a Parameter is given its full name will be used to grab the equivalent
        parameter in this Model.

    Returns
    -------
    parameter
        The equivalent Parameter object for the attr provided
    """
    if hasattr(attr, "full_name"):
        return model.get(attr.full_name)
    else:
        obj = model.get(attr)
        # If this attr string has no period in it, assume it is an element name
        # and try and get it
        if "." in attr:
            return obj
        else:
            if obj.default_parameter_name is None:
                raise ValueError(
                    f"{repr(obj)} does not have a default parameter, please specify one to use"
                )
            return getattr(obj, obj.default_parameter_name)


def request_dict_reduction(A, B):
    dd = defaultdict(list)
    for d in (A, B):
        for key, value in d.items():
            dd[key].extend(value)
    return dd


class AnalysisState(TreeNode):
    def __init__(self, model, name="AnalysisState", parent=None):
        super().__init__(f"{name} {model}", parent=parent)
        assert isinstance(model, finesse.model.Model)
        self.__model = model
        self.__sim = None
        self.__previous_solution = None
        self.model_finished_with = True
        self.__action_workspaces = {}

    @property
    def model(self):
        return self.__model

    @property
    def action_workspaces(self):
        """Actions can use their id, `id(self)`, to generate a key to store simulation
        specific data and reuse it each time run is called."""
        return self.__action_workspaces

    @property
    def sim(self):
        return self.__sim

    @property
    def previous_solution(self):
        return self.__previous_solution

    def apply(self, action):
        start = time.time_ns()
        sol = action._do(self)
        if sol is not None:
            if not isinstance(sol, BaseSolution):
                raise TypeError(
                    f"Action of type {type(action)} should return a BaseSolution derivative, not {sol}"
                )
            sol.time = (time.time_ns() - start) / 1e9
            self.__previous_solution = sol
        return sol

    def _split(self):
        state = AnalysisState(self.model.deepcopy(), parent=self)
        return state

    def build_model(self, changing_params, keep_nodes):
        if not self.model_finished_with:
            raise Exception(
                "Trying to build new model whilst current one is in use. Make sure to call `finished()` on this state if the simulation has been completed."
            )

        if self.model.is_built:
            self.finished()

        LOGGER.info(
            f"Building simulation for model {repr(self.model)}"
            f"Changing parameters = {changing_params}"
        )

        # If we do not have a simulation we need to build one
        for p in changing_params:
            p.is_tunable = True

        self.keep_nodes = tuple(names_to_nodes(self.model, keep_nodes))

        # Tell node it is being used as some sort of output so it doesn't get removed
        # TODO ddb : could refactor the naming for more generic use instead of detector
        for obj in self.keep_nodes:
            obj.used_in_detector_output.append(self)

        self.__changing_params = changing_params
        self.__sim = self.model._build()
        self.__sim.__enter__()
        self.model_finished_with = False

    def finished(self):
        if self.__sim:
            LOGGER.info(
                f"Finishing simulation {repr(self.sim)} for model {repr(self.model)}"
            )
            self.model_finished_with = True
            self.__sim.__exit__(None, None, None)
            self.model.unbuild()
            for p in self.__changing_params:
                p.is_tunable = False
            for obj in self.keep_nodes:
                obj.used_in_detector_output.remove(self)
            self.__sim = None

    def __copy__(self):
        raise Exception("Cannot copy state objects")

    def __deepcopy__(self):
        raise Exception("Cannot copy state objects")


class Action(metaclass=abc.ABCMeta):
    def __init__(self, name, analysis_state_manager=False):
        self.__name = name
        self.__analysis_state_manager = analysis_state_manager

    @property
    def name(self):
        return self.__name

    @property
    def analysis_state_manager(self):
        return self.__analysis_state_manager

    def _run(self, model, return_state=False, progress_bar=False):
        """Runs this Action on some input model and returns a solution.

        Parameters
        ----------
        model : Model
            Model to run this action on
        return_state : boolean
            If True the AnalysisState object is returned along with the solution
        progress_bar : bool, optional
            Whether to show progress bars or not

        Returns
        -------
        solution : BaseSolution
            Solution object generated by this action
        state : AnalysisState, when return_state = True
            The final state object after pasing through the action. This can be used
            to extract the models generated and tuned at later actions.
        """
        from .series import Series  # stop circular import

        before = finesse.config.show_progress_bars
        finesse.config.show_progress_bars = progress_bar

        state = AnalysisState(model)
        try:
            if not self.analysis_state_manager:
                action = Series(self)
            else:
                action = self

            result = state.apply(action)

            if type(result) is tuple:
                sol = BaseSolution("root")
                for _ in result:
                    if _ is not None:
                        sol.add(_)
            else:
                sol = result

            if type(sol) is BaseSolution and len(sol.children) == 1:
                sol = sol[0]
        finally:
            state.finished()
            finesse.config.show_progress_bars = before

        if return_state:
            return sol, state
        else:
            return sol

    @abc.abstractmethod
    def _requests(self, model, memo, first=True):
        """Updates the memo dictionary with details about what this action needs from a
        simulation to run. Parent actions will get requests from all its child actions
        so that it can build a model that suits all of them, to minimise the amount of
        building.

        This method can do initial checks to make sure the model has the
        required features to perform the action too.

        memo['changing_parameters'] - append to this list the full name string
                                      of parameters that this action needs
        memo['keep_nodes'] - append to this list the full name string
                                    of nodes that this action needs to keep.
                                    This should be used where actions are
                                    accessing node outputs without using a
                                    detector element (which registers that
                                    nodes should be kept already).

        Parameters
        ----------
        model : Model
            The Model that the action will be operating on
        memo : defaultdict(list)
            A dictionary that should be filled with requests
        first : boolean
            True if this is the first request being made
        """
        raise NotImplementedError()

    def get_requests(self, model):
        memo = defaultdict(list)
        self._requests(model, memo)
        return memo

    @abc.abstractmethod
    def _do(self, state: AnalysisState) -> BaseSolution:
        pass

    def plan(self, previous=None):
        """Returns an expected plan for the actions that will be run in a tree form.
        This may not be exactly what is ran.

        Returns
        -------
        plan : TreeNode
        """
        if previous is None:
            previous = TreeNode("start")

        me = TreeNode(self.name)
        me.empty = not self.analysis_state_manager
        previous.add(me)

        found_actions = []

        for key, value in self.__dict__.items():
            if isinstance(value, Action):
                found_actions.append(value)
            elif isinstance(value, (tuple, list, set)):
                for _ in value:
                    if isinstance(_, Action):
                        found_actions.append(_)

        for action in found_actions:
            action.plan(me)
        return previous
