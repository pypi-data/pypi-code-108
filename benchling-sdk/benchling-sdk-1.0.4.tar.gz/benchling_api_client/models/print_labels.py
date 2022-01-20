from typing import Any, cast, Dict, List, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="PrintLabels")


@attr.s(auto_attribs=True, repr=False)
class PrintLabels:
    """  """

    _container_ids: List[str]
    _label_template_id: str
    _printer_id: str

    def __repr__(self):
        fields = []
        fields.append("container_ids={}".format(repr(self._container_ids)))
        fields.append("label_template_id={}".format(repr(self._label_template_id)))
        fields.append("printer_id={}".format(repr(self._printer_id)))
        return "PrintLabels({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        container_ids = self._container_ids

        label_template_id = self._label_template_id
        printer_id = self._printer_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "containerIds": container_ids,
                "labelTemplateId": label_template_id,
                "printerId": printer_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_container_ids() -> List[str]:
            container_ids = cast(List[str], d.pop("containerIds"))

            return container_ids

        container_ids = get_container_ids() if "containerIds" in d else cast(List[str], UNSET)

        def get_label_template_id() -> str:
            label_template_id = d.pop("labelTemplateId")
            return label_template_id

        label_template_id = get_label_template_id() if "labelTemplateId" in d else cast(str, UNSET)

        def get_printer_id() -> str:
            printer_id = d.pop("printerId")
            return printer_id

        printer_id = get_printer_id() if "printerId" in d else cast(str, UNSET)

        print_labels = cls(
            container_ids=container_ids,
            label_template_id=label_template_id,
            printer_id=printer_id,
        )

        return print_labels

    @property
    def container_ids(self) -> List[str]:
        """List of IDs of containers that will have labels printed (one label will be printed per container)."""
        if isinstance(self._container_ids, Unset):
            raise NotPresentError(self, "container_ids")
        return self._container_ids

    @container_ids.setter
    def container_ids(self, value: List[str]) -> None:
        self._container_ids = value

    @property
    def label_template_id(self) -> str:
        """ID of label template to use (same template will be used for all labels printed)."""
        if isinstance(self._label_template_id, Unset):
            raise NotPresentError(self, "label_template_id")
        return self._label_template_id

    @label_template_id.setter
    def label_template_id(self, value: str) -> None:
        self._label_template_id = value

    @property
    def printer_id(self) -> str:
        """ID of printer to use (same printer will be used for all labels printed)."""
        if isinstance(self._printer_id, Unset):
            raise NotPresentError(self, "printer_id")
        return self._printer_id

    @printer_id.setter
    def printer_id(self, value: str) -> None:
        self._printer_id = value
