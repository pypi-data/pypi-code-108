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

import json
import logging
import time
from contextlib import suppress
from enum import Enum

from kazoo.exceptions import LockTimeout, NoNodeError
from kazoo.protocol.states import EventType

from zuul.lib.jsonutil import json_dumps
from zuul.lib.logutil import get_annotated_logger
from zuul.model import JobRequest
from zuul.zk import ZooKeeperSimpleBase, sharding
from zuul.zk.event_queues import JobResultFuture
from zuul.zk.exceptions import JobRequestNotFound
from zuul.zk.vendor.watchers import ExistingDataWatch
from zuul.zk.locks import SessionAwareLock


class JobRequestEvent(Enum):
    CREATED = 0
    UPDATED = 1
    RESUMED = 2
    CANCELED = 3
    DELETED = 4


class JobRequestQueue(ZooKeeperSimpleBase):
    log = logging.getLogger("zuul.JobRequestQueue")
    request_class = JobRequest

    def __init__(self, client, root, use_cache=True,
                 request_callback=None, event_callback=None):
        super().__init__(client)

        self.use_cache = use_cache

        self.REQUEST_ROOT = f"{root}/requests"
        self.LOCK_ROOT = f"{root}/locks"
        self.PARAM_ROOT = f"{root}/params"
        self.RESULT_ROOT = f"{root}/results"
        self.RESULT_DATA_ROOT = f"{root}/result-data"
        self.WAITER_ROOT = f"{root}/waiters"

        self.request_callback = request_callback
        self.event_callback = event_callback

        # path -> request
        self._cached_requests = {}

        self.kazoo_client.ensure_path(self.REQUEST_ROOT)
        self.kazoo_client.ensure_path(self.PARAM_ROOT)
        self.kazoo_client.ensure_path(self.RESULT_ROOT)
        self.kazoo_client.ensure_path(self.RESULT_DATA_ROOT)
        self.kazoo_client.ensure_path(self.WAITER_ROOT)
        self.kazoo_client.ensure_path(self.LOCK_ROOT)

        self.register()

    @property
    def initial_state(self):
        # This supports holding requests in tests
        return self.request_class.REQUESTED

    def register(self):
        if self.use_cache:
            # Register a child watch that listens for new requests
            self.kazoo_client.ChildrenWatch(
                self.REQUEST_ROOT,
                self._makeRequestWatcher(self.REQUEST_ROOT),
                send_event=True,
            )

    def _makeRequestWatcher(self, path):
        def watch(requests, event=None):
            return self._watchRequests(path, requests)
        return watch

    def _watchRequests(self, path, requests):
        # The requests list always contains all active children. Thus,
        # we first have to find the new ones by calculating the delta
        # between the requests list and our current cache entries.
        # NOTE (felix): We could also use this list to determine the
        # deleted requests, but it's easier to do this in the
        # DataWatch for the single request instead. Otherwise we have
        # to deal with race conditions between the children and the
        # data watch as one watch might update a cache entry while the
        # other tries to remove it.

        request_paths = {
            f"{path}/{uuid}" for uuid in requests
        }

        new_requests = request_paths - set(
            self._cached_requests.keys()
        )

        for req_path in new_requests:
            ExistingDataWatch(self.kazoo_client,
                              req_path,
                              self._makeStateWatcher(req_path))

        # Notify the user about new requests if a callback is provided.
        # When we register the data watch, we will receive an initial
        # callback immediately.  The list of children may be empty in
        # that case, so we should not fire our callback since there
        # are no requests to handle.

        if new_requests and self.request_callback:
            self.request_callback()

    def _makeStateWatcher(self, path):
        def watch(data, stat, event=None):
            return self._watchState(path, data, stat, event)
        return watch

    def _watchState(self, path, data, stat, event=None):
        if (not event or event.type == EventType.CHANGED) and data is not None:
            # As we already get the data and the stat value, we can directly
            # use it without asking ZooKeeper for the data again.
            content = self._bytesToDict(data)
            if not content:
                return

            # We need this one for the HOLD -> REQUESTED check further down
            old_request = self._cached_requests.get(path)

            request = self.request_class.fromDict(content)
            request.path = path
            request._zstat = stat
            self._cached_requests[path] = request

            # NOTE (felix): This is a test-specific condition: For test cases
            # which are using hold_*_jobs_in_queue the state change on the
            # request from HOLD to REQUESTED is done outside of the server.
            # Thus, we must also set the wake event (the callback) so the
            # servercan pick up those jobs after they are released. To not
            # cause a thundering herd problem in production for each cache
            # update, the callback is only called under this very specific
            # condition that can only occur in the tests.
            if (
                self.request_callback
                and old_request
                and old_request.state == self.request_class.HOLD
                and request.state == self.request_class.REQUESTED
            ):
                self.request_callback()

        elif ((event and event.type == EventType.DELETED) or data is None):
            request = self._cached_requests.get(path)
            with suppress(KeyError):
                del self._cached_requests[path]

            if request and self.event_callback:
                self.event_callback(request, JobRequestEvent.DELETED)

            # Return False to stop the datawatch as the build got deleted.
            return False

    def inState(self, *states):
        if not states:
            # If no states are provided, build a tuple containing all available
            # ones to always match. We need a tuple to be compliant to the
            # type of *states above.
            states = self.request_class.ALL_STATES

        requests = [
            req for req in self._cached_requests.values()
            if req.state in states
        ]

        # Sort the list of requests by precedence and their creation time
        # in ZooKeeper in ascending order to prevent older requests from
        # starving.
        return sorted(requests)

    def next(self):
        yield from self.inState(self.request_class.REQUESTED)

    def submit(self, request, params, needs_result=False):
        log = get_annotated_logger(self.log, event=request.event_id)

        path = "/".join([self.REQUEST_ROOT, request.uuid])
        request.path = path

        if not isinstance(request, self.request_class):
            raise RuntimeError("Request of wrong class")
        if request.state != self.request_class.UNSUBMITTED:
            raise RuntimeError("Request state must be unsubmitted")
        request.state = self.initial_state

        result = None

        # If a result is needed, create the result_path with the same
        # UUID and store it on the request, so the server can store
        # the result there.
        if needs_result:
            result_path = "/".join(
                [self.RESULT_ROOT, request.uuid]
            )
            waiter_path = "/".join(
                [self.WAITER_ROOT, request.uuid]
            )
            self.kazoo_client.create(waiter_path, ephemeral=True)
            result = JobResultFuture(self.client, request.path,
                                     result_path, waiter_path)
            request.result_path = result_path

        log.debug("Submitting job request to ZooKeeper %s", request)

        params_path = self._getParamsPath(request.uuid)
        with sharding.BufferedShardWriter(
            self.kazoo_client, params_path
        ) as stream:
            stream.write(self._dictToBytes(params))

        self.kazoo_client.create(path, self._dictToBytes(request.toDict()))

        return result

    def update(self, request):
        log = get_annotated_logger(
            self.log, event=request.event_id, build=request.uuid
        )
        log.debug("Updating request %s", request)

        if request._zstat is None:
            log.debug(
                "Cannot update request %s: Missing version information.",
                request.uuid,
            )
            return
        try:
            zstat = self.kazoo_client.set(
                request.path,
                self._dictToBytes(request.toDict()),
                version=request._zstat.version,
            )
            # Update the zstat on the item after updating the ZK node
            request._zstat = zstat
        except NoNodeError:
            raise JobRequestNotFound(
                f"Could not update {request.path}"
            )

    def reportResult(self, request, result):
        # Write the result data first since it may be multiple nodes.
        result_data_path = "/".join(
            [self.RESULT_DATA_ROOT, request.uuid]
        )
        with sharding.BufferedShardWriter(
                self.kazoo_client, result_data_path) as stream:
            stream.write(self._dictToBytes(result))

        # Then write the result node to signify it's ready.
        data = {'result_data_path': result_data_path}
        self.kazoo_client.create(request.result_path,
                                 self._dictToBytes(data))

    def get(self, path):
        """Get a request

        Note: do not mix get with iteration; iteration returns cached
        requests while get returns a newly created object each
        time. If you lock a request, you must use the same object to
        unlock it.

        """
        try:
            data, zstat = self.kazoo_client.get(path)
        except NoNodeError:
            return None

        if not data:
            return None

        content = self._bytesToDict(data)

        request = self.request_class.fromDict(content)
        request.path = path
        request._zstat = zstat

        return request

    def getByUuid(self, uuid):
        """Get a request by its UUID without using the cache."""
        path = f"{self.REQUEST_ROOT}/{uuid}"
        return self.get(path)

    def refresh(self, request):
        """Refreshs a request object with the current data from ZooKeeper. """
        try:
            data, zstat = self.kazoo_client.get(request.path)
        except NoNodeError:
            raise JobRequestNotFound(
                f"Could not refresh {request}, ZooKeeper node is missing")

        if not data:
            raise JobRequestNotFound(
                f"Could not refresh {request}, ZooKeeper node is empty")

        content = self._bytesToDict(data)

        request.updateFromDict(content)
        request._zstat = zstat

    def remove(self, request):
        log = get_annotated_logger(self.log, request.event_id)
        log.debug("Removing request %s", request)
        try:
            self.kazoo_client.delete(request.path, recursive=True)
        except NoNodeError:
            # Nothing to do if the node is already deleted
            pass
        try:
            self.clearParams(request)
        except NoNodeError:
            pass
        self._deleteLock(request.uuid)

    # We use child nodes here so that we don't need to lock the
    # request node.
    def requestResume(self, request):
        self.kazoo_client.ensure_path(f"{request.path}/resume")

    def requestCancel(self, request):
        self.kazoo_client.ensure_path(f"{request.path}/cancel")

    def fulfillResume(self, request):
        self.kazoo_client.delete(f"{request.path}/resume")

    def fulfillCancel(self, request):
        self.kazoo_client.delete(f"{request.path}/cancel")

    def _watchEvents(self, actions, event=None):
        if event is None:
            return

        job_event = None
        if "cancel" in actions:
            job_event = JobRequestEvent.CANCELED
        elif "resume" in actions:
            job_event = JobRequestEvent.RESUMED

        if job_event:
            request = self._cached_requests.get(event.path)
            self.event_callback(request, job_event)

    def lock(self, request, blocking=True, timeout=None):
        path = "/".join([self.LOCK_ROOT, request.uuid])
        have_lock = False
        lock = None
        try:
            lock = SessionAwareLock(self.kazoo_client, path)
            have_lock = lock.acquire(blocking, timeout)
        except LockTimeout:
            have_lock = False
            self.log.error(
                "Timeout trying to acquire lock: %s", request.uuid
            )

        # If we aren't blocking, it's possible we didn't get the lock
        # because someone else has it.
        if not have_lock:
            return False

        if not self.kazoo_client.exists(request.path):
            self._releaseLock(request, lock)
            return False

        # Update the request to ensure that we operate on the newest data.
        try:
            self.refresh(request)
        except JobRequestNotFound:
            self._releaseLock(request, lock)
            return False

        request.lock = lock

        # Create the children watch to listen for cancel/resume actions on this
        # build request.
        if self.event_callback:
            self.kazoo_client.ChildrenWatch(
                request.path, self._watchEvents, send_event=True)

        return True

    def _releaseLock(self, request, lock):
        """Releases a lock.

        This is used directly after acquiring the lock in case something went
        wrong.
        """
        lock.release()
        self.log.error("Request not found for locking: %s", request.uuid)

        # We may have just re-created the lock parent node just after the
        # scheduler deleted it; therefore we should (re-) delete it.
        self._deleteLock(request.uuid)

    def _deleteLock(self, uuid):
        # Recursively delete the children and the lock parent node.
        path = "/".join([self.LOCK_ROOT, uuid])
        try:
            children = self.kazoo_client.get_children(path)
        except NoNodeError:
            # The lock is apparently already gone.
            return
        tr = self.kazoo_client.transaction()
        for child in children:
            tr.delete("/".join([path, child]))
        tr.delete(path)
        # We don't care about the results
        tr.commit()

    def unlock(self, request):
        if request.lock is None:
            self.log.warning(
                "Request %s does not hold a lock", request
            )
        else:
            request.lock.release()
            request.lock = None

    def isLocked(self, request):
        path = "/".join([self.LOCK_ROOT, request.uuid])
        if not self.kazoo_client.exists(path):
            return False
        lock = SessionAwareLock(self.kazoo_client, path)
        is_locked = len(lock.contenders()) > 0
        return is_locked

    def lostRequests(self):
        # Get a list of requests which are running but not locked by
        # any client.
        for req in self.inState(self.request_class.RUNNING):
            if self.isLocked(req):
                continue
            # Double check that our cache isn't out of date: it should
            # still exist and be running.
            oldreq = req
            req = self.get(oldreq.path)
            if req is None:
                self._deleteLock(oldreq.uuid)
            elif req.state == self.request_class.RUNNING:
                yield req

    def _getAllRequestIds(self):
        # Get a list of all request ids without using the cache.
        return self.kazoo_client.get_children(self.REQUEST_ROOT)

    def _findLostParams(self, age):
        # Get data nodes which are older than the specified age (we
        # don't want to delete nodes which are just being written
        # slowly).
        # Convert to MS
        now = int(time.time() * 1000)
        age = age * 1000
        data_nodes = dict()
        for data_id in self.kazoo_client.get_children(self.PARAM_ROOT):
            data_path = self._getParamsPath(data_id)
            data_zstat = self.kazoo_client.exists(data_path)
            if now - data_zstat.mtime > age:
                data_nodes[data_id] = data_path

        # If there are no candidate data nodes, we don't need to
        # filter them by known requests.
        if not data_nodes:
            return data_nodes.values()

        # Remove current request uuids
        for request_id in self._getAllRequestIds():
            if request_id in data_nodes:
                del data_nodes[request_id]

        # Return the paths
        return data_nodes.values()

    def _findLostResults(self):
        # Get a list of results which don't have a connection waiting for
        # them. As the results and waiters are not part of our cache, we have
        # to look them up directly from ZK.
        waiters1 = set(self.kazoo_client.get_children(self.WAITER_ROOT))
        results = set(self.kazoo_client.get_children(self.RESULT_ROOT))
        result_data = set(self.kazoo_client.get_children(
            self.RESULT_DATA_ROOT))
        waiters2 = set(self.kazoo_client.get_children(self.WAITER_ROOT))

        waiters = waiters1.union(waiters2)
        lost_results = results - waiters
        lost_data = result_data - waiters
        return lost_results, lost_data

    def cleanup(self, age=300):
        # Delete build request params which are not associated with
        # any current build requests.  Note, this does not clean up
        # lost requests themselves; the client takes care of that.
        try:
            for path in self._findLostParams(age):
                try:
                    self.log.error("Removing request params: %s", path)
                    self.kazoo_client.delete(path, recursive=True)
                except Exception:
                    self.log.execption(
                        "Unable to delete request params %s", path)
        except Exception:
            self.log.exception(
                "Error cleaning up request queue %s", self)
        try:
            lost_results, lost_data = self._findLostResults()
            for result_id in lost_results:
                try:
                    path = '/'.join([self.RESULT_ROOT, result_id])
                    self.log.error("Removing request result: %s", path)
                    self.kazoo_client.delete(path, recursive=True)
                except Exception:
                    self.log.execption(
                        "Unable to delete request params %s", result_id)
            for result_id in lost_data:
                try:
                    path = '/'.join([self.RESULT_DATA_ROOT, result_id])
                    self.log.error(
                        "Removing request result data: %s", path)
                    self.kazoo_client.delete(path, recursive=True)
                except Exception:
                    self.log.execption(
                        "Unable to delete request params %s", result_id)
        except Exception:
            self.log.exception(
                "Error cleaning up result queue %s", self)
        try:
            for lock_id in self.kazoo_client.get_children(self.LOCK_ROOT):
                try:
                    lock_path = "/".join([self.LOCK_ROOT, lock_id])
                    request_path = "/".join([self.REQUEST_ROOT, lock_id])
                    if not self.kazoo_client.exists(request_path):
                        self.log.error("Removing stale lock: %s", lock_path)
                        self.kazoo_client.delete(lock_path, recursive=True)
                except Exception:
                    self.log.execption(
                        "Unable to delete lock %s", path)
        except Exception:
            self.log.exception("Error cleaning up locks %s", self)

    @staticmethod
    def _bytesToDict(data):
        return json.loads(data.decode("utf-8"))

    @staticmethod
    def _dictToBytes(data):
        # The custom json_dumps() will also serialize MappingProxyType objects
        return json_dumps(data, sort_keys=True).encode("utf-8")

    def _getParamsPath(self, uuid):
        return '/'.join([self.PARAM_ROOT, uuid])

    def clearParams(self, request):
        """Erase the parameters from ZK to save space"""
        self.kazoo_client.delete(self._getParamsPath(request.uuid),
                                 recursive=True)

    def getParams(self, request):
        """Return the parameters for a request, if they exist.

        Once a request is accepted by an executor, the params
        may be erased from ZK; this will return None in that case.

        """
        with sharding.BufferedShardReader(
            self.kazoo_client, self._getParamsPath(request.uuid)
        ) as stream:
            data = stream.read()
            if not data:
                return None
            return self._bytesToDict(data)

    def deleteResult(self, path):
        with suppress(NoNodeError):
            self.kazoo_client.delete(path, recursive=True)
