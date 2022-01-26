from typing import (
    Any,
    BinaryIO,
    Dict,
    List,
    Optional,
    TextIO,
    Tuple,
    Type,
    TypeVar,
    Union,
)

from attr import define, field

from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="CohortV1SaveAssociationsResponse")


@define(auto_attribs=True)
class CohortV1SaveAssociationsResponse:
    """
    Attributes:
        num_associations_saved (Union[Unset, int]):
    """

    num_associations_saved: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        num_associations_saved = self.num_associations_saved

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if num_associations_saved is not UNSET:
            field_dict["numAssociationsSaved"] = num_associations_saved

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        num_associations_saved = d.pop("numAssociationsSaved", UNSET)

        cohort_v1_save_associations_response = cls(
            num_associations_saved=num_associations_saved,
        )

        cohort_v1_save_associations_response.additional_properties = d
        return cohort_v1_save_associations_response

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
