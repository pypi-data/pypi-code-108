r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["San", "SanSchema"]
__pdoc__ = {
    "SanSchema.resource": False,
    "San": False,
}


class SanSchema(ResourceSchema):
    """The fields of the San object"""

    application_components = fields.List(fields.Nested("netapp_ontap.models.san_application_components.SanApplicationComponentsSchema", unknown=EXCLUDE), data_key="application_components")
    r""" The application_components field of the san. """

    exclude_aggregates = fields.List(fields.Nested("netapp_ontap.models.nas_exclude_aggregates.NasExcludeAggregatesSchema", unknown=EXCLUDE), data_key="exclude_aggregates")
    r""" The exclude_aggregates field of the san. """

    new_igroups = fields.List(fields.Nested("netapp_ontap.models.san_new_igroups.SanNewIgroupsSchema", unknown=EXCLUDE), data_key="new_igroups")
    r""" The list of initiator groups to create. """

    os_type = fields.Str(data_key="os_type")
    r""" The name of the host OS running the application.

Valid choices:

* aix
* hpux
* hyper_v
* linux
* netware
* openvms
* solaris
* solaris_efi
* vmware
* windows
* windows_2008
* windows_gpt
* xen """

    protection_type = fields.Nested("netapp_ontap.models.nas_protection_type.NasProtectionTypeSchema", unknown=EXCLUDE, data_key="protection_type")
    r""" The protection_type field of the san. """

    @property
    def resource(self):
        return San

    gettable_fields = [
        "application_components",
        "exclude_aggregates",
        "os_type",
        "protection_type",
    ]
    """application_components,exclude_aggregates,os_type,protection_type,"""

    patchable_fields = [
        "application_components",
        "new_igroups",
        "protection_type",
    ]
    """application_components,new_igroups,protection_type,"""

    postable_fields = [
        "application_components",
        "exclude_aggregates",
        "new_igroups",
        "os_type",
        "protection_type",
    ]
    """application_components,exclude_aggregates,new_igroups,os_type,protection_type,"""


class San(Resource):

    _schema = SanSchema
