r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["SanApplicationComponents", "SanApplicationComponentsSchema"]
__pdoc__ = {
    "SanApplicationComponentsSchema.resource": False,
    "SanApplicationComponents": False,
}


class SanApplicationComponentsSchema(ResourceSchema):
    """The fields of the SanApplicationComponents object"""

    igroup_name = fields.Str(data_key="igroup_name")
    r""" The name of the initiator group through which the contents of this application will be accessed. Modification of this parameter is a disruptive operation. All LUNs in the application component will be unmapped from the current igroup and re-mapped to the new igroup. """

    lun_count = Size(data_key="lun_count")
    r""" The number of LUNs in the application component. """

    name = fields.Str(data_key="name")
    r""" The name of the application component. """

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

    qos = fields.Nested("netapp_ontap.models.nas_qos.NasQosSchema", unknown=EXCLUDE, data_key="qos")
    r""" The qos field of the san_application_components. """

    storage_service = fields.Nested("netapp_ontap.models.nas_storage_service.NasStorageServiceSchema", unknown=EXCLUDE, data_key="storage_service")
    r""" The storage_service field of the san_application_components. """

    tiering = fields.Nested("netapp_ontap.models.san_application_components_tiering.SanApplicationComponentsTieringSchema", unknown=EXCLUDE, data_key="tiering")
    r""" The tiering field of the san_application_components. """

    total_size = Size(data_key="total_size")
    r""" The total size of the application component, split across the member LUNs. Usage: {&lt;integer&gt;[KB|MB|GB|TB|PB]} """

    @property
    def resource(self):
        return SanApplicationComponents

    gettable_fields = [
        "igroup_name",
        "lun_count",
        "name",
        "os_type",
        "qos",
        "storage_service",
        "tiering",
        "total_size",
    ]
    """igroup_name,lun_count,name,os_type,qos,storage_service,tiering,total_size,"""

    patchable_fields = [
        "igroup_name",
        "lun_count",
        "name",
        "os_type",
        "storage_service",
        "tiering",
        "total_size",
    ]
    """igroup_name,lun_count,name,os_type,storage_service,tiering,total_size,"""

    postable_fields = [
        "igroup_name",
        "lun_count",
        "name",
        "os_type",
        "qos",
        "storage_service",
        "tiering",
        "total_size",
    ]
    """igroup_name,lun_count,name,os_type,qos,storage_service,tiering,total_size,"""


class SanApplicationComponents(Resource):

    _schema = SanApplicationComponentsSchema
