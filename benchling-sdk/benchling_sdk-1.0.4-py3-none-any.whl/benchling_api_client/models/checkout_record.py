import datetime
from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..extensions import NotPresentError, UnknownType
from ..models.checkout_record_status import CheckoutRecordStatus
from ..models.team_summary import TeamSummary
from ..models.user_summary import UserSummary
from ..types import UNSET, Unset

T = TypeVar("T", bound="CheckoutRecord")


@attr.s(auto_attribs=True, repr=False)
class CheckoutRecord:
    """
    *assignee field* is set if status is "RESERVED" or "CHECKED_OUT", or null if status is "AVAILABLE".

    *comment field* is set when container was last reserved, checked out, or checked into.

    *modifiedAt field* is the date and time when container was last checked out, checked in, or reserved
    """

    _assignee: Union[Unset, None, UserSummary, TeamSummary, UnknownType] = UNSET
    _comment: Union[Unset, str] = UNSET
    _modified_at: Union[Unset, datetime.datetime] = UNSET
    _status: Union[Unset, CheckoutRecordStatus] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("assignee={}".format(repr(self._assignee)))
        fields.append("comment={}".format(repr(self._comment)))
        fields.append("modified_at={}".format(repr(self._modified_at)))
        fields.append("status={}".format(repr(self._status)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "CheckoutRecord({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        assignee: Union[Unset, None, Dict[str, Any]]
        if isinstance(self._assignee, Unset):
            assignee = UNSET
        elif self._assignee is None:
            assignee = None
        elif isinstance(self._assignee, UnknownType):
            assignee = self._assignee.value
        elif isinstance(self._assignee, UserSummary):
            assignee = UNSET
            if not isinstance(self._assignee, Unset):
                assignee = self._assignee.to_dict()

        else:
            assignee = UNSET
            if not isinstance(self._assignee, Unset):
                assignee = self._assignee.to_dict()

        comment = self._comment
        modified_at: Union[Unset, str] = UNSET
        if not isinstance(self._modified_at, Unset):
            modified_at = self._modified_at.isoformat()

        status: Union[Unset, int] = UNSET
        if not isinstance(self._status, Unset):
            status = self._status.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if assignee is not UNSET:
            field_dict["assignee"] = assignee
        if comment is not UNSET:
            field_dict["comment"] = comment
        if modified_at is not UNSET:
            field_dict["modifiedAt"] = modified_at
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_assignee() -> Union[Unset, None, UserSummary, TeamSummary, UnknownType]:
            def _parse_assignee(
                data: Union[Unset, None, Dict[str, Any]]
            ) -> Union[Unset, None, UserSummary, TeamSummary, UnknownType]:
                assignee: Union[Unset, None, UserSummary, TeamSummary, UnknownType]
                if data is None:
                    return data
                if isinstance(data, Unset):
                    return data
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    assignee = UNSET
                    _assignee = data
                    if not isinstance(_assignee, Unset):
                        assignee = UserSummary.from_dict(_assignee)

                    return assignee
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    assignee = UNSET
                    _assignee = data
                    if not isinstance(_assignee, Unset):
                        assignee = TeamSummary.from_dict(_assignee)

                    return assignee
                except:  # noqa: E722
                    pass
                return UnknownType(data)

            assignee = _parse_assignee(d.pop("assignee"))

            return assignee

        assignee = (
            get_assignee()
            if "assignee" in d
            else cast(Union[Unset, None, UserSummary, TeamSummary, UnknownType], UNSET)
        )

        def get_comment() -> Union[Unset, str]:
            comment = d.pop("comment")
            return comment

        comment = get_comment() if "comment" in d else cast(Union[Unset, str], UNSET)

        def get_modified_at() -> Union[Unset, datetime.datetime]:
            modified_at: Union[Unset, datetime.datetime] = UNSET
            _modified_at = d.pop("modifiedAt")
            if _modified_at is not None and not isinstance(_modified_at, Unset):
                modified_at = isoparse(cast(str, _modified_at))

            return modified_at

        modified_at = get_modified_at() if "modifiedAt" in d else cast(Union[Unset, datetime.datetime], UNSET)

        def get_status() -> Union[Unset, CheckoutRecordStatus]:
            status = None
            _status = d.pop("status")
            if _status is not None and _status is not UNSET:
                try:
                    status = CheckoutRecordStatus(_status)
                except ValueError:
                    status = CheckoutRecordStatus.of_unknown(_status)

            return status

        status = get_status() if "status" in d else cast(Union[Unset, CheckoutRecordStatus], UNSET)

        checkout_record = cls(
            assignee=assignee,
            comment=comment,
            modified_at=modified_at,
            status=status,
        )

        checkout_record.additional_properties = d
        return checkout_record

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
    def assignee(self) -> Optional[Union[UserSummary, TeamSummary, UnknownType]]:
        if isinstance(self._assignee, Unset):
            raise NotPresentError(self, "assignee")
        return self._assignee

    @assignee.setter
    def assignee(self, value: Optional[Union[UserSummary, TeamSummary, UnknownType]]) -> None:
        self._assignee = value

    @assignee.deleter
    def assignee(self) -> None:
        self._assignee = UNSET

    @property
    def comment(self) -> str:
        if isinstance(self._comment, Unset):
            raise NotPresentError(self, "comment")
        return self._comment

    @comment.setter
    def comment(self, value: str) -> None:
        self._comment = value

    @comment.deleter
    def comment(self) -> None:
        self._comment = UNSET

    @property
    def modified_at(self) -> datetime.datetime:
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
    def status(self) -> CheckoutRecordStatus:
        if isinstance(self._status, Unset):
            raise NotPresentError(self, "status")
        return self._status

    @status.setter
    def status(self, value: CheckoutRecordStatus) -> None:
        self._status = value

    @status.deleter
    def status(self) -> None:
        self._status = UNSET
