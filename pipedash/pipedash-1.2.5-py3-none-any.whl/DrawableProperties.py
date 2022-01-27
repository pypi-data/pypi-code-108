from enum import Enum

from typing import List

from pipedash.helper import Serializable

class DrawablePropertyType(Enum):
    string = "string"
    text = "string"
    number = "number"
    datetime = "datetime"
    boolean = "boolean"
    group = "group"
    object = "object"
    enum = "enum"
    array = "array"
    datafield = "datafield"
    datastream = "datastream"

special_characters = "!@#$% ^&*()-+?_=,<>/"

class DrawablePropertyBasic(Serializable):
    key: str
    name: str
    type: DrawablePropertyType

    def validate(self):
        return True

class DrawableProperty(DrawablePropertyBasic):
    name: str
    key: str
    defaultValue: any
    ref: str
    required: bool
    type: DrawablePropertyType
    typeOptions: any

    def __init__(self, key: str,  name: str, type: DrawablePropertyType, defaultValue: any = None, typeOptions: any = None, required: bool = False, ref: str = None):
        self.name = name
        if any(c in special_characters for c in key):
            raise Exception("The key can not contain any special characters or whitespaces because its used as object key.")
        self.key = key
        self.required = required
        self.ref = ref
        self.type = type
        self.defaultValue = defaultValue
        self.typeOptions = typeOptions
        pass



class DrawablePropertyRepeatable(DrawablePropertyBasic):
    key: str
    name: str
    ref: str
    type: DrawablePropertyType = DrawablePropertyType.group
    group: List[DrawableProperty]
    def __init__(self, key: str, name: str, group: List[DrawableProperty], ref: str = None):
        self.key = key
        self.name = name
        self.ref = ref
        self.type = DrawablePropertyType.group
        self.group = group
        return None

