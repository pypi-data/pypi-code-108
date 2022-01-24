# Copyright 2021 BMW Group
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

import random
import string
import threading

import testtools

from zuul import model
from zuul.driver import Driver, TriggerInterface
from zuul.lib.connections import ConnectionRegistry
from zuul.zk import ZooKeeperClient, event_queues, sharding

from tests.base import BaseTestCase, iterate_timeout


class EventQueueBaseTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.setupZK()

        self.zk_client = ZooKeeperClient(
            self.zk_chroot_fixture.zk_hosts,
            tls_cert=self.zk_chroot_fixture.zookeeper_cert,
            tls_key=self.zk_chroot_fixture.zookeeper_key,
            tls_ca=self.zk_chroot_fixture.zookeeper_ca
        )
        self.addCleanup(self.zk_client.disconnect)
        self.zk_client.connect()

        self.connections = ConnectionRegistry()
        self.addCleanup(self.connections.stop)


class DummyEvent(model.AbstractEvent):

    def toDict(self):
        return {}

    def updateFromDict(self):
        pass

    @classmethod
    def fromDict(cls, d):
        return cls()


class DummyEventQueue(event_queues.ZooKeeperEventQueue):

    def put(self, event):
        self._put(event.toDict())

    def __iter__(self):
        for data, ack_ref, _ in self._iterEvents():
            event = DummyEvent.fromDict(data)
            event.ack_ref = ack_ref
            yield event


class TestEventQueue(EventQueueBaseTestCase):

    def setUp(self):
        super().setUp()
        self.queue = DummyEventQueue(self.zk_client, "root")

    def test_missing_ack_ref(self):
        # Every event from a ZK event queue should have an ack_ref
        # attached to it when it is deserialized; ensure that an error
        # is raised if we try to ack an event without one.
        with testtools.ExpectedException(RuntimeError):
            self.queue.ack(DummyEvent())

    def test_double_ack(self):
        # Test that if we ack an event twice, an exception isn't
        # raised.
        self.queue.put(DummyEvent())
        self.assertEqual(len(self.queue), 1)

        event = next(iter(self.queue))
        self.queue.ack(event)
        self.assertEqual(len(self.queue), 0)

        # Should not raise an exception
        self.queue.ack(event)

    def test_invalid_json_ignored(self):
        # Test that invalid json is automatically removed.
        event_path = self.queue._put({})
        self.zk_client.client.set(event_path, b"{ invalid")

        self.assertEqual(len(self.queue), 1)
        self.assertEqual(list(self.queue._iterEvents()), [])
        self.assertEqual(len(self.queue), 0)


class DummyTriggerEvent(model.TriggerEvent):
    pass


class DummyDriver(Driver, TriggerInterface):
    name = driver_name = "dummy"

    def getTrigger(self, connection, config=None):
        pass

    def getTriggerSchema(self):
        pass

    def getTriggerEventClass(self):
        return DummyTriggerEvent


class TestTriggerEventQueue(EventQueueBaseTestCase):

    def setUp(self):
        super().setUp()
        self.driver = DummyDriver()
        self.connections.registerDriver(self.driver)

    def test_sharded_tenant_trigger_events(self):
        # Test enqueue/dequeue of the tenant trigger event queue.
        queue = event_queues.TenantTriggerEventQueue(
            self.zk_client, self.connections, "tenant"
        )

        self.assertEqual(len(queue), 0)
        self.assertFalse(queue.hasEvents())

        event = DummyTriggerEvent()
        data = {'test': ''.join(
            random.choice(string.ascii_letters + string.digits)
            for x in range(sharding.NODE_BYTE_SIZE_LIMIT * 2))}
        event.data = data

        queue.put(self.driver.driver_name, event)
        queue.put(self.driver.driver_name, event)

        self.assertEqual(len(queue), 2)
        self.assertTrue(queue.hasEvents())

        processed = 0
        for event in queue:
            self.assertIsInstance(event, DummyTriggerEvent)
            processed += 1

        self.assertEqual(processed, 2)
        self.assertEqual(len(queue), 2)
        self.assertTrue(queue.hasEvents())

        acked = 0
        for event in queue:
            queue.ack(event)
            self.assertEqual(event.data, data)
            acked += 1

        self.assertEqual(acked, 2)
        self.assertEqual(len(queue), 0)
        self.assertFalse(queue.hasEvents())

    def test_lost_sharded_tenant_trigger_events(self):
        # Test cleanup when we write out side-channel data but not an
        # event.
        queue = event_queues.TenantTriggerEventQueue(
            self.zk_client, self.connections, "tenant"
        )

        self.assertEqual(len(queue), 0)
        self.assertFalse(queue.hasEvents())

        event = DummyTriggerEvent()
        data = {'test': ''.join(
            random.choice(string.ascii_letters + string.digits)
            for x in range(sharding.NODE_BYTE_SIZE_LIMIT * 2))}
        event.data = data

        queue.put(self.driver.driver_name, event)
        queue.put(self.driver.driver_name, event)

        self.assertEqual(len(queue), 2)
        self.assertTrue(queue.hasEvents())

        # Delete the first event (but not its sharded data)
        events = list(queue)
        self.zk_client.client.delete(events[0].ack_ref.path)
        # There should still be 2 data nodes
        self.assertEqual(len(
            self.zk_client.client.get_children(queue.data_root)), 2)

        # Clean up lost data
        queue.cleanup(age=0)
        # There should only be one data node remaining
        self.assertEqual(len(
            self.zk_client.client.get_children(queue.data_root)), 1)

        # Ack the second event
        queue.ack(events[1])

        # Assert there are no side channel data nodes
        self.assertEqual(len(
            self.zk_client.client.get_children(queue.data_root)), 0)

    def test_tenant_trigger_events(self):
        # Test enqueue/dequeue of the tenant trigger event queue.
        queue = event_queues.TenantTriggerEventQueue(
            self.zk_client, self.connections, "tenant"
        )

        self.assertEqual(len(queue), 0)
        self.assertFalse(queue.hasEvents())

        event = DummyTriggerEvent()
        queue.put(self.driver.driver_name, event)
        queue.put(self.driver.driver_name, event)

        self.assertEqual(len(queue), 2)
        self.assertTrue(queue.hasEvents())

        processed = 0
        for event in queue:
            self.assertIsInstance(event, DummyTriggerEvent)
            processed += 1

        self.assertEqual(processed, 2)
        self.assertEqual(len(queue), 2)
        self.assertTrue(queue.hasEvents())

        acked = 0
        for event in queue:
            queue.ack(event)
            acked += 1

        self.assertEqual(acked, 2)
        self.assertEqual(len(queue), 0)
        self.assertFalse(queue.hasEvents())

    def test_pipeline_trigger_events(self):
        # Test enqueue/dequeue of pipeline-specific trigger event
        # queues.
        registry = event_queues.PipelineTriggerEventQueue.createRegistry(
            self.zk_client, self.connections
        )

        queue = registry["tenant"]["pipeline"]
        self.assertIsInstance(queue, event_queues.TriggerEventQueue)

        self.assertEqual(len(queue), 0)
        self.assertFalse(queue.hasEvents())

        event = DummyTriggerEvent()
        queue.put(self.driver.driver_name, event)

        self.assertEqual(len(queue), 1)
        self.assertTrue(queue.hasEvents())

        other_queue = registry["other_tenant"]["pipeline"]
        self.assertEqual(len(other_queue), 0)
        self.assertFalse(other_queue.hasEvents())

        acked = 0
        for event in queue:
            self.assertIsInstance(event, DummyTriggerEvent)
            queue.ack(event)
            acked += 1

        self.assertEqual(acked, 1)
        self.assertEqual(len(queue), 0)
        self.assertFalse(queue.hasEvents())


class TestManagementEventQueue(EventQueueBaseTestCase):

    def test_management_events(self):
        # Test enqueue/dequeue of the tenant management event queue.
        queue = event_queues.TenantManagementEventQueue(
            self.zk_client, "tenant")

        self.assertEqual(len(queue), 0)
        self.assertFalse(queue.hasEvents())

        event = model.ReconfigureEvent()
        result_future = queue.put(event, needs_result=False)
        self.assertIsNone(result_future)

        result_future = queue.put(event)
        self.assertIsNotNone(result_future)

        self.assertEqual(len(queue), 2)
        self.assertTrue(queue.hasEvents())
        self.assertFalse(result_future.wait(0.1))

        acked = 0
        for event in queue:
            self.assertIsInstance(event, model.ReconfigureEvent)
            queue.ack(event)
            acked += 1

        self.assertEqual(acked, 2)
        self.assertTrue(result_future.wait(5))
        self.assertEqual(len(queue), 0)
        self.assertFalse(queue.hasEvents())

    def test_management_event_error(self):
        # Test that management event errors are reported.
        queue = event_queues.TenantManagementEventQueue(
            self.zk_client, "tenant")
        event = model.ReconfigureEvent()
        result_future = queue.put(event)

        acked = 0
        for event in queue:
            event.traceback = "hello traceback"
            queue.ack(event)
            acked += 1

        self.assertEqual(acked, 1)
        with testtools.ExpectedException(RuntimeError, msg="hello traceback"):
            self.assertFalse(result_future.wait(5))

    def test_event_merge(self):
        # Test that similar management events (eg, reconfiguration of
        # two projects) can be merged.
        queue = event_queues.TenantManagementEventQueue(
            self.zk_client, "tenant")
        event = model.TenantReconfigureEvent("tenant", "project", "master")
        queue.put(event, needs_result=False)
        event = model.TenantReconfigureEvent("tenant", "other", "branch")
        queue.put(event, needs_result=False)

        self.assertEqual(len(queue), 2)
        events = list(queue)

        self.assertEqual(len(events), 1)
        event = events[0]
        self.assertEqual(len(event.merged_events), 1)
        self.assertEqual(
            event.project_branches,
            set([("project", "master"), ("other", "branch")])
        )

        queue.ack(event)
        self.assertFalse(queue.hasEvents())

    def test_event_ltime(self):
        tenant_queue = event_queues.TenantManagementEventQueue(
            self.zk_client, "tenant")
        registry = event_queues.PipelineManagementEventQueue.createRegistry(
            self.zk_client
        )

        event = model.ReconfigureEvent()
        tenant_queue.put(event, needs_result=False)
        self.assertTrue(tenant_queue.hasEvents())

        pipeline_queue = registry["tenant"]["pipeline"]
        self.assertIsInstance(
            pipeline_queue, event_queues.ManagementEventQueue
        )
        processed_events = 0
        for event in tenant_queue:
            processed_events += 1
            event_ltime = event.zuul_event_ltime
            self.assertGreater(event_ltime, -1)
            # Forward event to pipeline management event queue
            pipeline_queue.put(event)

        self.assertEqual(processed_events, 1)
        self.assertTrue(pipeline_queue.hasEvents())

        processed_events = 0
        for event in pipeline_queue:
            pipeline_queue.ack(event)
            processed_events += 1
            self.assertEqual(event.zuul_event_ltime, event_ltime)

        self.assertEqual(processed_events, 1)

    def test_pipeline_management_events(self):
        # Test that when a management event is forwarded from the
        # tenant to the a pipeline-specific queue, it is not
        # prematurely acked and the future returns correctly.
        tenant_queue = event_queues.TenantManagementEventQueue(
            self.zk_client, "tenant")
        registry = event_queues.PipelineManagementEventQueue.createRegistry(
            self.zk_client
        )

        event = model.PromoteEvent('tenant', 'check', ['1234,1'])
        result_future = tenant_queue.put(event, needs_result=False)
        self.assertIsNone(result_future)

        result_future = tenant_queue.put(event)
        self.assertIsNotNone(result_future)

        self.assertEqual(len(tenant_queue), 2)
        self.assertTrue(tenant_queue.hasEvents())

        pipeline_queue = registry["tenant"]["pipeline"]
        self.assertIsInstance(
            pipeline_queue, event_queues.ManagementEventQueue
        )
        acked = 0
        for event in tenant_queue:
            self.assertIsInstance(event, model.PromoteEvent)
            # Forward event to pipeline management event queue
            pipeline_queue.put(event)
            tenant_queue.ackWithoutResult(event)
            acked += 1

        self.assertEqual(acked, 2)
        # Event was just forwarded and since we expect a result, the
        # future should not be completed yet.
        self.assertFalse(result_future.wait(0.1))

        self.assertEqual(len(tenant_queue), 0)
        self.assertFalse(tenant_queue.hasEvents())

        self.assertEqual(len(pipeline_queue), 2)
        self.assertTrue(pipeline_queue.hasEvents())

        acked = 0
        for event in pipeline_queue:
            self.assertIsInstance(event, model.PromoteEvent)
            pipeline_queue.ack(event)
            acked += 1

        self.assertEqual(acked, 2)
        self.assertTrue(result_future.wait(5))
        self.assertEqual(len(pipeline_queue), 0)
        self.assertFalse(pipeline_queue.hasEvents())

    def test_management_events_client(self):
        # Test management events from a second client

        queue = event_queues.TenantManagementEventQueue(
            self.zk_client, "tenant")
        self.assertEqual(len(queue), 0)
        self.assertFalse(queue.hasEvents())

        # This client will submit a reconfigure event and wait for it.
        external_client = ZooKeeperClient(
            self.zk_chroot_fixture.zk_hosts,
            tls_cert=self.zk_chroot_fixture.zookeeper_cert,
            tls_key=self.zk_chroot_fixture.zookeeper_key,
            tls_ca=self.zk_chroot_fixture.zookeeper_ca)
        self.addCleanup(external_client.disconnect)
        external_client.connect()

        external_queue = event_queues.TenantManagementEventQueue(
            external_client, "tenant")

        event = model.ReconfigureEvent()
        result_future = external_queue.put(event)
        self.assertIsNotNone(result_future)

        self.assertEqual(len(queue), 1)
        self.assertTrue(queue.hasEvents())
        self.assertFalse(result_future.wait(0.1))

        acked = 0
        for event in queue:
            self.assertIsInstance(event, model.ReconfigureEvent)
            queue.ack(event)
            acked += 1

        self.assertEqual(acked, 1)
        self.assertTrue(result_future.wait(5))
        self.assertEqual(len(queue), 0)
        self.assertFalse(queue.hasEvents())

    def test_management_events_client_disconnect(self):
        # Test management events from a second client which
        # disconnects before the event is complete.

        queue = event_queues.TenantManagementEventQueue(
            self.zk_client, "tenant")
        self.assertEqual(len(queue), 0)
        self.assertFalse(queue.hasEvents())

        # This client will submit a reconfigure event and disconnect
        # before it's complete.
        external_client = ZooKeeperClient(
            self.zk_chroot_fixture.zk_hosts,
            tls_cert=self.zk_chroot_fixture.zookeeper_cert,
            tls_key=self.zk_chroot_fixture.zookeeper_key,
            tls_ca=self.zk_chroot_fixture.zookeeper_ca)
        self.addCleanup(external_client.disconnect)
        external_client.connect()

        external_queue = event_queues.TenantManagementEventQueue(
            external_client, "tenant")

        # Submit the event
        event = model.ReconfigureEvent()
        result_future = external_queue.put(event)
        self.assertIsNotNone(result_future)

        # Make sure the event is in the queue and the result node exists
        self.assertEqual(len(queue), 1)
        self.assertTrue(queue.hasEvents())
        self.assertFalse(result_future.wait(0.1))
        self.assertEqual(len(
            self.zk_client.client.get_children('/zuul/results/management')), 1)

        # Disconnect the originating client
        external_client.disconnect()
        # Ensure the result node is gone
        self.assertEqual(len(
            self.zk_client.client.get_children('/zuul/results/management')), 0)

        # Process the event
        acked = 0
        for event in queue:
            self.assertIsInstance(event, model.ReconfigureEvent)
            queue.ack(event)
            acked += 1

        # Make sure the event has been processed and we didn't
        # re-create the result node.
        self.assertEqual(acked, 1)
        self.assertEqual(len(queue), 0)
        self.assertFalse(queue.hasEvents())
        self.assertEqual(len(
            self.zk_client.client.get_children('/zuul/results/management')), 0)


class TestResultEventQueue(EventQueueBaseTestCase):

    def test_pipeline_result_events(self):
        # Test enqueue/dequeue of result events.
        registry = event_queues.PipelineResultEventQueue.createRegistry(
            self.zk_client
        )

        queue = registry["tenant"]["pipeline"]
        self.assertIsInstance(queue, event_queues.PipelineResultEventQueue)

        self.assertEqual(len(queue), 0)
        self.assertFalse(queue.hasEvents())

        event = model.BuildStartedEvent(
            "build", "buildset", "job", "build_request_path", {})
        queue.put(event)

        self.assertEqual(len(queue), 1)
        self.assertTrue(queue.hasEvents())

        other_queue = registry["other_tenant"]["pipeline"]
        self.assertEqual(len(other_queue), 0)
        self.assertFalse(other_queue.hasEvents())

        acked = 0
        for event in queue:
            self.assertIsInstance(event, model.BuildStartedEvent)
            queue.ack(event)
            acked += 1

        self.assertEqual(acked, 1)
        self.assertEqual(len(queue), 0)
        self.assertFalse(queue.hasEvents())


class TestEventWatchers(EventQueueBaseTestCase):

    def setUp(self):
        super().setUp()
        self.driver = DummyDriver()
        self.connections.registerDriver(self.driver)

    def _wait_for_event(self, event):
        for _ in iterate_timeout(5, "event set"):
            if event.is_set():
                break

    def test_tenant_event_watcher(self):
        event = threading.Event()
        event_queues.EventWatcher(self.zk_client, event.set)

        management_queue = (
            event_queues.TenantManagementEventQueue.createRegistry(
                self.zk_client)
        )
        trigger_queue = event_queues.TenantTriggerEventQueue.createRegistry(
            self.zk_client, self.connections
        )
        self.assertFalse(event.is_set())

        management_queue["tenant"].put(model.ReconfigureEvent(),
                                       needs_result=False)
        self._wait_for_event(event)
        event.clear()

        trigger_queue["tenant"].put(self.driver.driver_name,
                                    DummyTriggerEvent())
        self._wait_for_event(event)

    def test_pipeline_event_watcher(self):
        event = threading.Event()
        event_queues.EventWatcher(self.zk_client, event.set)

        management_queues = (
            event_queues.PipelineManagementEventQueue.createRegistry(
                self.zk_client
            )
        )
        trigger_queues = event_queues.PipelineTriggerEventQueue.createRegistry(
            self.zk_client, self.connections
        )
        result_queues = event_queues.PipelineResultEventQueue.createRegistry(
            self.zk_client
        )
        self.assertFalse(event.is_set())

        management_queues["tenant"]["check"].put(model.ReconfigureEvent())
        self._wait_for_event(event)
        event.clear()

        trigger_queues["tenant"]["gate"].put(self.driver.driver_name,
                                             DummyTriggerEvent())
        self._wait_for_event(event)
        event.clear()

        result_event = model.BuildStartedEvent(
            "build", "buildset", "job", "build_request_path", {})
        result_queues["other-tenant"]["post"].put(result_event)
        self._wait_for_event(event)


class TestConnectionEventQueue(EventQueueBaseTestCase):

    def test_connection_events(self):
        # Test enqueue/dequeue of the connection event queue.
        queue = event_queues.ConnectionEventQueue(self.zk_client, "dummy")

        self.assertEqual(len(queue), 0)
        self.assertFalse(queue.hasEvents())

        payload = {"message": "hello world!"}
        queue.put(payload)
        queue.put(payload)

        self.assertEqual(len(queue), 2)
        self.assertTrue(queue.hasEvents())

        acked = 0
        for event in queue:
            self.assertIsInstance(event, model.ConnectionEvent)
            self.assertEqual(event, payload)
            queue.ack(event)
            acked += 1

        self.assertEqual(acked, 2)
        self.assertEqual(len(queue), 0)
        self.assertFalse(queue.hasEvents())

    def test_event_watch(self):
        # Test the registered function is called on new events.
        queue = event_queues.ConnectionEventQueue(self.zk_client, "dummy")

        event = threading.Event()
        queue.registerEventWatch(event.set)
        self.assertFalse(event.is_set())

        queue.put({"message": "hello world!"})
        for _ in iterate_timeout(5, "event set"):
            if event.is_set():
                break
