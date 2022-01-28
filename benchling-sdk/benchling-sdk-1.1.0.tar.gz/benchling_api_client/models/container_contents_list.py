from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.container_content import ContainerContent
from ..types import UNSET, Unset

T = TypeVar("T", bound="ContainerContentsList")


@attr.s(auto_attribs=True, repr=False)
class ContainerContentsList:
    """  """

    _contents: Union[Unset, List[ContainerContent]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("contents={}".format(repr(self._contents)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "ContainerContentsList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        contents: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._contents, Unset):
            contents = []
            for contents_item_data in self._contents:
                contents_item = contents_item_data.to_dict()

                contents.append(contents_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if contents is not UNSET:
            field_dict["contents"] = contents

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_contents() -> Union[Unset, List[ContainerContent]]:
            contents = []
            _contents = d.pop("contents")
            for contents_item_data in _contents or []:
                contents_item = ContainerContent.from_dict(contents_item_data)

                contents.append(contents_item)

            return contents

        contents = get_contents() if "contents" in d else cast(Union[Unset, List[ContainerContent]], UNSET)

        container_contents_list = cls(
            contents=contents,
        )

        container_contents_list.additional_properties = d
        return container_contents_list

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
    def contents(self) -> List[ContainerContent]:
        if isinstance(self._contents, Unset):
            raise NotPresentError(self, "contents")
        return self._contents

    @contents.setter
    def contents(self, value: List[ContainerContent]) -> None:
        self._contents = value

    @contents.deleter
    def contents(self) -> None:
        self._contents = UNSET
