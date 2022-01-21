r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["StorageSwitchPeerPort", "StorageSwitchPeerPortSchema"]
__pdoc__ = {
    "StorageSwitchPeerPortSchema.resource": False,
    "StorageSwitchPeerPort": False,
}


class StorageSwitchPeerPortSchema(ResourceSchema):
    """The fields of the StorageSwitchPeerPort object"""

    connection = fields.Str(data_key="connection")
    r""" Storage switch peer port host and name """

    type = fields.Str(data_key="type")
    r""" Storage switch peer type

Valid choices:

* unknown
* bridge
* switch
* fcp_adapter
* fcvi_adapter """

    unique_id = fields.Str(data_key="unique_id")
    r""" Storage switch peer unique ID """

    wwn = fields.Str(data_key="wwn")
    r""" Storage switch peer port world wide name """

    @property
    def resource(self):
        return StorageSwitchPeerPort

    gettable_fields = [
        "connection",
        "type",
        "unique_id",
        "wwn",
    ]
    """connection,type,unique_id,wwn,"""

    patchable_fields = [
        "connection",
        "type",
        "unique_id",
        "wwn",
    ]
    """connection,type,unique_id,wwn,"""

    postable_fields = [
        "connection",
        "type",
        "unique_id",
        "wwn",
    ]
    """connection,type,unique_id,wwn,"""


class StorageSwitchPeerPort(Resource):

    _schema = StorageSwitchPeerPortSchema
