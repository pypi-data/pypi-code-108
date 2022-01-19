# Copyright 2018 VMware, Inc.
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
#

import copy
from unittest import mock

from oslo_utils import uuidutils

from vmware_nsxlib.tests.unit.v3 import nsxlib_testcase
from vmware_nsxlib.tests.unit.v3 import test_constants
from vmware_nsxlib.v3 import exceptions as nsxlib_exc
from vmware_nsxlib.v3 import nsx_constants
from vmware_nsxlib.v3 import router as nsx_router


class TestRouter(nsxlib_testcase.NsxClientTestCase):

    def test_validate_tier0(self):
        tier0_groups_dict = {}
        tier0_uuid = uuidutils.generate_uuid()
        rtr = {'edge_cluster_id': test_constants.FAKE_EDGE_CLUSTER_ID}
        with mock.patch.object(self.nsxlib.router._router_client, 'get',
                               return_value=rtr),\
            mock.patch.object(
                self.nsxlib.edge_cluster, 'get',
                return_value=test_constants.FAKE_EDGE_CLUSTER):
            self.nsxlib.router.validate_tier0(tier0_groups_dict, tier0_uuid)
            self.assertEqual(
                tier0_groups_dict[tier0_uuid]['edge_cluster_uuid'],
                test_constants.FAKE_EDGE_CLUSTER_ID)
            self.assertEqual(
                tier0_groups_dict[tier0_uuid]['member_index_list'], [0])

    def test_validate_tier0_fail_no_cluster(self):
        tier0_groups_dict = {}
        tier0_uuid = uuidutils.generate_uuid()
        rtr = {'edge_cluster_id': None}
        with mock.patch.object(self.nsxlib.router._router_client, 'get',
                               return_value=rtr):
            self.assertRaises(
                nsxlib_exc.NsxLibInvalidInput,
                self.nsxlib.router.validate_tier0,
                tier0_groups_dict, tier0_uuid)

    def test_validate_tier0_fail_no_members(self):
        tier0_groups_dict = {}
        tier0_uuid = uuidutils.generate_uuid()
        edge_cluster = copy.copy(test_constants.FAKE_EDGE_CLUSTER)
        edge_cluster['members'] = []
        with mock.patch.object(self.nsxlib.router._router_client, 'get'),\
            mock.patch.object(self.nsxlib.edge_cluster, 'get',
                              return_value=edge_cluster):
            self.assertRaises(
                nsxlib_exc.NsxLibInvalidInput,
                self.nsxlib.router.validate_tier0,
                tier0_groups_dict, tier0_uuid)

    def test_add_router_link_port(self):
        tags = [{'scope': 'a', 'tag': 'b'}]
        tier0_uuid = uuidutils.generate_uuid()
        tier1_uuid = uuidutils.generate_uuid()
        with mock.patch.object(self.nsxlib.router._router_port_client,
                               'create') as port_create:
            tier0_link_port = mock.MagicMock()
            tier1_link_port = mock.MagicMock()
            port_create.side_effect = [tier0_link_port, tier1_link_port]
            self.assertEqual(
                (tier0_link_port, tier1_link_port),
                self.nsxlib.router.add_router_link_port(
                    tier1_uuid, tier0_uuid, tags))
            self.assertEqual(port_create.call_count, 2)

    def test_add_router_link_port_fail(self):
        tags = [{'scope': 'a', 'tag': 'b'}]
        tier0_uuid = uuidutils.generate_uuid()
        tier1_uuid = uuidutils.generate_uuid()
        tier0_link_port_id = uuidutils.generate_uuid()
        with mock.patch.object(self.nsxlib.router._router_port_client,
                               'create') as port_create,\
            mock.patch.object(self.nsxlib.router._router_port_client,
                              'delete') as port_delete:
            tier0_link_port = {'id': tier0_link_port_id}
            port_create.side_effect = [tier0_link_port,
                                       nsxlib_exc.ManagerError]
            self.assertRaises(
                nsxlib_exc.ManagerError,
                self.nsxlib.router.add_router_link_port,
                tier1_uuid, tier0_uuid, tags)
            port_delete.assert_called_once_with(tier0_link_port_id)

    def test_remove_router_link_port(self):
        tier1_uuid = uuidutils.generate_uuid()
        with mock.patch.object(
            self.nsxlib.router._router_port_client, 'get_tier1_link_port',
            return_value=test_constants.FAKE_ROUTER_LINKT1_PORT) as port_get,\
            mock.patch.object(self.nsxlib.router._router_port_client,
                              'delete') as port_delete:
            self.nsxlib.router.remove_router_link_port(tier1_uuid)
            self.assertEqual(port_get.call_count, 1)
            self.assertEqual(port_delete.call_count, 2)

    def test_add_centralized_service_port(self):
        logical_router_id = uuidutils.generate_uuid()
        logical_port_id = uuidutils.generate_uuid()
        display_name = mock.Mock()
        tags = mock.Mock()
        address_groups = mock.Mock()
        port = mock.Mock()
        with mock.patch.object(
                self.nsxlib.router._router_port_client, 'create',
                return_value=port) as create_port:
            csp = self.nsxlib.router.add_centralized_service_port(
                logical_router_id, display_name=display_name, tags=tags,
                logical_port_id=logical_port_id, address_groups=address_groups)
            create_port.assert_called_once_with(
                logical_router_id, display_name=display_name, tags=tags,
                logical_port_id=logical_port_id, address_groups=address_groups,
                resource_type=nsx_constants.LROUTERPORT_CENTRALIZED)
            self.assertEqual(csp, port)

    def test_update_advertisement(self):
        router_id = test_constants.FAKE_ROUTER_UUID
        nat = True
        con = False
        static = True
        enabled = True
        vip = False
        snat = True
        data = {'advertise_route_nat': nat,
                'advertise_route_connected': con,
                'advertise_route_static': static,
                'enabled': enabled,
                'advertise_lb_vip': vip,
                'advertise_lb_snat_ip': snat}
        api_client = self.nsxlib.router.nsxlib.logical_router.client
        with mock.patch.object(api_client, 'get', return_value={}),\
            mock.patch.object(api_client, 'update') as client_update,\
            mock.patch("vmware_nsxlib.v3.NsxLib.get_version",
                       return_value=nsxlib_testcase.LATEST_VERSION):
            self.nsxlib.router.update_advertisement(router_id, **data)
            client_update.assert_called_with(
                'logical-routers/%s/routing/advertisement' % router_id,
                {'advertise_nat_routes': nat,
                 'advertise_nsx_connected_routes': con,
                 'advertise_static_routes': static,
                 'enabled': enabled,
                 'advertise_lb_vip': vip,
                 'advertise_lb_snat_ip': snat},
                headers=None)

    def test_update_advertisement_lb_unsupported(self):
        router_id = test_constants.FAKE_ROUTER_UUID
        nat = True
        con = False
        static = True
        enabled = True
        vip = False
        snat = True
        data = {'advertise_route_nat': nat,
                'advertise_route_connected': con,
                'advertise_route_static': static,
                'enabled': enabled,
                'advertise_lb_vip': vip,
                'advertise_lb_snat_ip': snat}
        api_client = self.nsxlib.router.nsxlib.logical_router.client
        with mock.patch.object(api_client, 'get', return_value={}),\
            mock.patch.object(api_client, 'update') as client_update,\
            mock.patch("vmware_nsxlib.v3.NsxLib.get_version",
                       return_value='2.0.0'):
            self.nsxlib.router.update_advertisement(router_id, **data)
            client_update.assert_called_with(
                'logical-routers/%s/routing/advertisement' % router_id,
                {'advertise_nat_routes': nat,
                 'advertise_nsx_connected_routes': con,
                 'advertise_static_routes': static,
                 'enabled': enabled},
                headers=None)

    def test_delete_gw_snat_rule(self):
        logical_router_id = test_constants.FAKE_ROUTER_UUID
        gw_ip = '1.1.1.1'
        with mock.patch.object(self.nsxlib.router.nsxlib.logical_router,
                               'delete_nat_rule_by_values') as del_api:
            self.nsxlib.router.delete_gw_snat_rule(logical_router_id, gw_ip)
            del_api.assert_called_with(
                logical_router_id,
                translated_network=gw_ip)

    def test_delete_gw_snat_rule_by_source(self):
        logical_router_id = test_constants.FAKE_ROUTER_UUID
        gw_ip = '1.1.1.1'
        source_net = '2.0.0.0/24'
        with mock.patch.object(self.nsxlib.router.nsxlib.logical_router,
                               'delete_nat_rule_by_values') as del_api:
            self.nsxlib.router.delete_gw_snat_rule_by_source(
                logical_router_id, gw_ip, source_net)
            del_api.assert_called_with(
                logical_router_id,
                translated_network=gw_ip,
                match_source_network=source_net,
                skip_not_found=False, strict_mode=True)

    def test_delete_gw_snat_rules(self):
        logical_router_id = test_constants.FAKE_ROUTER_UUID
        gw_ip = '1.1.1.1'
        with mock.patch.object(self.nsxlib.router.nsxlib.logical_router,
                               'delete_nat_rule_by_values') as del_api:
            self.nsxlib.router.delete_gw_snat_rules(
                logical_router_id, gw_ip)
            del_api.assert_called_with(
                logical_router_id,
                translated_network=gw_ip,
                skip_not_found=True, strict_mode=False)

    def test_add_gw_snat_rule(self):
        logical_router_id = test_constants.FAKE_ROUTER_UUID
        gw_ip = '1.1.1.1'
        with mock.patch.object(self.nsxlib.router.nsxlib.logical_router,
                               'add_nat_rule') as add_api:
            self.nsxlib.router.add_gw_snat_rule(
                logical_router_id, gw_ip)
            add_api.assert_called_with(
                logical_router_id,
                translated_network=gw_ip,
                action="SNAT",
                bypass_firewall=True,
                source_net=None,
                rule_priority=nsx_router.GW_NAT_PRI,
                tags=None,
                display_name=None)

    def test_update_router_edge_cluster(self):
        logical_router_id = test_constants.FAKE_ROUTER_UUID
        ec_id = test_constants.FAKE_EDGE_CLUSTER
        with mock.patch.object(self.nsxlib.router.nsxlib.logical_router,
                               'update') as update_api:
            self.nsxlib.router.update_router_edge_cluster(
                logical_router_id, ec_id)
            update_api.assert_called_with(
                logical_router_id,
                edge_cluster_id=ec_id)

    def test_update_router_transport_zone(self):
        logical_router_id = test_constants.FAKE_ROUTER_UUID
        tz_id = test_constants.FAKE_TZ_UUID
        with mock.patch.object(self.nsxlib.router.nsxlib.logical_router,
                               'update') as update_api:
            self.nsxlib.router.update_router_transport_zone(
                logical_router_id, tz_id)
            update_api.assert_called_with(
                logical_router_id,
                transport_zone_id=tz_id)

    def test_create_logical_router_intf_port_by_ls_id(self):
        logical_router_id = uuidutils.generate_uuid()
        display_name = 'dummy'
        tags = []
        ls_id = uuidutils.generate_uuid()
        logical_switch_port_id = uuidutils.generate_uuid()
        address_groups = []
        with mock.patch.object(
            self.nsxlib.router._router_port_client,
            "get_by_lswitch_id",
            side_effect=nsxlib_exc.ResourceNotFound()) as get_port,\
            mock.patch.object(self.nsxlib.router._router_port_client,
                              "create") as create_port:
            self.nsxlib.router.create_logical_router_intf_port_by_ls_id(
                logical_router_id,
                display_name,
                tags,
                ls_id,
                logical_switch_port_id,
                address_groups)
            get_port.assert_called_once_with(ls_id)
            create_port.assert_called_once_with(
                logical_router_id, display_name, tags,
                nsx_constants.LROUTERPORT_DOWNLINK,
                logical_switch_port_id, address_groups, urpf_mode=None,
                relay_service_uuid=None)

    def test_add_fip_nat_rules(self):
        with mock.patch.object(self.nsxlib.logical_router,
                               "add_nat_rule") as add_rule:
            self.nsxlib.router.add_fip_nat_rules(
                test_constants.FAKE_ROUTER_UUID,
                '1.1.1.1', '2.2.2.2')
            self.assertEqual(add_rule.call_count, 2)

    def test_delete_fip_nat_rules(self):
        with mock.patch.object(self.nsxlib.logical_router,
                               "delete_nat_rule_by_values") as del_rule:
            self.nsxlib.router.delete_fip_nat_rules(
                test_constants.FAKE_ROUTER_UUID,
                '1.1.1.1', '2.2.2.2')
            self.assertEqual(del_rule.call_count, 2)

    def test_delete_fip_nat_rules_by_int(self):
        with mock.patch.object(self.nsxlib.logical_router,
                               "delete_nat_rule_by_values") as del_rule:
            self.nsxlib.router.delete_fip_nat_rules_by_internal_ip(
                test_constants.FAKE_ROUTER_UUID, '1.1.1.1')
            self.assertEqual(del_rule.call_count, 2)

    def test_add_static_routes(self):
        dest = '1.1.1.0/24'
        nexthop = '2.2.2.2'
        route = {'destination': dest, 'nexthop': nexthop}
        with mock.patch.object(self.nsxlib.logical_router,
                               "add_static_route") as add_route:
            self.nsxlib.router.add_static_routes(
                test_constants.FAKE_ROUTER_UUID, route)
            add_route.assert_called_once_with(
                test_constants.FAKE_ROUTER_UUID,
                dest, nexthop)

    def test_del_static_routes(self):
        dest = '1.1.1.0/24'
        nexthop = '2.2.2.2'
        route = {'destination': dest, 'nexthop': nexthop}
        with mock.patch.object(self.nsxlib.logical_router,
                               "delete_static_route_by_values") as del_route:
            self.nsxlib.router.delete_static_routes(
                test_constants.FAKE_ROUTER_UUID, route)
            del_route.assert_called_once_with(
                test_constants.FAKE_ROUTER_UUID,
                dest_cidr=dest, nexthop=nexthop)

    def test_has_service_router(self):
        logical_router_id = test_constants.FAKE_ROUTER_UUID
        ec_id = test_constants.FAKE_EDGE_CLUSTER
        lr = {'id': logical_router_id,
              'edge_cluster_id': ec_id}
        with mock.patch.object(self.nsxlib.router.nsxlib.logical_router,
                               'get', return_value=lr):
            res = self.nsxlib.router.has_service_router(
                logical_router_id)
            self.assertTrue(res)

    def test_get_tier0_router_tz(self):
        tier0_uuid = uuidutils.generate_uuid()
        self.nsxlib.feature_supported = mock.MagicMock()
        self.nsxlib.feature_supported.return_value = False
        with mock.patch.object(self.nsxlib.router._router_client, 'get',
                               return_value=test_constants.FAKE_TIERO_ROUTER),\
            mock.patch.object(self.nsxlib.edge_cluster, 'get',
                              return_value=test_constants.FAKE_EDGE_CLUSTER),\
            mock.patch.object(self.nsxlib.transport_node, 'get',
                              return_value=test_constants.FAKE_TRANS_NODE):
            tzs = self.nsxlib.router.get_tier0_router_tz(tier0_uuid)
            self.assertEqual(tzs, [test_constants.FAKE_TZ_UUID])

    def test_get_tier0_router_overlay_tz(self):
        tier0_uuid = uuidutils.generate_uuid()
        self.nsxlib.feature_supported = mock.MagicMock()
        self.nsxlib.feature_supported.return_value = False
        with mock.patch.object(self.nsxlib.router._router_client, 'get',
                               return_value=test_constants.FAKE_TIERO_ROUTER),\
            mock.patch.object(self.nsxlib.edge_cluster, 'get',
                              return_value=test_constants.FAKE_EDGE_CLUSTER),\
            mock.patch.object(self.nsxlib.transport_node, 'get',
                              return_value=test_constants.FAKE_TRANS_NODE),\
            mock.patch.object(self.nsxlib.transport_zone, 'get_transport_type',
                              return_value="OVERLAY"):
            tz = self.nsxlib.router.get_tier0_router_overlay_tz(tier0_uuid)
            self.assertEqual(tz, test_constants.FAKE_TZ_UUID)

    def test_get_tier0_router_overlay_tz_via_advanced_config(self):
        tier0_uuid = uuidutils.generate_uuid()
        with mock.patch.object(self.nsxlib.router._router_client, 'get',
                               return_value=test_constants.FAKE_TIERO_ROUTER):
            tz = self.nsxlib.router.get_tier0_router_overlay_tz(tier0_uuid)
            self.assertEqual(tz, test_constants.FAKE_TZ_UUID)

    def test_get_connected_t0_transit_net(self):
        t1_uuid = uuidutils.generate_uuid()
        transit_net = '1.1.1.0'
        link_port = {
            'subnets': [{'ip_addresses': [transit_net],
                         'prefix_length': '31'}]}
        with mock.patch.object(self.nsxlib.router._router_port_client,
                               'get_tier1_link_port',
                               return_value=link_port) as get_port:
            net = self.nsxlib.router.get_connected_t0_transit_net(t1_uuid)
            get_port.assert_called_with(t1_uuid)
            self.assertEqual('%s' % (transit_net), net)
