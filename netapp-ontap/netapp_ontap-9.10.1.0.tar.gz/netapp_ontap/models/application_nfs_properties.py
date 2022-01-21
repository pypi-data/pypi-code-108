r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ApplicationNfsProperties", "ApplicationNfsPropertiesSchema"]
__pdoc__ = {
    "ApplicationNfsPropertiesSchema.resource": False,
    "ApplicationNfsProperties": False,
}


class ApplicationNfsPropertiesSchema(ResourceSchema):
    """The fields of the ApplicationNfsProperties object"""

    backing_storage = fields.Nested("netapp_ontap.models.application_cifs_properties_backing_storage.ApplicationCifsPropertiesBackingStorageSchema", unknown=EXCLUDE, data_key="backing_storage")
    r""" The backing_storage field of the application_nfs_properties. """

    export_policy = fields.Nested("netapp_ontap.models.application_nfs_properties_export_policy.ApplicationNfsPropertiesExportPolicySchema", unknown=EXCLUDE, data_key="export_policy")
    r""" The export_policy field of the application_nfs_properties. """

    ips = fields.List(fields.Str, data_key="ips")
    r""" The ips field of the application_nfs_properties. """

    path = fields.Str(data_key="path")
    r""" Junction path """

    permissions = fields.List(fields.Nested("netapp_ontap.models.application_nfs_properties_permissions.ApplicationNfsPropertiesPermissionsSchema", unknown=EXCLUDE), data_key="permissions")
    r""" The permissions field of the application_nfs_properties. """

    @property
    def resource(self):
        return ApplicationNfsProperties

    gettable_fields = [
        "backing_storage",
        "export_policy",
        "ips",
        "path",
        "permissions",
    ]
    """backing_storage,export_policy,ips,path,permissions,"""

    patchable_fields = [
        "backing_storage",
        "export_policy",
        "ips",
    ]
    """backing_storage,export_policy,ips,"""

    postable_fields = [
        "backing_storage",
        "export_policy",
        "ips",
    ]
    """backing_storage,export_policy,ips,"""


class ApplicationNfsProperties(Resource):

    _schema = ApplicationNfsPropertiesSchema
