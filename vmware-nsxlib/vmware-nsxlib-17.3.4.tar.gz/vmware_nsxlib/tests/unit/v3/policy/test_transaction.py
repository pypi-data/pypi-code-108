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

from vmware_nsxlib.tests.unit.v3 import nsxlib_testcase
from vmware_nsxlib.tests.unit.v3.policy import policy_testcase
from vmware_nsxlib.v3 import policy
from vmware_nsxlib.v3.policy import constants
from vmware_nsxlib.v3.policy import transaction as trans


class TestPolicyTransaction(policy_testcase.TestPolicyApi):

    def setUp(self):

        super(TestPolicyTransaction, self).setUp()

        nsxlib_config = nsxlib_testcase.get_default_nsxlib_config()
        # Mock the nsx-lib for the passthrough api
        with mock.patch('vmware_nsxlib.v3.NsxLib.get_version',
                        return_value='2.5.0'):

            self.policy_lib = policy.NsxPolicyLib(nsxlib_config)
        self.policy_api = self.policy_lib.policy_api
        self.policy_api.client = self.client

    def assert_infra_patch_call(self, body):
        self.assert_json_call('PATCH', self.client, 'infra',
                              data=body, headers=mock.ANY)

    def test_domains_only(self):

        tags = [{'scope': 'color', 'tag': 'green'}]
        d1 = {'resource_type': 'Domain', 'id': 'domain1',
              'display_name': 'd1', 'description': 'first domain',
              'tags': tags}

        d2 = {'resource_type': 'Domain', 'id': 'domain2',
              'display_name': 'd2', 'description': 'no tags',
              'tags': None}
        with trans.NsxPolicyTransaction():

            for d in (d1, d2):
                self.policy_lib.domain.create_or_overwrite(
                    d['display_name'],
                    d['id'],
                    d['description'],
                    tags=d['tags'] if 'tags' in d else None)

        expected_body = {'resource_type': 'Infra',
                         'children': [{'resource_type': 'ChildDomain',
                                       'Domain': d1},
                                      {'resource_type': 'ChildDomain',
                                       'Domain': d2}]}

        self.assert_infra_patch_call(expected_body)

    def test_domains_and_groups(self):

        tags = [{'scope': 'color', 'tag': 'green'}]
        g1 = {'resource_type': 'Group', 'id': 'group1',
              'display_name': 'g1',
              'description': 'first group',
              'tags': None, 'expression': []}
        g2 = {'resource_type': 'Group', 'id': 'group2',
              'description': 'second group',
              'display_name': 'g2',
              'tags': tags, 'expression': []}
        g3 = {'resource_type': 'Group', 'id': 'group3',
              'display_name': 'g3',
              'description': 'third group',
              'tags': None, 'expression': []}
        d1 = {'resource_type': 'Domain', 'id': 'domain1',
              'display_name': 'd1', 'description': 'first domain',
              'tags': tags}

        d2 = {'resource_type': 'Domain', 'id': 'domain2',
              'display_name': 'd2', 'description': 'no tags',
              'tags': None}

        with trans.NsxPolicyTransaction():

            for d in (d1, d2):
                self.policy_lib.domain.create_or_overwrite(
                    d['display_name'],
                    d['id'],
                    d['description'],
                    tags=d['tags'] if 'tags' in d else None)

                d['children'] = []

                for g in (g1, g2, g3):
                    self.policy_lib.group.create_or_overwrite(
                        g['display_name'],
                        d['id'],
                        g['id'],
                        g['description'],
                        tags=g['tags'] if 'tags' in g else None)

                    d['children'].append({'resource_type': 'ChildGroup',
                                          'Group': g})

        expected_body = {'resource_type': 'Infra',
                         'children': [{'resource_type': 'ChildDomain',
                                       'Domain': d1},
                                      {'resource_type': 'ChildDomain',
                                       'Domain': d2}]}

        self.assert_infra_patch_call(expected_body)

    def test_ip_address_pool_and_block_subnets(self):

        pool = {'id': 'pool1',
                'resource_type': 'IpAddressPool',
                'display_name': 'pool1',
                'children': []}

        ip_block_id = 'block1'
        subnet1 = {'id': 'subnet1',
                   'resource_type': 'IpAddressPoolBlockSubnet',
                   'ip_block_path': '/infra/ip-blocks/%s' % ip_block_id,
                   'size': 8}

        subnet2 = {'id': 'subnet2',
                   'resource_type': 'IpAddressPoolBlockSubnet',
                   'ip_block_path': '/infra/ip-blocks/%s' % ip_block_id,
                   'size': 4}

        with trans.NsxPolicyTransaction():
            self.policy_lib.ip_pool.create_or_overwrite(
                pool['display_name'],
                ip_pool_id=pool['id'])

            for s in (subnet1, subnet2):
                self.policy_lib.ip_pool.allocate_block_subnet(
                    ip_pool_id=pool['id'],
                    ip_block_id=ip_block_id,
                    ip_subnet_id=s['id'],
                    size=s['size'])

                pool['children'].append(
                    {'resource_type': 'ChildIpAddressPoolSubnet',
                     'IpAddressPoolSubnet': s})

        expected_body = {'resource_type': 'Infra',
                         'children': [{'resource_type': 'ChildIpAddressPool',
                                       'IpAddressPool': pool}]}

        self.assert_infra_patch_call(expected_body)

    def test_ip_address_pool_delete(self):

        pool = {'id': 'pool1',
                'resource_type': 'IpAddressPool'}

        with trans.NsxPolicyTransaction():
            self.policy_lib.ip_pool.delete(ip_pool_id=pool['id'])

        expected_body = {'resource_type': 'Infra',
                         'children': [{'resource_type': 'ChildIpAddressPool',
                                       'IpAddressPool': pool,
                                       'marked_for_delete': True}]}

        self.assert_infra_patch_call(expected_body)

    def test_groups_only(self):

        g1 = {'resource_type': 'Group', 'id': 'group1',
              'display_name': 'g1',
              'description': 'first group', 'expression': []}
        g2 = {'resource_type': 'Group', 'id': 'group2',
              'description': 'second group',
              'display_name': 'g2', 'expression': []}
        d1 = {'resource_type': 'Domain', 'id': 'domain1'}

        d2 = {'resource_type': 'Domain', 'id': 'domain2'}

        with trans.NsxPolicyTransaction():

            for d in (d1, d2):
                d['children'] = []

                for g in (g1, g2):
                    self.policy_lib.group.create_or_overwrite(
                        g['display_name'],
                        d['id'],
                        g['id'],
                        g['description'])

                    d['children'].append({'resource_type': 'ChildGroup',
                                          'Group': g})

        expected_body = {'resource_type': 'Infra',
                         'children': [{'resource_type': 'ChildDomain',
                                       'Domain': d1},
                                      {'resource_type': 'ChildDomain',
                                       'Domain': d2}]}

        self.assert_infra_patch_call(expected_body)

    def test_segment_ports(self):

        port1 = {'id': 'port_on_seg1',
                 'resource_type': 'SegmentPort',
                 'display_name': 'port_on_seg1',
                 'attachment': {'type': 'VIF',
                                'app_id': 'app1',
                                'traffic_tag': 5}
                 }

        port2 = {'id': 'port1_on_seg2',
                 'resource_type': 'SegmentPort',
                 'display_name': 'port_on_seg2',
                 'attachment': {'type': 'CHILD',
                                'app_id': 'app2',
                                'traffic_tag': None}
                 }

        seg1 = {'id': 'seg1',
                'resource_type': 'Segment',
                'children': [{'resource_type': 'ChildSegmentPort',
                              'SegmentPort': port1}]}
        seg2 = {'id': 'seg2',
                'resource_type': 'Segment',
                'children': [{'resource_type': 'ChildSegmentPort',
                              'SegmentPort': port2}]}

        with trans.NsxPolicyTransaction():

            self.policy_lib.segment_port.create_or_overwrite(
                port1['display_name'],
                seg1['id'],
                port1['id'],
                attachment_type=port1['attachment']['type'],
                app_id=port1['attachment']['app_id'],
                traffic_tag=port1['attachment']['traffic_tag'])

            self.policy_lib.segment_port.create_or_overwrite(
                port2['display_name'],
                seg2['id'],
                port2['id'],
                attachment_type=port2['attachment']['type'],
                app_id=port2['attachment']['app_id'],
                traffic_tag=port2['attachment']['traffic_tag'])

        expected_body = {'resource_type': 'Infra',
                         'children': [{'resource_type': 'ChildSegment',
                                       'Segment': seg1},
                                      {'resource_type': 'ChildSegment',
                                       'Segment': seg2}]}

        self.assert_infra_patch_call(expected_body)

    def test_tier1_nat_rules_create(self):
        tier1_id = 'tier1-1'
        nat_rule_id1 = 'nat1'
        nat_rule_id2 = 'nat2'

        nat_rule1 = {"action": constants.NAT_ACTION_SNAT,
                     "display_name": "snat rule",
                     "id": nat_rule_id1,
                     "resource_type": "PolicyNatRule",
                     "firewall_match": constants.NAT_FIREWALL_MATCH_BYPASS}
        nat_rule2 = {"action": constants.NAT_ACTION_DNAT,
                     "display_name": "dnat rule",
                     "id": nat_rule_id2,
                     "resource_type": "PolicyNatRule",
                     "firewall_match": constants.NAT_FIREWALL_MATCH_BYPASS}

        policy_nat = {"id": "USER",
                      "resource_type": "PolicyNat",
                      "children": [
                          {"PolicyNatRule": nat_rule1,
                           "resource_type": "ChildPolicyNatRule"},
                          {"PolicyNatRule": nat_rule2,
                           "resource_type": "ChildPolicyNatRule"}]}
        tier1_dict = {"id": tier1_id,
                      "resource_type": "Tier1",
                      "children": [{"PolicyNat": policy_nat,
                                    "resource_type": "ChildPolicyNat"}]}

        with trans.NsxPolicyTransaction():
            self.policy_lib.tier1_nat_rule.create_or_overwrite(
                'snat rule',
                tier1_id,
                nat_rule_id=nat_rule_id1,
                action=constants.NAT_ACTION_SNAT)

            self.policy_lib.tier1_nat_rule.create_or_overwrite(
                'dnat rule',
                tier1_id,
                nat_rule_id=nat_rule_id2,
                action=constants.NAT_ACTION_DNAT)

        expected_body = {"resource_type": "Infra",
                         "children": [{"Tier1": tier1_dict,
                                       "resource_type": "ChildTier1"}]}

        self.assert_infra_patch_call(expected_body)

    def test_tier1_nat_rules_delete(self):
        tier1_id = 'tier1-1'
        nat_rule_id1 = 'nat1'
        nat_rule_id2 = 'nat2'

        nat_rule1 = {"action": constants.NAT_ACTION_DNAT,
                     "id": nat_rule_id1,
                     "resource_type": "PolicyNatRule"}
        nat_rule2 = {"action": constants.NAT_ACTION_DNAT,
                     "id": nat_rule_id2,
                     "resource_type": "PolicyNatRule"}

        policy_nat = {"id": "USER",
                      "resource_type": "PolicyNat",
                      "children": [
                          {"PolicyNatRule": nat_rule1,
                           "marked_for_delete": True,
                           "resource_type": "ChildPolicyNatRule"},
                          {"PolicyNatRule": nat_rule2,
                           "marked_for_delete": True,
                           "resource_type": "ChildPolicyNatRule"}]}
        tier1_dict = {"id": tier1_id,
                      "resource_type": "Tier1",
                      "children": [{"PolicyNat": policy_nat,
                                    "resource_type": "ChildPolicyNat"}]}

        with trans.NsxPolicyTransaction():
            self.policy_lib.tier1_nat_rule.delete(
                tier1_id,
                nat_rule_id=nat_rule_id1)

            self.policy_lib.tier1_nat_rule.delete(
                tier1_id,
                nat_rule_id=nat_rule_id2)

        expected_body = {"resource_type": "Infra",
                         "children": [{"Tier1": tier1_dict,
                                       "resource_type": "ChildTier1"}]}

        self.assert_infra_patch_call(expected_body)

    def test_creating_security_policy_and_dfw_rules(self):
        dfw_rule = {'id': 'rule_id1', 'action': 'ALLOW',
                    'display_name': 'rule1', 'description': None,
                    'direction': 'IN_OUT', 'ip_protocol': 'IPV4_IPV6',
                    'logged': False, 'destination_groups': ['destination_url'],
                    'source_groups': ['src_url'], 'resource_type': 'Rule',
                    'scope': None, 'sequence_number': None, 'tag': None,
                    'services': ['ANY']}
        security_policy = {'id': 'security_policy_id1',
                           'display_name': 'security_policy',
                           'category': 'Application',
                           'resource_type': 'SecurityPolicy'}
        domain = {'resource_type': 'Domain', 'id': 'domain1'}
        domain_id = domain['id']
        map_id = security_policy['id']
        dfw_rule_entries = [self.policy_lib.comm_map.build_entry(
            name=dfw_rule['display_name'],
            domain_id=domain_id,
            map_id=map_id,
            entry_id=dfw_rule['id'],
            source_groups=dfw_rule['source_groups'],
            dest_groups=dfw_rule['destination_groups']
        )]
        with trans.NsxPolicyTransaction():
            self.policy_lib.comm_map.create_with_entries(
                name=security_policy['display_name'],
                domain_id=domain_id,
                map_id=map_id,
                entries=dfw_rule_entries
            )

        def get_group_path(group_id, domain_id):
            return '/infra/domains/' + domain_id + '/groups/' + group_id

        dfw_rule['destination_groups'] = [get_group_path(group_id, domain_id)
                                          for group_id in
                                          dfw_rule['destination_groups']]
        dfw_rule['source_groups'] = [get_group_path(group_id, domain_id) for
                                     group_id in dfw_rule['source_groups']]
        child_rules = [{'resource_type': 'ChildRule', 'Rule': dfw_rule}]
        security_policy.update({'children': child_rules})
        child_security_policies = [{
            'resource_type': 'ChildSecurityPolicy',
            'SecurityPolicy': security_policy
        }]
        domain.update({'children': child_security_policies})
        child_domains = [{'resource_type': 'ChildDomain',
                         'Domain': domain}]
        expected_body = {'resource_type': 'Infra',
                         'children': child_domains}
        self.assert_infra_patch_call(expected_body)

    @mock.patch('vmware_nsxlib.v3.policy.core_defs.NsxPolicyApi.get')
    def _test_updating_security_policy_and_dfw_rules(
        self, use_child_rules, mock_get_api):
        dfw_rule1 = {'id': 'rule_id1', 'action': 'ALLOW',
                     'display_name': 'rule1', 'description': None,
                     'direction': 'IN_OUT', 'ip_protocol': 'IPV4_IPV6',
                     'logged': False,
                     'destination_groups': ['destination_url'],
                     'source_groups': ['src_url'], 'resource_type': 'Rule',
                     'scope': None, 'sequence_number': None, 'tag': None,
                     'services': ['ANY'], "_create_time": 1}
        dfw_rule2 = {'id': 'rule_id2', 'action': 'DROP',
                     'display_name': 'rule2', 'description': None,
                     'direction': 'IN_OUT', 'ip_protocol': 'IPV4_IPV6',
                     'logged': False,
                     'destination_groups': ['destination_url'],
                     'source_groups': ['src_url'], 'resource_type': 'Rule',
                     'scope': None, 'sequence_number': None, 'tag': None,
                     'services': ['ANY'], "_create_time": 1}
        security_policy = {'id': 'security_policy_id1',
                           'display_name': 'security_policy',
                           'category': 'Application',
                           'resource_type': 'SecurityPolicy'}
        domain = {'resource_type': 'Domain', 'id': 'domain1'}
        domain_id = domain['id']
        map_id = security_policy['id']
        new_rule_name = 'new_rule1'
        new_direction = 'IN'
        dfw_rule_entries = [self.policy_lib.comm_map.build_entry(
            name=new_rule_name,
            domain_id=domain_id,
            map_id=map_id,
            entry_id=dfw_rule1['id'],
            source_groups=dfw_rule1['source_groups'],
            dest_groups=dfw_rule1['destination_groups'],
            direction=new_direction
        )]

        def get_group_path(group_id, domain_id):
            return '/infra/domains/' + domain_id + '/groups/' + group_id

        for dfw_rule in [dfw_rule1, dfw_rule2]:
            dfw_rule['destination_groups'] = [get_group_path(group_id,
                                                             domain_id)
                                              for group_id in
                                              dfw_rule['destination_groups']]
            dfw_rule['source_groups'] = [get_group_path(group_id, domain_id)
                                         for group_id in
                                         dfw_rule['source_groups']]

        security_policy_values = copy.deepcopy(security_policy)
        security_policy_values.update({'rules':
                                      copy.deepcopy([dfw_rule1, dfw_rule2])})
        mock_get_api.return_value = security_policy_values

        with trans.NsxPolicyTransaction():
            self.policy_lib.comm_map.update_with_entries(
                name=security_policy['display_name'],
                domain_id=domain_id,
                map_id=map_id,
                entries=dfw_rule_entries,
                use_child_rules=use_child_rules
            )

        dfw_rule1['display_name'] = new_rule_name
        dfw_rule1['direction'] = new_direction
        if use_child_rules:
            child_rules = [{'resource_type': 'ChildRule', 'Rule': dfw_rule1},
                           {'resource_type': 'ChildRule', 'Rule': dfw_rule2,
                            'marked_for_delete': True}]
            security_policy.update({'children': child_rules})
        else:
            security_policy['rules'] = copy.deepcopy([dfw_rule1, dfw_rule2])

        child_security_policies = [{
            'resource_type': 'ChildSecurityPolicy',
            'SecurityPolicy': security_policy
        }]
        domain.update({'children': child_security_policies})
        child_domains = [{
            'resource_type': 'ChildDomain',
            'Domain': domain
        }]
        expected_body = {'resource_type': 'Infra',
                         'children': child_domains}
        self.assert_infra_patch_call(expected_body)

    def test_updating_security_policy_and_dfw_rules(self):
        return self._test_updating_security_policy_and_dfw_rules(True)

    def test_updating_security_policy_and_dfw_rules_no_child_rules(self):
        return self._test_updating_security_policy_and_dfw_rules(False)

    @mock.patch('vmware_nsxlib.v3.policy.core_defs.NsxPolicyApi.get')
    def test_updating_security_policy_with_no_entries_set(self, mock_get_api):
        dfw_rule1 = {'id': 'rule_id1', 'action': 'ALLOW',
                     'display_name': 'rule1', 'description': None,
                     'direction': 'IN_OUT', 'ip_protocol': 'IPV4_IPV6',
                     'logged': False,
                     'destination_groups': ['destination_url'],
                     'source_groups': ['src_url'], 'resource_type': 'Rule',
                     'scope': None, 'sequence_number': None, 'tag': None,
                     'services': ['ANY'], "_create_time": 1}
        security_policy = {'id': 'security_policy_id1',
                           'display_name': 'security_policy',
                           'category': 'Application',
                           'resource_type': 'SecurityPolicy'}
        domain = {'resource_type': 'Domain', 'id': 'domain1'}
        domain_id = domain['id']
        map_id = security_policy['id']

        def get_group_path(group_id, domain_id):
            return '/infra/domains/' + domain_id + '/groups/' + group_id

        for dfw_rule in [dfw_rule1]:
            dfw_rule['destination_groups'] = [get_group_path(group_id,
                                                             domain_id)
                                              for group_id in
                                              dfw_rule['destination_groups']]
            dfw_rule['source_groups'] = [get_group_path(group_id, domain_id)
                                         for group_id in
                                         dfw_rule['source_groups']]

        security_policy.update({'rules': [dfw_rule1]})
        mock_get_api.return_value = security_policy

        with trans.NsxPolicyTransaction():
            self.policy_lib.comm_map.update_with_entries(
                name=security_policy['display_name'],
                domain_id=domain_id,
                map_id=map_id
            )

        child_security_policies = [{
            'resource_type': 'ChildSecurityPolicy',
            'SecurityPolicy': security_policy
        }]
        domain.update({'children': child_security_policies})
        child_domains = [{
            'resource_type': 'ChildDomain',
            'Domain': domain
        }]
        expected_body = {'resource_type': 'Infra',
                         'children': child_domains}
        self.assert_infra_patch_call(expected_body)
