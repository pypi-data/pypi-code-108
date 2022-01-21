r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["NodeExternalCache", "NodeExternalCacheSchema"]
__pdoc__ = {
    "NodeExternalCacheSchema.resource": False,
    "NodeExternalCache": False,
}


class NodeExternalCacheSchema(ResourceSchema):
    """The fields of the NodeExternalCache object"""

    is_enabled = fields.Boolean(data_key="is_enabled")
    r""" Indicates whether the external cache is enabled.

Example: true """

    is_hya_enabled = fields.Boolean(data_key="is_hya_enabled")
    r""" Indicates whether HyA caching is enabled.

Example: true """

    is_rewarm_enabled = fields.Boolean(data_key="is_rewarm_enabled")
    r""" Indicates whether rewarm is enabled.

Example: true """

    pcs_size = Size(data_key="pcs_size")
    r""" PCS size in gigabytes. """

    @property
    def resource(self):
        return NodeExternalCache

    gettable_fields = [
        "is_enabled",
        "is_hya_enabled",
        "is_rewarm_enabled",
        "pcs_size",
    ]
    """is_enabled,is_hya_enabled,is_rewarm_enabled,pcs_size,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class NodeExternalCache(Resource):

    _schema = NodeExternalCacheSchema
