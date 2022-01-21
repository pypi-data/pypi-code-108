r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["VolumeSnapmirrorDestinations", "VolumeSnapmirrorDestinationsSchema"]
__pdoc__ = {
    "VolumeSnapmirrorDestinationsSchema.resource": False,
    "VolumeSnapmirrorDestinations": False,
}


class VolumeSnapmirrorDestinationsSchema(ResourceSchema):
    """The fields of the VolumeSnapmirrorDestinations object"""

    is_cloud = fields.Boolean(data_key="is_cloud")
    r""" Specifies whether a volume is a SnapMirror source volume, using SnapMirror to protect its data to a cloud destination. """

    is_ontap = fields.Boolean(data_key="is_ontap")
    r""" Specifies whether a volume is a SnapMirror source volume, using SnapMirror to protect its data to an ONTAP destination. """

    @property
    def resource(self):
        return VolumeSnapmirrorDestinations

    gettable_fields = [
        "is_cloud",
        "is_ontap",
    ]
    """is_cloud,is_ontap,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class VolumeSnapmirrorDestinations(Resource):

    _schema = VolumeSnapmirrorDestinationsSchema
