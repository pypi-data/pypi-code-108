from typing import Any, cast, Dict, List, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..models.benchling_apps_archive_reason import BenchlingAppsArchiveReason
from ..types import UNSET, Unset

T = TypeVar("T", bound="BenchlingAppsArchive")


@attr.s(auto_attribs=True, repr=False)
class BenchlingAppsArchive:
    """  """

    _app_ids: List[str]
    _reason: BenchlingAppsArchiveReason

    def __repr__(self):
        fields = []
        fields.append("app_ids={}".format(repr(self._app_ids)))
        fields.append("reason={}".format(repr(self._reason)))
        return "BenchlingAppsArchive({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        app_ids = self._app_ids

        reason = self._reason.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "appIds": app_ids,
                "reason": reason,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_app_ids() -> List[str]:
            app_ids = cast(List[str], d.pop("appIds"))

            return app_ids

        app_ids = get_app_ids() if "appIds" in d else cast(List[str], UNSET)

        def get_reason() -> BenchlingAppsArchiveReason:
            _reason = d.pop("reason")
            try:
                reason = BenchlingAppsArchiveReason(_reason)
            except ValueError:
                reason = BenchlingAppsArchiveReason.of_unknown(_reason)

            return reason

        reason = get_reason() if "reason" in d else cast(BenchlingAppsArchiveReason, UNSET)

        benchling_apps_archive = cls(
            app_ids=app_ids,
            reason=reason,
        )

        return benchling_apps_archive

    @property
    def app_ids(self) -> List[str]:
        """ Array of app IDs """
        if isinstance(self._app_ids, Unset):
            raise NotPresentError(self, "app_ids")
        return self._app_ids

    @app_ids.setter
    def app_ids(self, value: List[str]) -> None:
        self._app_ids = value

    @property
    def reason(self) -> BenchlingAppsArchiveReason:
        """ Reason that apps are being archived. Actual reason enum varies by tenant. """
        if isinstance(self._reason, Unset):
            raise NotPresentError(self, "reason")
        return self._reason

    @reason.setter
    def reason(self, value: BenchlingAppsArchiveReason) -> None:
        self._reason = value
