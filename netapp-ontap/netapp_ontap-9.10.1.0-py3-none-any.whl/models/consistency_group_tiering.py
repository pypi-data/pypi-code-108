r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ConsistencyGroupTiering", "ConsistencyGroupTieringSchema"]
__pdoc__ = {
    "ConsistencyGroupTieringSchema.resource": False,
    "ConsistencyGroupTiering": False,
}


class ConsistencyGroupTieringSchema(ResourceSchema):
    """The fields of the ConsistencyGroupTiering object"""

    control = fields.Str(data_key="control")
    r""" Storage tiering placement rules for the object.

Valid choices:

* allowed
* best_effort
* disallowed
* required """

    policy = fields.Str(data_key="policy")
    r""" Policy that determines whether the user data blocks of a volume in a FabricPool will be tiered to the cloud store when they become cold.
<br>FabricPool combines flash (performance tier) with a cloud store into a single aggregate. Temperature of a volume block increases if it is accessed frequently and decreases when it is not. Valid in POST or PATCH.<br/>all &dash; Allows tiering of both Snapshot copies and active file system user data to the cloud store as soon as possible by ignoring the temperature on the volume blocks.<br/>auto &dash; Allows tiering of both snapshot and active file system user data to the cloud store<br/>none &dash; Volume blocks are not be tiered to the cloud store.<br/>snapshot_only &dash; Allows tiering of only the volume Snapshot copies not associated with the active file system.
<br>The default tiering policy is "snapshot-only" for a FlexVol volume and "none" for a FlexGroup volume. The default minimum cooling period for the "snapshot-only" tiering policy is 2 days and for the "auto" tiering policy it is 31 days.


Valid choices:

* all
* auto
* backup
* none
* snapshot_only """

    @property
    def resource(self):
        return ConsistencyGroupTiering

    gettable_fields = [
        "policy",
    ]
    """policy,"""

    patchable_fields = [
        "control",
    ]
    """control,"""

    postable_fields = [
        "control",
        "policy",
    ]
    """control,policy,"""


class ConsistencyGroupTiering(Resource):

    _schema = ConsistencyGroupTieringSchema
