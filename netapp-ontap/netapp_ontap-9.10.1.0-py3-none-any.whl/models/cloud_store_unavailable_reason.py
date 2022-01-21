r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["CloudStoreUnavailableReason", "CloudStoreUnavailableReasonSchema"]
__pdoc__ = {
    "CloudStoreUnavailableReasonSchema.resource": False,
    "CloudStoreUnavailableReason": False,
}


class CloudStoreUnavailableReasonSchema(ResourceSchema):
    """The fields of the CloudStoreUnavailableReason object"""

    message = fields.Str(data_key="message")
    r""" Indicates why the object store is unavailable. """

    @property
    def resource(self):
        return CloudStoreUnavailableReason

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


class CloudStoreUnavailableReason(Resource):

    _schema = CloudStoreUnavailableReasonSchema
