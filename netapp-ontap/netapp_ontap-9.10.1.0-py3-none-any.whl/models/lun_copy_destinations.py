r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["LunCopyDestinations", "LunCopyDestinationsSchema"]
__pdoc__ = {
    "LunCopyDestinationsSchema.resource": False,
    "LunCopyDestinations": False,
}


class LunCopyDestinationsSchema(ResourceSchema):
    """The fields of the LunCopyDestinations object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="_links")
    r""" The links field of the lun_copy_destinations. """

    max_throughput = Size(data_key="max_throughput")
    r""" The maximum data throughput, in bytes per second, that should be utilized in support of the LUN copy. See property `copy.source.max_throughput` for further details. """

    name = fields.Str(data_key="name")
    r""" The fully qualified path of the LUN copy destination composed of a "/vol" prefix, the volume name, the (optional) qtree name, and base name of the LUN.


Example: /vol/vol1/lun1 """

    progress = fields.Nested("netapp_ontap.models.lun_copy_progress.LunCopyProgressSchema", unknown=EXCLUDE, data_key="progress")
    r""" The progress field of the lun_copy_destinations. """

    uuid = fields.Str(data_key="uuid")
    r""" The unique identifier of the LUN copy destination.


Example: 1bc327d5-4654-5284-a116-f182282240b4 """

    @property
    def resource(self):
        return LunCopyDestinations

    gettable_fields = [
        "links",
        "max_throughput",
        "name",
        "progress",
        "uuid",
    ]
    """links,max_throughput,name,progress,uuid,"""

    patchable_fields = [
        "progress",
    ]
    """progress,"""

    postable_fields = [
        "progress",
    ]
    """progress,"""


class LunCopyDestinations(Resource):

    _schema = LunCopyDestinationsSchema
