r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["SecurityAuditLogSvm", "SecurityAuditLogSvmSchema"]
__pdoc__ = {
    "SecurityAuditLogSvmSchema.resource": False,
    "SecurityAuditLogSvm": False,
}


class SecurityAuditLogSvmSchema(ResourceSchema):
    """The fields of the SecurityAuditLogSvm object"""

    name = fields.Str(data_key="name")
    r""" The name field of the security_audit_log_svm. """

    @property
    def resource(self):
        return SecurityAuditLogSvm

    gettable_fields = [
        "name",
    ]
    """name,"""

    patchable_fields = [
        "name",
    ]
    """name,"""

    postable_fields = [
        "name",
    ]
    """name,"""


class SecurityAuditLogSvm(Resource):

    _schema = SecurityAuditLogSvmSchema
