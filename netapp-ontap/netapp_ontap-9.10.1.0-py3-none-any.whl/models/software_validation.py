r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["SoftwareValidation", "SoftwareValidationSchema"]
__pdoc__ = {
    "SoftwareValidationSchema.resource": False,
    "SoftwareValidation": False,
}


class SoftwareValidationSchema(ResourceSchema):
    """The fields of the SoftwareValidation object"""

    action = fields.Nested("netapp_ontap.models.software_validation_reference_action.SoftwareValidationReferenceActionSchema", unknown=EXCLUDE, data_key="action")
    r""" The action field of the software_validation. """

    issue = fields.Nested("netapp_ontap.models.software_validation_reference_issue.SoftwareValidationReferenceIssueSchema", unknown=EXCLUDE, data_key="issue")
    r""" The issue field of the software_validation. """

    status = fields.Str(data_key="status")
    r""" Status of the update check.

Valid choices:

* warning
* error """

    update_check = fields.Str(data_key="update_check")
    r""" Name of the update check.

Example: nfs_mounts """

    @property
    def resource(self):
        return SoftwareValidation

    gettable_fields = [
        "action",
        "issue",
        "status",
        "update_check",
    ]
    """action,issue,status,update_check,"""

    patchable_fields = [
        "action",
        "issue",
    ]
    """action,issue,"""

    postable_fields = [
        "action",
        "issue",
    ]
    """action,issue,"""


class SoftwareValidation(Resource):

    _schema = SoftwareValidationSchema
