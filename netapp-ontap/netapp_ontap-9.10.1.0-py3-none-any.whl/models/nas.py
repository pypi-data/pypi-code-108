r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["Nas", "NasSchema"]
__pdoc__ = {
    "NasSchema.resource": False,
    "Nas": False,
}


class NasSchema(ResourceSchema):
    """The fields of the Nas object"""

    application_components = fields.List(fields.Nested("netapp_ontap.models.nas_application_components.NasApplicationComponentsSchema", unknown=EXCLUDE), data_key="application_components")
    r""" The application_components field of the nas. """

    cifs_access = fields.List(fields.Nested("netapp_ontap.models.app_cifs_access.AppCifsAccessSchema", unknown=EXCLUDE), data_key="cifs_access")
    r""" The list of CIFS access controls. You must provide either 'user_or_group' or 'access' to enable CIFS access. """

    exclude_aggregates = fields.List(fields.Nested("netapp_ontap.models.nas_exclude_aggregates.NasExcludeAggregatesSchema", unknown=EXCLUDE), data_key="exclude_aggregates")
    r""" The exclude_aggregates field of the nas. """

    nfs_access = fields.List(fields.Nested("netapp_ontap.models.app_nfs_access.AppNfsAccessSchema", unknown=EXCLUDE), data_key="nfs_access")
    r""" The list of NFS access controls. You must provide either 'host' or 'access' to enable NFS access. """

    protection_type = fields.Nested("netapp_ontap.models.nas_protection_type.NasProtectionTypeSchema", unknown=EXCLUDE, data_key="protection_type")
    r""" The protection_type field of the nas. """

    @property
    def resource(self):
        return Nas

    gettable_fields = [
        "application_components",
        "cifs_access",
        "exclude_aggregates",
        "nfs_access",
        "protection_type",
    ]
    """application_components,cifs_access,exclude_aggregates,nfs_access,protection_type,"""

    patchable_fields = [
        "application_components",
        "protection_type",
    ]
    """application_components,protection_type,"""

    postable_fields = [
        "application_components",
        "cifs_access",
        "exclude_aggregates",
        "nfs_access",
        "protection_type",
    ]
    """application_components,cifs_access,exclude_aggregates,nfs_access,protection_type,"""


class Nas(Resource):

    _schema = NasSchema
