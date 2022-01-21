r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["StoragePortError", "StoragePortErrorSchema"]
__pdoc__ = {
    "StoragePortErrorSchema.resource": False,
    "StoragePortError": False,
}


class StoragePortErrorSchema(ResourceSchema):
    """The fields of the StoragePortError object"""

    corrective_action = fields.Str(data_key="corrective_action")
    r""" Error corrective action """

    message = fields.Str(data_key="message")
    r""" Error message """

    @property
    def resource(self):
        return StoragePortError

    gettable_fields = [
        "corrective_action",
        "message",
    ]
    """corrective_action,message,"""

    patchable_fields = [
        "corrective_action",
        "message",
    ]
    """corrective_action,message,"""

    postable_fields = [
        "corrective_action",
        "message",
    ]
    """corrective_action,message,"""


class StoragePortError(Resource):

    _schema = StoragePortErrorSchema
