from typing import Any, cast, Dict, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="ExportsAsyncTaskResponse")


@attr.s(auto_attribs=True, repr=False)
class ExportsAsyncTaskResponse:
    """  """

    _download_url: Union[Unset, str] = UNSET

    def __repr__(self):
        fields = []
        fields.append("download_url={}".format(repr(self._download_url)))
        return "ExportsAsyncTaskResponse({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        download_url = self._download_url

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if download_url is not UNSET:
            field_dict["downloadURL"] = download_url

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_download_url() -> Union[Unset, str]:
            download_url = d.pop("downloadURL")
            return download_url

        download_url = get_download_url() if "downloadURL" in d else cast(Union[Unset, str], UNSET)

        exports_async_task_response = cls(
            download_url=download_url,
        )

        return exports_async_task_response

    @property
    def download_url(self) -> str:
        if isinstance(self._download_url, Unset):
            raise NotPresentError(self, "download_url")
        return self._download_url

    @download_url.setter
    def download_url(self, value: str) -> None:
        self._download_url = value

    @download_url.deleter
    def download_url(self) -> None:
        self._download_url = UNSET
