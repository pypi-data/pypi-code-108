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
import json
import logging
import threading
from collections import defaultdict

from kazoo.exceptions import NoNodeError
from kazoo.protocol.states import EventType

from zuul.zk import ZooKeeperBase


COMPONENTS_ROOT = "/zuul/components"


class BaseComponent(ZooKeeperBase):
    """
    Read/write component object.

    This object holds an offline cache of all the component's attributes. In
    case of an failed update to ZooKeeper the local cache will still hold the
    fresh values. Updating any attribute uploads all attributes to ZooKeeper.

    This enables this object to be used as local key/value store even if the
    ZooKeeper connection got lost.

    :arg client ZooKeeperClient: The Zuul ZooKeeperClient object to use, or
         None if this should be a read-only component.
    :arg hostname str: The component's hostname (multiple components with
         the same hostname may be registered; the registry will create unique
         nodes for each).
    """

    # Component states
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"

    log = logging.getLogger("zuul.Component")
    kind = "base"

    def __init__(self, client, hostname, version=None):
        # Ensure that the content is available before setting any other
        # attribute, because our __setattr__ implementation is relying on it.
        self.__dict__["content"] = {
            "hostname": hostname,
            "state": self.STOPPED,
            "kind": self.kind,
            "version": version,
        }
        super().__init__(client)

        self.path = None
        self._zstat = None
        self.register_lock = threading.Lock()

    def __getattr__(self, name):
        try:
            return self.content[name]
        except KeyError:
            raise AttributeError

    def __setattr__(self, name, value):
        # If the specified attribute is not part of our content dictionary,
        # fall back to the default __settattr__ behaviour.
        if name not in self.content.keys():
            return super().__setattr__(name, value)

        # Set the value in the local content dict
        self.content[name] = value

        with self.register_lock:
            if not self.path:
                self.log.error(
                    "Path is not set on this component, did you forget "
                    "to call register()?"
                )
                return

            # Update the ZooKeeper node
            content = json.dumps(self.content, sort_keys=True).encode("utf-8")
            try:
                zstat = self.kazoo_client.set(
                    self.path, content, version=self._zstat.version
                )
                self._zstat = zstat
            except NoNodeError:
                self.log.error("Could not update %s in ZooKeeper", self)

    def register(self):
        with self.register_lock:
            path = "/".join([COMPONENTS_ROOT, self.kind, self.hostname])
            self.log.info("Registering component in ZooKeeper %s", path)
            self.path, self._zstat = self.kazoo_client.create(
                path,
                json.dumps(self.content, sort_keys=True).encode("utf-8"),
                makepath=True,
                ephemeral=True,
                sequence=True,
                # Also return the zstat, which is necessary to successfully
                # update the component.
                include_data=True,
            )

    def _onReconnect(self):
        self.register()

    def updateFromDict(self, data):
        self.content.update(data)

    @classmethod
    def fromDict(cls, client, hostname, data):
        component = cls(client, hostname)
        component.updateFromDict(data)
        return component

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.content}>"


class SchedulerComponent(BaseComponent):
    kind = "scheduler"


class ExecutorComponent(BaseComponent):
    kind = "executor"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial_state = {
            "accepting_work": False,
            "zone": None,
            "allow_unzoned": False,
            "process_merge_jobs": False,
        }
        self.content.update(self.initial_state)


class MergerComponent(BaseComponent):
    kind = "merger"


class FingerGatewayComponent(BaseComponent):
    kind = "fingergw"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial_state = {
            "zone": None,
            "public_port": None,
            "use_ssl": False,
        }
        self.content.update(self.initial_state)


class WebComponent(BaseComponent):
    kind = "web"


class ComponentRegistry(ZooKeeperBase):
    """A component registry is organized like:

        /zuul/components/{kind}/{sequence}

    Where kind corresponds to one of the classes in this module, and
    sequence is a ZK sequence node with a prefix of the hostname in
    order to produce a unique id for multiple identical components
    running on the same host.  An example path:

        /zuul/components/scheduler/hostname0000000000

    Components are ephemeral nodes, and so if the actual service
    disconnects from ZK, the node will disappear.

    Component objects returned by this class are read-only; updating
    their attributes will not be reflected in ZooKeeper.
    """
    log = logging.getLogger("zuul.ComponentRegistry")

    COMPONENT_CLASSES = {
        "scheduler": SchedulerComponent,
        "executor": ExecutorComponent,
        "merger": MergerComponent,
        "fingergw": FingerGatewayComponent,
        "web": WebComponent,
    }

    def __init__(self, client):
        super().__init__(client)

        self.client = client
        self._component_tree = None
        # kind -> hostname -> component
        self._cached_components = defaultdict(dict)

        # If we are already connected when the class is instantiated, directly
        # call the onConnect callback.
        if self.client.connected:
            self._onConnect()

    def _getComponentRoot(self, kind):
        return '/'.join([COMPONENTS_ROOT, kind])

    def _getComponentPath(self, kind, hostname):
        return '/'.join([COMPONENTS_ROOT, kind, hostname])

    def _onConnect(self):
        for kind in self.COMPONENT_CLASSES.keys():
            root = self._getComponentRoot(kind)
            self.kazoo_client.ensure_path(root)
            self.kazoo_client.ChildrenWatch(
                root, self._makeComponentRootWatcher(kind))

    def _makeComponentRootWatcher(self, kind):
        def watch(children, event=None):
            return self._onComponentRootUpdate(kind, children, event)
        return watch

    def _onComponentRootUpdate(self, kind, children, event):
        for hostname in children:
            component = self._cached_components[kind].get(hostname)
            if not component:
                self.log.info("Noticed new %s component %s", kind, hostname)
                root = self._getComponentPath(kind, hostname)
                self.kazoo_client.DataWatch(
                    root, self._makeComponentWatcher(kind, hostname))

    def _makeComponentWatcher(self, kind, hostname):
        def watch(data, stat, event=None):
            return self._onComponentUpdate(kind, hostname, data, stat, event)
        return watch

    def _onComponentUpdate(self, kind, hostname, data, stat, event):
        if event:
            etype = event.type
        else:
            etype = None
        self.log.debug(
            "Registry %s got event %s for %s %s",
            self, etype, kind, hostname)
        if (etype in (None, EventType.CHANGED, EventType.CREATED) and
            data is not None):

            # Perform an in-place update of the cached component (if any)
            component = self._cached_components.get(kind, {}).get(hostname)
            d = json.loads(data.decode("utf-8"))

            self.log.info(
                "Component %s %s updated: %s",
                kind, hostname, d)

            if component:
                if (stat.version <= component._zstat.version):
                    # Don't update to older data
                    return
                component.updateFromDict(d)
                component._zstat = stat
            else:
                # Create a new component from the data structure
                # Get the correct kind of component
                # TODO (felix): KeyError on unknown component type?
                component_cls = self.COMPONENT_CLASSES[kind]
                # Pass in null ZK client to make a read-only component
                # instance.
                component = component_cls.fromDict(None, hostname, d)
                component.path = self._getComponentPath(kind, hostname)
                component._zstat = stat

            self._cached_components[kind][hostname] = component
        elif (etype == EventType.DELETED or data is None):
            self.log.info(
                "Noticed %s component %s disappeared",
                kind, hostname)
            try:
                del self._cached_components[kind][hostname]
            except KeyError:
                # If it's already gone, don't care
                pass
            # Return False to stop the datawatch
            return False

    def all(self, kind=None):
        """Returns a list of components.

        If kind is None, then a list of tuples is returned, with each tuple
        being (kind, [list of components]).

        :arg kind str: The type of component to look up in the registry, or
            None to return all kinds
        """

        if kind is None:
            return [(kind, list(components.values()))
                    for (kind, components) in self._cached_components.items()]

        # Filter the cached components for the given kind
        return self._cached_components.get(kind, {}).values()
