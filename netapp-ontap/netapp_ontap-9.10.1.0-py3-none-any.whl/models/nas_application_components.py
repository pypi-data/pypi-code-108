r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["NasApplicationComponents", "NasApplicationComponentsSchema"]
__pdoc__ = {
    "NasApplicationComponentsSchema.resource": False,
    "NasApplicationComponents": False,
}


class NasApplicationComponentsSchema(ResourceSchema):
    """The fields of the NasApplicationComponents object"""

    export_policy = fields.Nested("netapp_ontap.models.nas_export_policy.NasExportPolicySchema", unknown=EXCLUDE, data_key="export_policy")
    r""" The export_policy field of the nas_application_components. """

    flexcache = fields.Nested("netapp_ontap.models.nas_flexcache.NasFlexcacheSchema", unknown=EXCLUDE, data_key="flexcache")
    r""" The flexcache field of the nas_application_components. """

    name = fields.Str(data_key="name")
    r""" The name of the application component. """

    qos = fields.Nested("netapp_ontap.models.nas_qos.NasQosSchema", unknown=EXCLUDE, data_key="qos")
    r""" The qos field of the nas_application_components. """

    scale_out = fields.Boolean(data_key="scale_out")
    r""" Denotes a Flexgroup. """

    share_count = Size(data_key="share_count")
    r""" The number of shares in the application component. """

    storage_service = fields.Nested("netapp_ontap.models.nas_storage_service.NasStorageServiceSchema", unknown=EXCLUDE, data_key="storage_service")
    r""" The storage_service field of the nas_application_components. """

    tiering = fields.Nested("netapp_ontap.models.nas_application_components_tiering.NasApplicationComponentsTieringSchema", unknown=EXCLUDE, data_key="tiering")
    r""" The tiering field of the nas_application_components. """

    total_size = Size(data_key="total_size")
    r""" The total size of the application component, split across the member shares. Usage: {&lt;integer&gt;[KB|MB|GB|TB|PB]} """

    @property
    def resource(self):
        return NasApplicationComponents

    gettable_fields = [
        "export_policy",
        "flexcache",
        "name",
        "qos",
        "scale_out",
        "share_count",
        "storage_service",
        "tiering",
        "total_size",
    ]
    """export_policy,flexcache,name,qos,scale_out,share_count,storage_service,tiering,total_size,"""

    patchable_fields = [
        "name",
        "storage_service",
        "tiering",
        "total_size",
    ]
    """name,storage_service,tiering,total_size,"""

    postable_fields = [
        "export_policy",
        "flexcache",
        "name",
        "qos",
        "scale_out",
        "share_count",
        "storage_service",
        "tiering",
        "total_size",
    ]
    """export_policy,flexcache,name,qos,scale_out,share_count,storage_service,tiering,total_size,"""


class NasApplicationComponents(Resource):

    _schema = NasApplicationComponentsSchema
