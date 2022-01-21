r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["VscanOnDemandPolicy", "VscanOnDemandPolicySchema"]
__pdoc__ = {
    "VscanOnDemandPolicySchema.resource": False,
    "VscanOnDemandPolicy": False,
}


class VscanOnDemandPolicySchema(ResourceSchema):
    """The fields of the VscanOnDemandPolicy object"""

    log_path = fields.Str(data_key="log_path")
    r""" The path from the Vserver root where the task report is created.

Example: /vol0/report_dir """

    name = fields.Str(data_key="name")
    r""" On-Demand task name

Example: task-1 """

    scan_paths = fields.List(fields.Str, data_key="scan_paths")
    r""" List of paths that need to be scanned.

Example: ["/vol1/","/vol2/cifs/"] """

    schedule = fields.Nested("netapp_ontap.resources.schedule.ScheduleSchema", unknown=EXCLUDE, data_key="schedule")
    r""" The schedule field of the vscan_on_demand_policy. """

    scope = fields.Nested("netapp_ontap.models.vscan_on_demand_scope.VscanOnDemandScopeSchema", unknown=EXCLUDE, data_key="scope")
    r""" The scope field of the vscan_on_demand_policy. """

    @property
    def resource(self):
        return VscanOnDemandPolicy

    gettable_fields = [
        "log_path",
        "name",
        "scan_paths",
        "schedule.links",
        "schedule.name",
        "schedule.uuid",
        "scope",
    ]
    """log_path,name,scan_paths,schedule.links,schedule.name,schedule.uuid,scope,"""

    patchable_fields = [
        "log_path",
        "scan_paths",
        "schedule.name",
        "schedule.uuid",
        "scope",
    ]
    """log_path,scan_paths,schedule.name,schedule.uuid,scope,"""

    postable_fields = [
        "log_path",
        "name",
        "scan_paths",
        "schedule.name",
        "schedule.uuid",
        "scope",
    ]
    """log_path,name,scan_paths,schedule.name,schedule.uuid,scope,"""


class VscanOnDemandPolicy(Resource):

    _schema = VscanOnDemandPolicySchema
