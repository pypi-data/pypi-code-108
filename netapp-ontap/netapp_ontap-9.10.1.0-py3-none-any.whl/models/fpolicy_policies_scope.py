r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["FpolicyPoliciesScope", "FpolicyPoliciesScopeSchema"]
__pdoc__ = {
    "FpolicyPoliciesScopeSchema.resource": False,
    "FpolicyPoliciesScope": False,
}


class FpolicyPoliciesScopeSchema(ResourceSchema):
    """The fields of the FpolicyPoliciesScope object"""

    exclude_export_policies = fields.List(fields.Str, data_key="exclude_export_policies")
    r""" The exclude_export_policies field of the fpolicy_policies_scope. """

    exclude_extension = fields.List(fields.Str, data_key="exclude_extension")
    r""" The exclude_extension field of the fpolicy_policies_scope. """

    exclude_shares = fields.List(fields.Str, data_key="exclude_shares")
    r""" The exclude_shares field of the fpolicy_policies_scope. """

    exclude_volumes = fields.List(fields.Str, data_key="exclude_volumes")
    r""" The exclude_volumes field of the fpolicy_policies_scope.

Example: ["vol1","vol_svm1","*"] """

    include_export_policies = fields.List(fields.Str, data_key="include_export_policies")
    r""" The include_export_policies field of the fpolicy_policies_scope. """

    include_extension = fields.List(fields.Str, data_key="include_extension")
    r""" The include_extension field of the fpolicy_policies_scope. """

    include_shares = fields.List(fields.Str, data_key="include_shares")
    r""" The include_shares field of the fpolicy_policies_scope.

Example: ["sh1","share_cifs"] """

    include_volumes = fields.List(fields.Str, data_key="include_volumes")
    r""" The include_volumes field of the fpolicy_policies_scope.

Example: ["vol1","vol_svm1"] """

    @property
    def resource(self):
        return FpolicyPoliciesScope

    gettable_fields = [
        "exclude_export_policies",
        "exclude_extension",
        "exclude_shares",
        "exclude_volumes",
        "include_export_policies",
        "include_extension",
        "include_shares",
        "include_volumes",
    ]
    """exclude_export_policies,exclude_extension,exclude_shares,exclude_volumes,include_export_policies,include_extension,include_shares,include_volumes,"""

    patchable_fields = [
        "exclude_export_policies",
        "exclude_extension",
        "exclude_shares",
        "exclude_volumes",
        "include_export_policies",
        "include_extension",
        "include_shares",
        "include_volumes",
    ]
    """exclude_export_policies,exclude_extension,exclude_shares,exclude_volumes,include_export_policies,include_extension,include_shares,include_volumes,"""

    postable_fields = [
        "exclude_export_policies",
        "exclude_extension",
        "exclude_shares",
        "exclude_volumes",
        "include_export_policies",
        "include_extension",
        "include_shares",
        "include_volumes",
    ]
    """exclude_export_policies,exclude_extension,exclude_shares,exclude_volumes,include_export_policies,include_extension,include_shares,include_volumes,"""


class FpolicyPoliciesScope(Resource):

    _schema = FpolicyPoliciesScopeSchema
