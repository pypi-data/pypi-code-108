from functools import singledispatch

from flask import url_for as url_for_orig


@singledispatch
def url_for(obj, _ns="", **kw) -> str:
    raise RuntimeError(f"Illegal argument for 'url_for': {obj} (type: {type(obj)})")


@url_for.register
def url_for_str(name: str, _ns="", **kw):
    return url_for_orig(name, **kw)
