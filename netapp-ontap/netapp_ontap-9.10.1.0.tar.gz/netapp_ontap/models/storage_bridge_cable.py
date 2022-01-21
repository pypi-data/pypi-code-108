r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["StorageBridgeCable", "StorageBridgeCableSchema"]
__pdoc__ = {
    "StorageBridgeCableSchema.resource": False,
    "StorageBridgeCable": False,
}


class StorageBridgeCableSchema(ResourceSchema):
    """The fields of the StorageBridgeCable object"""

    part_number = fields.Str(data_key="part_number")
    r""" Bridge cable part number """

    serial_number = fields.Str(data_key="serial_number")
    r""" Bridge cable serial number """

    technology = fields.Str(data_key="technology")
    r""" Bridge cable type """

    vendor = fields.Str(data_key="vendor")
    r""" Bridge cable vendor """

    @property
    def resource(self):
        return StorageBridgeCable

    gettable_fields = [
        "part_number",
        "serial_number",
        "technology",
        "vendor",
    ]
    """part_number,serial_number,technology,vendor,"""

    patchable_fields = [
        "part_number",
        "serial_number",
        "technology",
        "vendor",
    ]
    """part_number,serial_number,technology,vendor,"""

    postable_fields = [
        "part_number",
        "serial_number",
        "technology",
        "vendor",
    ]
    """part_number,serial_number,technology,vendor,"""


class StorageBridgeCable(Resource):

    _schema = StorageBridgeCableSchema
