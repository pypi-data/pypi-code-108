from typing import Any, cast, Dict, List, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="UnregisterEntities")


@attr.s(auto_attribs=True, repr=False)
class UnregisterEntities:
    """  """

    _entity_ids: List[str]
    _folder_id: str

    def __repr__(self):
        fields = []
        fields.append("entity_ids={}".format(repr(self._entity_ids)))
        fields.append("folder_id={}".format(repr(self._folder_id)))
        return "UnregisterEntities({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        entity_ids = self._entity_ids

        folder_id = self._folder_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "entityIds": entity_ids,
                "folderId": folder_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_entity_ids() -> List[str]:
            entity_ids = cast(List[str], d.pop("entityIds"))

            return entity_ids

        entity_ids = get_entity_ids() if "entityIds" in d else cast(List[str], UNSET)

        def get_folder_id() -> str:
            folder_id = d.pop("folderId")
            return folder_id

        folder_id = get_folder_id() if "folderId" in d else cast(str, UNSET)

        unregister_entities = cls(
            entity_ids=entity_ids,
            folder_id=folder_id,
        )

        return unregister_entities

    @property
    def entity_ids(self) -> List[str]:
        """ Array of entity IDs """
        if isinstance(self._entity_ids, Unset):
            raise NotPresentError(self, "entity_ids")
        return self._entity_ids

    @entity_ids.setter
    def entity_ids(self, value: List[str]) -> None:
        self._entity_ids = value

    @property
    def folder_id(self) -> str:
        """ ID of the folder that the entities should be moved to """
        if isinstance(self._folder_id, Unset):
            raise NotPresentError(self, "folder_id")
        return self._folder_id

    @folder_id.setter
    def folder_id(self, value: str) -> None:
        self._folder_id = value
