r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["LunCopySource", "LunCopySourceSchema"]
__pdoc__ = {
    "LunCopySourceSchema.resource": False,
    "LunCopySource": False,
}


class LunCopySourceSchema(ResourceSchema):
    """The fields of the LunCopySource object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="_links")
    r""" The links field of the lun_copy_source. """

    max_throughput = Size(data_key="max_throughput")
    r""" The maximum data throughput, in bytes per second, that should be utilized in support of the LUN copy. This property can be used to throttle a transfer and limit its impact on the performance of the source and destination nodes. The specified value will be rounded up to the nearest megabyte.<br/>
If this property is not specified in a POST that begins a LUN copy, throttling is not applied to the data transfer.<br/>
For more information, see _Size properties_ in the _docs_ section of the ONTAP REST API documentation.<br/>
Valid only in a POST that begins a LUN copy or a PATCH when a LUN copy is already in process. """

    name = fields.Str(data_key="name")
    r""" The fully qualified path of the LUN copy source composed of a "/vol" prefix, the volume name, the (optional) qtree name, and base name of the LUN.<br/>
Set this property in POST to specify the source for a LUN copy operation.


Example: /vol/vol2/lun1 """

    progress = fields.Nested("netapp_ontap.models.lun_copy_source_progress.LunCopySourceProgressSchema", unknown=EXCLUDE, data_key="progress")
    r""" The progress field of the lun_copy_source. """

    uuid = fields.Str(data_key="uuid")
    r""" The unique identifier of the LUN copy source.<br/>
Set this property in POST to specify the source for a LUN copy operation.


Example: 03c05019-40d9-3945-c767-dca4c3be5e90 """

    @property
    def resource(self):
        return LunCopySource

    gettable_fields = [
        "links",
        "max_throughput",
        "name",
        "progress",
        "uuid",
    ]
    """links,max_throughput,name,progress,uuid,"""

    patchable_fields = [
        "max_throughput",
        "progress",
    ]
    """max_throughput,progress,"""

    postable_fields = [
        "max_throughput",
        "name",
        "uuid",
    ]
    """max_throughput,name,uuid,"""


class LunCopySource(Resource):

    _schema = LunCopySourceSchema
