from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="LabelTemplate")


@attr.s(auto_attribs=True, repr=False)
class LabelTemplate:
    """  """

    _id: Union[Unset, str] = UNSET
    _name: Union[Unset, str] = UNSET
    _zpl_template: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("id={}".format(repr(self._id)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("zpl_template={}".format(repr(self._zpl_template)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "LabelTemplate({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        id = self._id
        name = self._name
        zpl_template = self._zpl_template

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if zpl_template is not UNSET:
            field_dict["zplTemplate"] = zpl_template

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_id() -> Union[Unset, str]:
            id = d.pop("id")
            return id

        id = get_id() if "id" in d else cast(Union[Unset, str], UNSET)

        def get_name() -> Union[Unset, str]:
            name = d.pop("name")
            return name

        name = get_name() if "name" in d else cast(Union[Unset, str], UNSET)

        def get_zpl_template() -> Union[Unset, str]:
            zpl_template = d.pop("zplTemplate")
            return zpl_template

        zpl_template = get_zpl_template() if "zplTemplate" in d else cast(Union[Unset, str], UNSET)

        label_template = cls(
            id=id,
            name=name,
            zpl_template=zpl_template,
        )

        label_template.additional_properties = d
        return label_template

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
    def id(self) -> str:
        """ ID of the label template. """
        if isinstance(self._id, Unset):
            raise NotPresentError(self, "id")
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        self._id = value

    @id.deleter
    def id(self) -> None:
        self._id = UNSET

    @property
    def name(self) -> str:
        """ Name of the label template. """
        if isinstance(self._name, Unset):
            raise NotPresentError(self, "name")
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @name.deleter
    def name(self) -> None:
        self._name = UNSET

    @property
    def zpl_template(self) -> str:
        """ The ZPL template that will be filled in and sent to a printer. """
        if isinstance(self._zpl_template, Unset):
            raise NotPresentError(self, "zpl_template")
        return self._zpl_template

    @zpl_template.setter
    def zpl_template(self, value: str) -> None:
        self._zpl_template = value

    @zpl_template.deleter
    def zpl_template(self) -> None:
        self._zpl_template = UNSET
