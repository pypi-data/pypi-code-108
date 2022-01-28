from typing import Any, cast, Dict, List, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.policy_statement import PolicyStatement
from ..types import UNSET, Unset

T = TypeVar("T", bound="AccessPolicy")


@attr.s(auto_attribs=True, repr=False)
class AccessPolicy:
    """  """

    _id: Union[Unset, str] = UNSET
    _name: Union[Unset, str] = UNSET
    _statements: Union[Unset, List[PolicyStatement]] = UNSET

    def __repr__(self):
        fields = []
        fields.append("id={}".format(repr(self._id)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("statements={}".format(repr(self._statements)))
        return "AccessPolicy({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        id = self._id
        name = self._name
        statements: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._statements, Unset):
            statements = []
            for statements_item_data in self._statements:
                statements_item = statements_item_data.to_dict()

                statements.append(statements_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if statements is not UNSET:
            field_dict["statements"] = statements

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

        def get_statements() -> Union[Unset, List[PolicyStatement]]:
            statements = []
            _statements = d.pop("statements")
            for statements_item_data in _statements or []:
                statements_item = PolicyStatement.from_dict(statements_item_data)

                statements.append(statements_item)

            return statements

        statements = (
            get_statements() if "statements" in d else cast(Union[Unset, List[PolicyStatement]], UNSET)
        )

        access_policy = cls(
            id=id,
            name=name,
            statements=statements,
        )

        return access_policy

    @property
    def id(self) -> str:
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
    def statements(self) -> List[PolicyStatement]:
        if isinstance(self._statements, Unset):
            raise NotPresentError(self, "statements")
        return self._statements

    @statements.setter
    def statements(self, value: List[PolicyStatement]) -> None:
        self._statements = value

    @statements.deleter
    def statements(self) -> None:
        self._statements = UNSET
