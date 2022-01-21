r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["SnapmirrorConsistencyGroupFailover", "SnapmirrorConsistencyGroupFailoverSchema"]
__pdoc__ = {
    "SnapmirrorConsistencyGroupFailoverSchema.resource": False,
    "SnapmirrorConsistencyGroupFailover": False,
}


class SnapmirrorConsistencyGroupFailoverSchema(ResourceSchema):
    """The fields of the SnapmirrorConsistencyGroupFailover object"""

    error = fields.Nested("netapp_ontap.models.error.ErrorSchema", unknown=EXCLUDE, data_key="error")
    r""" The error field of the snapmirror_consistency_group_failover. """

    status = fields.Nested("netapp_ontap.models.snapmirror_consistency_group_failover_status.SnapmirrorConsistencyGroupFailoverStatusSchema", unknown=EXCLUDE, data_key="status")
    r""" The status field of the snapmirror_consistency_group_failover. """

    @property
    def resource(self):
        return SnapmirrorConsistencyGroupFailover

    gettable_fields = [
        "error",
        "status",
    ]
    """error,status,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class SnapmirrorConsistencyGroupFailover(Resource):

    _schema = SnapmirrorConsistencyGroupFailoverSchema
