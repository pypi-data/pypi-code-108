r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["StorageSwitchErrors", "StorageSwitchErrorsSchema"]
__pdoc__ = {
    "StorageSwitchErrorsSchema.resource": False,
    "StorageSwitchErrors": False,
}


class StorageSwitchErrorsSchema(ResourceSchema):
    """The fields of the StorageSwitchErrors object"""

    component = fields.Nested("netapp_ontap.models.storage_switch_component.StorageSwitchComponentSchema", unknown=EXCLUDE, data_key="component")
    r""" The component field of the storage_switch_errors. """

    reason = fields.Nested("netapp_ontap.models.error.ErrorSchema", unknown=EXCLUDE, data_key="reason")
    r""" The reason field of the storage_switch_errors. """

    severity = fields.Str(data_key="severity")
    r""" Error component severity

Valid choices:

* unknown
* notice
* warning
* error """

    type = fields.Str(data_key="type")
    r""" Error component type

Valid choices:

* switch_unreachable
* temp_above_warning_level
* temp_above_critical_level
* temp_below_warning_level
* temp_below_critical_level
* temp_sensor_status_failed
* fan_status_non_operational
* power_supply_status_failed
* power_above_warning_level
* power_above_critical_level
* power_below_warning_level
* power_below_critical_level
* sfp_rx_power_above_warning_level
* sfp_rx_power_above_critical_level
* sfp_tx_power_above_warning_level
* sfp_tx_power_above_critical_level
* sfp_rx_power_below_warning_level
* sfp_rx_power_below_critical_level
* sfp_tx_power_below_warning_level
* sfp_tx_power_below_critical_level
* sfp_status_failed
* vsan_invalid_frame_delivery_configuration
* temp_sensor_status_unavailable
* fan_status_unavailable
* power_supply_inline_power_failed
* power_supply_status_unavailable
* unknown
* power_supply_off_env_other
* power_supply_off_admin
* power_supply_off_denied
* power_supply_off_env_power
* power_supply_off_env_temp
* power_supply_off_env_fan
* power_supply_on_but_fan_fail
* power_supply_off_cooling
* power_supply_off_connector_rating
* e_ports_down
* snmpv3_user_not_configured
* incomplete_snmp_data_refresh """

    @property
    def resource(self):
        return StorageSwitchErrors

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


class StorageSwitchErrors(Resource):

    _schema = StorageSwitchErrorsSchema
