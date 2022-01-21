r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ApplicationSubsystemMapObjectSubsystemHosts", "ApplicationSubsystemMapObjectSubsystemHostsSchema"]
__pdoc__ = {
    "ApplicationSubsystemMapObjectSubsystemHostsSchema.resource": False,
    "ApplicationSubsystemMapObjectSubsystemHosts": False,
}


class ApplicationSubsystemMapObjectSubsystemHostsSchema(ResourceSchema):
    """The fields of the ApplicationSubsystemMapObjectSubsystemHosts object"""

    links = fields.Nested("netapp_ontap.models.application_subsystem_map_object_subsystem_links.ApplicationSubsystemMapObjectSubsystemLinksSchema", unknown=EXCLUDE, data_key="_links")
    r""" The links field of the application_subsystem_map_object_subsystem_hosts. """

    nqn = fields.Str(data_key="nqn")
    r""" Host """

    @property
    def resource(self):
        return ApplicationSubsystemMapObjectSubsystemHosts

    gettable_fields = [
        "links",
        "nqn",
    ]
    """links,nqn,"""

    patchable_fields = [
        "links",
    ]
    """links,"""

    postable_fields = [
        "links",
    ]
    """links,"""


class ApplicationSubsystemMapObjectSubsystemHosts(Resource):

    _schema = ApplicationSubsystemMapObjectSubsystemHostsSchema
