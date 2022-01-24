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

import enum
import functools
import json
import logging
import threading
import time
import uuid
from collections import namedtuple
from collections.abc import Iterable
from contextlib import suppress

from kazoo.exceptions import NoNodeError
from kazoo.protocol.states import EventType

from zuul import model
from zuul.lib.collections import DefaultKeyDict
from zuul.zk import ZooKeeperSimpleBase, sharding
from zuul.zk.election import SessionAwareElection

RESULT_EVENT_TYPE_MAP = {
    "BuildCompletedEvent": model.BuildCompletedEvent,
    "BuildPausedEvent": model.BuildPausedEvent,
    "BuildStartedEvent": model.BuildStartedEvent,
    "BuildStatusEvent": model.BuildStatusEvent,
    "FilesChangesCompletedEvent": model.FilesChangesCompletedEvent,
    "MergeCompletedEvent": model.MergeCompletedEvent,
    "NodesProvisionedEvent": model.NodesProvisionedEvent,
}

MANAGEMENT_EVENT_TYPE_MAP = {
    "DequeueEvent": model.DequeueEvent,
    "EnqueueEvent": model.EnqueueEvent,
    "PromoteEvent": model.PromoteEvent,
    "ReconfigureEvent": model.ReconfigureEvent,
    "TenantReconfigureEvent": model.TenantReconfigureEvent,
}

# /zuul/events/tenant   TENANT_ROOT
#   /{tenant}           TENANT_NAME_ROOT
#     /management       TENANT_MANAGEMENT_ROOT
#       /queue          TENANT_MANAGEMENT_QUEUE
#       /data           [side channel data]
#     /trigger          TENANT_TRIGGER_ROOT
#       /queue          TENANT_TRIGGER_QUEUE
#       /data           [side channel data]
#     /pipelines        PIPELINE_ROOT
#       /{pipeline}     PIPELINE_NAME_ROOT
#         /management   PIPELINE_MANAGEMENT_ROOT
#           /queue      PIPELINE_MANAGEMENT_QUEUE
#           /data       [side channel data]
#         /trigger      PIPELINE_TRIGGER_ROOT
#           /queue      PIPELINE_TRIGGER_QUEUE
#           /data       [side channel data]
#         /result       PIPELINE_RESULT_ROOT
#           /queue      PIPELINE_RESULT_QUEUE
#           /data       [side channel data]

TENANT_ROOT = "/zuul/events/tenant"
TENANT_NAME_ROOT = TENANT_ROOT + "/{tenant}"
TENANT_MANAGEMENT_ROOT = TENANT_NAME_ROOT + "/management"
TENANT_MANAGEMENT_QUEUE = TENANT_MANAGEMENT_ROOT + "/queue"
TENANT_TRIGGER_ROOT = TENANT_NAME_ROOT + "/trigger"
TENANT_TRIGGER_QUEUE = TENANT_TRIGGER_ROOT + "/queue"
PIPELINE_ROOT = TENANT_NAME_ROOT + "/pipelines"
PIPELINE_NAME_ROOT = PIPELINE_ROOT + "/{pipeline}"
PIPELINE_MANAGEMENT_ROOT = PIPELINE_NAME_ROOT + "/management"
PIPELINE_MANAGEMENT_QUEUE = PIPELINE_MANAGEMENT_ROOT + "/queue"
PIPELINE_TRIGGER_ROOT = PIPELINE_NAME_ROOT + "/trigger"
PIPELINE_TRIGGER_QUEUE = PIPELINE_TRIGGER_ROOT + "/queue"
PIPELINE_RESULT_ROOT = PIPELINE_NAME_ROOT + "/result"
PIPELINE_RESULT_QUEUE = PIPELINE_RESULT_ROOT + "/queue"

CONNECTION_ROOT = "/zuul/events/connection"

# This is the path to the serialized from of the event in ZK (along
# with the version when it was read (which should not change since
# events are immutable in queue)).  When processing of the event is
# complete, this is the path that should be deleted in order to
# acknowledge it and prevent re-processing.  Instances of this are
# dynamically created and attached to de-serialized Event instances.
EventAckRef = namedtuple("EventAckRef", ("path", "version"))

UNKNOWN_ZVERSION = -1


class EventPrefix(enum.Enum):
    MANAGEMENT = "100"
    RESULT = "200"
    TRIGGER = "300"


class EventWatcher(ZooKeeperSimpleBase):

    log = logging.getLogger("zuul.zk.event_queues.EventWatcher")

    def __init__(self, client, callback):
        super().__init__(client)
        self.callback = callback
        self.watched_tenants = set()
        self.watched_pipelines = set()
        self.kazoo_client.ensure_path(TENANT_ROOT)
        self.kazoo_client.ChildrenWatch(TENANT_ROOT, self._tenantWatch)

    def _makePipelineWatcher(self, tenant_name):
        def watch(children, event=None):
            return self._pipelineWatch(tenant_name, children)
        return watch

    def _tenantWatch(self, tenants):
        for tenant_name in tenants:
            if tenant_name in self.watched_tenants:
                continue

            for path in (TENANT_MANAGEMENT_QUEUE,
                         TENANT_TRIGGER_QUEUE):
                path = path.format(tenant=tenant_name)
                self.kazoo_client.ensure_path(path)
                self.kazoo_client.ChildrenWatch(
                    path, self._eventWatch, send_event=True)

            pipelines_path = PIPELINE_ROOT.format(tenant=tenant_name)
            self.kazoo_client.ensure_path(pipelines_path)
            self.kazoo_client.ChildrenWatch(
                pipelines_path, self._makePipelineWatcher(tenant_name))

            self.watched_tenants.add(tenant_name)

    def _pipelineWatch(self, tenant_name, pipelines):
        for pipeline_name in pipelines:
            key = (tenant_name, pipeline_name)
            if key in self.watched_pipelines:
                continue

            for path in (PIPELINE_MANAGEMENT_QUEUE,
                         PIPELINE_TRIGGER_QUEUE,
                         PIPELINE_RESULT_QUEUE):
                path = path.format(tenant=tenant_name,
                                   pipeline=pipeline_name)

                self.kazoo_client.ensure_path(path)
                self.kazoo_client.ChildrenWatch(
                    path, self._eventWatch, send_event=True)
            self.watched_pipelines.add(key)

    def _eventWatch(self, event_list, event=None):
        if event is None:
            # Handle initial call when the watch is created. If there are
            # already events in the queue we trigger the callback.
            if event_list:
                self.callback()
        elif event.type == EventType.CHILD:
            self.callback()


class ZooKeeperEventQueue(ZooKeeperSimpleBase, Iterable):
    """Abstract API for events via ZooKeeper

    The lifecycle of a global (not pipeline-specific) event is:

    * Serialized form of event added to ZK queue.

    * During queue processing, events are de-serialized and
      AbstractEvent subclasses are instantiated.  An EventAckRef is
      associated with the event instance in order to maintain the link
      to the serialized form.

    * When event processing is complete, the EventAckRef is used to
      delete the original event.  If the event requires a result
      (e.g., a management event that returns data) the result will be
      written to a pre-determined location.  A future can watch for
      the result to appear at that location.

    Pipeline specific events usually start out as global events, but
    upon processing, may be forwarded to pipeline-specific queues.  In
    these cases, the original event will be deleted as above, and a
    new, identical event will be created in the pipeline-specific
    queue.  If the event expects a result, no result will be written
    upon forwarding; the result will only be written when the
    forwarded event is processed.

    """

    log = logging.getLogger("zuul.zk.event_queues.ZooKeeperEventQueue")

    def __init__(self, client, queue_root):
        super().__init__(client)
        self.queue_root = queue_root
        self.event_root = f'{queue_root}/queue'
        self.data_root = f'{queue_root}/data'
        self.kazoo_client.ensure_path(self.event_root)
        self.kazoo_client.ensure_path(self.data_root)

    def _listEvents(self):
        return self.kazoo_client.get_children(self.event_root)

    def __len__(self):
        try:
            data, stat = self.kazoo_client.get(self.event_root)
            return stat.children_count
        except NoNodeError:
            return 0

    def hasEvents(self):
        return bool(len(self))

    def ack(self, event):
        # Event.ack_ref is an EventAckRef, previously attached to an
        # event object when it was de-serialized.
        if not event.ack_ref:
            raise RuntimeError("Cannot ack event %s without reference", event)
        if not self._remove(event.ack_ref.path, event.ack_ref.version):
            self.log.warning("Event %s was already acknowledged", event)

    def _put(self, data):
        # Event data can be large, so we want to shard it.  But events
        # also need to be atomic (we don't want an event listener to
        # start processing a half-stored event).  A natural solution
        # is to write the sharded data along with the event.  However,
        # our events are sequence nodes in order to maintain ordering,
        # and we can't write shard nodes under the event without
        # creating the event first.  We can't use transactions because
        # they are subject to the same size limit.  To resolve this,
        # we store the event data in two places: the event itself and
        # associated metadata are in the event queue as a single
        # sequence node.  The event data are stored in a separate tree
        # under a UUID.  We have to use a UUID because we don't know
        # the sequence node when we write it.  The event metadata
        # includes the UUID of the data.  We call the separated data
        # "side channel data" to indicate it's stored outside the main
        # event queue.
        #
        # To make the API simpler to work with, we assume "event_data"
        # contains the bulk of the data.  We extract it here into the
        # side channel data, then in _iterEvents we re-constitute it
        # into the dictionary.

        # Add a trailing / for our sequence nodes
        event_path = f"{self.event_root}/"

        side_channel_data = None
        encoded_data = json.dumps(data, sort_keys=True).encode("utf-8")
        if (len(encoded_data) > sharding.NODE_BYTE_SIZE_LIMIT
            and 'event_data' in data):
            # Get a unique data node
            data_id = str(uuid.uuid4())
            data_root = f'{self.data_root}/{data_id}'
            side_channel_data = json.dumps(data['event_data'],
                                           sort_keys=True).encode("utf-8")
            data = data.copy()
            del data['event_data']
            data['event_data_path'] = data_root
            encoded_data = json.dumps(data, sort_keys=True).encode("utf-8")

            with sharding.BufferedShardWriter(
                    self.kazoo_client, data_root) as stream:
                stream.write(side_channel_data)

        return self.kazoo_client.create(
            event_path, encoded_data, sequence=True)

    def _iterEvents(self):
        try:
            # We need to sort this ourself, since Kazoo doesn't guarantee any
            # ordering of the returned children.
            events = sorted(self._listEvents())
        except NoNodeError:
            return

        for event_id in events:
            path = "/".join((self.event_root, event_id))

            # Load the event metadata
            data, zstat = self.kazoo_client.get(path)
            try:
                event = json.loads(data)
            except json.JSONDecodeError:
                self.log.exception("Malformed event data in %s", path)
                self._remove(path)
                continue

            # Load the event data (if present); if that fails, the
            # event is corrupt; delete and continue.
            side_channel_path = event.get('event_data_path')
            if side_channel_path:
                try:
                    with sharding.BufferedShardReader(
                            self.kazoo_client, side_channel_path) as stream:
                        side_channel_data = stream.read()
                except NoNodeError:
                    self.log.exception("Side channel data for %s "
                                       "not found at %s",
                                       path, side_channel_path)
                    self._remove(path)
                    continue

                try:
                    event_data = json.loads(side_channel_data)
                except json.JSONDecodeError:
                    self.log.exception("Malformed side channel "
                                       "event data in %s",
                                       side_channel_path)
                    self._remove(path)
                    continue
                event['event_data'] = event_data

            yield event, EventAckRef(path, zstat.version), zstat

    def _remove(self, path, version=UNKNOWN_ZVERSION):
        try:
            # Find the side channel path

            side_channel_path = None
            data, zstat = self.kazoo_client.get(path)
            try:
                event = json.loads(data)
                side_channel_path = event.get('event_data_path')
            except json.JSONDecodeError:
                pass

            if side_channel_path:
                with suppress(NoNodeError):
                    self.kazoo_client.delete(side_channel_path, recursive=True)

            self.kazoo_client.delete(path, version=version, recursive=True)
            return True
        except NoNodeError:
            return False

    def _findLostSideChannelData(self, age):
        # Get data nodes which are older than the specified age (we
        # don't want to delete nodes which are just being written
        # slowly).
        # Convert to MS
        now = int(time.time() * 1000)
        age = age * 1000
        data_nodes = set()
        for data_id in self.kazoo_client.get_children(self.data_root):
            data_path = f'{self.data_root}/{data_id}'
            data_zstat = self.kazoo_client.exists(data_path)
            if now - data_zstat.mtime > age:
                data_nodes.add(data_path)

        # If there are no candidate data nodes, we don't need to
        # filter them by known events.
        if not data_nodes:
            return data_nodes

        events = set(self._listEvents())

        for event_id in events:
            # Load the event metadata
            path = "/".join((self.event_root, event_id))
            data, zstat = self.kazoo_client.get(path)
            try:
                event = json.loads(data)
            except json.JSONDecodeError:
                self.log.exception("Malformed event data in %s", path)
                self._remove(path)
                continue

            side_channel_path = event.get('event_data_path')
            if side_channel_path:
                data_nodes.discard(side_channel_path)
        return data_nodes

    def cleanup(self, age=300):
        try:
            for path in self._findLostSideChannelData(age):
                try:
                    self.log.error("Removing side channel data: %s", path)
                    self.kazoo_client.delete(path, recursive=True)
                except Exception:
                    self.log.execption(
                        "Unable to delete side channel data %s", path)
        except Exception:
            self.log.exception("Error cleaning up event queue %s", self)


class EventResultFuture(ZooKeeperSimpleBase):
    """Base class for result futures for different events."""

    log = logging.getLogger("zuul.zk.event_queues.EventResultFuture")

    def __init__(self, client, result_path):
        super().__init__(client)
        self._result_path = result_path
        self._wait_event = threading.Event()
        self.kazoo_client.DataWatch(self._result_path, self._resultCallback)
        self.data = {}

    def _resultCallback(self, data=None, stat=None):
        if data is None:
            # Igore events w/o any data
            return None
        self._wait_event.set()
        # Stop the watch if we got a result
        return False

    def _read(self):
        # Internal method to read the result data; may be overridden
        # by subclasses.
        return self.kazoo_client.get(self._result_path)[0]

    def _delete(self):
        with suppress(NoNodeError):
            self.kazoo_client.delete(self._result_path, recursive=True)

    def wait(self, timeout=None):
        """Wait until the result for this event has been written."""

        # Note that due to event forwarding, the only way to confirm
        # that an event has been processed is to check for a result;
        # the original event may have been deleted when forwaded to a
        # different queue.
        if not self._wait_event.wait(timeout):
            return False
        try:
            try:
                data = self._read()
                self.data = json.loads(data.decode("utf-8"))
            except json.JSONDecodeError:
                self.log.exception(
                    "Malformed result data in %s", self._result_path
                )
                raise
        finally:
            self._delete()
        return True


class JobResultFuture(EventResultFuture):

    log = logging.getLogger("zuul.JobResultFuture")

    def __init__(self, client, request_path, result_path, waiter_path):
        super().__init__(client, result_path)

        self.request_path = request_path
        self._waiter_path = waiter_path
        self._result_data_path = None
        self.merged = None
        self.updated = None
        self.commit = None
        self.files = None
        self.repo_state = None
        self.item_in_branches = None

    def _read(self):
        result_node = self.kazoo_client.get(self._result_path)[0]
        result = json.loads(result_node)
        self._result_data_path = result['result_data_path']
        with sharding.BufferedShardReader(
                self.kazoo_client, self._result_data_path) as stream:
            return stream.read()

    def _delete(self):
        super()._delete()
        if self._result_data_path:
            with suppress(NoNodeError):
                self.kazoo_client.delete(self._result_data_path,
                                         recursive=True)

    def wait(self, timeout=None):
        try:
            res = super().wait(timeout)
        finally:
            with suppress(NoNodeError):
                self.kazoo_client.delete(self._waiter_path)
        self.merged = self.data.get("merged", False)
        self.updated = self.data.get("updated", False)
        self.commit = self.data.get("commit")
        self.files = self.data.get("files", {})
        self.repo_state = self.data.get("repo_state", {})
        self.item_in_branches = self.data.get("item_in_branches", [])
        return res

    def cancel(self):
        # Remove our waiter node so that if a result is ever reported,
        # it will be garbage collected.
        with suppress(NoNodeError):
            self.kazoo_client.delete(self._waiter_path)


class ManagementEventResultFuture(EventResultFuture):
    """Returned when a management event is put into a queue."""

    log = logging.getLogger("zuul.zk.event_queues.ManagementEventResultFuture")

    def __init__(self, client, result_path: str):
        super().__init__(client, result_path)

    def wait(self, timeout=None):
        res = super().wait(timeout)
        tb = self.data.get("traceback")
        if tb is not None:
            # TODO: raise some kind of ManagementEventException here
            raise RuntimeError(tb)
        return res


class ManagementEventQueue(ZooKeeperEventQueue):
    """Management events via ZooKeeper"""

    RESULTS_ROOT = "/zuul/results/management"

    log = logging.getLogger("zuul.zk.event_queues.ManagementEventQueue")

    def put(self, event, needs_result=True):
        result_path = None
        # If this event is forwarded it might have a result ref that
        # we need to forward.
        if event.result_ref:
            result_path = event.result_ref
        elif needs_result:
            result_path = "/".join((self.RESULTS_ROOT, str(uuid.uuid4())))

        data = {
            "event_type": type(event).__name__,
            "event_data": event.toDict(),
            "result_path": result_path,
        }
        if needs_result and not event.result_ref:
            # The event was not forwarded, create the result ref
            self.kazoo_client.create(result_path, None,
                                     makepath=True, ephemeral=True)
        self._put(data)
        if needs_result and result_path:
            return ManagementEventResultFuture(self.client, result_path)
        return None

    def __iter__(self):
        event_list = []
        for data, ack_ref, zstat in self._iterEvents():
            try:
                event_class = MANAGEMENT_EVENT_TYPE_MAP[data["event_type"]]
                event_data = data["event_data"]
                result_path = data["result_path"]
            except KeyError:
                self.log.warning("Malformed event found: %s", data)
                self._remove(ack_ref.path, ack_ref.version)
                continue
            event = event_class.fromDict(event_data)
            event.ack_ref = ack_ref
            event.result_ref = result_path
            # Initialize the logical timestamp if not valid
            if event.zuul_event_ltime is None:
                event.zuul_event_ltime = zstat.creation_transaction_id

            try:
                other_event = event_list[event_list.index(event)]
            except ValueError:
                other_event = None
            if other_event:
                if isinstance(other_event, model.TenantReconfigureEvent):
                    other_event.merge(event)
                    continue
            event_list.append(event)
        yield from event_list

    def ack(self, event):
        """Acknowledge the event (by deleting it from the queue)"""
        # Note: the result is reported first to ensure that the
        # originator of the event which may be waiting on a future
        # receives a result, or otherwise this event is considered
        # unprocessed and remains on the queue.
        self._reportResult(event)
        super().ack(event)
        if isinstance(event, model.TenantReconfigureEvent):
            for merged_event in event.merged_events:
                merged_event.traceback = event.traceback
                self._reportResult(merged_event)
                super().ack(merged_event)

    def _reportResult(self, event):
        if not event.result_ref:
            return

        result_data = {"traceback": event.traceback,
                       "timestamp": time.monotonic()}
        try:
            self.kazoo_client.set(
                event.result_ref,
                json.dumps(result_data, sort_keys=True).encode("utf-8"),
            )
        except NoNodeError:
            self.log.warning(f"No result node found for {event}; "
                             "client may have disconnected")


class PipelineManagementEventQueue(ManagementEventQueue):
    log = logging.getLogger(
        "zuul.zk.event_queues.PipelineManagementEventQueue"
    )

    def __init__(self, client, tenant_name, pipeline_name):
        queue_root = PIPELINE_MANAGEMENT_ROOT.format(
            tenant=tenant_name,
            pipeline=pipeline_name)
        super().__init__(client, queue_root)

    @classmethod
    def createRegistry(cls, client):
        """Create a tenant/pipeline queue registry

        Returns a nested dictionary of:
          tenant_name -> pipeline_name -> EventQueue

        Queues are dynamically created with the originally supplied ZK
        client as they are accessed via the registry (so new tenants
        or pipelines show up automatically).

        """
        return DefaultKeyDict(lambda t: cls._createRegistry(client, t))

    @classmethod
    def _createRegistry(cls, client, tenant_name):
        return DefaultKeyDict(lambda p: cls(client, tenant_name, p))


class TenantManagementEventQueue(ManagementEventQueue):
    log = logging.getLogger("zuul.zk.event_queues.TenantManagementEventQueue")

    def __init__(self, client, tenant_name):
        queue_root = TENANT_MANAGEMENT_ROOT.format(
            tenant=tenant_name)
        super().__init__(client, queue_root)

    def ackWithoutResult(self, event):
        """
        Used to ack a management event when forwarding to a pipeline queue
        """
        super(ManagementEventQueue, self).ack(event)
        if isinstance(event, model.TenantReconfigureEvent):
            for merged_event in event.merged_events:
                super(ManagementEventQueue, self).ack(merged_event)

    @classmethod
    def createRegistry(cls, client):
        """Create a tenant queue registry

        Returns a dictionary of: tenant_name -> EventQueue

        Queues are dynamically created with the originally supplied ZK
        client as they are accessed via the registry (so new tenants
        show up automatically).

        """
        return DefaultKeyDict(lambda t: cls(client, t))


class PipelineResultEventQueue(ZooKeeperEventQueue):
    """Result events via ZooKeeper"""

    log = logging.getLogger("zuul.zk.event_queues.PipelineResultEventQueue")

    def __init__(self, client, tenant_name, pipeline_name):
        queue_root = PIPELINE_RESULT_ROOT.format(
            tenant=tenant_name,
            pipeline=pipeline_name)
        super().__init__(client, queue_root)

    @classmethod
    def createRegistry(cls, client):
        """Create a tenant/pipeline queue registry

        Returns a nested dictionary of:
          tenant_name -> pipeline_name -> EventQueue

        Queues are dynamically created with the originally supplied ZK
        client as they are accessed via the registry (so new tenants
        or pipelines show up automatically).

        """
        return DefaultKeyDict(lambda t: cls._createRegistry(client, t))

    @classmethod
    def _createRegistry(cls, client, tenant_name):
        return DefaultKeyDict(lambda p: cls(client, tenant_name, p))

    def put(self, event):
        data = {
            "event_type": type(event).__name__,
            "event_data": event.toDict(),
        }
        self._put(data)

    def __iter__(self):
        for data, ack_ref, _ in self._iterEvents():
            try:
                event_class = RESULT_EVENT_TYPE_MAP[data["event_type"]]
                event_data = data["event_data"]
            except KeyError:
                self.log.warning("Malformed event found: %s", data)
                self._remove(ack_ref.path, ack_ref.version)
                continue
            event = event_class.fromDict(event_data)
            event.ack_ref = ack_ref
            yield event


class TriggerEventQueue(ZooKeeperEventQueue):
    """Trigger events via ZooKeeper"""

    log = logging.getLogger("zuul.zk.event_queues.TriggerEventQueue")

    def __init__(self, client, queue_root, connections):
        self.connections = connections
        super().__init__(client, queue_root)

    def put(self, driver_name, event):
        data = {
            "driver_name": driver_name,
            "event_data": event.toDict(),
        }
        self._put(data)

    def __iter__(self):
        for data, ack_ref, _ in self._iterEvents():
            try:
                event_class = self.connections.getTriggerEventClass(
                    data["driver_name"]
                )
                event_data = data["event_data"]
            except KeyError:
                self.log.warning("Malformed event found: %s", data)
                self._remove(ack_ref.path, ack_ref.version)
                continue
            event = event_class.fromDict(event_data)
            event.ack_ref = ack_ref
            event.driver_name = data["driver_name"]
            yield event


class TenantTriggerEventQueue(TriggerEventQueue):
    log = logging.getLogger("zuul.zk.event_queues.TenantTriggerEventQueue")

    def __init__(self, client, connections, tenant_name):
        queue_root = TENANT_TRIGGER_ROOT.format(
            tenant=tenant_name)
        super().__init__(client, queue_root, connections)

    @classmethod
    def createRegistry(cls, client, connections):
        """Create a tenant queue registry

        Returns a dictionary of: tenant_name -> EventQueue

        Queues are dynamically created with the originally supplied ZK
        client as they are accessed via the registry (so new tenants
        show up automatically).

        """
        return DefaultKeyDict(lambda t: cls(client, connections, t))


class PipelineTriggerEventQueue(TriggerEventQueue):
    log = logging.getLogger("zuul.zk.event_queues.PipelineTriggerEventQueue")

    def __init__(self, client, tenant_name, pipeline_name, connections):
        queue_root = PIPELINE_TRIGGER_ROOT.format(
            tenant=tenant_name,
            pipeline=pipeline_name)
        super().__init__(client, queue_root, connections)

    @classmethod
    def createRegistry(cls, client, connections):
        """Create a tenant/pipeline queue registry

        Returns a nested dictionary of:
          tenant_name -> pipeline_name -> EventQueue

        Queues are dynamically created with the originally supplied ZK
        client and connection registry as they are accessed via the
        queue registry (so new tenants or pipelines show up
        automatically).

        """
        return DefaultKeyDict(
            lambda t: cls._createRegistry(client, t, connections)
        )

    @classmethod
    def _createRegistry(cls, client, tenant_name, connections):
        return DefaultKeyDict(
            lambda p: cls(client, tenant_name, p, connections)
        )


class ConnectionEventQueue(ZooKeeperEventQueue):
    """Connection events via ZooKeeper"""

    log = logging.getLogger("zuul.zk.event_queues.ConnectionEventQueue")

    def __init__(self, client, connection_name):
        queue_root = "/".join((CONNECTION_ROOT, connection_name, "events"))
        super().__init__(client, queue_root)
        self.election_root = "/".join(
            (CONNECTION_ROOT, connection_name, "election")
        )
        self.kazoo_client.ensure_path(self.election_root)
        self.election = SessionAwareElection(
            self.kazoo_client, self.election_root)

    def _eventWatch(self, callback, event_list):
        if event_list:
            return callback()

    def registerEventWatch(self, callback):
        self.kazoo_client.ChildrenWatch(
            self.event_root, functools.partial(self._eventWatch, callback)
        )

    def put(self, data):
        self.log.debug("Submitting connection event to queue %s: %s",
                       self.event_root, data)
        self._put({'event_data': data})

    def __iter__(self):
        for data, ack_ref, _ in self._iterEvents():
            if not data:
                self.log.warning("Malformed event found: %s", data)
                self._remove(ack_ref.path)
                continue
            # TODO: We can assume event_data exists after 4.6.1 is released
            event = model.ConnectionEvent.fromDict(
                data.get('event_data', data))
            event.ack_ref = ack_ref
            yield event


class EventReceiverElection(SessionAwareElection):
    """Election for a singleton event receiver."""

    def __init__(self, client, connection_name, receiver_name):
        self.election_root = "/".join(
            (CONNECTION_ROOT, connection_name, f"election-{receiver_name}")
        )
        super().__init__(client.client, self.election_root)


class NodepoolEventElection(SessionAwareElection):
    """Election for the nodepool completion event processor."""

    def __init__(self, client):
        self.election_root = "/zuul/nodepool/election"
        super().__init__(client.client, self.election_root)
