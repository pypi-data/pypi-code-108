r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["VolumeConsistencyGroup", "VolumeConsistencyGroupSchema"]
__pdoc__ = {
    "VolumeConsistencyGroupSchema.resource": False,
    "VolumeConsistencyGroup": False,
}


class VolumeConsistencyGroupSchema(ResourceSchema):
    """The fields of the VolumeConsistencyGroup object"""

    name = fields.Str(data_key="name")
    r""" The name of the consistency group to which the volume belongs. Available only when the volume is part of a consistency group. If this volume belongs to a child consistency group, then this will be the UUID of the parent consistency group.

Example: consistency_group_1 """

    uuid = fields.Str(data_key="uuid")
    r""" The UUID of the consistency group to which the volume belongs. Available only when the volume is part of a consistency group. If this volume belongs to a child consistency group, then this will be the UUID of the parent consistency group.

Example: 1cd8a442-86d1-11e0-ae1d-123478563412 """

    @property
    def resource(self):
        return VolumeConsistencyGroup

    gettable_fields = [
        "name",
        "uuid",
    ]
    """name,uuid,"""

    patchable_fields = [
        "name",
    ]
    """name,"""

    postable_fields = [
        "name",
    ]
    """name,"""


class VolumeConsistencyGroup(Resource):

    _schema = VolumeConsistencyGroupSchema
