from chai_py.defaults import GUEST_UID, GUEST_KEY
from chai_py.logger import logger


def get_auth():
    return auth


def set_auth(uid: str, key: str):
    """
    Sets package-wide developer authentication.

    :param uid: Developer Unique Identifier.
    :param key: Developer key.
    :return:
    """
    global auth
    auth = ChaiAuth(uid=uid, key=key)


class ChaiAuth():
    """Credentials for developer API. """

    def __init__(self, uid: str, key: str):
        self._uid = uid
        self._key = key
        self._accessed = False

    @property
    def is_guest(self):
        return self._uid == GUEST_UID

    @property
    def uid(self) -> str:
        if not self._accessed and self.is_guest:
            logger.warning("Using guest credentials. To be able to redeploy and monitor your Chat AIs, "
                           "run chai_py.set_auth() with your uid and key from https://chai.ml/dev/")
            self._accessed = True
        return self._uid

    @property
    def key(self) -> str:
        return self._key

    def __repr__(self):
        return f"{self.__class__.__name__}(uid={self._uid}, key={self._key})"


auth = ChaiAuth(uid=GUEST_UID, key=GUEST_KEY)
