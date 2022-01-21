r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["SoftwareStatusDetailsReferenceAction", "SoftwareStatusDetailsReferenceActionSchema"]
__pdoc__ = {
    "SoftwareStatusDetailsReferenceActionSchema.resource": False,
    "SoftwareStatusDetailsReferenceAction": False,
}


class SoftwareStatusDetailsReferenceActionSchema(ResourceSchema):
    """The fields of the SoftwareStatusDetailsReferenceAction object"""

    code = Size(data_key="code")
    r""" Error code corresponding the status error """

    message = fields.Str(data_key="message")
    r""" Corrective action to be taken to resolve the status error. """

    @property
    def resource(self):
        return SoftwareStatusDetailsReferenceAction

    gettable_fields = [
        "code",
        "message",
    ]
    """code,message,"""

    patchable_fields = [
        "code",
        "message",
    ]
    """code,message,"""

    postable_fields = [
        "code",
        "message",
    ]
    """code,message,"""


class SoftwareStatusDetailsReferenceAction(Resource):

    _schema = SoftwareStatusDetailsReferenceActionSchema
