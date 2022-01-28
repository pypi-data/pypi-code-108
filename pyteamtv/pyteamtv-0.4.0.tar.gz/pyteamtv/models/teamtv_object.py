from pyteamtv.infra.requester import Requester


class TeamTVObject(object):
    def __init__(self, requester: Requester, attributes: dict):
        self._requester = requester
        self.__attributes = attributes

        self._use_attributes(attributes)

    def _use_attributes(self, attributes: dict):
        pass
