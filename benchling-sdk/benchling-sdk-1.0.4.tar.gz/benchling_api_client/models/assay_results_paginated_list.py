from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.assay_result import AssayResult
from ..types import UNSET, Unset

T = TypeVar("T", bound="AssayResultsPaginatedList")


@attr.s(auto_attribs=True, repr=False)
class AssayResultsPaginatedList:
    """  """

    _assay_results: Union[Unset, List[AssayResult]] = UNSET
    _next_token: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("assay_results={}".format(repr(self._assay_results)))
        fields.append("next_token={}".format(repr(self._next_token)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "AssayResultsPaginatedList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        assay_results: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._assay_results, Unset):
            assay_results = []
            for assay_results_item_data in self._assay_results:
                assay_results_item = assay_results_item_data.to_dict()

                assay_results.append(assay_results_item)

        next_token = self._next_token

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if assay_results is not UNSET:
            field_dict["assayResults"] = assay_results
        if next_token is not UNSET:
            field_dict["nextToken"] = next_token

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_assay_results() -> Union[Unset, List[AssayResult]]:
            assay_results = []
            _assay_results = d.pop("assayResults")
            for assay_results_item_data in _assay_results or []:
                assay_results_item = AssayResult.from_dict(assay_results_item_data)

                assay_results.append(assay_results_item)

            return assay_results

        assay_results = (
            get_assay_results() if "assayResults" in d else cast(Union[Unset, List[AssayResult]], UNSET)
        )

        def get_next_token() -> Union[Unset, str]:
            next_token = d.pop("nextToken")
            return next_token

        next_token = get_next_token() if "nextToken" in d else cast(Union[Unset, str], UNSET)

        assay_results_paginated_list = cls(
            assay_results=assay_results,
            next_token=next_token,
        )

        assay_results_paginated_list.additional_properties = d
        return assay_results_paginated_list

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
    def assay_results(self) -> List[AssayResult]:
        if isinstance(self._assay_results, Unset):
            raise NotPresentError(self, "assay_results")
        return self._assay_results

    @assay_results.setter
    def assay_results(self, value: List[AssayResult]) -> None:
        self._assay_results = value

    @assay_results.deleter
    def assay_results(self) -> None:
        self._assay_results = UNSET

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
