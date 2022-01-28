import datetime
from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..extensions import NotPresentError, UnknownType
from ..models.fields import Fields
from ..models.request_creator import RequestCreator
from ..models.request_requestor import RequestRequestor
from ..models.request_sample_group import RequestSampleGroup
from ..models.request_schema_property import RequestSchemaProperty
from ..models.request_status import RequestStatus
from ..models.request_task import RequestTask
from ..models.request_team_assignee import RequestTeamAssignee
from ..models.request_user_assignee import RequestUserAssignee
from ..types import UNSET, Unset

T = TypeVar("T", bound="Request")


@attr.s(auto_attribs=True, repr=False)
class Request:
    """  """

    _api_url: Union[Unset, str] = UNSET
    _assignees: Union[Unset, List[Union[RequestUserAssignee, RequestTeamAssignee, UnknownType]]] = UNSET
    _created_at: Union[Unset, str] = UNSET
    _creator: Union[Unset, RequestCreator] = UNSET
    _display_id: Union[Unset, str] = UNSET
    _fields: Union[Unset, Fields] = UNSET
    _id: Union[Unset, str] = UNSET
    _project_id: Union[Unset, str] = UNSET
    _request_status: Union[Unset, RequestStatus] = UNSET
    _requestor: Union[Unset, RequestRequestor] = UNSET
    _sample_groups: Union[Unset, List[RequestSampleGroup]] = UNSET
    _scheduled_on: Union[Unset, None, datetime.date] = UNSET
    _schema: Union[Unset, RequestSchemaProperty] = UNSET
    _tasks: Union[Unset, List[RequestTask]] = UNSET
    _web_url: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("api_url={}".format(repr(self._api_url)))
        fields.append("assignees={}".format(repr(self._assignees)))
        fields.append("created_at={}".format(repr(self._created_at)))
        fields.append("creator={}".format(repr(self._creator)))
        fields.append("display_id={}".format(repr(self._display_id)))
        fields.append("fields={}".format(repr(self._fields)))
        fields.append("id={}".format(repr(self._id)))
        fields.append("project_id={}".format(repr(self._project_id)))
        fields.append("request_status={}".format(repr(self._request_status)))
        fields.append("requestor={}".format(repr(self._requestor)))
        fields.append("sample_groups={}".format(repr(self._sample_groups)))
        fields.append("scheduled_on={}".format(repr(self._scheduled_on)))
        fields.append("schema={}".format(repr(self._schema)))
        fields.append("tasks={}".format(repr(self._tasks)))
        fields.append("web_url={}".format(repr(self._web_url)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "Request({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        api_url = self._api_url
        assignees: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._assignees, Unset):
            assignees = []
            for assignees_item_data in self._assignees:
                if isinstance(assignees_item_data, UnknownType):
                    assignees_item = assignees_item_data.value
                elif isinstance(assignees_item_data, RequestUserAssignee):
                    assignees_item = assignees_item_data.to_dict()

                else:
                    assignees_item = assignees_item_data.to_dict()

                assignees.append(assignees_item)

        created_at = self._created_at
        creator: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._creator, Unset):
            creator = self._creator.to_dict()

        display_id = self._display_id
        fields: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._fields, Unset):
            fields = self._fields.to_dict()

        id = self._id
        project_id = self._project_id
        request_status: Union[Unset, int] = UNSET
        if not isinstance(self._request_status, Unset):
            request_status = self._request_status.value

        requestor: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._requestor, Unset):
            requestor = self._requestor.to_dict()

        sample_groups: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._sample_groups, Unset):
            sample_groups = []
            for sample_groups_item_data in self._sample_groups:
                sample_groups_item = sample_groups_item_data.to_dict()

                sample_groups.append(sample_groups_item)

        scheduled_on: Union[Unset, None, str] = UNSET
        if not isinstance(self._scheduled_on, Unset):
            scheduled_on = self._scheduled_on.isoformat() if self._scheduled_on else None

        schema: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._schema, Unset):
            schema = self._schema.to_dict()

        tasks: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._tasks, Unset):
            tasks = []
            for tasks_item_data in self._tasks:
                tasks_item = tasks_item_data.to_dict()

                tasks.append(tasks_item)

        web_url = self._web_url

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if api_url is not UNSET:
            field_dict["apiURL"] = api_url
        if assignees is not UNSET:
            field_dict["assignees"] = assignees
        if created_at is not UNSET:
            field_dict["createdAt"] = created_at
        if creator is not UNSET:
            field_dict["creator"] = creator
        if display_id is not UNSET:
            field_dict["displayId"] = display_id
        if fields is not UNSET:
            field_dict["fields"] = fields
        if id is not UNSET:
            field_dict["id"] = id
        if project_id is not UNSET:
            field_dict["projectId"] = project_id
        if request_status is not UNSET:
            field_dict["requestStatus"] = request_status
        if requestor is not UNSET:
            field_dict["requestor"] = requestor
        if sample_groups is not UNSET:
            field_dict["sampleGroups"] = sample_groups
        if scheduled_on is not UNSET:
            field_dict["scheduledOn"] = scheduled_on
        if schema is not UNSET:
            field_dict["schema"] = schema
        if tasks is not UNSET:
            field_dict["tasks"] = tasks
        if web_url is not UNSET:
            field_dict["webURL"] = web_url

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_api_url() -> Union[Unset, str]:
            api_url = d.pop("apiURL")
            return api_url

        api_url = get_api_url() if "apiURL" in d else cast(Union[Unset, str], UNSET)

        def get_assignees() -> Union[
            Unset, List[Union[RequestUserAssignee, RequestTeamAssignee, UnknownType]]
        ]:
            assignees = []
            _assignees = d.pop("assignees")
            for assignees_item_data in _assignees or []:

                def _parse_assignees_item(
                    data: Union[Dict[str, Any]]
                ) -> Union[RequestUserAssignee, RequestTeamAssignee, UnknownType]:
                    assignees_item: Union[RequestUserAssignee, RequestTeamAssignee, UnknownType]
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        assignees_item = RequestUserAssignee.from_dict(data)

                        return assignees_item
                    except:  # noqa: E722
                        pass
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        assignees_item = RequestTeamAssignee.from_dict(data)

                        return assignees_item
                    except:  # noqa: E722
                        pass
                    return UnknownType(data)

                assignees_item = _parse_assignees_item(assignees_item_data)

                assignees.append(assignees_item)

            return assignees

        assignees = (
            get_assignees()
            if "assignees" in d
            else cast(Union[Unset, List[Union[RequestUserAssignee, RequestTeamAssignee, UnknownType]]], UNSET)
        )

        def get_created_at() -> Union[Unset, str]:
            created_at = d.pop("createdAt")
            return created_at

        created_at = get_created_at() if "createdAt" in d else cast(Union[Unset, str], UNSET)

        def get_creator() -> Union[Unset, RequestCreator]:
            creator: Union[Unset, RequestCreator] = UNSET
            _creator = d.pop("creator")
            if not isinstance(_creator, Unset):
                creator = RequestCreator.from_dict(_creator)

            return creator

        creator = get_creator() if "creator" in d else cast(Union[Unset, RequestCreator], UNSET)

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

        def get_id() -> Union[Unset, str]:
            id = d.pop("id")
            return id

        id = get_id() if "id" in d else cast(Union[Unset, str], UNSET)

        def get_project_id() -> Union[Unset, str]:
            project_id = d.pop("projectId")
            return project_id

        project_id = get_project_id() if "projectId" in d else cast(Union[Unset, str], UNSET)

        def get_request_status() -> Union[Unset, RequestStatus]:
            request_status = None
            _request_status = d.pop("requestStatus")
            if _request_status is not None and _request_status is not UNSET:
                try:
                    request_status = RequestStatus(_request_status)
                except ValueError:
                    request_status = RequestStatus.of_unknown(_request_status)

            return request_status

        request_status = (
            get_request_status() if "requestStatus" in d else cast(Union[Unset, RequestStatus], UNSET)
        )

        def get_requestor() -> Union[Unset, RequestRequestor]:
            requestor: Union[Unset, RequestRequestor] = UNSET
            _requestor = d.pop("requestor")
            if not isinstance(_requestor, Unset):
                requestor = RequestRequestor.from_dict(_requestor)

            return requestor

        requestor = get_requestor() if "requestor" in d else cast(Union[Unset, RequestRequestor], UNSET)

        def get_sample_groups() -> Union[Unset, List[RequestSampleGroup]]:
            sample_groups = []
            _sample_groups = d.pop("sampleGroups")
            for sample_groups_item_data in _sample_groups or []:
                sample_groups_item = RequestSampleGroup.from_dict(sample_groups_item_data)

                sample_groups.append(sample_groups_item)

            return sample_groups

        sample_groups = (
            get_sample_groups()
            if "sampleGroups" in d
            else cast(Union[Unset, List[RequestSampleGroup]], UNSET)
        )

        def get_scheduled_on() -> Union[Unset, None, datetime.date]:
            scheduled_on: Union[Unset, None, datetime.date] = UNSET
            _scheduled_on = d.pop("scheduledOn")
            if _scheduled_on is not None and not isinstance(_scheduled_on, Unset):
                scheduled_on = isoparse(cast(str, _scheduled_on)).date()

            return scheduled_on

        scheduled_on = (
            get_scheduled_on() if "scheduledOn" in d else cast(Union[Unset, None, datetime.date], UNSET)
        )

        def get_schema() -> Union[Unset, RequestSchemaProperty]:
            schema: Union[Unset, RequestSchemaProperty] = UNSET
            _schema = d.pop("schema")
            if not isinstance(_schema, Unset):
                schema = RequestSchemaProperty.from_dict(_schema)

            return schema

        schema = get_schema() if "schema" in d else cast(Union[Unset, RequestSchemaProperty], UNSET)

        def get_tasks() -> Union[Unset, List[RequestTask]]:
            tasks = []
            _tasks = d.pop("tasks")
            for tasks_item_data in _tasks or []:
                tasks_item = RequestTask.from_dict(tasks_item_data)

                tasks.append(tasks_item)

            return tasks

        tasks = get_tasks() if "tasks" in d else cast(Union[Unset, List[RequestTask]], UNSET)

        def get_web_url() -> Union[Unset, str]:
            web_url = d.pop("webURL")
            return web_url

        web_url = get_web_url() if "webURL" in d else cast(Union[Unset, str], UNSET)

        request = cls(
            api_url=api_url,
            assignees=assignees,
            created_at=created_at,
            creator=creator,
            display_id=display_id,
            fields=fields,
            id=id,
            project_id=project_id,
            request_status=request_status,
            requestor=requestor,
            sample_groups=sample_groups,
            scheduled_on=scheduled_on,
            schema=schema,
            tasks=tasks,
            web_url=web_url,
        )

        request.additional_properties = d
        return request

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
    def api_url(self) -> str:
        """ The canonical url of the Request in the API. """
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
    def assignees(self) -> List[Union[RequestUserAssignee, RequestTeamAssignee, UnknownType]]:
        """ Array of assignees """
        if isinstance(self._assignees, Unset):
            raise NotPresentError(self, "assignees")
        return self._assignees

    @assignees.setter
    def assignees(self, value: List[Union[RequestUserAssignee, RequestTeamAssignee, UnknownType]]) -> None:
        self._assignees = value

    @assignees.deleter
    def assignees(self) -> None:
        self._assignees = UNSET

    @property
    def created_at(self) -> str:
        """ Date and time the request was created """
        if isinstance(self._created_at, Unset):
            raise NotPresentError(self, "created_at")
        return self._created_at

    @created_at.setter
    def created_at(self, value: str) -> None:
        self._created_at = value

    @created_at.deleter
    def created_at(self) -> None:
        self._created_at = UNSET

    @property
    def creator(self) -> RequestCreator:
        if isinstance(self._creator, Unset):
            raise NotPresentError(self, "creator")
        return self._creator

    @creator.setter
    def creator(self, value: RequestCreator) -> None:
        self._creator = value

    @creator.deleter
    def creator(self) -> None:
        self._creator = UNSET

    @property
    def display_id(self) -> str:
        """ User-friendly ID of the request """
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
    def id(self) -> str:
        """ Unique ID for the request """
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
    def project_id(self) -> str:
        """ The ID of the project to which the request belongs. """
        if isinstance(self._project_id, Unset):
            raise NotPresentError(self, "project_id")
        return self._project_id

    @project_id.setter
    def project_id(self, value: str) -> None:
        self._project_id = value

    @project_id.deleter
    def project_id(self) -> None:
        self._project_id = UNSET

    @property
    def request_status(self) -> RequestStatus:
        if isinstance(self._request_status, Unset):
            raise NotPresentError(self, "request_status")
        return self._request_status

    @request_status.setter
    def request_status(self, value: RequestStatus) -> None:
        self._request_status = value

    @request_status.deleter
    def request_status(self) -> None:
        self._request_status = UNSET

    @property
    def requestor(self) -> RequestRequestor:
        if isinstance(self._requestor, Unset):
            raise NotPresentError(self, "requestor")
        return self._requestor

    @requestor.setter
    def requestor(self, value: RequestRequestor) -> None:
        self._requestor = value

    @requestor.deleter
    def requestor(self) -> None:
        self._requestor = UNSET

    @property
    def sample_groups(self) -> List[RequestSampleGroup]:
        if isinstance(self._sample_groups, Unset):
            raise NotPresentError(self, "sample_groups")
        return self._sample_groups

    @sample_groups.setter
    def sample_groups(self, value: List[RequestSampleGroup]) -> None:
        self._sample_groups = value

    @sample_groups.deleter
    def sample_groups(self) -> None:
        self._sample_groups = UNSET

    @property
    def scheduled_on(self) -> Optional[datetime.date]:
        """ Date the request is scheduled to be executed on, in YYYY-MM-DD format. """
        if isinstance(self._scheduled_on, Unset):
            raise NotPresentError(self, "scheduled_on")
        return self._scheduled_on

    @scheduled_on.setter
    def scheduled_on(self, value: Optional[datetime.date]) -> None:
        self._scheduled_on = value

    @scheduled_on.deleter
    def scheduled_on(self) -> None:
        self._scheduled_on = UNSET

    @property
    def schema(self) -> RequestSchemaProperty:
        if isinstance(self._schema, Unset):
            raise NotPresentError(self, "schema")
        return self._schema

    @schema.setter
    def schema(self, value: RequestSchemaProperty) -> None:
        self._schema = value

    @schema.deleter
    def schema(self) -> None:
        self._schema = UNSET

    @property
    def tasks(self) -> List[RequestTask]:
        if isinstance(self._tasks, Unset):
            raise NotPresentError(self, "tasks")
        return self._tasks

    @tasks.setter
    def tasks(self, value: List[RequestTask]) -> None:
        self._tasks = value

    @tasks.deleter
    def tasks(self) -> None:
        self._tasks = UNSET

    @property
    def web_url(self) -> str:
        """ URL of the request """
        if isinstance(self._web_url, Unset):
            raise NotPresentError(self, "web_url")
        return self._web_url

    @web_url.setter
    def web_url(self, value: str) -> None:
        self._web_url = value

    @web_url.deleter
    def web_url(self) -> None:
        self._web_url = UNSET
