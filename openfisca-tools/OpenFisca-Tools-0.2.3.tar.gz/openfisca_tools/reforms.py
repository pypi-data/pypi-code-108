"""
Utility functions for writing reforms.
"""
from pathlib import Path
from typing import Type
from openfisca_core.parameters.helpers import load_parameter_file
from openfisca_core.parameters.parameter import Parameter
from openfisca_core.parameters.parameter_scale import ParameterScale
from openfisca_core.reforms.reform import Reform
from openfisca_core.tracers.tracing_parameter_node_at_instant import (
    ParameterNode,
)
from openfisca_core.variables import Variable
from datetime import datetime

DATE = datetime.now()
YEAR, MONTH, DAY = DATE.year, DATE.month, DATE.day
CURRENT_INSTANT = DATE.strftime("%Y-%m-%d")


def restructure(variable: Type[Variable]) -> Reform:
    """Generates a structural reform.

    Args:
        variable (Type[Variable]): The class definition of a variable to replace.

    Returns:
        Reform: The reform object.
    """
    return type(
        variable.__name__,
        (Reform,),
        dict(apply=lambda self: self.update_variable(variable)),
    )


new_variable = restructure


def abolish(variable: str) -> Reform:
    return type(
        f"abolish_{variable}",
        (Reform,),
        dict(apply=lambda self: self.neutralize_variable(variable)),
    )


def get_parameter(root: ParameterNode, parameter: str) -> Parameter:
    """Gets a parameter from the tree.

    Args:
        root (ParameterNode): The root of the parameter tree.
        parameter (str): The name of the parameter to get.

    Returns:
        Parameter: The parameter.
    """
    node = root
    for name in parameter.split("."):
        try:
            if "[" not in name:
                node = node.children[name]
            else:
                try:
                    name, index = name.split("[")
                    index = int(index[:-1])
                    node = node.children[name].brackets[index]
                except:
                    raise ValueError(
                        "Invalid bracket syntax (should be e.g. tax.brackets[3].rate"
                    )
        except:
            raise ValueError(
                f"Could not find the parameter (failed at {name})."
            )
    return node


def set_parameter(
    parameter: str, value: float, period: str = "year:2015:10"
) -> Reform:
    """Generates a parametric reform.

    Args:
        parameter (str): The name of the parameter, e.g. tax.income_tax.rate.
        value (float): The value to set as the parameter value.
        period (str): The time period to set it for. Defaults to a ten-year period from 2015 to 2025.

    Returns:
        Reform: The reform object.
    """

    def modifier_fn(parameters: ParameterNode):
        node = get_parameter(parameters, parameter)
        node.update(period=period, value=value)
        return parameters

    return type(
        parameter,
        (Reform,),
        dict(apply=lambda self: self.modify_parameters(modifier_fn)),
    )


def add_parameter_file(path: str) -> Reform:
    """Generates a reform adding a parameter file to the tree.

    Args:
        path (str): The path to the parameter YAML file.

    Returns:
        Reform: The Reform adding the parameters.
    """

    def modify_parameters(parameters: ParameterNode):
        file_path = Path(path)
        reform_parameters_subtree = load_parameter_file(file_path)
        parameters.add_child("reforms", reform_parameters_subtree.reforms)
        return parameters

    class reform(Reform):
        def apply(self):
            self.modify_parameters(modify_parameters)

    return reform


def use_current_parameters(date: str = CURRENT_INSTANT) -> Reform:
    """Backdates parameters at a given instant to the start of the year.

    Args:
        date (str, optional): The given instant. Defaults to CURRENT_INSTANT.

    Returns:
        Reform: The reform backdating parameters.
    """

    def modify_parameters(parameters: ParameterNode):
        for child in parameters.get_descendants():
            if isinstance(child, Parameter):
                current_value = child(date)
                child.update(period=f"year:{YEAR-10}:20", value=current_value)
            elif isinstance(child, ParameterScale):
                for bracket in child.brackets:
                    if "rate" in bracket.children:
                        current_rate = bracket.rate(date)
                        bracket.rate.update(
                            period=f"year:{YEAR-10}:20", value=current_rate
                        )
                    if "threshold" in bracket.children:
                        current_threshold = bracket.threshold(date)
                        bracket.threshold.update(
                            period=f"year:{YEAR-10}:20",
                            value=current_threshold,
                        )
        return parameters

    class reform(Reform):
        def apply(self):
            self.modify_parameters(modify_parameters)

    return reform
