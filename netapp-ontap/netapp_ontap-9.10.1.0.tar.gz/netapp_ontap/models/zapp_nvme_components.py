r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ZappNvmeComponents", "ZappNvmeComponentsSchema"]
__pdoc__ = {
    "ZappNvmeComponentsSchema.resource": False,
    "ZappNvmeComponents": False,
}


class ZappNvmeComponentsSchema(ResourceSchema):
    """The fields of the ZappNvmeComponents object"""

    name = fields.Str(data_key="name")
    r""" The name of the application component. """

    namespace_count = Size(data_key="namespace_count")
    r""" The number of namespaces in the component. """

    os_type = fields.Str(data_key="os_type")
    r""" The name of the host OS running the application.

Valid choices:

* aix
* linux
* vmware
* windows """

    performance = fields.Nested("netapp_ontap.models.zapp_nvme_performance.ZappNvmePerformanceSchema", unknown=EXCLUDE, data_key="performance")
    r""" The performance field of the zapp_nvme_components. """

    qos = fields.Nested("netapp_ontap.models.nas_qos.NasQosSchema", unknown=EXCLUDE, data_key="qos")
    r""" The qos field of the zapp_nvme_components. """

    subsystem = fields.Nested("netapp_ontap.models.zapp_nvme_components_subsystem.ZappNvmeComponentsSubsystemSchema", unknown=EXCLUDE, data_key="subsystem")
    r""" The subsystem field of the zapp_nvme_components. """

    tiering = fields.Nested("netapp_ontap.models.zapp_nvme_components_tiering.ZappNvmeComponentsTieringSchema", unknown=EXCLUDE, data_key="tiering")
    r""" The tiering field of the zapp_nvme_components. """

    total_size = Size(data_key="total_size")
    r""" The total size of the component, spread across member namespaces. Usage: {&lt;integer&gt;[KB|MB|GB|TB|PB]} """

    @property
    def resource(self):
        return ZappNvmeComponents

    gettable_fields = [
        "name",
        "namespace_count",
        "os_type",
        "performance",
        "qos",
        "subsystem",
        "tiering",
        "total_size",
    ]
    """name,namespace_count,os_type,performance,qos,subsystem,tiering,total_size,"""

    patchable_fields = [
        "name",
        "namespace_count",
        "os_type",
        "performance",
        "subsystem",
        "tiering",
        "total_size",
    ]
    """name,namespace_count,os_type,performance,subsystem,tiering,total_size,"""

    postable_fields = [
        "name",
        "namespace_count",
        "os_type",
        "performance",
        "qos",
        "subsystem",
        "tiering",
        "total_size",
    ]
    """name,namespace_count,os_type,performance,qos,subsystem,tiering,total_size,"""


class ZappNvmeComponents(Resource):

    _schema = ZappNvmeComponentsSchema
