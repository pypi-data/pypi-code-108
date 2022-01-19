"""This module contains validation utility functions."""


def validate_mutually_exclusive_arguments(arguments_dict, require_one=False):
    """Validates that at least one of the passed mutually exclusive arguments is not `None`.

    Args:
        arguments_dict (collections.OrderedDict): ordered dictionary mapping argument names to values
        require_one (bool, optional): whether or not to require at least one argument to defined

    Returns:
        argument, value ((Any, Any) or None): specified argument and it's value or None if `require_one` is `False` and
            no argument was specified.

    Raises:
        ValueError: At least one of the given arguments must be specified.
        ValueError: Only one of the given arguments can be specified.
    """
    specified_arguments = [(argument, value) for argument, value in arguments_dict.items() if value is not None]

    # Create nicely formatted arguments list to use in exception messages.
    argument_names = list(arguments_dict.keys())
    formatted_arguments = ", ".join(["`{argument}`".format(argument=argument) for argument in argument_names])

    if len(specified_arguments) > 1:
        raise ValueError("Only one of {arguments} can be specified.".format(arguments=formatted_arguments))
    elif require_one:
        if not specified_arguments:
            raise ValueError("At least one of {arguments} must be specified.".format(arguments=formatted_arguments))
        else:
            return specified_arguments[0]
