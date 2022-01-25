from typing import List, Union
from .const import FieldGroupOperators, SortOrder, SystemFields, QueryOperators, SpecialValues
from XmlElement import XmlElement
from datetime import datetime, date

class QueryConditionField():
    def __init__(
            self, 
            field:Union[str, SystemFields], 
            values:Union[str,int,float,date,datetime,None,SpecialValues, List[Union[str,int,float,date,datetime,None,SpecialValues]]],
            operator:QueryOperators=QueryOperators.EQUAL,
            table:str=None
        ):
        """Create a new QueryConditionField() object.

        Keyword arguments:
        field -- A internal name as string or a instance of SystemFields. Internal names beeing automatically checked against known system field names.
        operator -- (Optional) QueryOperators instance, default = EQUAL.
        table -- (Optional) Table internal name. If this is set, the a `<TableCondition>` is created using the field parameter as `<TableColumn>`, default = None.
        values: A list of literal values, None (interpretet as `<NULL />` value) or a SpecialValues instance for `<SpecialValues>`
        """ 

        if not table and isinstance(field, SystemFields):
            self.internal_name = field.name
            self.system = True
        elif not table and field in [ system_field.name for system_field in SystemFields]:
            self.internal_name = field
            self.system = True
        else:
            self.internal_name = field
            self.system = False

        self.query_operator = operator
        self.table_name = table
        self.values = values

    def __repr__(self) -> str:
        return (f'{self.table_name}:' if self.table_name else '') + f'{self.internal_name} {self.query_operator.value} {self.values}'

    def to_xml_element(self) -> XmlElement:
        """Render self to XmlElement"""

        def values_to_xml_elements(self) -> List[XmlElement]:
            if not self.values:
                return [ XmlElement('NULL') ]
            result = []
            for v in self.values if isinstance(self.values, list) else [ self.values ]:
                if v == None:
                    result.append(XmlElement('NULL'))
                elif isinstance(v, SpecialValues):
                    result.append(XmlElement('SpecialValue', t=v.value))
                elif isinstance(v, datetime):
                    result.append(XmlElement('Value', t=datetime.strftime(v, '%d.%m.%Y %H:%M:%S')))
                elif isinstance(v, date):
                    v_datetime = datetime.combine(v, datetime.min.time())
                    result.append(XmlElement('Value', t=datetime.strftime(v_datetime, '%d.%m.%Y')))
                else:
                    result.append(XmlElement('Value', t=str(v)))
            
            if len(result) == 0:
                return [ XmlElement('NULL') ]
            
            return result

        if self.table_name:
            x = XmlElement('TableCondition', {'internal_name': self.table_name}, [
                XmlElement(
                    'TableColumn', {
                        'internal_name': self.internal_name, 
                        'operator': self.query_operator.value 
                    },
                    values_to_xml_elements(self)
                )
            ])
        else:
            x = XmlElement(
                    'FieldCondition', {
                        'internal_name': self.internal_name,
                        'operator': self.query_operator.value 
                    },
                    values_to_xml_elements(self)
                )
            if self.system:
                x.attributes['system'] = '1'
        
        return x