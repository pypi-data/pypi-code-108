from meili_sdk import exceptions

__all__ = ("BaseModel",)


class MetaBase(type):
    """
    Metaclass for all objects in the SDK

    Will check all the variables inside the class and determine which ones have default values set
    and create a new attribute with a set of missing properties
    """

    def __new__(mcs, name, bases, attrs, **kwargs):
        meta = attrs.get("Meta", None)
        annotations = attrs.get("__annotations__", None)

        def __is_variable(kv):
            k, v = kv
            return (
                not k.startswith("_")
                and not callable(v)
                and not isinstance(v, (staticmethod, classmethod, property))
            )

        if annotations and not getattr(meta, "abstract", False):
            annotated_items = set(
                filter(lambda x: not x.startswith("_"), annotations.keys())
            )
            defaulted = set(i[0] for i in filter(__is_variable, attrs.items()))
            required = annotated_items - defaulted
            attrs["__required_attrs"] = required
            attrs["__all_attrs"] = sorted((*annotated_items, *defaulted))

        return super().__new__(mcs, name, bases, attrs)


class BaseModel(metaclass=MetaBase):
    """
    Base model class

    Helps with object initialization. Will discard all arguments passed to `__init__` if they
    are not defined on the class
    """

    def __init__(self, **kwargs) -> None:
        required_attrs = getattr(self, "__required_attrs", None)
        if required_attrs:
            missing_attrs = required_attrs - set(kwargs.keys())
            if missing_attrs:
                raise exceptions.MissingAttributesException(
                    self.__class__, missing_attrs
                )
        for k, v in kwargs.items():
            if k in getattr(self, "__all_attrs", []):
                setattr(self, k, v)

        super().__init__()

    def validate(self):
        """
        Validate object has correct data passed into it

        Will also find all methods named `validate_{field}` and run them
        """
        attrs = sorted(getattr(self, "__all_attrs", []))

        errors = {}

        for attr in attrs:
            fun = getattr(self, f"validate_{attr}", None)
            if callable(fun) and getattr(self, attr, None) is not None:
                try:
                    value = fun()
                    setattr(self, attr, value)
                except exceptions.ValidationError as validation_error:
                    errors.update(**{attr: str(validation_error)})

        if errors:
            raise exceptions.ValidationError(
                "\n".join(
                    [
                        f"Validation error for {key}: {error}"
                        for key, error in errors.items()
                    ]
                )
            )

    def __str__(self) -> str:
        return str(dict(self))

    def __iter__(self):
        """
        Return dictionaries for related objects and omit null fields
        """
        for key in getattr(self, "__all_attrs", []):
            value = getattr(self, key)

            if value is None:
                continue
            if isinstance(value, BaseModel):
                yield key, dict(value)
            if isinstance(value, (list, tuple, set)):
                if any([isinstance(val, BaseModel) for val in value]):
                    values = []
                    for val in value:
                        values.append(dict(val))
                    yield key, values
                else:
                    yield key, value
            else:
                yield key, value

    class Meta:
        abstract = True
