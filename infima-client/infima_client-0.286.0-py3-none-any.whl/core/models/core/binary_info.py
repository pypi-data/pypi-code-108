from typing import (
    Any,
    BinaryIO,
    Dict,
    List,
    Optional,
    TextIO,
    Tuple,
    Type,
    TypeVar,
    Union,
)

from attr import define, field

from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="CoreBinaryInfo")


@define(auto_attribs=True)
class CoreBinaryInfo:
    """
    Attributes:
        binary (Union[Unset, str]):
        build_on (Union[Unset, str]):
        git_commit (Union[Unset, str]):
        git_hash (Union[Unset, str]):
        sem_version (Union[Unset, str]):
    """

    binary: Union[Unset, str] = UNSET
    build_on: Union[Unset, str] = UNSET
    git_commit: Union[Unset, str] = UNSET
    git_hash: Union[Unset, str] = UNSET
    sem_version: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        binary = self.binary
        build_on = self.build_on
        git_commit = self.git_commit
        git_hash = self.git_hash
        sem_version = self.sem_version

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if binary is not UNSET:
            field_dict["binary"] = binary
        if build_on is not UNSET:
            field_dict["buildOn"] = build_on
        if git_commit is not UNSET:
            field_dict["gitCommit"] = git_commit
        if git_hash is not UNSET:
            field_dict["gitHash"] = git_hash
        if sem_version is not UNSET:
            field_dict["semVersion"] = sem_version

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        binary = d.pop("binary", UNSET)

        build_on = d.pop("buildOn", UNSET)

        git_commit = d.pop("gitCommit", UNSET)

        git_hash = d.pop("gitHash", UNSET)

        sem_version = d.pop("semVersion", UNSET)

        core_binary_info = cls(
            binary=binary,
            build_on=build_on,
            git_commit=git_commit,
            git_hash=git_hash,
            sem_version=sem_version,
        )

        core_binary_info.additional_properties = d
        return core_binary_info

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
