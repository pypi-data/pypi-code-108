from __future__ import annotations

__all__ = [
    "Parameter",
    "ParameterMixin",
]

import json
import pickle
import warnings
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, List, Optional

import libsbml
from typing_extensions import Literal  # 3.7 compatability

from .basemodel import BaseModel
from .utils import convert_id_to_sbml, warning_on_one_line

warnings.formatwarning = warning_on_one_line  # type: ignore


@dataclass
class Parameter:
    """Meta-info container for parameters."""

    unit: Optional[str] = None
    annotation: Optional[str] = None
    database_links: dict = field(default_factory=dict)
    notes: dict = field(default_factory=dict)


class ParameterMixin(BaseModel):
    """Adding parameter functions."""

    def __init__(self, parameters: dict = None) -> None:
        self.parameters: Dict[str, float] = {}
        self.derived_parameters: Dict[str, Dict[str, Any]] = {}
        self._derived_from_parameters: set[str] = set()

        if parameters is not None:
            self.add_parameters(parameters=parameters)
        self.initialization_parameters = self.parameters.copy()

    ##########################################################################
    # Parameter functions
    ##########################################################################

    def add_parameter(self, parameter_name: str, parameter_value: float, **meta_info: Dict[str, Any]) -> None:
        """Add a new parameter to the model.

        Parameters
        ----------
        meta_info
            Meta info of the parameter. Allowed keys are
            {unit, database_links, notes}
        """
        self._check_and_insert_ids([parameter_name], context="add_parameter")
        self.add_and_update_parameter(parameter_name, parameter_value)
        self.meta_info.setdefault("parameters", {}).setdefault(
            parameter_name,
            Parameter(**meta_info),  # type: ignore
        )

    def add_parameters(
        self,
        parameters: Dict[str, float],
        meta_info: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add multiple parameters to the model"""
        meta_info = {} if meta_info is None else meta_info
        for parameter_name, parameter_value in parameters.items():
            info = meta_info.get(parameter_name, {})
            self.add_parameter(
                parameter_name=parameter_name,
                parameter_value=parameter_value,
                **info,
            )

    def update_parameter(self, parameter_name: str, parameter_value: float) -> None:
        """Update an existing model parameter.

        Warns
        -----
        UserWarning
            If parameter is not in the model
        """
        if parameter_name not in self.parameters:
            warnings.warn(f"Key {parameter_name} is not in the model. Adding.")
        self.add_and_update_parameter(parameter_name, parameter_value)

    def update_parameters(self, parameters: Dict[str, float]) -> None:
        """Update multiple existing model parameters.

        See Also
        --------
        update_parameter
        """
        for parameter_name, parameter_value in parameters.items():
            self.update_parameter(parameter_name=parameter_name, parameter_value=parameter_value)

    def add_and_update_parameter(
        self,
        parameter_name: str,
        parameter_value: float,
        update_derived: bool = True,
    ) -> None:
        """Add a new or update an existing parameter."""
        self.parameters[parameter_name] = parameter_value
        if parameter_name in self._derived_from_parameters and update_derived:
            self._update_derived_parameters()

    def add_and_update_parameters(self, parameters: Dict[str, float]) -> None:
        """Add new and update existing model parameters.

        See Also
        --------
        add_and_update_parameter
        """
        for parameter_name, parameter_value in parameters.items():
            self.add_and_update_parameter(parameter_name=parameter_name, parameter_value=parameter_value)

    def update_parameter_meta_info(self, parameter: str, meta_info: dict) -> None:
        """Update meta info of a parameter.

        Parameters
        ----------
        meta_info
            Meta info of the parameter. Allowed keys are
            {unit, database_links, notes}
        """
        self.update_meta_info(component="parameters", meta_info={parameter: meta_info})

    def remove_parameter(self, parameter_name: str) -> None:
        """Remove a parameter from the model."""
        del self.parameters[parameter_name]
        if parameter_name in self.meta_info:
            del self.meta_info["parameters"][parameter_name]
        self._remove_ids([parameter_name])

    def remove_parameters(self, parameter_names: Iterable[str]) -> None:
        """Remove multiple parameters from the model.

        See Also
        --------
        remove_parameter
        """
        for parameter_name in parameter_names:
            self.remove_parameter(parameter_name=parameter_name)

    def add_derived_parameter(self, parameter_name: str, function: Callable, parameters: List[str]) -> None:
        """Add a derived parameter.

        Derived parameters are calculated from other model parameters and dynamically updated
        on any changes.
        """
        # Do this first to check if all parameters are actually in the model
        # Since we also need the values to compute anything, don't use _check_for_existence here
        # that would be an unnecessary duplicate effort
        parameter_values = [self.parameters[i] for i in parameters]

        self.derived_parameters[parameter_name] = {
            "function": function,
            "parameters": parameters,
        }
        for parameter in parameters:
            self._derived_from_parameters.add(parameter)

        # Initial calculation
        self.add_parameter(
            parameter_name=parameter_name,
            parameter_value=function(*parameter_values),
        )

    def remove_derived_parameter(self, parameter_name: str) -> None:
        """Remove a derived parameter from the model."""
        old_parameter = self.derived_parameters.pop(parameter_name)
        derived_from = old_parameter["parameters"]
        for i in derived_from:
            if all(i not in j["parameters"] for j in self.derived_parameters.values()):
                self._derived_from_parameters.remove(i)
        self.remove_parameter(parameter_name=parameter_name)

    def _update_derived_parameters(self) -> None:
        """Update values of all derived parameters.

        This function is supposed to be run after a change to any parameter
        from which a derived parameter is calculated. Since this operation
        is assumed to take not a lot of time, it is run for all parameters.
        If there ever is a model with lots of derived parameters, it might
        make sense to make this a little less brute-force ;)
        """
        for parameter_name, parameter in self.derived_parameters.items():
            self.add_and_update_parameter(
                parameter_name=parameter_name,
                parameter_value=parameter["function"](*(self.parameters[i] for i in parameter["parameters"])),
                update_derived=False,
            )

    def store_parameters_to_file(
        self,
        filename: str,
        filetype: Literal["json", "pickle"] = "json",
    ) -> None:
        """Store the parameters into a json or pickle file."""
        if filetype == "json":
            if not filename.endswith(".json"):
                filename += ".json"
            with open(filename, "w") as f:
                json.dump(self.parameters, f)
        elif filetype == "pickle":
            if not filename.endswith(".p"):
                filename += ".p"
            with open(filename, "wb") as f:  # type: ignore
                pickle.dump(self.parameters, f)  # type: ignore
        else:
            raise ValueError("Can only save to json or pickle")

    def load_parameters_from_file(
        self,
        filename: str,
        filetype: Literal["json", "pickle"] = "json",
    ) -> None:
        """Load parameters from a json or pickle file."""
        if filetype == "json":
            with open(filename, "r") as f:
                self.add_and_update_parameters(parameters=json.load(f))
        elif filetype == "pickle":
            with open(filename, "rb") as f:  # type: ignore
                self.add_and_update_parameters(parameters=pickle.load(f))  # type: ignore
        else:
            raise ValueError("Can only load from json or pickle")

    def restore_initialization_parameters(self) -> None:
        """Restore parameters to initialization parameters."""
        self.parameters = self.initialization_parameters.copy()

    def get_parameter(self, parameter_name: str) -> float:
        """Return the value of a single parameter."""
        return float(self.parameters[parameter_name])

    def get_parameters(self) -> Dict[str, float]:
        """Return all parameters."""
        return dict(self.parameters)

    def get_parameter_names(self) -> List[str]:
        """Return names of all parameters"""
        return list(self.parameters)

    ##########################################################################
    # Source code functions
    ##########################################################################

    def _generate_parameters_source_code(self, *, include_meta_info: bool = True) -> str:
        """Generate modelbase source code for parameters.

        This is mainly used for the generate_model_source_code function.

        Parameters
        ----------
        include_meta_info : bool
            Whether to include the parameter meta info

        Returns
        -------
        parameter_modelbase_code : str
            Source code generating the modelbase parameters
        """
        parameters = repr(self.parameters)
        if include_meta_info:
            meta_info = self._get_nonzero_meta_info(component="parameters")
            if bool(meta_info):
                return f"m.add_parameters(parameters={parameters}, meta_info={meta_info})"
        return f"m.add_parameters(parameters={parameters})"

    ##########################################################################
    # SBML functions
    ##########################################################################

    def _create_sbml_parameters(self, *, sbml_model: libsbml.Model) -> None:
        """Create the parameters for the sbml model.

        Parameters
        ----------
        sbml_model : libsbml.Model
        """
        for parameter_id, value in self.parameters.items():
            parameter = self.meta_info["parameters"][parameter_id]
            k = sbml_model.createParameter()
            k.setId(convert_id_to_sbml(id_=parameter_id, prefix="PAR"))
            k.setConstant(True)
            k.setValue(float(value))
            unit = parameter.unit
            if unit is not None:
                k.setUnits(unit)
