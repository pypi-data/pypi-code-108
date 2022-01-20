# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is regenerated.
# --------------------------------------------------------------------------

from enum import Enum
from six import with_metaclass
from azure.core import CaseInsensitiveEnumMeta


class AllowedEndpointRecordType(with_metaclass(CaseInsensitiveEnumMeta, str, Enum)):
    """The allowed type DNS record types for this profile.
    """

    DOMAIN_NAME = "DomainName"
    I_PV4_ADDRESS = "IPv4Address"
    I_PV6_ADDRESS = "IPv6Address"
    ANY = "Any"

class EndpointMonitorStatus(with_metaclass(CaseInsensitiveEnumMeta, str, Enum)):
    """The monitoring status of the endpoint.
    """

    CHECKING_ENDPOINT = "CheckingEndpoint"
    ONLINE = "Online"
    DEGRADED = "Degraded"
    DISABLED = "Disabled"
    INACTIVE = "Inactive"
    STOPPED = "Stopped"

class EndpointStatus(with_metaclass(CaseInsensitiveEnumMeta, str, Enum)):
    """The status of the endpoint. If the endpoint is Enabled, it is probed for endpoint health and is
    included in the traffic routing method.
    """

    ENABLED = "Enabled"
    DISABLED = "Disabled"

class EndpointType(with_metaclass(CaseInsensitiveEnumMeta, str, Enum)):

    AZURE_ENDPOINTS = "AzureEndpoints"
    EXTERNAL_ENDPOINTS = "ExternalEndpoints"
    NESTED_ENDPOINTS = "NestedEndpoints"

class MonitorProtocol(with_metaclass(CaseInsensitiveEnumMeta, str, Enum)):
    """The protocol (HTTP, HTTPS or TCP) used to probe for endpoint health.
    """

    HTTP = "HTTP"
    HTTPS = "HTTPS"
    TCP = "TCP"

class ProfileMonitorStatus(with_metaclass(CaseInsensitiveEnumMeta, str, Enum)):
    """The profile-level monitoring status of the Traffic Manager profile.
    """

    CHECKING_ENDPOINTS = "CheckingEndpoints"
    ONLINE = "Online"
    DEGRADED = "Degraded"
    DISABLED = "Disabled"
    INACTIVE = "Inactive"

class ProfileStatus(with_metaclass(CaseInsensitiveEnumMeta, str, Enum)):
    """The status of the Traffic Manager profile.
    """

    ENABLED = "Enabled"
    DISABLED = "Disabled"

class TrafficRoutingMethod(with_metaclass(CaseInsensitiveEnumMeta, str, Enum)):
    """The traffic routing method of the Traffic Manager profile.
    """

    PERFORMANCE = "Performance"
    PRIORITY = "Priority"
    WEIGHTED = "Weighted"
    GEOGRAPHIC = "Geographic"
    MULTI_VALUE = "MultiValue"
    SUBNET = "Subnet"

class TrafficViewEnrollmentStatus(with_metaclass(CaseInsensitiveEnumMeta, str, Enum)):
    """Indicates whether Traffic View is 'Enabled' or 'Disabled' for the Traffic Manager profile.
    Null, indicates 'Disabled'. Enabling this feature will increase the cost of the Traffic Manage
    profile.
    """

    ENABLED = "Enabled"
    DISABLED = "Disabled"
