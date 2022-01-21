r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["StorageBridgeComponent", "StorageBridgeComponentSchema"]
__pdoc__ = {
    "StorageBridgeComponentSchema.resource": False,
    "StorageBridgeComponent": False,
}


class StorageBridgeComponentSchema(ResourceSchema):
    """The fields of the StorageBridgeComponent object"""

    id = Size(data_key="id")
    r""" Bridge error component ID """

    name = fields.Str(data_key="name")
    r""" Bridge error component name """

    unique_id = fields.Str(data_key="unique_id")
    r""" Bridge error component unique ID """

    @property
    def resource(self):
        return StorageBridgeComponent

    gettable_fields = [
        "id",
        "name",
        "unique_id",
    ]
    """id,name,unique_id,"""

    patchable_fields = [
        "id",
        "name",
        "unique_id",
    ]
    """id,name,unique_id,"""

    postable_fields = [
        "id",
        "name",
        "unique_id",
    ]
    """id,name,unique_id,"""


class StorageBridgeComponent(Resource):

    _schema = StorageBridgeComponentSchema
