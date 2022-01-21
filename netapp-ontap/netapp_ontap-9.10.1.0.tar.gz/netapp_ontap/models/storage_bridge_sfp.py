r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["StorageBridgeSfp", "StorageBridgeSfpSchema"]
__pdoc__ = {
    "StorageBridgeSfpSchema.resource": False,
    "StorageBridgeSfp": False,
}


class StorageBridgeSfpSchema(ResourceSchema):
    """The fields of the StorageBridgeSfp object"""

    data_rate_capability = fields.Number(data_key="data_rate_capability")
    r""" Bridge FC port SFP data rate capability, in Gbps """

    part_number = fields.Str(data_key="part_number")
    r""" The part_number field of the storage_bridge_sfp. """

    serial_number = fields.Str(data_key="serial_number")
    r""" Bridge FC port SFP serial number """

    vendor = fields.Str(data_key="vendor")
    r""" Bridge FC port SFP vendor """

    @property
    def resource(self):
        return StorageBridgeSfp

    gettable_fields = [
        "data_rate_capability",
        "part_number",
        "serial_number",
        "vendor",
    ]
    """data_rate_capability,part_number,serial_number,vendor,"""

    patchable_fields = [
        "data_rate_capability",
        "part_number",
        "serial_number",
        "vendor",
    ]
    """data_rate_capability,part_number,serial_number,vendor,"""

    postable_fields = [
        "data_rate_capability",
        "part_number",
        "serial_number",
        "vendor",
    ]
    """data_rate_capability,part_number,serial_number,vendor,"""


class StorageBridgeSfp(Resource):

    _schema = StorageBridgeSfpSchema
