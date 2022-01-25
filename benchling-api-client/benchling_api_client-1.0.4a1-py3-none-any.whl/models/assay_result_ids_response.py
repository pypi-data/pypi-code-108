from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="AssayResultIdsResponse")


@attr.s(auto_attribs=True, repr=False)
class AssayResultIdsResponse:
    """  """

    _assay_result_ids: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("assay_result_ids={}".format(repr(self._assay_result_ids)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "AssayResultIdsResponse({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        assay_result_ids: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._assay_result_ids, Unset):
            assay_result_ids = self._assay_result_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if assay_result_ids is not UNSET:
            field_dict["assayResultIds"] = assay_result_ids

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_assay_result_ids() -> Union[Unset, List[str]]:
            assay_result_ids = cast(List[str], d.pop("assayResultIds"))

            return assay_result_ids

        assay_result_ids = (
            get_assay_result_ids() if "assayResultIds" in d else cast(Union[Unset, List[str]], UNSET)
        )

        assay_result_ids_response = cls(
            assay_result_ids=assay_result_ids,
        )

        assay_result_ids_response.additional_properties = d
        return assay_result_ids_response

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
    def assay_result_ids(self) -> List[str]:
        if isinstance(self._assay_result_ids, Unset):
            raise NotPresentError(self, "assay_result_ids")
        return self._assay_result_ids

    @assay_result_ids.setter
    def assay_result_ids(self, value: List[str]) -> None:
        self._assay_result_ids = value

    @assay_result_ids.deleter
    def assay_result_ids(self) -> None:
        self._assay_result_ids = UNSET
