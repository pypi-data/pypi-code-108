from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.async_task_errors import AsyncTaskErrors
from ..models.async_task_status import AsyncTaskStatus
from ..models.bulk_create_dna_oligos_async_task_response import BulkCreateDnaOligosAsyncTaskResponse
from ..types import UNSET, Unset

T = TypeVar("T", bound="BulkCreateDnaOligosAsyncTask")


@attr.s(auto_attribs=True, repr=False)
class BulkCreateDnaOligosAsyncTask:
    """  """

    _status: AsyncTaskStatus
    _response: Union[Unset, BulkCreateDnaOligosAsyncTaskResponse] = UNSET
    _errors: Union[Unset, AsyncTaskErrors] = UNSET
    _message: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("status={}".format(repr(self._status)))
        fields.append("response={}".format(repr(self._response)))
        fields.append("errors={}".format(repr(self._errors)))
        fields.append("message={}".format(repr(self._message)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "BulkCreateDnaOligosAsyncTask({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        status = self._status.value

        response: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._response, Unset):
            response = self._response.to_dict()

        errors: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._errors, Unset):
            errors = self._errors.to_dict()

        message = self._message

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "status": status,
            }
        )
        if response is not UNSET:
            field_dict["response"] = response
        if errors is not UNSET:
            field_dict["errors"] = errors
        if message is not UNSET:
            field_dict["message"] = message

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_status() -> AsyncTaskStatus:
            _status = d.pop("status")
            try:
                status = AsyncTaskStatus(_status)
            except ValueError:
                status = AsyncTaskStatus.of_unknown(_status)

            return status

        status = get_status() if "status" in d else cast(AsyncTaskStatus, UNSET)

        def get_response() -> Union[Unset, BulkCreateDnaOligosAsyncTaskResponse]:
            response: Union[Unset, BulkCreateDnaOligosAsyncTaskResponse] = UNSET
            _response = d.pop("response")
            if not isinstance(_response, Unset):
                response = BulkCreateDnaOligosAsyncTaskResponse.from_dict(_response)

            return response

        response = (
            get_response()
            if "response" in d
            else cast(Union[Unset, BulkCreateDnaOligosAsyncTaskResponse], UNSET)
        )

        def get_errors() -> Union[Unset, AsyncTaskErrors]:
            errors: Union[Unset, AsyncTaskErrors] = UNSET
            _errors = d.pop("errors")
            if not isinstance(_errors, Unset):
                errors = AsyncTaskErrors.from_dict(_errors)

            return errors

        errors = get_errors() if "errors" in d else cast(Union[Unset, AsyncTaskErrors], UNSET)

        def get_message() -> Union[Unset, str]:
            message = d.pop("message")
            return message

        message = get_message() if "message" in d else cast(Union[Unset, str], UNSET)

        bulk_create_dna_oligos_async_task = cls(
            status=status,
            response=response,
            errors=errors,
            message=message,
        )

        bulk_create_dna_oligos_async_task.additional_properties = d
        return bulk_create_dna_oligos_async_task

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
    def status(self) -> AsyncTaskStatus:
        """ The current state of the task. """
        if isinstance(self._status, Unset):
            raise NotPresentError(self, "status")
        return self._status

    @status.setter
    def status(self, value: AsyncTaskStatus) -> None:
        self._status = value

    @property
    def response(self) -> BulkCreateDnaOligosAsyncTaskResponse:
        if isinstance(self._response, Unset):
            raise NotPresentError(self, "response")
        return self._response

    @response.setter
    def response(self, value: BulkCreateDnaOligosAsyncTaskResponse) -> None:
        self._response = value

    @response.deleter
    def response(self) -> None:
        self._response = UNSET

    @property
    def errors(self) -> AsyncTaskErrors:
        """Present only when status is FAILED for a bulk task. Contains information about the individual errors in the bulk task."""
        if isinstance(self._errors, Unset):
            raise NotPresentError(self, "errors")
        return self._errors

    @errors.setter
    def errors(self, value: AsyncTaskErrors) -> None:
        self._errors = value

    @errors.deleter
    def errors(self) -> None:
        self._errors = UNSET

    @property
    def message(self) -> str:
        """ Present only when status is FAILED. Contains information about the error. """
        if isinstance(self._message, Unset):
            raise NotPresentError(self, "message")
        return self._message

    @message.setter
    def message(self, value: str) -> None:
        self._message = value

    @message.deleter
    def message(self) -> None:
        self._message = UNSET
