from typing import List, Union
from .const import FieldGroupOperators, SortOrder, SystemFields
from .query_condition_field import QueryConditionField
from XmlElement import XmlElement

class QueryConditionGroup():
    def __init__(
            self, 
            object_name:str,
            field_conditions:Union[QueryConditionField, List[QueryConditionField]],
            group_operator:FieldGroupOperators=FieldGroupOperators.AND,
        ):
        """Create a new QueryConditionGroup() object combining the `<ConditionObject>` and `<FieldGroup>` tags.

        TODO
        Keyword arguments:
        object_name -- The internal name of a folder, register or document type.
        field_conditions -- A list of or single QueryConditionField(s).
        group_operator -- (Optional) FieldGroupOperators, default = FieldGroupOperators.AND.
        """ 
        self.internal_name = object_name
        if isinstance(field_conditions, list):
            self.field_conditions = field_conditions
        else:
            self.field_conditions = [ field_conditions ]
        
        self.group_operator = group_operator


    def __repr__(self) -> str:
        return f'{self.internal_name} ({self.group_operator.value}): {self.field_conditions}'

    
    def to_xml_element(self) -> XmlElement:
        """Render self to XmlElement"""
        return XmlElement(
            'ConditionObject', 
            {'internal_name': self.internal_name},
            [ x.to_xml_element() for x in self.field_conditions ]
        )