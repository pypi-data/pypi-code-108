r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["SoftwareNode", "SoftwareNodeSchema"]
__pdoc__ = {
    "SoftwareNodeSchema.resource": False,
    "SoftwareNode": False,
}


class SoftwareNodeSchema(ResourceSchema):
    """The fields of the SoftwareNode object"""

    firmware = fields.Nested("netapp_ontap.models.firmware.FirmwareSchema", unknown=EXCLUDE, data_key="firmware")
    r""" The firmware field of the software_node. """

    name = fields.Str(data_key="name")
    r""" Name of the node.

Example: node1 """

    software_images = fields.List(fields.Str, data_key="software_images")
    r""" The software_images field of the software_node. """

    version = fields.Str(data_key="version")
    r""" ONTAP version of the node.

Example: ONTAP_X """

    @property
    def resource(self):
        return SoftwareNode

    gettable_fields = [
        "firmware",
        "name",
        "software_images",
        "version",
    ]
    """firmware,name,software_images,version,"""

    patchable_fields = [
        "software_images",
    ]
    """software_images,"""

    postable_fields = [
        "software_images",
    ]
    """software_images,"""


class SoftwareNode(Resource):

    _schema = SoftwareNodeSchema
