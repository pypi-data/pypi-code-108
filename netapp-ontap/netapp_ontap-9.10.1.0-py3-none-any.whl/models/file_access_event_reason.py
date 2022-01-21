r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["FileAccessEventReason", "FileAccessEventReasonSchema"]
__pdoc__ = {
    "FileAccessEventReasonSchema.resource": False,
    "FileAccessEventReason": False,
}


class FileAccessEventReasonSchema(ResourceSchema):
    """The fields of the FileAccessEventReason object"""

    message = fields.Str(data_key="message")
    r""" The error message.


Example: Access is allowed because the operation is trusted and no security is configured. """

    @property
    def resource(self):
        return FileAccessEventReason

    gettable_fields = [
        "message",
    ]
    """message,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class FileAccessEventReason(Resource):

    _schema = FileAccessEventReasonSchema
