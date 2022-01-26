from openfisca_core.model_api import (
    DAY,
    MONTH,
    YEAR,
    ETERNITY,
    Variable as CoreVariable,
    Reform,
    max_,
    min_,
)
from typing import Callable, Tuple, Type, Union
import numpy as np

ReformType = Union[Reform, Tuple[Reform]]

allowed_variable_attributes = ("metadata", "quantity_type")

STOCK = "Stock"
FLOW = "Flow"


class Variable(CoreVariable):
    quantity_type: str = FLOW

    def __init__(self, baseline_variable=None):
        try:
            CoreVariable.__init__(self, baseline_variable=baseline_variable)
        except ValueError as e:
            if all(
                [
                    attribute not in str(e)
                    for attribute in allowed_variable_attributes
                ]
            ):
                raise e

        self.is_neutralized = False


np.random.seed(0)


def add(entity, period, variable_names, options=None):
    """Sums a list of variables over entities.

    Args:
        entity (Entity): Either person, benunit or household
        period (Period): The period to calculate over
        variable_names (list): A list of variable names
        options (list, optional): The options to use - ADD, DIVIDE or MATCH to define period mismatch behaviour. Defaults to None.

    Returns:
        Array: Array of entity values.
    """
    return sum(
        map(lambda var: entity(var, period, options=options), variable_names)
    )


def aggr(entity, period, variable_names, options=None):
    """Sums a list of variables over each member of a group.

    Args:
        entity (Entity): Either benunit or household
        period (Period): The period to calculate over
        variable_names (list): A list of variable names
        options (list, optional): The options to use - ADD, DIVIDE or MATCH to define period mismatch behaviour. Defaults to None.

    Returns:
        Array: Array of entity values.
    """
    return sum(
        map(
            lambda var: entity.sum(
                entity.members(var, period, options=options)
            ),
            variable_names,
        )
    )


def aggr_max(entity, period, variable_names, options=None):
    """Finds the maximum of a list of variables over each member of a group.

    Args:
        entity (Entity): Either benunit or household
        period (Period): The period to calculate over
        variable_names (list): A list of variable names
        options (list, optional): The options to use - ADD, DIVIDE or MATCH to define period mismatch behaviour. Defaults to None.

    Returns:
        Array: Array of entity values.
    """
    return sum(
        map(
            lambda var: entity.max(
                entity.members(var, period, options=options)
            ),
            variable_names,
        )
    )


def select(conditions, choices):
    """Selects the corresponding choice for the first matching condition in a list.

    Args:
        conditions (list): A list of boolean arrays
        choices (list): A list of arrays

    Returns:
        Array: Array of values
    """
    return np.select(conditions, choices)


clip = np.clip
inf = np.inf

WEEKS_IN_YEAR = 52
MONTHS_IN_YEAR = 12


def amount_over(amount, threshold):
    return max_(0, amount - threshold)


def amount_between(amount, threshold_1, threshold_2):
    return clip(amount, threshold_1, threshold_2) - threshold_1


def random(entity, reset=True):
    x = np.random.rand(entity.count)
    if reset:
        np.random.seed(0)
    return x


def is_in(values, *targets):
    return sum(map(lambda target: values == target, targets))


def uprated(by: str = None, start_year: int = 2015) -> Callable:
    """Attaches a formula applying an uprating factor to input variables (going back as far as 2015).

    Args:
        by (str, optional): The name of the parameter (under parameters.uprating). Defaults to None (no uprating applied).

    Returns:
        Callable: A class decorator.
    """

    def uprater(variable: Type[Variable]) -> type:
        if hasattr(variable, f"formula_{start_year}"):
            return variable

        formula = variable.formula if hasattr(variable, "formula") else None

        def formula_start_year(entity, period, parameters):
            if by is None:
                return entity(variable.__name__, period.last_year)
            else:
                uprating = (
                    parameters(period).uprating[by]
                    / parameters(period.last_year).uprating[by]
                )
                old = entity(variable.__name__, period.last_year)
                if (formula is not None) and (all(old) == 0):
                    # If no values have been inputted, don't uprate and
                    # instead use the previous formula on the current period.
                    return formula(entity, period, parameters)
                return uprating * old

        formula_start_year.__name__ = f"formula_{start_year}"
        setattr(variable, formula_start_year.__name__, formula_start_year)
        return variable

    return uprater


def carried_over(variable: type) -> type:
    return uprated()(variable)
