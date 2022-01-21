r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["SnapmirrorError", "SnapmirrorErrorSchema"]
__pdoc__ = {
    "SnapmirrorErrorSchema.resource": False,
    "SnapmirrorError": False,
}


class SnapmirrorErrorSchema(ResourceSchema):
    """The fields of the SnapmirrorError object"""

    code = Size(data_key="code")
    r""" Error code """

    message = fields.Str(data_key="message")
    r""" Error message """

    parameters = fields.List(fields.Str, data_key="parameters")
    r""" Parameters for the error message """

    @property
    def resource(self):
        return SnapmirrorError

    gettable_fields = [
        "code",
        "message",
        "parameters",
    ]
    """code,message,parameters,"""

    patchable_fields = [
        "code",
        "message",
        "parameters",
    ]
    """code,message,parameters,"""

    postable_fields = [
        "code",
        "message",
        "parameters",
    ]
    """code,message,parameters,"""


class SnapmirrorError(Resource):

    _schema = SnapmirrorErrorSchema
