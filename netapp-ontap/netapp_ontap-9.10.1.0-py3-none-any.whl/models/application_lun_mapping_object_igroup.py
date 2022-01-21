r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ApplicationLunMappingObjectIgroup", "ApplicationLunMappingObjectIgroupSchema"]
__pdoc__ = {
    "ApplicationLunMappingObjectIgroupSchema.resource": False,
    "ApplicationLunMappingObjectIgroup": False,
}


class ApplicationLunMappingObjectIgroupSchema(ResourceSchema):
    """The fields of the ApplicationLunMappingObjectIgroup object"""

    initiators = fields.List(fields.Str, data_key="initiators")
    r""" The initiators field of the application_lun_mapping_object_igroup. """

    name = fields.Str(data_key="name")
    r""" Igroup name """

    uuid = fields.Str(data_key="uuid")
    r""" Igroup UUID """

    @property
    def resource(self):
        return ApplicationLunMappingObjectIgroup

    gettable_fields = [
        "initiators",
        "name",
        "uuid",
    ]
    """initiators,name,uuid,"""

    patchable_fields = [
        "initiators",
    ]
    """initiators,"""

    postable_fields = [
        "initiators",
    ]
    """initiators,"""


class ApplicationLunMappingObjectIgroup(Resource):

    _schema = ApplicationLunMappingObjectIgroupSchema
