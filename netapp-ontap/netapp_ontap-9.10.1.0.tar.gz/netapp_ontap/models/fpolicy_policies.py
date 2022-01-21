r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["FpolicyPolicies", "FpolicyPoliciesSchema"]
__pdoc__ = {
    "FpolicyPoliciesSchema.resource": False,
    "FpolicyPolicies": False,
}


class FpolicyPoliciesSchema(ResourceSchema):
    """The fields of the FpolicyPolicies object"""

    enabled = fields.Boolean(data_key="enabled")
    r""" Specifies if the policy is enabled on the SVM or not. If no value is
mentioned for this field but priority is set, then this policy will be enabled. """

    engine = fields.Nested("netapp_ontap.resources.fpolicy_engine.FpolicyEngineSchema", unknown=EXCLUDE, data_key="engine")
    r""" The engine field of the fpolicy_policies. """

    events = fields.List(fields.Nested("netapp_ontap.resources.fpolicy_event.FpolicyEventSchema", unknown=EXCLUDE), data_key="events")
    r""" The events field of the fpolicy_policies.

Example: ["event_nfs_close","event_open"] """

    mandatory = fields.Boolean(data_key="mandatory")
    r""" Specifies what action to take on a file access event in a case when all primary and secondary servers are down or no response is received from the FPolicy servers within a given timeout period. When this parameter is set to true, file access events will be denied under these circumstances. """

    name = fields.Str(data_key="name")
    r""" Specifies the name of the policy.

Example: fp_policy_1 """

    priority = Size(data_key="priority")
    r""" Specifies the priority that is assigned to this policy. """

    scope = fields.Nested("netapp_ontap.models.fpolicy_policies_scope.FpolicyPoliciesScopeSchema", unknown=EXCLUDE, data_key="scope")
    r""" The scope field of the fpolicy_policies. """

    @property
    def resource(self):
        return FpolicyPolicies

    gettable_fields = [
        "enabled",
        "engine.links",
        "engine.name",
        "events",
        "mandatory",
        "name",
        "priority",
        "scope",
    ]
    """enabled,engine.links,engine.name,events,mandatory,name,priority,scope,"""

    patchable_fields = [
        "enabled",
        "engine.name",
        "events",
        "mandatory",
        "priority",
        "scope",
    ]
    """enabled,engine.name,events,mandatory,priority,scope,"""

    postable_fields = [
        "engine.name",
        "events",
        "mandatory",
        "name",
        "priority",
        "scope",
    ]
    """engine.name,events,mandatory,name,priority,scope,"""


class FpolicyPolicies(Resource):

    _schema = FpolicyPoliciesSchema
