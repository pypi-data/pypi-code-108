r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["LunMapReportingNodeLinks", "LunMapReportingNodeLinksSchema"]
__pdoc__ = {
    "LunMapReportingNodeLinksSchema.resource": False,
    "LunMapReportingNodeLinks": False,
}


class LunMapReportingNodeLinksSchema(ResourceSchema):
    """The fields of the LunMapReportingNodeLinks object"""

    node = fields.Nested("netapp_ontap.models.href.HrefSchema", unknown=EXCLUDE, data_key="node")
    r""" The node field of the lun_map_reporting_node_links. """

    self_ = fields.Nested("netapp_ontap.models.href.HrefSchema", unknown=EXCLUDE, data_key="self")
    r""" The self_ field of the lun_map_reporting_node_links. """

    @property
    def resource(self):
        return LunMapReportingNodeLinks

    gettable_fields = [
        "node",
        "self_",
    ]
    """node,self_,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class LunMapReportingNodeLinks(Resource):

    _schema = LunMapReportingNodeLinksSchema
