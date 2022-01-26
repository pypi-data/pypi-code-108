from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.request_fulfillment import RequestFulfillment
from ..types import UNSET, Unset

T = TypeVar("T", bound="RequestFulfillmentsPaginatedList")


@attr.s(auto_attribs=True, repr=False)
class RequestFulfillmentsPaginatedList:
    """ An object containing an array of RequestFulfillments """

    _next_token: Union[Unset, str] = UNSET
    _request_fulfillments: Union[Unset, List[RequestFulfillment]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("next_token={}".format(repr(self._next_token)))
        fields.append("request_fulfillments={}".format(repr(self._request_fulfillments)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "RequestFulfillmentsPaginatedList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        next_token = self._next_token
        request_fulfillments: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._request_fulfillments, Unset):
            request_fulfillments = []
            for request_fulfillments_item_data in self._request_fulfillments:
                request_fulfillments_item = request_fulfillments_item_data.to_dict()

                request_fulfillments.append(request_fulfillments_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if next_token is not UNSET:
            field_dict["nextToken"] = next_token
        if request_fulfillments is not UNSET:
            field_dict["requestFulfillments"] = request_fulfillments

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_next_token() -> Union[Unset, str]:
            next_token = d.pop("nextToken")
            return next_token

        next_token = get_next_token() if "nextToken" in d else cast(Union[Unset, str], UNSET)

        def get_request_fulfillments() -> Union[Unset, List[RequestFulfillment]]:
            request_fulfillments = []
            _request_fulfillments = d.pop("requestFulfillments")
            for request_fulfillments_item_data in _request_fulfillments or []:
                request_fulfillments_item = RequestFulfillment.from_dict(request_fulfillments_item_data)

                request_fulfillments.append(request_fulfillments_item)

            return request_fulfillments

        request_fulfillments = (
            get_request_fulfillments()
            if "requestFulfillments" in d
            else cast(Union[Unset, List[RequestFulfillment]], UNSET)
        )

        request_fulfillments_paginated_list = cls(
            next_token=next_token,
            request_fulfillments=request_fulfillments,
        )

        request_fulfillments_paginated_list.additional_properties = d
        return request_fulfillments_paginated_list

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
    def request_fulfillments(self) -> List[RequestFulfillment]:
        if isinstance(self._request_fulfillments, Unset):
            raise NotPresentError(self, "request_fulfillments")
        return self._request_fulfillments

    @request_fulfillments.setter
    def request_fulfillments(self, value: List[RequestFulfillment]) -> None:
        self._request_fulfillments = value

    @request_fulfillments.deleter
    def request_fulfillments(self) -> None:
        self._request_fulfillments = UNSET
