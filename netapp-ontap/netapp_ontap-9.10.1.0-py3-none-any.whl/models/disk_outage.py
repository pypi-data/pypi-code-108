r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["DiskOutage", "DiskOutageSchema"]
__pdoc__ = {
    "DiskOutageSchema.resource": False,
    "DiskOutage": False,
}


class DiskOutageSchema(ResourceSchema):
    """The fields of the DiskOutage object"""

    persistently_failed = fields.Boolean(data_key="persistently_failed")
    r""" Indicates whether RAID maintains the state of this disk as failed accross reboots. """

    reason = fields.Nested("netapp_ontap.models.error.ErrorSchema", unknown=EXCLUDE, data_key="reason")
    r""" This error message and code explaining the disk failure. """

    @property
    def resource(self):
        return DiskOutage

    gettable_fields = [
        "persistently_failed",
        "reason",
    ]
    """persistently_failed,reason,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class DiskOutage(Resource):

    _schema = DiskOutageSchema
