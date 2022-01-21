r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["DiskPathInfo", "DiskPathInfoSchema"]
__pdoc__ = {
    "DiskPathInfoSchema.resource": False,
    "DiskPathInfo": False,
}


class DiskPathInfoSchema(ResourceSchema):
    """The fields of the DiskPathInfo object"""

    initiator = fields.Str(data_key="initiator")
    r""" Initiator port.

Example: 3a """

    port_name = fields.Str(data_key="port_name")
    r""" Name of the disk port.

Example: A """

    port_type = fields.Str(data_key="port_type")
    r""" Disk port type.

Valid choices:

* sas
* fc
* nvme """

    wwnn = fields.Str(data_key="wwnn")
    r""" Target device's World Wide Node Name.

Example: 5000c2971c1b2b8c """

    wwpn = fields.Str(data_key="wwpn")
    r""" Target device's World Wide Port Name.

Example: 5000c2971c1b2b8d """

    @property
    def resource(self):
        return DiskPathInfo

    gettable_fields = [
        "initiator",
        "port_name",
        "port_type",
        "wwnn",
        "wwpn",
    ]
    """initiator,port_name,port_type,wwnn,wwpn,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class DiskPathInfo(Resource):

    _schema = DiskPathInfoSchema
