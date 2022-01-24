# Copyright 2017 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import socket
import time
from unittest import skip

import zuul.zk
import zuul.nodepool
from zuul import model

from tests.base import BaseTestCase


class TestNodepoolIntegration(BaseTestCase):
    # Tests the Nodepool interface class using a *real* nodepool and
    # fake scheduler.

    def setUp(self):
        super(TestNodepoolIntegration, self).setUp()

        self.statsd = None
        self.zk_client = zuul.zk.ZooKeeperClient('localhost:2181')
        self.addCleanup(self.zk_client.disconnect)
        self.zk_client.connect()
        self.hostname = socket.gethostname()

        self.provisioned_requests = []
        # This class implements the scheduler methods zuul.nodepool
        # needs, so we pass 'self' as the scheduler.
        self.nodepool = zuul.nodepool.Nodepool(
            self.zk_client, self.hostname, self.statsd, self)

    def waitForRequests(self):
        # Wait until all requests are complete.
        while len(list(self.nodepool.getNodeRequests())):
            time.sleep(0.1)

    def onNodesProvisioned(self, request):
        # This is a scheduler method that the nodepool class calls
        # back when a request is provisioned.
        self.provisioned_requests.append(request)

    def test_node_request(self):
        # Test a simple node request

        nodeset = model.NodeSet()
        nodeset.addNode(model.Node(['controller'], 'fake-label'))
        job = model.Job('testjob')
        job.nodeset = nodeset
        request = self.nodepool.requestNodes(
            "test-uuid", job, "tenant", "pipeline", "provider", 0, 0)
        self.waitForRequests()
        self.assertEqual(len(self.provisioned_requests), 1)
        self.assertEqual(request.state, model.STATE_FULFILLED)

        # Accept the nodes
        self.nodepool.acceptNodes(request, request.id)
        nodeset = request.nodeset

        for node in nodeset.getNodes():
            self.assertIsNotNone(node.lock)
            self.assertEqual(node.state, model.STATE_READY)

        # Mark the nodes in use
        self.nodepool.useNodeSet(nodeset, tenant_name=None, project_name=None)
        for node in nodeset.getNodes():
            self.assertEqual(node.state, model.STATE_IN_USE)

        # Return the nodes
        self.nodepool.returnNodeSet(
            nodeset, build=None, tenant_name=None, project_name=None,
            duration=0)
        for node in nodeset.getNodes():
            self.assertIsNone(node.lock)
            self.assertEqual(node.state, model.STATE_USED)

    def test_invalid_node_request(self):
        # Test requests with an invalid node type fail
        nodeset = model.NodeSet()
        nodeset.addNode(model.Node(['controller'], 'invalid-label'))
        job = model.Job('testjob')
        job.nodeset = nodeset
        request = self.nodepool.requestNodes(
            "test-uuid", job, "tenant", "pipeline", "provider", 0, 0)
        self.waitForRequests()
        self.assertEqual(len(self.provisioned_requests), 1)
        self.assertEqual(request.state, model.STATE_FAILED)

    @skip("Disabled until nodepool is ready")
    def test_node_request_disconnect(self):
        # Test that node requests are re-submitted after disconnect

        nodeset = model.NodeSet()
        nodeset.addNode(model.Node(['controller'], 'ubuntu-xenial'))
        nodeset.addNode(model.Node(['compute'], 'ubuntu-xenial'))
        job = model.Job('testjob')
        job.nodeset = nodeset
        self.fake_nodepool.paused = True
        request = self.nodepool.requestNodes(
            "test-uuid", job, "tenant", "pipeline", "provider", 0, 0)
        self.zk_client.client.stop()
        self.zk_client.client.start()
        self.fake_nodepool.paused = False
        self.waitForRequests()
        self.assertEqual(len(self.provisioned_requests), 1)
        self.assertEqual(request.state, model.STATE_FULFILLED)

    @skip("Disabled until nodepool is ready")
    def test_node_request_canceled(self):
        # Test that node requests can be canceled

        nodeset = model.NodeSet()
        nodeset.addNode(model.Node(['controller'], 'ubuntu-xenial'))
        nodeset.addNode(model.Node(['compute'], 'ubuntu-xenial'))
        job = model.Job('testjob')
        job.nodeset = nodeset
        self.fake_nodepool.paused = True
        request = self.nodepool.requestNodes(
            "test-uuid", job, "tenant", "pipeline", "provider", 0, 0)
        self.nodepool.cancelRequest(request)

        self.waitForRequests()
        self.assertEqual(len(self.provisioned_requests), 0)
