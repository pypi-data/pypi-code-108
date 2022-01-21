r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["StorageSwitchAdapter", "StorageSwitchAdapterSchema"]
__pdoc__ = {
    "StorageSwitchAdapterSchema.resource": False,
    "StorageSwitchAdapter": False,
}


class StorageSwitchAdapterSchema(ResourceSchema):
    """The fields of the StorageSwitchAdapter object"""

    name = fields.Str(data_key="name")
    r""" Node adapter name """

    type = fields.Str(data_key="type")
    r""" Node adapter type

Valid choices:

* unknown
* fcp_initiator
* fc_vi
* fcp_target """

    wwn = fields.Str(data_key="wwn")
    r""" Node adapter world wide name """

    @property
    def resource(self):
        return StorageSwitchAdapter

    gettable_fields = [
        "name",
        "type",
        "wwn",
    ]
    """name,type,wwn,"""

    patchable_fields = [
        "name",
        "type",
        "wwn",
    ]
    """name,type,wwn,"""

    postable_fields = [
        "name",
        "type",
        "wwn",
    ]
    """name,type,wwn,"""


class StorageSwitchAdapter(Resource):

    _schema = StorageSwitchAdapterSchema
