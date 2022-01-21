r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ServiceProcessor", "ServiceProcessorSchema"]
__pdoc__ = {
    "ServiceProcessorSchema.resource": False,
    "ServiceProcessor": False,
}


class ServiceProcessorSchema(ResourceSchema):
    """The fields of the ServiceProcessor object"""

    autoupdate_enabled = fields.Boolean(data_key="autoupdate_enabled")
    r""" Indicates whether the service processor can be automatically updated from ONTAP. """

    backup = fields.Nested("netapp_ontap.models.service_processor_backup.ServiceProcessorBackupSchema", unknown=EXCLUDE, data_key="backup")
    r""" The backup field of the service_processor. """

    dhcp_enabled = fields.Boolean(data_key="dhcp_enabled")
    r""" Set to "true" to use DHCP to configure an IPv4 interface. Do not provide values for address, netmask and gateway when set to "true". """

    firmware_version = fields.Str(data_key="firmware_version")
    r""" The version of firmware installed. """

    ipv4_interface = fields.Nested("netapp_ontap.models.ip_interface_and_gateway.IpInterfaceAndGatewaySchema", unknown=EXCLUDE, data_key="ipv4_interface")
    r""" The ipv4_interface field of the service_processor. """

    ipv6_interface = fields.Nested("netapp_ontap.models.ipv6_interface_and_gateway.Ipv6InterfaceAndGatewaySchema", unknown=EXCLUDE, data_key="ipv6_interface")
    r""" The ipv6_interface field of the service_processor. """

    is_ip_configured = fields.Boolean(data_key="is_ip_configured")
    r""" Indicates whether the service processor network is configured. """

    last_update_state = fields.Str(data_key="last_update_state")
    r""" Provides the "update status" of the last service processor update.

Valid choices:

* failed
* passed """

    link_status = fields.Str(data_key="link_status")
    r""" The link_status field of the service_processor.

Valid choices:

* up
* down
* disabled
* unknown """

    mac_address = fields.Str(data_key="mac_address")
    r""" The mac_address field of the service_processor. """

    primary = fields.Nested("netapp_ontap.models.service_processor_primary.ServiceProcessorPrimarySchema", unknown=EXCLUDE, data_key="primary")
    r""" The primary field of the service_processor. """

    ssh_info = fields.Nested("netapp_ontap.models.service_processor_ssh_info.ServiceProcessorSshInfoSchema", unknown=EXCLUDE, data_key="ssh_info")
    r""" The ssh_info field of the service_processor. """

    state = fields.Str(data_key="state")
    r""" The state field of the service_processor.

Valid choices:

* online
* offline
* degraded
* rebooting
* unknown
* updating
* node_offline
* sp_daemon_offline """

    type = fields.Str(data_key="type")
    r""" The type field of the service_processor.

Valid choices:

* sp
* none
* bmc """

    @property
    def resource(self):
        return ServiceProcessor

    gettable_fields = [
        "autoupdate_enabled",
        "backup",
        "dhcp_enabled",
        "firmware_version",
        "ipv4_interface",
        "ipv6_interface",
        "is_ip_configured",
        "last_update_state",
        "link_status",
        "mac_address",
        "primary",
        "ssh_info",
        "state",
        "type",
    ]
    """autoupdate_enabled,backup,dhcp_enabled,firmware_version,ipv4_interface,ipv6_interface,is_ip_configured,last_update_state,link_status,mac_address,primary,ssh_info,state,type,"""

    patchable_fields = [
        "autoupdate_enabled",
        "backup",
        "dhcp_enabled",
        "ipv4_interface",
        "ipv6_interface",
        "primary",
        "ssh_info",
    ]
    """autoupdate_enabled,backup,dhcp_enabled,ipv4_interface,ipv6_interface,primary,ssh_info,"""

    postable_fields = [
        "backup",
        "ipv4_interface",
        "primary",
        "ssh_info",
    ]
    """backup,ipv4_interface,primary,ssh_info,"""


class ServiceProcessor(Resource):

    _schema = ServiceProcessorSchema
