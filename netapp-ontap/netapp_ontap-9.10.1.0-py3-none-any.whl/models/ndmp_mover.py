r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["NdmpMover", "NdmpMoverSchema"]
__pdoc__ = {
    "NdmpMoverSchema.resource": False,
    "NdmpMover": False,
}


class NdmpMoverSchema(ResourceSchema):
    """The fields of the NdmpMover object"""

    bytes_moved = Size(data_key="bytes_moved")
    r""" Indicates the NDMP mover bytes moved.

Example: 645120 """

    connection = fields.Nested("netapp_ontap.models.ndmp_connect.NdmpConnectSchema", unknown=EXCLUDE, data_key="connection")
    r""" Indicates the NDMP connection attributes. """

    mode = fields.Str(data_key="mode")
    r""" Indicates the NDMP mover mode of operation. """

    reason = fields.Str(data_key="reason")
    r""" Indicates the reason for the NDMP mover pause or halt. """

    state = fields.Str(data_key="state")
    r""" Indicates the NDMP mover state. """

    @property
    def resource(self):
        return NdmpMover

    gettable_fields = [
        "bytes_moved",
        "connection",
        "mode",
        "reason",
        "state",
    ]
    """bytes_moved,connection,mode,reason,state,"""

    patchable_fields = [
        "bytes_moved",
        "connection",
        "mode",
        "reason",
        "state",
    ]
    """bytes_moved,connection,mode,reason,state,"""

    postable_fields = [
        "bytes_moved",
        "connection",
        "mode",
        "reason",
        "state",
    ]
    """bytes_moved,connection,mode,reason,state,"""


class NdmpMover(Resource):

    _schema = NdmpMoverSchema
