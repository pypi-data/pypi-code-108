from typing import Any, Dict, Type, TypeVar, Union, cast

import attr

from ..models.monolingual_text import MonolingualText
from ..models.quantity import Quantity
from ..models.time import Time
from ..types import UNSET, Unset

T = TypeVar("T", bound="Statement")


@attr.s(auto_attribs=True)
class Statement:
    """ """

    concept_id: str
    property_id: Union[Unset, str] = UNSET
    property_name: Union[Unset, str] = UNSET
    value_type: Union[Unset, str] = UNSET
    value: Union[MonolingualText, Quantity, Time, Unset, str] = UNSET
    value_name: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        concept_id = self.concept_id
        property_id = self.property_id
        property_name = self.property_name
        value_type = self.value_type
        value: Union[Dict[str, Any], Unset, str]
        if isinstance(self.value, Unset):
            value = UNSET
        elif isinstance(self.value, MonolingualText):
            value = UNSET
            if not isinstance(self.value, Unset):
                value = self.value.to_dict()

        elif isinstance(self.value, Quantity):
            value = UNSET
            if not isinstance(self.value, Unset):
                value = self.value.to_dict()

        elif isinstance(self.value, Time):
            value = UNSET
            if not isinstance(self.value, Unset):
                value = self.value.to_dict()

        else:
            value = self.value

        value_name = self.value_name

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "conceptId": concept_id,
            }
        )
        if property_id is not UNSET:
            field_dict["propertyId"] = property_id
        if property_name is not UNSET:
            field_dict["propertyName"] = property_name
        if value_type is not UNSET:
            field_dict["valueType"] = value_type
        if value is not UNSET:
            field_dict["value"] = value
        if value_name is not UNSET:
            field_dict["valueName"] = value_name

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        concept_id = d.pop("conceptId")

        property_id = d.pop("propertyId", UNSET)

        property_name = d.pop("propertyName", UNSET)

        value_type = d.pop("valueType", UNSET)

        def _parse_value(data: object) -> Union[MonolingualText, Quantity, Time, Unset, str]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                _value_type_1 = data
                value_type_1: Union[Unset, MonolingualText]
                if isinstance(_value_type_1, Unset):
                    value_type_1 = UNSET
                else:
                    value_type_1 = MonolingualText.from_dict(_value_type_1)

                return value_type_1
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                _value_type_2 = data
                value_type_2: Union[Unset, Quantity]
                if isinstance(_value_type_2, Unset):
                    value_type_2 = UNSET
                else:
                    value_type_2 = Quantity.from_dict(_value_type_2)

                return value_type_2
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                _value_type_3 = data
                value_type_3: Union[Unset, Time]
                if isinstance(_value_type_3, Unset):
                    value_type_3 = UNSET
                else:
                    value_type_3 = Time.from_dict(_value_type_3)

                return value_type_3
            except:  # noqa: E722
                pass
            return cast(Union[MonolingualText, Quantity, Time, Unset, str], data)

        value = _parse_value(d.pop("value", UNSET))

        value_name = d.pop("valueName", UNSET)

        statement = cls(
            concept_id=concept_id,
            property_id=property_id,
            property_name=property_name,
            value_type=value_type,
            value=value,
            value_name=value_name,
        )

        return statement
