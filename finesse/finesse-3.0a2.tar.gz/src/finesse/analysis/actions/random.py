"""Random collection of Actions that do no warrant a separate module."""

from ...parameter import Parameter
from .base import Action, convert_str_to_parameter
from finesse.solutions import BaseSolution

import logging

LOGGER = logging.getLogger(__name__)


class SaveModelAttrSolution(BaseSolution):
    """
    Attributes
    ----------
    values : dict
        Dictionary of model attribute values
    """

    pass


class Plot(Action):
    def __init__(self, name="abcd"):
        super().__init__(name)

    def _requests(self, model, memo, first=True):
        pass

    def _do(self, state):
        raise NotImplementedError()


class Printer(Action):
    def __init__(self, *args, name="printer"):
        super().__init__(name)
        self.args = args

    def _requests(self, model, memo, first=True):
        pass

    def _do(self, state):
        print(*(f"{_}" for _ in self.args))


class PrintModel(Action):
    def __init__(self, name="print_model"):
        super().__init__(name)

    def _requests(self, model, memo, first=True):
        pass

    def _do(self, state):
        print(state.model)


class StoreModelAttr(Action):
    def __init__(self, *args):
        super().__init__(self.__class__.__name__)
        self.args = tuple(a if isinstance(a, str) else a.full_name for a in args)

    def _requests(self, model, memo, first=True):
        pass

    def _do(self, state):
        sol = SaveModelAttrSolution(self.name)
        sol.values = {}
        for _ in self.args:
            p = state.model.get(_)
            if hasattr(p, "eval"):
                sol.values[_] = p.eval()
            else:
                sol.values[_] = p
        return sol


class PrintModelAttr(Action):
    def __init__(self, *args):
        super().__init__(self.__class__.__name__)
        self.args = tuple(a if isinstance(a, str) else a.full_name for a in args)

    def _requests(self, model, memo, first=True):
        pass

    def _do(self, state):
        print(*(f"{_}={state.model.get(_)}" for _ in self.args))


class Change(Action):
    """Changes a model Parameter to some value during an analysis."""

    def __init__(self, change_dict=None, *, relative=False, **kwargs):
        super().__init__(None)
        self.change_dict = change_dict
        self.kwargs = kwargs
        self.relative = relative

    @property
    def change_kwargs(self):
        kwargs = self.kwargs or {}
        if self.change_dict:
            kwargs.update(self.change_dict)
        return kwargs

    def _requests(self, model, memo, first=True):
        for el in self.change_kwargs.keys():
            p = convert_str_to_parameter(model, el)
            if isinstance(p, Parameter):
                memo["changing_parameters"].append(el)
            else:
                raise TypeError(
                    f"{el} is not a name of a Parameter or Component in the model"
                )

    def _do(self, state):
        for el, val in self.change_kwargs.items():
            p = convert_str_to_parameter(state.model, el)
            if self.relative:
                p.value += val
            else:
                p.value = val


class Exec(Action):
    """An action that will execute the function passed to it when it is run.

    Parameters
    ----------
    name : str
        The name to give this action.

    do_fn : function
        A function that takes an AnalysisState as its only argument

    parameters : list, optional
        A list of parameters that will be changed by do_fn, if any.
    """

    def __init__(self, name, do_fn, parameters=None):
        super().__init__(name)
        self.do_fn = do_fn
        self.parameters = parameters

    def _do(self, state):
        self.do_fn(state)

    def _requests(self, model, memo, first=True):
        if self.parameters is not None:
            memo["changing_parameters"].extend(self.parameters)


class UpdateMaps(Action):
    """Update any maps that might be changing in the simulation."""

    def __init__(self, name="update_maps", *args, **kwargs):
        super().__init__(name)
        self.args = args
        self.kwargs = kwargs

    def _requests(self, model, memo, first=True):
        return None

    def _do(self, state):
        state.sim.update_map_data()


class LogModelAttribute(Action):
    def __init__(self, *attrs):
        super().__init__("print_parmeter")
        self.attrs = attrs

    def _requests(self, model, memo, first=True):
        pass

    def _do(self, state):
        LOGGER.info(*(f"{_}={state.model.get(str(_))}" for _ in self.attrs))


class Scale(Action):
    """Action for scaling simulation outputs by some fixed amount. Included for
    compatibility with legacy Finesse code. New users should apply any desired scalings
    manually from Python.

    Parameters
    ----------
    detectors : dict
        A dictionary of `detector name: scaling factor` mappings.
    """

    def __init__(self, scales: dict, **kwargs):
        super().__init__(None)
        self.kwargs = kwargs
        self.scales = scales

    def _requests(self, model, memo, first=True):
        pass

    def _do(self, state):
        sol = state.previous_solution
        for det, fac in self.scales.items():
            sol._outputs[det][()] *= fac


class MakeTransparent(Action):
    """Action to make all provided surfaces transparent. Simply sets the reflectivity to
    zero and transmitivity to one.

    Parameters
    ----------
    surfaces : list
        A list of surface component names to be made transparent.
    """

    def __init__(self, surfaces, name="make transparent"):
        super().__init__(name)
        self.surfaces = surfaces

    def _do(self, state):
        for name, el in state.sim.model.elements.items():
            if name in self.surfaces:
                el.set_RTL(R=0, T=1)

    def _requests(self, model, memo, first=True):
        for name, el in model.elements.items():
            if name in self.surfaces:
                memo["changing_parameters"].extend(
                    [el.R.full_name, el.T.full_name, el.L.full_name]
                )
