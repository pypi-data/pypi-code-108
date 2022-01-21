r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["SoftwareStatusDetails", "SoftwareStatusDetailsSchema"]
__pdoc__ = {
    "SoftwareStatusDetailsSchema.resource": False,
    "SoftwareStatusDetails": False,
}


class SoftwareStatusDetailsSchema(ResourceSchema):
    """The fields of the SoftwareStatusDetails object"""

    action = fields.Nested("netapp_ontap.models.software_status_details_reference_action.SoftwareStatusDetailsReferenceActionSchema", unknown=EXCLUDE, data_key="action")
    r""" The action field of the software_status_details. """

    end_time = ImpreciseDateTime(data_key="end_time")
    r""" End time for each status phase.

Example: 2019-02-02T19:00:00.000+0000 """

    issue = fields.Nested("netapp_ontap.models.software_status_details_reference_issue.SoftwareStatusDetailsReferenceIssueSchema", unknown=EXCLUDE, data_key="issue")
    r""" The issue field of the software_status_details. """

    name = fields.Str(data_key="name")
    r""" Name of the phase to be retrieved for status details.

Example: initialize """

    node = fields.Nested("netapp_ontap.models.software_status_details_reference_node.SoftwareStatusDetailsReferenceNodeSchema", unknown=EXCLUDE, data_key="node")
    r""" The node field of the software_status_details. """

    start_time = ImpreciseDateTime(data_key="start_time")
    r""" Start time for each status phase.

Example: 2019-02-02T19:00:00.000+0000 """

    state = fields.Str(data_key="state")
    r""" Status of the phase

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
        return SoftwareStatusDetails

    gettable_fields = [
        "action",
        "end_time",
        "issue",
        "name",
        "node",
        "start_time",
        "state",
    ]
    """action,end_time,issue,name,node,start_time,state,"""

    patchable_fields = [
        "action",
        "issue",
        "node",
    ]
    """action,issue,node,"""

    postable_fields = [
        "action",
        "issue",
        "node",
    ]
    """action,issue,node,"""


class SoftwareStatusDetails(Resource):

    _schema = SoftwareStatusDetailsSchema
