r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["LunMapReportingNodeIgroup", "LunMapReportingNodeIgroupSchema"]
__pdoc__ = {
    "LunMapReportingNodeIgroupSchema.resource": False,
    "LunMapReportingNodeIgroup": False,
}


class LunMapReportingNodeIgroupSchema(ResourceSchema):
    """The fields of the LunMapReportingNodeIgroup object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="_links")
    r""" The links field of the lun_map_reporting_node_igroup. """

    uuid = fields.Str(data_key="uuid")
    r""" The unique identifier of the initiator group.


Example: 4ea7a442-86d1-11e0-ae1c-123478563412 """

    @property
    def resource(self):
        return LunMapReportingNodeIgroup

    gettable_fields = [
        "links",
        "uuid",
    ]
    """links,uuid,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class LunMapReportingNodeIgroup(Resource):

    _schema = LunMapReportingNodeIgroupSchema
