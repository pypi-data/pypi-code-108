r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["BackupNode", "BackupNodeSchema"]
__pdoc__ = {
    "BackupNodeSchema.resource": False,
    "BackupNode": False,
}


class BackupNodeSchema(ResourceSchema):
    """The fields of the BackupNode object"""

    name = fields.Str(data_key="name")
    r""" The name field of the backup_node. """

    @property
    def resource(self):
        return BackupNode

    gettable_fields = [
        "name",
    ]
    """name,"""

    patchable_fields = [
        "name",
    ]
    """name,"""

    postable_fields = [
        "name",
    ]
    """name,"""


class BackupNode(Resource):

    _schema = BackupNodeSchema
