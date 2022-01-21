r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["Smb", "SmbSchema"]
__pdoc__ = {
    "SmbSchema.resource": False,
    "Smb": False,
}


class SmbSchema(ResourceSchema):
    """The fields of the Smb object"""

    connect_state = fields.Str(data_key="connect_state")
    r""" SMB connection state.

Valid choices:

* connected
* disconnected
* reconnecting
* timedout """

    open_group_id = fields.Str(data_key="open_group_id")
    r""" SMB open group ID. """

    open_type = fields.Str(data_key="open_type")
    r""" SMB open type.

Valid choices:

* none
* durable
* persistent """

    @property
    def resource(self):
        return Smb

    gettable_fields = [
        "connect_state",
        "open_group_id",
        "open_type",
    ]
    """connect_state,open_group_id,open_type,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class Smb(Resource):

    _schema = SmbSchema
