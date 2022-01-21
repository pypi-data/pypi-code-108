r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["TapeDeviceAlias", "TapeDeviceAliasSchema"]
__pdoc__ = {
    "TapeDeviceAliasSchema.resource": False,
    "TapeDeviceAlias": False,
}


class TapeDeviceAliasSchema(ResourceSchema):
    """The fields of the TapeDeviceAlias object"""

    mapping = fields.Str(data_key="mapping")
    r""" Alias mapping.

Example: SN[10WT000933] """

    name = fields.Str(data_key="name")
    r""" Alias name.

Example: st6 """

    @property
    def resource(self):
        return TapeDeviceAlias

    gettable_fields = [
        "mapping",
        "name",
    ]
    """mapping,name,"""

    patchable_fields = [
        "mapping",
        "name",
    ]
    """mapping,name,"""

    postable_fields = [
        "mapping",
        "name",
    ]
    """mapping,name,"""


class TapeDeviceAlias(Resource):

    _schema = TapeDeviceAliasSchema
