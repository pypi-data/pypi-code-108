import datetime
from typing import Any, cast, Dict, List, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..extensions import NotPresentError
from ..models.worklist_creator import WorklistCreator
from ..models.worklist_item_summary import WorklistItemSummary
from ..models.worklist_type import WorklistType
from ..types import UNSET, Unset

T = TypeVar("T", bound="Worklist")


@attr.s(auto_attribs=True, repr=False)
class Worklist:
    """A worklist and its items as summaries."""

    _api_url: Union[Unset, str] = UNSET
    _created_at: Union[Unset, datetime.datetime] = UNSET
    _creator: Union[Unset, WorklistCreator] = UNSET
    _id: Union[Unset, str] = UNSET
    _modified_at: Union[Unset, datetime.datetime] = UNSET
    _name: Union[Unset, str] = UNSET
    _type: Union[Unset, WorklistType] = UNSET
    _worklist_items: Union[Unset, List[WorklistItemSummary]] = UNSET

    def __repr__(self):
        fields = []
        fields.append("api_url={}".format(repr(self._api_url)))
        fields.append("created_at={}".format(repr(self._created_at)))
        fields.append("creator={}".format(repr(self._creator)))
        fields.append("id={}".format(repr(self._id)))
        fields.append("modified_at={}".format(repr(self._modified_at)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("type={}".format(repr(self._type)))
        fields.append("worklist_items={}".format(repr(self._worklist_items)))
        return "Worklist({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        api_url = self._api_url
        created_at: Union[Unset, str] = UNSET
        if not isinstance(self._created_at, Unset):
            created_at = self._created_at.isoformat()

        creator: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._creator, Unset):
            creator = self._creator.to_dict()

        id = self._id
        modified_at: Union[Unset, str] = UNSET
        if not isinstance(self._modified_at, Unset):
            modified_at = self._modified_at.isoformat()

        name = self._name
        type: Union[Unset, int] = UNSET
        if not isinstance(self._type, Unset):
            type = self._type.value

        worklist_items: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._worklist_items, Unset):
            worklist_items = []
            for worklist_items_item_data in self._worklist_items:
                worklist_items_item = worklist_items_item_data.to_dict()

                worklist_items.append(worklist_items_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if api_url is not UNSET:
            field_dict["apiURL"] = api_url
        if created_at is not UNSET:
            field_dict["createdAt"] = created_at
        if creator is not UNSET:
            field_dict["creator"] = creator
        if id is not UNSET:
            field_dict["id"] = id
        if modified_at is not UNSET:
            field_dict["modifiedAt"] = modified_at
        if name is not UNSET:
            field_dict["name"] = name
        if type is not UNSET:
            field_dict["type"] = type
        if worklist_items is not UNSET:
            field_dict["worklistItems"] = worklist_items

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_api_url() -> Union[Unset, str]:
            api_url = d.pop("apiURL")
            return api_url

        api_url = get_api_url() if "apiURL" in d else cast(Union[Unset, str], UNSET)

        def get_created_at() -> Union[Unset, datetime.datetime]:
            created_at: Union[Unset, datetime.datetime] = UNSET
            _created_at = d.pop("createdAt")
            if _created_at is not None and not isinstance(_created_at, Unset):
                created_at = isoparse(cast(str, _created_at))

            return created_at

        created_at = get_created_at() if "createdAt" in d else cast(Union[Unset, datetime.datetime], UNSET)

        def get_creator() -> Union[Unset, WorklistCreator]:
            creator: Union[Unset, WorklistCreator] = UNSET
            _creator = d.pop("creator")
            if not isinstance(_creator, Unset):
                creator = WorklistCreator.from_dict(_creator)

            return creator

        creator = get_creator() if "creator" in d else cast(Union[Unset, WorklistCreator], UNSET)

        def get_id() -> Union[Unset, str]:
            id = d.pop("id")
            return id

        id = get_id() if "id" in d else cast(Union[Unset, str], UNSET)

        def get_modified_at() -> Union[Unset, datetime.datetime]:
            modified_at: Union[Unset, datetime.datetime] = UNSET
            _modified_at = d.pop("modifiedAt")
            if _modified_at is not None and not isinstance(_modified_at, Unset):
                modified_at = isoparse(cast(str, _modified_at))

            return modified_at

        modified_at = get_modified_at() if "modifiedAt" in d else cast(Union[Unset, datetime.datetime], UNSET)

        def get_name() -> Union[Unset, str]:
            name = d.pop("name")
            return name

        name = get_name() if "name" in d else cast(Union[Unset, str], UNSET)

        def get_type() -> Union[Unset, WorklistType]:
            type = None
            _type = d.pop("type")
            if _type is not None and _type is not UNSET:
                try:
                    type = WorklistType(_type)
                except ValueError:
                    type = WorklistType.of_unknown(_type)

            return type

        type = get_type() if "type" in d else cast(Union[Unset, WorklistType], UNSET)

        def get_worklist_items() -> Union[Unset, List[WorklistItemSummary]]:
            worklist_items = []
            _worklist_items = d.pop("worklistItems")
            for worklist_items_item_data in _worklist_items or []:
                worklist_items_item = WorklistItemSummary.from_dict(worklist_items_item_data)

                worklist_items.append(worklist_items_item)

            return worklist_items

        worklist_items = (
            get_worklist_items()
            if "worklistItems" in d
            else cast(Union[Unset, List[WorklistItemSummary]], UNSET)
        )

        worklist = cls(
            api_url=api_url,
            created_at=created_at,
            creator=creator,
            id=id,
            modified_at=modified_at,
            name=name,
            type=type,
            worklist_items=worklist_items,
        )

        return worklist

    @property
    def api_url(self) -> str:
        """ The canonical url of the Worklist in the API. """
        if isinstance(self._api_url, Unset):
            raise NotPresentError(self, "api_url")
        return self._api_url

    @api_url.setter
    def api_url(self, value: str) -> None:
        self._api_url = value

    @api_url.deleter
    def api_url(self) -> None:
        self._api_url = UNSET

    @property
    def created_at(self) -> datetime.datetime:
        """ Date and time the worklist was created """
        if isinstance(self._created_at, Unset):
            raise NotPresentError(self, "created_at")
        return self._created_at

    @created_at.setter
    def created_at(self, value: datetime.datetime) -> None:
        self._created_at = value

    @created_at.deleter
    def created_at(self) -> None:
        self._created_at = UNSET

    @property
    def creator(self) -> WorklistCreator:
        if isinstance(self._creator, Unset):
            raise NotPresentError(self, "creator")
        return self._creator

    @creator.setter
    def creator(self, value: WorklistCreator) -> None:
        self._creator = value

    @creator.deleter
    def creator(self) -> None:
        self._creator = UNSET

    @property
    def id(self) -> str:
        """ ID of the worklist """
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
    def modified_at(self) -> datetime.datetime:
        """ Date and time the worklist was last modified """
        if isinstance(self._modified_at, Unset):
            raise NotPresentError(self, "modified_at")
        return self._modified_at

    @modified_at.setter
    def modified_at(self, value: datetime.datetime) -> None:
        self._modified_at = value

    @modified_at.deleter
    def modified_at(self) -> None:
        self._modified_at = UNSET

    @property
    def name(self) -> str:
        """ Name of the worklist """
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
    def type(self) -> WorklistType:
        """The type of items a worklist contains."""
        if isinstance(self._type, Unset):
            raise NotPresentError(self, "type")
        return self._type

    @type.setter
    def type(self, value: WorklistType) -> None:
        self._type = value

    @type.deleter
    def type(self) -> None:
        self._type = UNSET

    @property
    def worklist_items(self) -> List[WorklistItemSummary]:
        if isinstance(self._worklist_items, Unset):
            raise NotPresentError(self, "worklist_items")
        return self._worklist_items

    @worklist_items.setter
    def worklist_items(self, value: List[WorklistItemSummary]) -> None:
        self._worklist_items = value

    @worklist_items.deleter
    def worklist_items(self) -> None:
        self._worklist_items = UNSET
