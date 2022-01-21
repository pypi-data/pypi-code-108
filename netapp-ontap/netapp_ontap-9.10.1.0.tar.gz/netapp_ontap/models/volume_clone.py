r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["VolumeClone", "VolumeCloneSchema"]
__pdoc__ = {
    "VolumeCloneSchema.resource": False,
    "VolumeClone": False,
}


class VolumeCloneSchema(ResourceSchema):
    """The fields of the VolumeClone object"""

    is_flexclone = fields.Boolean(data_key="is_flexclone")
    r""" Specifies if this volume is a normal FlexVol or FlexClone. This field needs to be set when creating a FlexClone. Valid in POST. """

    parent_snapshot = fields.Nested("netapp_ontap.resources.snapshot.SnapshotSchema", unknown=EXCLUDE, data_key="parent_snapshot")
    r""" The parent_snapshot field of the volume_clone. """

    parent_svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", unknown=EXCLUDE, data_key="parent_svm")
    r""" The parent_svm field of the volume_clone. """

    parent_volume = fields.Nested("netapp_ontap.resources.volume.VolumeSchema", unknown=EXCLUDE, data_key="parent_volume")
    r""" The parent_volume field of the volume_clone. """

    split_complete_percent = Size(data_key="split_complete_percent")
    r""" Percentage of FlexClone blocks split from its parent volume. """

    split_estimate = Size(data_key="split_estimate")
    r""" Space required by the containing-aggregate to split the FlexClone volume. """

    split_initiated = fields.Boolean(data_key="split_initiated")
    r""" This field is set when split is executed on any FlexClone, that is when the FlexClone volume is split from its parent FlexVol. This field needs to be set for splitting a FlexClone form FlexVol. Valid in PATCH. """

    @property
    def resource(self):
        return VolumeClone

    gettable_fields = [
        "is_flexclone",
        "parent_snapshot.links",
        "parent_snapshot.name",
        "parent_snapshot.uuid",
        "parent_svm.links",
        "parent_svm.name",
        "parent_svm.uuid",
        "parent_volume.links",
        "parent_volume.name",
        "parent_volume.uuid",
        "split_complete_percent",
        "split_estimate",
        "split_initiated",
    ]
    """is_flexclone,parent_snapshot.links,parent_snapshot.name,parent_snapshot.uuid,parent_svm.links,parent_svm.name,parent_svm.uuid,parent_volume.links,parent_volume.name,parent_volume.uuid,split_complete_percent,split_estimate,split_initiated,"""

    patchable_fields = [
        "is_flexclone",
        "parent_snapshot.name",
        "parent_snapshot.uuid",
        "parent_svm.name",
        "parent_svm.uuid",
        "parent_volume.name",
        "parent_volume.uuid",
        "split_initiated",
    ]
    """is_flexclone,parent_snapshot.name,parent_snapshot.uuid,parent_svm.name,parent_svm.uuid,parent_volume.name,parent_volume.uuid,split_initiated,"""

    postable_fields = [
        "is_flexclone",
        "parent_snapshot.name",
        "parent_snapshot.uuid",
        "parent_svm.name",
        "parent_svm.uuid",
        "parent_volume.name",
        "parent_volume.uuid",
        "split_initiated",
    ]
    """is_flexclone,parent_snapshot.name,parent_snapshot.uuid,parent_svm.name,parent_svm.uuid,parent_volume.name,parent_volume.uuid,split_initiated,"""


class VolumeClone(Resource):

    _schema = VolumeCloneSchema
