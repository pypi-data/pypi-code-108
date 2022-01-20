from typing import Any, cast, Dict, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..models.measurement import Measurement
from ..types import UNSET, Unset

T = TypeVar("T", bound="ContainerContentUpdate")


@attr.s(auto_attribs=True, repr=False)
class ContainerContentUpdate:
    """  """

    _concentration: Measurement

    def __repr__(self):
        fields = []
        fields.append("concentration={}".format(repr(self._concentration)))
        return "ContainerContentUpdate({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        concentration = self._concentration.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "concentration": concentration,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_concentration() -> Measurement:
            concentration = Measurement.from_dict(d.pop("concentration"))

            return concentration

        concentration = get_concentration() if "concentration" in d else cast(Measurement, UNSET)

        container_content_update = cls(
            concentration=concentration,
        )

        return container_content_update

    @property
    def concentration(self) -> Measurement:
        if isinstance(self._concentration, Unset):
            raise NotPresentError(self, "concentration")
        return self._concentration

    @concentration.setter
    def concentration(self, value: Measurement) -> None:
        self._concentration = value
