r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["QosPolicyAdaptive", "QosPolicyAdaptiveSchema"]
__pdoc__ = {
    "QosPolicyAdaptiveSchema.resource": False,
    "QosPolicyAdaptive": False,
}


class QosPolicyAdaptiveSchema(ResourceSchema):
    """The fields of the QosPolicyAdaptive object"""

    absolute_min_iops = Size(data_key="absolute_min_iops")
    r""" Specifies the absolute minimum IOPS that is used as an override when the expected_iops is less than this value. These floors are not guaranteed on non-AFF platforms or when FabricPool tiering policies are set. """

    block_size = fields.Str(data_key="block_size")
    r""" Specifies the block size

Valid choices:

* any
* 4k
* 8k
* 16k
* 32k
* 64k
* 128k """

    expected_iops = Size(data_key="expected_iops")
    r""" Expected IOPS. Specifies the minimum expected IOPS per TB allocated based on the storage object allocated size. These floors are not guaranteed on non-AFF platforms or when FabricPool tiering policies are set. """

    expected_iops_allocation = fields.Str(data_key="expected_iops_allocation")
    r""" Specifies the size to be used to calculate expected IOPS per TB. The size options are either the storage object allocated space or the storage object used space.

Valid choices:

* used_space
* allocated_space """

    peak_iops = Size(data_key="peak_iops")
    r""" Peak IOPS. Specifies the maximum possible IOPS per TB allocated based on the storage object allocated size or the storage object used size. """

    peak_iops_allocation = fields.Str(data_key="peak_iops_allocation")
    r""" Specifies the size to be used to calculate peak IOPS per TB. The size options are either the storage object allocated space or the storage object used space.

Valid choices:

* used_space
* allocated_space """

    @property
    def resource(self):
        return QosPolicyAdaptive

    gettable_fields = [
        "absolute_min_iops",
        "block_size",
        "expected_iops",
        "expected_iops_allocation",
        "peak_iops",
        "peak_iops_allocation",
    ]
    """absolute_min_iops,block_size,expected_iops,expected_iops_allocation,peak_iops,peak_iops_allocation,"""

    patchable_fields = [
        "absolute_min_iops",
        "block_size",
        "expected_iops",
        "expected_iops_allocation",
        "peak_iops",
        "peak_iops_allocation",
    ]
    """absolute_min_iops,block_size,expected_iops,expected_iops_allocation,peak_iops,peak_iops_allocation,"""

    postable_fields = [
        "absolute_min_iops",
        "block_size",
        "expected_iops",
        "expected_iops_allocation",
        "peak_iops",
        "peak_iops_allocation",
    ]
    """absolute_min_iops,block_size,expected_iops,expected_iops_allocation,peak_iops,peak_iops_allocation,"""


class QosPolicyAdaptive(Resource):

    _schema = QosPolicyAdaptiveSchema
