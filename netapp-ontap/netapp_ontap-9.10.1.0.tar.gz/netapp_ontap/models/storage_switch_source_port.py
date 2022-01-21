r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["StorageSwitchSourcePort", "StorageSwitchSourcePortSchema"]
__pdoc__ = {
    "StorageSwitchSourcePortSchema.resource": False,
    "StorageSwitchSourcePort": False,
}


class StorageSwitchSourcePortSchema(ResourceSchema):
    """The fields of the StorageSwitchSourcePort object"""

    mode = fields.Str(data_key="mode")
    r""" Storage switch port operating mode """

    name = fields.Str(data_key="name")
    r""" Storage switch port name """

    wwn = fields.Str(data_key="wwn")
    r""" Storage switch peer port world wide name """

    @property
    def resource(self):
        return StorageSwitchSourcePort

    gettable_fields = [
        "mode",
        "name",
        "wwn",
    ]
    """mode,name,wwn,"""

    patchable_fields = [
        "mode",
        "name",
        "wwn",
    ]
    """mode,name,wwn,"""

    postable_fields = [
        "mode",
        "name",
        "wwn",
    ]
    """mode,name,wwn,"""


class StorageSwitchSourcePort(Resource):

    _schema = StorageSwitchSourcePortSchema
