r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["PlexResync", "PlexResyncSchema"]
__pdoc__ = {
    "PlexResyncSchema.resource": False,
    "PlexResync": False,
}


class PlexResyncSchema(ResourceSchema):
    """The fields of the PlexResync object"""

    active = fields.Boolean(data_key="active")
    r""" Plex is being resynchronized to its mirrored plex """

    level = fields.Str(data_key="level")
    r""" Plex resyncing level

Valid choices:

* full
* incremental """

    percent = Size(data_key="percent")
    r""" Plex resyncing percentage

Example: 10 """

    @property
    def resource(self):
        return PlexResync

    gettable_fields = [
        "active",
        "level",
        "percent",
    ]
    """active,level,percent,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class PlexResync(Resource):

    _schema = PlexResyncSchema
