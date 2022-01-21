r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["S3PolicyStatement", "S3PolicyStatementSchema"]
__pdoc__ = {
    "S3PolicyStatementSchema.resource": False,
    "S3PolicyStatement": False,
}


class S3PolicyStatementSchema(ResourceSchema):
    """The fields of the S3PolicyStatement object"""

    actions = fields.List(fields.Str, data_key="actions")
    r""" For each resource, S3 supports a set of operations. The resource operations allowed or denied are identified by an action list:

* GetObject - retrieves objects from a bucket.
* PutObject - puts objects in a bucket.
* DeleteObject - deletes objects from a bucket.
* ListBucket - lists the objects in a bucket.
* GetBucketAcl - retrieves the access control list (ACL) of a bucket.
* GetObjectAcl - retrieves the access control list (ACL) of an object.
* ListAllMyBuckets - lists all of the buckets in a server.
* ListBucketMultipartUploads - lists the multipart uploads in progress for a bucket.
* ListMultipartUploadParts - lists the parts in a multipart upload.
* GetObjectTagging - retrieves the tag set of an object.
* PutObjecttagging - sets the tag set for an object.
* DeleteObjectTagging - deletes the tag set of an object.
* GetBucketLocation - retrieves the location of a bucket.
The wildcard character "*" can be used to form a regular expression for specifying actions.


Example: ["*"] """

    effect = fields.Str(data_key="effect")
    r""" Specifies whether access is allowed or denied. If access (to allow) is not granted explicitly to a resource, access is implicitly denied. Access can also be denied explicitly to a resource, in order to make sure that a user cannot access it, even if a different policy grants access.

Valid choices:

* allow
* deny """

    index = Size(data_key="index")
    r""" Specifies a unique statement index used to identify a particular statement. This parameter should not be specified in the POST method. A statement index is automatically generated and is retrieved using the GET method. """

    resources = fields.List(fields.Str, data_key="resources")
    r""" The resources field of the s3_policy_statement.

Example: ["bucket1","bucket1/*"] """

    sid = fields.Str(data_key="sid")
    r""" Specifies the statement identifier which contains additional information about the statement.

Example: FullAccessToBucket1 """

    @property
    def resource(self):
        return S3PolicyStatement

    gettable_fields = [
        "actions",
        "effect",
        "index",
        "resources",
        "sid",
    ]
    """actions,effect,index,resources,sid,"""

    patchable_fields = [
        "actions",
        "effect",
        "resources",
        "sid",
    ]
    """actions,effect,resources,sid,"""

    postable_fields = [
        "actions",
        "effect",
        "resources",
        "sid",
    ]
    """actions,effect,resources,sid,"""


class S3PolicyStatement(Resource):

    _schema = S3PolicyStatementSchema
