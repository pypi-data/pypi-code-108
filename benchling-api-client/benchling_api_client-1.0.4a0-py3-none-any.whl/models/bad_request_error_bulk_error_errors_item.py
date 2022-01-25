from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="BadRequestErrorBulkErrorErrorsItem")


@attr.s(auto_attribs=True, repr=False)
class BadRequestErrorBulkErrorErrorsItem:
    """  """

    _index: Union[Unset, float] = UNSET
    _message: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("index={}".format(repr(self._index)))
        fields.append("message={}".format(repr(self._message)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "BadRequestErrorBulkErrorErrorsItem({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        index = self._index
        message = self._message

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if index is not UNSET:
            field_dict["index"] = index
        if message is not UNSET:
            field_dict["message"] = message

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_index() -> Union[Unset, float]:
            index = d.pop("index")
            return index

        index = get_index() if "index" in d else cast(Union[Unset, float], UNSET)

        def get_message() -> Union[Unset, str]:
            message = d.pop("message")
            return message

        message = get_message() if "message" in d else cast(Union[Unset, str], UNSET)

        bad_request_error_bulk_error_errors_item = cls(
            index=index,
            message=message,
        )

        bad_request_error_bulk_error_errors_item.additional_properties = d
        return bad_request_error_bulk_error_errors_item

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
    def index(self) -> float:
        if isinstance(self._index, Unset):
            raise NotPresentError(self, "index")
        return self._index

    @index.setter
    def index(self, value: float) -> None:
        self._index = value

    @index.deleter
    def index(self) -> None:
        self._index = UNSET

    @property
    def message(self) -> str:
        if isinstance(self._message, Unset):
            raise NotPresentError(self, "message")
        return self._message

    @message.setter
    def message(self, value: str) -> None:
        self._message = value

    @message.deleter
    def message(self) -> None:
        self._message = UNSET
