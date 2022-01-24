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
from enum import Enum
from typing import Optional, List
import threading

from kazoo.exceptions import NoNodeError, LockTimeout
from kazoo.recipe.cache import TreeCache, TreeEvent
from kazoo.recipe.lock import Lock

import zuul.model
from zuul.lib.jsonutil import json_dumps
from zuul.model import HoldRequest, NodeRequest, Node
from zuul.zk import ZooKeeperBase
from zuul.zk.exceptions import LockException


class NodeRequestEvent(Enum):
    COMPLETED = 0  # FULFILLED | FAILED
    DELETED = 2


class NodeEvent(Enum):
    CHANGED = 0
    DELETED = 2


class ZooKeeperNodepool(ZooKeeperBase):
    """
    Class implementing Nodepool related ZooKeeper interface.
    """
    NODES_ROOT = "/nodepool/nodes"
    LAUNCHER_ROOT = "/nodepool/launchers"
    REQUEST_ROOT = '/nodepool/requests'
    REQUEST_LOCK_ROOT = "/nodepool/requests-lock"
    HOLD_REQUEST_ROOT = '/zuul/hold-requests'

    log = logging.getLogger("zuul.zk.nodepool.ZooKeeperNodepool")

    def __init__(self, client,
                 enable_node_request_cache=False,
                 node_request_event_callback=None,
                 enable_node_cache=False):
        super().__init__(client)
        self.enable_node_request_cache = enable_node_request_cache
        self.node_request_event_callback = node_request_event_callback
        self.enable_node_cache = enable_node_cache
        # The caching model we use is designed around handing out model
        # data as objects. To do this, we use two caches: one is a TreeCache
        # which contains raw znode data (among other details), and one for
        # storing that data serialized as objects. This allows us to return
        # objects from the APIs, and avoids calling the methods to serialize
        # the data into objects more than once.
        self._node_request_tree = None
        self._node_request_cache = {}
        self._node_tree = None
        self._node_cache = {}
        self._callback_lock = threading.Lock()

        if self.client.connected:
            self._onConnect()

    def _onConnect(self):
        if self.enable_node_request_cache:
            self._node_request_tree = TreeCache(self.kazoo_client,
                                                self.REQUEST_ROOT)
            self._node_request_tree.listen_fault(self._cacheFaultListener)
            self._node_request_tree.listen(self.requestCacheListener)
            self._node_request_tree.start()
        if self.enable_node_cache:
            self._node_tree = TreeCache(self.kazoo_client,
                                        self.NODES_ROOT)
            self._node_tree.listen_fault(self._cacheFaultListener)
            self._node_tree.listen(self.nodeCacheListener)
            self._node_tree.start()

    def _onDisconnect(self):
        if self._node_request_tree is not None:
            self._node_request_tree.close()
            self._node_request_tree = None
        if self._node_tree is not None:
            self._node_tree.close()
            self._node_tree = None

    def _launcherPath(self, launcher):
        return "%s/%s" % (self.LAUNCHER_ROOT, launcher)

    def _nodePath(self, node):
        return "%s/%s" % (self.NODES_ROOT, node)

    def _cacheFaultListener(self, e):
        self.log.exception(e)

    def register(self):
        self.kazoo_client.ensure_path(self.REQUEST_ROOT)

    def getRegisteredLaunchers(self):
        """
        Get a list of all launchers that have registered with ZooKeeper.

        :returns: A list of Launcher objects, or empty list if none are found.
        """
        try:
            launcher_ids = self.kazoo_client\
                .get_children(self.LAUNCHER_ROOT)
        except NoNodeError:
            return []

        objs = []
        for launcher in launcher_ids:
            path = self._launcherPath(launcher)
            try:
                data, _ = self.kazoo_client.get(path)
            except NoNodeError:
                # launcher disappeared
                continue

            objs.append(Launcher.fromDict(json.loads(data.decode('utf8'))))
        return objs

    def getNodes(self, cached=False):
        """
        Get the current list of all node ids.

        :param bool cached: Whether to use the internal cache to get the list
            of ids.
        :returns: A list of node ids.
        """
        if cached and self.enable_node_cache:
            return list(self._node_cache.keys())
        else:
            try:
                return self.kazoo_client.get_children(self.NODES_ROOT)
            except NoNodeError:
                return []

    def _getNodeData(self, node):
        """
        Get the data for a specific node.

        :param str node: The node ID.

        :returns: The node data, or None if the node was not found.
        """
        path = self._nodePath(node)
        try:
            data, stat = self.kazoo_client.get(path)
        except NoNodeError:
            return None
        if not data:
            return None

        d = json.loads(data.decode('utf8'))
        d['id'] = node
        return d

    def getNode(self, node_id):
        """
        Get a Node object for a specific node.

        :param str node_id: The node ID.

        :returns: The Node, or None if the node was not found.
        """
        node = self._node_cache.get(node_id)
        if node:
            return node

        path = self._nodePath(node_id)
        try:
            data, stat = self.kazoo_client.get(path)
        except NoNodeError:
            return None
        if not data:
            return None

        node = Node(None, None)
        node.updateFromDict(data)
        node.id = node_id
        node.stat = stat
        return node

    def nodeIterator(self):
        """
        Utility generator method for iterating through all nodes.
        """
        for node_id in self.getNodes():
            node = self.getNode(node_id)
            if node:
                yield node

    def getHoldRequests(self):
        """
        Get the current list of all hold requests.
        """

        try:
            return sorted(self.kazoo_client
                          .get_children(self.HOLD_REQUEST_ROOT))
        except NoNodeError:
            return []

    def getHoldRequest(self, hold_request_id):
        # To be friendly, zero pad if this request came from a client
        # call, where the user might have done "zuul autohold-delete
        # 123" thinking that would match the "0000000123" shown in
        # "autohold-list".
        #
        #  "A sequential node will be given the specified path plus a
        #  suffix i where i is the current sequential number of the
        #  node. The sequence number is always fixed length of 10
        #  digits, 0 padded. Once such a node is created, the
        #  sequential number will be incremented by one."
        if len(hold_request_id) != 10:
            hold_request_id = hold_request_id.rjust(10, '0')

        path = self.HOLD_REQUEST_ROOT + "/" + hold_request_id
        try:
            data, stat = self.kazoo_client.get(path)
        except NoNodeError:
            return None
        if not data:
            return None

        obj = HoldRequest.fromDict(json.loads(data.decode('utf8')))
        obj.id = hold_request_id
        obj.stat = stat
        return obj

    def storeHoldRequest(self, request: HoldRequest):
        """
        Create or update a hold request.

        If this is a new request with no value for the `id` attribute of the
        passed in request, then `id` will be set with the unique request
        identifier after successful creation.

        :param HoldRequest request: Object representing the hold request.
        """
        if request.id is None:
            path = self.kazoo_client.create(
                self.HOLD_REQUEST_ROOT + "/",
                value=request.serialize(),
                sequence=True,
                makepath=True)
            request.id = path.split('/')[-1]
        else:
            path = self.HOLD_REQUEST_ROOT + "/" + request.id
            self.kazoo_client.set(path, request.serialize())

    def _markHeldNodesAsUsed(self, request: HoldRequest):
        """
        Changes the state for each held node for the hold request to 'used'.

        :returns: True if all nodes marked USED, False otherwise.
        """
        def getHeldNodeIDs(req: HoldRequest) -> List[str]:
            node_ids: List[str] = []
            for data in req.nodes:
                # TODO(Shrews): Remove type check at some point.
                # When autoholds were initially changed to be stored in ZK,
                # the node IDs were originally stored as a list of strings.
                # A later change embedded them within a dict. Handle both
                # cases here to deal with the upgrade.
                if isinstance(data, dict):
                    node_ids += data['nodes']
                else:
                    node_ids.append(data)
            return node_ids

        failure = False
        for node_id in getHeldNodeIDs(request):
            node = self._getNodeData(node_id)
            if not node or node['state'] == zuul.model.STATE_USED:
                continue

            node['state'] = zuul.model.STATE_USED

            name = None
            label = None
            if 'name' in node:
                name = node['name']
            if 'label' in node:
                label = node['label']

            node_obj = zuul.model.Node(name, label)
            node_obj.updateFromDict(node)

            try:
                self.lockNode(node_obj, blocking=False)
                self.storeNode(node_obj)
            except Exception:
                self.log.exception("Cannot change HELD node state to USED "
                                   "for node %s in request %s",
                                   node_obj.id, request.id)
                failure = True
            finally:
                try:
                    if node_obj.lock:
                        self.unlockNode(node_obj)
                except Exception:
                    self.log.exception(
                        "Failed to unlock HELD node %s for request %s",
                        node_obj.id, request.id)

        return not failure

    def deleteHoldRequest(self, request: HoldRequest):
        """
        Delete a hold request.

        :param HoldRequest request: Object representing the hold request.
        """
        if not self._markHeldNodesAsUsed(request):
            self.log.info("Unable to delete hold request %s because "
                          "not all nodes marked as USED.", request.id)
            return

        path = self.HOLD_REQUEST_ROOT + "/" + request.id
        try:
            self.kazoo_client.delete(path, recursive=True)
        except NoNodeError:
            pass

    def lockHoldRequest(self, request: HoldRequest,
                        blocking: bool = True, timeout: Optional[int] = None):
        """
        Lock a node request.

        This will set the `lock` attribute of the request object when the
        lock is successfully acquired.

        :param request: The hold request to lock.
        :param blocking: Block until lock is obtained or return immediately.
        :param timeout: Don't wait forever to acquire the lock.
        """
        if not request.id:
            raise LockException(
                "Hold request without an ID cannot be locked: %s" % request)

        path = "%s/%s/lock" % (self.HOLD_REQUEST_ROOT, request.id)
        try:
            lock = Lock(self.kazoo_client, path)
            have_lock = lock.acquire(blocking, timeout)
        except LockTimeout:
            raise LockException("Timeout trying to acquire lock %s" % path)

        # If we aren't blocking, it's possible we didn't get the lock
        # because someone else has it.
        if not have_lock:
            raise LockException("Did not get lock on %s" % path)

        request.lock = lock

    def unlockHoldRequest(self, request: HoldRequest):
        """
        Unlock a hold request.

        The request must already have been locked.

        :param HoldRequest request: The request to unlock.

        :raises: ZKLockException if the request is not currently locked.
        """
        if request.lock is None:
            raise LockException("Request %s does not hold a lock" % request)
        request.lock.release()
        request.lock = None

    def requestCacheListener(self, event):
        try:
            # This lock is only needed for tests.  It wraps updating
            # our internal cache and performing the callback which
            # will generate node provisioned events in a critical
            # section.  This way the tests know if a request is
            # outstanding because either our cache is out of date or
            # there is an event on the queue.
            with self._callback_lock:
                self._requestCacheListener(event)
        except Exception:
            self.log.exception(
                "Exception in request cache update for event: %s",
                event)

    def _requestCacheListener(self, event):
        if hasattr(event.event_data, 'path'):
            # Ignore root node
            path = event.event_data.path
            if path == self.REQUEST_ROOT:
                return

            # Ignore lock nodes
            if '/lock' in path:
                return

        # Ignore any non-node related events such as connection events here
        if event.event_type not in (TreeEvent.NODE_ADDED,
                                    TreeEvent.NODE_UPDATED,
                                    TreeEvent.NODE_REMOVED):
            return

        path = event.event_data.path
        request_id = path.rsplit('/', 1)[1]

        if event.event_type in (TreeEvent.NODE_ADDED, TreeEvent.NODE_UPDATED):
            # Requests with empty data are invalid so skip add or update these.
            if not event.event_data.data:
                return

            # Perform an in-place update of the cached request if possible
            d = self._bytesToDict(event.event_data.data)
            request = self._node_request_cache.get(request_id)
            if request:
                if event.event_data.stat.version <= request.stat.version:
                    # Don't update to older data
                    return
                old_state = request.state
                request.updateFromDict(d)
                request.stat = event.event_data.stat
            else:
                old_state = None
                request = NodeRequest.fromDict(d)
                request.id = request_id
                request.stat = event.event_data.stat
                self._node_request_cache[request_id] = request

            if (request.state in {zuul.model.STATE_FULFILLED,
                                  zuul.model.STATE_FAILED}
                and request.state != old_state
                and self.node_request_event_callback):
                self.node_request_event_callback(
                    request, NodeRequestEvent.COMPLETED)

        elif event.event_type == TreeEvent.NODE_REMOVED:
            request = self._node_request_cache.pop(request_id)
            if self.node_request_event_callback:
                self.node_request_event_callback(
                    request, NodeRequestEvent.DELETED)

    def submitNodeRequest(self, node_request, priority):
        """
        Submit a request for nodes to Nodepool.

        :param NodeRequest node_request: A NodeRequest with the
            contents of the request.
        """
        node_request.created_time = time.time()
        data = node_request.toDict()

        path = '{}/{:0>3}-'.format(self.REQUEST_ROOT, priority)
        path = self.kazoo_client.create(path, json.dumps(data).encode('utf8'),
                                        makepath=True, sequence=True)
        reqid = path.split("/")[-1]
        node_request.id = reqid

    def getNodeRequests(self, cached=False):
        '''
        Get the current list of all node request IDs in priority sorted order.

        :param bool cached: Whether to use the internal cache to get the list
            of ids.
        :returns: A list of request ids.
        '''
        if cached and self.enable_node_request_cache:
            requests = self._node_request_cache.keys()
        else:
            try:
                requests = self.kazoo_client.get_children(self.REQUEST_ROOT)
            except NoNodeError:
                return []

        return sorted(requests)

    def getNodeRequest(self, node_request_id, cached=False):
        """
        Retrieve a NodeRequest from a given path in ZooKeeper.

        :param str node_request_id: The ID of the node request to retrieve.
        :param bool cached: Whether to use the cache.
        """
        if cached:
            req = self._node_request_cache.get(node_request_id)
            if req:
                return req

        path = f"{self.REQUEST_ROOT}/{node_request_id}"
        try:
            data, stat = self.kazoo_client.get(path)
        except NoNodeError:
            return None

        if not data:
            return None

        json_data = json.loads(data.decode("utf-8"))

        obj = NodeRequest.fromDict(json_data)
        obj.id = node_request_id
        obj.stat = stat
        return obj

    def deleteNodeRequest(self, node_request_id):
        """
        Delete a request for nodes.

        :param str node_request_id: The node request ID.

        :returns: True if the request was deleted, False if it did not exist.
        """
        path = '%s/%s' % (self.REQUEST_ROOT, node_request_id)
        try:
            self.kazoo_client.delete(path)
            return True
        except NoNodeError:
            return False

    def nodeRequestExists(self, node_request):
        """
        See if a NodeRequest exists in ZooKeeper.

        :param NodeRequest node_request: A NodeRequest to verify.

        :returns: True if the request exists, False otherwise.
        """
        path = '%s/%s' % (self.REQUEST_ROOT, node_request.id)
        if self.kazoo_client.exists(path):
            return True
        return False

    def storeNodeRequest(self, node_request):
        """
        Store the node request.

        The request is expected to already exist and is updated in its
        entirety.

        :param NodeRequest node_request: The request to update.
        """
        path = '%s/%s' % (self.REQUEST_ROOT, node_request.id)
        self.kazoo_client.set(
            path, json.dumps(node_request.toDict()).encode('utf8'),
            version=node_request.stat.version)

    def updateNodeRequest(self, node_request, data=None):
        """
        Refresh an existing node request.

        :param NodeRequest node_request: The request to update.
        :param dict data: The data to use; query ZK if absent.
        """
        if data is None:
            path = '%s/%s' % (self.REQUEST_ROOT, node_request.id)
            data, stat = self.kazoo_client.get(path)
        data = json.loads(data.decode('utf8'))
        node_request.updateFromDict(data)

    def nodeCacheListener(self, event):
        try:
            self._nodeCacheListener(event)
        except Exception:
            self.log.exception(
                "Exception in node cache update for event: %s",
                event)

    def _nodeCacheListener(self, event):
        if hasattr(event.event_data, 'path'):
            # Ignore root node
            path = event.event_data.path
            if path == self.NODES_ROOT:
                return

            # Ignore lock nodes
            if '/lock' in path:
                return

        # Ignore any non-node related events such as connection events here
        if event.event_type not in (TreeEvent.NODE_ADDED,
                                    TreeEvent.NODE_UPDATED,
                                    TreeEvent.NODE_REMOVED):
            return

        path = event.event_data.path
        node_id = path.rsplit('/', 1)[1]

        if event.event_type in (TreeEvent.NODE_ADDED, TreeEvent.NODE_UPDATED):
            # Nodes with empty data are invalid so skip add or update these.
            if not event.event_data.data:
                return

            # Perform an in-place update of the cached node if possible
            d = self._bytesToDict(event.event_data.data)
            node = self._node_cache.get(node_id)
            if node:
                if event.event_data.stat.version <= node.stat.version:
                    # Don't update to older data
                    return
                node.updateFromDict(d)
                node.stat = event.event_data.stat
            else:
                node = Node(None, None)
                node.updateFromDict(d)
                node.id = node_id
                node.stat = event.event_data.stat
                self._node_cache[node_id] = node

        elif event.event_type == TreeEvent.NODE_REMOVED:
            node = self._node_cache.pop(node_id)

    def storeNode(self, node):
        """
        Store the node.

        The node is expected to already exist and is updated in its
        entirety.

        :param Node node: The node to update.
        """
        path = '%s/%s' % (self.NODES_ROOT, node.id)
        self.kazoo_client.set(path, json.dumps(node.toDict()).encode('utf8'))

    def updateNode(self, node, node_id):
        """
        Refresh an existing node.

        :param Node node: The node to update.

        :param str node_id: The ID of the node to update.  The
            existing node.id attribute (if any) will be ignored
            and replaced with this.
        """
        node_path = '%s/%s' % (self.NODES_ROOT, node_id)
        node.id = node_id
        node_data, node_stat = self.kazoo_client.get(node_path)
        node_data = json.loads(node_data.decode('utf8'))
        node.updateFromDict(node_data)

    def lockNode(self, node, blocking=True, timeout=None):
        """
        Lock a node.

        This should be called as soon as a request is fulfilled and
        the lock held for as long as the node is in-use.  It can be
        used by nodepool to detect if Zuul has gone offline and the
        node should be reclaimed.

        :param Node node: The node which should be locked.
        """
        lock_path = '%s/%s/lock' % (self.NODES_ROOT, node.id)
        try:
            lock = Lock(self.kazoo_client, lock_path)
            have_lock = lock.acquire(blocking, timeout)
        except LockTimeout:
            raise LockException(
                "Timeout trying to acquire lock %s" % lock_path)

        # If we aren't blocking, it's possible we didn't get the lock
        # because someone else has it.
        if not have_lock:
            raise LockException("Did not get lock on %s" % lock_path)

        node.lock = lock

    def unlockNode(self, node):
        """
        Unlock a node.

        The node must already have been locked.

        :param Node node: The node which should be unlocked.
        """

        if node.lock is None:
            raise LockException(f"Node {node} does not hold a lock")
        node.lock.release()
        node.lock = None

    def lockNodeRequest(self, request, blocking=True, timeout=None):
        """
        Lock a node request.

        This will set the `lock` attribute of the request object when the
        lock is successfully acquired.

        :param NodeRequest request: The request to lock.
        :param bool blocking: Whether or not to block on trying to
            acquire the lock
        :param int timeout: When blocking, how long to wait for the lock
            to get acquired. None, the default, waits forever.

        :raises: TimeoutException if we failed to acquire the lock when
            blocking with a timeout. ZKLockException if we are not blocking
            and could not get the lock, or a lock is already held.
        """
        path = "%s/%s" % (self.REQUEST_LOCK_ROOT, request.id)
        lock = Lock(self.kazoo_client, path)
        try:
            have_lock = lock.acquire(blocking, timeout)
        except LockTimeout:
            raise LockException(
                "Timeout trying to acquire lock %s" % path)
        except NoNodeError:
            have_lock = False
            self.log.error("Request not found for locking: %s", request)

        # If we aren't blocking, it's possible we didn't get the lock
        # because someone else has it.
        if not have_lock:
            raise LockException("Did not get lock on %s" % path)

        request.lock = lock

    def unlockNodeRequest(self, request):
        """
        Unlock a node request.

        The request must already have been locked.

        :param NodeRequest request: The request to unlock.

        :raises: ZKLockException if the request is not currently locked.
        """
        if request.lock is None:
            raise LockException(
                "Request %s does not hold a lock" % request)
        request.lock.release()
        request.lock = None

    def heldNodeCount(self, autohold_key):
        """
        Count the number of nodes being held for the given tenant/project/job.

        :param set autohold_key: A set with the tenant/project/job names.
        """
        identifier = " ".join(autohold_key)
        try:
            nodes = self.kazoo_client.get_children(self.NODES_ROOT)
        except NoNodeError:
            return 0

        count = 0
        for nodeid in nodes:
            node_path = '%s/%s' % (self.NODES_ROOT, nodeid)
            try:
                node_data, node_stat = self.kazoo_client.get(node_path)
            except NoNodeError:
                # Node got removed on us. Just ignore.
                continue

            if not node_data:
                self.log.warning("Node ID %s has no data", nodeid)
                continue
            node_data = json.loads(node_data.decode('utf8'))
            if (node_data['state'] == zuul.model.STATE_HOLD and
                    node_data.get('hold_job') == identifier):
                count += 1
        return count

    @staticmethod
    def _bytesToDict(data):
        return json.loads(data.decode("utf-8"))

    @staticmethod
    def _dictToBytes(data):
        # The custom json_dumps() will also serialize MappingProxyType objects
        return json_dumps(data).encode("utf-8")


class Launcher:
    """
    Class to describe a nodepool launcher.
    """

    def __init__(self):
        self.id = None
        self._supported_labels = set()

    def __eq__(self, other):
        if isinstance(other, Launcher):
            return (self.id == other.id and
                    self.supported_labels == other.supported_labels)
        else:
            return False

    @property
    def supported_labels(self):
        return self._supported_labels

    @supported_labels.setter
    def supported_labels(self, value):
        if not isinstance(value, set):
            raise TypeError("'supported_labels' attribute must be a set")
        self._supported_labels = value

    @staticmethod
    def fromDict(d):
        obj = Launcher()
        obj.id = d.get('id')
        obj.supported_labels = set(d.get('supported_labels', []))
        return obj
