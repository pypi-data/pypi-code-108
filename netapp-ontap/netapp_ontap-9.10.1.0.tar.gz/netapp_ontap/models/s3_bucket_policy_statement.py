r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["S3BucketPolicyStatement", "S3BucketPolicyStatementSchema"]
__pdoc__ = {
    "S3BucketPolicyStatementSchema.resource": False,
    "S3BucketPolicyStatement": False,
}


class S3BucketPolicyStatementSchema(ResourceSchema):
    """The fields of the S3BucketPolicyStatement object"""

    actions = fields.List(fields.Str, data_key="actions")
    r""" The actions field of the s3_bucket_policy_statement.

Example: ["GetObject","PutObject","DeleteObject","ListBucket"] """

    conditions = fields.List(fields.Nested("netapp_ontap.models.s3_bucket_policy_condition.S3BucketPolicyConditionSchema", unknown=EXCLUDE), data_key="conditions")
    r""" Specifies bucket policy conditions. """

    effect = fields.Str(data_key="effect")
    r""" Specifies whether access is allowed or denied when a user requests the specific action. If access (to allow) is not granted explicitly to a resource, access is implicitly denied. Access can also be denied explicitly to a resource, in order to make sure that a user cannot access it, even if a different policy grants access.

Valid choices:

* allow
* deny """

    principals = fields.List(fields.Str, data_key="principals")
    r""" The principals field of the s3_bucket_policy_statement.

Example: ["user1","group/grp1"] """

    resources = fields.List(fields.Str, data_key="resources")
    r""" The resources field of the s3_bucket_policy_statement.

Example: ["bucket1","bucket1/*"] """

    sid = fields.Str(data_key="sid")
    r""" Specifies the statement identifier used to differentiate between statements.

Example: FullAccessToUser1 """

    @property
    def resource(self):
        return S3BucketPolicyStatement

    gettable_fields = [
        "actions",
        "conditions",
        "effect",
        "principals",
        "resources",
        "sid",
    ]
    """actions,conditions,effect,principals,resources,sid,"""

    patchable_fields = [
        "actions",
        "conditions",
        "effect",
        "principals",
        "resources",
        "sid",
    ]
    """actions,conditions,effect,principals,resources,sid,"""

    postable_fields = [
        "actions",
        "conditions",
        "effect",
        "principals",
        "resources",
        "sid",
    ]
    """actions,conditions,effect,principals,resources,sid,"""


class S3BucketPolicyStatement(Resource):

    _schema = S3BucketPolicyStatementSchema
