r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["NdmpData", "NdmpDataSchema"]
__pdoc__ = {
    "NdmpDataSchema.resource": False,
    "NdmpData": False,
}


class NdmpDataSchema(ResourceSchema):
    """The fields of the NdmpData object"""

    bytes_processed = Size(data_key="bytes_processed")
    r""" Indicates the NDMP data bytes processed.

Example: 5000 """

    connection = fields.Nested("netapp_ontap.models.ndmp_connect.NdmpConnectSchema", unknown=EXCLUDE, data_key="connection")
    r""" Indicates the NDMP connection attributes. """

    operation = fields.Str(data_key="operation")
    r""" Indicates the NDMP data server operation.

Valid choices:

* backup
* restore
* none """

    reason = fields.Str(data_key="reason")
    r""" Indicates the reason for the NDMP data server halt. """

    state = fields.Str(data_key="state")
    r""" Indicates the state of the NDMP data server. """

    @property
    def resource(self):
        return NdmpData

    gettable_fields = [
        "bytes_processed",
        "connection",
        "operation",
        "reason",
        "state",
    ]
    """bytes_processed,connection,operation,reason,state,"""

    patchable_fields = [
        "bytes_processed",
        "connection",
        "operation",
        "reason",
        "state",
    ]
    """bytes_processed,connection,operation,reason,state,"""

    postable_fields = [
        "bytes_processed",
        "connection",
        "operation",
        "reason",
        "state",
    ]
    """bytes_processed,connection,operation,reason,state,"""


class NdmpData(Resource):

    _schema = NdmpDataSchema
