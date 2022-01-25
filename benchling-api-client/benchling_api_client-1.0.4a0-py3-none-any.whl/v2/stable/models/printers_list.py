from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.printer import Printer
from ..types import UNSET, Unset

T = TypeVar("T", bound="PrintersList")


@attr.s(auto_attribs=True, repr=False)
class PrintersList:
    """  """

    _label_printers: Union[Unset, List[Printer]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("label_printers={}".format(repr(self._label_printers)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "PrintersList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        label_printers: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._label_printers, Unset):
            label_printers = []
            for label_printers_item_data in self._label_printers:
                label_printers_item = label_printers_item_data.to_dict()

                label_printers.append(label_printers_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if label_printers is not UNSET:
            field_dict["labelPrinters"] = label_printers

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_label_printers() -> Union[Unset, List[Printer]]:
            label_printers = []
            _label_printers = d.pop("labelPrinters")
            for label_printers_item_data in _label_printers or []:
                label_printers_item = Printer.from_dict(label_printers_item_data)

                label_printers.append(label_printers_item)

            return label_printers

        label_printers = (
            get_label_printers() if "labelPrinters" in d else cast(Union[Unset, List[Printer]], UNSET)
        )

        printers_list = cls(
            label_printers=label_printers,
        )

        printers_list.additional_properties = d
        return printers_list

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
    def label_printers(self) -> List[Printer]:
        if isinstance(self._label_printers, Unset):
            raise NotPresentError(self, "label_printers")
        return self._label_printers

    @label_printers.setter
    def label_printers(self, value: List[Printer]) -> None:
        self._label_printers = value

    @label_printers.deleter
    def label_printers(self) -> None:
        self._label_printers = UNSET
