# Copyright 2017 VMware, Inc.
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

from unittest import mock

from vmware_nsxlib.tests.unit.v3 import nsxlib_testcase
from vmware_nsxlib.tests.unit.v3.policy import policy_testcase
from vmware_nsxlib.tests.unit.v3 import test_client
from vmware_nsxlib.v3 import exceptions as nsxlib_exc
from vmware_nsxlib.v3 import nsx_constants
from vmware_nsxlib.v3 import policy
from vmware_nsxlib.v3.policy import constants
from vmware_nsxlib.v3.policy import core_defs
from vmware_nsxlib.v3.policy import core_resources

TEST_TENANT = 'test'


class NsxPolicyLibTestCase(policy_testcase.TestPolicyApi):

    def setUp(self, *args, **kwargs):
        super(NsxPolicyLibTestCase, self).setUp()

        nsxlib_config = nsxlib_testcase.get_default_nsxlib_config(
            allow_passthrough=kwargs.get('allow_passthrough', True))

        # Mock the nsx-lib for the passthrough api
        with mock.patch("vmware_nsxlib.v3.NsxLib") as mock_lib:
            mock_lib.return_value.get_version.return_value = (
                nsxlib_testcase.LATEST_VERSION)
            self.policy_lib = policy.NsxPolicyLib(nsxlib_config)

        self.policy_api = self.policy_lib.policy_api
        self.policy_api.client = self.client

        self.maxDiff = None

    def _compare_def(self, expected_def, actual_def):
        # verify the resource definition class
        self.assertEqual(expected_def.__class__, actual_def.__class__)
        # verify the resource definition tenant
        self.assertEqual(expected_def.get_tenant(), actual_def.get_tenant())
        # verify the resource definition values
        self.assertEqual(expected_def.get_obj_dict(),
                         actual_def.get_obj_dict())

    def assert_called_with_def(self, mock_api, expected_def, call_num=0):
        # verify the api was called
        mock_api.assert_called()
        actual_def = mock_api.call_args_list[call_num][0][0]
        self._compare_def(expected_def, actual_def)

    def assert_called_with_defs(self, mock_api, expected_defs, call_num=0):
        # verify the api & first resource definition
        self.assert_called_with_def(mock_api, expected_defs[0],
                                    call_num=call_num)
        # compare the 2nd resource definition class & values
        def_list = mock_api.call_args_list[call_num][0][1]
        if not isinstance(def_list, list):
            def_list = [def_list]

        for i in range(1, len(expected_defs)):
            actual_def = def_list[i - 1]
            expected_def = expected_defs[i]
            self._compare_def(expected_def, actual_def)

    def assert_called_with_def_and_dict(self, mock_api,
                                        expected_def, expected_dict,
                                        call_num=0):
        # verify the api & resource definition
        self.assert_called_with_def(mock_api, expected_def,
                                    call_num=call_num)
        # compare the 2nd api parameter which is a dictionary
        actual_dict = mock_api.call_args_list[call_num][0][0].body
        self.assertEqual(expected_dict, actual_dict)

    def assert_called_with_def_and_kwargs(self, mock_api, expected_def,
                                          call_num=0, **kwargs):
        # verify the api & resource definition
        self.assert_called_with_def(mock_api, expected_def, call_num=call_num)
        actual_kwargs = mock_api.call_args_list[call_num][1]
        self.assertDictEqual(actual_kwargs, kwargs)

    def mock_get(self, obj_id, obj_name, **kwargs):
        obj_dict = {
            'id': obj_id,
            'display_name': obj_name,
            'resource_type': self.resourceApi.entry_def.resource_type()}
        if kwargs:
            obj_dict.update(kwargs)
        return mock.patch.object(self.policy_api, "get",
                                 return_value=obj_dict)

    def mock_create_update(self):
        return mock.patch.object(self.policy_api, "create_or_update")


class TestPolicyDomain(NsxPolicyLibTestCase):

    def setUp(self, *args, **kwargs):
        super(TestPolicyDomain, self).setUp()
        self.resourceApi = self.policy_lib.domain

    def test_create_with_id(self):
        name = 'd1'
        description = 'desc'
        domain_id = '111'
        with self.mock_create_update() as api_call:
            result = self.resourceApi.create_or_overwrite(
                name,
                domain_id=domain_id,
                description=description,
                tenant=TEST_TENANT)
            expected_def = core_defs.DomainDef(domain_id=domain_id,
                                               name=name,
                                               description=description,
                                               tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(domain_id, result)

    def test_minimalistic_create(self):
        name = 'test'
        with self.mock_create_update() as api_call:
            result = self.resourceApi.create_or_overwrite(name,
                                                          tenant=TEST_TENANT)
            expected_def = core_defs.DomainDef(domain_id=mock.ANY,
                                               name=name,
                                               tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertIsNotNone(result)

    def test_create_without_id(self):
        name = 'd1'
        description = 'desc'
        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            result = self.resourceApi.create_or_overwrite(
                name, description=description, tenant=TEST_TENANT)
            expected_def = core_defs.DomainDef(domain_id=mock.ANY,
                                               name=name,
                                               description=description,
                                               tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertIsNotNone(result)

    def test_delete(self):
        domain_id = '111'
        with mock.patch.object(self.policy_api, "delete") as api_call:
            self.resourceApi.delete(domain_id, tenant=TEST_TENANT)
            expected_def = core_defs.DomainDef(domain_id=domain_id,
                                               tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_get(self):
        domain_id = '111'
        with mock.patch.object(self.policy_api, "get",
                               return_value={'id': domain_id}) as api_call:
            result = self.resourceApi.get(domain_id, tenant=TEST_TENANT)
            expected_def = core_defs.DomainDef(domain_id=domain_id,
                                               tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(domain_id, result['id'])

    def test_get_by_name(self):
        name = 'd1'
        with mock.patch.object(
            self.policy_api, "list",
            return_value={'results': [{'display_name': name}]}) as api_call:
            obj = self.resourceApi.get_by_name(name, tenant=TEST_TENANT)
            self.assertIsNotNone(obj)
            expected_def = core_defs.DomainDef(tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_list(self):
        with mock.patch.object(self.policy_api, "list",
                               return_value={'results': []}) as api_call:
            result = self.resourceApi.list(tenant=TEST_TENANT)
            expected_def = core_defs.DomainDef(tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual([], result)

    def test_update(self):
        domain_id = '111'
        name = 'new name'
        description = 'new desc'
        with self.mock_get(domain_id, name), \
            self.mock_create_update() as update_call:
            self.resourceApi.update(domain_id,
                                    name=name,
                                    description=description,
                                    tenant=TEST_TENANT)
            expected_def = core_defs.DomainDef(domain_id=domain_id,
                                               name=name,
                                               description=description,
                                               tenant=TEST_TENANT)
            self.assert_called_with_def(update_call, expected_def)

    def test_unset(self):
        domain_id = '111'
        with mock.patch.object(self.policy_api, "get",
                               return_value={'id': domain_id}):
            self.resourceApi.update(domain_id,
                                    description=None,
                                    tags=None,
                                    tenant=TEST_TENANT)

            expected_body = {'id': domain_id,
                             'resource_type': 'Domain',
                             'description': None,
                             'tags': None}

            self.assert_json_call('PATCH', self.client,
                                  '%s/domains/%s' % (TEST_TENANT, domain_id),
                                  data=expected_body,
                                  headers=test_client.PARTIAL_UPDATE_HEADERS)


class TestPolicyGroup(NsxPolicyLibTestCase):

    def setUp(self, *args, **kwargs):
        super(TestPolicyGroup, self).setUp()
        self.resourceApi = self.policy_lib.group

    def test_create_with_id(self):
        domain_id = '111'
        name = 'g1'
        description = 'desc'
        group_id = '222'
        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            result = self.resourceApi.create_or_overwrite(
                name, domain_id,
                group_id=group_id,
                description=description,
                tenant=TEST_TENANT)
            expected_def = core_defs.GroupDef(domain_id=domain_id,
                                              group_id=group_id,
                                              name=name,
                                              description=description,
                                              conditions=[],
                                              tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(group_id, result)

    def test_create_without_id(self):
        domain_id = '111'
        name = 'g1'
        description = 'desc'
        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            result = self.resourceApi.create_or_overwrite(
                name, domain_id,
                description=description,
                tenant=TEST_TENANT)
            expected_def = core_defs.GroupDef(domain_id=domain_id,
                                              group_id=mock.ANY,
                                              name=name,
                                              description=description,
                                              conditions=[],
                                              tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertIsNotNone(result)

    def test_create_with_condition(self):
        domain_id = '111'
        name = 'g1'
        description = 'desc'
        cond_val = '123'
        cond_op = constants.CONDITION_OP_EQUALS
        cond_member_type = constants.CONDITION_MEMBER_VM
        cond_key = constants.CONDITION_KEY_TAG
        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            result = self.resourceApi.create_or_overwrite(
                name, domain_id, description=description,
                cond_val=cond_val,
                cond_op=cond_op,
                cond_member_type=cond_member_type,
                cond_key=cond_key,
                tenant=TEST_TENANT)
            exp_cond = core_defs.Condition(value=cond_val,
                                           key=cond_key,
                                           operator=cond_op,
                                           member_type=cond_member_type)
            expected_def = core_defs.GroupDef(domain_id=domain_id,
                                              group_id=mock.ANY,
                                              name=name,
                                              description=description,
                                              conditions=[exp_cond],
                                              tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertIsNotNone(result)

    def test_create_with_empty_condition(self):
        domain_id = '111'
        name = 'g1'
        description = 'desc'
        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            result = self.resourceApi.create_or_overwrite(
                name, domain_id, description=description,
                tenant=TEST_TENANT)
            expected_def = core_defs.GroupDef(domain_id=domain_id,
                                              group_id=mock.ANY,
                                              name=name,
                                              description=description,
                                              conditions=[],
                                              tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertIsNotNone(result)

    def test_create_with_simple_condition(self):
        domain_id = '111'
        name = 'g1'
        description = 'desc'
        cond_val = '123'
        cond_op = constants.CONDITION_OP_EQUALS
        cond_member_type = constants.CONDITION_MEMBER_VM
        cond_key = constants.CONDITION_KEY_TAG

        cond = self.resourceApi.build_condition(
            cond_val=cond_val,
            cond_op=cond_op,
            cond_member_type=cond_member_type,
            cond_key=cond_key)

        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            result = self.resourceApi.create_or_overwrite_with_conditions(
                name, domain_id, description=description,
                conditions=[cond],
                tenant=TEST_TENANT)
            exp_cond = core_defs.Condition(value=cond_val,
                                           key=cond_key,
                                           operator=cond_op,
                                           member_type=cond_member_type)
            expected_def = core_defs.GroupDef(domain_id=domain_id,
                                              group_id=mock.ANY,
                                              name=name,
                                              description=description,
                                              conditions=[exp_cond],
                                              tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertIsNotNone(result)

    def _test_create_with_condition(self, condition, exp_condition):
        domain_id = '111'
        name = 'g1'
        description = 'desc'
        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            result = self.resourceApi.create_or_overwrite_with_conditions(
                name, domain_id, description=description,
                conditions=condition, tenant=TEST_TENANT)
            expected_def = core_defs.GroupDef(domain_id=domain_id,
                                              group_id=mock.ANY,
                                              name=name,
                                              description=description,
                                              conditions=exp_condition,
                                              tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertIsNotNone(result)

    def test_create_with_union_condition(self):
        cond_val1 = '123'
        cond_val2 = '456'
        cond_op = constants.CONDITION_OP_EQUALS
        cond_member_type = constants.CONDITION_MEMBER_VM
        cond_key = constants.CONDITION_KEY_TAG

        cond1 = self.resourceApi.build_condition(
            cond_val=cond_val1,
            cond_op=cond_op,
            cond_member_type=cond_member_type,
            cond_key=cond_key)
        cond2 = self.resourceApi.build_condition(
            cond_val=cond_val2,
            cond_op=cond_op,
            cond_member_type=cond_member_type,
            cond_key=cond_key)
        cond1_dup = self.resourceApi.build_condition(
            cond_val=cond_val1,
            cond_op=cond_op,
            cond_member_type=cond_member_type,
            cond_key=cond_key)

        union_cond_no_dup = self.resourceApi.build_union_condition(
            conditions=[cond1, cond2])
        union_cond_dup = self.resourceApi.build_union_condition(
            conditions=[cond1, cond1_dup])

        exp_cond1 = core_defs.Condition(value=cond_val1,
                                        key=cond_key,
                                        operator=cond_op,
                                        member_type=cond_member_type)
        exp_cond2 = core_defs.Condition(value=cond_val2,
                                        key=cond_key,
                                        operator=cond_op,
                                        member_type=cond_member_type)
        or_cond = core_defs.ConjunctionOperator(
            operator=constants.CONDITION_OP_OR)
        exp_cond = list(set([exp_cond1, exp_cond2]))
        exp_cond.insert(1, or_cond)
        self._test_create_with_condition(union_cond_no_dup, exp_cond)
        self._test_create_with_condition(union_cond_dup, [exp_cond1])

    def test_create_with_nested_condition(self):
        cond_val1 = '123'
        cond_val2 = '456'
        cond_op = constants.CONDITION_OP_EQUALS
        cond_member_type = constants.CONDITION_MEMBER_VM
        cond_key = constants.CONDITION_KEY_TAG

        cond1 = self.resourceApi.build_condition(
            cond_val=cond_val1,
            cond_op=cond_op,
            cond_member_type=cond_member_type,
            cond_key=cond_key)
        cond2 = self.resourceApi.build_condition(
            cond_val=cond_val2,
            cond_op=cond_op,
            cond_member_type=cond_member_type,
            cond_key=cond_key)
        nested = self.resourceApi.build_nested_condition(
            conditions=[cond1, cond2])

        exp_cond1 = core_defs.Condition(value=cond_val1,
                                        key=cond_key,
                                        operator=cond_op,
                                        member_type=cond_member_type)
        exp_cond2 = core_defs.Condition(value=cond_val2,
                                        key=cond_key,
                                        operator=cond_op,
                                        member_type=cond_member_type)
        and_cond = core_defs.ConjunctionOperator()
        expressions = list(set([exp_cond1, exp_cond2]))
        expressions.insert(1, and_cond)
        exp_cond = core_defs.NestedExpression(expressions=expressions)
        self._test_create_with_condition(nested, exp_cond)

    def test_create_with_dup_nested_condition(self):
        cond_val1 = '123'
        cond_val2 = '456'
        cond_op = constants.CONDITION_OP_EQUALS
        cond_member_type = constants.CONDITION_MEMBER_VM
        cond_key = constants.CONDITION_KEY_TAG

        cond1 = self.resourceApi.build_condition(
            cond_val=cond_val1,
            cond_op=cond_op,
            cond_member_type=cond_member_type,
            cond_key=cond_key)
        cond2 = self.resourceApi.build_condition(
            cond_val=cond_val2,
            cond_op=cond_op,
            cond_member_type=cond_member_type,
            cond_key=cond_key)
        nested = self.resourceApi.build_nested_condition(
            conditions=[cond1, cond2])

        cond1_dup = self.resourceApi.build_condition(
            cond_val=cond_val1,
            cond_op=cond_op,
            cond_member_type=cond_member_type,
            cond_key=cond_key)
        cond2_dup = self.resourceApi.build_condition(
            cond_val=cond_val2,
            cond_op=cond_op,
            cond_member_type=cond_member_type,
            cond_key=cond_key)
        nested_dup = self.resourceApi.build_nested_condition(
            conditions=[cond1_dup, cond2_dup])

        double_nested = self.resourceApi.build_nested_condition(
            conditions=[nested, nested_dup])
        exp_cond = core_defs.NestedExpression(expressions=[nested])
        self._test_create_with_condition(double_nested, exp_cond)

    def test_create_with_ip_expression(self):
        domain_id = '111'
        name = 'g1'
        description = 'desc'
        cidr = '1.1.1.0/24'

        cond = self.resourceApi.build_ip_address_expression([cidr])

        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            result = self.resourceApi.create_or_overwrite_with_conditions(
                name, domain_id, description=description,
                conditions=[cond],
                tenant=TEST_TENANT)
            exp_cond = core_defs.IPAddressExpression([cidr])
            expected_def = core_defs.GroupDef(domain_id=domain_id,
                                              group_id=mock.ANY,
                                              name=name,
                                              description=description,
                                              conditions=[exp_cond],
                                              tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertIsNotNone(result)

    def test_create_with_path_expression(self):
        domain_id = '111'
        name = 'g1'
        description = 'desc'
        path = '/test/path1'

        cond = self.resourceApi.build_path_expression([path])

        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            result = self.resourceApi.create_or_overwrite_with_conditions(
                name, domain_id, description=description,
                conditions=[cond],
                tenant=TEST_TENANT)
            exp_cond = core_defs.PathExpression([path])
            expected_def = core_defs.GroupDef(domain_id=domain_id,
                                              group_id=mock.ANY,
                                              name=name,
                                              description=description,
                                              conditions=[exp_cond],
                                              tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertIsNotNone(result)

    def test_delete(self):
        domain_id = '111'
        group_id = '222'
        with mock.patch.object(self.policy_api, "delete") as api_call:
            self.resourceApi.delete(domain_id, group_id, tenant=TEST_TENANT)
            expected_def = core_defs.GroupDef(domain_id=domain_id,
                                              group_id=group_id,
                                              tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_get(self):
        domain_id = '111'
        group_id = '222'
        with mock.patch.object(self.policy_api, "get",
                               return_value={'id': group_id}) as api_call:
            result = self.resourceApi.get(domain_id, group_id,
                                          tenant=TEST_TENANT)
            expected_def = core_defs.GroupDef(domain_id=domain_id,
                                              group_id=group_id,
                                              tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(group_id, result['id'])

    def test_get_by_name(self):
        domain_id = '111'
        name = 'g1'
        with mock.patch.object(
            self.policy_api, "list",
            return_value={'results': [{'display_name': name}]}) as api_call:
            obj = self.resourceApi.get_by_name(domain_id, name,
                                               tenant=TEST_TENANT)
            self.assertIsNotNone(obj)
            expected_def = core_defs.GroupDef(domain_id=domain_id,
                                              tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_list(self):
        domain_id = '111'
        with mock.patch.object(self.policy_api, "list",
                               return_value={'results': []}) as api_call:
            result = self.resourceApi.list(domain_id, tenant=TEST_TENANT)
            expected_def = core_defs.GroupDef(domain_id=domain_id,
                                              tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual([], result)

    def test_update(self):
        domain_id = '111'
        group_id = '222'
        name = 'new name'
        description = 'new desc'
        with self.mock_get(group_id, name), \
            self.mock_create_update() as update_call:
            self.resourceApi.update(domain_id, group_id,
                                    name=name,
                                    description=description,
                                    tenant=TEST_TENANT)
            expected_def = core_defs.GroupDef(domain_id=domain_id,
                                              group_id=group_id,
                                              name=name,
                                              description=description,
                                              tenant=TEST_TENANT)
            self.assert_called_with_def(
                update_call, expected_def)

    def test_update_with_conditions(self):
        domain_id = '111'
        group_id = '222'
        name = 'name'
        new_name = 'new name'
        description = 'desc'
        new_description = 'new desc'

        cond_val1 = '123'
        cond_val2 = '456'
        cond_op = constants.CONDITION_OP_EQUALS
        cond_member_type = constants.CONDITION_MEMBER_VM
        cond_key = constants.CONDITION_KEY_TAG
        cond1_def = core_defs.Condition(value=cond_val1,
                                        key=cond_key,
                                        operator=cond_op,
                                        member_type=cond_member_type)
        cond2_def = core_defs.Condition(value=cond_val2,
                                        key=cond_key,
                                        operator=cond_op,
                                        member_type=cond_member_type)
        original_group = {
            'id': group_id,
            'resource_type': 'Group',
            'display_name': name,
            'description': description,
            'expression': [cond1_def.get_obj_dict()]}
        updated_group = {
            'id': group_id,
            'resource_type': 'Group',
            'display_name': new_name,
            'description': new_description,
            'expression': [cond2_def.get_obj_dict()]}
        group_def = core_defs.GroupDef(
            domain_id=domain_id,
            group_id=group_id,
            tenant=TEST_TENANT)
        with mock.patch.object(self.policy_api, "get",
                               return_value=original_group),\
            mock.patch.object(self.policy_api.client,
                              "update") as update_call:
            self.resourceApi.update_with_conditions(
                domain_id, group_id, name=new_name,
                description=new_description,
                conditions=[cond2_def], tenant=TEST_TENANT)
            update_call.assert_called_once_with(
                group_def.get_resource_path(), updated_group)

    def test_update_with_conditions_callback(self):

        def update_payload_cbk(revised_payload, payload):
            revised_ips = revised_payload["expression"][0]["ip_addresses"]
            new_ips = payload["conditions"][0].ip_addresses
            updated_ips = revised_ips + new_ips
            payload["conditions"] = [core_defs.IPAddressExpression(
                updated_ips)]

        domain_id = '111'
        group_id = '222'
        name = 'name'
        new_name = 'new name'
        description = 'desc'
        new_description = 'new desc'

        ips1 = ["1.1.1.1"]
        ips2 = ["2.2.2.2"]
        cond1_def = core_defs.IPAddressExpression(ips1)
        cond2_def = core_defs.IPAddressExpression(ips2)
        updated_cond_def = core_defs.IPAddressExpression(ips1 + ips2)

        original_group = {
            'id': group_id,
            'resource_type': 'Group',
            'display_name': name,
            'description': description,
            'expression': [cond1_def.get_obj_dict()]}
        updated_group = {
            'id': group_id,
            'resource_type': 'Group',
            'display_name': new_name,
            'description': new_description,
            'expression': [updated_cond_def.get_obj_dict()]}
        group_def = core_defs.GroupDef(
            domain_id=domain_id,
            group_id=group_id,
            conditions=[cond2_def],
            tenant=TEST_TENANT)
        with mock.patch.object(self.policy_api, "get",
                               return_value=original_group),\
            mock.patch.object(self.policy_api.client,
                              "update") as update_call:
            self.resourceApi.update_with_conditions(
                domain_id, group_id, name=new_name,
                description=new_description,
                conditions=[cond2_def], tenant=TEST_TENANT,
                update_payload_cbk=update_payload_cbk)
            update_call.assert_called_once_with(
                group_def.get_resource_path(), updated_group)

    def test_unset(self):
        domain_id = '111'
        group_id = '222'
        description = 'new'

        with self.mock_get(group_id, 'test'):
            self.resourceApi.update(domain_id,
                                    group_id,
                                    name=None,
                                    description=description,
                                    tenant=TEST_TENANT)

            expected_body = {'id': group_id,
                             'resource_type': 'Group',
                             'display_name': None,
                             'description': description}

            self.assert_json_call('PATCH', self.client,
                                  '%s/domains/%s/groups/%s' % (TEST_TENANT,
                                                               domain_id,
                                                               group_id),
                                  data=expected_body,
                                  headers=test_client.PARTIAL_UPDATE_HEADERS)

    def test_get_realized(self):
        domain_id = 'd1'
        group_id = 'g1'
        result = [{'state': constants.STATE_REALIZED,
                   'entity_type': 'RealizedGroup'}]
        with mock.patch.object(
            self.policy_api, "get_realized_entities",
            return_value=result) as api_get:
            state = self.resourceApi.get_realized_state(
                domain_id, group_id, tenant=TEST_TENANT)
            self.assertEqual(constants.STATE_REALIZED, state)
            path = "/%s/domains/%s/groups/%s" % (
                TEST_TENANT, domain_id, group_id)
            api_get.assert_called_once_with(path, silent=False)

    def test_get_realized_multiple_results_get_default(self):
        domain_id = 'd1'
        group_id = 'g1'
        result = [{'state': constants.STATE_UNREALIZED,
                   'entity_type': 'NotRealizedGroup'},
                  {'state': constants.STATE_REALIZED,
                   'entity_type': 'RealizedGroup'}]
        with mock.patch.object(
            self.policy_api, "get_realized_entities",
            return_value=result) as api_get:
            state = self.resourceApi.get_realized_state(
                domain_id, group_id, tenant=TEST_TENANT)
            self.assertEqual(constants.STATE_UNREALIZED, state)
            path = "/%s/domains/%s/groups/%s" % (
                TEST_TENANT, domain_id, group_id)
            api_get.assert_called_once_with(path, silent=False)

    def test_get_realized_multiple_results_get_specific(self):
        domain_id = 'd1'
        group_id = 'g1'
        result = [{'state': constants.STATE_UNREALIZED,
                   'entity_type': 'NotRealizedGroup'},
                  {'state': constants.STATE_REALIZED,
                   'entity_type': 'RealizedGroup'}]
        with mock.patch.object(
            self.policy_api, "get_realized_entities",
            return_value=result) as api_get:
            state = self.resourceApi.get_realized_state(
                domain_id, group_id, entity_type='RealizedGroup',
                tenant=TEST_TENANT)
            self.assertEqual(constants.STATE_REALIZED, state)
            path = "/%s/domains/%s/groups/%s" % (
                TEST_TENANT, domain_id, group_id)
            api_get.assert_called_once_with(path, silent=False)

    def test_get_realized_id(self):
        domain_id = 'd1'
        group_id = 'g1'
        realized_id = 'realized_111'
        result = [{'state': constants.STATE_REALIZED,
                   'entity_type': 'RealizedGroup',
                   'realization_specific_identifier': realized_id}]
        with mock.patch.object(
            self.policy_api, "get_realized_entities",
            return_value=result) as api_get:
            result_id = self.resourceApi.get_realized_id(
                domain_id, group_id, tenant=TEST_TENANT)
            self.assertEqual(realized_id, result_id)
            path = "/%s/domains/%s/groups/%s" % (
                TEST_TENANT, domain_id, group_id)
            api_get.assert_called_once_with(path, silent=False)

    def test_get_path(self):
        domain_id = 'd1'
        group_id = 'g1'
        result = self.resourceApi.get_path(domain_id, group_id,
                                           tenant=TEST_TENANT)
        expected_path = '/%s/domains/%s/groups/%s' % (
            TEST_TENANT, domain_id, group_id)
        self.assertEqual(expected_path, result)

    def test_wait_until_realized_fail(self):
        domain_id = 'd1'
        group_id = 'g1'
        info = {'state': constants.STATE_UNREALIZED,
                'realization_specific_identifier': group_id,
                'entity_type': 'RealizedGroup'}
        with mock.patch.object(self.resourceApi, "_get_realization_info",
                               return_value=info):
            self.assertRaises(nsxlib_exc.RealizationTimeoutError,
                              self.resourceApi.wait_until_realized,
                              domain_id, group_id, max_attempts=5,
                              sleep=0.1, tenant=TEST_TENANT)

    def test_wait_until_realized_succeed(self):
        domain_id = 'd1'
        group_id = 'g1'
        info = {'state': constants.STATE_REALIZED,
                'realization_specific_identifier': group_id,
                'entity_type': 'RealizedGroup'}
        with mock.patch.object(self.resourceApi, "_get_realization_info",
                               return_value=info):
            actual_info = self.resourceApi.wait_until_realized(
                domain_id, group_id, max_attempts=5, sleep=0.1,
                tenant=TEST_TENANT)
            self.assertEqual(info, actual_info)


class TestPolicyL4Service(NsxPolicyLibTestCase):

    def setUp(self, *args, **kwargs):
        super(TestPolicyL4Service, self).setUp()
        self.resourceApi = self.policy_lib.service

    def test_create(self):
        name = 's1'
        description = 'desc'
        protocol = constants.TCP
        dest_ports = [81, 82]
        source_ports = [83, 84]
        tags = [{'scope': 'a', 'tag': 'b'}]
        with mock.patch.object(self.policy_api,
                               "create_with_parent") as api_call:
            result = self.resourceApi.create_or_overwrite(
                name,
                description=description,
                protocol=protocol,
                dest_ports=dest_ports,
                source_ports=source_ports,
                tags=tags,
                tenant=TEST_TENANT)
            exp_srv_def = core_defs.ServiceDef(service_id=mock.ANY,
                                               name=name,
                                               description=description,
                                               tags=tags,
                                               tenant=TEST_TENANT)
            exp_entry_def = core_defs.L4ServiceEntryDef(
                service_id=mock.ANY,
                entry_id='entry',
                name='entry',
                protocol=protocol,
                dest_ports=dest_ports,
                source_ports=source_ports,
                tenant=TEST_TENANT)
            self.assert_called_with_defs(
                api_call, [exp_srv_def, exp_entry_def])
            self.assertIsNotNone(result)

    def test_delete(self):
        srv_id = '111'
        with mock.patch.object(self.policy_api, "delete") as api_call:
            self.resourceApi.delete(srv_id, tenant=TEST_TENANT)
            expected_def = core_defs.ServiceDef(service_id=srv_id,
                                                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_get(self):
        srv_id = '111'
        with mock.patch.object(self.policy_api, "get",
                               return_value={'id': srv_id}) as api_call:
            result = self.resourceApi.get(srv_id, tenant=TEST_TENANT)
            expected_def = core_defs.ServiceDef(service_id=srv_id,
                                                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(srv_id, result['id'])

    def test_get_by_name(self):
        name = 's1'
        with mock.patch.object(
            self.policy_api, "list",
            return_value={'results': [{'display_name': name}]}) as api_call:
            obj = self.resourceApi.get_by_name(name, tenant=TEST_TENANT)
            self.assertIsNotNone(obj)
            expected_def = core_defs.ServiceDef(tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_list(self):
        with mock.patch.object(self.policy_api, "list",
                               return_value={'results': []}) as api_call:
            result = self.resourceApi.list(tenant=TEST_TENANT)
            expected_def = core_defs.ServiceDef(tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual([], result)

    def test_update(self):
        srv_id = '111'
        name = 'newName'
        description = 'new desc'
        protocol = 'tcp'
        tags = [{'scope': 'a', 'tag': 'b'}]
        entry_body = {'id': 'entry',
                      'l4_protocol': protocol}

        with mock.patch.object(self.policy_api,
                               "get",
                               return_value=entry_body),\
            mock.patch.object(self.policy_api,
                              "create_with_parent") as update_call:

            self.resourceApi.update(srv_id,
                                    name=name,
                                    description=description,
                                    tags=tags,
                                    tenant=TEST_TENANT)
            service_def = core_defs.ServiceDef(service_id=srv_id,
                                               name=name,
                                               description=description,
                                               tags=tags,
                                               tenant=TEST_TENANT)
            entry_def = core_defs.L4ServiceEntryDef(
                service_id=id,
                entry_id='entry',
                protocol=protocol,
                tenant=TEST_TENANT)
            self.assert_called_with_defs(update_call, [service_def, entry_def])

    def test_update_all(self):
        srv_id = '111'
        name = 'newName'
        description = 'new desc'
        protocol = 'udp'
        dest_ports = [555]
        source_ports = [666]

        entry_body = {'id': 'entry',
                      'l4_protocol': 'tcp'}

        with mock.patch.object(self.policy_api,
                               "get",
                               return_value=entry_body),\
            mock.patch.object(self.policy_api,
                              "create_with_parent") as update_call:
            self.resourceApi.update(srv_id,
                                    name=name,
                                    description=description,
                                    protocol=protocol,
                                    dest_ports=dest_ports,
                                    source_ports=source_ports,
                                    tenant=TEST_TENANT)

            service_def = core_defs.ServiceDef(service_id=srv_id,
                                               name=name,
                                               description=description,
                                               tenant=TEST_TENANT)
            entry_def = core_defs.L4ServiceEntryDef(
                service_id=srv_id,
                entry_id=mock.ANY,
                protocol=protocol,
                dest_ports=dest_ports,
                source_ports=source_ports,
                tenant=TEST_TENANT)

            self.assert_called_with_defs(
                update_call, [service_def, entry_def])

    def test_unset(self):
        name = 'hello'
        service_id = '111'

        # Until policy PATCH is fixed to accept partial update, we
        # call get on child entry
        with mock.patch.object(
            self.policy_api, "get",
            return_value={'display_name': name}):
            self.resourceApi.update(service_id,
                                    description=None,
                                    dest_ports=None,
                                    tenant=TEST_TENANT)

        expected_body = {'id': service_id,
                         'description': None,
                         'resource_type': 'Service',
                         'service_entries': [{
                             'display_name': name,
                             'id': 'entry',
                             'resource_type': 'L4PortSetServiceEntry',
                             'destination_ports': None}]
                         }

        self.assert_json_call('PATCH', self.client,
                              '%s/services/%s' % (TEST_TENANT, service_id),
                              data=expected_body)


class TestPolicyIcmpService(NsxPolicyLibTestCase):

    def setUp(self, *args, **kwargs):
        super(TestPolicyIcmpService, self).setUp()
        self.resourceApi = self.policy_lib.icmp_service

    def test_create(self):
        name = 's1'
        description = 'desc'
        icmp_type = 2
        with mock.patch.object(self.policy_api,
                               "create_with_parent") as api_call:
            result = self.resourceApi.create_or_overwrite(
                name,
                description=description,
                icmp_type=icmp_type,
                tenant=TEST_TENANT)
            exp_srv_def = core_defs.ServiceDef(service_id=mock.ANY,
                                               name=name,
                                               description=description,
                                               tenant=TEST_TENANT)
            exp_entry_def = core_defs.IcmpServiceEntryDef(
                service_id=mock.ANY,
                entry_id='entry',
                name='entry',
                version=4,
                icmp_type=icmp_type,
                tenant=TEST_TENANT)
            self.assert_called_with_defs(
                api_call, [exp_srv_def, exp_entry_def])
            self.assertIsNotNone(result)

    def test_delete(self):
        srv_id = '111'
        with mock.patch.object(self.policy_api, "delete") as api_call:
            self.resourceApi.delete(srv_id, tenant=TEST_TENANT)
            expected_def = core_defs.ServiceDef(service_id=srv_id,
                                                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_get(self):
        srv_id = '111'
        with mock.patch.object(self.policy_api, "get",
                               return_value={'id': srv_id}) as api_call:
            result = self.resourceApi.get(srv_id, tenant=TEST_TENANT)
            expected_def = core_defs.ServiceDef(service_id=srv_id,
                                                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(srv_id, result['id'])

    def test_get_by_name(self):
        name = 's1'
        with mock.patch.object(
            self.policy_api, "list",
            return_value={'results': [{'display_name': name}]}) as api_call:
            obj = self.resourceApi.get_by_name(name, tenant=TEST_TENANT)
            self.assertIsNotNone(obj)
            expected_def = core_defs.ServiceDef(tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_list(self):
        with mock.patch.object(self.policy_api, "list",
                               return_value={'results': []}) as api_call:
            result = self.resourceApi.list(tenant=TEST_TENANT)
            expected_def = core_defs.ServiceDef(tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual([], result)

    def test_update(self):
        srv_id = '111'
        name = 'new_name'
        description = 'new desc'
        with mock.patch.object(self.policy_api, "get",
                               return_value={'id': 'entry',
                                             'protocol': 'ICMPv4'}),\
            mock.patch.object(self.policy_api,
                              "create_with_parent") as update_call:
            self.resourceApi.update(srv_id,
                                    name=name,
                                    description=description,
                                    tenant=TEST_TENANT)

            service_def = core_defs.ServiceDef(service_id=srv_id,
                                               name=name,
                                               description=description,
                                               tenant=TEST_TENANT)

            entry_def = core_defs.IcmpServiceEntryDef(
                service_id=srv_id,
                entry_id='entry',
                version=4,
                tenant=TEST_TENANT)

            self.assert_called_with_defs(update_call, [service_def, entry_def])

    def test_update_all(self):
        srv_id = '111'
        name = 'newName'
        description = 'new desc'
        version = 6
        icmp_type = 3
        icmp_code = 3

        with mock.patch.object(self.policy_api, "get",
                               return_value={'id': 'entry'}),\
            mock.patch.object(self.policy_api,
                              "create_with_parent") as update_call:
            self.resourceApi.update(srv_id,
                                    name=name,
                                    description=description,
                                    version=version,
                                    icmp_type=icmp_type,
                                    icmp_code=icmp_code,
                                    tenant=TEST_TENANT)
            # get will be called for the entire service
            service_def = core_defs.ServiceDef(service_id=srv_id,
                                               name=name,
                                               description=description,
                                               tenant=TEST_TENANT)
            entry_def = core_defs.IcmpServiceEntryDef(
                service_id=srv_id,
                entry_id=mock.ANY,
                version=version,
                icmp_type=icmp_type,
                icmp_code=icmp_code,
                tenant=TEST_TENANT)

            self.assert_called_with_defs(
                update_call, [service_def, entry_def])

    def test_icmp_type_and_code_in_obj_dict(self):
        icmp_type, icmp_code = 0, 0
        entry_def = core_defs.IcmpServiceEntryDef(
            icmp_type=icmp_type, icmp_code=icmp_code)
        body = entry_def.get_obj_dict()
        self.assertEqual(icmp_type, body["icmp_type"])
        self.assertEqual(icmp_code, body["icmp_code"])


class TestPolicyIPProtocolService(NsxPolicyLibTestCase):

    def setUp(self, *args, **kwargs):
        super(TestPolicyIPProtocolService, self).setUp()
        self.resourceApi = self.policy_lib.ip_protocol_service

    def test_create(self):
        name = 's1'
        description = 'desc'
        protocol_number = 2
        with mock.patch.object(self.policy_api,
                               "create_with_parent") as api_call:
            result = self.resourceApi.create_or_overwrite(
                name,
                description=description,
                protocol_number=protocol_number,
                tenant=TEST_TENANT)
            exp_srv_def = core_defs.ServiceDef(service_id=mock.ANY,
                                               name=name,
                                               description=description,
                                               tenant=TEST_TENANT)
            exp_entry_def = core_defs.IPProtocolServiceEntryDef(
                service_id=mock.ANY,
                entry_id='entry',
                name='entry',
                protocol_number=protocol_number,
                tenant=TEST_TENANT)
            self.assert_called_with_defs(
                api_call, [exp_srv_def, exp_entry_def])
            self.assertIsNotNone(result)

    def test_delete(self):
        srv_id = '111'
        with mock.patch.object(self.policy_api, "delete") as api_call:
            self.resourceApi.delete(srv_id, tenant=TEST_TENANT)
            expected_def = core_defs.ServiceDef(service_id=srv_id,
                                                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_get(self):
        srv_id = '111'
        with mock.patch.object(self.policy_api, "get",
                               return_value={'id': srv_id}) as api_call:
            result = self.resourceApi.get(srv_id, tenant=TEST_TENANT)
            expected_def = core_defs.ServiceDef(service_id=srv_id,
                                                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(srv_id, result['id'])

    def test_get_by_name(self):
        name = 's1'
        with mock.patch.object(
            self.policy_api, "list",
            return_value={'results': [{'display_name': name}]}) as api_call:
            obj = self.resourceApi.get_by_name(name, tenant=TEST_TENANT)
            self.assertIsNotNone(obj)
            expected_def = core_defs.ServiceDef(tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_list(self):
        with mock.patch.object(self.policy_api, "list",
                               return_value={'results': []}) as api_call:
            result = self.resourceApi.list(tenant=TEST_TENANT)
            expected_def = core_defs.ServiceDef(tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual([], result)

    def test_update(self):
        srv_id = '111'
        name = 'new_name'
        description = 'new desc'
        with mock.patch.object(self.policy_api, "get",
                               return_value={'id': 'entry'}),\
            mock.patch.object(self.policy_api,
                              "create_with_parent") as update_call:
            self.resourceApi.update(srv_id,
                                    name=name,
                                    description=description,
                                    tenant=TEST_TENANT)
            service_def = core_defs.ServiceDef(service_id=srv_id,
                                               name=name,
                                               description=description,
                                               tenant=TEST_TENANT)

            entry_def = core_defs.IPProtocolServiceEntryDef(
                service_id=srv_id,
                entry_id='entry',
                tenant=TEST_TENANT)

            self.assert_called_with_defs(update_call, [service_def, entry_def])

    def test_update_all(self):
        srv_id = '111'
        name = 'newName'
        description = 'new desc'
        protocol_number = 3

        with mock.patch.object(self.policy_api, "get",
                               return_value={'id': 'entry'}),\
            mock.patch.object(self.policy_api,
                              "create_with_parent") as service_update_call:
            self.resourceApi.update(srv_id,
                                    name=name,
                                    description=description,
                                    protocol_number=protocol_number,
                                    tenant=TEST_TENANT)

            service_def = core_defs.ServiceDef(service_id=srv_id,
                                               name=name,
                                               description=description,
                                               tenant=TEST_TENANT)
            entry_def = core_defs.IPProtocolServiceEntryDef(
                service_id=srv_id,
                entry_id='entry',
                protocol_number=protocol_number,
                tenant=TEST_TENANT)

            self.assert_called_with_defs(service_update_call,
                                         [service_def, entry_def])

    def test_protocol_number_in_obj_dict(self):
        protocol_number = 0
        entry_def = core_defs.IPProtocolServiceEntryDef(
            protocol_number=protocol_number)
        body = entry_def.get_obj_dict()
        self.assertEqual(protocol_number, body["protocol_number"])


class TestPolicyMixedService(NsxPolicyLibTestCase):

    def setUp(self, *args, **kwargs):
        super(TestPolicyMixedService, self).setUp()
        self.l4ServiceApi = self.policy_lib.service
        self.icmpServiceApi = self.policy_lib.icmp_service
        self.ipServiceApi = self.policy_lib.ip_protocol_service
        self.resourceApi = self.policy_lib.mixed_service

    def test_create_service_only(self):
        name = 's1'
        srv_id = '111'
        description = 'desc'
        tags = [{'scope': 'a', 'tag': 'b'}]
        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            result = self.resourceApi.create_or_overwrite(
                name,
                srv_id,
                description=description,
                tags=tags,
                tenant=TEST_TENANT)

            exp_srv_def = core_defs.ServiceDef(
                service_id=srv_id,
                name=name,
                description=description,
                tags=tags,
                tenant=TEST_TENANT)

            self.assert_called_with_def(api_call, exp_srv_def)
            self.assertIsNotNone(result)

    def test_create_with_entries(self):
        name = 's1'
        srv_id = '111'
        description = 'desc'
        tags = [{'scope': 'a', 'tag': 'b'}]
        protocol = constants.TCP
        dest_ports = [81, 82]
        source_ports = [83, 84]
        icmp_type = 2
        protocol_number = 2

        l4_entry = self.l4ServiceApi.build_entry(
            'l4_entry', srv_id, 'l4_entry', protocol=protocol,
            dest_ports=dest_ports, source_ports=source_ports,
            tenant=TEST_TENANT)

        icmp_entry = self.icmpServiceApi.build_entry(
            'icmp_entry', srv_id, 'icmp_entry', icmp_type=icmp_type,
            tenant=TEST_TENANT)

        ip_entry = self.ipServiceApi.build_entry(
            'ip_entry', srv_id, 'ip_entry',
            protocol_number=protocol_number, tenant=TEST_TENANT)

        with mock.patch.object(self.policy_api,
                               "create_with_parent") as api_call:
            result = self.resourceApi.create_or_overwrite(
                name,
                srv_id,
                description=description,
                entries=[l4_entry, icmp_entry, ip_entry],
                tags=tags,
                tenant=TEST_TENANT)

            service_def = core_defs.ServiceDef(
                service_id=srv_id,
                name=name,
                description=description,
                tags=tags,
                tenant=TEST_TENANT)

            self.assert_called_with_defs(
                api_call, [service_def, l4_entry, icmp_entry, ip_entry])
            self.assertIsNotNone(result)

    def test_delete(self):
        srv_id = '111'
        with mock.patch.object(self.policy_api, "delete") as api_call:
            self.resourceApi.delete(srv_id, tenant=TEST_TENANT)
            expected_def = core_defs.ServiceDef(service_id=srv_id,
                                                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_get(self):
        srv_id = '111'
        with mock.patch.object(self.policy_api, "get",
                               return_value={'id': srv_id}) as api_call:
            result = self.resourceApi.get(srv_id, tenant=TEST_TENANT)
            expected_def = core_defs.ServiceDef(service_id=srv_id,
                                                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(srv_id, result['id'])

    def test_get_by_name(self):
        name = 's1'
        with mock.patch.object(
            self.policy_api, "list",
            return_value={'results': [{'display_name': name}]}) as api_call:
            obj = self.resourceApi.get_by_name(name, tenant=TEST_TENANT)
            self.assertIsNotNone(obj)
            expected_def = core_defs.ServiceDef(tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_list(self):
        with mock.patch.object(self.policy_api, "list",
                               return_value={'results': []}) as api_call:
            result = self.resourceApi.list(tenant=TEST_TENANT)
            expected_def = core_defs.ServiceDef(tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual([], result)

    def test_update(self):
        name = 'newName'
        srv_id = '111'
        description = 'new desc'
        tags = [{'scope': 'c', 'tag': 'd'}]
        protocol = constants.UDP
        dest_ports = [91, 92]
        source_ports = [93, 94]
        icmp_type = 3
        protocol_number = 3

        l4_entry = self.l4ServiceApi.build_entry(
            'l4_entry', srv_id, 'l4_entry', protocol=protocol,
            dest_ports=dest_ports, source_ports=source_ports,
            tenant=TEST_TENANT)

        icmp_entry = self.icmpServiceApi.build_entry(
            'icmp_entry', srv_id, 'icmp_entry', icmp_type=icmp_type,
            tenant=TEST_TENANT)

        ip_entry = self.ipServiceApi.build_entry(
            'ip_entry', srv_id, 'ip_entry',
            protocol_number=protocol_number, tenant=TEST_TENANT)

        with mock.patch.object(self.policy_api, "get",
                               return_value={}),\
            mock.patch.object(self.policy_api,
                              "create_with_parent") as update_call:
            self.resourceApi.update(
                srv_id,
                name=name,
                description=description,
                entries=[l4_entry, icmp_entry, ip_entry],
                tags=tags,
                tenant=TEST_TENANT)

            service_def = core_defs.ServiceDef(
                service_id=srv_id,
                name=name,
                description=description,
                tags=tags,
                tenant=TEST_TENANT)

            self.assert_called_with_defs(
                update_call, [service_def, l4_entry, icmp_entry, ip_entry])


class TestPolicyCommunicationMap(NsxPolicyLibTestCase):

    def setUp(self, *args, **kwargs):
        super(TestPolicyCommunicationMap, self).setUp()
        self.resourceApi = self.policy_lib.comm_map
        self.mapDef = core_defs.CommunicationMapDef
        self.entryDef = core_defs.CommunicationMapEntryDef
        self.resource_type = 'SecurityPolicy'
        self.path_name = 'security-policies'

    def test_create_another(self):
        domain_id = '111'
        map_id = '222'
        name = 'cm1'
        description = 'desc'
        source_group = 'g1'
        dest_group = 'g2'
        seq_num = 7
        map_seq_num = 10
        service_id = 'c1'
        direction = nsx_constants.IN_OUT
        get_return_value = {'rules': [{'sequence_number': 1}]}
        with mock.patch.object(self.policy_api,
                               "create_with_parent") as api_call,\
            mock.patch.object(self.policy_api, "get",
                              return_value=get_return_value):
            result = self.resourceApi.create_or_overwrite(
                name, domain_id,
                map_id=map_id,
                description=description,
                sequence_number=seq_num,
                service_ids=[service_id],
                source_groups=[source_group],
                dest_groups=[dest_group],
                direction=direction,
                logged=True,
                map_sequence_number=map_seq_num,
                tenant=TEST_TENANT)
            map_def = self.mapDef(
                domain_id=domain_id,
                map_id=map_id,
                name=name,
                description=description,
                category=constants.CATEGORY_APPLICATION,
                map_sequence_number=map_seq_num,
                tenant=TEST_TENANT)

            entry_def = self.entryDef(
                domain_id=domain_id,
                map_id=map_id,
                entry_id='entry',
                name=name,
                action=constants.ACTION_ALLOW,
                description=description,
                sequence_number=seq_num,
                service_ids=[service_id],
                source_groups=[source_group],
                dest_groups=[dest_group],
                direction=direction,
                logged=True,
                tenant=TEST_TENANT)
            self.assert_called_with_defs(api_call, [map_def, entry_def])
            self.assertEqual(map_id, result)

    def test_create_first_seqnum(self):
        domain_id = '111'
        map_id = '222'
        name = 'cm1'
        description = 'desc'
        source_group = 'g1'
        dest_group = 'g2'
        service_id = 'c1'
        category = 'Emergency'
        get_return_value = {'rules': []}
        with mock.patch.object(self.policy_api,
                               "create_with_parent") as api_call, \
            mock.patch.object(self.resourceApi, "get",
                              return_value=get_return_value):
            result = self.resourceApi.create_or_overwrite(
                name, domain_id,
                map_id=map_id,
                description=description,
                service_ids=[service_id],
                source_groups=[source_group],
                dest_groups=[dest_group],
                category=category,
                logged=False,
                tenant=TEST_TENANT)

            map_def = self.mapDef(
                domain_id=domain_id,
                map_id=map_id,
                name=name,
                description=description,
                category=category,
                tenant=TEST_TENANT)

            entry_def = self.entryDef(
                domain_id=domain_id,
                map_id=map_id,
                entry_id='entry',
                name=name,
                action=constants.ACTION_ALLOW,
                direction=nsx_constants.IN_OUT,
                description=description,
                sequence_number=1,
                service_ids=[service_id],
                source_groups=[source_group],
                dest_groups=[dest_group],
                logged=False,
                tenant=TEST_TENANT)
            self.assert_called_with_defs(api_call, [map_def, entry_def])
            self.assertEqual(map_id, result)

    def test_create_without_seqnum(self):
        domain_id = '111'
        name = 'cm1'
        description = 'desc'
        source_group = 'g1'
        dest_group = 'g2'
        service1_id = 'c1'
        service2_id = 'c2'
        with mock.patch.object(self.policy_api,
                               "create_with_parent") as api_call:
            result = self.resourceApi.create_or_overwrite(
                name, domain_id,
                description=description,
                service_ids=[service1_id, service2_id],
                source_groups=[source_group],
                dest_groups=[dest_group],
                tenant=TEST_TENANT)

            expected_map_def = self.mapDef(
                domain_id=domain_id,
                map_id=mock.ANY,
                name=name,
                description=description,
                category=constants.CATEGORY_APPLICATION,
                tenant=TEST_TENANT)

            expected_entry_def = self.entryDef(
                domain_id=domain_id,
                map_id=mock.ANY,
                entry_id=mock.ANY,
                action=constants.ACTION_ALLOW,
                direction=nsx_constants.IN_OUT,
                name=name,
                description=description,
                sequence_number=1,
                service_ids=[service1_id, service2_id],
                source_groups=[source_group],
                dest_groups=[dest_group],
                tenant=TEST_TENANT)

            self.assert_called_with_defs(
                api_call,
                [expected_map_def, expected_entry_def])
            self.assertIsNotNone(result)

    def test_create_map_only(self):
        domain_id = '111'
        name = 'cm1'
        description = 'desc'
        map_seq_num = 10
        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            result = self.resourceApi.create_or_overwrite_map_only(
                name, domain_id, description=description,
                map_sequence_number=map_seq_num, tenant=TEST_TENANT)

            expected_map_def = self.mapDef(
                domain_id=domain_id,
                map_id=mock.ANY,
                name=name,
                description=description,
                category=constants.CATEGORY_APPLICATION,
                map_sequence_number=map_seq_num,
                tenant=TEST_TENANT)

            self.assert_called_with_def(api_call, expected_map_def)
            self.assertIsNotNone(result)

    def test_create_entry(self):
        domain_id = '111'
        map_id = '333'
        name = 'cm1'
        description = 'desc'
        source_group = 'g1'
        dest_group = 'g2'
        service1_id = 'c1'
        service2_id = 'c2'
        tag = 'abc1234'
        tags = ['dummy']
        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            result = self.resourceApi.create_entry(
                name=name,
                domain_id=domain_id,
                map_id=map_id,
                description=description,
                service_ids=[service1_id, service2_id],
                source_groups=[source_group],
                dest_groups=[dest_group],
                sequence_number=1,
                direction=nsx_constants.IN,
                ip_protocol=nsx_constants.IPV4,
                tag=tag, tags=tags,
                tenant=TEST_TENANT)

            expected_entry_def = self.entryDef(
                domain_id=domain_id,
                map_id=map_id,
                entry_id=mock.ANY,
                name=name,
                action=constants.ACTION_ALLOW,
                description=description,
                sequence_number=1,
                service_ids=[service1_id, service2_id],
                source_groups=[source_group],
                dest_groups=[dest_group],
                direction=nsx_constants.IN,
                ip_protocol=nsx_constants.IPV4,
                scope=None,
                logged=False,
                tag=tag,
                tags=tags,
                tenant=TEST_TENANT)

            self.assert_called_with_def(api_call, expected_entry_def)
            self.assertIsNotNone(result)

    def test_create_entry_no_service(self):
        domain_id = '111'
        map_id = '333'
        name = 'cm1'
        description = 'desc'
        source_group = 'g1'
        dest_group = 'g2'
        tag = 'abc1234'
        tags = ['abc1234']
        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            result = self.resourceApi.create_entry(
                name, domain_id, map_id,
                description=description,
                source_groups=[source_group],
                dest_groups=[dest_group],
                sequence_number=1,
                tag=tag, tags=tags,
                tenant=TEST_TENANT)

            expected_entry_def = self.entryDef(
                domain_id=domain_id,
                map_id=map_id,
                entry_id=mock.ANY,
                name=name,
                action=constants.ACTION_ALLOW,
                direction=nsx_constants.IN_OUT,
                ip_protocol=nsx_constants.IPV4_IPV6,
                description=description,
                sequence_number=1,
                service_ids=None,
                source_groups=[source_group],
                dest_groups=[dest_group],
                scope=None,
                logged=False,
                tag=tag,
                tags=tags,
                tenant=TEST_TENANT)

            self.assert_called_with_def(api_call, expected_entry_def)
            self.assertIsNotNone(result)

    def test_create_entry_no_seq_num(self):
        domain_id = '111'
        map_id = '333'
        name = 'cm1'
        description = 'desc'
        source_group = 'g1'
        dest_group = 'g2'
        service1_id = 'c1'
        service2_id = 'c2'
        seq_num = 1
        ret_comm = {'rules': [{'sequence_number': seq_num}]}
        tag = 'abc1234'
        tags = ['dummy']
        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call,\
            mock.patch.object(self.policy_api,
                              "get", return_value=ret_comm):
            result = self.resourceApi.create_entry(
                name, domain_id, map_id,
                description=description,
                service_ids=[service1_id, service2_id],
                source_groups=[source_group],
                dest_groups=[dest_group],
                logged=False,
                tag=tag, tags=tags,
                tenant=TEST_TENANT)

            expected_entry_def = self.entryDef(
                domain_id=domain_id,
                map_id=map_id,
                entry_id=mock.ANY,
                name=name,
                action=constants.ACTION_ALLOW,
                direction=nsx_constants.IN_OUT,
                ip_protocol=nsx_constants.IPV4_IPV6,
                description=description,
                service_ids=[service1_id, service2_id],
                source_groups=[source_group],
                dest_groups=[dest_group],
                sequence_number=seq_num + 1,
                scope=None,
                logged=False,
                tag=tag,
                tags=tags,
                tenant=TEST_TENANT)

            self.assert_called_with_def(api_call, expected_entry_def)
            self.assertIsNotNone(result)

    def test_create_with_entries(self):
        domain_id = '111'
        map_id = '222'
        name = 'cm1'
        description = 'desc'
        source_group = 'g1'
        dest_group = 'g2'
        service_id = 'c1'
        category = 'Emergency'
        ip_protocol = nsx_constants.IPV4
        map_seq_num = 10

        rule_id = 1
        entry1 = self.resourceApi.build_entry(
            'DHCP Reply', domain_id, map_id,
            rule_id, sequence_number=rule_id, service_ids=[service_id],
            action=constants.ACTION_DENY,
            source_groups=None,
            dest_groups=[dest_group],
            direction=nsx_constants.IN,
            ip_protocol=ip_protocol)
        self.assertEqual(rule_id, entry1.get_id())
        rule_id += 1
        entry2 = self.resourceApi.build_entry(
            'DHCP Request', domain_id, map_id,
            rule_id, sequence_number=rule_id, service_ids=None,
            action=constants.ACTION_DENY,
            source_groups=[source_group],
            dest_groups=None,
            direction=nsx_constants.OUT, ip_protocol=ip_protocol)
        self.assertEqual(rule_id, entry2.get_id())

        with mock.patch.object(self.policy_api,
                               "create_with_parent") as api_call:
            result = self.resourceApi.create_with_entries(
                name, domain_id,
                map_id=map_id,
                description=description,
                entries=[entry1, entry2],
                category=category,
                map_sequence_number=map_seq_num,
                tenant=TEST_TENANT)

            expected_def = self.mapDef(
                domain_id=domain_id,
                map_id=map_id,
                name=name,
                description=description,
                category=category,
                map_sequence_number=map_seq_num,
                tenant=TEST_TENANT)

            self.assert_called_with_defs(api_call,
                                         [expected_def, entry1, entry2])
            self.assertEqual(map_id, result)

    def test_create_with_entries_no_id(self):
        domain_id = '111'
        map_id = '222'
        name = 'cm1'
        description = 'desc'
        source_group = 'g1'
        dest_group = 'g2'
        service_id = 'c1'
        category = 'Emergency'
        ip_protocol = nsx_constants.IPV4
        map_seq_num = 10

        rule_id = 1
        entry1 = self.resourceApi.build_entry(
            'DHCP Reply', domain_id, map_id,
            sequence_number=rule_id, service_ids=[service_id],
            action=constants.ACTION_DENY,
            source_groups=None,
            dest_groups=[dest_group],
            direction=nsx_constants.IN,
            ip_protocol=ip_protocol)
        self.assertIsNotNone(entry1.get_id())
        rule_id += 1
        entry2 = self.resourceApi.build_entry(
            'DHCP Request', domain_id, map_id,
            sequence_number=rule_id, service_ids=None,
            action=constants.ACTION_DENY,
            source_groups=[source_group],
            dest_groups=None,
            direction=nsx_constants.OUT, ip_protocol=ip_protocol)
        self.assertIsNotNone(entry2.get_id())

        with mock.patch.object(self.policy_api,
                               "create_with_parent") as api_call:
            result = self.resourceApi.create_with_entries(
                name, domain_id,
                map_id=map_id,
                description=description,
                entries=[entry1, entry2],
                category=category,
                map_sequence_number=map_seq_num,
                tenant=TEST_TENANT)

            expected_def = self.mapDef(
                domain_id=domain_id,
                map_id=map_id,
                name=name,
                description=description,
                category=category,
                map_sequence_number=map_seq_num,
                tenant=TEST_TENANT)

            self.assert_called_with_defs(api_call,
                                         [expected_def, entry1, entry2])
            self.assertEqual(map_id, result)

    def test_delete(self):
        domain_id = '111'
        map_id = '222'
        with mock.patch.object(self.policy_api, "delete") as api_call:
            self.resourceApi.delete(domain_id, map_id, tenant=TEST_TENANT)
            expected_def = self.mapDef(
                domain_id=domain_id,
                map_id=map_id,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_delete_entry(self):
        domain_id = '111'
        map_id = '222'
        entry_id = '333'
        with mock.patch.object(self.policy_api, "delete") as api_call:
            self.resourceApi.delete_entry(domain_id, map_id, entry_id,
                                          tenant=TEST_TENANT)
            expected_def = self.entryDef(
                domain_id=domain_id,
                map_id=map_id,
                entry_id=entry_id,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_get(self):
        domain_id = '111'
        map_id = '222'
        with mock.patch.object(self.policy_api, "get",
                               return_value={'id': map_id}) as api_call:
            result = self.resourceApi.get(domain_id, map_id,
                                          tenant=TEST_TENANT)
            expected_def = self.mapDef(
                domain_id=domain_id,
                map_id=map_id,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(map_id, result['id'])

    def test_get_entry(self):
        domain_id = '111'
        map_id = '222'
        entry_id = '333'
        with mock.patch.object(self.policy_api, "get",
                               return_value={'id': entry_id}) as api_call:
            result = self.resourceApi.get_entry(domain_id, map_id,
                                                entry_id, tenant=TEST_TENANT)
            expected_def = self.entryDef(
                domain_id=domain_id,
                map_id=map_id,
                entry_id=entry_id,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(entry_id, result['id'])

    def test_get_by_name(self):
        domain_id = '111'
        name = 'cm1'
        with mock.patch.object(
            self.policy_api, "list",
            return_value={'results': [{'display_name': name}]}) as api_call:
            obj = self.resourceApi.get_by_name(domain_id, name,
                                               tenant=TEST_TENANT)
            self.assertIsNotNone(obj)
            expected_def = self.mapDef(
                domain_id=domain_id,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_list(self):
        domain_id = '111'
        with mock.patch.object(self.policy_api, "list",
                               return_value={'results': []}) as api_call:
            result = self.resourceApi.list(domain_id, tenant=TEST_TENANT)
            expected_def = self.mapDef(
                domain_id=domain_id,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual([], result)

    def test_update(self):
        domain_id = '111'
        map_id = '222'
        name = 'new name'
        description = 'new desc'
        source_group = 'ng1'
        dest_group = 'ng2'
        service1_id = 'nc1'
        service2_id = 'nc2'
        category = constants.CATEGORY_EMERGENCY
        with mock.patch.object(self.policy_api, "get",
                               return_value={}),\
            mock.patch.object(self.resourceApi, "get",
                              return_value={'category': category}),\
            mock.patch.object(self.policy_api,
                              "create_with_parent") as update_call:
            self.resourceApi.update(domain_id, map_id,
                                    name=name,
                                    description=description,
                                    service_ids=[service1_id, service2_id],
                                    source_groups=[source_group],
                                    dest_groups=[dest_group],
                                    tenant=TEST_TENANT)
            map_def = self.mapDef(
                domain_id=domain_id,
                map_id=map_id,
                name=name,
                description=description,
                category=category,
                tenant=TEST_TENANT)

            entry_def = self.entryDef(
                domain_id=domain_id,
                map_id=map_id,
                entry_id='entry',
                service_ids=[service1_id, service2_id],
                source_groups=[source_group],
                dest_groups=[dest_group],
                tenant=TEST_TENANT)

            self.assert_called_with_defs(update_call, [map_def, entry_def])

    def test_update_entry(self):
        domain_id = '111'
        map_id = '222'
        entry_id = 'entry'
        name = 'new name'
        description = 'new desc'
        source_group = 'ng1'
        dest_group = 'ng2'
        service1_id = 'nc1'
        service2_id = 'nc2'
        with mock.patch.object(self.policy_api, "get",
                               return_value={}),\
            mock.patch.object(self.policy_api,
                              "create_or_update") as update_call:
            self.resourceApi.update_entry(
                domain_id, map_id, entry_id,
                name=name,
                description=description,
                service_ids=[service1_id, service2_id],
                source_groups=[source_group],
                dest_groups=[dest_group],
                tenant=TEST_TENANT)

            entry_def = self.entryDef(
                domain_id=domain_id,
                map_id=map_id,
                entry_id=entry_id,
                name=name,
                description=description,
                service_ids=[service1_id, service2_id],
                source_groups=[source_group],
                dest_groups=[dest_group],
                tenant=TEST_TENANT)

            self.assert_called_with_def(update_call, entry_def)

    def test_update_entries(self):
        domain_id = '111'
        map_id = '222'
        entries = "fake_entries"
        with mock.patch.object(self.resourceApi,
                               "update_with_entries") as update_call:
            self.resourceApi.update_entries(
                domain_id, map_id, entries, tenant=TEST_TENANT)
            update_call.assert_called_once_with(
                domain_id, map_id, entries,
                category=constants.CATEGORY_APPLICATION,
                use_child_rules=True,
                tenant=TEST_TENANT)

    def test_update_with_entries(self):
        domain_id = '111'
        map_id = '222'
        entry1_id = 'entry1'
        entry2_id = 'entry2'
        entry3_id = 'entry3'
        entry1 = self.entryDef(
            domain_id=domain_id,
            map_id=map_id,
            entry_id=entry1_id,
            scope=['new_scope1'],
            tenant=TEST_TENANT)
        entry2 = self.entryDef(
            domain_id=domain_id,
            map_id=map_id,
            entry_id=entry2_id,
            scope=['scope2'],
            tenant=TEST_TENANT)
        original_map = {
            'id': map_id,
            'resource_type': self.resource_type,
            'category': constants.CATEGORY_APPLICATION,
            'display_name': 'map_name',
            'rules': [
                {'id': entry1_id, 'resource_type': 'Rule',
                 'display_name': 'name1', 'scope': ['scope1']},
                {'id': entry2_id, 'resource_type': 'Rule',
                 'display_name': 'name2', 'scope': ['scope2']},
                {'id': entry3_id, 'resource_type': 'Rule',
                 'display_name': 'name3', 'scope': ['scope3']}]}
        updated_map = {
            'id': map_id,
            'resource_type': self.resource_type,
            'category': constants.CATEGORY_APPLICATION,
            'display_name': 'new_map_name',
            'rules': [
                {'id': entry1_id, 'resource_type': 'Rule',
                 'display_name': 'name1', 'scope': ['new_scope1']},
                {'id': entry2_id, 'resource_type': 'Rule',
                 'display_name': 'name2', 'scope': ['scope2']}]}
        map_def = self.mapDef(
            domain_id=domain_id,
            map_id=map_id,
            tenant=TEST_TENANT)
        with mock.patch.object(self.policy_api, "get",
                               return_value=original_map),\
            mock.patch.object(self.policy_api.client,
                              "update") as update_call:
            self.resourceApi.update_with_entries(
                domain_id, map_id, entries=[entry1, entry2],
                name='new_map_name', tenant=TEST_TENANT)
            update_call.assert_called_once_with(
                map_def.get_resource_path(), updated_map)

    def test_update_with_entries_for_IGNORE_entries(self):
        domain_id = '111'
        map_id = '222'
        entry1_id = 'entry1'
        entry2_id = 'entry2'
        entry3_id = 'entry3'
        original_map = {
            'id': map_id,
            'resource_type': self.resource_type,
            'category': constants.CATEGORY_APPLICATION,
            'display_name': 'map_name',
            'rules': [
                {'id': entry1_id, 'resource_type': 'Rule',
                 'display_name': 'name1', 'scope': ['scope1'],
                 '_created_time': 1},
                {'id': entry2_id, 'resource_type': 'Rule',
                 'display_name': 'name2', 'scope': ['scope2']},
                {'id': entry3_id, 'resource_type': 'Rule',
                 'display_name': 'name3', 'scope': ['scope3']}]}
        updated_map = {
            'id': map_id,
            'resource_type': self.resource_type,
            'category': constants.CATEGORY_APPLICATION,
            'display_name': 'new_map_name',
            'rules': [
                {'id': entry1_id, 'resource_type': 'Rule',
                 'display_name': 'name1', 'scope': ['scope1'],
                 '_created_time': 1},
                {'id': entry2_id, 'resource_type': 'Rule',
                 'display_name': 'name2', 'scope': ['scope2']},
                {'id': entry3_id, 'resource_type': 'Rule',
                 'display_name': 'name3', 'scope': ['scope3']}]}
        map_def = self.mapDef(
            domain_id=domain_id,
            map_id=map_id,
            tenant=TEST_TENANT)
        with mock.patch.object(self.policy_api, "get",
                               return_value=original_map),\
            mock.patch.object(self.policy_api.client,
                              "update") as update_call:
            self.resourceApi.update_with_entries(
                domain_id, map_id, name='new_map_name', tenant=TEST_TENANT)
            update_call.assert_called_once_with(
                map_def.get_resource_path(), updated_map)

    def test_unset(self):
        name = 'hello'
        domain_id = 'test'
        map_id = '111'
        dest_groups = ['/infra/stuff']
        category = constants.CATEGORY_EMERGENCY

        # Until policy PATCH is fixed to accept partial update, we
        # call get on child entry
        with mock.patch.object(
            self.policy_api, "get",
            return_value={'display_name': name,
                          'source_groups': ['/infra/other/stuff'],
                          'destination_groups': dest_groups}),\
            mock.patch.object(self.resourceApi, "get",
                              return_value={'category': category}):
            self.resourceApi.update(domain_id, map_id,
                                    description=None,
                                    source_groups=None,
                                    service_ids=None,
                                    tenant=TEST_TENANT)

        expected_body = {'id': map_id,
                         'description': None,
                         'category': category,
                         'resource_type': self.resource_type,
                         'rules': [{
                             'display_name': name,
                             'id': 'entry',
                             'resource_type': 'Rule',
                             'services': ["ANY"],
                             'source_groups': ["ANY"],
                             'destination_groups': dest_groups}]
                         }

        url = '%s/domains/%s/%s/%s' % (TEST_TENANT,
                                       domain_id,
                                       self.path_name,
                                       map_id)
        self.assert_json_call('PATCH', self.client, url, data=expected_body)

    def test_update_entries_logged(self):
        domain_id = '111'
        map_id = '222'
        dummy_map = {'rules': [{'logged': False}]}
        updated_map = {'rules': [{'logged': True}]}
        map_def = self.mapDef(
            domain_id=domain_id,
            map_id=map_id,
            tenant=TEST_TENANT)
        with mock.patch.object(self.policy_api, "get",
                               return_value=dummy_map),\
            mock.patch.object(self.policy_api.client,
                              "update") as update_call:
            self.resourceApi.update_entries_logged(
                domain_id, map_id,
                logged=True,
                tenant=TEST_TENANT)
            update_call.assert_called_once_with(
                map_def.get_resource_path(), updated_map)

    def test_get_realized(self):
        domain_id = 'd1'
        map_id = '111'
        result = [{'state': constants.STATE_REALIZED,
                   'entity_type': 'RealizedFirewallSection'}]
        with mock.patch.object(
            self.policy_api, "get_realized_entities",
            return_value=result) as api_get:
            state = self.resourceApi.get_realized_state(
                domain_id, map_id, tenant=TEST_TENANT)
            self.assertEqual(constants.STATE_REALIZED, state)
            path = "/%s/domains/%s/%s/%s" % (
                TEST_TENANT, domain_id, self.path_name, map_id)
            api_get.assert_called_once_with(path, silent=False)


class TestPolicyGatewayPolicy(TestPolicyCommunicationMap):

    def setUp(self, *args, **kwargs):
        super(TestPolicyGatewayPolicy, self).setUp()
        self.resourceApi = self.policy_lib.gateway_policy
        self.mapDef = core_defs.GatewayPolicyDef
        self.entryDef = core_defs.GatewayPolicyRuleDef
        self.resource_type = 'GatewayPolicy'
        self.path_name = 'gateway-policies'

    def test_build_entry(self):
        domain_id = '111'
        map_id = '222'
        name = 'rule1'
        desc = 'desc'
        dest_group = 'g1'
        service_id = 's1'
        policy_id = 'policy1'
        ip_protocol = nsx_constants.IPV4
        rule_id = 1
        entry1 = self.resourceApi.build_entry(
            name, domain_id, map_id, entry_id=rule_id, description=desc,
            sequence_number=rule_id, service_ids=[service_id],
            action=constants.ACTION_DENY,
            scope=policy_id,
            source_groups=None, dest_groups=[dest_group],
            direction=nsx_constants.IN,
            ip_protocol=ip_protocol)
        expected_dict1 = {
            'display_name': 'rule1',
            'id': 1,
            'description': 'desc',
            'resource_type': 'Rule',
            'scope': 'policy1',
            'ip_protocol': 'IPV4',
            'sequence_number': 1,
            'action': 'DROP',
            'source_groups': ['ANY'],
            'destination_groups': ['/infra/domains/111/groups/g1'],
            'direction': 'IN',
            'logged': False,
            'services': ['/infra/services/s1'],
            'tag': None}
        self.assertEqual(entry1.get_obj_dict(), expected_dict1)

        entry2 = self.resourceApi.build_entry(
            name, domain_id, map_id, entry_id=rule_id, description=desc,
            sequence_number=rule_id, service_ids=[service_id],
            action=constants.ACTION_DENY,
            scope=policy_id,
            dest_groups=[dest_group],
            direction=nsx_constants.IN,
            ip_protocol=ip_protocol,
            plain_groups=True)
        expected_dict2 = {
            'display_name': 'rule1',
            'id': 1,
            'description': 'desc',
            'resource_type': 'Rule',
            'scope': 'policy1',
            'ip_protocol': 'IPV4',
            'sequence_number': 1,
            'action': 'DROP',
            'source_groups': ['ANY'],
            'destination_groups': ['g1'],
            'direction': 'IN',
            'logged': False,
            'services': ['/infra/services/s1'],
            'tag': None}
        self.assertEqual(entry2.get_obj_dict(), expected_dict2)

        with mock.patch.object(self.resourceApi, 'version', '0.0.0'):
            self.assertRaises(nsxlib_exc.NsxLibInvalidInput,
                              self.resourceApi.build_entry,
                              name, domain_id, map_id, entry_id=rule_id,
                              description=desc, sequence_number=rule_id,
                              service_ids=[service_id], scope=policy_id,
                              dest_groups=[dest_group], plain_groups=True)

    def test_get_realized(self):
        domain_id = 'd1'
        map_id = '111'
        result = [{'state': constants.STATE_REALIZED,
                   'entity_type': 'RealizedFirewallSection'}]
        with mock.patch.object(
            self.policy_api, "get_realized_entities",
            return_value=result) as api_get:
            state = self.resourceApi.get_realized_state(
                domain_id, map_id, tenant=TEST_TENANT)
            self.assertEqual(constants.STATE_REALIZED, state)
            path = "/%s/domains/%s/%s/%s" % (
                TEST_TENANT, domain_id, self.path_name, map_id)
            api_get.assert_called_once_with(path, silent=False)

    def test_wait_until_realized_failed(self):
        domain_id = 'd1'
        map_id = '111'
        gw_section_id = 'realized_111'
        info = {'state': constants.STATE_UNREALIZED,
                'realization_specific_identifier': gw_section_id}
        with mock.patch.object(self.resourceApi, "_get_realization_info",
                               return_value=info):
            self.assertRaises(nsxlib_exc.RealizationTimeoutError,
                              self.resourceApi.wait_until_realized,
                              domain_id, map_id, tenant=TEST_TENANT,
                              max_attempts=5, sleep=0.1)

    def test_wait_until_state_sucessful_with_error(self):
        domain_id = 'd1'
        map_id = '111'
        info = {'consolidated_status': {'consolidated_status': 'ERROR'}}
        with mock.patch.object(self.resourceApi.policy_api,
                               "get_intent_consolidated_status",
                               return_value=info):
            self.assertRaises(nsxlib_exc.RealizationErrorStateError,
                              self.resourceApi.wait_until_state_sucessful,
                              domain_id, map_id, tenant=TEST_TENANT,
                              max_attempts=5, sleep=0.1)

    def test_wait_until_state_sucessful(self):
        domain_id = 'd1'
        map_id = '111'
        info = {'consolidated_status': {'consolidated_status': 'SUCCESS'}}
        with mock.patch.object(self.resourceApi.policy_api,
                               "get_intent_consolidated_status",
                               return_value=info):
            self.resourceApi.wait_until_state_sucessful(
                domain_id, map_id, tenant=TEST_TENANT,
                max_attempts=5, sleep=0.1)


class TestPolicyEnforcementPoint(NsxPolicyLibTestCase):

    def setUp(self, *args, **kwargs):
        super(TestPolicyEnforcementPoint, self).setUp()
        self.resourceApi = self.policy_lib.enforcement_point

    def test_create(self):
        name = 'ep'
        description = 'desc'
        ip_address = '1.1.1.1'
        username = 'admin'
        password = 'zzz'
        thumbprint = 'abc'
        edge_cluster_id = 'ec1'
        transport_zone_id = 'tz1'
        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            result = self.resourceApi.create_or_overwrite(
                name, description=description,
                ip_address=ip_address,
                thumbprint=thumbprint,
                username=username,
                password=password,
                edge_cluster_id=edge_cluster_id,
                transport_zone_id=transport_zone_id,
                tenant=TEST_TENANT)

            expected_def = core_defs.EnforcementPointDef(
                ep_id=mock.ANY,
                name=name,
                description=description,
                ip_address=ip_address,
                username=username,
                thumbprint=thumbprint,
                password=password,
                edge_cluster_id=edge_cluster_id,
                transport_zone_id=transport_zone_id,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertIsNotNone(result)

    def test_delete(self):
        ef_id = '111'
        with mock.patch.object(self.policy_api, "delete") as api_call:
            self.resourceApi.delete(ef_id, tenant=TEST_TENANT)
            expected_def = core_defs.EnforcementPointDef(ep_id=ef_id,
                                                         tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_get(self):
        ef_id = '111'
        with mock.patch.object(self.policy_api, "get",
                               return_value={'id': ef_id}) as api_call:
            result = self.resourceApi.get(ef_id, tenant=TEST_TENANT)
            expected_def = core_defs.EnforcementPointDef(ep_id=ef_id,
                                                         tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(ef_id, result['id'])

    def test_get_by_name(self):
        name = 'ep1'
        with mock.patch.object(
            self.policy_api, "list",
            return_value={'results': [{'display_name': name}]}) as api_call:
            obj = self.resourceApi.get_by_name(name, tenant=TEST_TENANT)
            self.assertIsNotNone(obj)
            expected_def = core_defs.EnforcementPointDef(tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_list(self):
        with mock.patch.object(self.policy_api, "list",
                               return_value={'results': []}) as api_call:
            result = self.resourceApi.list(tenant=TEST_TENANT)
            expected_def = core_defs.EnforcementPointDef(tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual([], result)

    def test_update(self):
        ef_id = '111'
        name = 'new name'
        username = 'admin'
        password = 'zzz'
        ip_address = '1.1.1.1'
        thumbprint = 'abc'
        edge_cluster_id = 'ec1'
        transport_zone_id = 'tz1'
        entry = {'id': ef_id,
                 'connection_info': {'thumbprint': thumbprint,
                                     'resource_type': 'NSXTConnectionInfo'}}

        with mock.patch.object(self.policy_api,
                               "create_or_update") as update_call,\
            mock.patch.object(self.policy_api, "get",
                              return_value=entry):
            self.resourceApi.update(ef_id,
                                    name=name,
                                    username=username,
                                    password=password,
                                    ip_address=ip_address,
                                    edge_cluster_id=edge_cluster_id,
                                    transport_zone_id=transport_zone_id,
                                    tenant=TEST_TENANT)
            expected_def = core_defs.EnforcementPointDef(
                ep_id=ef_id,
                name=name,
                username=username,
                password=password,
                ip_address=ip_address,
                thumbprint=thumbprint,
                edge_cluster_id=edge_cluster_id,
                transport_zone_id=transport_zone_id,
                tenant=TEST_TENANT)

            self.assert_called_with_def(update_call, expected_def)

    def test_get_realized(self):
        ep_id = 'ef1'
        result = [{'state': constants.STATE_REALIZED}]
        with mock.patch.object(
            self.policy_api, "get_realized_entities",
            return_value=result) as api_get:
            state = self.resourceApi.get_realized_state(
                ep_id, tenant=TEST_TENANT)
            self.assertEqual(constants.STATE_REALIZED, state)
            path = "/%s/sites/default/enforcement-points/%s" % (
                TEST_TENANT, ep_id)
            api_get.assert_called_once_with(path, silent=False)

    def test_reload(self):
        ef_id = '111'
        with mock.patch.object(self.policy_api.client, "url_post") as api_post:
            self.resourceApi.reload(ef_id, tenant=TEST_TENANT)
            expected_def = core_defs.EnforcementPointDef(ep_id=ef_id,
                                                         tenant=TEST_TENANT)
            api_post.assert_called_once_with(
                expected_def.get_resource_path() + '?action=reload',
                None, expected_results=None, headers=None)


class TestPolicyDeploymentMap(NsxPolicyLibTestCase):

    def setUp(self, *args, **kwargs):
        super(TestPolicyDeploymentMap, self).setUp()
        self.resourceApi = self.policy_lib.deployment_map

    def test_create(self):
        name = 'map1'
        description = 'desc'
        domain_id = 'domain1'
        ep_id = 'ep1'
        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            result = self.resourceApi.create_or_overwrite(
                name,
                description=description,
                ep_id=ep_id,
                domain_id=domain_id,
                tenant=TEST_TENANT)
            expected_def = core_defs.DeploymentMapDef(
                map_id=mock.ANY,
                name=name,
                description=description,
                ep_id=ep_id,
                domain_id=domain_id,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertIsNotNone(result)

    def test_delete(self):
        obj_id = '111'
        domain_id = 'domain1'
        with mock.patch.object(self.policy_api, "delete") as api_call:
            self.resourceApi.delete(obj_id, domain_id=domain_id,
                                    tenant=TEST_TENANT)
            expected_def = core_defs.DeploymentMapDef(map_id=obj_id,
                                                      domain_id=domain_id,
                                                      tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_get(self):
        obj_id = '111'
        domain_id = 'domain1'
        with mock.patch.object(self.policy_api, "get",
                               return_value={'id': obj_id}) as api_call:
            result = self.resourceApi.get(obj_id, domain_id=domain_id,
                                          tenant=TEST_TENANT)
            expected_def = core_defs.DeploymentMapDef(map_id=obj_id,
                                                      domain_id=domain_id,
                                                      tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(obj_id, result['id'])

    def test_get_by_name(self):
        name = 'ep1'
        domain_id = 'domain1'
        with mock.patch.object(
            self.policy_api, "list",
            return_value={'results': [{'display_name': name}]}) as api_call:
            obj = self.resourceApi.get_by_name(name, domain_id=domain_id,
                                               tenant=TEST_TENANT)
            self.assertIsNotNone(obj)
            expected_def = core_defs.DeploymentMapDef(domain_id=domain_id,
                                                      tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_list(self):
        domain_id = 'domain1'
        with mock.patch.object(self.policy_api, "list",
                               return_value={'results': []}) as api_call:
            result = self.resourceApi.list(domain_id=domain_id,
                                           tenant=TEST_TENANT)
            expected_def = core_defs.DeploymentMapDef(domain_id=domain_id,
                                                      tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual([], result)

    def test_update(self):
        obj_id = '111'
        name = 'new name'
        domain_id = 'domain2'
        ep_id = 'ep2'
        with self.mock_get(domain_id, name), \
            self.mock_create_update() as update_call:
            self.resourceApi.update(obj_id,
                                    name=name,
                                    ep_id=ep_id,
                                    domain_id=domain_id,
                                    tenant=TEST_TENANT)
            expected_def = core_defs.DeploymentMapDef(
                map_id=obj_id,
                name=name,
                ep_id=ep_id,
                domain_id=domain_id,
                tenant=TEST_TENANT)
            self.assert_called_with_def(
                update_call, expected_def)


class TestPolicyTransportZone(NsxPolicyLibTestCase):

    def setUp(self, *args, **kwargs):
        super(TestPolicyTransportZone, self).setUp()
        self.resourceApi = self.policy_lib.transport_zone

    def test_get(self):
        obj_id = '111'
        with mock.patch.object(self.policy_api, "get",
                               return_value={'id': obj_id}) as api_call:
            result = self.resourceApi.get(obj_id, tenant=TEST_TENANT)
            expected_def = core_defs.TransportZoneDef(tz_id=obj_id,
                                                      tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(obj_id, result['id'])

    def test_get_with_cache(self):
        """Verify that cache is used for GET"""
        obj_id = '111'
        with mock.patch.object(self.policy_api.client, "get") as client_get:
            self.resourceApi.get(obj_id, tenant=TEST_TENANT)
            self.resourceApi.get(obj_id, tenant=TEST_TENANT)
            self.assertEqual(1, client_get.call_count)

    def test_get_by_name(self):
        name = 'tz1'
        with mock.patch.object(
            self.policy_api, "list",
            return_value={'results': [{'display_name': name}]}) as api_call:
            obj = self.resourceApi.get_by_name(name, tenant=TEST_TENANT)
            self.assertIsNotNone(obj)
            expected_def = core_defs.TransportZoneDef(tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_get_tz_type(self):
        obj_id = '111'
        tz_type = self.resourceApi.TZ_TYPE_OVERLAY
        with mock.patch.object(self.policy_api, "get",
                               return_value={'tz_type': tz_type}) as api_call:
            actual_tz_type = self.resourceApi.get_tz_type(
                obj_id, tenant=TEST_TENANT)
            expected_def = core_defs.TransportZoneDef(tz_id=obj_id,
                                                      tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(tz_type, actual_tz_type)

    def test_get_transport_type(self):
        obj_id = '111'
        tz_type = self.resourceApi.TZ_TYPE_OVERLAY
        with mock.patch.object(self.policy_api, "get",
                               return_value={'tz_type': tz_type}) as api_call:
            actual_tz_type = self.resourceApi.get_transport_type(
                obj_id, tenant=TEST_TENANT)
            expected_def = core_defs.TransportZoneDef(tz_id=obj_id,
                                                      tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(nsx_constants.TRANSPORT_TYPE_OVERLAY,
                             actual_tz_type)

    def test_get_switch_mode(self):
        obj_id = '111'
        tz_type = self.resourceApi.TZ_TYPE_OVERLAY
        with mock.patch.object(self.policy_api, "get",
                               return_value={'tz_type': tz_type}) as api_call:
            actual_sm = self.resourceApi.get_host_switch_mode(
                obj_id, tenant=TEST_TENANT)
            expected_def = core_defs.TransportZoneDef(tz_id=obj_id,
                                                      tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(nsx_constants.HOST_SWITCH_MODE_STANDARD,
                             actual_sm)

    def test_list(self):
        with mock.patch.object(self.policy_api, "list",
                               return_value={'results': []}) as api_call:
            result = self.resourceApi.list(tenant=TEST_TENANT)
            expected_def = core_defs.TransportZoneDef(tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual([], result)


class TestPolicyEdgeCluster(NsxPolicyLibTestCase):

    def setUp(self, *args, **kwargs):
        super(TestPolicyEdgeCluster, self).setUp()
        self.resourceApi = self.policy_lib.edge_cluster

    def test_get(self):
        obj_id = '111'
        with mock.patch.object(self.policy_api, "get",
                               return_value={'id': obj_id}) as api_call:
            result = self.resourceApi.get(obj_id, tenant=TEST_TENANT)
            expected_def = core_defs.EdgeClusterDef(ec_id=obj_id,
                                                    tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(obj_id, result['id'])

    def test_get_by_name(self):
        name = 'tz1'
        with mock.patch.object(
            self.policy_api, "list",
            return_value={'results': [{'display_name': name}]}) as api_call:
            obj = self.resourceApi.get_by_name(name, tenant=TEST_TENANT)
            self.assertIsNotNone(obj)
            expected_def = core_defs.EdgeClusterDef(tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_list(self):
        with mock.patch.object(self.policy_api, "list",
                               return_value={'results': []}) as api_call:
            result = self.resourceApi.list(tenant=TEST_TENANT)
            expected_def = core_defs.EdgeClusterDef(tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual([], result)

    def test_get_nodes(self):
        obj_id = '111'
        node_id = 'node1'
        with mock.patch.object(
            self.policy_api, "list",
            return_value={'results': [{'id': node_id}]}) as api_call:
            result = self.resourceApi.get_edge_node_ids(
                obj_id, tenant=TEST_TENANT)
            expected_def = core_defs.EdgeClusterNodeDef(
                ec_id=obj_id, tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual([node_id], result)

    def test_get_nodes_nsx_ids(self):
        obj_id = '111'
        node_id = 'node1'
        node_nsx_id = 'nsx1'
        with mock.patch.object(
            self.policy_api, "list",
            return_value={'results': [{'id': node_id,
                                       'nsx_id': node_nsx_id}]}) as api_call:
            result = self.resourceApi.get_edge_node_nsx_ids(
                obj_id, tenant=TEST_TENANT)
            expected_def = core_defs.EdgeClusterNodeDef(
                ec_id=obj_id, tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual([node_nsx_id], result)


class TestPolicyMetadataProxy(NsxPolicyLibTestCase):

    def setUp(self, *args, **kwargs):
        super(TestPolicyMetadataProxy, self).setUp()
        self.resourceApi = self.policy_lib.md_proxy

    def test_get(self):
        obj_id = '111'
        with mock.patch.object(self.policy_api, "get",
                               return_value={'id': obj_id}) as api_call:
            result = self.resourceApi.get(obj_id, tenant=TEST_TENANT)
            expected_def = core_defs.MetadataProxyDef(mdproxy_id=obj_id,
                                                      tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(obj_id, result['id'])

    def test_get_by_name(self):
        name = 'tz1'
        with mock.patch.object(
            self.policy_api, "list",
            return_value={'results': [{'display_name': name}]}) as api_call:
            obj = self.resourceApi.get_by_name(name, tenant=TEST_TENANT)
            self.assertIsNotNone(obj)
            expected_def = core_defs.MetadataProxyDef(tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_list(self):
        with mock.patch.object(self.policy_api, "list",
                               return_value={'results': []}) as api_call:
            result = self.resourceApi.list(tenant=TEST_TENANT)
            expected_def = core_defs.MetadataProxyDef(tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual([], result)


class TestPolicyTier1(NsxPolicyLibTestCase):

    def setUp(self, *args, **kwargs):
        super(TestPolicyTier1, self).setUp(*args, **kwargs)
        self.resourceApi = self.policy_lib.tier1
        self.partial_updates = True

    def test_create(self):
        name = 'test'
        description = 'desc'
        tier0_id = '111'
        pool_alloc_type = 'LB_SMALL'
        route_adv = self.resourceApi.build_route_advertisement(
            lb_vip=True,
            lb_snat=True)
        ipv6_profile_id = '222'

        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            result = self.resourceApi.create_or_overwrite(
                name, description=description,
                tier0=tier0_id,
                force_whitelisting=True,
                route_advertisement=route_adv,
                pool_allocation=pool_alloc_type,
                ipv6_ndra_profile_id=ipv6_profile_id,
                tenant=TEST_TENANT)

            expected_def = core_defs.Tier1Def(
                nsx_version=self.policy_lib.get_version(),
                tier1_id=mock.ANY,
                name=name,
                description=description,
                tier0=tier0_id,
                force_whitelisting=True,
                failover_mode=constants.NON_PREEMPTIVE,
                route_advertisement=route_adv,
                pool_allocation=pool_alloc_type,
                ipv6_ndra_profile_id=ipv6_profile_id,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertIsNotNone(result)

    def test_create_no_ipv6_profile(self):
        name = 'test'
        description = 'desc'
        tier0_id = '111'
        pool_alloc_type = 'LB_SMALL'
        route_adv = self.resourceApi.build_route_advertisement(
            lb_vip=True,
            lb_snat=True)

        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            result = self.resourceApi.create_or_overwrite(
                name, description=description,
                tier0=tier0_id,
                force_whitelisting=True,
                route_advertisement=route_adv,
                pool_allocation=pool_alloc_type,
                ipv6_ndra_profile_id=None,
                tenant=TEST_TENANT)

            expected_def = core_defs.Tier1Def(
                nsx_version=self.policy_lib.get_version(),
                tier1_id=mock.ANY,
                name=name,
                description=description,
                tier0=tier0_id,
                force_whitelisting=True,
                failover_mode=constants.NON_PREEMPTIVE,
                route_advertisement=route_adv,
                pool_allocation=pool_alloc_type,
                ipv6_ndra_profile_id=None,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertIsNotNone(result)

    def test_delete(self):
        obj_id = '111'
        with mock.patch.object(self.policy_api, "delete") as api_call:
            self.resourceApi.delete(obj_id, tenant=TEST_TENANT)
            expected_def = core_defs.Tier1Def(tier1_id=obj_id,
                                              tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_get(self):
        obj_id = '111'
        with mock.patch.object(self.policy_api, "get",
                               return_value={'id': obj_id}) as api_call:
            result = self.resourceApi.get(obj_id, tenant=TEST_TENANT)
            expected_def = core_defs.Tier1Def(tier1_id=obj_id,
                                              tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(obj_id, result['id'])

    def test_get_path(self):
        obj_id = '111'
        result = self.resourceApi.get_path(obj_id, tenant=TEST_TENANT)
        self.assertEqual('/%s/tier-1s/%s' % (TEST_TENANT, obj_id), result)

    def test_get_with_no_cache(self):
        """Make sure cache is not used for GET requests"""
        obj_id = '111'
        with mock.patch.object(self.policy_api.client, "get") as client_get:
            self.resourceApi.get(obj_id, tenant=TEST_TENANT)
            self.resourceApi.get(obj_id, tenant=TEST_TENANT)
            self.assertEqual(2, client_get.call_count)

    def test_get_by_name(self):
        name = 'test'
        with mock.patch.object(
            self.policy_api, "list",
            return_value={'results': [{'display_name': name}]}) as api_call:
            obj = self.resourceApi.get_by_name(name, tenant=TEST_TENANT)
            self.assertIsNotNone(obj)
            expected_def = core_defs.Tier1Def(tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_list(self):
        with mock.patch.object(self.policy_api, "list",
                               return_value={'results': []}) as api_call:
            result = self.resourceApi.list(tenant=TEST_TENANT)
            expected_def = core_defs.Tier1Def(tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual([], result)

    def test_update(self):
        obj_id = '111'
        name = 'new name'
        tier0 = 'tier0'
        pool_alloc_type = 'LB_SMALL'
        with self.mock_get(obj_id, name), \
            self.mock_create_update() as update_call:
            self.resourceApi.update(obj_id,
                                    name=name, tier0=tier0,
                                    enable_standby_relocation=False,
                                    pool_allocation=pool_alloc_type,
                                    tenant=TEST_TENANT)
            expected_def = core_defs.Tier1Def(
                nsx_version=self.policy_lib.get_version(),
                tier1_id=obj_id,
                name=name,
                tier0=tier0,
                enable_standby_relocation=False,
                pool_allocation=pool_alloc_type,
                tenant=TEST_TENANT)
            self.assert_called_with_def(
                update_call, expected_def)

    def test_update_ignore_tier0(self):
        obj_id = '111'
        name = 'new name'
        with mock.patch.object(self.policy_api, "get",
                               return_value={}),\
            mock.patch.object(self.policy_api,
                              "create_or_update") as update_call:
            self.resourceApi.update(obj_id,
                                    name=name,
                                    enable_standby_relocation=False,
                                    tenant=TEST_TENANT)
            expected_def = core_defs.Tier1Def(tier1_id=obj_id,
                                              name=name,
                                              enable_standby_relocation=False,
                                              tenant=TEST_TENANT)
            self.assert_called_with_def(update_call, expected_def)
            # make sure tier0 is not in the body
            actual_def = update_call.call_args_list[0][0][0]
            self.assertNotIn('tier0_path', actual_def.get_obj_dict())

    def test_update_unset_tier0(self):
        obj_id = '111'
        name = 'new name'
        description = 'abc'
        with mock.patch.object(self.policy_api, "get",
                               return_value={}),\
            mock.patch.object(self.policy_api,
                              "create_or_update") as update_call:
            self.resourceApi.update(obj_id,
                                    name=name,
                                    description=description,
                                    tier0=None,
                                    enable_standby_relocation=False,
                                    tenant=TEST_TENANT)
            expected_def = core_defs.Tier1Def(tier1_id=obj_id,
                                              name=name,
                                              description=description,
                                              tier0=None,
                                              enable_standby_relocation=False,
                                              tenant=TEST_TENANT)
            self.assert_called_with_def(update_call, expected_def)
            # make sure tier0 is in the body with value None
            actual_def = update_call.call_args_list[0][0][0]
            self.assertIn('tier0_path', actual_def.get_obj_dict())
            self.assertEqual("", actual_def.get_obj_dict()['tier0_path'])

    def test_update_route_adv(self):
        obj_id = '111'
        rtr_name = 'rtr111'
        get_result = {'id': obj_id,
                      'display_name': rtr_name,
                      'route_advertisement_types': ['TIER1_NAT',
                                                    'TIER1_LB_VIP']}
        with mock.patch.object(self.policy_api, "get",
                               return_value=get_result),\
            mock.patch.object(self.policy_api,
                              "create_or_update") as update_call:
            self.resourceApi.update_route_advertisement(
                obj_id,
                static_routes=True,
                lb_vip=False,
                lb_snat=True,
                ipsec_endpoints=True,
                tenant=TEST_TENANT)

            new_adv = self.resourceApi.build_route_advertisement(
                nat=True, static_routes=True, lb_snat=True,
                ipsec_endpoints=True)

            expected_def = core_defs.Tier1Def(
                tier1_id=obj_id,
                route_advertisement=new_adv,
                tenant=TEST_TENANT)
            if not self.partial_updates:
                expected_def.attrs['name'] = rtr_name

            self.assert_called_with_def(
                update_call, expected_def)

    def test_update_route_adv_and_tier0(self):
        obj_id = '111'
        rtr_name = 'rtr111'
        tier0 = 'tier0-id'
        get_result = {'id': obj_id,
                      'display_name': rtr_name,
                      'route_advertisement_types': ['TIER1_NAT',
                                                    'TIER1_LB_VIP']}
        with mock.patch.object(self.policy_api, "get",
                               return_value=get_result),\
            mock.patch.object(self.policy_api,
                              "create_or_update") as update_call:
            self.resourceApi.update_route_advertisement(
                obj_id,
                static_routes=True,
                lb_vip=False,
                lb_snat=True,
                tier0=tier0,
                tenant=TEST_TENANT)

            new_adv = self.resourceApi.build_route_advertisement(
                nat=True, static_routes=True, lb_snat=True)

            expected_def = core_defs.Tier1Def(
                tier1_id=obj_id,
                route_advertisement=new_adv,
                tier0=tier0,
                tenant=TEST_TENANT)
            if not self.partial_updates:
                expected_def.attrs['name'] = rtr_name

            self.assert_called_with_def(
                update_call, expected_def)

    def test_set_enable_standby_relocation(self):
        obj_id = '111'
        name = 'new name'
        tier0 = 'tier0'
        with mock.patch.object(self.policy_api, "get",
                               return_value={}),\
            mock.patch.object(self.policy_api,
                              "create_or_update") as update_call:
            self.resourceApi.update(obj_id,
                                    name=name, tier0=tier0,
                                    enable_standby_relocation=True,
                                    tenant=TEST_TENANT)
            expected_def = core_defs.Tier1Def(tier1_id=obj_id,
                                              name=name,
                                              tier0=tier0,
                                              enable_standby_relocation=True,
                                              tenant=TEST_TENANT)
            self.assert_called_with_def(
                update_call, expected_def)

    def test_wait_until_realized_fail(self):
        tier1_id = '111'
        logical_router_id = 'realized_111'
        info = {'state': constants.STATE_UNREALIZED,
                'realization_specific_identifier': logical_router_id,
                'entity_type': 'RealizedLogicalRouter'}
        with mock.patch.object(self.resourceApi, "_get_realization_info",
                               return_value=info):
            self.assertRaises(nsxlib_exc.RealizationTimeoutError,
                              self.resourceApi.wait_until_realized,
                              tier1_id, max_attempts=5, sleep=0.1,
                              tenant=TEST_TENANT)

    def test_wait_until_realized_succeed(self):
        tier1_id = '111'
        logical_router_id = 'realized_111'
        info = {'state': constants.STATE_REALIZED,
                'realization_specific_identifier': logical_router_id,
                'entity_type': 'RealizedLogicalRouter'}
        with mock.patch.object(self.resourceApi, "_get_realization_info",
                               return_value=info):
            actual_info = self.resourceApi.wait_until_realized(
                tier1_id, max_attempts=5, sleep=0.1, tenant=TEST_TENANT)
            self.assertEqual(info, actual_info)

    def test_update_transport_zone(self):
        # Test the passthrough api
        tier1_id = '111'
        logical_router_id = 'realized_111'
        tz_uuid = 'dummy_tz'
        info = {'state': constants.STATE_REALIZED,
                'entity_type': 'RealizedLogicalRouter',
                'realization_specific_identifier': logical_router_id}
        passthrough_mock = self.resourceApi.nsx_api.logical_router.update
        with mock.patch.object(self.resourceApi, "_get_realization_info",
                               return_value=info) as realization,\
            mock.patch.object(self.resourceApi,
                              "_get_realized_id_using_search",
                              return_value=logical_router_id):
            self.resourceApi.update_transport_zone(tier1_id, tz_uuid,
                                                   tenant=TEST_TENANT)
            realization.assert_called_once()
            passthrough_mock.assert_called_once_with(
                logical_router_id, transport_zone_id=tz_uuid)

    def test_wait_until_realized(self):
        tier1_id = '111'
        logical_router_id = 'realized_111'
        info = {'state': constants.STATE_UNREALIZED,
                'realization_specific_identifier': logical_router_id}
        with mock.patch.object(self.resourceApi, "_get_realization_info",
                               return_value=info):
            self.assertRaises(nsxlib_exc.RealizationTimeoutError,
                              self.resourceApi.wait_until_realized,
                              tier1_id, tenant=TEST_TENANT,
                              max_attempts=5, sleep=0.1)

    def test_get_realized_id(self):
        # Get realized ID using search
        tier1_id = '111'
        logical_router_id = 'realized_111'
        info = {'results': [{'status': {'state': 'success'},
                             'id': logical_router_id}]}
        with mock.patch.object(self.resourceApi.nsx_api, "search_by_tags",
                               return_value=info):
            realized_id = self.resourceApi.get_realized_id(tier1_id)
            self.assertEqual(logical_router_id, realized_id)

    def test_get_realized_id_failed(self):
        # Get realized ID using search
        tier1_id = '111'
        logical_router_id = 'realized_111'
        info = {'results': [{'status': {'state': 'in_progress'},
                             'id': logical_router_id}]}
        with mock.patch.object(self.resourceApi.nsx_api, "search_by_tags",
                               return_value=info),\
            mock.patch.object(self.resourceApi.policy_api,
                              "get_realized_entities"):
            self.assertRaises(nsxlib_exc.RealizationTimeoutError,
                              self.resourceApi.get_realized_id, tier1_id)

    def test_get_realized_downlink_port(self):
        tier1_id = '111'
        segment_id = '222'
        lrp_id = '333'
        info = {'state': constants.STATE_REALIZED,
                'realization_specific_identifier': lrp_id,
                'entity_type': 'RealizedLogicalRouterPort'}
        dummy_port = {'resource_type': nsx_constants.LROUTERPORT_DOWNLINK,
                      'id': lrp_id,
                      'display_name': 'test_%s' % segment_id}
        with mock.patch.object(self.resourceApi.policy_api,
                               "get_realized_entities",
                               return_value=[info]),\
            mock.patch.object(self.resourceApi.nsx_api.logical_router_port,
                              "get", return_value=dummy_port):
            actual_id = self.resourceApi._get_realized_downlink_port(
                tier1_id, segment_id)
            self.assertEqual(lrp_id, actual_id)

    def test_get_realization_info(self):
        tier1_id = 'id-rtr'
        with mock.patch.object(self.resourceApi, "_get_realization_info") as\
                mock_call:
            self.resourceApi.get_realization_info(
                tier1_id, entity_type='RealizedLogicalRouterPort', tenant=None)
            expected_def = core_defs.Tier1Def(tier1_id=tier1_id, tenant=None)
            self.assert_called_with_def_and_kwargs(
                mock_call,
                expected_def,
                entity_type='RealizedLogicalRouterPort',
                silent=False)

    def test_get_realized_router_port(self):
        tier1_id = 'id-rtr'
        with mock.patch.object(self.resourceApi, "_get_realization_info") as \
                mock_call:
            self.resourceApi.get_realized_router_port(
                tier1_id, tenant=None)
            expected_def = core_defs.Tier1Def(tier1_id=tier1_id, tenant=None)
            self.assert_called_with_def_and_kwargs(
                mock_call,
                expected_def,
                entity_type='RealizedLogicalRouterPort',
                all_result=True,
                silent=False
            )

    def test_set_dhcp_relay(self):
        tier1_id = '111'
        segment_id = '222'
        lrp_id = '333'
        relay_id = '444'
        info = {'state': constants.STATE_REALIZED,
                'realization_specific_identifier': lrp_id,
                'entity_type': 'RealizedLogicalRouterPort'}
        dummy_port = {'resource_type': nsx_constants.LROUTERPORT_DOWNLINK,
                      'id': lrp_id,
                      'display_name': 'test_%s' % segment_id}
        with mock.patch.object(self.resourceApi.policy_api,
                               "get_realized_entities",
                               return_value=[info]),\
            mock.patch.object(self.resourceApi.nsx_api.logical_router_port,
                              "get", return_value=dummy_port),\
            mock.patch.object(self.resourceApi.nsx_api.logical_router_port,
                              "update") as nsx_lrp_update:
            self.resourceApi.set_dhcp_relay(tier1_id, segment_id, relay_id)
            nsx_lrp_update.assert_called_once_with(
                lrp_id, relay_service_uuid=relay_id)

    def test_get_locale_tier1_services(self):
        tier1_id = '111'
        path = 'dummy/path'
        mock_result = [{'edge_cluster_path': path}, {'test': 'test'}]
        with mock.patch.object(self.policy_api, "list",
                               return_value={'results': mock_result}):
            self.assertEqual(
                self.resourceApi.get_locale_tier1_services(tier1_id),
                mock_result)

    def test_get_edge_cluster_by_searching(self):
        tier1_id = '111'
        path = 'dummy/path'
        with mock.patch.object(self.resourceApi, "get_locale_tier1_services",
                               return_value=[{'edge_cluster_path': path},
                                             {'test': 'test'}]):
            result = self.resourceApi.get_edge_cluster_path_by_searching(
                tier1_id, tenant=TEST_TENANT)
            self.assertEqual(path, result)

    def test_get_edge_cluster(self):
        tier1_id = '111'
        path = 'dummy/path'
        with mock.patch.object(self.policy_api, "get",
                               return_value={'edge_cluster_path': path}):
            result = self.resourceApi.get_edge_cluster_path(
                tier1_id, tenant=TEST_TENANT)
            self.assertEqual(path, result)

    def test_set_edge_cluster(self):
        tier1_id = '111'
        path = 'dummy/path'
        preferred_edge_paths = ['dummy/path/edge/0', 'dummy/path/edge/1']
        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            self.resourceApi.set_edge_cluster_path(
                tier1_id, path,
                preferred_edge_paths=preferred_edge_paths,
                tenant=TEST_TENANT)

            expected_def = core_defs.Tier1LocaleServiceDef(
                tier1_id=tier1_id,
                service_id=self.resourceApi._locale_service_id(tier1_id),
                edge_cluster_path=path,
                preferred_edge_paths=preferred_edge_paths,
                tenant=TEST_TENANT)

            self.assert_called_with_def(api_call, expected_def)

    def test_remove_edge_cluster(self):
        tier1_id = '111'
        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            self.resourceApi.remove_edge_cluster(
                tier1_id,
                tenant=TEST_TENANT)
            expected_def = core_defs.Tier1LocaleServiceDef(
                tier1_id=tier1_id,
                service_id=self.resourceApi._locale_service_id(tier1_id),
                edge_cluster_path="",
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_create_locale_service(self):
        tier1_id = '111'
        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            self.resourceApi.create_locale_service(
                tier1_id,
                tenant=TEST_TENANT)
            expected_def = core_defs.Tier1LocaleServiceDef(
                tier1_id=tier1_id,
                service_id=self.resourceApi._locale_service_id(tier1_id),
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_delete_locale_service(self):
        tier1_id = '111'
        with mock.patch.object(self.policy_api,
                               "delete") as api_call:
            self.resourceApi.delete_locale_service(
                tier1_id,
                tenant=TEST_TENANT)
            expected_def = core_defs.Tier1LocaleServiceDef(
                tier1_id=tier1_id,
                service_id=self.resourceApi._locale_service_id(tier1_id),
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_add_router_interface(self):
        tier1_id = '111'
        interface_id = 'seg-if'
        segment_id = 'seg'
        ip_addr = '1.1.1.1'
        prefix_len = '24'
        ndra_profile = 'slaac'
        subnet = core_defs.InterfaceSubnet([ip_addr], prefix_len)
        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            self.resourceApi.add_segment_interface(
                tier1_id, interface_id, segment_id,
                subnets=[subnet],
                ipv6_ndra_profile_id=ndra_profile,
                tenant=TEST_TENANT)

            expected_def = core_defs.Tier1InterfaceDef(
                tier1_id=tier1_id,
                service_id=self.resourceApi._locale_service_id(tier1_id),
                interface_id=interface_id,
                segment_id=segment_id,
                subnets=[subnet],
                ipv6_ndra_profile_id=ndra_profile,
                tenant=TEST_TENANT)

            self.assert_called_with_def(api_call, expected_def)

    def test_add_route_interface_subnet_as_dict(self):
        tier1_id = '111'
        interface_id = 'seg-if'
        segment_id = 'seg'
        ip_addr = '1.1.1.1'
        prefix_len = '24'
        ndra_profile = 'slaac'
        subnet = {'ip_addresses': ip_addr,
                  'prefix_len': prefix_len}
        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            self.resourceApi.add_segment_interface(
                tier1_id, interface_id, segment_id,
                subnets=[subnet],
                ipv6_ndra_profile_id=ndra_profile,
                tenant=TEST_TENANT)

            expected_def = core_defs.Tier1InterfaceDef(
                tier1_id=tier1_id,
                service_id=self.resourceApi._locale_service_id(tier1_id),
                interface_id=interface_id,
                segment_id=segment_id,
                subnets=[subnet],
                ipv6_ndra_profile_id=ndra_profile,
                tenant=TEST_TENANT)

            self.assert_called_with_def(api_call, expected_def)

    def test_add_router_interface_no_ndra(self):
        tier1_id = '111'
        interface_id = 'seg-if'
        segment_id = 'seg'
        ip_addr = '1.1.1.1'
        prefix_len = '24'
        subnet = core_defs.InterfaceSubnet([ip_addr], prefix_len)
        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            self.resourceApi.add_segment_interface(
                tier1_id, interface_id, segment_id,
                subnets=[subnet],
                tenant=TEST_TENANT)

            expected_def = core_defs.Tier1InterfaceDef(
                tier1_id=tier1_id,
                service_id=self.resourceApi._locale_service_id(tier1_id),
                interface_id=interface_id,
                segment_id=segment_id,
                subnets=[subnet],
                tenant=TEST_TENANT)

            self.assert_called_with_def(api_call, expected_def)

    def test_remove_router_interface(self):
        tier1_id = '111'
        interface_id = 'seg-if'
        with mock.patch.object(self.policy_api,
                               "delete") as api_call:
            self.resourceApi.remove_segment_interface(
                tier1_id, interface_id,
                tenant=TEST_TENANT)

            expected_def = core_defs.Tier1InterfaceDef(
                tier1_id=tier1_id,
                service_id=self.resourceApi._locale_service_id(tier1_id),
                interface_id=interface_id,
                tenant=TEST_TENANT)

            self.assert_called_with_def(api_call, expected_def)

    def test_get_multicast(self):
        tier1_id = '111'
        with mock.patch.object(self.policy_api, "get") as api_call:
            api_call.return_value = {'enabled': True}
            enabled = self.resourceApi.get_multicast(
                tier1_id,
                tenant=TEST_TENANT)

            expected_def = core_defs.Tier1MulticastDef(
                tier1_id=tier1_id,
                service_id=self.resourceApi._locale_service_id(tier1_id),
                tenant=TEST_TENANT)

            self.assert_called_with_def(api_call, expected_def)
            self.assertTrue(enabled)

    def test_enable_multicast(self):
        tier1_id = '111'
        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            self.resourceApi.enable_multicast(
                tier1_id,
                tenant=TEST_TENANT)

            expected_def = core_defs.Tier1MulticastDef(
                tier1_id=tier1_id,
                service_id=self.resourceApi._locale_service_id(tier1_id),
                enabled=True,
                tenant=TEST_TENANT)

            self.assert_called_with_def(api_call, expected_def)

    def test_disable_multicast(self):
        tier1_id = '111'
        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            self.resourceApi.disable_multicast(
                tier1_id,
                tenant=TEST_TENANT)

            expected_def = core_defs.Tier1MulticastDef(
                tier1_id=tier1_id,
                service_id=self.resourceApi._locale_service_id(tier1_id),
                enabled=False,
                tenant=TEST_TENANT)

            self.assert_called_with_def(api_call, expected_def)

    def test_add_advertisement_rule(self):
        tier1_id = '111'
        rule_name = 'rule_name'
        rule_action = 'rule_action'
        rule_pfx_operator = 'GE'
        rule_adv_types = ['A']
        rule_subnets = ['x', 'y', 'z']
        with mock.patch.object(self.policy_api,
                               "get",
                               return_value={'id': tier1_id,
                                             'resource_type': 'Tier1'}),\
            mock.patch.object(self.policy_api,
                              'create_or_update') as api_call:
            self.resourceApi.add_advertisement_rule(
                tier1_id, rule_name, action=rule_action,
                prefix_operator=rule_pfx_operator,
                route_advertisement_types=rule_adv_types, subnets=rule_subnets,
                tenant=TEST_TENANT)

            expected_def = core_defs.Tier1Def(
                tier1_id=tier1_id,
                route_advertisement_rules=[
                    core_defs.RouteAdvertisementRule(
                        rule_name,
                        action=rule_action,
                        prefix_operator=rule_pfx_operator,
                        route_advertisement_types=rule_adv_types,
                        subnets=rule_subnets)],
                tenant=TEST_TENANT)

            self.assert_called_with_def(api_call, expected_def)

    def test_remove_advertisement_rule(self):
        tier1_id = '111'
        rule_name = 'rule_name'
        get_retval = {
            'id': tier1_id,
            'route_advertisement_rules': [{'name': rule_name}]}
        with mock.patch.object(self.policy_api,
                               "get",
                               return_value=get_retval),\
            mock.patch.object(self.policy_api,
                              'create_or_update') as api_call:
            self.resourceApi.remove_advertisement_rule(
                tier1_id, rule_name, tenant=TEST_TENANT)

            expected_def = core_defs.Tier1Def(
                tier1_id=tier1_id,
                route_advertisement_rules=[],
                tenant=TEST_TENANT)

            self.assert_called_with_def(api_call, expected_def)

    def test_update_advertisement_rules(self):
        tier1_id = '111'
        old_rule = 'old'
        new_rule = 'new'
        get_retval = {
            'id': tier1_id,
            'route_advertisement_rules': [{'name': old_rule}]}
        rules = [{'name': new_rule}]
        with mock.patch.object(self.policy_api,
                               "get",
                               return_value=get_retval),\
            mock.patch.object(self.policy_api,
                              'create_or_update') as api_call:
            self.resourceApi.update_advertisement_rules(
                tier1_id, rules, name_prefix=None, tenant=TEST_TENANT)

            expected_def = core_defs.Tier1Def(
                tier1_id=tier1_id,
                route_advertisement_rules=rules,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_update_advertisement_rules_with_replace(self):
        tier1_id = '111'
        old_rule1 = 'old1'
        old_rule2 = 'old2'
        new_rule = 'new'
        get_retval = {
            'id': tier1_id,
            'route_advertisement_rules': [
                {'name': old_rule1},
                {'name': old_rule2}]}
        rules = [{'name': new_rule}]
        with mock.patch.object(self.policy_api,
                               "get",
                               return_value=get_retval),\
            mock.patch.object(self.policy_api,
                              'create_or_update') as api_call:
            self.resourceApi.update_advertisement_rules(
                tier1_id, rules, name_prefix='old1', tenant=TEST_TENANT)

            expected_def = core_defs.Tier1Def(
                tier1_id=tier1_id,
                route_advertisement_rules=[
                    {'name': old_rule2},
                    {'name': new_rule}],
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_update_advertisement_rules_remove(self):
        tier1_id = '111'
        old_rule1 = 'old1'
        old_rule2 = 'old2'
        get_retval = {
            'id': tier1_id,
            'route_advertisement_rules': [
                {'name': old_rule1},
                {'name': old_rule2}]}
        with mock.patch.object(self.policy_api,
                               "get",
                               return_value=get_retval),\
            mock.patch.object(self.policy_api,
                              'create_or_update') as api_call:
            self.resourceApi.update_advertisement_rules(
                tier1_id, None, name_prefix='old1', tenant=TEST_TENANT)

            expected_def = core_defs.Tier1Def(
                tier1_id=tier1_id,
                route_advertisement_rules=[
                    {'name': old_rule2}],
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_create_with_unsupported_attr(self):
        name = 'test'
        description = 'test_version_support'
        tier0_id = 'tier0'
        pool_alloc_type = 'LB_SMALL'
        route_adv = self.resourceApi.build_route_advertisement(
            lb_vip=True,
            lb_snat=True)

        with mock.patch.object(
                self.policy_api, "create_or_update") as api_call, \
                mock.patch.object(self.resourceApi, 'version', '0.0.0'):
            result = self.resourceApi.create_or_overwrite(
                name, description=description,
                tier0=tier0_id,
                force_whitelisting=True,
                route_advertisement=route_adv,
                pool_allocation=pool_alloc_type,
                tenant=TEST_TENANT)

            expected_def = core_defs.Tier1Def(
                tier1_id=mock.ANY,
                name=name,
                description=description,
                tier0=tier0_id,
                force_whitelisting=True,
                failover_mode=constants.NON_PREEMPTIVE,
                route_advertisement=route_adv,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertIsNotNone(result)

    def test_get_preferred_edge_paths(self):
        tier1_id = "1111"
        preferred_edge_paths = [
            "/fake/edge-clusters/edge-nodes/0",
            "/fake/edge-clusters/edge-nodes/0"
        ]
        with mock.patch.object(
                self.resourceApi, "get_locale_tier1_services",
                return_value=[{"preferred_edge_paths": preferred_edge_paths}]):
            result = self.resourceApi.get_preferred_edge_paths(tier1_id)
            self.assertEqual(
                preferred_edge_paths,
                result)


class TestPolicyTier1NoPassthrough(TestPolicyTier1):

    def setUp(self, *args, **kwargs):
        super(TestPolicyTier1NoPassthrough, self).setUp(
            allow_passthrough=False)
        # No passthrough also means no partial updates
        self.partial_updates = False

    def test_update_transport_zone(self):
        # Will not work without passthrough api
        tier1_id = '111'
        tz_uuid = 'dummy_tz'
        with mock.patch.object(self.resourceApi,
                               "_get_realization_info") as realization:
            self.resourceApi.update_transport_zone(tier1_id, tz_uuid,
                                                   tenant=TEST_TENANT)
            realization.assert_not_called()

    def test_get_realized_downlink_port(self):
        # Will not work without passthrough api
        tier1_id = '111'
        segment_id = '222'
        with mock.patch.object(self.resourceApi.policy_api,
                               "get_realized_entities") as realization:
            actual_id = self.resourceApi._get_realized_downlink_port(
                tier1_id, segment_id)
            self.assertIsNone(actual_id)
            realization.assert_not_called()

    def test_set_dhcp_relay(self):
        # Will not work without passthrough api
        tier1_id = '111'
        segment_id = '222'
        relay_id = '444'
        with mock.patch.object(self.resourceApi.policy_api,
                               "get_realized_entities") as realization:
            self.resourceApi.set_dhcp_relay(tier1_id, segment_id, relay_id)
            realization.assert_not_called()

    def test_get_realized_id(self):
        # Get realized ID using policy api
        tier1_id = '111'
        logical_router_id = 'realized_111'
        result = [{'state': constants.STATE_REALIZED,
                   'entity_type': 'RealizedLogicalRouter',
                   'realization_specific_identifier': logical_router_id}]
        with mock.patch.object(self.resourceApi.policy_api,
                               "get_realized_entities",
                               return_value=result):
            realized_id = self.resourceApi.get_realized_id(tier1_id)
            self.assertEqual(logical_router_id, realized_id)

    def test_get_realized_id_failed(self):
        # Get realized ID using policy api
        tier1_id = '111'
        result = [{'state': constants.STATE_UNREALIZED,
                   'entity_type': 'RealizedLogicalRouter'}]
        with mock.patch.object(self.resourceApi.policy_api,
                               "get_realized_entities",
                               return_value=result):
            realized_id = self.resourceApi.get_realized_id(tier1_id)
            self.assertEqual(None, realized_id)


class TestPolicyTier0Bgp(NsxPolicyLibTestCase):

    def setUp(self, *args, **kwargs):
        super(TestPolicyTier0Bgp, self).setUp()
        self.resourceApi = self.policy_lib.tier0_bgp

    def test_create(self):
        name = 'test'
        description = 'bgp'
        tier0_id = 't0'
        service_id = "default",
        ecmp = True,
        enabled = True,
        graceful_restart_config = {
            "mode": "DISABLE",
            "timer": {
                "restart_timer": 180,
                "stale_route_timer": 600
            }
        }
        inter_sr_ibgp = False,
        local_as_num = "65546",
        multipath_relax = False,
        route_aggregations = [{
            "prefix": "10.1.1.0/24"}, {
            "prefix": "11.1.0.0/16", "summary_only": "false"}]
        tags = [{"tag": "tag", "scope": "scope"}]
        tenant = TEST_TENANT
        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            result = self.resourceApi.create_or_overwrite(
                tier0_id, service_id,
                name=name,
                description=description,
                ecmp=ecmp,
                enabled=enabled,
                graceful_restart_config=graceful_restart_config,
                inter_sr_ibgp=inter_sr_ibgp,
                local_as_num=local_as_num,
                multipath_relax=multipath_relax,
                route_aggregations=route_aggregations,
                tags=tags,
                tenant=tenant)
            expected_def = core_defs.BgpRoutingConfigDef(
                tier0_id=tier0_id,
                service_id=service_id,
                name=name,
                description=description,
                ecmp=ecmp,
                enabled=enabled,
                graceful_restart_config=graceful_restart_config,
                inter_sr_ibgp=inter_sr_ibgp,
                local_as_num=local_as_num,
                multipath_relax=multipath_relax,
                route_aggregations=route_aggregations,
                tags=tags,
                tenant=tenant
            )
            self.assert_called_with_def(api_call, expected_def)
            self.assertIsNone(result)

    def test_update_patch(self):
        name = 'test'
        description = 'bgp'
        tier0_id = 't0'
        service_id = "default",
        ecmp = True,
        enabled = True,
        graceful_restart_config = {
            "mode": "DISABLE",
            "timer": {
                "restart_timer": 180,
                "stale_route_timer": 600
            }
        }
        inter_sr_ibgp = False,
        local_as_num = "65546",
        multipath_relax = False,
        route_aggregations = [{
            "prefix": "10.1.1.0/24"}, {
            "prefix": "11.1.0.0/16", "summary_only": "false"}]
        tags = [{"tag": "tag", "scope": "scope"}]
        tenant = TEST_TENANT
        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            result = self.resourceApi.update(
                tier0_id, service_id,
                name=name,
                description=description,
                ecmp=ecmp,
                enabled=enabled,
                graceful_restart_config=graceful_restart_config,
                inter_sr_ibgp=inter_sr_ibgp,
                local_as_num=local_as_num,
                multipath_relax=multipath_relax,
                route_aggregations=route_aggregations,
                tags=tags,
                tenant=tenant)
            expected_def = core_defs.BgpRoutingConfigDef(
                tier0_id=tier0_id,
                service_id=service_id,
                name=name,
                description=description,
                ecmp=ecmp,
                enabled=enabled,
                graceful_restart_config=graceful_restart_config,
                inter_sr_ibgp=inter_sr_ibgp,
                local_as_num=local_as_num,
                multipath_relax=multipath_relax,
                route_aggregations=route_aggregations,
                tags=tags,
                tenant=tenant
            )
            self.assert_called_with_def(api_call, expected_def)
            self.assertIsNone(result)

    def test_update_put(self):
        name = 'test'
        description = 'bgp'
        tier0_id = 't0'
        service_id = "default",
        ecmp = True,
        enabled = True,
        graceful_restart_config = {
            "mode": "DISABLE",
            "timer": {
                "restart_timer": 180,
                "stale_route_timer": 600
            }
        }
        inter_sr_ibgp = False,
        local_as_num = "65546",
        multipath_relax = False,
        route_aggregations = [{
            "prefix": "10.1.1.0/24"}, {
            "prefix": "11.1.0.0/16", "summary_only": "false"}]
        tags = [{"tag": "tag", "scope": "scope"}]
        tenant = TEST_TENANT
        with mock.patch.object(self.policy_api, "get",
                               return_value={}),\
            mock.patch.object(self.policy_api,
                              "update_with_put") as api_call:
            result = self.resourceApi.update(
                tier0_id, service_id,
                name=name,
                description=description,
                ecmp=ecmp,
                enabled=enabled,
                graceful_restart_config=graceful_restart_config,
                inter_sr_ibgp=inter_sr_ibgp,
                local_as_num=local_as_num,
                multipath_relax=multipath_relax,
                route_aggregations=route_aggregations,
                tags=tags,
                tenant=tenant,
                put=True,
                revision=1)
            expected_def = core_defs.BgpRoutingConfigDef(
                tier0_id=tier0_id,
                service_id=service_id,
                name=name,
                description=description,
                ecmp=ecmp,
                enabled=enabled,
                graceful_restart_config=graceful_restart_config,
                inter_sr_ibgp=inter_sr_ibgp,
                local_as_num=local_as_num,
                multipath_relax=multipath_relax,
                route_aggregations=route_aggregations,
                tags=tags,
                tenant=tenant
            )
            self.assert_called_with_def_and_kwargs(
                api_call, expected_def, revision=1)
            self.assertIsNotNone(result)

    def test_get(self):
        tier0_id = 't0'
        service_id = 'default'
        tenant = TEST_TENANT
        with mock.patch.object(self.policy_api, "get") as api_call:
            mock_tier0_bgp = mock.Mock()
            api_call.return_value = mock_tier0_bgp
            result = self.resourceApi.get(tier0_id, service_id, tenant=tenant)
            expected_def = core_defs.BgpRoutingConfigDef(
                tier0_id=tier0_id, service_id=service_id, tenant=tenant)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(result, mock_tier0_bgp)


class TestPolicyTier0NatRule(NsxPolicyLibTestCase):

    def setUp(self, *args, **kwargs):
        super(TestPolicyTier0NatRule, self).setUp()
        self.resourceApi = self.policy_lib.tier0_nat_rule

    def test_create(self):
        name = 'test'
        description = 'desc'
        tier0_id = '111'
        nat_rule_id = 'rule1'
        action = constants.NAT_ACTION_SNAT
        firewall_match = constants.NAT_FIREWALL_MATCH_INTERNAL
        cidr1 = '1.1.1.1/32'
        cidr2 = '2.2.2.0/24'
        enabled = True
        logging = False

        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            result = self.resourceApi.create_or_overwrite(
                name, tier0_id,
                nat_rule_id=nat_rule_id,
                description=description,
                action=action,
                translated_network=cidr1,
                source_network=cidr2,
                firewall_match=firewall_match,
                tenant=TEST_TENANT,
                enabled=enabled,
                logging=logging)
            expected_def = core_defs.Tier0NatRule(
                tier0_id=tier0_id,
                nat_rule_id=nat_rule_id,
                nat_id=self.resourceApi.DEFAULT_NAT_ID,
                name=name,
                description=description,
                action=action,
                translated_network=cidr1,
                source_network=cidr2,
                firewall_match=firewall_match,
                tenant=TEST_TENANT,
                enabled=enabled,
                logging=logging)
            self.assert_called_with_def(api_call, expected_def)
            self.assertIsNotNone(result)

    def test_delete(self):
        tier0_id = '111'
        nat_rule_id = 'rule1'
        with mock.patch.object(self.policy_api, "delete") as api_call:
            self.resourceApi.delete(
                tier0_id,
                nat_rule_id,
                tenant=TEST_TENANT)
            expected_def = core_defs.Tier0NatRule(
                tier0_id=tier0_id,
                nat_rule_id=nat_rule_id,
                nat_id=self.resourceApi.DEFAULT_NAT_ID,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_get(self):
        tier0_id = '111'
        nat_rule_id = 'rule1'
        with mock.patch.object(self.policy_api, "get") as api_call:
            mock_t0_nat_rule = mock.Mock()
            api_call.return_value = mock_t0_nat_rule
            result = self.resourceApi.get(tier0_id, nat_rule_id,
                                          tenant=TEST_TENANT)
            expected_def = core_defs.Tier0NatRule(
                tier0_id=tier0_id,
                nat_rule_id=nat_rule_id,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(mock_t0_nat_rule, result)

    def test_update(self):
        name = 'test'
        description = 'desc'
        tier0_id = '111'
        nat_rule_id = 'rule1'
        action = constants.NAT_ACTION_SNAT
        firewall_match = constants.NAT_FIREWALL_MATCH_EXTERNAL
        cidr1 = '1.1.1.1/32'
        cidr2 = '2.2.2.0/24'
        enabled = True
        logging = False

        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            self.resourceApi.update(
                tier0_id, nat_rule_id,
                name=name,
                description=description,
                action=action,
                translated_network=cidr1,
                firewall_match=firewall_match,
                source_network=cidr2,
                tenant=TEST_TENANT,
                enabled=enabled,
                logging=logging)

            expected_def = core_defs.Tier0NatRule(
                tier0_id=tier0_id,
                nat_rule_id=nat_rule_id,
                nat_id=self.resourceApi.DEFAULT_NAT_ID,
                name=name,
                description=description,
                action=action,
                translated_network=cidr1,
                firewall_match=firewall_match,
                source_network=cidr2,
                tenant=TEST_TENANT,
                enabled=enabled,
                logging=logging)
            self.assert_called_with_def(api_call, expected_def)


class TestPolicyTier1NatRule(NsxPolicyLibTestCase):

    def setUp(self, *args, **kwargs):
        super(TestPolicyTier1NatRule, self).setUp()
        self.resourceApi = self.policy_lib.tier1_nat_rule

    def test_create(self):
        name = 'test'
        description = 'desc'
        tier1_id = '111'
        nat_rule_id = 'rule1'
        action = constants.NAT_ACTION_SNAT
        firewall_match = constants.NAT_FIREWALL_MATCH_INTERNAL
        cidr1 = '1.1.1.1/32'
        cidr2 = '2.2.2.0/24'
        enabled = True
        logging = True

        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            result = self.resourceApi.create_or_overwrite(
                name, tier1_id,
                nat_rule_id=nat_rule_id,
                description=description,
                action=action,
                translated_network=cidr1,
                firewall_match=firewall_match,
                source_network=cidr2,
                tenant=TEST_TENANT,
                enabled=enabled,
                logging=logging)

            expected_def = core_defs.Tier1NatRule(
                tier1_id=tier1_id,
                nat_rule_id=nat_rule_id,
                nat_id=self.resourceApi.DEFAULT_NAT_ID,
                name=name,
                description=description,
                action=action,
                translated_network=cidr1,
                firewall_match=firewall_match,
                source_network=cidr2,
                tenant=TEST_TENANT,
                enabled=enabled,
                logging=logging)
            self.assert_called_with_def(api_call, expected_def)
            self.assertIsNotNone(result)

    def test_delete(self):
        tier1_id = '111'
        nat_rule_id = 'rule1'
        with mock.patch.object(self.policy_api, "delete") as api_call:
            self.resourceApi.delete(
                tier1_id,
                nat_rule_id,
                tenant=TEST_TENANT)
            expected_def = core_defs.Tier1NatRule(
                tier1_id=tier1_id,
                nat_rule_id=nat_rule_id,
                nat_id=self.resourceApi.DEFAULT_NAT_ID,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_update(self):
        name = 'test'
        description = 'desc'
        tier1_id = '111'
        nat_rule_id = 'rule1'
        action = constants.NAT_ACTION_SNAT
        firewall_match = constants.NAT_FIREWALL_MATCH_INTERNAL
        cidr1 = '1.1.1.1/32'
        cidr2 = '2.2.2.0/24'
        enabled = True
        logging = True

        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            self.resourceApi.update(
                tier1_id, nat_rule_id,
                name=name,
                description=description,
                action=action,
                translated_network=cidr1,
                firewall_match=firewall_match,
                source_network=cidr2,
                tenant=TEST_TENANT,
                enabled=enabled,
                logging=logging)

            expected_def = core_defs.Tier1NatRule(
                tier1_id=tier1_id,
                nat_rule_id=nat_rule_id,
                nat_id=self.resourceApi.DEFAULT_NAT_ID,
                name=name,
                description=description,
                action=action,
                translated_network=cidr1,
                firewall_match=firewall_match,
                source_network=cidr2,
                tenant=TEST_TENANT,
                enabled=enabled,
                logging=logging)
            self.assert_called_with_def(api_call, expected_def)


class TestPolicyTier1StaticRoute(NsxPolicyLibTestCase):

    def setUp(self, *args, **kwargs):
        super(TestPolicyTier1StaticRoute, self).setUp()
        self.resourceApi = self.policy_lib.tier1_static_route

    def test_create(self):
        name = 'test'
        description = 'desc'
        tier1_id = '111'
        static_route_id = '222'
        network = '1.1.1.1/24'
        nexthop = '2.2.2.2'

        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            result = self.resourceApi.create_or_overwrite(
                name, tier1_id,
                static_route_id=static_route_id,
                description=description,
                network=network,
                next_hop=nexthop,
                tenant=TEST_TENANT)

            expected_def = core_defs.Tier1StaticRoute(
                tier1_id=tier1_id,
                static_route_id=static_route_id,
                name=name,
                description=description,
                network=network,
                next_hop=nexthop,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertIsNotNone(result)

    def test_delete(self):
        tier1_id = '111'
        static_route_id = '222'
        with mock.patch.object(self.policy_api, "delete") as api_call:
            self.resourceApi.delete(
                tier1_id,
                static_route_id,
                tenant=TEST_TENANT)
            expected_def = core_defs.Tier1StaticRoute(
                tier1_id=tier1_id,
                static_route_id=static_route_id,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_get(self):
        tier1_id = '111'
        static_route_id = '222'
        with mock.patch.object(self.policy_api, "get") as api_call:
            mock_get = mock.Mock()
            api_call.return_value = mock_get
            result = self.resourceApi.get(
                tier1_id,
                static_route_id,
                tenant=TEST_TENANT)
            expected_def = core_defs.Tier1StaticRoute(
                tier1_id=tier1_id,
                static_route_id=static_route_id,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(mock_get, result)

    def test_wait_until_realized_failed(self):
        tier1_id = 'tier1'
        route_id = 'route1'
        with mock.patch.object(self.resourceApi, "_get_realization_info",
                               return_value=[]):
            self.assertRaises(nsxlib_exc.RealizationTimeoutError,
                              self.resourceApi.wait_until_realized,
                              tier1_id, route_id, tenant=TEST_TENANT,
                              max_attempts=3, sleep=0.1)


class TestPolicyTier0(NsxPolicyLibTestCase):

    def setUp(self, *args, **kwargs):
        super(TestPolicyTier0, self).setUp()
        self.resourceApi = self.policy_lib.tier0

    def test_create(self):
        name = 'test'
        description = 'desc'
        dhcp_config = '111'
        subnets = ["2.2.2.0/24"]
        ipv6_profile_id = '222'

        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            result = self.resourceApi.create_or_overwrite(
                name, description=description,
                dhcp_config=dhcp_config,
                force_whitelisting=True,
                default_rule_logging=True,
                transit_subnets=subnets,
                ipv6_ndra_profile_id=ipv6_profile_id,
                tenant=TEST_TENANT)

            expected_def = core_defs.Tier0Def(
                tier0_id=mock.ANY,
                name=name,
                description=description,
                dhcp_config=dhcp_config,
                default_rule_logging=True,
                force_whitelisting=True,
                ha_mode=constants.ACTIVE_ACTIVE,
                failover_mode=constants.NON_PREEMPTIVE,
                transit_subnets=subnets,
                ipv6_ndra_profile_id=ipv6_profile_id,
                tenant=TEST_TENANT)

            self.assert_called_with_def(api_call, expected_def)
            self.assertIsNotNone(result)

    def test_delete(self):
        obj_id = '111'
        with mock.patch.object(self.policy_api, "delete") as api_call:
            self.resourceApi.delete(obj_id, tenant=TEST_TENANT)
            expected_def = core_defs.Tier0Def(tier0_id=obj_id,
                                              tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_get(self):
        obj_id = '111'
        with mock.patch.object(self.policy_api, "get",
                               return_value={'id': obj_id}) as api_call:
            result = self.resourceApi.get(obj_id, tenant=TEST_TENANT)
            expected_def = core_defs.Tier0Def(tier0_id=obj_id,
                                              tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(obj_id, result['id'])

    def test_get_path(self):
        obj_id = '111'
        result = self.resourceApi.get_path(obj_id, tenant=TEST_TENANT)
        self.assertEqual('/%s/tier-0s/%s' % (TEST_TENANT, obj_id), result)

    def test_get_with_cache(self):
        """Make sure the cache is used for GET requests"""
        obj_id = '111'
        with mock.patch.object(self.policy_api.client, "get") as client_get:
            self.resourceApi.get(obj_id, tenant=TEST_TENANT)
            self.resourceApi.get(obj_id, tenant=TEST_TENANT)
            self.assertEqual(1, client_get.call_count)

    def test_get_by_name(self):
        name = 'test'
        with mock.patch.object(
            self.policy_api, "list",
            return_value={'results': [{'display_name': name}]}) as api_call:
            obj = self.resourceApi.get_by_name(name, tenant=TEST_TENANT)
            self.assertIsNotNone(obj)
            expected_def = core_defs.Tier0Def(tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_list(self):
        with mock.patch.object(self.policy_api, "list",
                               return_value={'results': []}) as api_call:
            result = self.resourceApi.list(tenant=TEST_TENANT)
            expected_def = core_defs.Tier0Def(tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual([], result)

    def test_update(self):
        obj_id = '111'
        name = 'new name'
        with self.mock_get(obj_id, name), \
            self.mock_create_update() as update_call:
            self.resourceApi.update(obj_id,
                                    name=name,
                                    tenant=TEST_TENANT)
            expected_def = core_defs.Tier0Def(tier0_id=obj_id,
                                              name=name,
                                              tenant=TEST_TENANT)
            self.assert_called_with_def(
                update_call, expected_def)

    def test_get_overlay_transport_zone(self):
        # Test the passthrough api
        tier0_id = '111'
        logical_router_id = 'realized_111'
        info = {'state': constants.STATE_REALIZED,
                'entity_type': 'RealizedLogicalRouter',
                'realization_specific_identifier': logical_router_id}
        pt_mock = self.resourceApi.nsx_api.router.get_tier0_router_overlay_tz
        with mock.patch.object(self.resourceApi, "_get_realization_info",
                               return_value=info) as realization:
            result = self.resourceApi.get_overlay_transport_zone(
                tier0_id, tenant=TEST_TENANT)
            realization.assert_called_once()
            pt_mock.assert_called_once_with(logical_router_id)
            self.assertIsNotNone(result)

    def test_wait_until_realized(self):
        tier1_id = '111'
        logical_router_id = 'realized_111'
        info = {'state': constants.STATE_UNREALIZED,
                'realization_specific_identifier': logical_router_id}
        with mock.patch.object(self.resourceApi, "_get_realization_info",
                               return_value=info):
            self.assertRaises(nsxlib_exc.RealizationTimeoutError,
                              self.resourceApi.wait_until_realized,
                              tier1_id, max_attempts=5, sleep=0.1,
                              tenant=TEST_TENANT)

    def test_get_uplink_ips(self):
        tier0_id = '111'
        ip_addr = '5.5.5.5'
        interface = {'id': '222', 'type': 'EXTERNAL',
                     'subnets': [{'ip_addresses': [ip_addr]}]}
        with mock.patch.object(self.resourceApi.policy_api, "list",
                               return_value={'results': [interface]}):
            uplink_ips = self.resourceApi.get_uplink_ips(
                tier0_id, tenant=TEST_TENANT)
            self.assertEqual([ip_addr], uplink_ips)

    def test_get_transport_zones(self):
        # Test the passthrough api
        tier0_id = '111'
        logical_router_id = 'realized_111'
        info = {'state': constants.STATE_REALIZED,
                'entity_type': 'RealizedLogicalRouter',
                'realization_specific_identifier': logical_router_id}
        pt_mock = self.resourceApi.nsx_api.router.get_tier0_router_tz
        with mock.patch.object(self.resourceApi, "_get_realization_info",
                               return_value=info) as realization:
            result = self.resourceApi.get_transport_zones(
                tier0_id, tenant=TEST_TENANT)
            realization.assert_called_once()
            pt_mock.assert_called_once_with(logical_router_id)
            self.assertIsNotNone(result)

    def test_get_bgp_config(self):
        tier0_id = '111'
        services = {'results': [{'id': 'service1'}]}
        bgp_config = {"id": "bgp", "enabled": True}
        with mock.patch.object(self.resourceApi.policy_api, "get",
                               return_value=bgp_config), \
            mock.patch.object(self.resourceApi.policy_api, "list",
                              return_value=services):
            result = self.resourceApi.get_bgp_config(
                tier0_id, tenant=TEST_TENANT)
            self.assertEqual(result, bgp_config)

    def test_build_route_redistribution_rule(self):
        name = "rule_name"
        types = ["T1_CONNECTED", "T1_SEGMENT"]
        route_map_path = "/infra/route_map_path"
        rule = self.resourceApi.build_route_redistribution_rule(
            name, types, route_map_path)
        self.assertEqual(name, rule.name)
        self.assertEqual(types, rule.route_redistribution_types)
        self.assertEqual(route_map_path, rule.route_map_path)

    def test_build_route_redistribution_config(self):
        enabled = True
        rules = ["redistribution_types"]
        config = self.resourceApi.build_route_redistribution_config(
            enabled, rules)
        self.assertEqual(enabled, config.enabled)
        self.assertEqual(rules, config.redistribution_rules)

    def test_get_route_redistribution_config(self):
        tier0_id = '111'
        config = 'redistribution_config'
        with mock.patch.object(
            self.resourceApi, "get_locale_services",
            return_value=[{'route_redistribution_config': config}]):
            result = self.resourceApi.get_route_redistribution_config(
                tier0_id, tenant=TEST_TENANT)
            self.assertEqual(config, result)

    def test_update_route_redistribution_config(self):
        tier0_id = '111'
        service_id = '222'
        config = 'redistribution_config'
        with mock.patch.object(
            self.policy_api, "create_or_update") as api_call:
            self.resourceApi.update_route_redistribution_config(
                tier0_id, config, service_id, tenant=TEST_TENANT)
            expected_def = core_defs.Tier0LocaleServiceDef(
                nsx_version=nsxlib_testcase.LATEST_VERSION, tier0_id=tier0_id,
                service_id=service_id, route_redistribution_config=config,
                tenant=TEST_TENANT)

            self.assert_called_with_def(api_call, expected_def)

        with mock.patch.object(self.resourceApi, "get_locale_services",
                               return_value=[]):
            self.assertRaises(
                nsxlib_exc.ManagerError,
                self.resourceApi.update_route_redistribution_config,
                tier0_id, config, tenant=TEST_TENANT)

    def test_feature_supported(self):
        with mock.patch.object(self.policy_lib, "get_version",
                               return_value='2.5.0'):
            self.assertFalse(
                self.policy_lib.feature_supported(
                    nsx_constants.FEATURE_ROUTE_REDISTRIBUTION_CONFIG))
        with mock.patch.object(self.policy_lib, "get_version",
                               return_value=nsxlib_testcase.LATEST_VERSION):
            self.assertTrue(
                self.policy_lib.feature_supported(
                    nsx_constants.FEATURE_ROUTE_REDISTRIBUTION_CONFIG))


class TestPolicyTier1Segment(NsxPolicyLibTestCase):

    def setUp(self, *args, **kwargs):
        super(TestPolicyTier1Segment, self).setUp()
        self.resourceApi = self.policy_lib.tier1_segment

    def test_create(self):
        name = 'test'
        description = 'desc'
        tier1_id = '111'
        ip_pool_id = 'external-ip-pool'

        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            result = self.resourceApi.create_or_overwrite(
                name, description=description,
                tier1_id=tier1_id,
                ip_pool_id=ip_pool_id,
                tenant=TEST_TENANT)

            expected_def = core_defs.Tier1SegmentDef(
                segment_id=mock.ANY,
                name=name,
                description=description,
                tier1_id=tier1_id,
                ip_pool_id=ip_pool_id,
                tenant=TEST_TENANT)

            self.assert_called_with_def(api_call, expected_def)
            self.assertIsNotNone(result)

    def test_delete(self):
        tier1_id = '111'
        segment_id = '111'
        with mock.patch.object(self.policy_api, "delete") as api_call:
            self.resourceApi.delete(tier1_id, segment_id, tenant=TEST_TENANT)
            expected_def = core_defs.Tier1SegmentDef(
                tier1_id=tier1_id, segment_id=segment_id, tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_get(self):
        tier1_id = '111'
        segment_id = '111'
        with mock.patch.object(self.policy_api, "get",
                               return_value={'id': segment_id}) as api_call:
            result = self.resourceApi.get(tier1_id, segment_id,
                                          tenant=TEST_TENANT)
            expected_def = core_defs.Tier1SegmentDef(
                tier1_id=tier1_id, segment_id=segment_id, tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(segment_id, result['id'])

    def test_list(self):
        tier1_id = '111'
        with mock.patch.object(self.policy_api, "list",
                               return_value={'results': []}) as api_call:
            result = self.resourceApi.list(tier1_id=tier1_id,
                                           tenant=TEST_TENANT)
            expected_def = core_defs.Tier1SegmentDef(tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual([], result)

    def test_update(self):
        tier1_id = '111'
        segment_id = '111'
        name = 'new name'
        with self.mock_get(tier1_id, name), \
            self.mock_create_update() as update_call:
            self.resourceApi.update(segment_id=segment_id,
                                    tier1_id=tier1_id,
                                    name=name,
                                    tenant=TEST_TENANT)
            expected_def = core_defs.Tier1SegmentDef(
                tier1_id=tier1_id, segment_id=segment_id,
                name=name, tenant=TEST_TENANT)
            self.assert_called_with_def(update_call, expected_def)

    def test_build_subnet(self):
        gateway_address = "10.0.0.1/24"
        dhcp_ranges = None
        subnet = self.resourceApi.build_subnet(
            gateway_address=gateway_address, dhcp_ranges=dhcp_ranges)
        self.assertEqual(gateway_address, subnet.gateway_address)
        self.assertEqual(dhcp_ranges, subnet.dhcp_ranges)

    def test_build_dhcp_config_v4(self):
        server_address = "10.0.0.2/24"
        dns_servers = ["10.0.0.3/24"]
        lease_time = 36600
        dhcp_config_v4 = self.resourceApi.build_dhcp_config_v4(
            server_address, dns_servers=dns_servers, lease_time=lease_time)
        self.assertEqual(server_address, dhcp_config_v4.server_address)
        self.assertEqual(dns_servers, dhcp_config_v4.dns_servers)
        self.assertEqual(lease_time, dhcp_config_v4.lease_time)

    def test_build_dhcp_config_v6(self):
        server_address = "2000::01ab/64"
        dns_servers = ["2000::01ac/64"]
        lease_time = 36600
        dhcp_config_v6 = self.resourceApi.build_dhcp_config_v6(
            server_address, dns_servers=dns_servers, lease_time=lease_time)
        self.assertEqual(server_address, dhcp_config_v6.server_address)
        self.assertEqual(dns_servers, dhcp_config_v6.dns_servers)
        self.assertEqual(lease_time, dhcp_config_v6.lease_time)


class TestPolicySegment(NsxPolicyLibTestCase):

    def setUp(self, *args, **kwargs):
        super(TestPolicySegment, self).setUp()
        self.resourceApi = self.policy_lib.segment

    def _test_create(self, tier1_id=None, tier0_id=None, mdproxy=None,
                     dhcp_server=None, admin_state=None,
                     ip_pool_id='external-ip-pool', ls_id=None,
                     unique_id=None, tz_id=None, ep_id=None, overlay_id=None):
        name = 'test'
        description = 'desc'
        subnets = [core_defs.Subnet(gateway_address="2.2.2.0/24")]
        kwargs = {'description': description,
                  'subnets': subnets,
                  'ip_pool_id': ip_pool_id,
                  'tenant': TEST_TENANT}
        if tier1_id:
            kwargs['tier1_id'] = tier1_id

        if tier0_id:
            kwargs['tier0_id'] = tier0_id

        if mdproxy:
            kwargs['metadata_proxy_id'] = mdproxy

        if dhcp_server:
            kwargs['dhcp_server_config_id'] = dhcp_server
        if admin_state:
            kwargs['admin_state'] = admin_state
        if overlay_id:
            kwargs['overlay_id'] = overlay_id

        if ls_id:
            kwargs['ls_id'] = ls_id
        if unique_id:
            kwargs['unique_id'] = unique_id

        if tz_id:
            kwargs['transport_zone_id'] = tz_id
        if ep_id:
            kwargs['ep_id'] = ep_id

        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            result = self.resourceApi.create_or_overwrite(name, **kwargs)

            if admin_state:
                kwargs['admin_state'] = admin_state if 'UP' else 'DOWN'
            expected_def = core_defs.SegmentDef(
                nsx_version=nsxlib_testcase.LATEST_VERSION,
                segment_id=mock.ANY,
                name=name,
                **kwargs)

            self.assert_called_with_def(api_call, expected_def)
            self.assertIsNotNone(result)
            if ip_pool_id is None:
                expected_advanced_config = {'address_pool_paths': []}
            else:
                ip_pool_def = core_defs.IpPoolDef(ip_pool_id=ip_pool_id)
                ip_pool_path = ip_pool_def.get_resource_full_path()
                expected_advanced_config = {
                    'address_pool_paths': [ip_pool_path]}
            self.assertEqual(expected_def.get_obj_dict()['advanced_config'],
                             expected_advanced_config)

    def test_create_with_t1(self):
        self._test_create(tier1_id='111')

    def test_create_with_t0(self):
        self._test_create(tier0_id='000')

    def test_create_with_t0_t1_fail(self):
        self.assertRaises(nsxlib_exc.InvalidInput,
                          self.resourceApi.create_or_overwrite,
                          'seg-name', tier1_id='111', tier0_id='000')

    def test_create_with_mdproxy(self):
        self._test_create(mdproxy='md1')

    def test_create_with_dhcp_server_config(self):
        self._test_create(dhcp_server='dhcp1')

    def test_create_with_admin_state_up(self):
        self._test_create(admin_state=True)

    def test_create_with_admin_state_down(self):
        self._test_create(admin_state=False)

    def test_create_without_ip_pool(self):
        self._test_create(ip_pool_id=None)

    def test_create_with_ls_id(self):
        self._test_create(ls_id='lsid1')

    def test_create_with_unique_id(self):
        self._test_create(unique_id='lsid1')

    def test_create_with_transport_zone_id(self):
        self._test_create(tz_id='tz_id1', ep_id='ep_id1')

    def test_create_with_transport_zone_id_and_default_ep(self):
        self._test_create(tz_id='tz_id1')

    def test_create_with_overlay_id(self):
        self._test_create(overlay_id=100)

    def test_delete(self):
        segment_id = '111'
        with mock.patch.object(self.policy_api, "delete") as api_call:
            self.resourceApi.delete(segment_id, tenant=TEST_TENANT)
            expected_def = core_defs.SegmentDef(segment_id=segment_id,
                                                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_get(self):
        segment_id = '111'
        with mock.patch.object(self.policy_api, "get",
                               return_value={'id': segment_id}) as api_call:
            result = self.resourceApi.get(segment_id, tenant=TEST_TENANT)
            expected_def = core_defs.SegmentDef(segment_id=segment_id,
                                                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(segment_id, result['id'])

    def test_list(self):
        with mock.patch.object(self.policy_api, "list",
                               return_value={'results': []}) as api_call:
            result = self.resourceApi.list(tenant=TEST_TENANT)
            expected_def = core_defs.SegmentDef(tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual([], result)

    def test_update(self):
        segment_id = '111'
        name = 'new name'
        admin_state = False
        with self.mock_get(segment_id, name), \
            self.mock_create_update() as update_call:

            self.resourceApi.update(segment_id,
                                    name=name,
                                    admin_state=admin_state,
                                    tenant=TEST_TENANT)
            expected_def = core_defs.SegmentDef(
                nsx_version=nsxlib_testcase.LATEST_VERSION,
                segment_id=segment_id,
                name=name,
                admin_state=admin_state,
                tenant=TEST_TENANT)
            self.assert_called_with_def(update_call, expected_def)

    def test_remove_connectivity_and_subnets(self):
        segment_id = '111'
        with mock.patch.object(self.policy_api, "get",
                               return_value={'id': segment_id}) as api_get,\
            mock.patch.object(self.policy_api.client, "update") as api_put:
            self.resourceApi.remove_connectivity_and_subnets(
                segment_id, tenant=TEST_TENANT)
            api_get.assert_called_once()
            api_put.assert_called_once_with(
                '%s/segments/%s' % (TEST_TENANT, segment_id),
                {'id': segment_id, 'connectivity_path': None, 'subnets': None})

    def test_remove_connectivity_path(self):
        segment_id = '111'
        with mock.patch.object(self.policy_api, "get",
                               return_value={'id': segment_id}) as api_get,\
            mock.patch.object(self.policy_api.client, "update") as api_put:
            self.resourceApi.remove_connectivity_path(
                segment_id, tenant=TEST_TENANT)
            api_get.assert_called_once()
            api_put.assert_called_once_with(
                '%s/segments/%s' % (TEST_TENANT, segment_id),
                {'id': segment_id, 'connectivity_path': None})

    def test_build_subnet(self):
        gateway_address = "10.0.0.1/24"
        dhcp_ranges = None
        subnet = self.resourceApi.build_subnet(
            gateway_address=gateway_address, dhcp_ranges=dhcp_ranges)
        self.assertEqual(gateway_address, subnet.gateway_address)
        self.assertEqual(dhcp_ranges, subnet.dhcp_ranges)

    def test_get_tz_id(self):
        segment_id = '111'
        tz_id = '222'
        tz_path = 'dummy-path/%s' % tz_id
        with mock.patch.object(
            self.policy_api, "get",
            return_value={'id': segment_id,
                          'transport_zone_path': tz_path}) as api_get:
            result = self.resourceApi.get_transport_zone_id(
                segment_id, tenant=TEST_TENANT)
            api_get.assert_called_once()
            self.assertEqual(tz_id, result)

    def test_set_admin_state(self):
        # NSX version 3 & up
        segment_id = '111'
        with mock.patch.object(self.policy_api.client, "patch") as api_patch:
            self.resourceApi.set_admin_state(
                segment_id, False, tenant=TEST_TENANT)
            api_patch.assert_called_once_with(
                '%s/segments/%s' % (TEST_TENANT, segment_id),
                {'id': segment_id, 'admin_state': 'DOWN',
                 'resource_type': 'Segment'},
                headers={'nsx-enable-partial-patch': 'true'})

    def test_set_admin_state_old(self):
        # NSX version before 3
        segment_id = '111'
        with mock.patch.object(self.resourceApi, 'version', '2.5.0'),\
            mock.patch.object(self.resourceApi, 'wait_until_realized'),\
            mock.patch.object(self.resourceApi.nsx_api.logical_switch,
                              "update") as ls_update:
            self.resourceApi.set_admin_state(
                segment_id, True, tenant=TEST_TENANT)
            ls_update.assert_called_once_with(mock.ANY, admin_state=True)


class TestPolicyIpPool(NsxPolicyLibTestCase):

    def setUp(self, *args, **kwargs):
        super(TestPolicyIpPool, self).setUp()
        self.resourceApi = self.policy_lib.ip_pool

    def test_create(self):
        name = 'test'
        description = 'desc'
        ip_pool_id = '111'

        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            result = self.resourceApi.create_or_overwrite(
                name, ip_pool_id, description=description,
                tenant=TEST_TENANT)

            expected_def = core_defs.IpPoolDef(
                ip_pool_id=ip_pool_id,
                name=name,
                description=description,
                tenant=TEST_TENANT)

            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(ip_pool_id, result)

    def test_delete(self):
        ip_pool_id = '111'
        with mock.patch.object(self.policy_api, "delete") as api_call:
            self.resourceApi.delete(ip_pool_id, tenant=TEST_TENANT)
            expected_def = core_defs.IpPoolDef(ip_pool_id=ip_pool_id,
                                               tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_get(self):
        ip_pool_id = '111'
        with mock.patch.object(self.policy_api, "get",
                               return_value={'id': ip_pool_id}) as api_call:
            result = self.resourceApi.get(ip_pool_id, tenant=TEST_TENANT)
            expected_def = core_defs.IpPoolDef(ip_pool_id=ip_pool_id,
                                               tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(ip_pool_id, result['id'])

    def test_list(self):
        with mock.patch.object(self.policy_api, "list",
                               return_value={'results': []}) as api_call:
            result = self.resourceApi.list(tenant=TEST_TENANT)
            expected_def = core_defs.IpPoolDef(tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual([], result)

    def test_update(self):
        ip_pool_id = '111'
        name = 'new name'
        with self.mock_get(ip_pool_id, name), \
            self.mock_create_update() as update_call:

            self.resourceApi.update(ip_pool_id,
                                    name=name,
                                    tenant=TEST_TENANT)
            expected_def = core_defs.IpPoolDef(ip_pool_id=ip_pool_id,
                                               name=name,
                                               tenant=TEST_TENANT)
            self.assert_called_with_def(update_call, expected_def)

    def test_allocate_ip(self):
        ip_pool_id = '111'
        ip_allocation_id = 'alloc-id'
        with mock.patch.object(self.policy_api,
                               "create_or_update") as update_call:
            self.resourceApi.allocate_ip(ip_pool_id,
                                         ip_allocation_id,
                                         tenant=TEST_TENANT)
            expected_def = core_defs.IpPoolAllocationDef(
                ip_pool_id=ip_pool_id,
                ip_allocation_id=ip_allocation_id,
                tenant=TEST_TENANT)
            self.assert_called_with_def(update_call, expected_def)

    def test_release_ip(self):
        ip_pool_id = '111'
        ip_allocation_id = 'alloc-id'
        with mock.patch.object(self.policy_api, "delete") as delete_call:
            self.resourceApi.release_ip(ip_pool_id,
                                        ip_allocation_id,
                                        tenant=TEST_TENANT)
            expected_def = core_defs.IpPoolAllocationDef(
                ip_pool_id=ip_pool_id,
                ip_allocation_id=ip_allocation_id,
                tenant=TEST_TENANT)
            self.assert_called_with_def(delete_call, expected_def)

    def test_allocate_block_subnet(self):
        ip_pool_id = '111'
        ip_block_id = 'block-id'
        size = 256
        ip_subnet_id = 'subnet-id'
        start_ip = '192.168.1.0'

        with mock.patch.object(
                self.policy_api, "create_or_update") as api_call, \
                mock.patch.object(self.resourceApi, 'version',
                                  nsxlib_testcase.LATEST_VERSION):
            self.resourceApi.allocate_block_subnet(
                ip_pool_id, ip_block_id, size, ip_subnet_id,
                tenant=TEST_TENANT, start_ip=start_ip)

            expected_def = core_defs.IpPoolBlockSubnetDef(
                nsx_version=nsxlib_testcase.LATEST_VERSION,
                ip_pool_id=ip_pool_id,
                ip_block_id=ip_block_id,
                ip_subnet_id=ip_subnet_id,
                size=size,
                tenant=TEST_TENANT,
                start_ip=start_ip)
            self.assert_called_with_def(api_call, expected_def)

    def test_allocate_block_subnet_with_unsupported_attribute(self):
        ip_pool_id = '111'
        ip_block_id = 'block-id'
        size = 256
        ip_subnet_id = 'subnet-id'
        start_ip = '192.168.1.0'

        with mock.patch.object(
                self.policy_api, "create_or_update") as api_call, \
                mock.patch.object(self.resourceApi, 'version', '2.5.0'):
            self.resourceApi.allocate_block_subnet(
                ip_pool_id, ip_block_id, size, ip_subnet_id,
                tenant=TEST_TENANT, start_ip=start_ip)

            expected_def = core_defs.IpPoolBlockSubnetDef(
                nsx_version='2.5.0',
                ip_pool_id=ip_pool_id,
                ip_block_id=ip_block_id,
                ip_subnet_id=ip_subnet_id,
                size=size,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_release_block_subnet(self):
        ip_pool_id = '111'
        ip_subnet_id = 'subnet-id'
        with mock.patch.object(self.policy_api, "delete") as delete_call:
            self.resourceApi.release_block_subnet(ip_pool_id,
                                                  ip_subnet_id,
                                                  tenant=TEST_TENANT)
            expected_def = core_defs.IpPoolBlockSubnetDef(
                ip_pool_id=ip_pool_id,
                ip_subnet_id=ip_subnet_id,
                tenant=TEST_TENANT)
            self.assert_called_with_def(delete_call, expected_def)

    def test_list_block_subnets(self):
        ip_pool_id = 'ip-pool-id'
        api_results = {
            'results': [{'id': 'static_subnet_1',
                         'resource_type': 'IpAddressPoolStaticSubnet'},
                        {'id': 'block_subnet_2',
                         'resource_type': 'IpAddressPoolBlockSubnet'}]
        }
        with mock.patch.object(
            self.policy_api, "list", return_value=api_results) as api_call:
            result = self.resourceApi.list_block_subnets(
                ip_pool_id, tenant=TEST_TENANT)
            expected_def = core_defs.IpPoolBlockSubnetDef(
                ip_pool_id=ip_pool_id,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            expected_result = [{'id': 'block_subnet_2',
                                'resource_type': 'IpAddressPoolBlockSubnet'}]
            self.assertEqual(result, expected_result)

    def test_get_ip_subnet_realization_info(self):
        ip_pool_id = '111'
        ip_subnet_id = 'subnet-id'
        result = {'extended_attributes': [{'values': ['5.5.0.0/24'],
                                           'key': 'cidr'}]}
        with mock.patch.object(
            self.resourceApi, "_get_realization_info",
            return_value=result) as api_get:
            self.resourceApi.get_ip_subnet_realization_info(
                ip_pool_id, ip_subnet_id, tenant=TEST_TENANT)
            api_get.assert_called_once()
        # Test with wait set to True
        with mock.patch.object(
            self.resourceApi, "_wait_until_realized",
            return_value=result) as api_get:
            self.resourceApi.get_ip_subnet_realization_info(
                ip_pool_id, ip_subnet_id, tenant=TEST_TENANT,
                wait=True)
            api_get.assert_called_once()

    def test_get_ip_block_subnet_cidr(self):
        ip_pool_id = '111'
        ip_subnet_id = 'subnet-id'
        result = {'extended_attributes': [{'values': ['5.5.0.0/24'],
                                           'key': 'cidr'}]}
        with mock.patch.object(
            self.resourceApi, "_get_realization_info",
            return_value=result) as api_get:
            cidr = self.resourceApi.get_ip_block_subnet_cidr(
                ip_pool_id, ip_subnet_id, tenant=TEST_TENANT)
            self.assertEqual(['5.5.0.0/24'], cidr)
            api_get.assert_called_once()

    def test_get_ip_alloc_realization_info(self):
        ip_pool_id = '111'
        ip_allocation_id = 'alloc-id'
        result = {'extended_attributes': [{'values': ['5.5.0.8']}]}
        with mock.patch.object(
            self.resourceApi, "_get_realization_info",
            return_value=result) as api_get:
            self.resourceApi.get_ip_alloc_realization_info(
                ip_pool_id, ip_allocation_id, tenant=TEST_TENANT)
            api_get.assert_called_once()
        # Test with wait set to True
        with mock.patch.object(
            self.resourceApi, "_wait_until_realized",
            return_value=result) as api_get:
            self.resourceApi.get_ip_alloc_realization_info(
                ip_pool_id, ip_allocation_id, tenant=TEST_TENANT,
                wait=True)
            api_get.assert_called_once()

    def test_get_realized_allocated_ip(self):
        ip_pool_id = '111'
        ip_allocation_id = 'alloc-id'
        result = {'extended_attributes': [{'values': ['5.5.0.8']}]}
        with mock.patch.object(
            self.resourceApi, "_get_realization_info",
            return_value=result) as api_get:
            ip = self.resourceApi.get_realized_allocated_ip(
                ip_pool_id, ip_allocation_id, tenant=TEST_TENANT)
            self.assertEqual('5.5.0.8', ip)
            api_get.assert_called_once()

    def test_create_or_update_static_subnet(self):
        ip_pool_id = 'ip-pool-id'
        ip_subnet_id = 'static-subnet-id'
        cidr = '10.10.10.0/24'
        allocation_ranges = [{'start': '10.10.10.2', 'end': '10.10.10.250'}]

        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            self.resourceApi.create_or_update_static_subnet(
                ip_pool_id, cidr, allocation_ranges, ip_subnet_id,
                tenant=TEST_TENANT)

            expected_def = core_defs.IpPoolStaticSubnetDef(
                ip_pool_id=ip_pool_id,
                cidr=cidr,
                allocation_ranges=allocation_ranges,
                ip_subnet_id=ip_subnet_id,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_release_static_subnet(self):
        ip_pool_id = 'ip-pool-id'
        ip_subnet_id = 'static-subnet-id'
        with mock.patch.object(self.policy_api, "delete") as delete_call:
            self.resourceApi.release_static_subnet(
                ip_pool_id, ip_subnet_id, tenant=TEST_TENANT)
            expected_def = core_defs.IpPoolStaticSubnetDef(
                ip_pool_id=ip_pool_id,
                ip_subnet_id=ip_subnet_id,
                tenant=TEST_TENANT)
            self.assert_called_with_def(delete_call, expected_def)

    def test_list_static_subnet(self):
        ip_pool_id = 'ip-pool-id'
        api_results = {
            'results': [{'id': 'static_subnet_1',
                         'resource_type': 'IpAddressPoolStaticSubnet'},
                        {'id': 'block_subnet_2',
                         'resource_type': 'IpAddressPoolBlockSubnet'}]
        }
        with mock.patch.object(
            self.policy_api, "list", return_value=api_results) as api_call:
            result = self.resourceApi.list_static_subnets(
                ip_pool_id, tenant=TEST_TENANT)
            expected_def = core_defs.IpPoolStaticSubnetDef(
                ip_pool_id=ip_pool_id,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            expected_result = [{'id': 'static_subnet_1',
                                'resource_type': 'IpAddressPoolStaticSubnet'}]
            self.assertEqual(result, expected_result)

    def test_get_static_subnet(self):
        ip_pool_id = 'ip-pool-id'
        ip_subnet_id = 'static-subnet-id'
        with mock.patch.object(self.policy_api, "get") as api_call:
            self.resourceApi.get_static_subnet(
                ip_pool_id, ip_subnet_id, tenant=TEST_TENANT)
            expected_def = core_defs.IpPoolStaticSubnetDef(
                ip_pool_id=ip_pool_id,
                ip_subnet_id=ip_subnet_id,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_get_realization_info(self):
        ip_pool_id = '111'
        with mock.patch.object(
            self.resourceApi, "_get_realization_info") as api_call:
            self.resourceApi.get_realization_info(
                ip_pool_id, tenant=TEST_TENANT)
            expected_def = core_defs.IpPoolDef(
                ip_pool_id=ip_pool_id,
                tenant=TEST_TENANT)
            self.assert_called_with_def_and_dict(api_call, expected_def, {})

    def test_get_static_subnet_realization_info(self):
        ip_pool_id = 'ip-pool-id'
        ip_subnet_id = 'static-subnet-id'
        result = {'extended_attributes': [
            {'values': '10.10.10.0/24', 'key': 'cidr'},
            {'values': [{'value': '10.10.10.2', 'key': 'start'},
                        {'value': '10.10.10.250', 'key': 'end'}],
             'key': 'allocation_ranges'}]}
        with mock.patch.object(
            self.resourceApi, "_get_realization_info",
            return_value=result) as api_get:
            self.resourceApi.get_ip_subnet_realization_info(
                ip_pool_id, ip_subnet_id, tenant=TEST_TENANT,
                subnet_type=constants.IPPOOL_STATIC_SUBNET)
            api_get.assert_called_once()
        # Test with wait set to True
        with mock.patch.object(
            self.resourceApi, "_wait_until_realized",
            return_value=result) as api_get:
            self.resourceApi.get_ip_subnet_realization_info(
                ip_pool_id, ip_subnet_id, tenant=TEST_TENANT,
                wait=True, subnet_type=constants.IPPOOL_STATIC_SUBNET)
            api_get.assert_called_once()

    def test_get_ip_subnet_realization_info_timeout(self):
        ip_pool_id = '111'
        ip_subnet_id = 'subnet-id'
        subnet_id = 'realized_111'
        pool_id = 'realized_222'
        info = [{'state': constants.STATE_UNREALIZED,
                 'realization_specific_identifier': subnet_id,
                 'entity_type': 'IpBlockSubnet'},
                {'state': constants.STATE_REALIZED,
                 'realization_specific_identifier': pool_id,
                 'entity_type': 'IpPool'}]
        with mock.patch.object(self.resourceApi, "_get_realization_info",
                               return_value=info):
            self.assertRaises(nsxlib_exc.RealizationTimeoutError,
                              self.resourceApi.get_ip_subnet_realization_info,
                              ip_pool_id, ip_subnet_id, tenant=TEST_TENANT,
                              wait=True, all_results=True)

    def test_get_ip_subnet_realization_info_error(self):
        ip_pool_id = '111'
        ip_subnet_id = 'subnet-id'
        subnet_id = 'realized_111'
        info = [{'state': constants.STATE_REALIZED,
                 'realization_specific_identifier': subnet_id,
                 'entity_type': 'IpBlockSubnet'},
                {'state': constants.STATE_ERROR,
                 'alarms': [{'message': 'dummy',
                             'error_details': {
                                 'error_code': 5109}}],
                 'entity_type': 'IpPool'}]
        with mock.patch.object(self.resourceApi, "_get_realization_info",
                               return_value=info):
            self.assertRaises(nsxlib_exc.RealizationErrorStateError,
                              self.resourceApi.get_ip_subnet_realization_info,
                              ip_pool_id, ip_subnet_id, tenant=TEST_TENANT,
                              wait=True, all_results=True)
        with mock.patch.object(self.resourceApi, "_get_realization_info",
                               return_value=info):
            with self.assertRaises(nsxlib_exc.RealizationErrorStateError) as e:
                self.resourceApi.get_ip_subnet_realization_info(
                    ip_pool_id, ip_subnet_id, tenant=TEST_TENANT,
                    wait=True, all_results=True)
            self.assertTrue(e.exception.msg.endswith('dummy'))
            self.assertEqual(e.exception.error_code, 5109)
            self.assertEqual(e.exception.related_error_codes, [])

    def test_get_ip_subnet_realization_info_succeed(self):
        ip_pool_id = '111'
        ip_subnet_id = 'subnet-id'
        subnet_id = 'realized_111'
        pool_id = 'realized_222'
        info = [{'state': constants.STATE_REALIZED,
                 'realization_specific_identifier': subnet_id,
                 'entity_type': 'IpBlockSubnet'},
                {'state': constants.STATE_REALIZED,
                 'realization_specific_identifier': pool_id,
                 'entity_type': 'IpPool'}]
        with mock.patch.object(self.resourceApi, "_get_realization_info",
                               return_value=info) as api_get:
            self.resourceApi.get_ip_subnet_realization_info(
                ip_pool_id, ip_subnet_id, tenant=TEST_TENANT,
                wait=True, all_results=True)
            api_get.assert_called_once()

    def test_wait_until_realized_fail(self):
        ip_pool_id = 'p1'
        info = {'state': constants.STATE_UNREALIZED,
                'realization_specific_identifier': ip_pool_id,
                'entity_type': 'IpPool'}
        with mock.patch.object(self.resourceApi, "_get_realization_info",
                               return_value=info):
            self.assertRaises(nsxlib_exc.RealizationTimeoutError,
                              self.resourceApi.wait_until_realized,
                              ip_pool_id, max_attempts=5, sleep=0.1,
                              tenant=TEST_TENANT)

    def test_wait_until_realized_error(self):
        ip_alloc_id = 'ip_alloc_1'
        error_code = 5109
        error_msg = 'Insufficient free IP addresses.'
        info = {'state': constants.STATE_ERROR,
                'realization_specific_identifier': ip_alloc_id,
                'entity_type': 'AllocationIpAddress',
                'alarms': [{
                    'message': error_msg,
                    'error_details': {
                        'error_code': error_code,
                        'module_name': 'id-allocation service',
                        'error_message': error_msg
                    }
                }]}
        with mock.patch.object(self.resourceApi, "_get_realization_info",
                               return_value=info):
            with self.assertRaises(nsxlib_exc.RealizationErrorStateError) as e:
                self.resourceApi.wait_until_realized(
                    ip_alloc_id, tenant=TEST_TENANT)
            self.assertTrue(e.exception.msg.endswith(error_msg))
            self.assertEqual(e.exception.error_code, error_code)
            self.assertEqual(e.exception.related_error_codes, [])

    def test_wait_until_realized_succeed(self):
        ip_pool_id = 'p1'
        info = {'state': constants.STATE_REALIZED,
                'realization_specific_identifier': ip_pool_id,
                'entity_type': 'IpPool'}
        with mock.patch.object(self.resourceApi, "_get_realization_info",
                               return_value=info):
            actual_info = self.resourceApi.wait_until_realized(
                ip_pool_id, max_attempts=5, sleep=0.1, tenant=TEST_TENANT)
            self.assertEqual(info, actual_info)


class TestPolicySegmentPort(NsxPolicyLibTestCase):

    def setUp(self, *args, **kwargs):
        super(TestPolicySegmentPort, self).setUp()
        self.resourceApi = self.policy_lib.segment_port

    def test_feature_supported(self):
        with mock.patch.object(self.policy_lib, "get_version",
                               return_value='2.5.0'):
            self.assertFalse(
                self.policy_lib.feature_supported(
                    nsx_constants.FEATURE_SWITCH_HYPERBUS_MODE))
        with mock.patch.object(self.policy_lib, "get_version",
                               return_value=nsxlib_testcase.LATEST_VERSION):
            self.assertTrue(
                self.policy_lib.feature_supported(
                    nsx_constants.FEATURE_SWITCH_HYPERBUS_MODE))

    def test_create(self):
        name = 'test'
        description = 'desc'
        segment_id = "segment"
        address_bindings = []
        attachment_type = "CHILD"
        vif_id = "vif"
        app_id = "app"
        context_id = "context"
        traffic_tag = 10
        allocate_addresses = "BOTH"
        tags = [{'scope': 'a', 'tag': 'b'}]
        hyperbus_mode = 'DISABLE'
        admin_state = True
        init_state = 'RESTORE_VIF'

        with mock.patch.object(
            self.policy_api, "create_or_update") as api_call, \
            mock.patch.object(self.resourceApi, 'version',
                              nsxlib_testcase.LATEST_VERSION):
            result = self.resourceApi.create_or_overwrite(
                name, segment_id, description=description,
                address_bindings=address_bindings,
                attachment_type=attachment_type, vif_id=vif_id, app_id=app_id,
                context_id=context_id, traffic_tag=traffic_tag,
                allocate_addresses=allocate_addresses,
                hyperbus_mode=hyperbus_mode, admin_state=admin_state,
                tags=tags,
                tenant=TEST_TENANT,
                init_state=init_state)

            expected_def = core_defs.SegmentPortDef(
                nsx_version=nsxlib_testcase.LATEST_VERSION,
                segment_id=segment_id,
                port_id=mock.ANY,
                name=name,
                description=description,
                address_bindings=address_bindings,
                attachment_type=attachment_type,
                vif_id=vif_id,
                app_id=app_id,
                context_id=context_id,
                traffic_tag=traffic_tag,
                allocate_addresses=allocate_addresses,
                admin_state=admin_state,
                tags=tags,
                tenant=TEST_TENANT,
                hyperbus_mode=hyperbus_mode,
                init_state=init_state)

            self.assert_called_with_def(api_call, expected_def)
            self.assertIsNotNone(result)

    def test_create_with_unsupported_attribute(self):
        name = 'test'
        description = 'desc'
        segment_id = "segment"
        address_bindings = []
        attachment_type = "CHILD"
        vif_id = "vif"
        app_id = "app"
        context_id = "context"
        traffic_tag = 10
        allocate_addresses = "BOTH"
        tags = [{'scope': 'a', 'tag': 'b'}]
        hyperbus_mode = 'DISABLE'
        init_state = 'RESTORE_VIF'

        with mock.patch.object(
            self.policy_api, "create_or_update") as api_call, \
            mock.patch.object(self.resourceApi, 'version', '0.0.0'):
            result = self.resourceApi.create_or_overwrite(
                name, segment_id, description=description,
                address_bindings=address_bindings,
                attachment_type=attachment_type, vif_id=vif_id, app_id=app_id,
                context_id=context_id, traffic_tag=traffic_tag,
                allocate_addresses=allocate_addresses, tags=tags,
                tenant=TEST_TENANT, hyperbus_mode=hyperbus_mode,
                init_state=init_state)
            expected_def = core_defs.SegmentPortDef(
                nsx_version=self.policy_lib.get_version(),
                segment_id=segment_id,
                port_id=mock.ANY,
                name=name,
                description=description,
                address_bindings=address_bindings,
                attachment_type=attachment_type,
                vif_id=vif_id,
                app_id=app_id,
                context_id=context_id,
                traffic_tag=traffic_tag,
                allocate_addresses=allocate_addresses,
                tags=tags,
                tenant=TEST_TENANT)

            self.assert_called_with_def(api_call, expected_def)
            self.assertIsNotNone(result)

    def test_create_with_invalid_init_state(self):
        name = 'test'
        description = 'desc'
        segment_id = "segment"
        address_bindings = []
        attachment_type = "CHILD"
        vif_id = "vif"
        app_id = "app"
        context_id = "context"
        traffic_tag = 10
        allocate_addresses = "BOTH"
        tags = [{'scope': 'a', 'tag': 'b'}]
        hyperbus_mode = 'DISABLE'
        init_state = 'OK'

        with mock.patch.object(
            self.policy_api, "create_or_update") as api_call, \
            mock.patch.object(self.resourceApi, 'version',
                              nsxlib_testcase.LATEST_VERSION):
            with self.assertRaises(nsxlib_exc.InvalidInput):
                self.resourceApi.create_or_overwrite(
                    name, segment_id, description=description,
                    address_bindings=address_bindings,
                    attachment_type=attachment_type, vif_id=vif_id,
                    app_id=app_id,
                    context_id=context_id, traffic_tag=traffic_tag,
                    allocate_addresses=allocate_addresses, tags=tags,
                    tenant=TEST_TENANT, hyperbus_mode=hyperbus_mode,
                    init_state=init_state)
                actual_def = api_call.call_args_list[0][0][0]
                actual_def.get_obj_dict()

    def test_attach(self):
        segment_id = "segment"
        port_id = "port"
        attachment_type = "CHILD"
        vif_id = "vif"
        app_id = "app"
        context_id = "context"
        traffic_tag = 10
        allocate_addresses = "BOTH"
        tags = [{'scope': 'a', 'tag': 'b'}]
        hyperbus_mode = 'DISABLE'
        with mock.patch.object(
            self.policy_api, "create_or_update") as api_call, \
            mock.patch.object(self.resourceApi, 'version',
                              nsxlib_testcase.LATEST_VERSION):
            self.resourceApi.attach(
                segment_id, port_id,
                attachment_type=attachment_type, vif_id=vif_id, app_id=app_id,
                context_id=context_id, traffic_tag=traffic_tag,
                allocate_addresses=allocate_addresses,
                hyperbus_mode=hyperbus_mode, tags=tags,
                tenant=TEST_TENANT)

            expected_def = core_defs.SegmentPortDef(
                nsx_version=nsxlib_testcase.LATEST_VERSION,
                segment_id=segment_id,
                port_id=port_id,
                attachment_type=attachment_type,
                vif_id=vif_id,
                app_id=app_id,
                context_id=context_id,
                traffic_tag=traffic_tag,
                allocate_addresses=allocate_addresses,
                hyperbus_mode=hyperbus_mode,
                tags=tags,
                tenant=TEST_TENANT)

            self.assert_called_with_def(api_call, expected_def)

    def test_detach(self):
        segment_id = "segment"
        port_id = "port"
        tags = [{'scope': 'a', 'tag': 'b'}]
        with mock.patch.object(self.policy_api.client,
                               "get", return_value={}) as api_get,\
            mock.patch.object(self.policy_api.client,
                              "update") as api_put:
            self.resourceApi.detach(
                segment_id, port_id, tags=tags,
                tenant=TEST_TENANT)

            api_get.assert_called_once()
            api_put.assert_called_once_with(
                "%s/segments/%s/ports/%s" % (TEST_TENANT, segment_id, port_id),
                {'attachment': None, 'tags': tags})

    def test_detach_with_vif(self):
        segment_id = "segment"
        port_id = "port"
        vif_id = "abc"
        tags = [{'scope': 'a', 'tag': 'b'}]
        with mock.patch.object(self.policy_api.client,
                               "get", return_value={}) as api_get,\
            mock.patch.object(self.policy_api.client,
                              "update") as api_put:
            self.resourceApi.detach(
                segment_id, port_id, tags=tags, vif_id=vif_id,
                tenant=TEST_TENANT)

            api_get.assert_called_once()
            api_put.assert_called_once_with(
                "%s/segments/%s/ports/%s" % (TEST_TENANT, segment_id, port_id),
                {'attachment': {'id': vif_id}, 'tags': tags})

    def test_set_admin_state(self):
        # NSX version 3 & up
        segment_id = '111'
        port_id = '222'
        with mock.patch.object(self.policy_api.client, "patch") as api_patch:
            self.resourceApi.set_admin_state(
                segment_id, port_id, False, tenant=TEST_TENANT)
            api_patch.assert_called_once_with(
                '%s/segments/%s/ports/%s' % (TEST_TENANT, segment_id, port_id),
                {'resource_type': 'SegmentPort', 'id': port_id,
                 'admin_state': 'DOWN'},
                headers={'nsx-enable-partial-patch': 'true'})

    def test_set_admin_state_old(self):
        # NSX version before 3
        segment_id = '111'
        port_id = '222'
        with mock.patch.object(self.resourceApi, 'version', '2.5.0'),\
            mock.patch.object(self.resourceApi, 'wait_until_realized'),\
            mock.patch.object(self.resourceApi.nsx_api.logical_port,
                              "update") as lp_update:
            self.resourceApi.set_admin_state(
                segment_id, port_id, True, tenant=TEST_TENANT)
            lp_update.assert_called_once_with(
                mock.ANY, False, admin_state=True)


class TestPolicySegmentProfileBase(NsxPolicyLibTestCase):

    def setUp(self, resource_api_name='segment_security_profile',
              resource_def=core_defs.SegmentSecurityProfileDef):
        super(TestPolicySegmentProfileBase, self).setUp()
        self.resourceApi = getattr(self.policy_lib, resource_api_name)
        self.resourceDef = resource_def

    def test_create(self):
        name = 'test'
        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            result = self.resourceApi.create_or_overwrite(
                name,
                tenant=TEST_TENANT)

            expected_def = self.resourceDef(
                profile_id=mock.ANY,
                name=name,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertIsNotNone(result)

    def test_delete(self):
        profile_id = '111'
        with mock.patch.object(self.policy_api, "delete") as api_call:
            self.resourceApi.delete(profile_id, tenant=TEST_TENANT)
            expected_def = self.resourceDef(profile_id=profile_id,
                                            tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_get(self):
        profile_id = '111'
        with mock.patch.object(self.policy_api, "get",
                               return_value={'id': profile_id}) as api_call:
            result = self.resourceApi.get(profile_id, tenant=TEST_TENANT)
            expected_def = self.resourceDef(profile_id=profile_id,
                                            tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(profile_id, result['id'])

    def test_get_by_name(self):
        name = 'test'
        with mock.patch.object(
            self.policy_api, "list",
            return_value={'results': [{'display_name': name}]}) as api_call:
            obj = self.resourceApi.get_by_name(name, tenant=TEST_TENANT)
            self.assertIsNotNone(obj)
            expected_def = self.resourceDef(tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_list(self):
        with mock.patch.object(self.policy_api, "list",
                               return_value={'results': []}) as api_call:
            result = self.resourceApi.list(tenant=TEST_TENANT)
            expected_def = self.resourceDef(tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual([], result)

    def test_update(self):
        profile_id = '111'
        name = 'new name'
        with self.mock_get(profile_id, name), \
            self.mock_create_update() as update_call:
            self.resourceApi.update(profile_id,
                                    name=name,
                                    tenant=TEST_TENANT)
            expected_def = self.resourceDef(profile_id=profile_id,
                                            name=name,
                                            tenant=TEST_TENANT)
            self.assert_called_with_def(
                update_call, expected_def)


class TestPolicyQosProfile(TestPolicySegmentProfileBase):

    def setUp(self):
        super(TestPolicyQosProfile, self).setUp(
            resource_api_name='qos_profile',
            resource_def=core_defs.QosProfileDef)

    def test_create_with_params(self):
        name = 'test'
        description = 'desc'
        dscp = self.resourceApi.build_dscp(trusted=False, priority=7)
        limiter = self.resourceApi.build_ingress_rate_limiter(
            average_bandwidth=700,
            enabled=True)
        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            result = self.resourceApi.create_or_overwrite(
                name,
                description=description,
                dscp=dscp,
                shaper_configurations=[limiter],
                tenant=TEST_TENANT)

            expected_def = self.resourceDef(
                profile_id=mock.ANY,
                name=name,
                description=description,
                dscp=dscp,
                shaper_configurations=[limiter],
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertIsNotNone(result)


class TestPolicySpoofguardProfile(TestPolicySegmentProfileBase):

    def setUp(self):
        super(TestPolicySpoofguardProfile, self).setUp(
            resource_api_name='spoofguard_profile',
            resource_def=core_defs.SpoofguardProfileDef)


class TestPolicyIpDiscoveryProfile(TestPolicySegmentProfileBase):

    def setUp(self):
        super(TestPolicyIpDiscoveryProfile, self).setUp(
            resource_api_name='ip_discovery_profile',
            resource_def=core_defs.IpDiscoveryProfileDef)


class TestPolicyMacDiscoveryProfile(TestPolicySegmentProfileBase):

    def setUp(self):
        super(TestPolicyMacDiscoveryProfile, self).setUp(
            resource_api_name='mac_discovery_profile',
            resource_def=core_defs.MacDiscoveryProfileDef)


class TestPolicyWAFProfile(TestPolicySegmentProfileBase):

    def setUp(self):
        super(TestPolicyWAFProfile, self).setUp(
            resource_api_name='waf_profile',
            resource_def=core_defs.WAFProfileDef)


class TestPolicySegmentSecurityProfile(TestPolicySegmentProfileBase):

    def test_create_with_params(self):
        name = 'test'
        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            result = self.resourceApi.create_or_overwrite(
                name,
                bpdu_filter_enable=True,
                dhcp_client_block_enabled=False,
                dhcp_client_block_v6_enabled=True,
                dhcp_server_block_enabled=False,
                dhcp_server_block_v6_enabled=True,
                non_ip_traffic_block_enabled=False,
                ra_guard_enabled=True,
                rate_limits_enabled=False,
                tenant=TEST_TENANT)

            expected_def = self.resourceDef(
                profile_id=mock.ANY,
                name=name,
                bpdu_filter_enable=True,
                dhcp_client_block_enabled=False,
                dhcp_client_block_v6_enabled=True,
                dhcp_server_block_enabled=False,
                dhcp_server_block_v6_enabled=True,
                non_ip_traffic_block_enabled=False,
                ra_guard_enabled=True,
                rate_limits_enabled=False,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertIsNotNone(result)


class TestPolicySegmentSecProfilesBinding(NsxPolicyLibTestCase):

    def setUp(self, resource_api_name='segment_security_profile_maps',
              resource_def=core_defs.SegmentSecProfilesBindingMapDef):
        super(TestPolicySegmentSecProfilesBinding, self).setUp()
        self.resourceApi = getattr(self.policy_lib, resource_api_name)
        self.resourceDef = resource_def

    def test_create(self):
        name = 'test'
        segment_id = 'seg1'
        prf1 = '1'
        prf2 = '2'
        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            result = self.resourceApi.create_or_overwrite(
                name, segment_id,
                segment_security_profile_id=prf1,
                spoofguard_profile_id=prf2,
                tenant=TEST_TENANT)

            expected_def = self.resourceDef(
                segment_id=segment_id,
                map_id=core_resources.DEFAULT_MAP_ID,
                name=name,
                segment_security_profile_id=prf1,
                spoofguard_profile_id=prf2,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertIsNotNone(result)

    def test_delete(self):
        segment_id = 'seg1'
        with mock.patch.object(self.policy_api, "delete") as api_call:
            self.resourceApi.delete(segment_id, tenant=TEST_TENANT)
            expected_def = self.resourceDef(
                segment_id=segment_id,
                map_id=core_resources.DEFAULT_MAP_ID,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_get(self):
        segment_id = 'seg1'
        with mock.patch.object(self.policy_api, "get",
                               return_value={'id': segment_id}) as api_call:
            result = self.resourceApi.get(segment_id,
                                          tenant=TEST_TENANT)
            expected_def = self.resourceDef(
                segment_id=segment_id,
                map_id=core_resources.DEFAULT_MAP_ID,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(segment_id, result['id'])

    def test_list(self):
        segment_id = 'seg1'
        with mock.patch.object(self.policy_api, "list",
                               return_value={'results': []}) as api_call:
            result = self.resourceApi.list(segment_id,
                                           tenant=TEST_TENANT)
            expected_def = self.resourceDef(
                segment_id=segment_id,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual([], result)

    def test_update(self):
        name = 'new name'
        segment_id = 'seg1'
        prf1 = '1'
        prf2 = '2'
        with self.mock_get(segment_id, name), \
            self.mock_create_update() as update_call:

            self.resourceApi.update(
                segment_id=segment_id,
                name=name,
                segment_security_profile_id=prf1,
                spoofguard_profile_id=prf2,
                tenant=TEST_TENANT)
            expected_def = self.resourceDef(
                segment_id=segment_id,
                map_id=core_resources.DEFAULT_MAP_ID,
                name=name,
                segment_security_profile_id=prf1,
                spoofguard_profile_id=prf2,
                tenant=TEST_TENANT)
            self.assert_called_with_def(
                update_call, expected_def)


class TestPolicySegmentDiscoveryProfilesBinding(NsxPolicyLibTestCase):

    def setUp(self, resource_api_name='segment_discovery_profile_maps',
              resource_def=core_defs.SegmentDiscoveryProfilesBindingMapDef):
        super(TestPolicySegmentDiscoveryProfilesBinding, self).setUp()
        self.resourceApi = getattr(self.policy_lib, resource_api_name)
        self.resourceDef = resource_def

    def test_create(self):
        name = 'test'
        segment_id = 'seg1'
        prf1 = '1'
        prf2 = '2'
        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            result = self.resourceApi.create_or_overwrite(
                name, segment_id,
                ip_discovery_profile_id=prf1,
                mac_discovery_profile_id=prf2,
                tenant=TEST_TENANT)

            expected_def = self.resourceDef(
                segment_id=segment_id,
                map_id=core_resources.DEFAULT_MAP_ID,
                name=name,
                ip_discovery_profile_id=prf1,
                mac_discovery_profile_id=prf2,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertIsNotNone(result)

    def test_delete(self):
        segment_id = 'seg1'
        with mock.patch.object(self.policy_api, "delete") as api_call:
            self.resourceApi.delete(segment_id, tenant=TEST_TENANT)
            expected_def = self.resourceDef(
                segment_id=segment_id,
                map_id=core_resources.DEFAULT_MAP_ID,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_get(self):
        segment_id = 'seg1'
        with mock.patch.object(self.policy_api, "get",
                               return_value={'id': segment_id}) as api_call:
            result = self.resourceApi.get(segment_id,
                                          tenant=TEST_TENANT)
            expected_def = self.resourceDef(
                segment_id=segment_id,
                map_id=core_resources.DEFAULT_MAP_ID,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(segment_id, result['id'])

    def test_list(self):
        segment_id = 'seg1'
        with mock.patch.object(self.policy_api, "list",
                               return_value={'results': []}) as api_call:
            result = self.resourceApi.list(segment_id,
                                           tenant=TEST_TENANT)
            expected_def = self.resourceDef(
                segment_id=segment_id,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual([], result)

    def test_update(self):
        name = 'new name'
        segment_id = 'seg1'
        prf1 = '1'
        prf2 = '2'
        with self.mock_get(segment_id, name), \
            self.mock_create_update() as update_call:

            self.resourceApi.update(
                segment_id=segment_id,
                name=name,
                ip_discovery_profile_id=prf1,
                mac_discovery_profile_id=prf2,
                tenant=TEST_TENANT)
            expected_def = self.resourceDef(
                segment_id=segment_id,
                map_id=core_resources.DEFAULT_MAP_ID,
                name=name,
                ip_discovery_profile_id=prf1,
                mac_discovery_profile_id=prf2,
                tenant=TEST_TENANT)
            self.assert_called_with_def(
                update_call, expected_def)


class TestPolicySegmentQosProfilesBinding(NsxPolicyLibTestCase):

    def setUp(self, resource_api_name='segment_qos_profile_maps',
              resource_def=core_defs.SegmentQosProfilesBindingMapDef):
        super(TestPolicySegmentQosProfilesBinding, self).setUp()
        self.resourceApi = getattr(self.policy_lib, resource_api_name)
        self.resourceDef = resource_def

    def test_create(self):
        name = 'test'
        segment_id = 'seg1'
        prf1 = '1'
        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            result = self.resourceApi.create_or_overwrite(
                name, segment_id,
                qos_profile_id=prf1,
                tenant=TEST_TENANT)

            expected_def = self.resourceDef(
                segment_id=segment_id,
                map_id=core_resources.DEFAULT_MAP_ID,
                name=name,
                qos_profile_id=prf1,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertIsNotNone(result)

    def test_delete(self):
        segment_id = 'seg1'
        with mock.patch.object(self.policy_api, "delete") as api_call:
            self.resourceApi.delete(segment_id, tenant=TEST_TENANT)
            expected_def = self.resourceDef(
                segment_id=segment_id,
                map_id=core_resources.DEFAULT_MAP_ID,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_get(self):
        segment_id = 'seg1'
        with mock.patch.object(self.policy_api, "get",
                               return_value={'id': segment_id}) as api_call:
            result = self.resourceApi.get(segment_id,
                                          tenant=TEST_TENANT)
            expected_def = self.resourceDef(
                segment_id=segment_id,
                map_id=core_resources.DEFAULT_MAP_ID,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(segment_id, result['id'])

    def test_list(self):
        segment_id = 'seg1'
        with mock.patch.object(self.policy_api, "list",
                               return_value={'results': []}) as api_call:
            result = self.resourceApi.list(segment_id,
                                           tenant=TEST_TENANT)
            expected_def = self.resourceDef(
                segment_id=segment_id,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual([], result)

    def test_update(self):
        name = 'new name'
        segment_id = 'seg1'
        prf1 = '1'
        with self.mock_get(segment_id, name), \
            self.mock_create_update() as update_call:

            self.resourceApi.update(
                segment_id=segment_id,
                name=name,
                qos_profile_id=prf1,
                tenant=TEST_TENANT)
            expected_def = self.resourceDef(
                segment_id=segment_id,
                map_id=core_resources.DEFAULT_MAP_ID,
                name=name,
                qos_profile_id=prf1,
                tenant=TEST_TENANT)
            self.assert_called_with_def(
                update_call, expected_def)


class TestPolicySegmentPortSecProfilesBinding(NsxPolicyLibTestCase):

    def setUp(self, resource_api_name='segment_port_security_profiles',
              resource_def=core_defs.SegmentPortSecProfilesBindingMapDef):
        super(TestPolicySegmentPortSecProfilesBinding, self).setUp()
        self.resourceApi = getattr(self.policy_lib, resource_api_name)
        self.resourceDef = resource_def

    def test_create(self):
        name = 'test'
        segment_id = 'seg1'
        port_id = 'port1'
        prf1 = '1'
        prf2 = '2'
        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            result = self.resourceApi.create_or_overwrite(
                name, segment_id, port_id,
                segment_security_profile_id=prf1,
                spoofguard_profile_id=prf2,
                tenant=TEST_TENANT)

            expected_def = self.resourceDef(
                segment_id=segment_id,
                port_id=port_id,
                map_id=core_resources.DEFAULT_MAP_ID,
                name=name,
                segment_security_profile_id=prf1,
                spoofguard_profile_id=prf2,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertIsNotNone(result)

    def test_delete(self):
        segment_id = 'seg1'
        port_id = 'port1'
        with mock.patch.object(self.policy_api, "delete") as api_call:
            self.resourceApi.delete(segment_id, port_id, tenant=TEST_TENANT)
            expected_def = self.resourceDef(
                segment_id=segment_id,
                port_id=port_id,
                map_id=core_resources.DEFAULT_MAP_ID,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_get(self):
        segment_id = 'seg1'
        port_id = 'port1'
        with mock.patch.object(self.policy_api, "get",
                               return_value={'id': port_id}) as api_call:
            result = self.resourceApi.get(segment_id, port_id,
                                          tenant=TEST_TENANT)
            expected_def = self.resourceDef(
                segment_id=segment_id,
                port_id=port_id,
                map_id=core_resources.DEFAULT_MAP_ID,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(port_id, result['id'])

    def test_list(self):
        segment_id = 'seg1'
        port_id = 'port1'
        with mock.patch.object(self.policy_api, "list",
                               return_value={'results': []}) as api_call:
            result = self.resourceApi.list(segment_id, port_id,
                                           tenant=TEST_TENANT)
            expected_def = self.resourceDef(
                segment_id=segment_id,
                port_id=port_id,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual([], result)

    def test_update(self):
        name = 'new name'
        segment_id = 'seg1'
        port_id = 'port1'
        prf1 = '1'
        prf2 = '2'
        with self.mock_get(segment_id, name), \
            self.mock_create_update() as update_call:

            self.resourceApi.update(
                segment_id=segment_id,
                port_id=port_id,
                name=name,
                segment_security_profile_id=prf1,
                spoofguard_profile_id=prf2,
                tenant=TEST_TENANT)
            expected_def = self.resourceDef(
                segment_id=segment_id,
                port_id=port_id,
                map_id=core_resources.DEFAULT_MAP_ID,
                name=name,
                segment_security_profile_id=prf1,
                spoofguard_profile_id=prf2,
                tenant=TEST_TENANT)
            self.assert_called_with_def(
                update_call, expected_def)


class TestPolicySegmentPortDiscoveryProfilesBinding(NsxPolicyLibTestCase):

    def setUp(
        self, resource_api_name='segment_port_discovery_profiles',
        resource_def=core_defs.SegmentPortDiscoveryProfilesBindingMapDef):

        super(TestPolicySegmentPortDiscoveryProfilesBinding, self).setUp()
        self.resourceApi = getattr(self.policy_lib, resource_api_name)
        self.resourceDef = resource_def

    def test_create(self):
        name = 'test'
        segment_id = 'seg1'
        port_id = 'port1'
        prf1 = '1'
        prf2 = '2'
        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            result = self.resourceApi.create_or_overwrite(
                name, segment_id, port_id,
                mac_discovery_profile_id=prf1,
                ip_discovery_profile_id=prf2,
                tenant=TEST_TENANT)

            expected_def = self.resourceDef(
                segment_id=segment_id,
                port_id=port_id,
                map_id=core_resources.DEFAULT_MAP_ID,
                name=name,
                mac_discovery_profile_id=prf1,
                ip_discovery_profile_id=prf2,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertIsNotNone(result)

    def test_delete(self):
        segment_id = 'seg1'
        port_id = 'port1'
        with mock.patch.object(self.policy_api, "delete") as api_call:
            self.resourceApi.delete(segment_id, port_id, tenant=TEST_TENANT)
            expected_def = self.resourceDef(
                segment_id=segment_id,
                port_id=port_id,
                map_id=core_resources.DEFAULT_MAP_ID,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_get(self):
        segment_id = 'seg1'
        port_id = 'port1'
        with mock.patch.object(self.policy_api, "get",
                               return_value={'id': port_id}) as api_call:
            result = self.resourceApi.get(segment_id, port_id,
                                          tenant=TEST_TENANT)
            expected_def = self.resourceDef(
                segment_id=segment_id,
                port_id=port_id,
                map_id=core_resources.DEFAULT_MAP_ID,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(port_id, result['id'])

    def test_list(self):
        segment_id = 'seg1'
        port_id = 'port1'
        with mock.patch.object(self.policy_api, "list",
                               return_value={'results': []}) as api_call:
            result = self.resourceApi.list(segment_id, port_id,
                                           tenant=TEST_TENANT)
            expected_def = self.resourceDef(
                segment_id=segment_id,
                port_id=port_id,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual([], result)

    def test_update(self):
        name = 'new name'
        segment_id = 'seg1'
        port_id = 'port1'
        prf1 = '1'
        prf2 = '2'
        with self.mock_get(segment_id, name), \
            self.mock_create_update() as update_call:
            self.resourceApi.update(
                segment_id=segment_id,
                port_id=port_id,
                name=name,
                mac_discovery_profile_id=prf1,
                ip_discovery_profile_id=prf2,
                tenant=TEST_TENANT)
            expected_def = self.resourceDef(
                segment_id=segment_id,
                port_id=port_id,
                map_id=core_resources.DEFAULT_MAP_ID,
                name=name,
                mac_discovery_profile_id=prf1,
                ip_discovery_profile_id=prf2,
                tenant=TEST_TENANT)
            self.assert_called_with_def(
                update_call, expected_def)


class TestPolicySegmentPortQosProfilesBinding(NsxPolicyLibTestCase):

    def setUp(
        self, resource_api_name='segment_port_qos_profiles',
        resource_def=core_defs.SegmentPortQoSProfilesBindingMapDef):

        super(TestPolicySegmentPortQosProfilesBinding, self).setUp()
        self.resourceApi = getattr(self.policy_lib, resource_api_name)
        self.resourceDef = resource_def

    def test_create(self):
        name = 'test'
        segment_id = 'seg1'
        port_id = 'port1'
        prf1 = '1'
        with self.mock_create_update() as api_call:
            result = self.resourceApi.create_or_overwrite(
                name, segment_id, port_id,
                qos_profile_id=prf1,
                tenant=TEST_TENANT)

            expected_def = self.resourceDef(
                segment_id=segment_id,
                port_id=port_id,
                map_id=core_resources.DEFAULT_MAP_ID,
                name=name,
                qos_profile_id=prf1,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertIsNotNone(result)

    def test_delete(self):
        segment_id = 'seg1'
        port_id = 'port1'
        with mock.patch.object(self.policy_api, "delete") as api_call:
            self.resourceApi.delete(segment_id, port_id, tenant=TEST_TENANT)
            expected_def = self.resourceDef(
                segment_id=segment_id,
                port_id=port_id,
                map_id=core_resources.DEFAULT_MAP_ID,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_get(self):
        segment_id = 'seg1'
        port_id = 'port1'
        with mock.patch.object(self.policy_api, "get",
                               return_value={'id': segment_id}) as api_call:
            result = self.resourceApi.get(segment_id, port_id,
                                          tenant=TEST_TENANT)
            expected_def = self.resourceDef(
                segment_id=segment_id,
                port_id=port_id,
                map_id=core_resources.DEFAULT_MAP_ID,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(segment_id, result['id'])

    def test_list(self):
        segment_id = 'seg1'
        port_id = 'port1'
        with mock.patch.object(self.policy_api, "list",
                               return_value={'results': []}) as api_call:
            result = self.resourceApi.list(segment_id, port_id,
                                           tenant=TEST_TENANT)
            expected_def = self.resourceDef(
                segment_id=segment_id,
                port_id=port_id,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual([], result)

    def test_update(self):
        name = 'new name'
        segment_id = 'seg1'
        port_id = 'port1'
        prf1 = '1'
        with self.mock_get(segment_id, name), \
            self.mock_create_update() as update_call:
            self.resourceApi.update(
                segment_id=segment_id,
                port_id=port_id,
                name=name,
                qos_profile_id=prf1,
                tenant=TEST_TENANT)
            expected_def = self.resourceDef(
                segment_id=segment_id,
                port_id=port_id,
                map_id=core_resources.DEFAULT_MAP_ID,
                name=name,
                qos_profile_id=prf1,
                tenant=TEST_TENANT)
            self.assert_called_with_def(
                update_call, expected_def)


class TestPolicyTier1SegmentPort(NsxPolicyLibTestCase):

    def setUp(self, *args, **kwargs):
        super(TestPolicyTier1SegmentPort, self).setUp()
        self.resourceApi = self.policy_lib.tier1_segment_port

    def test_create(self):
        name = 'test'
        tier1_id = 'tier1'
        description = 'desc'
        segment_id = "segment"
        address_bindings = []
        attachment_type = "CHILD"
        vif_id = "vif"
        app_id = "app"
        context_id = "context"
        traffic_tag = 10
        allocate_addresses = "BOTH"
        tags = [{'scope': 'a', 'tag': 'b'}]

        with self.mock_create_update() as api_call:
            result = self.resourceApi.create_or_overwrite(
                name, tier1_id, segment_id, description=description,
                address_bindings=address_bindings,
                attachment_type=attachment_type, vif_id=vif_id, app_id=app_id,
                context_id=context_id, traffic_tag=traffic_tag,
                allocate_addresses=allocate_addresses, tags=tags,
                tenant=TEST_TENANT)

            expected_def = core_defs.Tier1SegmentPortDef(
                segment_id=segment_id,
                tier1_id=tier1_id,
                port_id=mock.ANY,
                name=name,
                description=description,
                address_bindings=address_bindings,
                attachment_type=attachment_type,
                vif_id=vif_id,
                app_id=app_id,
                context_id=context_id,
                traffic_tag=traffic_tag,
                allocate_addresses=allocate_addresses,
                tags=tags,
                tenant=TEST_TENANT)

            self.assert_called_with_def(api_call, expected_def)
            self.assertIsNotNone(result)

    def test_wait_until_realized_fail(self):
        tier1_id = '111'
        port_id = 'port-111'
        segment_id = 'seg-111'
        logical_port_id = 'realized_port_111'
        info = {'state': constants.STATE_UNREALIZED,
                'realization_specific_identifier': logical_port_id,
                'entity_type': 'RealizedLogicalPort'}
        with mock.patch.object(self.resourceApi, "_get_realization_info",
                               return_value=info):
            self.assertRaises(nsxlib_exc.RealizationTimeoutError,
                              self.resourceApi.wait_until_realized,
                              tier1_id, segment_id, port_id, max_attempts=5,
                              sleep=0.1, tenant=TEST_TENANT)

    def test_wait_until_realized_error(self):
        tier1_id = '111'
        port_id = 'port-111'
        segment_id = 'seg-111'
        info = {'state': constants.STATE_ERROR,
                'alarms': [{'message': 'dummy',
                            'error_details': {
                                'error_code': 5109}}],
                'entity_type': 'RealizedLogicalPort'}
        with mock.patch.object(self.resourceApi, "_get_realization_info",
                               return_value=info):
            self.assertRaises(nsxlib_exc.RealizationErrorStateError,
                              self.resourceApi.wait_until_realized,
                              tier1_id, segment_id, port_id, max_attempts=5,
                              sleep=0.1, tenant=TEST_TENANT)

    def test_wait_until_realized_succeed(self):
        tier1_id = '111'
        port_id = 'port-111'
        segment_id = 'seg-111'
        logical_port_id = 'realized_port_111'
        info = {'state': constants.STATE_REALIZED,
                'realization_specific_identifier': logical_port_id,
                'entity_type': 'RealizedLogicalPort'}
        with mock.patch.object(self.resourceApi, "_get_realization_info",
                               return_value=info):
            actual_info = self.resourceApi.wait_until_realized(
                tier1_id, segment_id, port_id, max_attempts=5, sleep=0.1,
                tenant=TEST_TENANT)
            self.assertEqual(info, actual_info)


class TestPolicySegmentDhcpStaticBinding(NsxPolicyLibTestCase):

    def setUp(self, *args, **kwargs):
        super(TestPolicySegmentDhcpStaticBinding, self).setUp()
        self.resourceApi = self.policy_lib.segment_dhcp_static_bindings

    def test_create(self):
        """Create v4 static bindings"""
        name = 'test'
        description = 'desc'
        segment_id = "segment"
        ip_address = "1.1.1.1"
        mac_address = "fa:16:3e:44:56:df"

        with mock.patch.object(
            self.policy_api, "create_or_update") as api_call:
            result = self.resourceApi.create_or_overwrite_v4(
                name, segment_id, description=description,
                ip_address=ip_address, mac_address=mac_address,
                tenant=TEST_TENANT)

            expected_def = core_defs.DhcpV4StaticBindingConfig(
                segment_id=segment_id,
                binding_id=mock.ANY,
                name=name,
                description=description,
                ip_address=ip_address,
                mac_address=mac_address,
                tenant=TEST_TENANT)

            self.assert_called_with_def(api_call, expected_def)
            self.assertIsNotNone(result)

    def test_create_v6(self):
        """Create v6 static bindings"""
        name = 'test'
        description = 'desc'
        segment_id = "segment"
        ip_address = "2000::01ab"
        mac_address = "fa:16:3e:44:56:df"

        with mock.patch.object(
            self.policy_api, "create_or_update") as api_call:
            result = self.resourceApi.create_or_overwrite_v6(
                name, segment_id, description=description,
                ip_addresses=[ip_address],
                mac_address=mac_address,
                tenant=TEST_TENANT)

            expected_def = core_defs.DhcpV6StaticBindingConfig(
                segment_id=segment_id,
                binding_id=mock.ANY,
                name=name,
                description=description,
                ip_addresses=[ip_address],
                mac_address=mac_address,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertIsNotNone(result)

    def test_list(self):
        segment_id = '111'
        with mock.patch.object(self.policy_api, "list",
                               return_value={'results': []}) as api_call:
            result = self.resourceApi.list(segment_id, tenant=TEST_TENANT)
            expected_def = core_defs.DhcpV4StaticBindingConfig(
                segment_id=segment_id,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual([], result)

    def test_delete(self):
        segment_id = '111'
        binding_id = '222'
        with mock.patch.object(self.policy_api, "delete") as api_call:
            self.resourceApi.delete(segment_id, binding_id, tenant=TEST_TENANT)
            expected_def = core_defs.DhcpV4StaticBindingConfig(
                segment_id=segment_id,
                binding_id=binding_id,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_get(self):
        segment_id = '111'
        binding_id = '222'
        with mock.patch.object(self.policy_api, "get",
                               return_value={'id': binding_id}) as api_call:
            result = self.resourceApi.get(segment_id, binding_id,
                                          tenant=TEST_TENANT)
            expected_def = core_defs.DhcpV4StaticBindingConfig(
                segment_id=segment_id,
                binding_id=binding_id,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(binding_id, result['id'])


class TestPolicyDhcpRelayConfig(NsxPolicyLibTestCase):

    def setUp(self, *args, **kwargs):
        super(TestPolicyDhcpRelayConfig, self).setUp()
        self.resourceApi = self.policy_lib.dhcp_relay_config

    def test_create(self):
        name = 'test'
        description = 'desc'
        server_addr = '1.1.1.1'

        with self.mock_create_update() as api_call:
            result = self.resourceApi.create_or_overwrite(
                name, description=description,
                server_addresses=[server_addr],
                tenant=TEST_TENANT)

            expected_def = core_defs.DhcpRelayConfigDef(
                config_id=mock.ANY,
                name=name,
                description=description,
                server_addresses=[server_addr],
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertIsNotNone(result)

    def test_delete(self):
        config_id = '111'
        with mock.patch.object(self.policy_api, "delete") as api_call:
            self.resourceApi.delete(config_id, tenant=TEST_TENANT)
            expected_def = core_defs.DhcpRelayConfigDef(config_id=config_id,
                                                        tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_get(self):
        config_id = '111'
        with mock.patch.object(self.policy_api, "get",
                               return_value={'id': config_id}) as api_call:
            result = self.resourceApi.get(config_id, tenant=TEST_TENANT)
            expected_def = core_defs.DhcpRelayConfigDef(config_id=config_id,
                                                        tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(config_id, result['id'])

    def test_list(self):
        with mock.patch.object(self.policy_api, "list",
                               return_value={'results': []}) as api_call:
            result = self.resourceApi.list(tenant=TEST_TENANT)
            expected_def = core_defs.DhcpRelayConfigDef(tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual([], result)


class TestPolicyDhcpServerConfig(NsxPolicyLibTestCase):

    def setUp(self, *args, **kwargs):
        super(TestPolicyDhcpServerConfig, self).setUp()
        self.resourceApi = self.policy_lib.dhcp_server_config

    def test_create(self):
        name = 'test'
        description = 'desc'
        server_addr = '1.1.1.1'
        lease_time = 100
        edge_cluster_path = 'dummy/path'
        tags = [{'scope': 'a', 'tag': 'b'}]

        with self.mock_create_update() as api_call:
            result = self.resourceApi.create_or_overwrite(
                name, description=description,
                server_addresses=[server_addr],
                edge_cluster_path=edge_cluster_path,
                lease_time=lease_time, tags=tags,
                tenant=TEST_TENANT)

            expected_def = core_defs.DhcpServerConfigDef(
                config_id=mock.ANY,
                name=name,
                description=description,
                server_addresses=[server_addr],
                edge_cluster_path=edge_cluster_path,
                lease_time=lease_time,
                tags=tags,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertIsNotNone(result)

    def test_delete(self):
        config_id = '111'
        with mock.patch.object(self.policy_api, "delete") as api_call:
            self.resourceApi.delete(config_id, tenant=TEST_TENANT)
            expected_def = core_defs.DhcpServerConfigDef(config_id=config_id,
                                                         tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_get(self):
        config_id = '111'
        with mock.patch.object(self.policy_api, "get",
                               return_value={'id': config_id}) as api_call:
            result = self.resourceApi.get(config_id, tenant=TEST_TENANT)
            expected_def = core_defs.DhcpServerConfigDef(config_id=config_id,
                                                         tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(config_id, result['id'])

    def test_list(self):
        with mock.patch.object(self.policy_api, "list",
                               return_value={'results': []}) as api_call:
            result = self.resourceApi.list(tenant=TEST_TENANT)
            expected_def = core_defs.DhcpServerConfigDef(tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual([], result)

    def test_update(self):
        name = 'test'
        description = 'desc'
        server_addr = '1.1.1.1'
        lease_time = 100
        edge_cluster_path = 'dummy/path'
        tags = [{'scope': 'a', 'tag': 'b'}]
        config_id = 'aaa'

        with self.mock_create_update() as api_call:
            self.resourceApi.update(
                config_id, name=name, description=description,
                server_addresses=[server_addr],
                edge_cluster_path=edge_cluster_path,
                lease_time=lease_time, tags=tags,
                tenant=TEST_TENANT)

            expected_def = core_defs.DhcpServerConfigDef(
                config_id=mock.ANY,
                name=name,
                description=description,
                server_addresses=[server_addr],
                edge_cluster_path=edge_cluster_path,
                lease_time=lease_time,
                tags=tags,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)


class TestPolicyCertificate(NsxPolicyLibTestCase):

    def setUp(self, *args, **kwargs):
        super(TestPolicyCertificate, self).setUp()
        self.resourceApi = self.policy_lib.certificate

    def test_create_with_id(self):
        name = 'd1'
        description = 'desc'
        obj_id = '111'
        pem_encoded = 'pem_encoded'
        private_key = 'private_key'
        passphrase = 'passphrase'
        key_algo = 'algo'
        with self.mock_create_update() as api_call:
            result = self.resourceApi.create_or_overwrite(
                name,
                certificate_id=obj_id,
                description=description,
                pem_encoded=pem_encoded,
                private_key=private_key,
                passphrase=passphrase,
                key_algo=key_algo,
                tenant=TEST_TENANT)
            expected_def = (
                core_defs.CertificateDef(
                    certificate_id=obj_id,
                    name=name,
                    description=description,
                    pem_encoded=pem_encoded,
                    private_key=private_key,
                    passphrase=passphrase,
                    key_algo=key_algo,
                    tenant=TEST_TENANT))
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(obj_id, result)

    def test_create_without_id(self):
        name = 'd1'
        description = 'desc'
        pem_encoded = 'pem_encoded'
        with self.mock_create_update() as api_call:
            result = self.resourceApi.create_or_overwrite(
                name, description=description,
                tenant=TEST_TENANT,
                pem_encoded=pem_encoded)
            expected_def = (
                core_defs.CertificateDef(certificate_id=mock.ANY,
                                         name=name,
                                         description=description,
                                         tenant=TEST_TENANT,
                                         pem_encoded=pem_encoded))
            self.assert_called_with_def(api_call, expected_def)
            self.assertIsNotNone(result)

    def test_delete(self):
        obj_id = '111'
        with mock.patch.object(self.policy_api, "delete") as api_call:
            self.resourceApi.delete(obj_id, tenant=TEST_TENANT)
            expected_def = core_defs.CertificateDef(
                certificate_id=obj_id,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_get(self):
        obj_id = '111'
        with mock.patch.object(self.policy_api, "get",
                               return_value={'id': obj_id}) as api_call:
            result = self.resourceApi.get(obj_id, tenant=TEST_TENANT)
            expected_def = core_defs.CertificateDef(
                certificate_id=obj_id,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(obj_id, result['id'])

    def test_get_by_name(self):
        name = 'd1'
        with mock.patch.object(
            self.policy_api, "list",
            return_value={'results': [{'display_name': name}]}) as api_call:
            obj = self.resourceApi.get_by_name(name, tenant=TEST_TENANT)
            self.assertIsNotNone(obj)
            expected_def = core_defs.CertificateDef(tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_list(self):
        with mock.patch.object(self.policy_api, "list",
                               return_value={'results': []}) as api_call:
            result = self.resourceApi.list(tenant=TEST_TENANT)
            expected_def = core_defs.CertificateDef(tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual([], result)

    def test_update(self):
        obj_id = '111'
        name = 'new name'
        description = 'new desc'
        pem_encoded = 'pem_encoded'
        private_key = 'private_key'
        passphrase = '12'
        key_algo = 'new_algo'
        with self.mock_get(obj_id, name), \
            self.mock_create_update() as update_call:
            self.resourceApi.update(obj_id,
                                    name=name,
                                    description=description,
                                    tenant=TEST_TENANT,
                                    pem_encoded=pem_encoded,
                                    private_key=private_key,
                                    passphrase=passphrase,
                                    key_algo=key_algo)
            expected_def = core_defs.CertificateDef(
                certificate_id=obj_id,
                name=name,
                description=description,
                tenant=TEST_TENANT,
                pem_encoded=pem_encoded,
                private_key=private_key,
                passphrase=passphrase,
                key_algo=key_algo
            )
            self.assert_called_with_def(update_call, expected_def)

    def test_wait_until_realized_fail(self):
        cert_id = 'test_cert'
        info = {'state': constants.STATE_UNREALIZED,
                'realization_specific_identifier': cert_id}
        with mock.patch.object(self.resourceApi, "_get_realization_info",
                               return_value=info):
            self.assertRaises(nsxlib_exc.RealizationTimeoutError,
                              self.resourceApi.wait_until_realized,
                              cert_id, max_attempts=5, sleep=0.1,
                              tenant=TEST_TENANT)

    def test_wait_until_realized_succeed(self):
        cert_id = 'test_cert'
        info = {'state': constants.STATE_REALIZED,
                'realization_specific_identifier': cert_id}
        with mock.patch.object(self.resourceApi, "_get_realization_info",
                               return_value=info):
            actual_info = self.resourceApi.wait_until_realized(
                cert_id, max_attempts=5,
                sleep=0.1, tenant=TEST_TENANT)
            self.assertEqual(info, actual_info)

    def test_find_cert_with_pem(self):
        id1 = '1'
        id2 = '2'
        pem1 = '111'
        pem2 = '222'
        with mock.patch.object(self.policy_api, "list",
                               return_value={'results': [
                                   {'id': id1, 'pem_encoded': pem1},
                                   {'id': id2, 'pem_encoded': pem2}]}) as api:
            cert_ids = self.resourceApi.find_cert_with_pem(
                pem1, tenant=TEST_TENANT)
            self.assertEqual(1, len(cert_ids))
            self.assertEqual(id1, cert_ids[0])
            expected_def = core_defs.CertificateDef(tenant=TEST_TENANT)
            self.assert_called_with_def(api, expected_def)


class TestPolicyExcludeList(NsxPolicyLibTestCase):

    def setUp(self, *args, **kwargs):
        super(TestPolicyExcludeList, self).setUp()
        self.resourceApi = self.policy_lib.exclude_list

    def test_create_or_overwrite(self):
        members = ["/infra/domains/default/groups/adit1"]
        with self.mock_create_update() as api_call:
            self.resourceApi.create_or_overwrite(
                members=members, tenant=TEST_TENANT)
            expected_def = core_defs.ExcludeListDef(
                members=members, tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_delete(self):
        self.skipTest("The action is not supported by this resource")

    def test_get(self):
        with mock.patch.object(self.policy_api, "get") as api_call:
            self.resourceApi.get(tenant=TEST_TENANT)
            expected_def = core_defs.ExcludeListDef(
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_list(self):
        self.skipTest("The action is not supported by this resource")

    def test_update(self):
        self.skipTest("The action is not supported by this resource")


class TestPolicyTier0RouteMap(NsxPolicyLibTestCase):

    def setUp(self, *args, **kwargs):
        super(TestPolicyTier0RouteMap, self).setUp()
        self.resourceApi = self.policy_lib.tier0_route_map

    def test_create(self):
        name = 'route_map_test'
        tier0_id = 't0_test'
        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            # test with 'entries'
            entry = core_defs.RouteMapEntry('DENY')
            result = self.resourceApi.create_or_overwrite(
                name, tier0_id, entries=[entry], tenant=TEST_TENANT)
            expected_def = core_defs.Tier0RouteMapDef(
                tier0_id=tier0_id,
                route_map_id=mock.ANY,
                name=name,
                entries=[entry],
                tenant=TEST_TENANT)

            self.assert_called_with_def(api_call, expected_def)
            self.assertIsNotNone(result)

    def test_delete(self):
        tier0_id = 't0_test'
        route_map_id = 'route_map_test'
        with mock.patch.object(self.policy_api, "delete") as api_call:
            self.resourceApi.delete(tier0_id, route_map_id, tenant=TEST_TENANT)
            expected_def = core_defs.Tier0RouteMapDef(
                tier0_id=tier0_id,
                route_map_id=route_map_id,
                tenant=TEST_TENANT)

            self.assert_called_with_def(api_call, expected_def)

    def test_get(self):
        tier0_id = 't0_test'
        route_map_id = 'route_map_test'
        entries = []
        with mock.patch.object(self.policy_api, "get",
                               return_value={'id': route_map_id}) as api_call:
            result = self.resourceApi.get(tier0_id, route_map_id,
                                          tenant=TEST_TENANT)
            expected_def = core_defs.Tier0RouteMapDef(
                tier0_id=tier0_id,
                route_map_id=route_map_id,
                entries=entries,
                tenant=TEST_TENANT)

            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(route_map_id, result['id'])

    def test_list(self):
        tier0_id = 't0_test'
        with mock.patch.object(self.policy_api, "list",
                               return_value={'results': []}) as api_call:
            result = self.resourceApi.list(tier0_id=tier0_id,
                                           tenant=TEST_TENANT)
            expected_def = core_defs.Tier0RouteMapDef(
                tier0_id=tier0_id,
                tenant=TEST_TENANT)

            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual([], result)

    def test_update(self):
        tier0_id = 't0_test'
        route_map_id = 'route_map_test'
        name = 'new_name'
        entries = []
        with self.mock_get(tier0_id, name), \
            self.mock_create_update() as update_call:
            self.resourceApi.update(name, tier0_id, route_map_id, entries,
                                    tenant=TEST_TENANT, force=True)
            expected_def = core_defs.Tier0RouteMapDef(
                tier0_id=tier0_id,
                route_map_id=route_map_id,
                name=name,
                entries=entries,
                tenant=TEST_TENANT)
            update_call.assert_called_with(mock.ANY, partial_updates=True,
                                           force=True)
            self.assert_called_with_def(update_call, expected_def)

    def test_build_route_map_entry(self):
        action = constants.ADV_RULE_PERMIT
        community_list_matches = mock.ANY
        prefix_list_matches = ["prefix_list_matches"]
        entry_set = mock.ANY
        route_map_entry = self.resourceApi.build_route_map_entry(
            action, community_list_matches, prefix_list_matches, entry_set)

        self.assertEqual(action, route_map_entry.action)
        self.assertEqual(community_list_matches,
                         route_map_entry.community_list_matches)
        self.assertEqual(prefix_list_matches,
                         route_map_entry.prefix_list_matches)
        self.assertEqual(entry_set, route_map_entry.entry_set)

    def test_build_route_map_entry_set(self):
        local_preference = 100
        as_path_prepend = mock.ANY
        community = mock.ANY
        med = mock.ANY
        weight = mock.ANY
        entry_set = self.resourceApi.build_route_map_entry_set(
            local_preference, as_path_prepend, community, med, weight)

        self.assertEqual(local_preference, entry_set.local_preference)
        self.assertEqual(as_path_prepend, entry_set.as_path_prepend)
        self.assertEqual(community, entry_set.community)
        self.assertEqual(med, entry_set.med)
        self.assertEqual(weight, entry_set.weight)

    def test_build_community_match_criteria(self):
        criteria = "test_criteria"
        match_operator = mock.ANY
        match_criteria = self.resourceApi.build_community_match_criteria(
            criteria, match_operator)

        self.assertEqual(criteria, match_criteria.criteria)
        self.assertEqual(match_operator, match_criteria.match_operator)


class TestPolicyTier0PrefixList(NsxPolicyLibTestCase):

    def setUp(self, *args, **kwargs):
        super(TestPolicyTier0PrefixList, self).setUp()
        self.resourceApi = self.policy_lib.tier0_prefix_list

    def test_create(self):
        name = 'prefix_list_test'
        tier0_id = 't0_test'
        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            # test with 'prefixes'
            prefix = core_defs.PrefixEntry('network_test')
            result = self.resourceApi.create_or_overwrite(
                name, tier0_id, prefixes=[prefix], tenant=TEST_TENANT)
            expected_def = core_defs.Tier0PrefixListDef(
                tier0_id=tier0_id,
                prefix_list_id=mock.ANY,
                name=name,
                prefixes=[prefix],
                tenant=TEST_TENANT)

            self.assert_called_with_def(api_call, expected_def)
            self.assertIsNotNone(result)

    def test_delete(self):
        tier0_id = 't0_test'
        prefix_list_id = 'prefix_list_test'
        with mock.patch.object(self.policy_api, "delete") as api_call:
            self.resourceApi.delete(tier0_id, prefix_list_id,
                                    tenant=TEST_TENANT)
            expected_def = core_defs.Tier0PrefixListDef(
                tier0_id=tier0_id,
                prefix_list_id=prefix_list_id,
                tenant=TEST_TENANT)

            self.assert_called_with_def(api_call, expected_def)

    def test_get(self):
        tier0_id = 't0_test'
        prefix_list_id = 'prefix_list_test'
        with mock.patch.object(
            self.policy_api, "get",
            return_value={'id': prefix_list_id}) as api_call:
            result = self.resourceApi.get(tier0_id, prefix_list_id,
                                          tenant=TEST_TENANT)
            expected_def = core_defs.Tier0PrefixListDef(
                tier0_id=tier0_id,
                prefix_list_id=prefix_list_id,
                tenant=TEST_TENANT)

            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual(prefix_list_id, result['id'])

    def test_list(self):
        tier0_id = 't0_test'
        with mock.patch.object(self.policy_api, "list",
                               return_value={'results': []}) as api_call:
            result = self.resourceApi.list(tier0_id=tier0_id,
                                           tenant=TEST_TENANT)
            expected_def = core_defs.Tier0PrefixListDef(
                tier0_id=tier0_id,
                tenant=TEST_TENANT)

            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual([], result)

    def test_update(self):
        tier0_id = 't0_test'
        prefix_list_id = 'prefix_list_test'
        name = 'new_name'
        prefixes = []
        with self.mock_get(tier0_id, name), \
            self.mock_create_update() as update_call:
            self.resourceApi.update(name, tier0_id, prefix_list_id, prefixes,
                                    tenant=TEST_TENANT)
            expected_def = core_defs.Tier0PrefixListDef(
                tier0_id=tier0_id,
                prefix_list_id=prefix_list_id,
                name=name,
                prefixes=prefixes,
                tenant=TEST_TENANT)

            self.assert_called_with_def(update_call, expected_def)

    def test_build_prefix_entry(self):
        network = "network_test"
        le = mock.ANY
        ge = mock.ANY
        action = constants.ADV_RULE_DENY
        prefix_entry = self.resourceApi.build_prefix_entry(
            network, le, ge, action)

        self.assertEqual(network, prefix_entry.network)
        self.assertEqual(le, prefix_entry.le)
        self.assertEqual(ge, prefix_entry.ge)
        self.assertEqual(action, prefix_entry.action)


class TestNsxSearch(NsxPolicyLibTestCase):

    def setUp(self):
        super(TestNsxSearch, self).setUp()
        self.search_path = 'search/query?query=%s&sort_by=id'

    def test_nsx_search_by_realization(self):
        """Test search of resources with the specified tag."""
        with mock.patch.object(self.policy_lib.client, 'url_get') as search:
            realized_id = 'xxx'
            realized_type = 'RealizedLogicalSwitch'
            query = ('resource_type:GenericPolicyRealizedResource AND '
                     'realization_specific_identifier:%s AND '
                     'entity_type:%s' % (realized_id, realized_type))
            self.policy_lib.search_resource_by_realized_id(
                realized_id, realized_type)
            search.assert_called_with(self.search_path % query)


class TestPolicyGlobalConfig(NsxPolicyLibTestCase):

    def setUp(self, *args, **kwargs):
        super(TestPolicyGlobalConfig, self).setUp()
        self.resourceApi = self.policy_lib.global_config

    def test_create_or_overwrite(self):
        self.skipTest("The action is not supported by this resource")

    def test_delete(self):
        self.skipTest("The action is not supported by this resource")

    def test_get(self):
        with mock.patch.object(self.policy_api, "get") as api_call:
            self.resourceApi.get(tenant=TEST_TENANT)
            expected_def = core_defs.GlobalConfigDef(
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)

    def test_list(self):
        self.skipTest("The action is not supported by this resource")

    def test_update(self):
        self.skipTest("The action is not supported by this resource")

    def test_enable_ipv6(self):
        current_config = {'l3_forwarding_mode': 'IPV4_ONLY'}
        with mock.patch.object(self.policy_api, "get",
                               return_value=current_config) as api_get,\
            mock.patch.object(self.policy_api.client, "update") as api_put:
            self.resourceApi.enable_ipv6(tenant=TEST_TENANT)
            api_get.assert_called_once()
            api_put.assert_called_once_with(
                "%s/global-config/" % TEST_TENANT,
                {'l3_forwarding_mode': 'IPV4_AND_IPV6'})

    def test_enable_ipv6_no_call(self):
        current_config = {'l3_forwarding_mode': 'IPV4_AND_IPV6'}
        with mock.patch.object(self.policy_api, "get",
                               return_value=current_config) as api_get,\
            mock.patch.object(self.policy_api.client, "update") as api_put:
            self.resourceApi.enable_ipv6(tenant=TEST_TENANT)
            api_get.assert_called_once()
            api_put.assert_not_called()

    def test_disable_ipv6(self):
        current_config = {'l3_forwarding_mode': 'IPV4_AND_IPV6'}
        with mock.patch.object(self.policy_api, "get",
                               return_value=current_config) as api_get,\
            mock.patch.object(self.policy_api.client, "update") as api_put:
            self.resourceApi.disable_ipv6(tenant=TEST_TENANT)
            api_get.assert_called_once()
            api_put.assert_called_once_with(
                "%s/global-config/" % TEST_TENANT,
                {'l3_forwarding_mode': 'IPV4_ONLY'})

    def test_disable_ipv6_no_call(self):
        current_config = {'l3_forwarding_mode': 'IPV4_ONLY'}
        with mock.patch.object(self.policy_api, "get",
                               return_value=current_config) as api_get,\
            mock.patch.object(self.policy_api.client, "update") as api_put:
            self.resourceApi.disable_ipv6(tenant=TEST_TENANT)
            api_get.assert_called_once()
            api_put.assert_not_called()


class TestPolicyTier0StaticRoute(NsxPolicyLibTestCase):

    def setUp(self, *args, **kwargs):
        super(TestPolicyTier0StaticRoute, self).setUp()
        self.resourceApi = self.policy_lib.tier0_static_route

    def test_create(self):
        name = 'test'
        description = 'desc'
        tier0_id = '111'
        static_route_id = '222'
        network = '1.1.1.1/24'
        nexthop = '2.2.2.2'
        scope = 'ContainerT0'

        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            result = self.resourceApi.create_or_overwrite(
                name, tier0_id,
                static_route_id=static_route_id,
                description=description,
                network=network,
                next_hop=nexthop,
                tenant=TEST_TENANT,
                scope=scope
            )

            expected_def = core_defs.Tier0StaticRoute(
                tier0_id=tier0_id,
                static_route_id=static_route_id,
                name=name,
                description=description,
                network=network,
                next_hop=nexthop,
                tenant=TEST_TENANT,
                scope=scope
            )
            self.assert_called_with_def(api_call, expected_def)
            self.assertIsNotNone(result)

    def test_delete(self):
        tier0_id = '111'
        static_route_id = '222'
        with mock.patch.object(self.policy_api, "delete") as api_call:
            self.resourceApi.delete(
                tier0_id,
                static_route_id,
                tenant=TEST_TENANT)
            expected_def = core_defs.Tier0StaticRoute(
                tier0_id=tier0_id,
                static_route_id=static_route_id,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)


class TestNsxPolicyObjectRolePermissionGroup(NsxPolicyLibTestCase):

    def setUp(self, *args, **kwargs):
        super(TestNsxPolicyObjectRolePermissionGroup, self).setUp()
        self.resourceApi = self.policy_lib.object_permission

    def test_create(self):
        name = 'orbac_test'
        operation = 'none'
        path_prefix = '/fake/path/prefix'
        role_name = 'cloud_admin'
        with mock.patch.object(self.policy_api,
                               "create_or_update") as api_call:
            self.resourceApi.create_or_overwrite(
                name, operation, path_prefix, role_name, tenant=TEST_TENANT)
            expected_def = core_defs.ObjectRolePermissionGroupDef(
                name=name,
                operation=operation,
                path_prefix=path_prefix,
                role_name=role_name,
                tenant=TEST_TENANT,
                patch=True)

            self.assert_called_with_def(api_call, expected_def)

    def test_update(self):
        name = 'orbac_test'
        operation = 'none'
        path_prefix = '/fake/path/prefix'
        role_name = 'cloud_admin'
        entry_body = {
            "path_prefix": path_prefix,
            "role_name": role_name,
            "operation": "read",
            "name": name
        }
        with mock.patch.object(self.policy_api,
                               "get",
                               return_value=entry_body),\
            self.mock_create_update() as update_call:
            self.resourceApi.update(
                name, operation, path_prefix, role_name, tenant=TEST_TENANT)

            expected_def = core_defs.ObjectRolePermissionGroupDef(
                name=name,
                operation=operation,
                path_prefix=path_prefix,
                role_name=role_name,
                tenant=TEST_TENANT,
                patch=True)
            self.assert_called_with_def(update_call, expected_def)

    def test_get(self):
        self.skipTest("The action is not supported by this resource")

    def test_list(self):
        path_prefix = '/fake/path/prefix'
        role_name = 'cloud_admin'
        with mock.patch.object(self.policy_api, "list",
                               return_value={'results': []}) as api_call:
            result = self.resourceApi.list(path_prefix=path_prefix,
                                           role_name=role_name,
                                           tenant=TEST_TENANT)
            expected_def = core_defs.ObjectRolePermissionGroupDef(
                path_prefix=path_prefix,
                role_name=role_name,
                tenant=TEST_TENANT)

            self.assert_called_with_def(api_call, expected_def)
            self.assertEqual([], result)

    def test_delete(self):
        path_prefix = '/fake/path/prefix'
        role_name = 'cloud_admin'
        with mock.patch.object(self.policy_api, "delete") as api_call:
            self.resourceApi.delete(path_prefix=path_prefix,
                                    role_name=role_name,
                                    tenant=TEST_TENANT)
            expected_def = core_defs.ObjectRolePermissionGroupDef(
                path_prefix=path_prefix,
                role_name=role_name,
                tenant=TEST_TENANT)
            self.assert_called_with_def(api_call, expected_def)
