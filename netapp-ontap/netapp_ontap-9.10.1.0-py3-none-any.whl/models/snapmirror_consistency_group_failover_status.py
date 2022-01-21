r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["SnapmirrorConsistencyGroupFailoverStatus", "SnapmirrorConsistencyGroupFailoverStatusSchema"]
__pdoc__ = {
    "SnapmirrorConsistencyGroupFailoverStatusSchema.resource": False,
    "SnapmirrorConsistencyGroupFailoverStatus": False,
}


class SnapmirrorConsistencyGroupFailoverStatusSchema(ResourceSchema):
    """The fields of the SnapmirrorConsistencyGroupFailoverStatus object"""

    code = fields.Str(data_key="code")
    r""" Status code """

    message = fields.Str(data_key="message")
    r""" SnapMirror Consistency Group failover status. """

    @property
    def resource(self):
        return SnapmirrorConsistencyGroupFailoverStatus

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


class SnapmirrorConsistencyGroupFailoverStatus(Resource):

    _schema = SnapmirrorConsistencyGroupFailoverStatusSchema
