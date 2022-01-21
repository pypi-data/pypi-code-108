r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ZappS3BucketApplicationComponentsAccessPolicies", "ZappS3BucketApplicationComponentsAccessPoliciesSchema"]
__pdoc__ = {
    "ZappS3BucketApplicationComponentsAccessPoliciesSchema.resource": False,
    "ZappS3BucketApplicationComponentsAccessPolicies": False,
}


class ZappS3BucketApplicationComponentsAccessPoliciesSchema(ResourceSchema):
    """The fields of the ZappS3BucketApplicationComponentsAccessPolicies object"""

    actions = fields.List(fields.Str, data_key="actions")
    r""" The actions field of the zapp_s3_bucket_application_components_access_policies. """

    conditions = fields.List(fields.Nested("netapp_ontap.models.zapp_s3_bucket_application_components_access_policies_conditions.ZappS3BucketApplicationComponentsAccessPoliciesConditionsSchema", unknown=EXCLUDE), data_key="conditions")
    r""" conditions. """

    effect = fields.Str(data_key="effect")
    r""" Allow or Deny Access.

Valid choices:

* allow
* deny """

    principals = fields.List(fields.Str, data_key="principals")
    r""" The principals field of the zapp_s3_bucket_application_components_access_policies. """

    resources = fields.List(fields.Str, data_key="resources")
    r""" The resources field of the zapp_s3_bucket_application_components_access_policies. """

    sid = fields.Str(data_key="sid")
    r""" Statement Identifier Usage: &lt;(size 1..256)&gt; """

    @property
    def resource(self):
        return ZappS3BucketApplicationComponentsAccessPolicies

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
        "principals",
        "resources",
    ]
    """actions,principals,resources,"""

    postable_fields = [
        "actions",
        "conditions",
        "effect",
        "principals",
        "resources",
        "sid",
    ]
    """actions,conditions,effect,principals,resources,sid,"""


class ZappS3BucketApplicationComponentsAccessPolicies(Resource):

    _schema = ZappS3BucketApplicationComponentsAccessPoliciesSchema
