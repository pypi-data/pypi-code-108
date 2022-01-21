r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ApplicationNfsPropertiesPermissions", "ApplicationNfsPropertiesPermissionsSchema"]
__pdoc__ = {
    "ApplicationNfsPropertiesPermissionsSchema.resource": False,
    "ApplicationNfsPropertiesPermissions": False,
}


class ApplicationNfsPropertiesPermissionsSchema(ResourceSchema):
    """The fields of the ApplicationNfsPropertiesPermissions object"""

    access = fields.Str(data_key="access")
    r""" Access granted to the host """

    host = fields.Str(data_key="host")
    r""" Host granted access """

    @property
    def resource(self):
        return ApplicationNfsPropertiesPermissions

    gettable_fields = [
        "access",
        "host",
    ]
    """access,host,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class ApplicationNfsPropertiesPermissions(Resource):

    _schema = ApplicationNfsPropertiesPermissionsSchema
