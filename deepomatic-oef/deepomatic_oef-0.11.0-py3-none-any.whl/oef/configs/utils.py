from copy import deepcopy


def dict_inject_sub(target_dict, values_dict, _keys_=None):
    """
    This utility recursively in-place merge values_dict into target_dict
    (i.e. target_dict is modified).
    It checks for target values and avoid overriding them. It raises
    an exception in case of conflicting values.

    Examples:

    target_dict = {'foo': 1, 'bar': {'x': 1}}
    dict_inject_sub(target_dict, {'hello': 'world', 'bar': {'y': 2}})

    will modify target_dict such that:
    target_dict == {'foo': 1, 'bar': {'x': 1, 'y': 2}, 'hello': 'world'}

    Args:
        target_dict (dict): It will be modified in-place to merge values from values_dict.
        values_dict (dict): The values to merge into target_dict.
        _keys_ (reserved): For internal use: stores the hierachy of keys to display errors.

    Raises:
        Exception: if values conflict. Ex: dict_inject_sub({'x': 1}, {'x': 2})
    """
    for key, value in values_dict.items():
        if key in target_dict:
            # We save the key name recursively for error display in case of Exception
            if _keys_ is None:
                subkeys = key
            else:
                subkeys = _keys_ + '.' + key

            if isinstance(value, dict):
                # We need to recursively apply dict_inject
                dict_inject_sub(target_dict[key], value, subkeys)
            elif target_dict[key] != value:
                raise Exception("Conflicting values for {}: current value is '{}', trying to update to '{}'".format(subkeys, target_dict[key], value))
        else:
            # Key does not exist: we set it.
            target_dict[key] = value


def dict_inject(initial_dict, values_dict, shortcuts=None):
    """
    This utility recursively merge values_dict into target_dict. Keys of values_dict
    can be of the form `'for.bar': 2`. This will be equivalent to: `'foo': {'bar': 2}`.

    It checks for target values and avoid overriding them. It raises
    an exception in case of conflicting values.

    If shortcuts if not None, keys starting with '@' will be replaced by the value hold in
    shortcuts[keys.split('.')[0]].

    Examples:

    target_dict = {'foo': 1, 'bar': {'x': 1}}
    dict_inject(target_dict, {'@model': {'hello': 'world'}, 'bar.y': 2}, shortcuts={'@model': ['image_classification']})

    will return:
    {'foo': 1, 'bar': {'x': 1, 'y': 2}, 'image_classification': {'hello': 'world'}}

    Args:
        target_dict (dict): The source dictionnary in which to merge values from values_dict.
        values_dict (dict): The values to merge into target_dict.
        shortcuts (dict of list): The dict of shortcuts.

    Returns:
        result (dict): The merged dictionnary.

    Raises:
        Exception: if values conflict. Ex: dict_inject({'x': 1}, {'x': 2})
    """
    result_dict = deepcopy(initial_dict)
    for key, value in values_dict.items():
        keys = key.split('.')
        if shortcuts is not None and keys[0].startswith('@'):
            if keys[0] in shortcuts:
                keys = shortcuts[keys[0]] + keys[1:]
            else:
                raise Exception('Unknown shortcut: {}'.format(keys[0]))

        # Make sure the value follows the key splitting process if relevant
        if isinstance(value, dict):
            value = dict_inject({}, value, shortcuts)

        # Wrap the value into dict with one key
        for key in reversed(keys):
            value = {key: value}
        dict_inject_sub(result_dict, value)
    return result_dict
