# Copyright 2020 BMW Group
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

import zuul.rpcclient

from tests.base import ZuulTestCase, simple_layout


class TestReporting(ZuulTestCase):
    tenant_config_file = "config/single-tenant/main.yaml"

    @simple_layout("layouts/dequeue-reporting.yaml")
    def test_dequeue_reporting(self):
        """Check that explicitly dequeued items are reported as dequeued"""

        # We use the rpcclient to explicitly dequeue the item
        client = zuul.rpcclient.RPCClient(
            "127.0.0.1", self.gearman_server.port
        )
        self.addCleanup(client.shutdown)

        self.executor_server.hold_jobs_in_build = True
        A = self.fake_gerrit.addFakeChange("org/project", "master", "A")
        A.addApproval("Code-Review", 2)
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        client.dequeue(
            tenant="tenant-one",
            pipeline="check",
            project="org/project",
            change="1,1",
            ref=None,
        )
        self.waitUntilSettled()

        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        check_pipeline = tenant.layout.pipelines['check']

        # A should have been reported two times: start, cancel
        self.assertEqual(2, A.reported)
        self.assertEqual(2, len(A.messages))
        self.assertIn("Build started (check)", A.messages[0])
        self.assertIn("Build canceled (check)", A.messages[1])
        # There shouldn't be any successful items
        self.assertEqual(len(check_pipeline.getAllItems()), 0)
        # But one canceled
        self.assertEqual(self.countJobResults(self.history, "ABORTED"), 1)

    @simple_layout("layouts/dequeue-reporting.yaml")
    def test_dequeue_reporting_gate_reset(self):
        """Check that a gate reset is not reported as dequeued"""

        A = self.fake_gerrit.addFakeChange("org/project", "master", "A")
        B = self.fake_gerrit.addFakeChange("org/project", "master", "B")
        A.addApproval("Code-Review", 2)
        B.addApproval("Code-Review", 2)

        self.executor_server.failJob("project-test1", A)

        self.fake_gerrit.addEvent(A.addApproval("Approved", 1))
        self.fake_gerrit.addEvent(B.addApproval("Approved", 1))
        self.waitUntilSettled()

        # None of the items should be reported as dequeued, only success or
        # failure
        self.assertEqual(A.data["status"], "NEW")
        self.assertEqual(B.data["status"], "MERGED")
        self.assertEqual(A.reported, 2)
        self.assertEqual(B.reported, 2)

        self.assertIn("Build started (gate)", A.messages[0])
        self.assertIn("Build failed (gate)", A.messages[1])
        self.assertIn("Build started (gate)", B.messages[0])
        self.assertIn("Build succeeded (gate)", B.messages[1])

    @simple_layout("layouts/dequeue-reporting.yaml")
    def test_dequeue_reporting_supercedes(self):
        """Test that a superceeded change is reported as dequeued"""

        self.executor_server.hold_jobs_in_build = True

        A = self.fake_gerrit.addFakeChange("org/project", "master", "A")
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        A.addApproval("Code-Review", 2)
        self.fake_gerrit.addEvent(A.addApproval("Approved", 1))

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertEqual(4, A.reported)

        self.assertIn("Build started (check)", A.messages[0])
        self.assertIn("Build canceled (check)", A.messages[1])
        self.assertIn("Build started (gate)", A.messages[2])
        self.assertIn("Build succeeded (gate)", A.messages[3])

    @simple_layout("layouts/dequeue-reporting.yaml")
    def test_dequeue_reporting_new_patchset(self):
        "Test that change superceeded by a new patchset is reported as deqeued"

        self.executor_server.hold_jobs_in_build = True

        A = self.fake_gerrit.addFakeChange("org/project", "master", "A")
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        self.assertEqual(1, len(self.builds))

        A.addPatchset()
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(2))
        self.waitUntilSettled()

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertEqual(4, A.reported)

        self.assertIn("Build started (check)", A.messages[0])
        self.assertIn("Build canceled (check)", A.messages[1])
        self.assertIn("Build started (check)", A.messages[2])
        self.assertIn("Build succeeded (check)", A.messages[3])
