# Copyright 2021 BMW Group
# Copyright 2021 Acme Gating, LLC
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

import zuul.model

from tests.base import iterate_timeout, ZuulTestCase, simple_layout
from zuul.zk.locks import SessionAwareWriteLock, TENANT_LOCK_ROOT


class TestScaleOutScheduler(ZuulTestCase):
    tenant_config_file = "config/single-tenant/main.yaml"
    # Those tests are testing specific interactions between multiple
    # schedulers. They create additional schedulers as necessary and
    # start or stop them individually to test specific interactions.
    # Using the scheduler_count in addition to create even more
    # schedulers doesn't make sense for those tests.
    scheduler_count = 1

    def test_multi_scheduler(self):
        # A smoke test that we can enqueue a change with one scheduler
        # and have another one finish the run.
        self.executor_server.hold_jobs_in_build = True

        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        A.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.waitUntilSettled()

        app = self.createScheduler()
        app.start()
        self.assertEqual(len(self.scheds), 2)

        # Hold the lock on the first scheduler so that only the second
        # will act.
        with self.scheds.first.sched.run_handler_lock:
            self.executor_server.hold_jobs_in_build = False
            self.executor_server.release()
            self.waitUntilSettled(matcher=[app])

        self.assertHistory([
            dict(name='project-merge', result='SUCCESS', changes='1,1'),
            dict(name='project-test1', result='SUCCESS', changes='1,1'),
            dict(name='project-test2', result='SUCCESS', changes='1,1'),
        ], ordered=False)

    def test_config_priming(self):
        # Wait until scheduler is primed
        self.waitUntilSettled()
        first_app = self.scheds.first
        initial_max_hold_exp = first_app.sched.globals.max_hold_expiration
        layout_state = first_app.sched.tenant_layout_state.get("tenant-one")
        self.assertIsNotNone(layout_state)

        # Second scheduler instance
        second_app = self.createScheduler()
        # Change a system attribute in order to check that the system config
        # from Zookeeper was used.
        second_app.sched.globals.max_hold_expiration += 1234
        second_app.config.set("scheduler", "max_hold_expiration", str(
            second_app.sched.globals.max_hold_expiration))

        second_app.start()
        self.waitUntilSettled()

        self.assertEqual(first_app.sched.local_layout_state.get("tenant-one"),
                         second_app.sched.local_layout_state.get("tenant-one"))

        # Make sure only the first schedulers issued cat jobs
        self.assertIsNotNone(
            first_app.sched.merger.merger_api.history.get("cat"))
        self.assertIsNone(
            second_app.sched.merger.merger_api.history.get("cat"))

        for _ in iterate_timeout(
                10, "Wait for all schedulers to have the same system config"):
            if (first_app.sched.unparsed_abide.ltime
                    == second_app.sched.unparsed_abide.ltime):
                break

        # TODO (swestphahl): change this to assertEqual() when we remove
        # the smart reconfiguration during config priming.
        # Currently the smart reconfiguration during priming of the second
        # scheduler will update the system config in Zookeeper and the first
        # scheduler updates it's config in return.
        self.assertNotEqual(second_app.sched.globals.max_hold_expiration,
                            initial_max_hold_exp)

    def test_reconfigure(self):
        # Create a second scheduler instance
        app = self.createScheduler()
        app.start()
        self.assertEqual(len(self.scheds), 2)

        for _ in iterate_timeout(10, "Wait until priming is complete"):
            old = self.scheds.first.sched.tenant_layout_state.get("tenant-one")
            if old is not None:
                break

        for _ in iterate_timeout(
                10, "Wait for all schedulers to have the same layout state"):
            layout_states = [a.sched.local_layout_state.get("tenant-one")
                             for a in self.scheds.instances]
            if all(l == old for l in layout_states):
                break

        self.scheds.first.sched.reconfigure(self.scheds.first.config)
        self.waitUntilSettled()

        new = self.scheds.first.sched.tenant_layout_state["tenant-one"]
        self.assertNotEqual(old, new)

        for _ in iterate_timeout(10, "Wait for all schedulers to update"):
            layout_states = [a.sched.local_layout_state.get("tenant-one")
                             for a in self.scheds.instances]
            if all(l == new for l in layout_states):
                break

        layout_uuids = [a.sched.abide.tenants["tenant-one"].layout.uuid
                        for a in self.scheds.instances]
        self.assertTrue(all(l == new.uuid for l in layout_uuids))
        self.waitUntilSettled()

    def test_change_cache(self):
        # Test re-using a change from the change cache.
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'B')

        B.setDependsOn(A, 1)

        self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()
        # This has populated the change cache with our change.

        app = self.createScheduler()
        app.start()
        self.assertEqual(len(self.scheds), 2)

        # Hold the lock on the first scheduler so that only the second
        # will act.
        with self.scheds.first.sched.run_handler_lock:
            # Enqueue the change again.  The second scheduler will
            # load the change object from the cache.
            self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(1))

            self.waitUntilSettled(matcher=[app])

        # Each job should appear twice and contain both changes.
        self.assertHistory([
            dict(name='project-merge', result='SUCCESS', changes='1,1 2,1'),
            dict(name='project-test1', result='SUCCESS', changes='1,1 2,1'),
            dict(name='project-test2', result='SUCCESS', changes='1,1 2,1'),
            dict(name='project-merge', result='SUCCESS', changes='1,1 2,1'),
            dict(name='project-test1', result='SUCCESS', changes='1,1 2,1'),
            dict(name='project-test2', result='SUCCESS', changes='1,1 2,1'),
        ], ordered=False)

    def test_pipeline_summary(self):
        # Test that we can deal with a truncated pipeline summary
        self.executor_server.hold_jobs_in_build = True
        tenant = self.scheds.first.sched.abide.tenants.get('tenant-one')
        pipeline = tenant.layout.pipelines['check']
        context = self.createZKContext()

        def new_summary():
            summary = zuul.model.PipelineSummary()
            summary._set(pipeline=pipeline)
            summary.refresh(context)
            return summary

        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()

        # Check we have a good summary
        summary1 = new_summary()
        self.assertNotEqual(summary1.status, {})
        self.assertTrue(context.client.exists(summary1.getPath()))

        # Make a syntax error in the status summary json
        summary = new_summary()
        summary._save(context, b'{"foo')

        # With the corrupt data, we should get an empty status but the
        # path should still exist.
        summary2 = new_summary()
        self.assertEqual(summary2.status, {})
        self.assertTrue(context.client.exists(summary2.getPath()))

        # Our earlier summary object should use its cached data
        summary1.refresh(context)
        self.assertNotEqual(summary1.status, {})

        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.waitUntilSettled()

        # The scheduler should have written a new summary that our
        # second object can read now.
        summary2.refresh(context)
        self.assertNotEqual(summary2.status, {})

    @simple_layout('layouts/semaphore.yaml')
    def test_semaphore(self):
        self.executor_server.hold_jobs_in_build = True
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()
        self.assertEqual(len(self.builds), 1)
        self.assertEqual(self.builds[0].name, 'test1')
        self.assertHistory([])

        tenant = self.scheds.first.sched.abide.tenants['tenant-one']
        semaphore = tenant.semaphore_handler.getSemaphores()[0]
        holders = tenant.semaphore_handler.semaphoreHolders(semaphore)
        self.assertEqual(len(holders), 1)

        # Start a second scheduler so that it runs through the initial
        # cleanup processes.
        app = self.createScheduler()
        # Hold the lock on the second scheduler so that if any events
        # happen, they are processed by the first scheduler (this lets
        # them be as out of sync as possible).
        with app.sched.run_handler_lock:
            app.start()
            self.assertEqual(len(self.scheds), 2)
            self.waitUntilSettled(matcher=[self.scheds.first])
            # Wait until initial cleanup is run
            app.sched.start_cleanup_thread.join()
            # We should not have released the semaphore
            holders = tenant.semaphore_handler.semaphoreHolders(semaphore)
            self.assertEqual(len(holders), 1)

        self.executor_server.release()
        self.waitUntilSettled()
        self.assertEqual(len(self.builds), 1)
        self.assertEqual(self.builds[0].name, 'test2')
        self.assertHistory([
            dict(name='test1', result='SUCCESS', changes='1,1'),
        ], ordered=False)
        holders = tenant.semaphore_handler.semaphoreHolders(semaphore)
        self.assertEqual(len(holders), 1)

        self.executor_server.release()
        self.waitUntilSettled()
        self.assertEqual(len(self.builds), 0)
        self.assertHistory([
            dict(name='test1', result='SUCCESS', changes='1,1'),
            dict(name='test2', result='SUCCESS', changes='1,1'),
        ], ordered=False)

        holders = tenant.semaphore_handler.semaphoreHolders(semaphore)
        self.assertEqual(len(holders), 0)


class TestSOSCircularDependencies(ZuulTestCase):
    # Those tests are testing specific interactions between multiple
    # schedulers. They create additional schedulers as necessary and
    # start or stop them individually to test specific interactions.
    # Using the scheduler_count in addition to create even more
    # schedulers doesn't make sense for those tests.
    scheduler_count = 1

    @simple_layout('layouts/sos-circular.yaml')
    def test_sos_circular_deps(self):
        # This test sets the window to 1 so that we can test a code
        # path where we write the queue items to ZK as little as
        # possible on the first scheduler while doing most of the work
        # on the second.
        self.executor_server.hold_jobs_in_build = True
        Z = self.fake_gerrit.addFakeChange('org/project', "master", "Z")
        A = self.fake_gerrit.addFakeChange('org/project', "master", "A")
        B = self.fake_gerrit.addFakeChange('org/project', "master", "B")

        # Z, A <-> B (via commit-depends)
        A.data["commitMessage"] = "{}\n\nDepends-On: {}\n".format(
            A.subject, B.data["url"]
        )
        B.data["commitMessage"] = "{}\n\nDepends-On: {}\n".format(
            B.subject, A.data["url"]
        )
        Z.addApproval("Code-Review", 2)
        self.fake_gerrit.addEvent(Z.addApproval("Approved", 1))
        self.waitUntilSettled()
        A.addApproval("Code-Review", 2)
        B.addApproval("Code-Review", 2)
        A.addApproval("Approved", 1)
        self.fake_gerrit.addEvent(B.addApproval("Approved", 1))
        self.waitUntilSettled()

        # Start a second scheduler
        app = self.createScheduler()
        app.start()
        self.assertEqual(len(self.scheds), 2)
        self.waitUntilSettled()

        # Hold the lock on the first scheduler so that only the second
        # will act.
        with self.scheds.first.sched.run_handler_lock:
            # Release the first item so the second moves into the
            # active window.
            self.assertEqual(len(self.builds), 2)
            builds = self.builds[:]
            builds[0].release()
            builds[1].release()
            self.waitUntilSettled(matcher=[app])
            self.assertEqual(len(self.builds), 4)
            builds = self.builds[:]
            self.executor_server.failJob('job1', A)
            builds[0].release()
            app.sched.wake_event.set()
            self.waitUntilSettled(matcher=[app])
            self.assertEqual(A.reported, 2)
            self.assertEqual(B.reported, 2)


class TestScaleOutSchedulerMultiTenant(ZuulTestCase):
    # Those tests are testing specific interactions between multiple
    # schedulers. They create additional schedulers as necessary and
    # start or stop them individually to test specific interactions.
    # Using the scheduler_count in addition to create even more
    # schedulers doesn't make sense for those tests.
    scheduler_count = 1
    tenant_config_file = "config/two-tenant/main.yaml"

    def test_background_layout_update(self):
        # This test performs a reconfiguration on one scheduler and
        # verifies that a second scheduler begins processing changes
        # for each tenant as it is updated.

        first = self.scheds.first
        # Create a second scheduler instance
        second = self.createScheduler()
        second.start()
        self.assertEqual(len(self.scheds), 2)
        tenant_one_lock = SessionAwareWriteLock(
            self.zk_client.client,
            f"{TENANT_LOCK_ROOT}/tenant-one")

        A = self.fake_gerrit.addFakeChange('org/project1', 'master', 'A')
        B = self.fake_gerrit.addFakeChange('org/project2', 'master', 'B')

        for _ in iterate_timeout(10, "until priming is complete"):
            state_one = first.sched.local_layout_state.get("tenant-one")
            state_two = first.sched.local_layout_state.get("tenant-two")
            if all([state_one, state_two]):
                break

        for _ in iterate_timeout(
                10, "all schedulers to have the same layout state"):
            if (second.sched.local_layout_state.get(
                    "tenant-one") == state_one and
                second.sched.local_layout_state.get(
                    "tenant-two") == state_two):
                break

        self.log.debug("Freeze scheduler-1")
        with second.sched.layout_update_lock:
            state_one = first.sched.local_layout_state.get("tenant-one")
            state_two = first.sched.local_layout_state.get("tenant-two")
            self.log.debug("Reconfigure scheduler-0")
            first.sched.reconfigure(first.config)
            for _ in iterate_timeout(
                    10, "tenants to be updated on scheduler-0"):
                if ((first.sched.local_layout_state["tenant-one"] !=
                     state_one) and
                    (first.sched.local_layout_state["tenant-two"] !=
                     state_two)):
                    break
            self.waitUntilSettled(matcher=[first])
            self.log.debug("Grab tenant-one write lock")
            tenant_one_lock.acquire(blocking=True)

        self.log.debug("Thaw scheduler-1")
        self.log.debug("Freeze scheduler-0")
        with first.sched.run_handler_lock:
            self.log.debug("Open change in tenant-one")
            self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))

            for _ in iterate_timeout(10, "trigger event appears"):
                if second.sched.trigger_events['tenant-one'].hasEvents():
                    break

            for _ in iterate_timeout(
                    10, "tenant-two to be updated on scheduler-1"):
                if (first.sched.local_layout_state["tenant-two"] ==
                    second.sched.local_layout_state.get("tenant-two")):
                    break
            # Tenant two should be up to date, but tenant one should
            # still be out of date on scheduler two.
            self.assertEqual(first.sched.local_layout_state["tenant-two"],
                             second.sched.local_layout_state["tenant-two"])
            self.assertNotEqual(first.sched.local_layout_state["tenant-one"],
                                second.sched.local_layout_state["tenant-one"])
            self.log.debug("Verify tenant-one change is unprocessed")
            # If we have updated tenant-two's configuration without
            # processing the tenant-one change, then we know we've
            # completed at least one run loop.
            self.assertHistory([])

            self.log.debug("Open change in tenant-two")
            self.fake_gerrit.addEvent(B.getPatchsetCreatedEvent(1))
            self.log.debug("Wait for scheduler-1 to process tenant-two change")
            for _ in iterate_timeout(10, "tenant-two build finish"):
                if len(self.history):
                    break

            self.assertHistory([
                dict(name='test', result='SUCCESS', changes='2,1'),
            ], ordered=False)

            # Tenant two should be up to date, but tenant one should
            # still be out of date on scheduler two.
            self.assertEqual(first.sched.local_layout_state["tenant-two"],
                             second.sched.local_layout_state["tenant-two"])
            self.assertNotEqual(first.sched.local_layout_state["tenant-one"],
                                second.sched.local_layout_state["tenant-one"])

            self.log.debug("Release tenant-one write lock")
            tenant_one_lock.release()

            self.log.debug("Wait for both changes to be processed")
            self.waitUntilSettled(matcher=[second])
            self.assertHistory([
                dict(name='test', result='SUCCESS', changes='2,1'),
                dict(name='test', result='SUCCESS', changes='1,1'),
            ], ordered=False)

            # Both tenants should be up to date
            self.assertEqual(first.sched.local_layout_state["tenant-two"],
                             second.sched.local_layout_state["tenant-two"])
            self.assertEqual(first.sched.local_layout_state["tenant-one"],
                             second.sched.local_layout_state["tenant-one"])
        self.waitUntilSettled()
