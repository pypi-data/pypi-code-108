from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.request import Request
from ..types import UNSET, Unset

T = TypeVar("T", bound="RequestsPaginatedList")


@attr.s(auto_attribs=True, repr=False)
class RequestsPaginatedList:
    """  """

    _next_token: Union[Unset, str] = UNSET
    _requests: Union[Unset, List[Request]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("next_token={}".format(repr(self._next_token)))
        fields.append("requests={}".format(repr(self._requests)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "RequestsPaginatedList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        next_token = self._next_token
        requests: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._requests, Unset):
            requests = []
            for requests_item_data in self._requests:
                requests_item = requests_item_data.to_dict()

                requests.append(requests_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if next_token is not UNSET:
            field_dict["nextToken"] = next_token
        if requests is not UNSET:
            field_dict["requests"] = requests

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_next_token() -> Union[Unset, str]:
            next_token = d.pop("nextToken")
            return next_token

        next_token = get_next_token() if "nextToken" in d else cast(Union[Unset, str], UNSET)

        def get_requests() -> Union[Unset, List[Request]]:
            requests = []
            _requests = d.pop("requests")
            for requests_item_data in _requests or []:
                requests_item = Request.from_dict(requests_item_data)

                requests.append(requests_item)

            return requests

        requests = get_requests() if "requests" in d else cast(Union[Unset, List[Request]], UNSET)

        requests_paginated_list = cls(
            next_token=next_token,
            requests=requests,
        )

        requests_paginated_list.additional_properties = d
        return requests_paginated_list

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
    def next_token(self) -> str:
        if isinstance(self._next_token, Unset):
            raise NotPresentError(self, "next_token")
        return self._next_token

    @next_token.setter
    def next_token(self, value: str) -> None:
        self._next_token = value

    @next_token.deleter
    def next_token(self) -> None:
        self._next_token = UNSET

    @property
    def requests(self) -> List[Request]:
        if isinstance(self._requests, Unset):
            raise NotPresentError(self, "requests")
        return self._requests

    @requests.setter
    def requests(self, value: List[Request]) -> None:
        self._requests = value

    @requests.deleter
    def requests(self) -> None:
        self._requests = UNSET
