from typing import Optional, Union
from json import loads, JSONDecodeError
from smart_crypt import Crypt


def decrypt_request_data(data: dict, salt: str, token: str) -> dict:
    c = Crypt(salt=salt)
    try:
        decrypted_str = c.decrypt(data['data'], token)
        return loads(decrypted_str)
    except (ValueError, JSONDecodeError):
        raise ValueError('cant decrypt data, invalid salt or token')


def _create_definition(keys: Union[str, list], data: dict) -> dict:
    """return name/title for event/error

    Args:
        keys (Union[str, list]): keys for chacke in data
        data (dict): function data

    Returns:
        dict: name/title
    """
    if isinstance(keys, str):
        return {keys: data[keys]}
    elif isinstance(keys, (list, tuple)):
        return {k: data[k] for k in keys}
    else:
        return {}


# CREATE EVENT data
def get_list_values(
    keys: Union[str, list],
    list_value: str,
    iter_key: str,
    var_names: list,
    *args,
    **kwargs,
) -> dict:
    """return name and description

    Args:
        keys (Union[str, list]):  keys for chacke in data
        list_value (str): task list
        iter_key (str): iter key
        var_names (list): func names

    Returns:
        dict: definiton
    """
    list_ = []
    index = 0
    if list_value in kwargs:
        list_ = kwargs[list_value]
    elif list_value in var_names:
        list_ = args[var_names.index(list_value)]
    if iter_key in kwargs:
        index = kwargs[iter_key]
    elif iter_key in var_names:
        index = args[var_names.index(iter_key)]
    data = list_[index]
    definition = _create_definition(keys, data)
    return {
        "definition": definition,
    }


# for creating default name
def get_values(
    keys: Union[str, list],
    var_names: list,
    *args,
    **kwargs,
) -> dict:
    """ger values

    Args:
        keys (Union[str, list]):  keys for chacke in data
        var_names (list): func var names

    Returns:
        dict: definition
    """
    definition = {}
    if isinstance(keys, str):
        if keys in kwargs:
            definition[keys] = kwargs[keys]
        elif keys in var_names:
            definition[keys] = args[var_names.index(keys)]
        else:
            definition[keys] = ''
    else:
        for key in keys:
            if key in kwargs:
                value = kwargs[key]
            elif key in var_names:
                value = args[var_names.index(key)]
            else:
                raise ValueError('invalid keys')
            definition[key] = value
    return {"definition": definition}


def create_event_definition(
    keys: Union[str, list],
    values: Union[dict, list, None] = None,
    key: Optional[int] = None,
) -> dict:
    """helper for create event name, error na,e

    Args:
        keys (Union[str, list]):  keys for chacke in data
        values (Union[dict, list, None], optional): data. Defaults to None.
        key (Optional[int], optional): [description]. Defaults to None.

    Returns:
        str: {"definition": <definiton>}
    """
    if isinstance(values, list) and isinstance(key, int):
        data: dict = values[key]
    else:
        data: dict = values  # type: ignore
    try:
        return get_values(keys, [], **data)["definition"]
    except IndexError:
        pass
    return {}


def _check_lambda_args(args):
    for arg in args:
        if arg.__class__.__name__ == "LambdaContext":
            return tuple()
    return args
