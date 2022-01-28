from typing import Any, cast, Dict, List, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.containers_archive_reason import ContainersArchiveReason
from ..types import UNSET, Unset

T = TypeVar("T", bound="ContainersArchive")


@attr.s(auto_attribs=True, repr=False)
class ContainersArchive:
    """  """

    _container_ids: List[str]
    _reason: ContainersArchiveReason
    _should_remove_barcodes: Union[Unset, bool] = UNSET

    def __repr__(self):
        fields = []
        fields.append("container_ids={}".format(repr(self._container_ids)))
        fields.append("reason={}".format(repr(self._reason)))
        fields.append("should_remove_barcodes={}".format(repr(self._should_remove_barcodes)))
        return "ContainersArchive({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        container_ids = self._container_ids

        reason = self._reason.value

        should_remove_barcodes = self._should_remove_barcodes

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "containerIds": container_ids,
                "reason": reason,
            }
        )
        if should_remove_barcodes is not UNSET:
            field_dict["shouldRemoveBarcodes"] = should_remove_barcodes

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_container_ids() -> List[str]:
            container_ids = cast(List[str], d.pop("containerIds"))

            return container_ids

        container_ids = get_container_ids() if "containerIds" in d else cast(List[str], UNSET)

        def get_reason() -> ContainersArchiveReason:
            _reason = d.pop("reason")
            try:
                reason = ContainersArchiveReason(_reason)
            except ValueError:
                reason = ContainersArchiveReason.of_unknown(_reason)

            return reason

        reason = get_reason() if "reason" in d else cast(ContainersArchiveReason, UNSET)

        def get_should_remove_barcodes() -> Union[Unset, bool]:
            should_remove_barcodes = d.pop("shouldRemoveBarcodes")
            return should_remove_barcodes

        should_remove_barcodes = (
            get_should_remove_barcodes() if "shouldRemoveBarcodes" in d else cast(Union[Unset, bool], UNSET)
        )

        containers_archive = cls(
            container_ids=container_ids,
            reason=reason,
            should_remove_barcodes=should_remove_barcodes,
        )

        return containers_archive

    @property
    def container_ids(self) -> List[str]:
        """ Array of container IDs """
        if isinstance(self._container_ids, Unset):
            raise NotPresentError(self, "container_ids")
        return self._container_ids

    @container_ids.setter
    def container_ids(self, value: List[str]) -> None:
        self._container_ids = value

    @property
    def reason(self) -> ContainersArchiveReason:
        """Reason that containers are being archived."""
        if isinstance(self._reason, Unset):
            raise NotPresentError(self, "reason")
        return self._reason

    @reason.setter
    def reason(self, value: ContainersArchiveReason) -> None:
        self._reason = value

    @property
    def should_remove_barcodes(self) -> bool:
        """Remove barcodes. Removing barcodes from archived storage that contain items will also remove barcodes from the contained items."""
        if isinstance(self._should_remove_barcodes, Unset):
            raise NotPresentError(self, "should_remove_barcodes")
        return self._should_remove_barcodes

    @should_remove_barcodes.setter
    def should_remove_barcodes(self, value: bool) -> None:
        self._should_remove_barcodes = value

    @should_remove_barcodes.deleter
    def should_remove_barcodes(self) -> None:
        self._should_remove_barcodes = UNSET
