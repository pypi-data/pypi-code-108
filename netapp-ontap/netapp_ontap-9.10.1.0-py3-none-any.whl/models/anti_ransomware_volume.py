r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["AntiRansomwareVolume", "AntiRansomwareVolumeSchema"]
__pdoc__ = {
    "AntiRansomwareVolumeSchema.resource": False,
    "AntiRansomwareVolume": False,
}


class AntiRansomwareVolumeSchema(ResourceSchema):
    """The fields of the AntiRansomwareVolume object"""

    attack_probability = fields.Str(data_key="attack_probability")
    r""" Probability of a ransomware attack.<br>`none` No files are suspected of ransomware activity.<br>`low` A number of files are suspected of ransomware activity.<br>`moderate` A moderate number of files are suspected of ransomware activity.<br>`high` A large number of files are suspected of ransomware activity.

Valid choices:

* none
* low
* moderate
* high """

    attack_reports = fields.List(fields.Nested("netapp_ontap.models.anti_ransomware_attack_report.AntiRansomwareAttackReportSchema", unknown=EXCLUDE), data_key="attack_reports")
    r""" The attack_reports field of the anti_ransomware_volume. """

    dry_run_start_time = ImpreciseDateTime(data_key="dry_run_start_time")
    r""" Time when Anti-ransomware monitoring `state` is set to dry-run value for starting evaluation mode. """

    space = fields.Nested("netapp_ontap.models.anti_ransomware_volume_space.AntiRansomwareVolumeSpaceSchema", unknown=EXCLUDE, data_key="space")
    r""" The space field of the anti_ransomware_volume. """

    state = fields.Str(data_key="state")
    r""" Anti-ransomware state.<br>`disabled` Anti-ransomware monitoring is disabled on the volume.  This is the default state in a POST operation.<br>`disable_in_progress` Anti-ransomware monitoring is being disabled and a cleanup operation is in effect. Valid in GET operation.<br>`dry_run` Anti-ransomware monitoring is enabled in the evaluation mode.<br>`enabled` Anti-ransomware monitoring is active on the volume.<br>`paused` Anti-ransomware monitoring is paused on the volume.<br>`enable_paused` Anti-ransomware monitoring is paused on the volume from its earlier enabled state. Valid in GET operation. <br>`dry_run_paused` Anti-ransomware monitoring is paused on the volume from its earlier dry_run state. Valid in GET operation. <br>For POST, the valid Anti-ransomware states are only `disabled`, `enabled` and `dry_run`, whereas for PATCH, `paused` is also valid along with the three valid states for POST.

Valid choices:

* disabled
* disable_in_progress
* dry_run
* enabled
* paused
* enable_paused
* dry_run_paused """

    suspect_files = fields.List(fields.Nested("netapp_ontap.models.anti_ransomware_volume_suspect_files.AntiRansomwareVolumeSuspectFilesSchema", unknown=EXCLUDE), data_key="suspect_files")
    r""" The suspect_files field of the anti_ransomware_volume. """

    @property
    def resource(self):
        return AntiRansomwareVolume

    gettable_fields = [
        "attack_probability",
        "attack_reports",
        "dry_run_start_time",
        "space",
        "state",
        "suspect_files",
    ]
    """attack_probability,attack_reports,dry_run_start_time,space,state,suspect_files,"""

    patchable_fields = [
        "state",
    ]
    """state,"""

    postable_fields = [
        "state",
    ]
    """state,"""


class AntiRansomwareVolume(Resource):

    _schema = AntiRansomwareVolumeSchema
