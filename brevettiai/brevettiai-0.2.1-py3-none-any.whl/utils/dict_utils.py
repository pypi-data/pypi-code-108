def dict_merger(source, target):
    """
    Merge two dicts of dicts
    :param source:
    :param target:
    :return:
    """
    for k, v in source.items():
        if isinstance(v, dict) and isinstance(target.get(k), dict):
            dict_merger(v, target[k])
        else:
            target[k] = v


def in_dicts(d, uri):
    """
    Check if path of keys in dict of dicts
    :param d: dict of dicts
    :param uri: list of keys
    :return:
    """
    if len(uri) > 1:
        if uri[0] not in d:
            return False
        return in_dicts(d[uri[0]], uri[1:])
    else:
        return uri[0] in d