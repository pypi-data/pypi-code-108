from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..models.column_passport_autocorrelations import ColumnPassportAutocorrelations
from ..types import UNSET, Unset

T = TypeVar("T", bound="ColumnPassport")


@attr.s(auto_attribs=True)
class ColumnPassport:
    """ Summary statistics / properties of a raw column. Calculated on upload of a dataset. """

    id: int
    name: str
    cadence: float
    n_rows: int
    autocorrelations: ColumnPassportAutocorrelations
    is_text: Union[Unset, bool] = False
    is_binary: Union[Unset, bool] = False
    binary_labels: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        name = self.name
        cadence = self.cadence
        n_rows = self.n_rows
        autocorrelations = self.autocorrelations.to_dict()

        is_text = self.is_text
        is_binary = self.is_binary
        binary_labels: Union[Unset, List[str]] = UNSET
        if not isinstance(self.binary_labels, Unset):
            binary_labels = self.binary_labels

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "cadence": cadence,
                "nRows": n_rows,
                "autocorrelations": autocorrelations,
            }
        )
        if is_text is not UNSET:
            field_dict["isText"] = is_text
        if is_binary is not UNSET:
            field_dict["isBinary"] = is_binary
        if binary_labels is not UNSET:
            field_dict["binaryLabels"] = binary_labels

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        name = d.pop("name")

        cadence = d.pop("cadence")

        n_rows = d.pop("nRows")

        autocorrelations = ColumnPassportAutocorrelations.from_dict(d.pop("autocorrelations"))

        is_text = d.pop("isText", UNSET)

        is_binary = d.pop("isBinary", UNSET)

        binary_labels = cast(List[str], d.pop("binaryLabels", UNSET))

        column_passport = cls(
            id=id,
            name=name,
            cadence=cadence,
            n_rows=n_rows,
            autocorrelations=autocorrelations,
            is_text=is_text,
            is_binary=is_binary,
            binary_labels=binary_labels,
        )

        column_passport.additional_properties = d
        return column_passport

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
