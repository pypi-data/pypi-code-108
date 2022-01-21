import inspect
from validr import T


def get_params(f: callable):
    sig = inspect.signature(f)
    sig_items = list(sig.parameters.values())
    params_schema = {}
    for p in sig_items[1:]:
        if p.default is not inspect.Parameter.empty:
            params_schema[p.name] = p.default
    if params_schema:
        return T.dict(params_schema).__schema__
    return None


def get_returns(f: callable):
    sig = inspect.signature(f)
    if sig.return_annotation is not inspect.Signature.empty:
        schema = sig.return_annotation
        if schema is not None:
            return T(schema).__schema__
    return None
