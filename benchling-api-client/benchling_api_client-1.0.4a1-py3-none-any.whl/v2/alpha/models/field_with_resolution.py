from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError, UnknownType
from ..models.field_type import FieldType
from ..models.field_value import FieldValue
from ..types import UNSET, Unset

T = TypeVar("T", bound="FieldWithResolution")


@attr.s(auto_attribs=True, repr=False)
class FieldWithResolution:
    """  """

    _value: Union[None, str, bool, float, FieldValue, List[str], UnknownType]
    _display_value: Union[Unset, None, str] = UNSET
    _is_multi: Union[Unset, bool] = UNSET
    _text_value: Union[Unset, None, str] = UNSET
    _type: Union[Unset, FieldType] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("value={}".format(repr(self._value)))
        fields.append("display_value={}".format(repr(self._display_value)))
        fields.append("is_multi={}".format(repr(self._is_multi)))
        fields.append("text_value={}".format(repr(self._text_value)))
        fields.append("type={}".format(repr(self._type)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "FieldWithResolution({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        value: Union[None, str, bool, float, Dict[str, Any], List[Any]]
        if isinstance(self._value, Unset):
            value = UNSET
        if self._value is None:
            value = None
        elif isinstance(self._value, UnknownType):
            value = self._value.value
        elif isinstance(self._value, FieldValue):
            value = self._value.to_dict()

        elif isinstance(self._value, list):
            value = self._value

        else:
            value = self._value

        display_value = self._display_value
        is_multi = self._is_multi
        text_value = self._text_value
        type: Union[Unset, int] = UNSET
        if not isinstance(self._type, Unset):
            type = self._type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "value": value,
            }
        )
        if display_value is not UNSET:
            field_dict["displayValue"] = display_value
        if is_multi is not UNSET:
            field_dict["isMulti"] = is_multi
        if text_value is not UNSET:
            field_dict["textValue"] = text_value
        if type is not UNSET:
            field_dict["type"] = type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_value() -> Union[None, str, bool, float, FieldValue, List[str], UnknownType]:
            def _parse_value(
                data: Union[None, str, bool, float, Dict[str, Any], List[Any]]
            ) -> Union[None, str, bool, float, FieldValue, List[str], UnknownType]:
                value: Union[None, str, bool, float, FieldValue, List[str], UnknownType]
                if data is None:
                    return data
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    value = FieldValue.from_dict(data)

                    return value
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, list):
                        raise TypeError()
                    value = cast(List[str], data)

                    return value
                except:  # noqa: E722
                    pass
                if isinstance(data, dict):
                    return UnknownType(data)
                return cast(Union[None, str, bool, float, FieldValue, List[str], UnknownType], data)

            value = _parse_value(d.pop("value"))

            return value

        value = (
            get_value()
            if "value" in d
            else cast(Union[None, str, bool, float, FieldValue, List[str], UnknownType], UNSET)
        )

        def get_display_value() -> Union[Unset, None, str]:
            display_value = d.pop("displayValue")
            return display_value

        display_value = get_display_value() if "displayValue" in d else cast(Union[Unset, None, str], UNSET)

        def get_is_multi() -> Union[Unset, bool]:
            is_multi = d.pop("isMulti")
            return is_multi

        is_multi = get_is_multi() if "isMulti" in d else cast(Union[Unset, bool], UNSET)

        def get_text_value() -> Union[Unset, None, str]:
            text_value = d.pop("textValue")
            return text_value

        text_value = get_text_value() if "textValue" in d else cast(Union[Unset, None, str], UNSET)

        def get_type() -> Union[Unset, FieldType]:
            type = None
            _type = d.pop("type")
            if _type is not None and _type is not UNSET:
                try:
                    type = FieldType(_type)
                except ValueError:
                    type = FieldType.of_unknown(_type)

            return type

        type = get_type() if "type" in d else cast(Union[Unset, FieldType], UNSET)

        field_with_resolution = cls(
            value=value,
            display_value=display_value,
            is_multi=is_multi,
            text_value=text_value,
            type=type,
        )

        field_with_resolution.additional_properties = d
        return field_with_resolution

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties

    def get(self, key, default=None) -> Optional[Any]:
        return self.additional_properties.get(key, default)

    @property
    def value(self) -> Optional[Union[str, bool, float, FieldValue, List[str], UnknownType]]:
        """For single link fields, use the id of the item you want to link (eg. "seq_jdf8BV24").
        For multi-link fields, use an array of ids of the items you want to link (eg. ["seq_jdf8BV24"])
        """
        if isinstance(self._value, Unset):
            raise NotPresentError(self, "value")
        return self._value

    @value.setter
    def value(self, value: Optional[Union[str, bool, float, FieldValue, List[str], UnknownType]]) -> None:
        self._value = value

    @property
    def display_value(self) -> Optional[str]:
        if isinstance(self._display_value, Unset):
            raise NotPresentError(self, "display_value")
        return self._display_value

    @display_value.setter
    def display_value(self, value: Optional[str]) -> None:
        self._display_value = value

    @display_value.deleter
    def display_value(self) -> None:
        self._display_value = UNSET

    @property
    def is_multi(self) -> bool:
        if isinstance(self._is_multi, Unset):
            raise NotPresentError(self, "is_multi")
        return self._is_multi

    @is_multi.setter
    def is_multi(self, value: bool) -> None:
        self._is_multi = value

    @is_multi.deleter
    def is_multi(self) -> None:
        self._is_multi = UNSET

    @property
    def text_value(self) -> Optional[str]:
        if isinstance(self._text_value, Unset):
            raise NotPresentError(self, "text_value")
        return self._text_value

    @text_value.setter
    def text_value(self, value: Optional[str]) -> None:
        self._text_value = value

    @text_value.deleter
    def text_value(self) -> None:
        self._text_value = UNSET

    @property
    def type(self) -> FieldType:
        if isinstance(self._type, Unset):
            raise NotPresentError(self, "type")
        return self._type

    @type.setter
    def type(self, value: FieldType) -> None:
        self._type = value

    @type.deleter
    def type(self) -> None:
        self._type = UNSET
