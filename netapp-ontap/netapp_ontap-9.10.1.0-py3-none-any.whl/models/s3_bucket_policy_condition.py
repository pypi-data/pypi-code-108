r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["S3BucketPolicyCondition", "S3BucketPolicyConditionSchema"]
__pdoc__ = {
    "S3BucketPolicyConditionSchema.resource": False,
    "S3BucketPolicyCondition": False,
}


class S3BucketPolicyConditionSchema(ResourceSchema):
    """The fields of the S3BucketPolicyCondition object"""

    delimiters = fields.List(fields.Str, data_key="delimiters")
    r""" An array of delimiters that are compared with the delimiter value specified at the time of execution of an S3-based command, using the condition operator specified.


Example: ["/"] """

    max_keys = fields.List(Size, data_key="max_keys")
    r""" An array of maximum keys that are allowed or denied to be retrieved using an S3 list operation, based on the condition operator specified.


Example: [1000] """

    operator = fields.Str(data_key="operator")
    r""" Condition operator that is applied to the specified condition key.

Valid choices:

* ip_address
* not_ip_address
* string_equals
* string_not_equals
* string_equals_ignore_case
* string_not_equals_ignore_case
* string_like
* string_not_like
* numeric_equals
* numeric_not_equals
* numeric_greater_than
* numeric_greater_than_equals
* numeric_less_than
* numeric_less_than_equals """

    prefixes = fields.List(fields.Str, data_key="prefixes")
    r""" An array of prefixes that are compared with the input prefix value specified at the time of execution of an S3-based command, using the condition operator specified.


Example: ["pref"] """

    source_ips = fields.List(fields.Str, data_key="source_ips")
    r""" An array of IP address ranges that are compared with the IP address of a source command at the time of execution of an S3-based command, using the condition operator specified.


Example: ["1.1.1.1","1.2.2.0/24"] """

    usernames = fields.List(fields.Str, data_key="usernames")
    r""" An array of usernames that a current user in the context is evaluated against using the condition operators.


Example: ["user1"] """

    @property
    def resource(self):
        return S3BucketPolicyCondition

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
        "operator",
        "prefixes",
        "source_ips",
        "usernames",
    ]
    """delimiters,max_keys,operator,prefixes,source_ips,usernames,"""

    postable_fields = [
        "delimiters",
        "max_keys",
        "operator",
        "prefixes",
        "source_ips",
        "usernames",
    ]
    """delimiters,max_keys,operator,prefixes,source_ips,usernames,"""


class S3BucketPolicyCondition(Resource):

    _schema = S3BucketPolicyConditionSchema
