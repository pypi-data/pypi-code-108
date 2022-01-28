from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="AssayResultsCreateResponse")


@attr.s(auto_attribs=True, repr=False)
class AssayResultsCreateResponse:
    """  """

    _assay_results: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("assay_results={}".format(repr(self._assay_results)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "AssayResultsCreateResponse({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        assay_results: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._assay_results, Unset):
            assay_results = self._assay_results

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if assay_results is not UNSET:
            field_dict["assayResults"] = assay_results

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_assay_results() -> Union[Unset, List[str]]:
            assay_results = cast(List[str], d.pop("assayResults"))

            return assay_results

        assay_results = get_assay_results() if "assayResults" in d else cast(Union[Unset, List[str]], UNSET)

        assay_results_create_response = cls(
            assay_results=assay_results,
        )

        assay_results_create_response.additional_properties = d
        return assay_results_create_response

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
    def assay_results(self) -> List[str]:
        if isinstance(self._assay_results, Unset):
            raise NotPresentError(self, "assay_results")
        return self._assay_results

    @assay_results.setter
    def assay_results(self, value: List[str]) -> None:
        self._assay_results = value

    @assay_results.deleter
    def assay_results(self) -> None:
        self._assay_results = UNSET
