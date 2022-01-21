r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["SnapmirrorRelationshipTransfer", "SnapmirrorRelationshipTransferSchema"]
__pdoc__ = {
    "SnapmirrorRelationshipTransferSchema.resource": False,
    "SnapmirrorRelationshipTransfer": False,
}


class SnapmirrorRelationshipTransferSchema(ResourceSchema):
    """The fields of the SnapmirrorRelationshipTransfer object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="_links")
    r""" The links field of the snapmirror_relationship_transfer. """

    bytes_transferred = Size(data_key="bytes_transferred")
    r""" Bytes transferred. """

    end_time = ImpreciseDateTime(data_key="end_time")
    r""" End time of the last transfer.

Example: 2020-12-03T02:36:19.000+0000 """

    state = fields.Str(data_key="state")
    r""" The state field of the snapmirror_relationship_transfer.

Valid choices:

* aborted
* failed
* hard_aborted
* queued
* success
* transferring """

    total_duration = fields.Str(data_key="total_duration")
    r""" Transfer elapsed time.

Example: PT28M41S """

    uuid = fields.Str(data_key="uuid")
    r""" Transfer UUID. This property is applicable only for active transfers.

Example: 4ea7a442-86d1-11e0-ae1c-123478563412 """

    @property
    def resource(self):
        return SnapmirrorRelationshipTransfer

    gettable_fields = [
        "links",
        "bytes_transferred",
        "end_time",
        "state",
        "total_duration",
        "uuid",
    ]
    """links,bytes_transferred,end_time,state,total_duration,uuid,"""

    patchable_fields = [
        "bytes_transferred",
        "end_time",
        "state",
        "total_duration",
        "uuid",
    ]
    """bytes_transferred,end_time,state,total_duration,uuid,"""

    postable_fields = [
        "bytes_transferred",
        "end_time",
        "state",
        "total_duration",
        "uuid",
    ]
    """bytes_transferred,end_time,state,total_duration,uuid,"""


class SnapmirrorRelationshipTransfer(Resource):

    _schema = SnapmirrorRelationshipTransferSchema
