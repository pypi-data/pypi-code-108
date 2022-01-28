from typing import Any, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import UnknownType
from ..models.inaccessible_resource import InaccessibleResource
from ..models.well import Well

T = TypeVar("T", bound="PlateWells")


@attr.s(auto_attribs=True, repr=False)
class PlateWells:
    """ Well contents of the plate, keyed by position string (eg. "A1"). """

    additional_properties: Dict[str, Union[Well, InaccessibleResource, UnknownType]] = attr.ib(
        init=False, factory=dict
    )

    def __repr__(self):
        fields = []
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "PlateWells({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:

        field_dict: Dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            if isinstance(prop, UnknownType):
                field_dict[prop_name] = prop.value
            elif isinstance(prop, Well):
                field_dict[prop_name] = prop.to_dict()

            else:
                field_dict[prop_name] = prop.to_dict()

        field_dict.update({})

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        plate_wells = cls()

        additional_properties = {}
        for prop_name, prop_dict in d.items():

            def _parse_additional_property(
                data: Union[Dict[str, Any]]
            ) -> Union[Well, InaccessibleResource, UnknownType]:
                additional_property: Union[Well, InaccessibleResource, UnknownType]
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    additional_property = Well.from_dict(data)

                    return additional_property
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    additional_property = InaccessibleResource.from_dict(data)

                    return additional_property
                except:  # noqa: E722
                    pass
                return UnknownType(data)

            additional_property = _parse_additional_property(prop_dict)

            additional_properties[prop_name] = additional_property

        plate_wells.additional_properties = additional_properties
        return plate_wells

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Union[Well, InaccessibleResource, UnknownType]:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Union[Well, InaccessibleResource, UnknownType]) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties

    def get(self, key, default=None) -> Optional[Union[Well, InaccessibleResource, UnknownType]]:
        return self.additional_properties.get(key, default)
