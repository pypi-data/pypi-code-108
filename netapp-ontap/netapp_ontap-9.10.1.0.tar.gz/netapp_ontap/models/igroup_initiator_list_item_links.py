r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["IgroupInitiatorListItemLinks", "IgroupInitiatorListItemLinksSchema"]
__pdoc__ = {
    "IgroupInitiatorListItemLinksSchema.resource": False,
    "IgroupInitiatorListItemLinks": False,
}


class IgroupInitiatorListItemLinksSchema(ResourceSchema):
    """The fields of the IgroupInitiatorListItemLinks object"""

    self_ = fields.Nested("netapp_ontap.models.href.HrefSchema", unknown=EXCLUDE, data_key="self")
    r""" The self_ field of the igroup_initiator_list_item_links. """

    @property
    def resource(self):
        return IgroupInitiatorListItemLinks

    gettable_fields = [
        "self_",
    ]
    """self_,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class IgroupInitiatorListItemLinks(Resource):

    _schema = IgroupInitiatorListItemLinksSchema
