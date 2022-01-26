import typing as t
from meili_sdk.exceptions import MissingAttributesException
from meili_sdk.models.base import BaseModel

__all__ = (
    "Variable",
    "FormVariable",
    "Form",
    "VariableInstance",
    "FormInstance",
)


class Variable(BaseModel):
    uuid: str
    name: str
    variable_name: str
    variable_type: str


class FormVariable(BaseModel):
    uuid: str
    name: str
    help_text: t.Optional[str]
    required: bool
    sort_priority: int
    variable: Variable

    def __init__(self, **kwargs):
        kwargs["variable"] = Variable(**kwargs.get("variable", {}))
        super().__init__(**kwargs)


class Form(BaseModel):
    uuid: str
    name: str
    team: t.Optional[str] = None
    target_object: str
    variables: t.List[FormVariable]

    def __init__(self, **kwargs):
        variables = kwargs.pop("variables", None)

        if not variables:
            raise MissingAttributesException(self.__class__, "variables")

        variables_objects = []
        for variable in variables:
            variables_objects.append(FormVariable(**variable))
        kwargs["variables"] = variables_objects
        super().__init__(**kwargs)


class VariableInstance(BaseModel):
    value: t.Union[str, bool, int, float]
    variable_name: str
    variable_type: str


class FormInstance(BaseModel):
    entries: t.List[VariableInstance]

    def __init__(self, **kwargs):
        entries = kwargs.pop("entries", None)

        if not entries:
            raise MissingAttributesException(self.__class__, "entries")

        entry_objects = []
        for entry in entries:
            entry_objects.append(VariableInstance(**entry))
        kwargs["entries"] = entry_objects
        super().__init__(**kwargs)
