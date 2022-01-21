r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ZappS3BucketApplicationComponentsAccessPoliciesConditions", "ZappS3BucketApplicationComponentsAccessPoliciesConditionsSchema"]
__pdoc__ = {
    "ZappS3BucketApplicationComponentsAccessPoliciesConditionsSchema.resource": False,
    "ZappS3BucketApplicationComponentsAccessPoliciesConditions": False,
}


class ZappS3BucketApplicationComponentsAccessPoliciesConditionsSchema(ResourceSchema):
    """The fields of the ZappS3BucketApplicationComponentsAccessPoliciesConditions object"""

    delimiters = fields.List(fields.Str, data_key="delimiters")
    r""" The delimiters field of the zapp_s3_bucket_application_components_access_policies_conditions. """

    max_keys = fields.List(Size, data_key="max_keys")
    r""" The max_keys field of the zapp_s3_bucket_application_components_access_policies_conditions. """

    operator = fields.Str(data_key="operator")
    r""" Policy Condition Operator. """

    prefixes = fields.List(fields.Str, data_key="prefixes")
    r""" The prefixes field of the zapp_s3_bucket_application_components_access_policies_conditions. """

    source_ips = fields.List(fields.Str, data_key="source_ips")
    r""" The source_ips field of the zapp_s3_bucket_application_components_access_policies_conditions. """

    usernames = fields.List(fields.Str, data_key="usernames")
    r""" The usernames field of the zapp_s3_bucket_application_components_access_policies_conditions. """

    @property
    def resource(self):
        return ZappS3BucketApplicationComponentsAccessPoliciesConditions

    gettable_fields = [
        "delimiters",
        "max_keys",
        "operator",
        "prefixes",
        "source_ips",
        "usernames",
    ]
    """delimiters,max_keys,operator,prefixes,source_ips,usernames,"""

    patchable_fields = [
        "delimiters",
        "max_keys",
        "prefixes",
        "source_ips",
        "usernames",
    ]
    """delimiters,max_keys,prefixes,source_ips,usernames,"""

    postable_fields = [
        "delimiters",
        "max_keys",
        "operator",
        "prefixes",
        "source_ips",
        "usernames",
    ]
    """delimiters,max_keys,operator,prefixes,source_ips,usernames,"""


class ZappS3BucketApplicationComponentsAccessPoliciesConditions(Resource):

    _schema = ZappS3BucketApplicationComponentsAccessPoliciesConditionsSchema
