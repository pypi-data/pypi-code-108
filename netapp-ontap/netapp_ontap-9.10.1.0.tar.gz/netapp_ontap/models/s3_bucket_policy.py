r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["S3BucketPolicy", "S3BucketPolicySchema"]
__pdoc__ = {
    "S3BucketPolicySchema.resource": False,
    "S3BucketPolicy": False,
}


class S3BucketPolicySchema(ResourceSchema):
    """The fields of the S3BucketPolicy object"""

    statements = fields.List(fields.Nested("netapp_ontap.models.s3_bucket_policy_statement.S3BucketPolicyStatementSchema", unknown=EXCLUDE), data_key="statements")
    r""" Specifies bucket access policy statement. """

    @property
    def resource(self):
        return S3BucketPolicy

    gettable_fields = [
        "statements",
    ]
    """statements,"""

    patchable_fields = [
        "statements",
    ]
    """statements,"""

    postable_fields = [
        "statements",
    ]
    """statements,"""


class S3BucketPolicy(Resource):

    _schema = S3BucketPolicySchema
