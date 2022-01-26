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

T = TypeVar("T", bound="PoolV1SaveActualPrepaymentsResponse")


@define(auto_attribs=True)
class PoolV1SaveActualPrepaymentsResponse:
    """
    Attributes:
        num_prepayments_saved (Union[Unset, int]):
    """

    num_prepayments_saved: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        num_prepayments_saved = self.num_prepayments_saved

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if num_prepayments_saved is not UNSET:
            field_dict["numPrepaymentsSaved"] = num_prepayments_saved

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        num_prepayments_saved = d.pop("numPrepaymentsSaved", UNSET)

        pool_v1_save_actual_prepayments_response = cls(
            num_prepayments_saved=num_prepayments_saved,
        )

        pool_v1_save_actual_prepayments_response.additional_properties = d
        return pool_v1_save_actual_prepayments_response

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
