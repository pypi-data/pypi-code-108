r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["SoftwareReferenceMetroclusterProgressDetails", "SoftwareReferenceMetroclusterProgressDetailsSchema"]
__pdoc__ = {
    "SoftwareReferenceMetroclusterProgressDetailsSchema.resource": False,
    "SoftwareReferenceMetroclusterProgressDetails": False,
}


class SoftwareReferenceMetroclusterProgressDetailsSchema(ResourceSchema):
    """The fields of the SoftwareReferenceMetroclusterProgressDetails object"""

    message = fields.Str(data_key="message")
    r""" MetroCluster update progress details.

Example: Switchover in progress """

    @property
    def resource(self):
        return SoftwareReferenceMetroclusterProgressDetails

    gettable_fields = [
        "message",
    ]
    """message,"""

    patchable_fields = [
        "message",
    ]
    """message,"""

    postable_fields = [
        "message",
    ]
    """message,"""


class SoftwareReferenceMetroclusterProgressDetails(Resource):

    _schema = SoftwareReferenceMetroclusterProgressDetailsSchema
