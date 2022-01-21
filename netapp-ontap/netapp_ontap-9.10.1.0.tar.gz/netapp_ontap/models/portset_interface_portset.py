r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["PortsetInterfacePortset", "PortsetInterfacePortsetSchema"]
__pdoc__ = {
    "PortsetInterfacePortsetSchema.resource": False,
    "PortsetInterfacePortset": False,
}


class PortsetInterfacePortsetSchema(ResourceSchema):
    """The fields of the PortsetInterfacePortset object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="_links")
    r""" The links field of the portset_interface_portset. """

    uuid = fields.Str(data_key="uuid")
    r""" The unique identifier of the portset.


Example: 4ea7a442-86d1-11e0-ae1c-123478563412 """

    @property
    def resource(self):
        return PortsetInterfacePortset

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


class PortsetInterfacePortset(Resource):

    _schema = PortsetInterfacePortsetSchema
