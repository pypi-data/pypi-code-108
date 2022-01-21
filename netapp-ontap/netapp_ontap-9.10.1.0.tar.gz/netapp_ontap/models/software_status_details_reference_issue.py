r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["SoftwareStatusDetailsReferenceIssue", "SoftwareStatusDetailsReferenceIssueSchema"]
__pdoc__ = {
    "SoftwareStatusDetailsReferenceIssueSchema.resource": False,
    "SoftwareStatusDetailsReferenceIssue": False,
}


class SoftwareStatusDetailsReferenceIssueSchema(ResourceSchema):
    """The fields of the SoftwareStatusDetailsReferenceIssue object"""

    code = Size(data_key="code")
    r""" Error code corresponding to update status

Example: 10551399 """

    message = fields.Str(data_key="message")
    r""" Update status details

Example: Image update complete """

    @property
    def resource(self):
        return SoftwareStatusDetailsReferenceIssue

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


class SoftwareStatusDetailsReferenceIssue(Resource):

    _schema = SoftwareStatusDetailsReferenceIssueSchema
