#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""TBW."""
import typing as t

__all__ = ["get_obj_att", "get_obj_by_type", "get_value", "get_state_ids", "copy_state"]


# TODO: Remove this function ? See issue #230.
def get_obj_by_type(obj: t.Any, key: str, obj_type: t.Optional[t.Type] = None) -> t.Any:
    """Get the object associated with the class type following the key chain.

    :param obj:
    :param key:
    :param obj_type:
    :return:
    """
    obj, att = get_obj_att(obj, key, obj_type)
    if obj_type is not None:
        if isinstance(obj, obj_type):
            return obj


# TODO: Remove this function ? See issue #230.
def get_obj_att(
    obj: t.Any, key: str, obj_type: t.Optional[t.Type] = None
) -> t.Tuple[t.Any, str]:
    """Get the object associated with the key.

    Example::

        >>> obj = {"processor": {"pipeline": {"models": [1, 2, 3]}}}
        >>> om.get_obj_att(obj, "processor.pipeline.models")
        ({'models': [1, 2, 3]}, 'models')

    The above example works as well for a user-defined object with a attribute
    objects, i.e. configuration object model.

    :param obj:
    :param key:
    :param obj_type:
    :return: the object and attribute name tuple
    """
    *body, tail = key.split(".")
    for part in body:
        try:
            if isinstance(obj, dict):
                obj = obj[part]
            elif isinstance(obj, list):
                try:
                    index = int(part)
                    obj = obj[index]
                except ValueError:
                    for _, obj_i in enumerate(obj):
                        if hasattr(obj_i, part):
                            obj = getattr(obj_i, part)
                            break
                        elif obj_i.__class__.__name__ == part:
                            if hasattr(obj_i, tail):
                                obj = obj_i
                                break
            elif hasattr(obj, part):
                obj = getattr(obj, part)
            else:
                raise NotImplementedError(
                    f"obj={obj!r}, key={key!r}, obj_type={obj_type!r}, part={part!r}"
                )

            if obj_type and isinstance(obj, obj_type):
                return obj, tail

        except AttributeError:
            # logging.error('Cannot find attribute %r in key %r', part, key)
            obj = None
            break
    return obj, tail


# TODO: Remove this function ? See issue #230.
def get_state(obj: t.Any) -> t.Mapping[str, t.Any]:
    """Convert the config object to a embedded dict object.

    The returned value will be a dictionary tree that is JSON
    compatible. Only dict, list, str, numbers will be contained
    in the returned dictionary.

    :param obj: a top level dict object or a object that defines
        the __getstate__ method.

    :return: the dictionary representation of the passed object.
    """
    result = {}
    if isinstance(obj, dict):
        for key, value in obj.items():
            result[key] = value.__getstate__()

    elif hasattr(obj, "__getstate__"):
        result = obj.__getstate__()

    return result


# TODO: Remove this function ? See issue #230.
def get_state_ids(
    obj: t.Any,
    parent_key_list: t.Optional[t.Sequence[str]] = None,
    result: t.Optional[t.Dict[str, t.Any]] = None,
) -> t.Any:
    """Retrieve a flat dictionary of the object attribute hierarchy.

    The dot-format is used as the key representation.

    :param obj:
    :param parent_key_list:
    :param result:
    :return:
    """
    if result is None:
        from collections import OrderedDict

        result = OrderedDict()

    if parent_key_list is None:
        parent_key_list = []

    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, (str, int, float)):
                key = ".".join(parent_key_list) + "." + key
                result[key] = value
            else:
                list(parent_key_list) + [key]
                get_state_ids(value, list(parent_key_list) + [key], result)

    elif isinstance(obj, list):
        is_primitive = all([isinstance(value, (str, int, float)) for value in obj])
        if is_primitive:
            key = ".".join(parent_key_list)
            result[key] = obj
        else:
            for i, value in enumerate(obj):
                get_state_ids(value, list(parent_key_list) + [str(i)], result)
    return result


# TODO: Remove this function ? See issue #230.
def get_value(obj: t.Any, key: str) -> t.Any:
    """Retrieve the attribute value of the object given the attribute dot formatted key chain.

    Example::

        >>> obj = {"processor": {"pipeline": {"models": [1, 2, 3]}}}
        >>> om.get_value(obj, "processor.pipeline.models")
        [1, 2, 3]

    The above example works as well for a user-defined object with a attribute
    objects, i.e. configuration object model.

    :param obj:
    :param key:
    :return:
    """
    obj, att = get_obj_att(obj, key)

    if isinstance(obj, dict) and att in obj:
        value = obj[att]
    else:
        value = getattr(obj, att)

    return value


# TODO: Remove this function ? See issue #230.
def copy_state(obj: t.Any) -> t.Mapping[str, t.Any]:
    """Deep copy the object as a attribute name/value pairs dictionary.

    :param obj:
    :return:
    """
    kwargs = {}
    for key, _ in obj.__getstate__().items():
        obj_att = getattr(obj, key)
        if obj_att is None:
            cpy_obj = None
        elif hasattr(
            obj_att, "copy"
        ):  # TODO: PYXEL specific: this should be replaced with __copy__
            cpy_obj = obj_att.copy()
        else:
            cpy_obj = type(obj_att)(obj_att)
        kwargs[key] = cpy_obj
    return kwargs
