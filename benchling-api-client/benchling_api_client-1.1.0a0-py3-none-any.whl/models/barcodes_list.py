from typing import Any, cast, Dict, List, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="BarcodesList")


@attr.s(auto_attribs=True, repr=False)
class BarcodesList:
    """  """

    _barcodes: List[str]

    def __repr__(self):
        fields = []
        fields.append("barcodes={}".format(repr(self._barcodes)))
        return "BarcodesList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        barcodes = self._barcodes

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "barcodes": barcodes,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_barcodes() -> List[str]:
            barcodes = cast(List[str], d.pop("barcodes"))

            return barcodes

        barcodes = get_barcodes() if "barcodes" in d else cast(List[str], UNSET)

        barcodes_list = cls(
            barcodes=barcodes,
        )

        return barcodes_list

    @property
    def barcodes(self) -> List[str]:
        """ Array of barcodes to validate. """
        if isinstance(self._barcodes, Unset):
            raise NotPresentError(self, "barcodes")
        return self._barcodes

    @barcodes.setter
    def barcodes(self, value: List[str]) -> None:
        self._barcodes = value
