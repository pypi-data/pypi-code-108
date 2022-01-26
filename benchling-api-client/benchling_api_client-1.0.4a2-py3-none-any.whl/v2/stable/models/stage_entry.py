import datetime
from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..extensions import NotPresentError
from ..models.custom_fields import CustomFields
from ..models.entry_schema import EntrySchema
from ..models.fields import Fields
from ..models.stage_entry_review_record import StageEntryReviewRecord
from ..models.user_summary import UserSummary
from ..types import UNSET, Unset

T = TypeVar("T", bound="StageEntry")


@attr.s(auto_attribs=True, repr=False)
class StageEntry:
    """ A notebook entry used for execution of one or more stage runs in a legacy workflow. """

    _api_url: Union[Unset, str] = UNSET
    _authors: Union[Unset, List[UserSummary]] = UNSET
    _created_at: Union[Unset, datetime.datetime] = UNSET
    _creator: Union[Unset, UserSummary] = UNSET
    _custom_fields: Union[Unset, CustomFields] = UNSET
    _display_id: Union[Unset, str] = UNSET
    _fields: Union[Unset, Fields] = UNSET
    _folder_id: Union[Unset, str] = UNSET
    _id: Union[Unset, str] = UNSET
    _modified_at: Union[Unset, str] = UNSET
    _name: Union[Unset, str] = UNSET
    _review_record: Union[Unset, None, StageEntryReviewRecord] = UNSET
    _schema: Union[Unset, None, EntrySchema] = UNSET
    _web_url: Union[Unset, str] = UNSET
    _workflow_id: Union[Unset, str] = UNSET
    _workflow_stage_id: Union[Unset, str] = UNSET

    def __repr__(self):
        fields = []
        fields.append("api_url={}".format(repr(self._api_url)))
        fields.append("authors={}".format(repr(self._authors)))
        fields.append("created_at={}".format(repr(self._created_at)))
        fields.append("creator={}".format(repr(self._creator)))
        fields.append("custom_fields={}".format(repr(self._custom_fields)))
        fields.append("display_id={}".format(repr(self._display_id)))
        fields.append("fields={}".format(repr(self._fields)))
        fields.append("folder_id={}".format(repr(self._folder_id)))
        fields.append("id={}".format(repr(self._id)))
        fields.append("modified_at={}".format(repr(self._modified_at)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("review_record={}".format(repr(self._review_record)))
        fields.append("schema={}".format(repr(self._schema)))
        fields.append("web_url={}".format(repr(self._web_url)))
        fields.append("workflow_id={}".format(repr(self._workflow_id)))
        fields.append("workflow_stage_id={}".format(repr(self._workflow_stage_id)))
        return "StageEntry({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        api_url = self._api_url
        authors: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._authors, Unset):
            authors = []
            for authors_item_data in self._authors:
                authors_item = authors_item_data.to_dict()

                authors.append(authors_item)

        created_at: Union[Unset, str] = UNSET
        if not isinstance(self._created_at, Unset):
            created_at = self._created_at.isoformat()

        creator: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._creator, Unset):
            creator = self._creator.to_dict()

        custom_fields: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._custom_fields, Unset):
            custom_fields = self._custom_fields.to_dict()

        display_id = self._display_id
        fields: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._fields, Unset):
            fields = self._fields.to_dict()

        folder_id = self._folder_id
        id = self._id
        modified_at = self._modified_at
        name = self._name
        review_record: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self._review_record, Unset):
            review_record = self._review_record.to_dict() if self._review_record else None

        schema: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self._schema, Unset):
            schema = self._schema.to_dict() if self._schema else None

        web_url = self._web_url
        workflow_id = self._workflow_id
        workflow_stage_id = self._workflow_stage_id

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if api_url is not UNSET:
            field_dict["apiURL"] = api_url
        if authors is not UNSET:
            field_dict["authors"] = authors
        if created_at is not UNSET:
            field_dict["createdAt"] = created_at
        if creator is not UNSET:
            field_dict["creator"] = creator
        if custom_fields is not UNSET:
            field_dict["customFields"] = custom_fields
        if display_id is not UNSET:
            field_dict["displayId"] = display_id
        if fields is not UNSET:
            field_dict["fields"] = fields
        if folder_id is not UNSET:
            field_dict["folderId"] = folder_id
        if id is not UNSET:
            field_dict["id"] = id
        if modified_at is not UNSET:
            field_dict["modifiedAt"] = modified_at
        if name is not UNSET:
            field_dict["name"] = name
        if review_record is not UNSET:
            field_dict["reviewRecord"] = review_record
        if schema is not UNSET:
            field_dict["schema"] = schema
        if web_url is not UNSET:
            field_dict["webURL"] = web_url
        if workflow_id is not UNSET:
            field_dict["workflowId"] = workflow_id
        if workflow_stage_id is not UNSET:
            field_dict["workflowStageId"] = workflow_stage_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_api_url() -> Union[Unset, str]:
            api_url = d.pop("apiURL")
            return api_url

        api_url = get_api_url() if "apiURL" in d else cast(Union[Unset, str], UNSET)

        def get_authors() -> Union[Unset, List[UserSummary]]:
            authors = []
            _authors = d.pop("authors")
            for authors_item_data in _authors or []:
                authors_item = UserSummary.from_dict(authors_item_data)

                authors.append(authors_item)

            return authors

        authors = get_authors() if "authors" in d else cast(Union[Unset, List[UserSummary]], UNSET)

        def get_created_at() -> Union[Unset, datetime.datetime]:
            created_at: Union[Unset, datetime.datetime] = UNSET
            _created_at = d.pop("createdAt")
            if _created_at is not None and not isinstance(_created_at, Unset):
                created_at = isoparse(cast(str, _created_at))

            return created_at

        created_at = get_created_at() if "createdAt" in d else cast(Union[Unset, datetime.datetime], UNSET)

        def get_creator() -> Union[Unset, UserSummary]:
            creator: Union[Unset, UserSummary] = UNSET
            _creator = d.pop("creator")
            if not isinstance(_creator, Unset):
                creator = UserSummary.from_dict(_creator)

            return creator

        creator = get_creator() if "creator" in d else cast(Union[Unset, UserSummary], UNSET)

        def get_custom_fields() -> Union[Unset, CustomFields]:
            custom_fields: Union[Unset, CustomFields] = UNSET
            _custom_fields = d.pop("customFields")
            if not isinstance(_custom_fields, Unset):
                custom_fields = CustomFields.from_dict(_custom_fields)

            return custom_fields

        custom_fields = (
            get_custom_fields() if "customFields" in d else cast(Union[Unset, CustomFields], UNSET)
        )

        def get_display_id() -> Union[Unset, str]:
            display_id = d.pop("displayId")
            return display_id

        display_id = get_display_id() if "displayId" in d else cast(Union[Unset, str], UNSET)

        def get_fields() -> Union[Unset, Fields]:
            fields: Union[Unset, Fields] = UNSET
            _fields = d.pop("fields")
            if not isinstance(_fields, Unset):
                fields = Fields.from_dict(_fields)

            return fields

        fields = get_fields() if "fields" in d else cast(Union[Unset, Fields], UNSET)

        def get_folder_id() -> Union[Unset, str]:
            folder_id = d.pop("folderId")
            return folder_id

        folder_id = get_folder_id() if "folderId" in d else cast(Union[Unset, str], UNSET)

        def get_id() -> Union[Unset, str]:
            id = d.pop("id")
            return id

        id = get_id() if "id" in d else cast(Union[Unset, str], UNSET)

        def get_modified_at() -> Union[Unset, str]:
            modified_at = d.pop("modifiedAt")
            return modified_at

        modified_at = get_modified_at() if "modifiedAt" in d else cast(Union[Unset, str], UNSET)

        def get_name() -> Union[Unset, str]:
            name = d.pop("name")
            return name

        name = get_name() if "name" in d else cast(Union[Unset, str], UNSET)

        def get_review_record() -> Union[Unset, None, StageEntryReviewRecord]:
            review_record = None
            _review_record = d.pop("reviewRecord")
            if _review_record is not None and not isinstance(_review_record, Unset):
                review_record = StageEntryReviewRecord.from_dict(_review_record)

            return review_record

        review_record = (
            get_review_record()
            if "reviewRecord" in d
            else cast(Union[Unset, None, StageEntryReviewRecord], UNSET)
        )

        def get_schema() -> Union[Unset, None, EntrySchema]:
            schema = None
            _schema = d.pop("schema")
            if _schema is not None and not isinstance(_schema, Unset):
                schema = EntrySchema.from_dict(_schema)

            return schema

        schema = get_schema() if "schema" in d else cast(Union[Unset, None, EntrySchema], UNSET)

        def get_web_url() -> Union[Unset, str]:
            web_url = d.pop("webURL")
            return web_url

        web_url = get_web_url() if "webURL" in d else cast(Union[Unset, str], UNSET)

        def get_workflow_id() -> Union[Unset, str]:
            workflow_id = d.pop("workflowId")
            return workflow_id

        workflow_id = get_workflow_id() if "workflowId" in d else cast(Union[Unset, str], UNSET)

        def get_workflow_stage_id() -> Union[Unset, str]:
            workflow_stage_id = d.pop("workflowStageId")
            return workflow_stage_id

        workflow_stage_id = (
            get_workflow_stage_id() if "workflowStageId" in d else cast(Union[Unset, str], UNSET)
        )

        stage_entry = cls(
            api_url=api_url,
            authors=authors,
            created_at=created_at,
            creator=creator,
            custom_fields=custom_fields,
            display_id=display_id,
            fields=fields,
            folder_id=folder_id,
            id=id,
            modified_at=modified_at,
            name=name,
            review_record=review_record,
            schema=schema,
            web_url=web_url,
            workflow_id=workflow_id,
            workflow_stage_id=workflow_stage_id,
        )

        return stage_entry

    @property
    def api_url(self) -> str:
        """ The canonical url of the Stage Entry in the API. """
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
    def authors(self) -> List[UserSummary]:
        """Array of UserSummary Resources of the authors of the stage entry. This defaults to the creator but can be manually changed."""
        if isinstance(self._authors, Unset):
            raise NotPresentError(self, "authors")
        return self._authors

    @authors.setter
    def authors(self, value: List[UserSummary]) -> None:
        self._authors = value

    @authors.deleter
    def authors(self) -> None:
        self._authors = UNSET

    @property
    def created_at(self) -> datetime.datetime:
        """ DateTime the stage entry was created at """
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
    def creator(self) -> UserSummary:
        if isinstance(self._creator, Unset):
            raise NotPresentError(self, "creator")
        return self._creator

    @creator.setter
    def creator(self, value: UserSummary) -> None:
        self._creator = value

    @creator.deleter
    def creator(self) -> None:
        self._creator = UNSET

    @property
    def custom_fields(self) -> CustomFields:
        if isinstance(self._custom_fields, Unset):
            raise NotPresentError(self, "custom_fields")
        return self._custom_fields

    @custom_fields.setter
    def custom_fields(self, value: CustomFields) -> None:
        self._custom_fields = value

    @custom_fields.deleter
    def custom_fields(self) -> None:
        self._custom_fields = UNSET

    @property
    def display_id(self) -> str:
        """ User-friendly ID of the stage entry """
        if isinstance(self._display_id, Unset):
            raise NotPresentError(self, "display_id")
        return self._display_id

    @display_id.setter
    def display_id(self, value: str) -> None:
        self._display_id = value

    @display_id.deleter
    def display_id(self) -> None:
        self._display_id = UNSET

    @property
    def fields(self) -> Fields:
        if isinstance(self._fields, Unset):
            raise NotPresentError(self, "fields")
        return self._fields

    @fields.setter
    def fields(self, value: Fields) -> None:
        self._fields = value

    @fields.deleter
    def fields(self) -> None:
        self._fields = UNSET

    @property
    def folder_id(self) -> str:
        """ ID of the folder that contains the stage entry """
        if isinstance(self._folder_id, Unset):
            raise NotPresentError(self, "folder_id")
        return self._folder_id

    @folder_id.setter
    def folder_id(self, value: str) -> None:
        self._folder_id = value

    @folder_id.deleter
    def folder_id(self) -> None:
        self._folder_id = UNSET

    @property
    def id(self) -> str:
        """ ID of the stage entry """
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
    def modified_at(self) -> str:
        """ DateTime the stage entry was last modified """
        if isinstance(self._modified_at, Unset):
            raise NotPresentError(self, "modified_at")
        return self._modified_at

    @modified_at.setter
    def modified_at(self, value: str) -> None:
        self._modified_at = value

    @modified_at.deleter
    def modified_at(self) -> None:
        self._modified_at = UNSET

    @property
    def name(self) -> str:
        """ Title of the stage entry """
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
    def review_record(self) -> Optional[StageEntryReviewRecord]:
        """ Review record if set """
        if isinstance(self._review_record, Unset):
            raise NotPresentError(self, "review_record")
        return self._review_record

    @review_record.setter
    def review_record(self, value: Optional[StageEntryReviewRecord]) -> None:
        self._review_record = value

    @review_record.deleter
    def review_record(self) -> None:
        self._review_record = UNSET

    @property
    def schema(self) -> Optional[EntrySchema]:
        """ Entry schema """
        if isinstance(self._schema, Unset):
            raise NotPresentError(self, "schema")
        return self._schema

    @schema.setter
    def schema(self, value: Optional[EntrySchema]) -> None:
        self._schema = value

    @schema.deleter
    def schema(self) -> None:
        self._schema = UNSET

    @property
    def web_url(self) -> str:
        """ URL of the stage entry """
        if isinstance(self._web_url, Unset):
            raise NotPresentError(self, "web_url")
        return self._web_url

    @web_url.setter
    def web_url(self, value: str) -> None:
        self._web_url = value

    @web_url.deleter
    def web_url(self) -> None:
        self._web_url = UNSET

    @property
    def workflow_id(self) -> str:
        """ ID of the parent workflow """
        if isinstance(self._workflow_id, Unset):
            raise NotPresentError(self, "workflow_id")
        return self._workflow_id

    @workflow_id.setter
    def workflow_id(self, value: str) -> None:
        self._workflow_id = value

    @workflow_id.deleter
    def workflow_id(self) -> None:
        self._workflow_id = UNSET

    @property
    def workflow_stage_id(self) -> str:
        """ ID of the associated workflow stage """
        if isinstance(self._workflow_stage_id, Unset):
            raise NotPresentError(self, "workflow_stage_id")
        return self._workflow_stage_id

    @workflow_stage_id.setter
    def workflow_stage_id(self, value: str) -> None:
        self._workflow_stage_id = value

    @workflow_stage_id.deleter
    def workflow_stage_id(self) -> None:
        self._workflow_stage_id = UNSET
