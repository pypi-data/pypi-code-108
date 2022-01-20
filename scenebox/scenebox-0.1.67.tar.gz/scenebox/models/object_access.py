#  Copyright (c) 2020 Caliber Data Labs.
#  All rights reserved.
#
from typing import Dict, Optional

from ..tools import misc
from ..tools.naming import UriParser


class ObjectAccessError(Exception):
    pass


class ObjectAccessMedium:
    ASSET_MANAGER = "asset-manager"
    PUBLIC_URL = "public-url"
    GS = "gs"
    S3 = "s3"

# examples
# {
#   "medium": "url", #required
#   "id": "laksjdlkawsd" #required
#   "url": "http....", #required
#   "filename": "abc.png" #optional
# }
#
# {
#   "medium": "asset-manager", #required
#   "id": "laksjdlkawsd" #required
#   "filename": "abc.png" #optional
# }
#


class ObjectAccess(object):
    def __init__(self,
                 id: Optional[str] = None,
                 filename: Optional[str] = None,
                 url: Optional[str] = None,
                 uri: Optional[str] = None):
        if url:
            self.medium = ObjectAccessMedium.PUBLIC_URL
        elif uri:
            uri_parser = UriParser(uri)
            if uri_parser.cloud_provider == "gs":
                self.medium = ObjectAccessMedium.GS
            elif uri_parser.cloud_provider == "s3":
                self.medium = ObjectAccessMedium.S3
            else:
                raise ObjectAccessError(
                    "invalid cloud storage provider {}".format(
                        uri_parser.cloud_provider))
            filename = uri_parser.key.split("/")[-1]
        elif id:
            self.medium = ObjectAccessMedium.ASSET_MANAGER
        else:
            raise ObjectAccessError(
                "invalid medium- either url or id, or uri should be specified")

        if id:
            self.id = id
        elif uri or url:
            self.id = misc.get_md5_from_string(uri or url)
        else:
            self.id = misc.get_guid()
        self.url = url  # optional
        self.uri = uri  # optional
        self.filename = filename  # optional

    def __hash__(self):
        return self.id.__hash__()

    def __eq__(self, other):
        return self.id == other.id

    def to_dic(self) -> dict:
        object_access_dict = {
            "id": self.id
        }

        if self.filename:
            object_access_dict["filename"] = self.filename

        if self.url:
            object_access_dict["url"] = self.url

        if self.uri:
            object_access_dict["uri"] = self.uri

        return object_access_dict

    @classmethod
    def from_dict(cls, data: Dict):
        fields = {
            "id",
            "filename",
            "url",
            "uri"
        }
        return cls(**{field: data.get(field) for field in fields})
