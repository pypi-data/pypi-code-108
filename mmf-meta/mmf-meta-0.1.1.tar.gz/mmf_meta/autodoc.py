import dataclasses
import typing
from dataclasses import field, Field


def desc(default=..., description=None, *args, **kwargs):
    if default is not ...:
        return field(*args, metadata={"desc": description}, default=default, **kwargs)
    else:
        return field(*args, metadata={"desc": description}, **kwargs)


def resolve_type(f: Field):
    if not f.type.__module__ == "builtins":
        try:
            tp = f"[{f.type.__name__}][{f.type.__module__}.{f.type.__name__}]"
        except:
            tp = f"`{repr(f.type)}`"
    else:
        tp = f"`{f.type.__name__}`"
    return f"{tp}" if f.default is None else f"{tp}, default={f.default}"


def autodoc_dc(cls):
    fields = dataclasses.fields(cls)
    args = "\n".join(
        (
            f"\t- **{f.name}** ({resolve_type(f)}): {f.metadata.get('desc', '')}"
            for f in fields
        )
    )
    cls.__doc__ = cls.__doc__.strip() + f"\n\nПараметры:\n{args}"
    return typing.cast(cls, cls)
