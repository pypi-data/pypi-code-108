r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["SoftwareUpdateDetails", "SoftwareUpdateDetailsSchema"]
__pdoc__ = {
    "SoftwareUpdateDetailsSchema.resource": False,
    "SoftwareUpdateDetails": False,
}


class SoftwareUpdateDetailsSchema(ResourceSchema):
    """The fields of the SoftwareUpdateDetails object"""

    elapsed_duration = Size(data_key="elapsed_duration")
    r""" Elapsed duration for each update phase

Example: 2100 """

    estimated_duration = Size(data_key="estimated_duration")
    r""" Estimated duration for each update phase

Example: 4620 """

    node = fields.Nested("netapp_ontap.models.software_update_details_reference_node.SoftwareUpdateDetailsReferenceNodeSchema", unknown=EXCLUDE, data_key="node")
    r""" The node field of the software_update_details. """

    phase = fields.Str(data_key="phase")
    r""" Phase details

Example: Post-update checks """

    state = fields.Str(data_key="state")
    r""" State of the update phase

Valid choices:

* in_progress
* waiting
* paused_by_user
* paused_on_error
* completed
* canceled
* failed
* pause_pending
* cancel_pending """

    @property
    def resource(self):
        return SoftwareUpdateDetails

    gettable_fields = [
        "elapsed_duration",
        "estimated_duration",
        "node",
        "phase",
        "state",
    ]
    """elapsed_duration,estimated_duration,node,phase,state,"""

    patchable_fields = [
        "node",
    ]
    """node,"""

    postable_fields = [
        "node",
    ]
    """node,"""


class SoftwareUpdateDetails(Resource):

    _schema = SoftwareUpdateDetailsSchema
