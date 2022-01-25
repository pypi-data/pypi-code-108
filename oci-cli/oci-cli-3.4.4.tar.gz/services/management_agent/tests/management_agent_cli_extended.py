# coding: utf-8
# Copyright (c) 2016, 2021, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl or Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0. You may choose either license.

import unittest
from tests import util


class TestManagementAgent(unittest.TestCase):
    def setUp(self):
        pass

    def test_agent(self):
        result = util.invoke_command(['management-agent', 'management-agent', 'list', '--compartment-id', 'ocid1.compartment.oc1..123'])
        assert 'Error: No such command' in result.output
        result = util.invoke_command(['management-agent', 'agent', 'list', '--compartment-id', 'ocid1.compartment.oc1..123'])
        assert 'NotAuthorizedOrNotFound' in result.output
        result = util.invoke_command(['management-agent', 'agent', 'list', '--agent-version', 'version123', '--compartment-id', 'ocid1.compartment.oc1..123'])
        assert 'NotAuthorizedOrNotFound' in result.output

        result = util.invoke_command(['management-agent', 'agent', 'get', '--management-agent-id', 'ocid1.123'])
        assert 'Error: no such option' in result.output
        result = util.invoke_command(['management-agent', 'agent', 'get', '--agent-id', 'ocid1.123'])
        assert 'NotAuthorizedOrNotFound' in result.output

        result = util.invoke_command(['management-agent', 'management-agent-install-key', 'list', '--compartment-id', 'ocid1.compartment.oc1..123'])
        assert 'Error: No such command' in result.output
        result = util.invoke_command(['management-agent', 'install-key', 'list', '--compartment-id', 'ocid1.compartment.oc1..123'])
        assert 'NotAuthorizedOrNotFound' in result.output

        result = util.invoke_command(['management-agent', 'management-agent-image', 'list', '--compartment-id', 'ocid1.compartment.oc1..123'])
        assert 'Error: No such command' in result.output

        result = util.invoke_command(['management-agent', 'install-key', 'get-management-agent-install-key-content', '--management-agent-install-key-id', 'ocid1.key', '--file', '-'])
        assert 'Error: No such command' in result.output
        result = util.invoke_command(['management-agent', 'install-key', 'get-install-key-content', '--management-agent-install-key-id', 'ocid1.key', '--file', '-'])
        assert 'NotAuthorizedOrNotFound' in result.output

        result = util.invoke_command(['management-agent', 'management-agent-plugin', 'list', '--compartment-id', 'ocid1.compartment.oc1..123'])
        assert 'Error: No such command' in result.output
        result = util.invoke_command(['management-agent', 'plugin', 'list', '--compartment-id', 'ocid1.compartment.oc1..123'])
        assert 'Authorization failed' in result.output

        result = util.invoke_command(['management-agent', 'agent', 'summarize-management-agent-plugin-counts', '--compartment-id', 'compartment_id', '--group-by', 'pluginName'])
        assert 'Error: No such command' in result.output

        result = util.invoke_command(['management-agent', 'agent', 'summarize-management-agent-counts', '--compartment-id', 'compartment_id', '--group-by', 'platformType'])
        assert 'Error: No such command' in result.output
