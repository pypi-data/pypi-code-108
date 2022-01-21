r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["SoftwareReferenceMetroclusterProgressSummary", "SoftwareReferenceMetroclusterProgressSummarySchema"]
__pdoc__ = {
    "SoftwareReferenceMetroclusterProgressSummarySchema.resource": False,
    "SoftwareReferenceMetroclusterProgressSummary": False,
}


class SoftwareReferenceMetroclusterProgressSummarySchema(ResourceSchema):
    """The fields of the SoftwareReferenceMetroclusterProgressSummary object"""

    message = fields.Str(data_key="message")
    r""" MetroCluster update progress summary.

Example: MetroCluster updated successfully. """

    @property
    def resource(self):
        return SoftwareReferenceMetroclusterProgressSummary

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


class SoftwareReferenceMetroclusterProgressSummary(Resource):

    _schema = SoftwareReferenceMetroclusterProgressSummarySchema
