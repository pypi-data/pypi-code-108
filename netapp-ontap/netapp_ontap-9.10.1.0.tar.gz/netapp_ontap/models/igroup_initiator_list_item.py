r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["IgroupInitiatorListItem", "IgroupInitiatorListItemSchema"]
__pdoc__ = {
    "IgroupInitiatorListItemSchema.resource": False,
    "IgroupInitiatorListItem": False,
}


class IgroupInitiatorListItemSchema(ResourceSchema):
    """The fields of the IgroupInitiatorListItem object"""

    links = fields.Nested("netapp_ontap.models.igroup_initiator_list_item_links.IgroupInitiatorListItemLinksSchema", unknown=EXCLUDE, data_key="_links")
    r""" The links field of the igroup_initiator_list_item. """

    comment = fields.Str(data_key="comment")
    r""" A comment available for use by the administrator. Valid in POST and PATCH. """

    igroup = fields.Nested("netapp_ontap.resources.igroup.IgroupSchema", unknown=EXCLUDE, data_key="igroup")
    r""" The igroup field of the igroup_initiator_list_item. """

    name = fields.Str(data_key="name")
    r""" The FC WWPN, iSCSI IQN, or iSCSI EUI that identifies the host initiator. Valid in POST only and not allowed when the `records` property is used.<br/>
An FC WWPN consists of 16 hexadecimal digits grouped as 8 pairs separated by colons. The format for an iSCSI IQN is _iqn.yyyy-mm.reverse_domain_name:any_. The iSCSI EUI format consists of the _eui._ prefix followed by 16 hexadecimal characters.


Example: iqn.1998-01.com.corp.iscsi:name1 """

    @property
    def resource(self):
        return IgroupInitiatorListItem

    gettable_fields = [
        "links",
        "comment",
        "igroup.links",
        "igroup.name",
        "igroup.uuid",
        "name",
    ]
    """links,comment,igroup.links,igroup.name,igroup.uuid,name,"""

    patchable_fields = [
        "comment",
        "igroup.name",
        "igroup.uuid",
    ]
    """comment,igroup.name,igroup.uuid,"""

    postable_fields = [
        "comment",
        "igroup.name",
        "igroup.uuid",
        "name",
    ]
    """comment,igroup.name,igroup.uuid,name,"""


class IgroupInitiatorListItem(Resource):

    _schema = IgroupInitiatorListItemSchema
