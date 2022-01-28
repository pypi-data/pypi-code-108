from typing import Any, cast, Dict, List, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.collaboration_create import CollaborationCreate
from ..models.worklist_type import WorklistType
from ..types import UNSET, Unset

T = TypeVar("T", bound="WorklistCreate")


@attr.s(auto_attribs=True, repr=False)
class WorklistCreate:
    """  """

    _name: str
    _type: WorklistType
    _collaborations: Union[Unset, List[CollaborationCreate]] = UNSET
    _worklist_item_ids: Union[Unset, List[str]] = UNSET

    def __repr__(self):
        fields = []
        fields.append("name={}".format(repr(self._name)))
        fields.append("type={}".format(repr(self._type)))
        fields.append("collaborations={}".format(repr(self._collaborations)))
        fields.append("worklist_item_ids={}".format(repr(self._worklist_item_ids)))
        return "WorklistCreate({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        name = self._name
        type = self._type.value

        collaborations: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._collaborations, Unset):
            collaborations = []
            for collaborations_item_data in self._collaborations:
                collaborations_item = collaborations_item_data.to_dict()

                collaborations.append(collaborations_item)

        worklist_item_ids: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._worklist_item_ids, Unset):
            worklist_item_ids = self._worklist_item_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "name": name,
                "type": type,
            }
        )
        if collaborations is not UNSET:
            field_dict["collaborations"] = collaborations
        if worklist_item_ids is not UNSET:
            field_dict["worklistItemIds"] = worklist_item_ids

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_name() -> str:
            name = d.pop("name")
            return name

        name = get_name() if "name" in d else cast(str, UNSET)

        def get_type() -> WorklistType:
            _type = d.pop("type")
            try:
                type = WorklistType(_type)
            except ValueError:
                type = WorklistType.of_unknown(_type)

            return type

        type = get_type() if "type" in d else cast(WorklistType, UNSET)

        def get_collaborations() -> Union[Unset, List[CollaborationCreate]]:
            collaborations = []
            _collaborations = d.pop("collaborations")
            for collaborations_item_data in _collaborations or []:
                collaborations_item = CollaborationCreate.from_dict(collaborations_item_data)

                collaborations.append(collaborations_item)

            return collaborations

        collaborations = (
            get_collaborations()
            if "collaborations" in d
            else cast(Union[Unset, List[CollaborationCreate]], UNSET)
        )

        def get_worklist_item_ids() -> Union[Unset, List[str]]:
            worklist_item_ids = cast(List[str], d.pop("worklistItemIds"))

            return worklist_item_ids

        worklist_item_ids = (
            get_worklist_item_ids() if "worklistItemIds" in d else cast(Union[Unset, List[str]], UNSET)
        )

        worklist_create = cls(
            name=name,
            type=type,
            collaborations=collaborations,
            worklist_item_ids=worklist_item_ids,
        )

        return worklist_create

    @property
    def name(self) -> str:
        """ Name of the worklist """
        if isinstance(self._name, Unset):
            raise NotPresentError(self, "name")
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def type(self) -> WorklistType:
        """The type of items a worklist contains."""
        if isinstance(self._type, Unset):
            raise NotPresentError(self, "type")
        return self._type

    @type.setter
    def type(self, value: WorklistType) -> None:
        self._type = value

    @property
    def collaborations(self) -> List[CollaborationCreate]:
        if isinstance(self._collaborations, Unset):
            raise NotPresentError(self, "collaborations")
        return self._collaborations

    @collaborations.setter
    def collaborations(self, value: List[CollaborationCreate]) -> None:
        self._collaborations = value

    @collaborations.deleter
    def collaborations(self) -> None:
        self._collaborations = UNSET

    @property
    def worklist_item_ids(self) -> List[str]:
        """An ordered set of IDs to assign as worklist items. IDs should reference existing items which fit the worklist's specific type. For instance, a worklist of type container should only have item IDs which represent containers."""
        if isinstance(self._worklist_item_ids, Unset):
            raise NotPresentError(self, "worklist_item_ids")
        return self._worklist_item_ids

    @worklist_item_ids.setter
    def worklist_item_ids(self, value: List[str]) -> None:
        self._worklist_item_ids = value

    @worklist_item_ids.deleter
    def worklist_item_ids(self) -> None:
        self._worklist_item_ids = UNSET
