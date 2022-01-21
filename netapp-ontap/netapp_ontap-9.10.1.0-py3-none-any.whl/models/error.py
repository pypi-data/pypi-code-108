r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["Error", "ErrorSchema"]
__pdoc__ = {
    "ErrorSchema.resource": False,
    "Error": False,
}


class ErrorSchema(ResourceSchema):
    """The fields of the Error object"""

    arguments = fields.List(fields.Nested("netapp_ontap.models.error_arguments.ErrorArgumentsSchema", unknown=EXCLUDE), data_key="arguments")
    r""" Message arguments """

    code = fields.Str(data_key="code")
    r""" Error code

Example: 4 """

    message = fields.Str(data_key="message")
    r""" Error message

Example: entry doesn't exist """

    target = fields.Str(data_key="target")
    r""" The target parameter that caused the error.

Example: uuid """

    @property
    def resource(self):
        return Error

    gettable_fields = [
        "arguments",
        "code",
        "message",
        "target",
    ]
    """arguments,code,message,target,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class Error(Resource):

    _schema = ErrorSchema
