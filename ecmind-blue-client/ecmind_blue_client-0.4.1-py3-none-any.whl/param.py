from __future__ import annotations
from datetime import datetime
from typing import Any
from XmlElement import XmlElement

from .const import ParamTypes

class Param():
    def __init__(self, name:str, type:ParamTypes, value:Any):
        """Create a new Param() object.

        Keyword arguments:
        name -- String with parameter name, i. e. 'Flags'
        type -- ParamTypes Enum element definiting the parameter type, i. e. ParamTypes.INTEGER
        value -- The value to store for this Param.
        """        
        self.name = name
        self.type = type
        self.value = value

    
    def __repr__(self) -> str:
        return f'{self.name}:{self.type.value} = {self.value}'


    @staticmethod
    def infer_type(name:str, value:Any) -> Param:
        """Factory function to create new Param() objects without explicitly 
        stating a ParamTypes enum element as the parameter type.
        The type is infered by checking the values type against int, bool, float, datetime 
        or if the value is a instance of XmlElement or has the name 'XML'.

        Keyword arguments:
        name -- String with parameter name, i. e. 'Flags'
        value -- The value to store for this Param.
        """
        if isinstance(value, bool):
            return Param(name, ParamTypes.BOOLEAN, value) 
        elif isinstance(value, int):
            return Param(name, ParamTypes.INTEGER, value)
        elif isinstance(value, float):
            return Param(name, ParamTypes.DOUBLE, value)
        elif isinstance(value, datetime):
            return Param(name, ParamTypes.DATE_TIME, value)
        elif isinstance(value, XmlElement):
            return Param(name, ParamTypes.BASE64, value.to_string())
        elif name == "XML":
            return Param(name, ParamTypes.BASE64, value)
        else:
            return Param(name, ParamTypes.STRING, value)