# Copyright 2019 BMW Group
#
# This module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>.

import textwrap

import zuul.rpcclient

from tests.base import ZuulTestCase


class TestGerritCircularDependencies(ZuulTestCase):
    config_file = "zuul-gerrit-github.conf"
    tenant_config_file = "config/circular-dependencies/main.yaml"

    def _test_simple_cycle(self, project1, project2):
        A = self.fake_gerrit.addFakeChange(project1, "master", "A")
        B = self.fake_gerrit.addFakeChange(project2, "master", "B")

        # A <-> B (via commit-depends)
        A.data["commitMessage"] = "{}\n\nDepends-On: {}\n".format(
            A.subject, B.data["url"]
        )
        B.data["commitMessage"] = "{}\n\nDepends-On: {}\n".format(
            B.subject, A.data["url"]
        )

        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        self.assertEqual(len(A.patchsets[-1]["approvals"]), 1)
        self.assertEqual(A.patchsets[-1]["approvals"][0]["type"], "Verified")
        self.assertEqual(A.patchsets[-1]["approvals"][0]["value"], "1")

        self.assertEqual(len(B.patchsets[-1]["approvals"]), 1)
        self.assertEqual(B.patchsets[-1]["approvals"][0]["type"], "Verified")
        self.assertEqual(B.patchsets[-1]["approvals"][0]["value"], "1")

        # We're about to add approvals to changes without adding the
        # triggering events to Zuul, so that we can be sure that it is
        # enqueing the changes based on dependencies, not because of
        # triggering events.  Since it will have the changes cached
        # already (without approvals), we need to clear the cache
        # first.
        for connection in self.scheds.first.connections.connections.values():
            connection.maintainCache([], max_age=0)

        A.addApproval("Code-Review", 2)
        B.addApproval("Code-Review", 2)
        A.addApproval("Approved", 1)
        self.fake_gerrit.addEvent(B.addApproval("Approved", 1))
        self.waitUntilSettled()

        self.assertEqual(A.reported, 3)
        self.assertEqual(B.reported, 3)
        self.assertEqual(A.data["status"], "MERGED")
        self.assertEqual(B.data["status"], "MERGED")

    def _test_transitive_cycle(self, project1, project2, project3):
        A = self.fake_gerrit.addFakeChange(project1, "master", "A")
        B = self.fake_gerrit.addFakeChange(project2, "master", "B")
        C = self.fake_gerrit.addFakeChange(project3, "master", "C")

        # A -> B -> C -> A (via commit-depends)
        A.data["commitMessage"] = "{}\n\nDepends-On: {}\n".format(
            A.subject, B.data["url"]
        )
        B.data["commitMessage"] = "{}\n\nDepends-On: {}\n".format(
            B.subject, C.data["url"]
        )
        C.data["commitMessage"] = "{}\n\nDepends-On: {}\n".format(
            C.subject, A.data["url"]
        )

        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(1))
        self.fake_gerrit.addEvent(C.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        self.assertEqual(len(A.patchsets[-1]["approvals"]), 1)
        self.assertEqual(A.patchsets[-1]["approvals"][0]["type"], "Verified")
        self.assertEqual(A.patchsets[-1]["approvals"][0]["value"], "1")

        self.assertEqual(len(B.patchsets[-1]["approvals"]), 1)
        self.assertEqual(B.patchsets[-1]["approvals"][0]["type"], "Verified")
        self.assertEqual(B.patchsets[-1]["approvals"][0]["value"], "1")

        self.assertEqual(len(C.patchsets[-1]["approvals"]), 1)
        self.assertEqual(C.patchsets[-1]["approvals"][0]["type"], "Verified")
        self.assertEqual(C.patchsets[-1]["approvals"][0]["value"], "1")

        # We're about to add approvals to changes without adding the
        # triggering events to Zuul, so that we can be sure that it is
        # enqueing the changes based on dependencies, not because of
        # triggering events.  Since it will have the changes cached
        # already (without approvals), we need to clear the cache
        # first.
        for connection in self.scheds.first.connections.connections.values():
            connection.maintainCache([], max_age=0)

        A.addApproval("Code-Review", 2)
        B.addApproval("Code-Review", 2)
        C.addApproval("Code-Review", 2)
        C.addApproval("Approved", 1)
        A.addApproval("Approved", 1)
        self.fake_gerrit.addEvent(B.addApproval("Approved", 1))
        self.waitUntilSettled()

        self.assertEqual(A.reported, 3)
        self.assertEqual(B.reported, 3)
        self.assertEqual(C.reported, 3)
        self.assertEqual(A.data["status"], "MERGED")
        self.assertEqual(B.data["status"], "MERGED")
        self.assertEqual(C.data["status"], "MERGED")

    def test_single_project_cycle(self):
        self._test_simple_cycle("org/project", "org/project")

    def test_crd_cycle(self):
        self._test_simple_cycle("org/project1", "org/project2")

    def test_single_project_transitive_cycle(self):
        self._test_transitive_cycle(
            "org/project1", "org/project1", "org/project1"
        )

    def test_crd_transitive_cycle(self):
        self._test_transitive_cycle(
            "org/project", "org/project1", "org/project2"
        )

    def test_forbidden_cycle(self):
        A = self.fake_gerrit.addFakeChange("org/project", "master", "A")
        B = self.fake_gerrit.addFakeChange("org/project3", "master", "B")

        # A <-> B (via commit-depends)
        A.data["commitMessage"] = "{}\n\nDepends-On: {}\n".format(
            A.subject, B.data["url"]
        )
        B.data["commitMessage"] = "{}\n\nDepends-On: {}\n".format(
            B.subject, A.data["url"]
        )

        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        self.assertEqual(len(A.patchsets[-1]["approvals"]), 1)
        self.assertEqual(A.patchsets[-1]["approvals"][0]["type"], "Verified")
        self.assertEqual(A.patchsets[-1]["approvals"][0]["value"], "-1")

        self.assertEqual(len(B.patchsets[-1]["approvals"]), 1)
        self.assertEqual(B.patchsets[-1]["approvals"][0]["type"], "Verified")
        self.assertEqual(B.patchsets[-1]["approvals"][0]["value"], "-1")

        # We're about to add approvals to changes without adding the
        # triggering events to Zuul, so that we can be sure that it is
        # enqueing the changes based on dependencies, not because of
        # triggering events.  Since it will have the changes cached
        # already (without approvals), we need to clear the cache
        # first.
        for connection in self.scheds.first.connections.connections.values():
            connection.maintainCache([], max_age=0)

        A.addApproval("Code-Review", 2)
        B.addApproval("Code-Review", 2)
        B.addApproval("Approved", 1)
        self.fake_gerrit.addEvent(A.addApproval("Approved", 1))
        self.waitUntilSettled()

        self.assertEqual(A.reported, 1)
        self.assertEqual(B.reported, 1)
        self.assertEqual(A.data["status"], "NEW")
        self.assertEqual(B.data["status"], "NEW")

    def test_git_dependency_with_cycle(self):
        A = self.fake_gerrit.addFakeChange("org/project", "master", "A")
        B = self.fake_gerrit.addFakeChange("org/project", "master", "B")
        C = self.fake_gerrit.addFakeChange("org/project1", "master", "C")

        # A -> B (git) -> C -> A
        A.setDependsOn(B, 1)
        B.data["commitMessage"] = "{}\n\nDepends-On: {}\n".format(
            B.subject, C.data["url"]
        )
        C.data["commitMessage"] = "{}\n\nDepends-On: {}\n".format(
            C.subject, A.data["url"]
        )

        self.fake_gerrit.addEvent(C.getPatchsetCreatedEvent(1))
        self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(1))
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        self.assertEqual(len(A.patchsets[-1]["approvals"]), 1)
        self.assertEqual(A.patchsets[-1]["approvals"][0]["type"], "Verified")
        self.assertEqual(A.patchsets[-1]["approvals"][0]["value"], "1")

        self.assertEqual(len(B.patchsets[-1]["approvals"]), 1)
        self.assertEqual(B.patchsets[-1]["approvals"][0]["type"], "Verified")
        self.assertEqual(B.patchsets[-1]["approvals"][0]["value"], "1")

        self.assertEqual(len(C.patchsets[-1]["approvals"]), 1)
        self.assertEqual(C.patchsets[-1]["approvals"][0]["type"], "Verified")
        self.assertEqual(C.patchsets[-1]["approvals"][0]["value"], "1")

        # We're about to add approvals to changes without adding the
        # triggering events to Zuul, so that we can be sure that it is
        # enqueing the changes based on dependencies, not because of
        # triggering events.  Since it will have the changes cached
        # already (without approvals), we need to clear the cache
        # first.
        for connection in self.scheds.first.connections.connections.values():
            connection.maintainCache([], max_age=0)

        self.executor_server.hold_jobs_in_build = True
        A.addApproval("Code-Review", 2)
        B.addApproval("Code-Review", 2)
        C.addApproval("Code-Review", 2)
        A.addApproval("Approved", 1)
        B.addApproval("Approved", 1)
        self.fake_gerrit.addEvent(C.addApproval("Approved", 1))
        self.waitUntilSettled()

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertEqual(A.reported, 3)
        self.assertEqual(B.reported, 3)
        self.assertEqual(C.reported, 3)
        self.assertEqual(A.data["status"], "MERGED")
        self.assertEqual(B.data["status"], "MERGED")
        self.assertEqual(C.data["status"], "MERGED")

    def test_dependency_on_cycle(self):
        A = self.fake_gerrit.addFakeChange("org/project", "master", "A")
        B = self.fake_gerrit.addFakeChange("org/project1", "master", "B")
        C = self.fake_gerrit.addFakeChange("org/project2", "master", "C")

        # A -> B -> C -> B (via commit-depends)
        A.data["commitMessage"] = "{}\n\nDepends-On: {}\n".format(
            A.subject, B.data["url"]
        )
        B.data["commitMessage"] = "{}\n\nDepends-On: {}\n".format(
            B.subject, C.data["url"]
        )
        C.data["commitMessage"] = "{}\n\nDepends-On: {}\n".format(
            C.subject, B.data["url"]
        )

        self.fake_gerrit.addEvent(C.getPatchsetCreatedEvent(1))
        self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(1))
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        self.assertEqual(len(A.patchsets[-1]["approvals"]), 1)
        self.assertEqual(A.patchsets[-1]["approvals"][0]["type"], "Verified")
        self.assertEqual(A.patchsets[-1]["approvals"][0]["value"], "1")

        self.assertEqual(len(B.patchsets[-1]["approvals"]), 1)
        self.assertEqual(B.patchsets[-1]["approvals"][0]["type"], "Verified")
        self.assertEqual(B.patchsets[-1]["approvals"][0]["value"], "1")

        self.assertEqual(len(C.patchsets[-1]["approvals"]), 1)
        self.assertEqual(C.patchsets[-1]["approvals"][0]["type"], "Verified")
        self.assertEqual(C.patchsets[-1]["approvals"][0]["value"], "1")

        # We're about to add approvals to changes without adding the
        # triggering events to Zuul, so that we can be sure that it is
        # enqueing the changes based on dependencies, not because of
        # triggering events.  Since it will have the changes cached
        # already (without approvals), we need to clear the cache
        # first.
        for connection in self.scheds.first.connections.connections.values():
            connection.maintainCache([], max_age=0)

        A.addApproval("Code-Review", 2)
        B.addApproval("Code-Review", 2)
        C.addApproval("Code-Review", 2)
        B.addApproval("Approved", 1)
        C.addApproval("Approved", 1)
        self.fake_gerrit.addEvent(A.addApproval("Approved", 1))
        self.waitUntilSettled()

        self.assertEqual(A.reported, 3)
        self.assertEqual(B.reported, 3)
        self.assertEqual(C.reported, 3)
        self.assertEqual(A.data["status"], "MERGED")
        self.assertEqual(B.data["status"], "MERGED")
        self.assertEqual(C.data["status"], "MERGED")

    def test_dependent_change_on_cycle(self):
        self.executor_server.hold_jobs_in_build = True

        A = self.fake_gerrit.addFakeChange("org/project", "master", "A")
        B = self.fake_gerrit.addFakeChange("org/project", "master", "B")
        C = self.fake_gerrit.addFakeChange("org/project2", "master", "C")

        A.setDependsOn(B, 1)
        B.data["commitMessage"] = "{}\n\nDepends-On: {}\n".format(
            B.subject, C.data["url"]
        )
        C.data["commitMessage"] = "{}\n\nDepends-On: {}\n".format(
            C.subject, B.data["url"]
        )

        A.addApproval("Code-Review", 2)
        A.addApproval("Approved", 1)
        B.addApproval("Code-Review", 2)
        B.addApproval("Approved", 1)
        C.addApproval("Code-Review", 2)
        self.fake_gerrit.addEvent(C.addApproval("Approved", 1))
        self.waitUntilSettled()

        self.assertEqual(len(self.builds), 3)

        # Make sure the out-of-cycle change (A) is enqueued after the cycle.
        tenant = self.scheds.first.sched.abide.tenants.get("tenant-one")
        queue_change_numbers = []
        for queue in tenant.layout.pipelines["gate"].queues:
            for item in queue.queue:
                queue_change_numbers.append(item.change.number)
        self.assertEqual(queue_change_numbers, ['2', '3', '1'])

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertEqual(A.reported, 2)
        self.assertEqual(B.reported, 2)
        self.assertEqual(C.reported, 2)
        self.assertEqual(A.data["status"], "MERGED")
        self.assertEqual(B.data["status"], "MERGED")
        self.assertEqual(C.data["status"], "MERGED")

    def test_cycle_dependency_on_cycle(self):
        A = self.fake_gerrit.addFakeChange("org/project", "master", "A")
        B = self.fake_gerrit.addFakeChange("org/project1", "master", "B")
        C = self.fake_gerrit.addFakeChange("org/project1", "master", "C")
        D = self.fake_gerrit.addFakeChange("org/project2", "master", "D")

        # A -> B -> A + C
        # C -> D -> C
        A.data["commitMessage"] = "{}\n\nDepends-On: {}\n".format(
            A.subject, B.data["url"]
        )
        B.data[
            "commitMessage"
        ] = "{}\n\nDepends-On: {}\nDepends-On: {}\n".format(
            B.subject, A.data["url"], C.data["url"]
        )
        C.data["commitMessage"] = "{}\n\nDepends-On: {}\n".format(
            C.subject, D.data["url"]
        )
        D.data["commitMessage"] = "{}\n\nDepends-On: {}\n".format(
            D.subject, C.data["url"]
        )

        self.fake_gerrit.addEvent(D.getPatchsetCreatedEvent(1))
        self.fake_gerrit.addEvent(C.getPatchsetCreatedEvent(1))
        self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(1))
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        self.assertEqual(len(A.patchsets[-1]["approvals"]), 1)
        self.assertEqual(A.patchsets[-1]["approvals"][0]["type"], "Verified")
        self.assertEqual(A.patchsets[-1]["approvals"][0]["value"], "1")

        self.assertEqual(len(B.patchsets[-1]["approvals"]), 1)
        self.assertEqual(B.patchsets[-1]["approvals"][0]["type"], "Verified")
        self.assertEqual(B.patchsets[-1]["approvals"][0]["value"], "1")

        self.assertEqual(len(C.patchsets[-1]["approvals"]), 1)
        self.assertEqual(C.patchsets[-1]["approvals"][0]["type"], "Verified")
        self.assertEqual(C.patchsets[-1]["approvals"][0]["value"], "1")

        self.assertEqual(len(D.patchsets[-1]["approvals"]), 1)
        self.assertEqual(D.patchsets[-1]["approvals"][0]["type"], "Verified")
        self.assertEqual(D.patchsets[-1]["approvals"][0]["value"], "1")

        # We're about to add approvals to changes without adding the
        # triggering events to Zuul, so that we can be sure that it is
        # enqueing the changes based on dependencies, not because of
        # triggering events.  Since it will have the changes cached
        # already (without approvals), we need to clear the cache
        # first.
        for connection in self.scheds.first.connections.connections.values():
            connection.maintainCache([], max_age=0)

        A.addApproval("Code-Review", 2)
        B.addApproval("Code-Review", 2)
        C.addApproval("Code-Review", 2)
        D.addApproval("Code-Review", 2)
        B.addApproval("Approved", 1)
        C.addApproval("Approved", 1)
        D.addApproval("Approved", 1)
        self.fake_gerrit.addEvent(A.addApproval("Approved", 1))
        self.waitUntilSettled()

        self.assertEqual(A.reported, 3)
        self.assertEqual(B.reported, 3)
        self.assertEqual(C.reported, 3)
        self.assertEqual(D.reported, 3)
        self.assertEqual(A.data["status"], "MERGED")
        self.assertEqual(B.data["status"], "MERGED")
        self.assertEqual(C.data["status"], "MERGED")
        self.assertEqual(D.data["status"], "MERGED")

    def test_cycle_failure(self):
        A = self.fake_gerrit.addFakeChange("org/project", "master", "A")
        B = self.fake_gerrit.addFakeChange("org/project1", "master", "B")

        # A <-> B (via commit-depends)
        A.data["commitMessage"] = "{}\n\nDepends-On: {}\n".format(
            A.subject, B.data["url"]
        )
        B.data["commitMessage"] = "{}\n\nDepends-On: {}\n".format(
            B.subject, A.data["url"]
        )

        self.executor_server.failJob("project-job", A)
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        self.assertEqual(len(A.patchsets[-1]["approvals"]), 1)
        self.assertEqual(A.patchsets[-1]["approvals"][0]["type"], "Verified")
        self.assertEqual(A.patchsets[-1]["approvals"][0]["value"], "-1")

        # We're about to add approvals to changes without adding the
        # triggering events to Zuul, so that we can be sure that it is
        # enqueing the changes based on dependencies, not because of
        # triggering events.  Since it will have the changes cached
        # already (without approvals), we need to clear the cache
        # first.
        for connection in self.scheds.first.connections.connections.values():
            connection.maintainCache([], max_age=0)

        A.addApproval("Code-Review", 2)
        B.addApproval("Code-Review", 2)
        B.addApproval("Approved", 1)

        self.executor_server.failJob("project-job", A)
        self.fake_gerrit.addEvent(A.addApproval("Approved", 1))
        self.waitUntilSettled()

        self.assertEqual(A.reported, 3)
        self.assertEqual(B.reported, 3)
        self.assertIn("bundle", A.messages[-1])
        self.assertIn("bundle", B.messages[-1])
        self.assertEqual(A.data["status"], "NEW")
        self.assertEqual(B.data["status"], "NEW")

    def test_dependency_on_cycle_failure(self):
        A = self.fake_gerrit.addFakeChange("org/project", "master", "A")
        B = self.fake_gerrit.addFakeChange("org/project1", "master", "B")
        C = self.fake_gerrit.addFakeChange("org/project2", "master", "C")
        A.addApproval("Code-Review", 2)
        B.addApproval("Code-Review", 2)
        B.addApproval("Approved", 1)
        C.addApproval("Code-Review", 2)
        C.addApproval("Approved", 1)

        # A -> B -> C -> B (via commit-depends)
        A.data["commitMessage"] = "{}\n\nDepends-On: {}\n".format(
            A.subject, B.data["url"]
        )
        B.data["commitMessage"] = "{}\n\nDepends-On: {}\n".format(
            B.subject, C.data["url"]
        )
        C.data["commitMessage"] = "{}\n\nDepends-On: {}\n".format(
            C.subject, B.data["url"]
        )

        self.executor_server.failJob("project2-job", C)
        self.fake_gerrit.addEvent(A.addApproval("Approved", 1))
        self.waitUntilSettled()

        self.assertIn("depends on a change that failed to merge",
                      A.messages[-1])
        self.assertIn("bundle that failed.", B.messages[-1])
        self.assertIn("bundle that failed.", C.messages[-1])
        self.assertEqual(A.data["status"], "NEW")
        self.assertEqual(B.data["status"], "NEW")
        self.assertEqual(C.data["status"], "NEW")

    def test_cycle_dependency_on_change(self):
        A = self.fake_gerrit.addFakeChange("org/project", "master", "A")
        B = self.fake_gerrit.addFakeChange("org/project1", "master", "B")
        C = self.fake_gerrit.addFakeChange("org/project2", "master", "C")

        # A -> B -> A + C (git)
        A.data["commitMessage"] = "{}\n\nDepends-On: {}\n".format(
            A.subject, B.data["url"]
        )
        B.data["commitMessage"] = "{}\n\nDepends-On: {}\n".format(
            B.subject, A.data["url"]
        )
        B.setDependsOn(C, 1)

        self.fake_gerrit.addEvent(C.getPatchsetCreatedEvent(1))
        self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(1))
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        self.assertEqual(len(A.patchsets[-1]["approvals"]), 1)
        self.assertEqual(A.patchsets[-1]["approvals"][0]["type"], "Verified")
        self.assertEqual(A.patchsets[-1]["approvals"][0]["value"], "1")

        self.assertEqual(len(B.patchsets[-1]["approvals"]), 1)
        self.assertEqual(B.patchsets[-1]["approvals"][0]["type"], "Verified")
        self.assertEqual(B.patchsets[-1]["approvals"][0]["value"], "1")

        self.assertEqual(len(C.patchsets[-1]["approvals"]), 1)
        self.assertEqual(C.patchsets[-1]["approvals"][0]["type"], "Verified")
        self.assertEqual(C.patchsets[-1]["approvals"][0]["value"], "1")

        # We're about to add approvals to changes without adding the
        # triggering events to Zuul, so that we can be sure that it is
        # enqueing the changes based on dependencies, not because of
        # triggering events.  Since it will have the changes cached
        # already (without approvals), we need to clear the cache
        # first.
        for connection in self.scheds.first.connections.connections.values():
            connection.maintainCache([], max_age=0)

        A.addApproval("Code-Review", 2)
        B.addApproval("Code-Review", 2)
        C.addApproval("Code-Review", 2)
        A.addApproval("Approved", 1)
        B.addApproval("Approved", 1)
        self.fake_gerrit.addEvent(C.addApproval("Approved", 1))
        self.waitUntilSettled()

        self.assertEqual(A.reported, 3)
        self.assertEqual(B.reported, 3)
        self.assertEqual(C.reported, 3)
        self.assertEqual(A.data["status"], "MERGED")
        self.assertEqual(B.data["status"], "MERGED")
        self.assertEqual(C.data["status"], "MERGED")

    def test_failing_cycle_dependency_on_change(self):
        A = self.fake_gerrit.addFakeChange("org/project", "master", "A")
        B = self.fake_gerrit.addFakeChange("org/project1", "master", "B")
        C = self.fake_gerrit.addFakeChange("org/project2", "master", "C")
        A.addApproval("Code-Review", 2)
        B.addApproval("Code-Review", 2)
        B.addApproval("Approved", 1)
        C.addApproval("Code-Review", 2)
        C.addApproval("Approved", 1)

        # A -> B -> A + C (via commit-depends)
        A.data["commitMessage"] = "{}\n\nDepends-On: {}\n".format(
            A.subject, B.data["url"]
        )
        B.data[
            "commitMessage"
        ] = "{}\n\nDepends-On: {}\nDepends-On: {}\n".format(
            B.subject, A.data["url"], C.data["url"]
        )

        self.executor_server.failJob("project-job", A)
        self.fake_gerrit.addEvent(A.addApproval("Approved", 1))
        self.waitUntilSettled()

        self.assertEqual(A.reported, 2)
        self.assertEqual(B.reported, 2)
        self.assertEqual(C.reported, 2)
        self.assertEqual(A.data["status"], "NEW")
        self.assertEqual(B.data["status"], "NEW")
        self.assertEqual(C.data["status"], "MERGED")

    def test_reopen_cycle(self):
        self.executor_server.hold_jobs_in_build = True
        A = self.fake_gerrit.addFakeChange("org/project", "master", "A")
        B = self.fake_gerrit.addFakeChange("org/project2", "master", "B")

        # A <-> B (via commit-depends)
        A.data["commitMessage"] = "{}\n\nDepends-On: {}\n".format(
            A.subject, B.data["url"]
        )
        B.data["commitMessage"] = "{}\n\nDepends-On: {}\n".format(
            B.subject, A.data["url"]
        )

        A.addApproval("Code-Review", 2)
        B.addApproval("Code-Review", 2)
        A.addApproval("Approved", 1)

        self.fake_gerrit.addEvent(B.addApproval("Approved", 1))
        self.waitUntilSettled()

        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        items_before = tenant.layout.pipelines['gate'].getAllItems()

        # Trigger a re-enqueue of change B
        self.fake_gerrit.addEvent(B.getChangeAbandonedEvent())
        self.fake_gerrit.addEvent(B.getChangeRestoredEvent())
        self.fake_gerrit.addEvent(B.addApproval("Approved", 1))
        self.waitUntilSettled()

        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        items_after = tenant.layout.pipelines['gate'].getAllItems()

        # Make sure the complete cycle was re-enqueued
        for before, after in zip(items_before, items_after):
            self.assertNotEqual(before, after)

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertEqual(A.reported, 3)
        self.assertEqual(B.reported, 3)
        self.assertEqual(A.data["status"], "MERGED")
        self.assertEqual(B.data["status"], "MERGED")

    def test_cycle_larger_pipeline_window(self):
        tenant = self.scheds.first.sched.abide.tenants.get("tenant-one")

        # Make the gate window smaller than the length of the cycle
        for queue in tenant.layout.pipelines["gate"].queues:
            if any("org/project" in p.name for p in queue.projects):
                queue.window = 1

        self._test_simple_cycle("org/project", "org/project")

    def test_cycle_reporting_failure(self):
        A = self.fake_gerrit.addFakeChange("org/project", "master", "A")
        B = self.fake_gerrit.addFakeChange("org/project1", "master", "B")
        A.addApproval("Code-Review", 2)
        B.addApproval("Code-Review", 2)
        B.addApproval("Approved", 1)

        B.fail_merge = True

        # A <-> B (via commit-depends)
        A.data["commitMessage"] = "{}\n\nDepends-On: {}\n".format(
            A.subject, B.data["url"]
        )
        B.data["commitMessage"] = "{}\n\nDepends-On: {}\n".format(
            B.subject, A.data["url"]
        )

        self.fake_gerrit.addEvent(A.addApproval("Approved", 1))
        self.waitUntilSettled()

        self.assertEqual(A.reported, 2)
        self.assertEqual(B.reported, 3)
        self.assertEqual(A.patchsets[-1]["approvals"][-1]["value"], "-2")
        self.assertEqual(B.patchsets[-1]["approvals"][-1]["value"], "-2")
        self.assertIn("bundle", A.messages[-1])
        self.assertIn("bundle", B.messages[-1])
        self.assertEqual(A.data["status"], "NEW")
        self.assertEqual(B.data["status"], "NEW")

    def test_cycle_reporting_partial_failure(self):
        A = self.fake_gerrit.addFakeChange("org/project", "master", "A")
        B = self.fake_gerrit.addFakeChange("org/project1", "master", "B")
        A.addApproval("Code-Review", 2)
        B.addApproval("Code-Review", 2)
        B.addApproval("Approved", 1)

        A.fail_merge = True

        # A <-> B (via commit-depends)
        A.data["commitMessage"] = "{}\n\nDepends-On: {}\n".format(
            A.subject, B.data["url"]
        )
        B.data["commitMessage"] = "{}\n\nDepends-On: {}\n".format(
            B.subject, A.data["url"]
        )

        self.fake_gerrit.addEvent(A.addApproval("Approved", 1))
        self.waitUntilSettled()

        self.assertEqual(A.reported, 3)
        self.assertEqual(B.reported, 3)
        self.assertIn("bundle", A.messages[-1])
        self.assertIn("bundle", B.messages[-1])
        self.assertEqual(A.data["status"], "NEW")
        self.assertEqual(B.data["status"], "MERGED")

    def test_gate_reset_with_cycle(self):
        self.executor_server.hold_jobs_in_build = True
        A = self.fake_gerrit.addFakeChange("org/project", "master", "A")
        B = self.fake_gerrit.addFakeChange("org/project1", "master", "B")
        C = self.fake_gerrit.addFakeChange("org/project1", "master", "C")

        # A <-> B (via depends-on)
        A.data["commitMessage"] = "{}\n\nDepends-On: {}\n".format(
            A.subject, B.data["url"]
        )
        B.data["commitMessage"] = "{}\n\nDepends-On: {}\n".format(
            B.subject, A.data["url"]
        )

        A.addApproval("Code-Review", 2)
        B.addApproval("Code-Review", 2)
        C.addApproval("Code-Review", 2)
        C.addApproval("Approved", 1)
        B.addApproval("Approved", 1)
        self.fake_gerrit.addEvent(C.addApproval("Approved", 1))
        self.fake_gerrit.addEvent(A.addApproval("Approved", 1))
        self.waitUntilSettled()

        self.executor_server.failJob("project1-job", C)
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertEqual(len(self.builds), 3)
        for build in self.builds:
            self.assertTrue(build.hasChanges(A, B))
            self.assertFalse(build.hasChanges(C))

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertEqual(A.reported, 2)
        self.assertEqual(B.reported, 2)
        self.assertEqual(C.reported, 2)
        self.assertEqual(A.data["status"], "MERGED")
        self.assertEqual(B.data["status"], "MERGED")
        self.assertEqual(C.data["status"], "NEW")

    def test_independent_bundle_items(self):
        self.executor_server.hold_jobs_in_build = True
        A = self.fake_gerrit.addFakeChange("org/project", "master", "A")
        B = self.fake_gerrit.addFakeChange("org/project", "master", "B")

        # A <-> B (via commit-depends)
        A.data["commitMessage"] = "{}\n\nDepends-On: {}\n".format(
            A.subject, B.data["url"]
        )
        B.data["commitMessage"] = "{}\n\nDepends-On: {}\n".format(
            B.subject, A.data["url"]
        )

        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        tenant = self.scheds.first.sched.abide.tenants.get("tenant-one")
        for queue in tenant.layout.pipelines["check"].queues:
            for item in queue.queue:
                self.assertIn(item, item.bundle.items)
                self.assertEqual(len(item.bundle.items), 2)

        for build in self.builds:
            self.assertTrue(build.hasChanges(A, B))

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertEqual(len(A.patchsets[-1]["approvals"]), 1)
        self.assertEqual(A.patchsets[-1]["approvals"][0]["type"], "Verified")
        self.assertEqual(A.patchsets[-1]["approvals"][0]["value"], "1")

        self.assertEqual(len(B.patchsets[-1]["approvals"]), 1)
        self.assertEqual(B.patchsets[-1]["approvals"][0]["type"], "Verified")
        self.assertEqual(B.patchsets[-1]["approvals"][0]["value"], "1")

    def test_gate_correct_commits(self):
        self.executor_server.hold_jobs_in_build = True
        A = self.fake_gerrit.addFakeChange("org/project", "master", "A")
        B = self.fake_gerrit.addFakeChange("org/project1", "master", "B")
        C = self.fake_gerrit.addFakeChange("org/project1", "master", "C")
        D = self.fake_gerrit.addFakeChange("org/project", "master", "D")

        # A <-> B (via depends-on)
        A.data["commitMessage"] = "{}\n\nDepends-On: {}\n".format(
            A.subject, B.data["url"]
        )
        B.data["commitMessage"] = "{}\n\nDepends-On: {}\n".format(
            B.subject, A.data["url"]
        )
        D.setDependsOn(A, 1)

        A.addApproval("Code-Review", 2)
        B.addApproval("Code-Review", 2)
        C.addApproval("Code-Review", 2)
        D.addApproval("Code-Review", 2)
        C.addApproval("Approved", 1)
        B.addApproval("Approved", 1)
        self.fake_gerrit.addEvent(C.addApproval("Approved", 1))
        self.fake_gerrit.addEvent(A.addApproval("Approved", 1))
        self.fake_gerrit.addEvent(D.addApproval("Approved", 1))
        self.waitUntilSettled()

        for build in self.builds:
            if build.change in ("1 1", "2 1"):
                self.assertTrue(build.hasChanges(C, B, A))
                self.assertFalse(build.hasChanges(D))
            elif build.change == "3 1":
                self.assertTrue(build.hasChanges(C))
                self.assertFalse(build.hasChanges(A))
                self.assertFalse(build.hasChanges(B))
                self.assertFalse(build.hasChanges(D))
            else:
                self.assertTrue(build.hasChanges(C, B, A, D))

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertEqual(A.reported, 2)
        self.assertEqual(B.reported, 2)
        self.assertEqual(C.reported, 2)
        self.assertEqual(D.reported, 2)
        self.assertEqual(A.data["status"], "MERGED")
        self.assertEqual(B.data["status"], "MERGED")
        self.assertEqual(C.data["status"], "MERGED")
        self.assertEqual(D.data["status"], "MERGED")

    def test_cycle_git_dependency(self):
        A = self.fake_gerrit.addFakeChange("org/project", "master", "A")
        B = self.fake_gerrit.addFakeChange("org/project", "master", "B")
        A.addApproval("Code-Review", 2)
        B.addApproval("Code-Review", 2)
        B.addApproval("Approved", 1)

        # A -> B (via commit-depends)
        A.data["commitMessage"] = "{}\n\nDepends-On: {}\n".format(
            A.subject, B.data["url"]
        )
        # B -> A (via parent-child dependency)
        B.setDependsOn(A, 1)

        self.fake_gerrit.addEvent(A.addApproval("Approved", 1))
        self.waitUntilSettled()

        self.assertEqual(A.reported, 2)
        self.assertEqual(B.reported, 2)
        self.assertEqual(A.data["status"], "MERGED")
        self.assertEqual(B.data["status"], "MERGED")

    def test_cycle_git_dependency_failure(self):
        A = self.fake_gerrit.addFakeChange("org/project", "master", "A")
        B = self.fake_gerrit.addFakeChange("org/project", "master", "B")
        A.addApproval("Code-Review", 2)
        B.addApproval("Code-Review", 2)
        B.addApproval("Approved", 1)

        # A -> B (via commit-depends)
        A.data["commitMessage"] = "{}\n\nDepends-On: {}\n".format(
            A.subject, B.data["url"]
        )
        # B -> A (via parent-child dependency)
        B.setDependsOn(A, 1)

        self.executor_server.failJob("project-job", A)
        self.fake_gerrit.addEvent(A.addApproval("Approved", 1))
        self.waitUntilSettled()

        self.assertEqual(A.reported, 2)
        self.assertEqual(B.reported, 2)
        self.assertEqual(A.data["status"], "NEW")
        self.assertEqual(B.data["status"], "NEW")

    def test_independent_reporting(self):
        self.executor_server.hold_jobs_in_build = True
        A = self.fake_gerrit.addFakeChange("org/project", "master", "A")
        B = self.fake_gerrit.addFakeChange("org/project", "master", "B")

        # A <-> B (via commit-depends)
        A.data["commitMessage"] = "{}\n\nDepends-On: {}\n".format(
            A.subject, B.data["url"]
        )
        B.data["commitMessage"] = "{}\n\nDepends-On: {}\n".format(
            B.subject, A.data["url"]
        )

        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        self.fake_gerrit.addEvent(B.getChangeAbandonedEvent())
        self.waitUntilSettled()

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertEqual(len(A.patchsets[-1]["approvals"]), 1)
        self.assertEqual(A.patchsets[-1]["approvals"][0]["type"], "Verified")
        self.assertEqual(A.patchsets[-1]["approvals"][0]["value"], "1")

    def test_cycle_merge_conflict(self):
        self.hold_merge_jobs_in_queue = True
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'B')

        # A <-> B (via commit-depends)
        A.data["commitMessage"] = "{}\n\nDepends-On: {}\n".format(
            A.subject, B.data["url"]
        )
        B.data["commitMessage"] = "{}\n\nDepends-On: {}\n".format(
            B.subject, A.data["url"]
        )

        A.addApproval("Code-Review", 2)
        B.addApproval("Code-Review", 2)
        B.addApproval("Approved", 1)

        self.fake_gerrit.addEvent(A.addApproval("Approved", 1))
        self.waitUntilSettled()

        # We only want to have a merge failure for the first item in the queue
        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        items = tenant.layout.pipelines['gate'].getAllItems()
        context = self.createZKContext()
        items[0].current_build_set.updateAttributes(context,
                                                    unable_to_merge=True)

        self.waitUntilSettled()

        self.hold_merge_jobs_in_queue = False
        self.merger_api.release()
        self.waitUntilSettled()

        self.assertEqual(A.reported, 0)
        self.assertEqual(B.reported, 1)
        self.assertEqual(A.data["status"], "NEW")
        self.assertEqual(B.data["status"], "NEW")

    def test_circular_config_change(self):
        define_job = textwrap.dedent(
            """
            - job:
                name: new-job
            """)
        use_job = textwrap.dedent(
            """
            - project:
                check:
                  jobs:
                    - new-job
                gate:
                  queue: integrated
                  jobs:
                    - new-job
            """)
        A = self.fake_gerrit.addFakeChange("org/project", "master", "A",
                                           files={"zuul.yaml": define_job})
        B = self.fake_gerrit.addFakeChange("org/project1", "master", "B",
                                           files={"zuul.yaml": use_job})

        # A <-> B (via commit-depends)
        A.data["commitMessage"] = "{}\n\nDepends-On: {}\n".format(
            A.subject, B.data["url"]
        )
        B.data["commitMessage"] = "{}\n\nDepends-On: {}\n".format(
            B.subject, A.data["url"]
        )

        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        self.assertEqual(len(A.patchsets[-1]["approvals"]), 1)
        self.assertEqual(A.patchsets[-1]["approvals"][0]["type"], "Verified")
        self.assertEqual(A.patchsets[-1]["approvals"][0]["value"], "1")

        self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        self.assertEqual(len(B.patchsets[-1]["approvals"]), 1)
        self.assertEqual(B.patchsets[-1]["approvals"][0]["type"], "Verified")
        self.assertEqual(B.patchsets[-1]["approvals"][0]["value"], "1")

        A.addApproval("Code-Review", 2)
        B.addApproval("Code-Review", 2)
        self.fake_gerrit.addEvent(B.addApproval("Approved", 1))
        self.fake_gerrit.addEvent(A.addApproval("Approved", 1))
        self.waitUntilSettled()

        self.assertEqual(A.reported, 3)
        self.assertEqual(B.reported, 3)
        self.assertEqual(A.data["status"], "MERGED")
        self.assertEqual(B.data["status"], "MERGED")

    def test_circular_config_change_job_vars(self):
        org_project_files = {
            "zuul.yaml": textwrap.dedent(
                """
                - job:
                    name: project-vars-job
                    vars:
                      test_var: pass

                - project:
                    check:
                      jobs:
                        - project-vars-job
                    gate:
                      queue: integrated
                      jobs:
                        - project-vars-job
                """)
        }
        A = self.fake_gerrit.addFakeChange("org/project2", "master", "A",
                                           files=org_project_files)
        B = self.fake_gerrit.addFakeChange("org/project1", "master", "B")
        C = self.fake_gerrit.addFakeChange("org/project1", "master", "C")

        # C <-> A <-> B (via commit-depends)
        A.data["commitMessage"] = (
            "{}\n\nDepends-On: {}\nDepends-On: {}\n".format(
                A.subject, B.data["url"], C.data["url"]
            )
        )
        B.data["commitMessage"] = "{}\n\nDepends-On: {}\n".format(
            B.subject, A.data["url"]
        )
        C.data["commitMessage"] = "{}\n\nDepends-On: {}\n".format(
            C.subject, A.data["url"]
        )

        self.executor_server.hold_jobs_in_build = True
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        vars_builds = [b for b in self.builds if b.name == "project-vars-job"]
        self.assertEqual(len(vars_builds), 1)
        self.assertEqual(vars_builds[0].job.combined_variables["test_var"],
                         "pass")

        self.executor_server.release()
        self.waitUntilSettled()

        self.assertEqual(len(A.patchsets[-1]["approvals"]), 1)
        self.assertEqual(A.patchsets[-1]["approvals"][0]["type"], "Verified")
        self.assertEqual(A.patchsets[-1]["approvals"][0]["value"], "1")

        self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        vars_builds = [b for b in self.builds if b.name == "project-vars-job"]
        self.assertEqual(len(vars_builds), 1)
        self.assertEqual(vars_builds[0].job.combined_variables["test_var"],
                         "pass")

        self.executor_server.release()
        self.waitUntilSettled()

        self.assertEqual(len(B.patchsets[-1]["approvals"]), 1)
        self.assertEqual(B.patchsets[-1]["approvals"][0]["type"], "Verified")
        self.assertEqual(B.patchsets[-1]["approvals"][0]["value"], "1")

        self.fake_gerrit.addEvent(C.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        vars_builds = [b for b in self.builds if b.name == "project-vars-job"]
        self.assertEqual(len(vars_builds), 1)
        self.assertEqual(vars_builds[0].job.combined_variables["test_var"],
                         "pass")

        self.executor_server.release()
        self.waitUntilSettled()

        self.assertEqual(len(C.patchsets[-1]["approvals"]), 1)
        self.assertEqual(C.patchsets[-1]["approvals"][0]["type"], "Verified")
        self.assertEqual(C.patchsets[-1]["approvals"][0]["value"], "1")

        A.addApproval("Code-Review", 2)
        B.addApproval("Code-Review", 2)
        C.addApproval("Code-Review", 2)

        self.fake_gerrit.addEvent(A.addApproval("Approved", 1))
        self.fake_gerrit.addEvent(B.addApproval("Approved", 1))
        self.fake_gerrit.addEvent(C.addApproval("Approved", 1))
        self.waitUntilSettled()

        vars_builds = [b for b in self.builds if b.name == "project-vars-job"]
        self.assertEqual(len(vars_builds), 3)
        for build in vars_builds:
            self.assertEqual(build.job.combined_variables["test_var"],
                             "pass")

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertEqual(A.reported, 3)
        self.assertEqual(B.reported, 3)
        self.assertEqual(C.reported, 3)
        self.assertEqual(A.data["status"], "MERGED")
        self.assertEqual(B.data["status"], "MERGED")
        self.assertEqual(C.data["status"], "MERGED")

    def test_cross_tenant_cycle(self):
        org_project_files = {
            "zuul.yaml": textwrap.dedent(
                """
                - job:
                    name: project-vars-job
                    vars:
                      test_var: pass

                - project:
                    check:
                      jobs:
                        - project-vars-job
                    gate:
                      queue: integrated
                      jobs:
                        - project-vars-job
                """)
        }
        # Change zuul config so the bundle is considered updating config
        A = self.fake_gerrit.addFakeChange("org/project2", "master", "A",
                                           files=org_project_files)
        B = self.fake_gerrit.addFakeChange("org/project1", "master", "B")
        C = self.fake_gerrit.addFakeChange("org/project1", "master", "C")
        D = self.fake_gerrit.addFakeChange("org/project4", "master", "D",)

        # C <-> A <-> B (via commit-depends)
        A.data["commitMessage"] = (
            "{}\n\nDepends-On: {}\nDepends-On: {}\n".format(
                A.subject, B.data["url"], C.data["url"]
            )
        )
        # A <-> B (via commit-depends)
        B.data["commitMessage"] = "{}\n\nDepends-On: {}\n".format(
            B.subject, A.data["url"]
        )
        # A <-> C <-> D (via commit-depends)
        C.data["commitMessage"] = (
            "{}\n\nDepends-On: {}\nDepends-On: {}\n".format(
                C.subject, A.data["url"], D.data["url"]
            )
        )
        # D <-> C (via commit-depends)
        D.data["commitMessage"] = "{}\n\nDepends-On: {}\n".format(
            D.subject, C.data["url"]
        )

        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(1))
        self.fake_gerrit.addEvent(C.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        self.assertEqual(len(A.patchsets[-1]["approvals"]), 1)
        self.assertEqual(A.patchsets[-1]["approvals"][0]["type"], "Verified")
        self.assertEqual(A.patchsets[-1]["approvals"][0]["value"], "-1")

        self.assertEqual(len(B.patchsets[-1]["approvals"]), 1)
        self.assertEqual(B.patchsets[-1]["approvals"][0]["type"], "Verified")
        self.assertEqual(B.patchsets[-1]["approvals"][0]["value"], "-1")

        self.assertEqual(len(C.patchsets[-1]["approvals"]), 1)
        self.assertEqual(C.patchsets[-1]["approvals"][0]["type"], "Verified")
        self.assertEqual(C.patchsets[-1]["approvals"][0]["value"], "-1")

        A.addApproval("Code-Review", 2)
        B.addApproval("Code-Review", 2)
        C.addApproval("Code-Review", 2)
        D.addApproval("Code-Review", 2)

        self.fake_gerrit.addEvent(A.addApproval("Approved", 1))
        self.fake_gerrit.addEvent(B.addApproval("Approved", 1))
        self.fake_gerrit.addEvent(C.addApproval("Approved", 1))
        self.fake_gerrit.addEvent(D.addApproval("Approved", 1))
        self.waitUntilSettled()

        self.assertEqual(A.data["status"], "NEW")
        self.assertEqual(B.data["status"], "NEW")
        self.assertEqual(C.data["status"], "NEW")

        D.setMerged()
        for connection in self.scheds.first.connections.connections.values():
            connection.maintainCache([], max_age=0)

        # Pretend D was merged so we can gate the cycle
        self.fake_gerrit.addEvent(A.addApproval("Approved", 1))
        self.waitUntilSettled()

        self.assertEqual(A.reported, 3)
        self.assertEqual(B.reported, 3)
        self.assertEqual(C.reported, 3)
        self.assertEqual(A.data["status"], "MERGED")
        self.assertEqual(B.data["status"], "MERGED")
        self.assertEqual(C.data["status"], "MERGED")

    def test_cycle_unknown_repo(self):
        self.init_repo("org/unknown", tag='init')
        A = self.fake_gerrit.addFakeChange("org/project", "master", "A")
        B = self.fake_gerrit.addFakeChange("org/unknown", "master", "B")

        # A <-> B (via commit-depends)
        A.data["commitMessage"] = "{}\n\nDepends-On: {}\n".format(
            A.subject, B.data["url"]
        )
        B.data["commitMessage"] = "{}\n\nDepends-On: {}\n".format(
            B.subject, A.data["url"]
        )

        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        self.assertEqual(len(A.patchsets[-1]["approvals"]), 1)
        self.assertEqual(A.patchsets[-1]["approvals"][0]["type"], "Verified")
        self.assertEqual(A.patchsets[-1]["approvals"][0]["value"], "-1")

        for connection in self.scheds.first.connections.connections.values():
            connection.maintainCache([], max_age=0)

        A.addApproval("Code-Review", 2)
        B.addApproval("Code-Review", 2)
        B.addApproval("Approved", 1)
        self.fake_gerrit.addEvent(A.addApproval("Approved", 1))
        self.waitUntilSettled()

        self.assertEqual(A.reported, 1)
        self.assertEqual(A.data["status"], "NEW")
        self.assertEqual(B.data["status"], "NEW")

        for connection in self.scheds.first.connections.connections.values():
            connection.maintainCache([], max_age=0)

        B.setMerged()
        self.fake_gerrit.addEvent(A.addApproval("Approved", 1))
        self.waitUntilSettled()

        self.assertEqual(A.reported, 3)
        self.assertEqual(A.data["status"], "MERGED")

    def test_promote_cycle(self):
        self.executor_server.hold_jobs_in_build = True
        A = self.fake_gerrit.addFakeChange("org/project", "master", "A")
        B = self.fake_gerrit.addFakeChange("org/project1", "master", "B")
        C = self.fake_gerrit.addFakeChange("org/project2", "master", "C")

        # A <-> B
        A.data["commitMessage"] = "{}\n\nDepends-On: {}\n".format(
            A.subject, B.data["url"]
        )
        B.data["commitMessage"] = "{}\n\nDepends-On: {}\n".format(
            B.subject, A.data["url"]
        )

        A.addApproval("Code-Review", 2)
        B.addApproval("Code-Review", 2)
        C.addApproval("Code-Review", 2)
        B.addApproval("Approved", 1)
        self.fake_gerrit.addEvent(C.addApproval("Approved", 1))
        self.fake_gerrit.addEvent(A.addApproval("Approved", 1))
        self.waitUntilSettled()

        client = zuul.rpcclient.RPCClient("127.0.0.1",
                                          self.gearman_server.port)
        self.addCleanup(client.shutdown)
        client.promote(
            tenant="tenant-one",
            pipeline="gate",
            change_ids=["2,1"]
        )
        self.waitUntilSettled()

        self.assertEqual(len(self.builds), 4)
        self.assertTrue(self.builds[0].hasChanges(A))
        self.assertTrue(self.builds[0].hasChanges(B))
        self.assertFalse(self.builds[0].hasChanges(C))

        self.assertTrue(self.builds[1].hasChanges(A))
        self.assertTrue(self.builds[1].hasChanges(B))
        self.assertFalse(self.builds[0].hasChanges(C))

        self.assertTrue(self.builds[3].hasChanges(B))
        self.assertTrue(self.builds[3].hasChanges(C))
        self.assertTrue(self.builds[3].hasChanges(A))

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertEqual(A.reported, 2)
        self.assertEqual(B.reported, 2)
        self.assertEqual(C.reported, 2)
        self.assertEqual(A.data["status"], "MERGED")
        self.assertEqual(B.data["status"], "MERGED")
        self.assertEqual(C.data["status"], "MERGED")


class TestGithubCircularDependencies(ZuulTestCase):
    config_file = "zuul-gerrit-github.conf"
    tenant_config_file = "config/circular-dependencies/main.yaml"
    scheduler_count = 1

    def test_cycle_not_ready(self):
        A = self.fake_github.openFakePullRequest("gh/project", "master", "A")
        B = self.fake_github.openFakePullRequest("gh/project1", "master", "B")
        C = self.fake_github.openFakePullRequest("gh/project1", "master", "C")
        A.addReview('derp', 'APPROVED')
        B.addReview('derp', 'APPROVED')
        B.addLabel("approved")
        C.addReview('derp', 'APPROVED')

        # A -> B + C (via PR depends)
        # B -> A
        # C -> A
        A.body = "{}\n\nDepends-On: {}\nDepends-On: {}\n".format(
            A.subject, B.url, C.url
        )
        B.body = "{}\n\nDepends-On: {}\n".format(
            B.subject, A.url
        )
        C.body = "{}\n\nDepends-On: {}\n".format(
            C.subject, A.url
        )

        self.fake_github.emitEvent(A.addLabel("approved"))
        self.waitUntilSettled()

        self.assertEqual(len(A.comments), 0)
        self.assertEqual(len(B.comments), 0)
        self.assertEqual(len(C.comments), 0)
        self.assertFalse(A.is_merged)
        self.assertFalse(B.is_merged)
        self.assertFalse(C.is_merged)

    def test_complex_cycle_not_ready(self):
        A = self.fake_github.openFakePullRequest("gh/project", "master", "A")
        B = self.fake_github.openFakePullRequest("gh/project1", "master", "B")
        C = self.fake_github.openFakePullRequest("gh/project1", "master", "C")
        X = self.fake_github.openFakePullRequest("gh/project1", "master", "C")
        Y = self.fake_github.openFakePullRequest("gh/project1", "master", "C")
        A.addReview('derp', 'APPROVED')
        A.addLabel("approved")
        B.addReview('derp', 'APPROVED')
        B.addLabel("approved")
        C.addReview('derp', 'APPROVED')
        Y.addReview('derp', 'APPROVED')
        Y.addLabel("approved")
        X.addReview('derp', 'APPROVED')

        # A -> B + C (via PR depends)
        # B -> A
        # C -> A
        # X -> A + Y
        # Y -> X
        A.body = "{}\n\nDepends-On: {}\nDepends-On: {}\n".format(
            A.subject, B.url, C.url
        )
        B.body = "{}\n\nDepends-On: {}\n".format(
            B.subject, A.url
        )
        C.body = "{}\n\nDepends-On: {}\n".format(
            C.subject, A.url
        )
        X.body = "{}\n\nDepends-On: {}\nDepends-On: {}\n".format(
            X.subject, Y.url, A.url
        )
        Y.body = "{}\n\nDepends-On: {}\n".format(
            Y.subject, X.url
        )

        self.fake_github.emitEvent(X.addLabel("approved"))
        self.waitUntilSettled()

        self.assertEqual(len(A.comments), 0)
        self.assertEqual(len(B.comments), 0)
        self.assertEqual(len(C.comments), 0)
        self.assertEqual(len(X.comments), 0)
        self.assertEqual(len(Y.comments), 0)
        self.assertFalse(A.is_merged)
        self.assertFalse(B.is_merged)
        self.assertFalse(C.is_merged)
        self.assertFalse(X.is_merged)
        self.assertFalse(Y.is_merged)

    def test_filter_unprotected_branches(self):
        """
        Tests that repo state filtering due to excluding unprotected branches
        doesn't break builds if the items are targeted against different
        branches.
        """
        github = self.fake_github.getGithubClient()
        self.create_branch('gh/project', 'stable/foo')
        github.repo_from_project('gh/project')._set_branch_protection(
            'master', True)
        github.repo_from_project('gh/project')._set_branch_protection(
            'stable/foo', True)
        pevent = self.fake_github.getPushEvent(project='gh/project',
                                               ref='refs/heads/stable/foo')
        self.fake_github.emitEvent(pevent)

        self.create_branch('gh/project1', 'stable/bar')
        github.repo_from_project('gh/project1')._set_branch_protection(
            'master', True)
        github.repo_from_project('gh/project1')._set_branch_protection(
            'stable/bar', True)
        pevent = self.fake_github.getPushEvent(project='gh/project',
                                               ref='refs/heads/stable/bar')
        self.fake_github.emitEvent(pevent)

        # Wait until push events are processed to pick up branch
        # protection settings
        self.waitUntilSettled()

        A = self.fake_github.openFakePullRequest(
            "gh/project", "stable/foo", "A")
        B = self.fake_github.openFakePullRequest(
            "gh/project1", "stable/bar", "B")
        A.addReview('derp', 'APPROVED')
        B.addReview('derp', 'APPROVED')
        B.addLabel("approved")

        # A <-> B
        A.body = "{}\n\nDepends-On: {}\n".format(
            A.subject, B.url
        )
        B.body = "{}\n\nDepends-On: {}\n".format(
            B.subject, A.url
        )

        self.fake_github.emitEvent(A.addLabel("approved"))
        self.waitUntilSettled()

        self.assertEqual(len(A.comments), 2)
        self.assertEqual(len(B.comments), 2)
        self.assertTrue(A.is_merged)
        self.assertTrue(B.is_merged)

    def test_cycle_failed_reporting(self):
        self.executor_server.hold_jobs_in_build = True
        A = self.fake_github.openFakePullRequest("gh/project", "master", "A")
        B = self.fake_github.openFakePullRequest("gh/project1", "master", "B")
        A.addReview('derp', 'APPROVED')
        B.addReview('derp', 'APPROVED')
        B.addLabel("approved")

        # A <-> B
        A.body = "{}\n\nDepends-On: {}\n".format(
            A.subject, B.url
        )
        B.body = "{}\n\nDepends-On: {}\n".format(
            B.subject, A.url
        )

        self.fake_github.emitEvent(A.addLabel("approved"))
        self.waitUntilSettled()

        # Change draft status of A so it can no longer merge. Note that we
        # don't send an event to test the "github doesn't send an event"
        # case.
        A.draft = True
        self.waitUntilSettled()

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        self.assertEqual(len(A.comments), 2)
        self.assertEqual(len(B.comments), 2)
        self.assertFalse(A.is_merged)
        self.assertFalse(B.is_merged)
