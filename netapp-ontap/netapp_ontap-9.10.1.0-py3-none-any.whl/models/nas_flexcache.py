r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["NasFlexcache", "NasFlexcacheSchema"]
__pdoc__ = {
    "NasFlexcacheSchema.resource": False,
    "NasFlexcache": False,
}


class NasFlexcacheSchema(ResourceSchema):
    """The fields of the NasFlexcache object"""

    dr_cache = fields.Boolean(data_key="dr_cache")
    r""" Dr-cache is a FlexCache volume create time option that has the same flexgroup-msid as that of the origin of a FlexCache volume. By default, dr-cache is disabled. The flexgroup-msid of the FlexCache volume does not need to be same as that of the origin of a FlexCache volume. """

    origin = fields.Nested("netapp_ontap.models.nas_flexcache_origin.NasFlexcacheOriginSchema", unknown=EXCLUDE, data_key="origin")
    r""" The origin field of the nas_flexcache. """

    @property
    def resource(self):
        return NasFlexcache

    gettable_fields = [
        "dr_cache",
        "origin",
    ]
    """dr_cache,origin,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
        "dr_cache",
        "origin",
    ]
    """dr_cache,origin,"""


class NasFlexcache(Resource):

    _schema = NasFlexcacheSchema
