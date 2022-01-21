r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["NfsServiceProtocolV41Features", "NfsServiceProtocolV41FeaturesSchema"]
__pdoc__ = {
    "NfsServiceProtocolV41FeaturesSchema.resource": False,
    "NfsServiceProtocolV41Features": False,
}


class NfsServiceProtocolV41FeaturesSchema(ResourceSchema):
    """The fields of the NfsServiceProtocolV41Features object"""

    acl_enabled = fields.Boolean(data_key="acl_enabled")
    r""" Specifies whether NFSv4.1 or later ACLs is enabled. """

    pnfs_enabled = fields.Boolean(data_key="pnfs_enabled")
    r""" Specifies whether NFSv4.1 or later Parallel NFS is enabled. """

    read_delegation_enabled = fields.Boolean(data_key="read_delegation_enabled")
    r""" Specifies whether NFSv4.1 or later Read Delegation is enabled. """

    write_delegation_enabled = fields.Boolean(data_key="write_delegation_enabled")
    r""" Specifies whether NFSv4.1 or later Write Delegation is enabled. """

    @property
    def resource(self):
        return NfsServiceProtocolV41Features

    gettable_fields = [
        "acl_enabled",
        "pnfs_enabled",
        "read_delegation_enabled",
        "write_delegation_enabled",
    ]
    """acl_enabled,pnfs_enabled,read_delegation_enabled,write_delegation_enabled,"""

    patchable_fields = [
        "acl_enabled",
        "pnfs_enabled",
        "read_delegation_enabled",
        "write_delegation_enabled",
    ]
    """acl_enabled,pnfs_enabled,read_delegation_enabled,write_delegation_enabled,"""

    postable_fields = [
        "acl_enabled",
        "pnfs_enabled",
        "read_delegation_enabled",
        "write_delegation_enabled",
    ]
    """acl_enabled,pnfs_enabled,read_delegation_enabled,write_delegation_enabled,"""


class NfsServiceProtocolV41Features(Resource):

    _schema = NfsServiceProtocolV41FeaturesSchema
