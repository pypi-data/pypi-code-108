r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["NodeControllerFlashCache", "NodeControllerFlashCacheSchema"]
__pdoc__ = {
    "NodeControllerFlashCacheSchema.resource": False,
    "NodeControllerFlashCache": False,
}


class NodeControllerFlashCacheSchema(ResourceSchema):
    """The fields of the NodeControllerFlashCache object"""

    capacity = Size(data_key="capacity")
    r""" Size in bytes

Example: 1024000000000 """

    device_id = Size(data_key="device_id")
    r""" The device_id field of the node_controller_flash_cache.

Example: 0 """

    firmware_file = fields.Str(data_key="firmware_file")
    r""" The firmware_file field of the node_controller_flash_cache.

Example: X9170_O000Z6300NVM """

    firmware_version = fields.Str(data_key="firmware_version")
    r""" The firmware_version field of the node_controller_flash_cache.

Example: NA05 """

    hardware_revision = fields.Str(data_key="hardware_revision")
    r""" The hardware_revision field of the node_controller_flash_cache.

Example: A1 """

    model = fields.Str(data_key="model")
    r""" The model field of the node_controller_flash_cache.

Example: X1970A """

    part_number = fields.Str(data_key="part_number")
    r""" The part_number field of the node_controller_flash_cache.

Example: 119-00207 """

    serial_number = fields.Str(data_key="serial_number")
    r""" The serial_number field of the node_controller_flash_cache.

Example: A22P5061550000187 """

    slot = fields.Str(data_key="slot")
    r""" The slot field of the node_controller_flash_cache.

Example: 6-1 """

    state = fields.Str(data_key="state")
    r""" The state field of the node_controller_flash_cache.

Valid choices:

* ok
* erasing
* erased
* failed
* removed """

    @property
    def resource(self):
        return NodeControllerFlashCache

    gettable_fields = [
        "capacity",
        "device_id",
        "firmware_file",
        "firmware_version",
        "hardware_revision",
        "model",
        "part_number",
        "serial_number",
        "slot",
        "state",
    ]
    """capacity,device_id,firmware_file,firmware_version,hardware_revision,model,part_number,serial_number,slot,state,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class NodeControllerFlashCache(Resource):

    _schema = NodeControllerFlashCacheSchema
