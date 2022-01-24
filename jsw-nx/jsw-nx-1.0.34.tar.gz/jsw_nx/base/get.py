# https://gist.github.com/wonderbeyond/085f7a8a4bfbf092b830
# https://pypi.org/project/dict-deep/
def get(data, key, default=None, raising=False):
    value = data
    try:
        for key in key.split('.'):
            if isinstance(value, dict):
                value = value[key]
                continue
            else:
                if raising:
                    raise KeyError
                return default
    except KeyError:
        if raising:
            raise
        return default
    else:
        return value
