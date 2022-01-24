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

import logging

from kazoo.exceptions import NoNodeError

from zuul.lib.collections import DefaultKeyDict
from zuul.model import BuildRequest
from zuul.zk.job_request_queue import JobRequestQueue


class ExecutorQueue(JobRequestQueue):
    log = logging.getLogger("zuul.ExecutorQueue")
    request_class = BuildRequest

    def __init__(self, client, root,
                 initial_state_getter,
                 use_cache=True,
                 request_callback=None,
                 event_callback=None):
        self.log.debug("Creating executor queue at root %s", root)
        self._initial_state_getter = initial_state_getter
        super().__init__(
            client, root, use_cache, request_callback, event_callback)

    @property
    def initial_state(self):
        # This supports holding requests in tests
        return self._initial_state_getter()

    def lostRequests(self):
        # Get a list of requests which are running but not locked by
        # any client.
        yield from filter(
            lambda b: not self.isLocked(b),
            self.inState(self.request_class.RUNNING,
                         self.request_class.PAUSED),
        )


class ExecutorApi:
    log = logging.getLogger("zuul.ExecutorApi")

    def __init__(self, client, zone_filter=None, use_cache=True,
                 build_request_callback=None,
                 build_event_callback=None):
        self.client = client
        self.use_cache = use_cache
        self.request_callback = build_request_callback
        self.event_callback = build_event_callback
        self.zone_filter = zone_filter
        self._watched_zones = set()
        self.root = '/zuul/executor'
        self.unzoned_root = f"{self.root}/unzoned"
        self.zones_root = f"{self.root}/zones"

        self.zone_queues = DefaultKeyDict(
            lambda zone: ExecutorQueue(
                self.client,
                self._getZoneRoot(zone),
                self._getInitialState,
                self.use_cache,
                self.request_callback,
                self.event_callback))

        if zone_filter is None:
            self.registerAllZones()
        else:
            for zone in zone_filter:
                # For the side effect of creating a queue
                self.zone_queues[zone]

    def _getInitialState(self):
        return BuildRequest.REQUESTED

    def _getZoneRoot(self, zone):
        if zone is None:
            return self.unzoned_root
        else:
            return f"{self.zones_root}/{zone}"

    def registerAllZones(self):
        # Register a child watch that listens to new zones and automatically
        # registers to them.
        def watch_zones(children):
            for zone in children:
                # For the side effect of creating a queue
                self.zone_queues[zone]

        self.client.client.ChildrenWatch(self.zones_root, watch_zones)
        # For the side effect of creating a queue
        self.zone_queues[None]

    def _getAllZones(self):
        # Get a list of all zones without using the cache.
        try:
            # Get all available zones from ZooKeeper
            zones = self.client.client.get_children(self.zones_root)
            zones.append(None)
        except NoNodeError:
            zones = [None]
        return zones

    # Override JobRequestQueue methods to accomodate the zone dict.

    def inState(self, *states):
        requests = []
        for queue in self.zone_queues.values():
            requests.extend(queue.inState(*states))
        return sorted(requests)

    def next(self):
        yield from self.inState(BuildRequest.REQUESTED)

    def submit(self, request, params):
        return self.zone_queues[request.zone].submit(request, params)

    def update(self, request):
        return self.zone_queues[request.zone].update(request)

    def reportResult(self, request, result):
        return self.zone_queues[request.zone].reportResult(request)

    def get(self, path):
        if path.startswith(self.zones_root):
            # Remove zone root so we end up with: <zone>/requests/<uuid>
            rel_path = path[len(f"{self.zones_root}/"):]
            zone = rel_path.split("/")[0]
        else:
            zone = None
        return self.zone_queues[zone].get(path)

    def getByUuid(self, uuid):
        """Find a build request by its UUID.

        This method will search for the UUID in all available zones.
        """
        for zone in self._getAllZones():
            request = self.zone_queues[zone].getByUuid(uuid)
            if request:
                return request, zone
        return None, None

    def remove(self, request):
        return self.zone_queues[request.zone].remove(request)

    def requestResume(self, request):
        return self.zone_queues[request.zone].requestResume(request)

    def requestCancel(self, request):
        return self.zone_queues[request.zone].requestCancel(request)

    def fulfillResume(self, request):
        return self.zone_queues[request.zone].fulfillResume(request)

    def fulfillCancel(self, request):
        return self.zone_queues[request.zone].fulfillCancel(request)

    def lock(self, request, *args, **kw):
        return self.zone_queues[request.zone].lock(request, *args, **kw)

    def unlock(self, request):
        return self.zone_queues[request.zone].unlock(request)

    def isLocked(self, request):
        return self.zone_queues[request.zone].isLocked(request)

    def lostRequests(self):
        for queue in self.zone_queues.values():
            yield from queue.lostRequests()

    def cleanup(self, age=300):
        for queue in self.zone_queues.values():
            queue.cleanup(age)

    def clearParams(self, request):
        return self.zone_queues[request.zone].clearParams(request)

    def getParams(self, request):
        return self.zone_queues[request.zone].getParams(request)

    def _getAllRequestIds(self):
        ret = []
        for queue in self.zone_queues.values():
            ret.extend(queue._getAllRequestIds())
        return ret
