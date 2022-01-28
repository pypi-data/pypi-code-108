from pyteamtv.models.sharing_group import SharingGroup
from . import _ResourceGroup

from .capabilities import _HasTeamsMixin, _HasSportingEventsMixin, _HasVideosMixin


class SharingGroupResourceGroup(_ResourceGroup, _HasTeamsMixin, _HasSportingEventsMixin, _HasVideosMixin):
    def get_sharing_group(self):
        return SharingGroup(
            self._requester,
            self._requester.request(
                "GET",
                f"/sharingGroups/{self.sharing_group_id}"
            )
        )

    @property
    def sharing_group_id(self):
        return self._sharing_group_id

    def _use_attributes(self, attributes: dict):
        self._sharing_group_id = attributes['targetResourceId'].split(":")[1]
        super()._use_attributes(attributes)



