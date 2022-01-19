# Copyright 2016 OpenStack Foundation
# All Rights Reserved
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import copy
from distutils import version

from oslo_log import log

from vmware_nsxlib import v3
from vmware_nsxlib.v3 import client
from vmware_nsxlib.v3 import exceptions
from vmware_nsxlib.v3 import lib
from vmware_nsxlib.v3 import nsx_constants
from vmware_nsxlib.v3 import utils as lib_utils

from vmware_nsxlib.v3.policy import core_defs
from vmware_nsxlib.v3.policy import core_resources
from vmware_nsxlib.v3.policy import ipsec_vpn_resources
from vmware_nsxlib.v3.policy import lb_resources

LOG = log.getLogger(__name__)


class NsxPolicyLib(lib.NsxLibBase):

    def init_api(self):
        # Initialize the policy client
        self.policy_api = core_defs.NsxPolicyApi(self.client)

        # NSX manager api will be used as a pass-through for apis which are
        # not implemented by the policy manager yet
        if self.nsxlib_config.allow_passthrough:
            config = copy.deepcopy(self.nsxlib_config)
            # X-Allow-Overwrite must be set for passthrough apis
            config.allow_overwrite_header = True
            # Manually copy providers (No deep copy, as those are instances)
            # FIXME(asarfaty): This can be handled nicer by adding
            # __deepcopy__ methods to the provider classes to do the deepcopy
            # correctly
            config.token_provider = self.nsxlib_config.token_provider
            config.client_cert_provider = (
                self.nsxlib_config.client_cert_provider)
            self.nsx_api = v3.NsxLib(config)
        else:
            self.nsx_api = None

        self.nsx_version = self.get_version()

        if not self.feature_supported(nsx_constants.FEATURE_PARTIAL_UPDATES):
            self.policy_api.disable_partial_updates()

        args = (self.policy_api, self.nsx_api, self.nsx_version,
                self.nsxlib_config)

        # Initialize all the different resources
        self.domain = core_resources.NsxPolicyDomainApi(*args)
        self.group = core_resources.NsxPolicyGroupApi(*args)
        self.service = core_resources.NsxPolicyL4ServiceApi(*args)
        self.icmp_service = core_resources.NsxPolicyIcmpServiceApi(
            *args)
        self.ip_protocol_service = (
            core_resources.NsxPolicyIPProtocolServiceApi(*args))
        self.mixed_service = core_resources.NsxPolicyMixedServiceApi(*args)
        self.tier0 = core_resources.NsxPolicyTier0Api(*args)
        self.tier0_nat_rule = core_resources.NsxPolicyTier0NatRuleApi(
            *args)
        self.tier0_route_map = core_resources.NsxPolicyTier0RouteMapApi(*args)
        self.tier0_prefix_list = core_resources.NsxPolicyTier0PrefixListApi(
            *args)
        self.tier0_bgp = core_resources.NsxPolicyTier0BgpApi(*args)
        self.tier0_static_route = (
            core_resources.NSXPolicyTier0StaticRouteApi(*args))
        self.tier1 = core_resources.NsxPolicyTier1Api(*args)
        self.tier1_segment = core_resources.NsxPolicyTier1SegmentApi(*args)
        self.tier1_nat_rule = core_resources.NsxPolicyTier1NatRuleApi(
            *args)
        self.tier1_static_route = (
            core_resources.NsxPolicyTier1StaticRouteApi(*args))
        self.segment = core_resources.NsxPolicySegmentApi(*args)
        self.segment_port = core_resources.NsxPolicySegmentPortApi(
            *args)
        self.tier1_segment_port = (
            core_resources.NsxPolicyTier1SegmentPortApi(*args))
        self.comm_map = core_resources.NsxPolicyCommunicationMapApi(*args)
        self.gateway_policy = core_resources.NsxPolicyGatewayPolicyApi(*args)
        self.enforcement_point = core_resources.NsxPolicyEnforcementPointApi(
            *args)
        self.transport_zone = core_resources.NsxPolicyTransportZoneApi(
            *args)
        self.edge_cluster = core_resources.NsxPolicyEdgeClusterApi(
            *args)
        self.deployment_map = core_resources.NsxPolicyDeploymentMapApi(
            *args)
        self.ip_block = core_resources.NsxPolicyIpBlockApi(*args)
        self.ip_pool = core_resources.NsxPolicyIpPoolApi(*args)
        self.segment_security_profile = (
            core_resources.NsxSegmentSecurityProfileApi(*args))
        self.qos_profile = (
            core_resources.NsxQosProfileApi(*args))
        self.spoofguard_profile = (
            core_resources.NsxSpoofguardProfileApi(*args))
        self.ip_discovery_profile = (
            core_resources.NsxIpDiscoveryProfileApi(*args))
        self.mac_discovery_profile = (
            core_resources.NsxMacDiscoveryProfileApi(*args))
        self.waf_profile = (
            core_resources.NsxWAFProfileApi(*args))
        self.segment_security_profile_maps = (
            core_resources.SegmentSecurityProfilesBindingMapApi(
                *args))
        self.segment_qos_profile_maps = (
            core_resources.SegmentQosProfilesBindingMapApi(
                *args))
        self.segment_discovery_profile_maps = (
            core_resources.SegmentDiscoveryProfilesBindingMapApi(
                *args))
        self.segment_port_security_profiles = (
            core_resources.SegmentPortSecurityProfilesBindingMapApi(
                *args))
        self.segment_port_discovery_profiles = (
            core_resources.SegmentPortDiscoveryProfilesBindingMapApi(
                *args))
        self.segment_port_qos_profiles = (
            core_resources.SegmentPortQosProfilesBindingMapApi(
                *args))
        self.segment_dhcp_static_bindings = (
            core_resources.SegmentDhcpStaticBindingConfigApi(*args))
        self.ipv6_ndra_profile = (
            core_resources.NsxIpv6NdraProfileApi(*args))
        self.dhcp_relay_config = core_resources.NsxDhcpRelayConfigApi(*args)
        self.dhcp_server_config = core_resources.NsxDhcpServerConfigApi(*args)
        self.md_proxy = core_resources.NsxPolicyMetadataProxyApi(*args)
        self.certificate = core_resources.NsxPolicyCertApi(*args)
        self.exclude_list = core_resources.NsxPolicyExcludeListApi(*args)
        self.load_balancer = lb_resources.NsxPolicyLoadBalancerApi(*args)
        self.ipsec_vpn = ipsec_vpn_resources.NsxPolicyIpsecVpnApi(*args)
        self.global_config = core_resources.NsxPolicyGlobalConfig(*args)
        self.object_permission = (
            core_resources.NsxPolicyObjectRolePermissionGroupApi(*args))

    def get_nsxlib_passthrough(self):
        return self.nsx_api

    def get_version(self):
        """Get the NSX Policy manager version

        Currently the backend does not support it, so the nsx-manager api
        will be used temporarily as a passthrough.
        """
        if self.nsx_version:
            return self.nsx_version

        if self.nsx_api:
            self.nsx_version = self.nsx_api.get_version()
        else:
            # return the initial supported version
            self.nsx_version = nsx_constants.NSX_VERSION_2_4_0
        return self.nsx_version

    def feature_supported(self, feature):
        if (version.LooseVersion(self.get_version()) >=
            version.LooseVersion(nsx_constants.NSX_VERSION_2_4_0)):
            # Features available since 2.4
            if (feature == nsx_constants.FEATURE_NSX_POLICY_NETWORKING):
                return True
            if (feature == nsx_constants.FEATURE_NSX_POLICY_ORBAC):
                return True

        if (version.LooseVersion(self.get_version()) >=
            version.LooseVersion(nsx_constants.NSX_VERSION_2_5_0)):
            # Features available since 2.5
            if (feature == nsx_constants.FEATURE_ENS_WITH_QOS):
                return True

        if (version.LooseVersion(self.get_version()) >=
            version.LooseVersion(nsx_constants.NSX_VERSION_3_0_0)):
            # features available since 3.0.0
            if feature == nsx_constants.FEATURE_PARTIAL_UPDATES:
                return True
            if feature == nsx_constants.FEATURE_SWITCH_HYPERBUS_MODE:
                return True
            if feature == nsx_constants.FEATURE_NSX_POLICY_MDPROXY:
                return True
            if feature == nsx_constants.FEATURE_NSX_POLICY_DHCP:
                return True
            if (feature == nsx_constants.FEATURE_RELAX_SCALE_VALIDATION):
                return True
            if (feature == nsx_constants.FEATURE_NSX_POLICY_GLOBAL_CONFIG):
                return True
            if feature == nsx_constants.FEATURE_ROUTE_REDISTRIBUTION_CONFIG:
                return True
            if feature == nsx_constants.FEATURE_NSX_POLICY_ADMIN_STATE:
                return True

        if (version.LooseVersion(self.get_version()) >=
            version.LooseVersion(nsx_constants.NSX_VERSION_3_1_0)):
            # features available since 3.1.0
            if feature == nsx_constants.FEATURE_SPOOFGUARD_CIDR:
                return True

        return (feature == nsx_constants.FEATURE_NSX_POLICY)

    def reinitialize_cluster(self, resource, event, trigger, payload=None):
        super(NsxPolicyLib, self).reinitialize_cluster(
            resource, event, trigger, payload=payload)
        if self.nsx_api:
            self.nsx_api.reinitialize_cluster(resource, event, trigger,
                                              payload)

    @property
    def client_url_prefix(self):
        return client.NSX3Client.NSX_POLICY_V1_API_PREFIX

    def set_realization_interval(self, interval_min):
        # Sets intent realization and purge cycles interval (in minutes)
        realization_config = {"key": "populate_realized_state_cron_expression",
                              "value": "0 */%d * * * *" % interval_min}
        body = {"keyValuePairs": [realization_config]}
        self.client.patch("system-config", body)

    def search_resource_by_realized_id(self, realized_id, realized_type):
        """Search resources by a realized id & type

        :returns: a list of resource pathes matching the realized id and type.
        """
        if not realized_type or not realized_id:
            raise exceptions.NsxSearchInvalidQuery(
                reason=_("Resource type or id was not specified"))
        query = ('resource_type:GenericPolicyRealizedResource AND '
                 'realization_specific_identifier:%s AND '
                 'entity_type:%s' % (realized_id, realized_type))
        url = self._get_search_url() % query

        # Retry the search on case of error
        @lib_utils.retry_upon_exception(exceptions.NsxSearchError,
                                        max_attempts=self.client.max_attempts)
        def do_search(url):
            return self.client.url_get(url)

        results = do_search(url)
        pathes = []
        for resource in results['results']:
            pathes.extend(resource.get('intent_paths', []))
        return pathes
