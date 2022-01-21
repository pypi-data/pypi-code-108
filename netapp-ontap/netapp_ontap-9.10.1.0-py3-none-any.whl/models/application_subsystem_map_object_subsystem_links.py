r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ApplicationSubsystemMapObjectSubsystemLinks", "ApplicationSubsystemMapObjectSubsystemLinksSchema"]
__pdoc__ = {
    "ApplicationSubsystemMapObjectSubsystemLinksSchema.resource": False,
    "ApplicationSubsystemMapObjectSubsystemLinks": False,
}


class ApplicationSubsystemMapObjectSubsystemLinksSchema(ResourceSchema):
    """The fields of the ApplicationSubsystemMapObjectSubsystemLinks object"""

    self_ = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="self")
    r""" The self_ field of the application_subsystem_map_object_subsystem_links. """

    @property
    def resource(self):
        return ApplicationSubsystemMapObjectSubsystemLinks

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


class ApplicationSubsystemMapObjectSubsystemLinks(Resource):

    _schema = ApplicationSubsystemMapObjectSubsystemLinksSchema
