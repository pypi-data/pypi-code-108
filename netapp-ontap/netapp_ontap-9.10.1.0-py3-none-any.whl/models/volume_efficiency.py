r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["VolumeEfficiency", "VolumeEfficiencySchema"]
__pdoc__ = {
    "VolumeEfficiencySchema.resource": False,
    "VolumeEfficiency": False,
}


class VolumeEfficiencySchema(ResourceSchema):
    """The fields of the VolumeEfficiency object"""

    application_io_size = fields.Str(data_key="application_io_size")
    r""" Block size to use by compression. Valid for POST.

Valid choices:

* 8k
* auto """

    compaction = fields.Str(data_key="compaction")
    r""" The system can be enabled/disabled compaction.<br>inline &dash; Data will be compacted first and written to the volume.<br>none &dash; None<br>mixed &dash; Read only field for FlexGroups, where some of the constituent volumes are compaction enabled and some are disabled.

Valid choices:

* inline
* none
* mixed """

    compression = fields.Str(data_key="compression")
    r""" The system can be enabled/disabled compression.<br>inline &dash; Data will be compressed first and written to the volume.<br>background &dash; Data will be written to the volume and compressed later.<br>both &dash; Inline compression compresses the data and write to the volume, background compression compresses only the blocks on which inline compression is not run.<br>none &dash; None<br>mixed &dash; Read only field for FlexGroups, where some of the constituent volumes are compression enabled and some are disabled.

Valid choices:

* inline
* background
* both
* none
* mixed """

    cross_volume_dedupe = fields.Str(data_key="cross_volume_dedupe")
    r""" The system can be enabled/disabled cross volume dedupe. it can be enabled only when dedupe is enabled.<br>inline &dash; Data will be cross volume deduped first and written to the volume.<br>background &dash; Data will be written to the volume and cross volume deduped later.<br>both &dash; Inline cross volume dedupe dedupes the data and write to the volume, background cross volume dedupe dedupes only the blocks on which inline dedupe is not run.<br>none &dash; None<br>mixed &dash; Read only field for FlexGroups, where some of the constituent volumes are cross volume dedupe enabled and some are disabled.

Valid choices:

* inline
* background
* both
* none
* mixed """

    dedupe = fields.Str(data_key="dedupe")
    r""" The system can be enabled/disabled dedupe.<br>inline &dash; Data will be deduped first and written to the volume.<br>background &dash; Data will be written to the volume and deduped later.<br>both &dash; Inline dedupe dedupes the data and write to the volume, background dedupe dedupes only the blocks on which inline dedupe is not run.<br>none &dash; None<br>mixed &dash; Read only field for FlexGroups, where some of the constituent volumes are dedupe enabled and some are disabled.

Valid choices:

* inline
* background
* both
* none
* mixed """

    last_op_begin = fields.Str(data_key="last_op_begin")
    r""" Last sis operation begin timestamp. """

    last_op_end = fields.Str(data_key="last_op_end")
    r""" Last sis operation end timestamp. """

    last_op_err = fields.Str(data_key="last_op_err")
    r""" Last sis operation error text. """

    last_op_size = Size(data_key="last_op_size")
    r""" Last sis operation size. """

    last_op_state = fields.Str(data_key="last_op_state")
    r""" Last sis operation state. """

    op_state = fields.Str(data_key="op_state")
    r""" Sis status of the volume.

Valid choices:

* idle
* initializing
* active
* undoing
* pending
* downgrading
* disabled """

    path = fields.Str(data_key="path")
    r""" Absolute volume path of the volume. """

    policy = fields.Nested("netapp_ontap.models.volume_efficiency_policy1.VolumeEfficiencyPolicy1Schema", unknown=EXCLUDE, data_key="policy")
    r""" The policy field of the volume_efficiency. """

    progress = fields.Str(data_key="progress")
    r""" Sis progress of the volume. """

    schedule = fields.Str(data_key="schedule")
    r""" Schedule associated with volume. """

    state = fields.Str(data_key="state")
    r""" Storage efficiency state of the volume. Currently, this field supports POST/PATCH only for RW (Read-Write) volumes on FSx for ONTAP.<br>disabled &dash; All storage efficiency features are disabled.<br>mixed &dash; Read-only field for FlexGroup volumes, storage efficiency is enabled on certain constituents and disabled on others.<br>On FSx for ONTAP &dash; <br> &emsp; enabled &dash; All supported storage efficiency features for the volume are enabled.<br> &emsp; custom &dash; Read-only field currently only supported for the FSx for ONTAP, user-defined storage efficiency features are enabled.<br>For other platforms &dash; <br> &emsp; enabled &dash; At least one storage efficiency feature for the volume is enabled.

Valid choices:

* disabled
* enabled
* mixed
* custom """

    storage_efficiency_mode = fields.Str(data_key="storage_efficiency_mode")
    r""" Storage efficiency mode used by volume. This parameter is supported only on AFF platform.

Valid choices:

* default
* efficient """

    type = fields.Str(data_key="type")
    r""" Sis Type of the volume.

Valid choices:

* regular
* snapvault """

    @property
    def resource(self):
        return VolumeEfficiency

    gettable_fields = [
        "compaction",
        "compression",
        "cross_volume_dedupe",
        "dedupe",
        "last_op_begin",
        "last_op_end",
        "last_op_err",
        "last_op_size",
        "last_op_state",
        "op_state",
        "path",
        "policy",
        "progress",
        "schedule",
        "state",
        "storage_efficiency_mode",
        "type",
    ]
    """compaction,compression,cross_volume_dedupe,dedupe,last_op_begin,last_op_end,last_op_err,last_op_size,last_op_state,op_state,path,policy,progress,schedule,state,storage_efficiency_mode,type,"""

    patchable_fields = [
        "compaction",
        "compression",
        "cross_volume_dedupe",
        "dedupe",
        "policy",
        "state",
        "storage_efficiency_mode",
    ]
    """compaction,compression,cross_volume_dedupe,dedupe,policy,state,storage_efficiency_mode,"""

    postable_fields = [
        "application_io_size",
        "compaction",
        "compression",
        "cross_volume_dedupe",
        "dedupe",
        "state",
        "storage_efficiency_mode",
    ]
    """application_io_size,compaction,compression,cross_volume_dedupe,dedupe,state,storage_efficiency_mode,"""


class VolumeEfficiency(Resource):

    _schema = VolumeEfficiencySchema
