r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["StorageBridgeErrors", "StorageBridgeErrorsSchema"]
__pdoc__ = {
    "StorageBridgeErrorsSchema.resource": False,
    "StorageBridgeErrors": False,
}


class StorageBridgeErrorsSchema(ResourceSchema):
    """The fields of the StorageBridgeErrors object"""

    component = fields.Nested("netapp_ontap.models.storage_bridge_component.StorageBridgeComponentSchema", unknown=EXCLUDE, data_key="component")
    r""" The component field of the storage_bridge_errors. """

    reason = fields.Nested("netapp_ontap.models.error.ErrorSchema", unknown=EXCLUDE, data_key="reason")
    r""" The reason field of the storage_bridge_errors. """

    severity = fields.Str(data_key="severity")
    r""" Bridge error severity

Valid choices:

* unknown
* notice
* warning
* error """

    type = fields.Str(data_key="type")
    r""" Bridge error type

Valid choices:

* unknown
* bridge_unreachable
* temp_above_critical_level
* temp_below_critical_level
* temp_sensor_status_critical
* temp_sensor_status_unavailable
* invalid_configuration
* sas_port_offline
* link_failure
* sas_port_online
* power_supply_offline """

    @property
    def resource(self):
        return StorageBridgeErrors

    gettable_fields = [
        "component",
        "reason",
        "severity",
        "type",
    ]
    """component,reason,severity,type,"""

    patchable_fields = [
        "component",
        "severity",
        "type",
    ]
    """component,severity,type,"""

    postable_fields = [
        "component",
        "severity",
        "type",
    ]
    """component,severity,type,"""


class StorageBridgeErrors(Resource):

    _schema = StorageBridgeErrorsSchema
