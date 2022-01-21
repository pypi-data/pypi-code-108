AutoStringMapping = {
    "true": True,
    "True": True,
    "False": False,
    "false": False,
    "null": None,
    "None": None,
}


def auto_form(form=None, **kwargs):
    if form is None:
        form = kwargs
    elif isinstance(form, dict):
        form.update(kwargs)
    else:
        raise TypeError("$form is not None nor dict")

    data = {}
    auto_keys = AutoStringMapping.keys()
    if isinstance(form, dict):
        for k, v in form.items():
            if isinstance(v, str):
                v = v.strip()
                if v in auto_keys:
                    v = AutoStringMapping[v]
                elif v.isdecimal():
                    v = int(v)
            data[k] = v
    return data


def fetch_dict(form, keys, default=None):
    ds = {}
    for k in keys:
        v = form.get(k, default)
        ds[k] = v
    return ds


def brief_object(obj):
    data = {}
    for attr in dir(obj):
        if not attr.startswith('_'):
            value = getattr(obj, attr)
            if not callable(value):
                if isinstance(value, str):
                    value = value.strip()
                data[attr] = value
    return data


def _debug_form(form, *required_args, _verified_kws=None):
    keys = form.keys()
    args_set = set(required_args)
    for arg in required_args:
        if arg in keys:
            args_set.remove(arg)
    if len(args_set) > 0:
        yield ValueError("Require Args: {}".format(args_set))
    if isinstance(_verified_kws, dict):
        for k, v in _verified_kws.items():
            dv = form.get(k, None)
            if dv != v:
                yield ValueError("Require ${}={}".format(k, v))


def debug_form(form, *required_args, _verified_kws=None, verbose=False):
    _debug = _debug_form(form, *required_args, _verified_kws=_verified_kws)
    if not verbose:
        for msg in _debug:
            raise ValueError(msg)
    else:
        msg = '\n'.join(" [{}] {} ".format(i + 1, info) for i, info in _debug)
        raise ValueError(msg)
