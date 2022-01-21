r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["AutosupportMessageError", "AutosupportMessageErrorSchema"]
__pdoc__ = {
    "AutosupportMessageErrorSchema.resource": False,
    "AutosupportMessageError": False,
}


class AutosupportMessageErrorSchema(ResourceSchema):
    """The fields of the AutosupportMessageError object"""

    code = Size(data_key="code")
    r""" Error code

Example: 53149746 """

    message = fields.Str(data_key="message")
    r""" Error message

Example: Could not resolve host: test.com """

    @property
    def resource(self):
        return AutosupportMessageError

    gettable_fields = [
        "code",
        "message",
    ]
    """code,message,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class AutosupportMessageError(Resource):

    _schema = AutosupportMessageErrorSchema
