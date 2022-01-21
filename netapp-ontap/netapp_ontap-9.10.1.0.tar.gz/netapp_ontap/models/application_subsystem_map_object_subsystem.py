r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ApplicationSubsystemMapObjectSubsystem", "ApplicationSubsystemMapObjectSubsystemSchema"]
__pdoc__ = {
    "ApplicationSubsystemMapObjectSubsystemSchema.resource": False,
    "ApplicationSubsystemMapObjectSubsystem": False,
}


class ApplicationSubsystemMapObjectSubsystemSchema(ResourceSchema):
    """The fields of the ApplicationSubsystemMapObjectSubsystem object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="_links")
    r""" The links field of the application_subsystem_map_object_subsystem. """

    hosts = fields.List(fields.Nested("netapp_ontap.models.application_subsystem_map_object_subsystem_hosts.ApplicationSubsystemMapObjectSubsystemHostsSchema", unknown=EXCLUDE), data_key="hosts")
    r""" The hosts field of the application_subsystem_map_object_subsystem. """

    name = fields.Str(data_key="name")
    r""" Subsystem name """

    uuid = fields.Str(data_key="uuid")
    r""" Subsystem UUID """

    @property
    def resource(self):
        return ApplicationSubsystemMapObjectSubsystem

    gettable_fields = [
        "links",
        "hosts",
        "name",
        "uuid",
    ]
    """links,hosts,name,uuid,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class ApplicationSubsystemMapObjectSubsystem(Resource):

    _schema = ApplicationSubsystemMapObjectSubsystemSchema
