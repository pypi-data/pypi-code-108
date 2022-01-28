from dataclasses import dataclass

from .teamtv_object import TeamTVObject


@dataclass
class Credentials(object):
    access_key_id: str
    secret_access_key: str
    session_token: str


@dataclass
class BucketInfo(object):
    bucket: str
    base_key: str


class AppStorageTokens(TeamTVObject):
    @property
    def credentials(self):
        return self._credentials

    def _use_attributes(self, attributes: dict):
        self._credentials = Credentials(
            access_key_id=attributes['credentials']['accessKeyId'],
            secret_access_key=attributes['credentials']['secretAccessKey'],
            session_token=attributes['credentials']['sessionToken']
        )
        self._bucket_info = BucketInfo(
            bucket=attributes['storage']['bucket'],
            base_key=attributes['storage']['baseKey']
        )
