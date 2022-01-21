r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["IscsiSessionInitiator", "IscsiSessionInitiatorSchema"]
__pdoc__ = {
    "IscsiSessionInitiatorSchema.resource": False,
    "IscsiSessionInitiator": False,
}


class IscsiSessionInitiatorSchema(ResourceSchema):
    """The fields of the IscsiSessionInitiator object"""

    alias = fields.Str(data_key="alias")
    r""" The initiator alias.


Example: initiator_alias1 """

    comment = fields.Str(data_key="comment")
    r""" A comment available for use by the administrator. This is modifiable from the initiator REST endpoint directly. See [`PATCH /protocols/san/igroups/{igroup.uuid}/initiators/{name}`](#/SAN/igroup_initiator_modify).


Example: This is an iSCSI initiator for host 5 """

    name = fields.Str(data_key="name")
    r""" The world wide unique name of the initiator.


Example: iqn.1992-01.example.com:string """

    @property
    def resource(self):
        return IscsiSessionInitiator

    gettable_fields = [
        "alias",
        "comment",
        "name",
    ]
    """alias,comment,name,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class IscsiSessionInitiator(Resource):

    _schema = IscsiSessionInitiatorSchema
