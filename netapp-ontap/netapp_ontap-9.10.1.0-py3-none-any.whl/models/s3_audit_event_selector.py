r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["S3AuditEventSelector", "S3AuditEventSelectorSchema"]
__pdoc__ = {
    "S3AuditEventSelectorSchema.resource": False,
    "S3AuditEventSelector": False,
}


class S3AuditEventSelectorSchema(ResourceSchema):
    """The fields of the S3AuditEventSelector object"""

    access = fields.Str(data_key="access")
    r""" Specifies read and write access types.


Valid choices:

* read
* write
* all """

    permission = fields.Str(data_key="permission")
    r""" Specifies allow and deny permission types.


Valid choices:

* deny
* allow
* all """

    @property
    def resource(self):
        return S3AuditEventSelector

    gettable_fields = [
        "access",
        "permission",
    ]
    """access,permission,"""

    patchable_fields = [
        "access",
        "permission",
    ]
    """access,permission,"""

    postable_fields = [
        "access",
        "permission",
    ]
    """access,permission,"""


class S3AuditEventSelector(Resource):

    _schema = S3AuditEventSelectorSchema
