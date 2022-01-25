"""
Various utilities.
"""
import importlib
import inspect


def valueize(s: str):
    try:
        return float(s)
    except:
        return s


def parse_verb_and_args(verb_and_args: str):
    """
    Parse a general purpose specification consisting of a verb, positional arguments, and named arguments.
    :param verb_and_args:   VERB:POSITIONAL_ARGUMENT:NAME=NAMED_ARGUMENT
    :return:   A tuple with the verb, args and kwargs.
    """
    parts = verb_and_args.split(":")
    args = []
    kwargs = {}
    for arg in parts[1:]:
        arg_parts = arg.split('=', maxsplit=1)
        if len(arg_parts) == 1:
            args.append(valueize(arg))
        else:
            kwargs[arg_parts[0]] = valueize(arg_parts[1])
    return parts[0], tuple(args), kwargs


def instantiate_class_and_args(class_and_args: str, required_type=None):
    """
    Instantiate a class of a given type, given a string specifying a class name and constructor arguments.

    See parse_verb_and_args() for format explanation.

    :param class_and_args:      PACKAGE.CLASS:ARG:NAME=ARG
    :param required_type:       A type, or list of types which must be matched.
    :return:                An instance of the specified class.
    """
    cls_name, args, kwargs = parse_verb_and_args(class_and_args)
    try:
        cls = import_named_object(cls_name)
        if required_type and not issubclass(cls, required_type):
            raise ValueError(f"Specified class {cls_name} is not {required_type}")
        return cls(*args, **kwargs)
    except ImportError:
        raise ValueError(f"Specified class {cls_name} was not found")


def import_named_object(package_and_object: str):
    """
    Import a class or method based on a string giving a package, module and attribute name delimited by '.'.
    :param package_and_object:   PACKAGE.MODULE.NAME
    :return:    Method imported from the indicated module.
    """
    parts = package_and_object.split(".")
    module = importlib.import_module('.'.join(parts[:-1]))
    return getattr(module, parts[-1])
