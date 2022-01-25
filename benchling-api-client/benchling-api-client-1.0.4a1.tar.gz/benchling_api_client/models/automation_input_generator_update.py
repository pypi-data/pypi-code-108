from typing import Any, cast, Dict, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="AutomationInputGeneratorUpdate")


@attr.s(auto_attribs=True, repr=False)
class AutomationInputGeneratorUpdate:
    """  """

    _file_id: Union[Unset, None, str] = UNSET

    def __repr__(self):
        fields = []
        fields.append("file_id={}".format(repr(self._file_id)))
        return "AutomationInputGeneratorUpdate({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        file_id = self._file_id

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if file_id is not UNSET:
            field_dict["fileId"] = file_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_file_id() -> Union[Unset, None, str]:
            file_id = d.pop("fileId")
            return file_id

        file_id = get_file_id() if "fileId" in d else cast(Union[Unset, None, str], UNSET)

        automation_input_generator_update = cls(
            file_id=file_id,
        )

        return automation_input_generator_update

    @property
    def file_id(self) -> Optional[str]:
        """ The ID of the file (blob) associated with the input generator. Set to `null` to remove an existing file from the generator. """
        if isinstance(self._file_id, Unset):
            raise NotPresentError(self, "file_id")
        return self._file_id

    @file_id.setter
    def file_id(self, value: Optional[str]) -> None:
        self._file_id = value

    @file_id.deleter
    def file_id(self) -> None:
        self._file_id = UNSET
