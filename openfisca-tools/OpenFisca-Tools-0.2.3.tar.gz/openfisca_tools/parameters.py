from openfisca_core.parameters import ParameterNode, Parameter
from openfisca_core.parameters.parameter_at_instant import ParameterAtInstant
from openfisca_core.periods import instant
from numpy import ceil, floor
from openfisca_tools.reforms import get_parameter


def interpolate_parameters(root: ParameterNode) -> ParameterNode:
    """Interpolates parameters according to their metadata.

    Args:
        root (ParameterNode): The root of the parameter tree.

    Returns:
        ParameterNode: The same root, with interpolation applied to descendants.
    """
    for parameter in root.get_descendants():
        if isinstance(parameter, Parameter):
            if "interpolation" in parameter.metadata:
                interpolated_entries = []
                for i in range(len(parameter.values_list) - 1):
                    # For each gap in parameter values
                    start = instant(parameter.values_list[::-1][i].instant_str)
                    num_intervals = 1
                    # Find the number of intervals to fill
                    interval_size = parameter.metadata["interpolation"][
                        "interval"
                    ]
                    parameter_dates = [
                        at_instant.instant_str
                        for at_instant in parameter.values_list
                    ]
                    while (
                        str(start.offset(num_intervals, interval_size))
                        not in parameter_dates
                    ):
                        num_intervals += 1
                    # Interpolate in each interval
                    for j in range(1, num_intervals):
                        start_str = str(
                            start.offset(
                                j,
                                parameter.metadata["interpolation"][
                                    "interval"
                                ],
                            )
                        )
                        start_value = parameter.values_list[::-1][i].value
                        end_value = parameter.values_list[::-1][i + 1].value
                        new_value = (
                            start_value
                            + (end_value - start_value) * j / num_intervals
                        )
                        interpolated_entries += [
                            ParameterAtInstant(
                                parameter.name, start_str, data=new_value
                            )
                        ]
                for entry in interpolated_entries:
                    parameter.values_list.append(entry)
                parameter.values_list.sort(
                    key=lambda x: x.instant_str, reverse=True
                )
    return root


def uprate_parameters(root: ParameterNode) -> ParameterNode:
    """Uprates parameters according to their metadata.

    Args:
        root (ParameterNode): The root of the parameter tree.

    Returns:
        ParameterNode: The same root, with uprating applied to descendants.
    """

    for parameter in root.get_descendants():
        if isinstance(parameter, Parameter):
            if "uprating" in parameter.metadata:
                uprating_parameter = get_parameter(
                    root, parameter.metadata["uprating"]["parameter"]
                )
                # Start from the latest value
                last_instant = instant(parameter.values_list[0].instant_str)
                # For each defined instant in the uprating parameter
                for entry in uprating_parameter.values_list[::-1]:
                    entry_instant = instant(entry.instant_str)
                    # If the uprater instant is defined after the last parameter instant
                    if entry_instant > last_instant:
                        # Apply the uprater and add to the parameter
                        value_at_start = parameter(last_instant)
                        uprater_at_start = uprating_parameter(last_instant)
                        uprater_at_entry = uprating_parameter(entry_instant)
                        uprated_value = (
                            value_at_start
                            * uprater_at_entry
                            / uprater_at_start
                        )
                        if "rounding" in parameter.metadata["uprating"]:
                            rounding_config = parameter.metadata["uprating"][
                                "rounding"
                            ]
                            if isinstance(rounding_config, float):
                                interval = rounding_config
                                rounding_fn = round
                            elif isinstance(rounding_config, dict):
                                interval = rounding_config["interval"]
                                rounding_fn = dict(
                                    nearest=round,
                                    upwards=ceil,
                                    downwards=floor,
                                )[rounding_config["type"]]
                            uprated_value = (
                                rounding_fn(uprated_value / interval)
                                * interval
                            )
                        parameter.values_list.append(
                            ParameterAtInstant(
                                parameter.name,
                                entry.instant_str,
                                data=uprated_value,
                            )
                        )
                parameter.values_list.sort(
                    key=lambda x: x.instant_str, reverse=True
                )
    return root
