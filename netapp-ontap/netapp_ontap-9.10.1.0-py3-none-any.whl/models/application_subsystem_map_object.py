r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ApplicationSubsystemMapObject", "ApplicationSubsystemMapObjectSchema"]
__pdoc__ = {
    "ApplicationSubsystemMapObjectSchema.resource": False,
    "ApplicationSubsystemMapObject": False,
}


class ApplicationSubsystemMapObjectSchema(ResourceSchema):
    """The fields of the ApplicationSubsystemMapObject object"""

    anagrpid = fields.Str(data_key="anagrpid")
    r""" Subsystem ANA group ID """

    nsid = fields.Str(data_key="nsid")
    r""" Subsystem namespace ID """

    subsystem = fields.Nested("netapp_ontap.models.application_subsystem_map_object_subsystem.ApplicationSubsystemMapObjectSubsystemSchema", unknown=EXCLUDE, data_key="subsystem")
    r""" The subsystem field of the application_subsystem_map_object. """

    @property
    def resource(self):
        return ApplicationSubsystemMapObject

    gettable_fields = [
        "anagrpid",
        "nsid",
        "subsystem",
    ]
    """anagrpid,nsid,subsystem,"""

    patchable_fields = [
        "subsystem",
    ]
    """subsystem,"""

    postable_fields = [
        "subsystem",
    ]
    """subsystem,"""


class ApplicationSubsystemMapObject(Resource):

    _schema = ApplicationSubsystemMapObjectSchema
