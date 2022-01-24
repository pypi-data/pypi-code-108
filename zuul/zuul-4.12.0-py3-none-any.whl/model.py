# Copyright 2012 Hewlett-Packard Development Company, L.P.
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

import abc
from collections import OrderedDict, defaultdict, namedtuple, UserDict
import copy
import json
import hashlib
import logging
import os
from functools import total_ordering

import re2
import time
from uuid import uuid4
import urllib.parse
import textwrap
import types
import itertools

from kazoo.exceptions import NoNodeError, ZookeeperError
from cachetools.func import lru_cache

from zuul.lib import yamlutil as yaml
from zuul.lib.varnames import check_varnames

import jsonpath_rw

from zuul import change_matcher
from zuul.lib.config import get_default
from zuul.lib.result_data import get_artifacts_from_result_data
from zuul.lib.logutil import get_annotated_logger
from zuul.lib.capabilities import capabilities_registry
from zuul.lib.jsonutil import json_dumps
from zuul.zk import zkobject
from zuul.zk.change_cache import ChangeKey

MERGER_MERGE = 1          # "git merge"
MERGER_MERGE_RESOLVE = 2  # "git merge -s resolve"
MERGER_CHERRY_PICK = 3    # "git cherry-pick"
MERGER_SQUASH_MERGE = 4    # "git merge --squash"

MERGER_MAP = {
    'merge': MERGER_MERGE,
    'merge-resolve': MERGER_MERGE_RESOLVE,
    'cherry-pick': MERGER_CHERRY_PICK,
    'squash-merge': MERGER_SQUASH_MERGE,
}

PRECEDENCE_NORMAL = 0
PRECEDENCE_LOW = 1
PRECEDENCE_HIGH = 2

PRECEDENCE_MAP = {
    None: PRECEDENCE_NORMAL,
    'low': PRECEDENCE_LOW,
    'normal': PRECEDENCE_NORMAL,
    'high': PRECEDENCE_HIGH,
}

PRIORITY_MAP = {
    PRECEDENCE_NORMAL: 200,
    PRECEDENCE_LOW: 300,
    PRECEDENCE_HIGH: 100,
}

# Request states
STATE_REQUESTED = 'requested'
STATE_FULFILLED = 'fulfilled'
STATE_FAILED = 'failed'
REQUEST_STATES = set([STATE_REQUESTED,
                      STATE_FULFILLED,
                      STATE_FAILED])

# Node states
STATE_BUILDING = 'building'
STATE_TESTING = 'testing'
STATE_READY = 'ready'
STATE_IN_USE = 'in-use'
STATE_USED = 'used'
STATE_HOLD = 'hold'
STATE_DELETING = 'deleting'
NODE_STATES = set([STATE_BUILDING,
                   STATE_TESTING,
                   STATE_READY,
                   STATE_IN_USE,
                   STATE_USED,
                   STATE_HOLD,
                   STATE_DELETING])

# Workspace scheme
SCHEME_GOLANG = 'golang'
SCHEME_FLAT = 'flat'
SCHEME_UNIQUE = 'unique'  # Internal use only


def add_debug_line(debug_messages, msg, indent=0):
    if debug_messages is None:
        return
    if indent:
        indent = '  ' * indent
    else:
        indent = ''
    debug_messages.append(indent + msg)


class ZuulMark:
    # The yaml mark class differs between the C and python versions.
    # The C version does not provide a snippet, and also appears to
    # lose data under some circumstances.
    def __init__(self, start_mark, end_mark, stream):
        self.name = start_mark.name
        self.index = start_mark.index
        self.line = start_mark.line
        self.end_line = end_mark.line
        self.end_index = end_mark.index
        self.column = start_mark.column
        self.end_column = end_mark.column
        self.snippet = stream[start_mark.index:end_mark.index]

    def __str__(self):
        return '  in "{name}", line {line}, column {column}'.format(
            name=self.name,
            line=self.line + 1,
            column=self.column + 1,
        )

    def __eq__(self, other):
        return (self.line == other.line and
                self.snippet == other.snippet)

    def serialize(self):
        return {
            "name": self.name,
            "index": self.index,
            "line": self.line,
            "end_line": self.end_line,
            "end_index": self.end_index,
            "column": self.column,
            "end_column": self.end_column,
            "snippet": self.snippet,
        }

    @classmethod
    def deserialize(cls, data):
        o = cls.__new__(cls)
        o.__dict__.update(data)
        return o


class ConfigurationErrorKey(object):
    """A class which attempts to uniquely identify configuration errors
    based on their file location.  It's not perfect, but it's usually
    sufficient to determine whether we should show an error to a user.
    """

    def __init__(self, context, mark, error_text):
        self.context = context
        self.mark = mark
        self.error_text = error_text
        elements = []
        if context:
            elements.extend([
                context.project_canonical_name,
                context.branch,
                context.path,
            ])
        else:
            elements.extend([None, None, None])
        if mark:
            elements.extend([
                mark.line,
                mark.snippet,
            ])
        else:
            elements.extend([None, None])
        elements.append(error_text)

        hasher = hashlib.sha256()
        hasher.update(json.dumps(elements, sort_keys=True).encode('utf8'))
        self._hash = hasher.hexdigest()

    def serialize(self):
        return {
            "context": self.context and self.context.serialize(),
            "mark": self.mark and self.mark.serialize(),
            "error_text": self.error_text,
            "_hash": self._hash,
        }

    @classmethod
    def deserialize(cls, data):
        data.update({
            "context": data["context"] and SourceContext.deserialize(
                data["context"]),
            "mark": data["mark"] and ZuulMark.deserialize(data["mark"]),
        })
        o = cls.__new__(cls)
        o.__dict__.update(data)
        return o

    def __hash__(self):
        return hash(self._hash)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        if not isinstance(other, ConfigurationErrorKey):
            return False
        return (self.context == other.context and
                self.mark == other.mark and
                self.error_text == other.error_text)


class ConfigurationError(object):

    """A configuration error"""
    def __init__(self, context, mark, error, short_error=None):
        self.error = str(error)
        self.short_error = short_error
        self.key = ConfigurationErrorKey(context, mark, self.error)

    def serialize(self):
        return {
            "error": self.error,
            "short_error": self.short_error,
            "key": self.key.serialize()
        }

    @classmethod
    def deserialize(cls, data):
        data["key"] = ConfigurationErrorKey.deserialize(data["key"])
        o = cls.__new__(cls)
        o.__dict__.update(data)
        return o

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        if not isinstance(other, ConfigurationError):
            return False
        return (self.error == other.error and
                self.short_error == other.short_error and
                self.key == other.key)


class ConfigurationErrorList(zkobject.ShardedZKObject):
    """A list of configuration errors.

    BuildSets may have zero or one of these.
    """

    def __repr__(self):
        return '<ConfigurationErrorList>'

    def getPath(self):
        return self._path

    def serialize(self):
        data = {
            "errors": [e.serialize() for e in self.errors],
        }
        return json.dumps(data, sort_keys=True).encode("utf8")

    def deserialize(self, raw, context):
        data = super().deserialize(raw, context)
        data.update({
            "errors": [ConfigurationError.deserialize(d)
                       for d in data["errors"]],
        })
        return data


class LoadingErrors(object):
    """A configuration errors accumalator attached to a layout object
    """
    def __init__(self):
        self.errors = []
        self.error_keys = set()

    def addError(self, context, mark, error, short_error=None):
        e = ConfigurationError(context, mark, error, short_error)
        self.errors.append(e)
        self.error_keys.add(e.key)

    def __getitem__(self, index):
        return self.errors[index]

    def __len__(self):
        return len(self.errors)


class NoMatchingParentError(Exception):
    """A job referenced a parent, but that parent had no variants which
    matched the current change."""
    pass


class TemplateNotFoundError(Exception):
    """A project referenced a template that does not exist."""
    pass


class RequirementsError(Exception):
    """A job's requirements were not met."""
    pass


class Attributes(object):
    """A class to hold attributes for string formatting."""

    def __init__(self, **kw):
        setattr(self, '__dict__', kw)


class Freezable(object):
    """A mix-in class so that an object can be made immutable"""

    def __init__(self):
        super(Freezable, self).__setattr__('_frozen', False)

    def freeze(self):
        """Make this object immutable"""
        def _freezelist(l):
            for i, v in enumerate(l):
                if isinstance(v, Freezable):
                    if not v._frozen:
                        v.freeze()
                elif isinstance(v, dict):
                    l[i] = _freezedict(v)
                elif isinstance(v, list):
                    l[i] = _freezelist(v)
            return tuple(l)

        def _freezedict(d):
            for k, v in list(d.items()):
                if isinstance(v, Freezable):
                    if not v._frozen:
                        v.freeze()
                elif isinstance(v, dict):
                    d[k] = _freezedict(v)
                elif isinstance(v, list):
                    d[k] = _freezelist(v)
            return types.MappingProxyType(d)

        _freezedict(self.__dict__)
        # Ignore return value from freezedict because __dict__ can't
        # be a mappingproxy.
        self._frozen = True

    @staticmethod
    def thaw(data):
        """Thaw the supplied dictionary"""
        def _thawlist(l):
            l = list(l)
            for i, v in enumerate(l):
                if isinstance(v, (types.MappingProxyType, dict)):
                    l[i] = _thawdict(v)
                elif isinstance(v, (tuple, list)):
                    l[i] = _thawlist(v)
            return l

        def _thawdict(d):
            d = dict(d)
            for k, v in list(d.items()):
                if isinstance(v, (types.MappingProxyType, dict)):
                    d[k] = _thawdict(v)
                elif isinstance(v, (tuple, list)):
                    d[k] = _thawlist(v)
            return d

        return _thawdict(data)

    def __setattr__(self, name, value):
        if self._frozen:
            raise Exception("Unable to modify frozen object %s" %
                            (repr(self),))
        super(Freezable, self).__setattr__(name, value)


class ConfigObject(Freezable):
    def __init__(self):
        super().__init__()
        self.source_context = None
        self.start_mark = None


class Pipeline(object):
    """A configuration that ties together triggers, reporters and managers

    Trigger
        A description of which events should be processed

    Manager
        Responsible for enqueing and dequeing Changes

    Reporter
        Communicates success and failure results somewhere
    """
    STATE_NORMAL = 'normal'
    STATE_ERROR = 'error'

    def __init__(self, name, tenant):
        self.name = name
        # Note that pipelines are not portable across tenants (new
        # pipeline objects must be made when a tenant is
        # reconfigured).  A pipeline requires a tenant in order to
        # reach the currently active layout for that tenant.
        self.tenant = tenant
        self.source_context = None
        self.start_mark = None
        self.description = None
        self.failure_message = None
        self.merge_failure_message = None
        self.success_message = None
        self.footer_message = None
        self.enqueue_message = None
        self.start_message = None
        self.dequeue_message = None
        self.post_review = False
        self.dequeue_on_new_patchset = True
        self.ignore_dependencies = False
        self.manager = None
        self.precedence = PRECEDENCE_NORMAL
        self.supercedes = []
        self.triggers = []
        self.enqueue_actions = []
        self.start_actions = []
        self.success_actions = []
        self.failure_actions = []
        self.merge_failure_actions = []
        self.no_jobs_actions = []
        self.disabled_actions = []
        self.dequeue_actions = []
        self.disable_at = None
        self.window = None
        self.window_floor = None
        self.window_increase_type = None
        self.window_increase_factor = None
        self.window_decrease_type = None
        self.window_decrease_factor = None
        self.state = None
        self.change_list = None

    @property
    def queues(self):
        return self.state.queues

    @property
    def relative_priority_queues(self):
        return self.state.relative_priority_queues

    @property
    def actions(self):
        return (
            self.enqueue_actions +
            self.start_actions +
            self.success_actions +
            self.failure_actions +
            self.merge_failure_actions +
            self.no_jobs_actions +
            self.disabled_actions +
            self.dequeue_actions
        )

    def __repr__(self):
        return '<Pipeline %s>' % self.name

    def getSafeAttributes(self):
        return Attributes(name=self.name)

    def validateReferences(self, layout):
        # Verify that references to other objects in the layout are
        # valid.

        for pipeline in self.supercedes:
            if not layout.pipelines.get(pipeline):
                raise Exception(
                    'The pipeline "{this}" supercedes an unknown pipeline '
                    '{other}.'.format(
                        this=self.name,
                        other=pipeline))

    def setManager(self, manager):
        self.manager = manager

    def addQueue(self, queue):
        with self.state.activeContext(self.manager.current_context):
            self.queues.append(queue)

    def getQueue(self, project_cname, branch):
        # Queues might be branch specific so match with branch
        for queue in self.queues:
            if queue.matches(project_cname, branch):
                return queue
        return None

    def getRelativePriorityQueue(self, project):
        for queue in self.relative_priority_queues.values():
            if project in queue:
                return queue
        return [project]

    def setRelativePriorityQueues(self, queues):
        self.state.updateAttributes(self.manager.current_context,
                                    relative_priority_queues=queues)

    def removeQueue(self, queue):
        if queue in self.queues:
            with self.state.activeContext(self.manager.current_context):
                self.queues.remove(queue)
            queue.delete(self.manager.current_context)

    def getChangesInQueue(self):
        changes = []
        for shared_queue in self.queues:
            changes.extend([x.change for x in shared_queue.queue])
        return changes

    def getAllItems(self, include_old=False):
        items = []
        for shared_queue in self.queues:
            items.extend(shared_queue.queue)
        if include_old:
            for shared_queue in self.state.old_queues:
                items.extend(shared_queue.queue)
        return items

    def formatStatusJSON(self, websocket_url=None):
        j_pipeline = dict(name=self.name,
                          description=self.description,
                          state=self.state.state,
                          manager=self.manager.type)
        j_pipeline['triggers'] = [
            {'driver': t.driver.name} for t in self.triggers
        ]
        j_queues = []
        j_pipeline['change_queues'] = j_queues
        for queue in self.queues:
            j_queue = dict(name=queue.name)
            j_queues.append(j_queue)
            j_queue['heads'] = []
            j_queue['window'] = queue.window

            if queue.project_branches and queue.project_branches[0][1]:
                j_queue['branch'] = queue.project_branches[0][1]
            else:
                j_queue['branch'] = None

            j_changes = []
            for e in queue.queue:
                if not e.item_ahead:
                    if j_changes:
                        j_queue['heads'].append(j_changes)
                    j_changes = []
                j_changes.append(e.formatJSON(websocket_url))
                if (len(j_changes) > 1 and
                        (j_changes[-2]['remaining_time'] is not None) and
                        (j_changes[-1]['remaining_time'] is not None)):
                    j_changes[-1]['remaining_time'] = max(
                        j_changes[-2]['remaining_time'],
                        j_changes[-1]['remaining_time'])
            if j_changes:
                j_queue['heads'].append(j_changes)
        return j_pipeline


class PipelineState(zkobject.ZKObject):

    def __init__(self):
        super().__init__()
        self._set(**self.defaultState())

    @classmethod
    def defaultState(cls):
        return dict(
            state=Pipeline.STATE_NORMAL,
            queues=[],
            old_queues=[],
            relative_priority_queues={},
            consecutive_failures=0,
            disabled=False,
            pipeline=None,
            layout_uuid=None,
        )

    @classmethod
    def fromZK(klass, context, path, pipeline, **kw):
        obj = klass()
        obj._set(pipeline=pipeline, **kw)
        # Bind the state to the pipeline, so child objects can access
        # the the full pipeline state.
        pipeline.state = obj
        obj._load(context, path=path)
        return obj

    @classmethod
    def resetOrCreate(cls, pipeline, layout_uuid):
        ctx = pipeline.manager.current_context
        try:
            state = cls.fromZK(ctx, cls.pipelinePath(pipeline),
                               pipeline=pipeline)
            if state.layout_uuid != layout_uuid:
                reset_state = {
                    **cls.defaultState(),
                    "layout_uuid": layout_uuid,
                    "pipeline": pipeline,
                    "old_queues": state.old_queues + state.queues,
                }
                state.updateAttributes(ctx, **reset_state)
            return state
        except NoNodeError:
            return cls.new(ctx, pipeline=pipeline, layout_uuid=layout_uuid)

    def getPath(self):
        return self.pipelinePath(self.pipeline)

    @classmethod
    def pipelinePath(cls, pipeline):
        safe_tenant = urllib.parse.quote_plus(pipeline.tenant.name)
        safe_pipeline = urllib.parse.quote_plus(pipeline.name)
        return f"/zuul/tenant/{safe_tenant}/pipeline/{safe_pipeline}"

    def setOldQueues(self, context, queues):
        old_queues = []
        for queue in queues:
            queue._set(pipeline=self.pipeline)
            for item in queue.queue:
                item._set(pipeline=self.pipeline)
            old_queues.append(queue)

        self.updateAttributes(context, old_queues=old_queues)

    def removeOldQueue(self, context, queue):
        if queue in self.old_queues:
            with self.activeContext(context):
                self.old_queues.remove(queue)

    def serialize(self):
        data = {
            "state": self.state,
            "consecutive_failures": self.consecutive_failures,
            "disabled": self.disabled,
            "queues": [q.getPath() for q in self.queues],
            "old_queues": [q.getPath() for q in self.old_queues],
            "layout_uuid": self.layout_uuid,
        }
        return json.dumps(data, sort_keys=True).encode("utf8")

    def deserialize(self, raw, context):
        data = super().deserialize(raw, context)
        existing_queues = {
            q.getPath(): q for q in self.queues + self.old_queues
        }

        # Restore the old queues first, so that in case an item is
        # already in one of the new queues the item(s) ahead/behind
        # pointers are corrected when restoring the new queues.
        old_queues = []
        for queue_path in data["old_queues"]:
            queue = existing_queues.get(queue_path)
            if queue:
                queue.refresh(context)
            else:
                queue = ChangeQueue.fromZK(context, queue_path,
                                           pipeline=self.pipeline)
            old_queues.append(queue)

        queues = []
        for queue_path in data["queues"]:
            queue = existing_queues.get(queue_path)
            if queue:
                queue.refresh(context)
            else:
                queue = ChangeQueue.fromZK(context, queue_path,
                                           pipeline=self.pipeline)
            queues.append(queue)

        if hasattr(self.pipeline.manager, "change_queue_managers"):
            # Clear out references to old queues
            for cq_manager in self.pipeline.manager.change_queue_managers:
                cq_manager.created_for_branches.clear()

            # Add queues to matching change queue managers
            for queue in queues:
                project_cname, branch = queue.project_branches[0]
                for cq_manager in self.pipeline.manager.change_queue_managers:
                    managed_projects = {
                        p.canonical_name for p in cq_manager.projects
                    }
                    if project_cname in managed_projects:
                        cq_manager.created_for_branches[branch] = queue
                        break

        data.update({
            "queues": queues,
            "old_queues": old_queues,
        })
        return data

    def _getKnownItems(self):
        items = []
        for queue in (*self.old_queues, *self.queues):
            items.extend(queue.queue)
        return items

    def cleanup(self, context):
        pipeline_path = self.getPath()
        try:
            all_items = set(context.client.get_children(
                f"{pipeline_path}/item"))
        except NoNodeError:
            all_items = set()

        known_items = {i.uuid for i in self._getKnownItems()}
        stale_items = all_items - known_items
        for item_uuid in stale_items:
            self.pipeline.manager.log.debug("Cleaning up stale item %s",
                                            item_uuid)
            context.client.delete(QueueItem.itemPath(pipeline_path, item_uuid),
                                  recursive=True)

        try:
            all_queues = set(context.client.get_children(
                f"{pipeline_path}/queue"))
        except NoNodeError:
            all_queues = set()

        known_queues = {q.uuid for q in (*self.old_queues, *self.queues)}
        stale_queues = all_queues - known_queues
        for queue_uuid in stale_queues:
            self.pipeline.manager.log.debug("Cleaning up stale queue %s",
                                            queue_uuid)
            context.client.delete(
                ChangeQueue.queuePath(pipeline_path, queue_uuid),
                recursive=True)


class PipelineChangeList(zkobject.ShardedZKObject):
    """A list of change references within a pipeline

       This is used by the scheduler to quickly decide if events which
       otherwise don't match the pipeline triggers should be
       nevertheless forwarded to the pipeline.

       It is also used to maintain the connection cache.
    """
    # We can read from this object without locking, and since it's
    # sharded, that may produce an error.  If that happens, don't
    # delete the object, just retry.
    delete_on_error = False

    def __init__(self):
        super().__init__()
        self._set(
            changes=[],
        )

    def refresh(self, context):
        # See comment above about reading without a lock.
        while context.sessionIsValid():
            try:
                super().refresh(context)
                return
            except ZookeeperError:
                # These errors come from the server and are not
                # retryable.  Connection errors are KazooExceptions so
                # they aren't caught here and we will retry.
                raise
            except Exception:
                context.log.error("Failed to refresh change list")
                time.sleep(self._retry_interval)

    def getPath(self):
        return self.getChangeListPath(self.pipeline)

    @classmethod
    def getChangeListPath(cls, pipeline):
        pipeline_path = pipeline.state.getPath()
        return pipeline_path + '/change_list'

    @classmethod
    def create(cls, pipeline):
        ctx = pipeline.manager.current_context
        try:
            change_list = cls.fromZK(ctx, cls.getChangeListPath(pipeline),
                                     pipeline=pipeline)
            return change_list
        except NoNodeError:
            return cls.new(ctx, pipeline=pipeline)

    def serialize(self):
        data = {
            "changes": self.changes,
        }
        return json.dumps(data, sort_keys=True).encode("utf8")

    def deserialize(self, data, context):
        data = super().deserialize(data, context)
        change_keys = []
        # We must have a dictionary with a 'changes' key; otherwise we
        # may be reading immediately after truncating.  Allow the
        # KeyError exception to propogate in that case.
        for ref in data['changes']:
            change_keys.append(ChangeKey.fromReference(ref))
        data['_change_keys'] = change_keys
        return data

    def setChangeKeys(self, context, change_keys):
        change_refs = [key.reference for key in change_keys]
        if change_refs == self.changes:
            return
        self.updateAttributes(context, changes=change_refs)
        self._set(_change_keys=change_keys)

    def getChangeKeys(self):
        return self._change_keys


class PipelineSummary(zkobject.ShardedZKObject):

    log = logging.getLogger("zuul.PipelineSummary")
    truncate_on_create = True
    delete_on_error = False

    def __init__(self):
        super().__init__()
        self._set(
            status={},
        )

    def getPath(self):
        return f"{PipelineState.pipelinePath(self.pipeline)}/status"

    def update(self, context, zuul_globals):
        status = self.pipeline.formatStatusJSON(zuul_globals.websocket_url)
        self.updateAttributes(context, status=status)

    def serialize(self):
        data = {
            "status": self.status,
        }
        return json.dumps(data, sort_keys=True).encode("utf8")

    def refresh(self, context):
        # Ignore exceptions and just re-use the previous state. This
        # might happen in case the sharded status data is truncated
        # while zuul-web tries to read it.
        try:
            super().refresh(context)
        except Exception:
            self.log.exception("Failed to refresh data")
        return self.status


class ChangeQueue(zkobject.ZKObject):

    """A ChangeQueue contains Changes to be processed for related projects.

    A Pipeline with a DependentPipelineManager has multiple parallel
    ChangeQueues shared by different projects. For instance, there may a
    ChangeQueue shared by interrelated projects foo and bar, and a second queue
    for independent project baz.

    A Pipeline with an IndependentPipelineManager puts every Change into its
    own ChangeQueue.

    The ChangeQueue Window is inspired by TCP windows and controlls how many
    Changes in a given ChangeQueue will be considered active and ready to
    be processed. If a Change succeeds, the Window is increased by
    `window_increase_factor`. If a Change fails, the Window is decreased by
    `window_decrease_factor`.

    A ChangeQueue may be a dynamically created queue, which may be removed
    from a DependentPipelineManager once empty.
    """
    def __init__(self):
        super().__init__()
        self._set(
            uuid=uuid4().hex,
            pipeline=None,
            name="",
            project_branches=[],
            _jobs=set(),
            queue=[],
            window=0,
            window_floor=1,
            window_increase_type="linear",
            window_increase_factor=1,
            window_decrease_type="exponential",
            window_decrease_factor=2,
            dynamic=False,
        )

    def serialize(self):
        data = {
            "uuid": self.uuid,
            "name": self.name,
            "project_branches": self.project_branches,
            "_jobs": list(self._jobs),
            "queue": [i.getPath() for i in self.queue],
            "window": self.window,
            "window_floor": self.window_floor,
            "window_increase_type": self.window_increase_type,
            "window_increase_factor": self.window_increase_factor,
            "window_decrease_type": self.window_decrease_type,
            "window_decrease_factor": self.window_decrease_factor,
            "dynamic": self.dynamic,
        }
        return json.dumps(data, sort_keys=True).encode("utf8")

    def deserialize(self, raw, context):
        data = super().deserialize(raw, context)

        existing_items = {}
        for item in self.queue:
            existing_items[item.getPath()] = item
            if item.bundle:
                existing_items.update({
                    i.getPath(): i for i in item.bundle.items
                })

        items_by_path = OrderedDict()
        for item_path in data["queue"]:
            item = existing_items.get(item_path)
            if item:
                item.refresh(context)
            else:
                item = QueueItem.fromZK(context, item_path,
                                        pipeline=self.pipeline, queue=self)
            items_by_path[item.getPath()] = item

        # Resolve ahead/behind references between queue items
        for item in items_by_path.values():
            # After a re-enqueue we might have references to items
            # outside the current queue. We will resolve those
            # references to None for the item ahead or simply exclude
            # it in the list of items behind.
            # The pipeline manager will take care of correcting the
            # references on the next queue iteration.
            item._set(
                item_ahead=items_by_path.get(item._item_ahead),
                items_behind=[items_by_path[p] for p in item._items_behind
                              if p in items_by_path])

        bundle_by_uuid = {}
        for item in items_by_path.values():
            if not item.bundle:
                continue
            bundle_data = item.bundle
            item._set(bundle=bundle_by_uuid.setdefault(
                bundle_data["uuid"],
                Bundle.deserialize(context, self, items_by_path, bundle_data)))

        data.update({
            "_jobs": set(data["_jobs"]),
            "queue": list(items_by_path.values()),
            "project_branches": [tuple(pb) for pb in data["project_branches"]],
        })
        return data

    def getPath(self):
        pipeline_path = self.pipeline.state.getPath()
        return self.queuePath(pipeline_path, self.uuid)

    @classmethod
    def queuePath(cls, pipeline_path, queue_uuid):
        return f"{pipeline_path}/queue/{queue_uuid}"

    @property
    def zk_context(self):
        return self.pipeline.manager.current_context

    def __repr__(self):
        return '<ChangeQueue %s: %s>' % (self.pipeline.name, self.name)

    def getJobs(self):
        return self._jobs

    def addProject(self, project, branch):
        """
        Adds a project branch combination to the queue.

        The queue will match exactly this combination. If the caller doesn't
        care about branches it can supply None (but must supply None as well
        when matching)
        """
        project_branch = (project.canonical_name, branch)
        if project_branch not in self.project_branches:
            with self.activeContext(self.zk_context):
                self.project_branches.append(project_branch)

    def matches(self, project_cname, branch):
        return (project_cname, branch) in self.project_branches

    def enqueueChange(self, change, event):
        item = QueueItem.new(self.zk_context,
                             queue=self,
                             pipeline=self.pipeline,
                             change=change,
                             event=event,
                             enqueue_time=time.time())
        self.enqueueItem(item)
        return item

    def enqueueItem(self, item):
        # FIXME: the pipeline should not change
        item._set(pipeline=self.pipeline, queue=self)
        if self.queue:
            item.updateAttributes(self.zk_context, item_ahead=self.queue[-1])
            with item.item_ahead.activeContext(self.zk_context):
                item.item_ahead.items_behind.append(item)
        with self.activeContext(self.zk_context):
            self.queue.append(item)

    def dequeueItem(self, item):
        if item in self.queue:
            with self.activeContext(self.zk_context):
                self.queue.remove(item)
        if item.item_ahead:
            with item.item_ahead.activeContext(self.zk_context):
                item.item_ahead.items_behind.remove(item)
                item.item_ahead.items_behind.extend(item.items_behind)
        for item_behind in item.items_behind:
            item_behind.updateAttributes(self.zk_context,
                                         item_ahead=item.item_ahead)

        if item.bundle:
            if any([i in self.queue for i in item.bundle.items]):
                item.updateAttributes(
                    self.zk_context, item_ahead=None, items_behind=[],
                    dequeue_time=time.time())
            else:
                # We no longer need the bundle items
                for bundle_item in item.bundle.items:
                    bundle_item.delete(self.zk_context)
                item._set(dequeue_time=time.time())
        else:
            item.delete(self.zk_context)
            # We use the dequeue time for stats reporting, but the queue
            # item will no longer be in Zookeeper at this point.
            item._set(dequeue_time=time.time())

    def moveItem(self, item, item_ahead):
        if item.item_ahead == item_ahead:
            return False
        # Remove from current location
        if item.item_ahead:
            with item.item_ahead.activeContext(self.zk_context):
                item.item_ahead.items_behind.remove(item)
                item.item_ahead.items_behind.extend(item.items_behind)
        for item_behind in item.items_behind:
            item_behind.updateAttributes(
                self.zk_context,
                item_ahead=item.item_ahead)
        # Add to new location
        item.updateAttributes(
            self.zk_context,
            item_ahead=item_ahead,
            items_behind=[])
        if item.item_ahead:
            with item.item_ahead.activeContext(self.zk_context):
                item.item_ahead.items_behind.append(item)
        return True

    def isActionable(self, item):
        if not self.window:
            return True
        # Ignore done items waiting for bundle dependencies to finish
        num_waiting_items = len([
            i for i in self.queue
            if i.bundle and i.areAllJobsComplete()
        ])
        window = self.window + num_waiting_items
        return item in self.queue[:window]

    def increaseWindowSize(self):
        if not self.window:
            return
        with self.activeContext(self.zk_context):
            if self.window_increase_type == 'linear':
                self.window += self.window_increase_factor
            elif self.window_increase_type == 'exponential':
                self.window *= self.window_increase_factor

    def decreaseWindowSize(self):
        if not self.window:
            return
        with self.activeContext(self.zk_context):
            if self.window_decrease_type == 'linear':
                self.window = max(
                    self.window_floor,
                    self.window - self.window_decrease_factor)
            elif self.window_decrease_type == 'exponential':
                self.window = max(
                    self.window_floor,
                    int(self.window / self.window_decrease_factor))


class Project(object):
    """A Project represents a git repository such as openstack/nova."""

    # NOTE: Projects should only be instantiated via a Source object
    # so that they are associated with and cached by their Connection.
    # This makes a Project instance a unique identifier for a given
    # project from a given source.

    def __init__(self, name, source, foreign=False):
        self.name = name
        self.source = source
        self.connection_name = source.connection.connection_name
        self.canonical_hostname = source.canonical_hostname
        self.canonical_name = source.canonical_hostname + '/' + name
        self.private_secrets_key = None
        self.public_secrets_key = None
        self.private_ssh_key = None
        self.public_ssh_key = None
        # foreign projects are those referenced in dependencies
        # of layout projects, this should matter
        # when deciding whether to enqueue their changes
        # TODOv3 (jeblair): re-add support for foreign projects if needed
        self.foreign = foreign

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<Project %s>' % (self.name)

    def getSafeAttributes(self):
        return Attributes(name=self.name)

    def toDict(self):
        d = {}
        d['name'] = self.name
        d['connection_name'] = self.connection_name
        d['canonical_name'] = self.canonical_name
        return d


class Node(ConfigObject):
    """A single node for use by a job.

    This may represent a request for a node, or an actual node
    provided by Nodepool.
    """

    def __init__(self, name, label):
        super(Node, self).__init__()
        self.name = name
        self.label = label
        self.id = None
        self.lock = None
        self.hold_job = None
        self.comment = None
        self.user_data = None
        # Attributes from Nodepool
        self._state = 'unknown'
        self.state_time = time.time()
        self.host_id = None
        self.interface_ip = None
        self.public_ipv4 = None
        self.private_ipv4 = None
        self.public_ipv6 = None
        self.private_ipv6 = None
        self.connection_port = 22
        self.connection_type = None
        self._keys = []
        self.az = None
        self.provider = None
        self.region = None
        self.username = None
        self.hold_expiration = None
        self.resources = None
        self.allocated_to = None
        self.attributes = {}

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        if value not in NODE_STATES:
            raise TypeError("'%s' is not a valid state" % value)
        self._state = value
        self.state_time = time.time()

    def __repr__(self):
        return '<Node %s %s:%s>' % (self.id, self.name, self.label)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        if not isinstance(other, Node):
            return False
        return (self.name == other.name and
                self.label == other.label and
                self.id == other.id)

    def toDict(self, internal_attributes=False):
        d = {}
        d["id"] = self.id
        d['state'] = self.state
        d['hold_job'] = self.hold_job
        d['comment'] = self.comment
        d['user_data'] = self.user_data
        for k in self._keys:
            d[k] = getattr(self, k)
        if internal_attributes:
            # These attributes are only useful for the rpc serialization
            d['name'] = self.name[0]
            d['aliases'] = self.name[1:]
            d['label'] = self.label
        return d

    def updateFromDict(self, data):
        self._state = data['state']
        keys = []
        for k, v in data.items():
            if k in ['state', 'name', 'aliases']:
                continue
            keys.append(k)
            setattr(self, k, v)
        self._keys = keys

    @classmethod
    def fromDict(cls, data):
        aliases = data.get('aliases', [])
        node = cls([data["name"]] + aliases, data["label"])
        node.updateFromDict(data)
        return node


class Group(ConfigObject):
    """A logical group of nodes for use by a job.

    A Group is a named set of node names that will be provided to
    jobs in the inventory to describe logical units where some subset of tasks
    run.
    """

    def __init__(self, name, nodes):
        super(Group, self).__init__()
        self.name = name
        self.nodes = nodes

    def __repr__(self):
        return '<Group %s %s>' % (self.name, str(self.nodes))

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        if not isinstance(other, Group):
            return False
        return (self.name == other.name and
                self.nodes == other.nodes)

    def toDict(self):
        return {
            'name': self.name,
            'nodes': self.nodes
        }

    @classmethod
    def fromDict(cls, data):
        return cls(data["name"], data["nodes"])


class NodeSet(ConfigObject):
    """A set of nodes.

    In configuration, NodeSets are attributes of Jobs indicating that
    a Job requires nodes matching this description.

    They may appear as top-level configuration objects and be named,
    or they may appears anonymously in in-line job definitions.
    """

    def __init__(self, name=None):
        super(NodeSet, self).__init__()
        self.name = name or ''
        self.nodes = OrderedDict()
        self.groups = OrderedDict()

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        if not isinstance(other, NodeSet):
            return False
        return (self.name == other.name and
                self.nodes == other.nodes)

    def toDict(self):
        d = {}
        d['name'] = self.name
        d['nodes'] = []
        for node in self.nodes.values():
            d['nodes'].append(node.toDict(internal_attributes=True))
        d['groups'] = []
        for group in self.groups.values():
            d['groups'].append(group.toDict())
        return d

    @classmethod
    def fromDict(cls, data):
        nodeset = cls(data["name"])
        for node in data["nodes"]:
            nodeset.addNode(Node.fromDict(node))
        for group in data["groups"]:
            nodeset.addGroup(Group.fromDict(group))
        return nodeset

    def copy(self):
        n = NodeSet(self.name)
        for name, node in self.nodes.items():
            n.addNode(Node(node.name, node.label))
        for name, group in self.groups.items():
            n.addGroup(Group(group.name, group.nodes[:]))
        return n

    def addNode(self, node):
        for name in node.name:
            if name in self.nodes:
                raise Exception("Duplicate node in %s" % (self,))
        self.nodes[tuple(node.name)] = node

    def getNodes(self):
        return list(self.nodes.values())

    def addGroup(self, group):
        if group.name in self.groups:
            raise Exception("Duplicate group in %s" % (self,))
        self.groups[group.name] = group

    def getGroups(self):
        return list(self.groups.values())

    def __repr__(self):
        if self.name:
            name = self.name + ' '
        else:
            name = ''
        return '<NodeSet %s%s>' % (name, list(self.nodes.values()))

    def __len__(self):
        return len(self.nodes)


class NodeRequest(object):
    """A request for a set of nodes."""

    def __init__(self, requestor, build_set_uuid, tenant_name, pipeline_name,
                 job_name, labels, provider, relative_priority,
                 event_id=None):
        self.requestor = requestor
        self.build_set_uuid = build_set_uuid
        self.tenant_name = tenant_name
        self.pipeline_name = pipeline_name
        self.job_name = job_name
        self.labels = labels
        self.nodes = []
        self._state = STATE_REQUESTED
        self.requested_time = time.time()
        self.state_time = time.time()
        self.created_time = None
        self.stat = None
        self.relative_priority = relative_priority
        self.provider = provider
        self.id = None
        self._zk_data = {}  # Data that we read back from ZK
        self.event_id = event_id
        # Zuul internal flags (not stored in ZK so they are not
        # overwritten).
        self.failed = False
        self.canceled = False

    def reset(self):
        # Reset the node request for re-submission
        self._zk_data = {}
        # Remove any real node information
        self.nodes = []
        self.id = None
        self.state = STATE_REQUESTED
        self.stat = None
        self.failed = False
        self.canceled = False

    @property
    def fulfilled(self):
        return (self._state == STATE_FULFILLED) and not self.failed

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        if value not in REQUEST_STATES:
            raise TypeError("'%s' is not a valid state" % value)
        self._state = value
        self.state_time = time.time()

    def __repr__(self):
        return '<NodeRequest %s %s>' % (self.id, self.labels)

    def toDict(self):
        """
        Serialize a NodeRequest so it can be stored in ZooKeeper.

        Any additional information must be stored in the requestor_data field,
        so Nodepool doesn't strip the information when it fulfills the request.
        """
        # Start with any previously read data
        d = self._zk_data.copy()
        # The requestor_data is opaque to nodepool and won't be touched by
        # nodepool when it fulfills the request.
        d["requestor_data"] = {
            "build_set_uuid": self.build_set_uuid,
            "tenant_name": self.tenant_name,
            "pipeline_name": self.pipeline_name,
            "job_name": self.job_name,
        }
        d.setdefault('node_types', self.labels)
        d.setdefault('requestor', self.requestor)
        d.setdefault('created_time', self.created_time)
        d.setdefault('provider', self.provider)
        # We might change these
        d['state'] = self.state
        d['state_time'] = self.state_time
        d['relative_priority'] = self.relative_priority
        d['event_id'] = self.event_id
        d['tenant_name'] = self.tenant_name
        return d

    def updateFromDict(self, data):
        self._zk_data = data
        self._state = data['state']
        self.state_time = data['state_time']
        self.relative_priority = data.get('relative_priority', 0)
        self.event_id = data['event_id']
        # Make sure we don't update tenant_name to 'None'.
        # This can happen if nodepool does not report one back and leads
        # to errors at other places where we rely on that info.
        if 'tenant_name' in data:
            self.tenant_name = data['tenant_name']
        self.nodes = data.get('nodes', [])

    @classmethod
    def fromDict(cls, data):
        """Deserialize a NodeRequest from the data in ZooKeeper.

        Any additional information must be stored in the requestor_data field,
        so Nodepool doesn't strip the information when it fulfills the request.
        """
        # The requestor_data contains zuul-specific information which is opaque
        # to nodepool and returned as-is when the NodeRequest is fulfilled.
        requestor_data = data["requestor_data"]
        if requestor_data is None:
            requestor_data = {}
        request = cls(
            requestor=data["requestor"],
            build_set_uuid=requestor_data.get("build_set_uuid"),
            tenant_name=requestor_data.get("tenant_name"),
            pipeline_name=requestor_data.get("pipeline_name"),
            job_name=requestor_data.get("job_name"),
            labels=data["node_types"],
            provider=data["provider"],
            relative_priority=data.get("relative_priority", 0),
        )

        request.updateFromDict(data)

        return request


class Secret(ConfigObject):
    """A collection of private data.

    In configuration, Secrets are collections of private data in
    key-value pair format.  They are defined as top-level
    configuration objects and then referenced by Jobs.

    """

    def __init__(self, name, source_context):
        super(Secret, self).__init__()
        self.name = name
        self.source_context = source_context
        # The secret data may or may not be encrypted.  This attribute
        # is named 'secret_data' to make it easy to search for and
        # spot where it is directly used.
        self.secret_data = {}

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        if not isinstance(other, Secret):
            return False
        return (self.name == other.name and
                self.source_context == other.source_context and
                self.secret_data == other.secret_data)

    def areDataEqual(self, other):
        return (self.secret_data == other.secret_data)

    def __repr__(self):
        return '<Secret %s>' % (self.name,)

    def _decrypt(self, private_key, secret_data):
        # recursive function to decrypt data
        if hasattr(secret_data, 'decrypt'):
            return secret_data.decrypt(private_key)

        if isinstance(secret_data, (dict, types.MappingProxyType)):
            decrypted_secret_data = {}
            for k, v in secret_data.items():
                decrypted_secret_data[k] = self._decrypt(private_key, v)
            return decrypted_secret_data

        if isinstance(secret_data, (list, tuple)):
            decrypted_secret_data = []
            for v in secret_data:
                decrypted_secret_data.append(self._decrypt(private_key, v))
            return decrypted_secret_data

        return secret_data

    def decrypt(self, private_key):
        """Return a copy of this secret with any encrypted data decrypted.
        Note that the original remains encrypted."""

        r = Secret(self.name, self.source_context)
        r.secret_data = self._decrypt(private_key, self.secret_data)
        return r

    def serialize(self):
        return yaml.encrypted_dump(self.secret_data, default_flow_style=False)


class SecretUse(ConfigObject):
    """A use of a secret in a Job"""

    def __init__(self, name, alias):
        super(SecretUse, self).__init__()
        self.name = name
        self.alias = alias
        self.pass_to_parent = False


class FrozenSecret(ConfigObject):
    """A frozen secret for use by the executor"""

    def __init__(self, connection_name, project_name, name, encrypted_data):
        super(FrozenSecret, self).__init__()
        self.connection_name = connection_name
        self.project_name = project_name
        self.name = name
        self.encrypted_data = encrypted_data

    @staticmethod
    @lru_cache(maxsize=1024)
    def construct_cached(connection_name, project_name, name, encrypted_data):
        """
        A caching constructor that enables re-use already existing
        FrozenSecret objects.
        """
        return FrozenSecret(connection_name, project_name, name,
                            encrypted_data)

    def toDict(self):
        # Name is omitted since this is used in a dictionary
        return dict(
            connection_name=self.connection_name,
            project_name=self.project_name,
            encrypted_data=self.encrypted_data,
        )


class ProjectContext(ConfigObject):

    def __init__(self, project_canonical_name, project_name):
        super().__init__()
        self.project_canonical_name = project_canonical_name
        self.project_name = project_name
        self.branch = None
        self.path = None

    def __str__(self):
        return self.project_name

    def toDict(self):
        return dict(
            project=self.project_name,
        )


class SourceContext(ConfigObject):
    """A reference to the branch of a project in configuration.

    Jobs and playbooks reference this to keep track of where they
    originate."""

    def __init__(self, project_canonical_name, project_name,
                 project_connection_name, branch, path, trusted):
        super(SourceContext, self).__init__()
        self.project_canonical_name = project_canonical_name
        self.project_name = project_name
        self.project_connection_name = project_connection_name
        self.branch = branch
        self.path = path
        self.trusted = trusted
        self.implied_branch_matchers = None
        self.implied_branches = None

    def __str__(self):
        return '%s/%s@%s' % (
            self.project_name, self.path, self.branch)

    def __repr__(self):
        return '<SourceContext %s trusted:%s>' % (str(self),
                                                  self.trusted)

    def __deepcopy__(self, memo):
        return self.copy()

    def copy(self):
        return self.__class__(
            self.project_canonical_name, self.project_name,
            self.project_connection_name, self.branch, self.path, self.trusted)

    def isSameProject(self, other):
        if not isinstance(other, SourceContext):
            return False
        return (self.project_canonical_name == other.project_canonical_name and
                self.trusted == other.trusted)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        if not isinstance(other, SourceContext):
            return False
        return (self.project_canonical_name == other.project_canonical_name and
                self.branch == other.branch and
                self.path == other.path and
                self.trusted == other.trusted)

    def serialize(self):
        return {
            "project_canonical_name": self.project_canonical_name,
            "project_name": self.project_name,
            "project_connection_name": self.project_connection_name,
            "branch": self.branch,
            "path": self.path,
            "trusted": self.trusted,
            "implied_branch_matchers": self.implied_branch_matchers,
            "implied_branches": self.implied_branches,
        }

    @classmethod
    def deserialize(cls, data):
        o = cls.__new__(cls)
        o.__dict__.update(data)
        return o

    def toDict(self):
        return dict(
            project=self.project_name,
            branch=self.branch,
            path=self.path,
        )


class PlaybookContext(ConfigObject):
    """A reference to a playbook in the context of a project.

    Jobs refer to objects of this class for their main, pre, and post
    playbooks so that we can keep track of which repos and security
    contexts are needed in order to run them.

    We also keep a list of roles so that playbooks only run with the
    roles which were defined at the point the playbook was defined.

    """

    def __init__(self, source_context, path, roles, secrets):
        super(PlaybookContext, self).__init__()
        self.source_context = source_context
        self.path = path
        self.roles = roles
        # The original SecretUse objects describing how the secret
        # should be used
        self.secrets = secrets
        # FrozenSecret objects which contain only the info the
        # executor needs
        self.frozen_secrets = ()

    def __repr__(self):
        return '<PlaybookContext %s %s>' % (self.source_context,
                                            self.path)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        if not isinstance(other, PlaybookContext):
            return False
        return (self.source_context == other.source_context and
                self.path == other.path and
                self.roles == other.roles and
                self.secrets == other.secrets)

    def copy(self):
        r = PlaybookContext(self.source_context,
                            self.path,
                            self.roles,
                            self.secrets)
        return r

    def validateReferences(self, layout):
        # Verify that references to other objects in the layout are
        # valid.
        for secret_use in self.secrets:
            secret = layout.secrets.get(secret_use.name)
            if secret is None:
                raise Exception(
                    'The secret "{name}" was not found.'.format(
                        name=secret_use.name))
            check_varnames({secret_use.alias: ''})
            if not secret.source_context.isSameProject(self.source_context):
                raise Exception(
                    "Unable to use secret {name}.  Secrets must be "
                    "defined in the same project in which they "
                    "are used".format(
                        name=secret_use.name))
            project = layout.tenant.getProject(
                self.source_context.project_canonical_name)[1]
            # Decrypt a copy of the secret to verify it can be done
            secret.decrypt(project.private_secrets_key)

    def freezeSecrets(self, layout):
        secrets = []
        for secret_use in self.secrets:
            secret = layout.secrets.get(secret_use.name)
            secret_name = secret_use.alias
            encrypted_secret_data = secret.serialize()
            # Use *our* project, not the secret's, because we want to decrypt
            # with *our* key.
            project = layout.tenant.getProject(
                self.source_context.project_canonical_name)[1]
            secrets.append(FrozenSecret.construct_cached(
                project.connection_name, project.name, secret_name,
                encrypted_secret_data))
        self.frozen_secrets = tuple(secrets)

    def addSecrets(self, frozen_secrets):
        current_names = set([s.name for s in self.frozen_secrets])
        new_secrets = [s for s in frozen_secrets
                       if s.name not in current_names]
        self.frozen_secrets = self.frozen_secrets + tuple(new_secrets)

    def toDict(self, redact_secrets=True):
        # Render to a dict to use in passing json to the executor
        secrets = {}
        for secret in self.frozen_secrets:
            if redact_secrets:
                secrets[secret.name] = 'REDACTED'
            else:
                secrets[secret.name] = secret.toDict()
        return dict(
            connection=self.source_context.project_connection_name,
            project=self.source_context.project_name,
            branch=self.source_context.branch,
            trusted=self.source_context.trusted,
            roles=[r.toDict() for r in self.roles],
            secrets=secrets,
            path=self.path)

    def toSchemaDict(self):
        # Render to a dict to use in REST api
        d = {
            'path': self.path,
            'roles': list(map(lambda x: x.toDict(), self.roles)),
            'secrets': [{'name': secret.name, 'alias': secret.alias}
                        for secret in self.secrets],
        }
        if self.source_context:
            d['source_context'] = self.source_context.toDict()
        else:
            d['source_context'] = None
        return d


class Role(ConfigObject, metaclass=abc.ABCMeta):
    """A reference to an ansible role."""

    def __init__(self, target_name):
        super(Role, self).__init__()
        self.target_name = target_name

    @abc.abstractmethod
    def __repr__(self):
        pass

    def __ne__(self, other):
        return not self.__eq__(other)

    @abc.abstractmethod
    def __eq__(self, other):
        if not isinstance(other, Role):
            return False
        return (self.target_name == other.target_name)

    @abc.abstractmethod
    def toDict(self):
        # Render to a dict to use in passing json to the executor
        return dict(target_name=self.target_name)


class ZuulRole(Role):
    """A reference to an ansible role in a Zuul project."""

    def __init__(self, target_name, project_canonical_name, implicit=False):
        super(ZuulRole, self).__init__(target_name)
        self.project_canonical_name = project_canonical_name
        self.implicit = implicit

    def __repr__(self):
        return '<ZuulRole %s %s>' % (self.project_canonical_name,
                                     self.target_name)

    __hash__ = object.__hash__

    def __eq__(self, other):
        if not isinstance(other, ZuulRole):
            return False
        # Implicit is not consulted for equality so that we can handle
        # implicit to explicit conversions.
        return (super(ZuulRole, self).__eq__(other) and
                self.project_canonical_name == other.project_canonical_name)

    def toDict(self):
        # Render to a dict to use in passing json to the executor
        d = super(ZuulRole, self).toDict()
        d['type'] = 'zuul'
        d['project_canonical_name'] = self.project_canonical_name
        d['implicit'] = self.implicit
        return d

    @classmethod
    def fromDict(cls, data):
        self = cls(data['target_name'],
                   data['project_canonical_name'],
                   data['implicit'])
        return self


class JobData(zkobject.ShardedZKObject):
    """Data or variables for a job.

    These can be arbitrarily large, so they are stored as sharded ZK objects.

    A hash attribute can be stored on the job object itself to detect
    whether the data need to be refreshed.

    """

    # We can always recreate data if necessary, so go ahead and
    # truncate when we update so we avoid corrupted data.
    truncate_on_create = True

    def __repr__(self):
        return '<JobData>'

    def getPath(self):
        return self._path

    @classmethod
    def new(klass, context, **kw):
        """Create a new instance and save it in ZooKeeper"""
        obj = klass()
        kw['hash'] = JobData.getHash(kw['data'])
        obj._set(**kw)
        data = obj._trySerialize(context)
        obj._save(context, data, create=True)
        return obj

    @staticmethod
    def getHash(data):
        hasher = hashlib.sha256()
        # Use json_dumps to strip any ZuulMark entries
        hasher.update(json_dumps(data, sort_keys=True).encode('utf8'))
        return hasher.hexdigest()

    def serialize(self):
        data = {
            "data": self.data,
            "hash": self.hash,
            "_path": self._path,
        }
        return json_dumps(data, sort_keys=True).encode("utf8")


class FrozenJob(zkobject.ZKObject):
    """A rendered job definition that will actually be run.

    This is the combination of one or more Job variants to produce a
    rendered job definition that can be serialized and run by the
    executor.

    Most variables should not be updated once created, except some
    variables which deal with the current state of the job in the
    pipeline.
    """
    # If data/variables are more than 10k, we offload them to another
    # object, otherwise we store them on this one.
    MAX_DATA_LEN = 10 * 1024

    attributes = ('ansible_version',
                  'dependencies',
                  'inheritance_path',
                  'name',
                  'nodeset',
                  'override_branch',
                  'override_checkout',
                  'post_timeout',
                  'required_projects',
                  'semaphores',
                  'tags',
                  'timeout',
                  'voting',
                  'queued',
                  'hold_following_changes',
                  'waiting_status',
                  'pre_run',
                  'run',
                  'post_run',
                  'cleanup_run',
                  'attempts',
                  'success_message',
                  'failure_message',
                  'provides',
                  'requires',
                  'workspace_scheme',
                  'config_hash',
                  )

    job_data_attributes = ('artifact_data',
                           'extra_variables',
                           'group_variables',
                           'host_variables',
                           'secret_parent_data',
                           'variables',
                           'parent_data',
                           'secrets',
                           'affected_projects',
                           )

    def __repr__(self):
        return '<FrozenJob %s>' % (self.name)

    @classmethod
    def new(klass, context, **kw):
        obj = klass()

        # Convert these to JobData after creation.
        job_data_vars = {}
        for k in klass.job_data_attributes:
            v = kw.pop(k, None)
            if v:
                # If the value is long, we need to make this a JobData;
                # otherwise we can use the dict as-is.
                if (len(json_dumps(v, sort_keys=True).encode('utf8')) >
                    klass.MAX_DATA_LEN):
                    job_data_vars[k] = v
                    v = None
            kw['_' + k] = v
        obj._set(**kw)
        data = obj._trySerialize(context)
        obj._save(context, data, create=True)

        # If we need to make any JobData entries, do that now.
        update_kw = {}
        for (k, v) in job_data_vars.items():
            update_kw['_' + k] = obj._makeJobData(context, k, v)
        if update_kw:
            obj.updateAttributes(context, **update_kw)
        return obj

    def isBase(self):
        return self.parent is None

    @classmethod
    def jobPath(cls, job_name, parent_path):
        safe_job = urllib.parse.quote_plus(job_name)
        return f"{parent_path}/job/{safe_job}"

    def getPath(self):
        return self.jobPath(self.name, self.buildset.getPath())

    def serialize(self):
        data = {}
        for k in self.attributes:
            # TODO: Backwards compat handling, remove after 5.0
            if k == 'config_hash':
                if not hasattr(self, k):
                    continue
            v = getattr(self, k)
            if k == 'nodeset':
                v = v.toDict()
            elif k == 'dependencies':
                # list of JobDependency
                v = [dep.toDict() for dep in v]
            elif k == 'semaphores':
                # list of JobSemaphores
                v = [sem.toDict() for sem in v]
            elif k in ('provides', 'requires'):
                v = list(v)
            elif k == 'required_projects':
                # dict of name->JobProject
                v = {project_name: job_project.toDict()
                     for (project_name, job_project) in v.items()}
            data[k] = v

        for k in self.job_data_attributes:
            v = getattr(self, '_' + k)
            if isinstance(v, JobData):
                v = {'storage': 'offload', 'path': v.getPath(), 'hash': v.hash}
            else:
                v = {'storage': 'local', 'data': v}
            data[k] = v

        # Use json_dumps to strip any ZuulMark entries
        return json_dumps(data, sort_keys=True).encode("utf8")

    def deserialize(self, raw, context):
        data = super().deserialize(raw, context)

        if hasattr(self, 'nodeset'):
            nodeset = self.nodeset
        else:
            nodeset = data.get('nodeset')
            if nodeset:
                nodeset = NodeSet.fromDict(nodeset)
        data['nodeset'] = nodeset

        if hasattr(self, 'dependencies'):
            data['dependencies'] = self.dependencies
        else:
            data['dependencies'] = [JobDependency.fromDict(dep)
                                    for dep in data['dependencies']]

        if hasattr(self, 'semaphores'):
            data['semaphores'] = self.semaphores
        else:
            data['semaphores'] = [JobSemaphore.fromDict(sem)
                                  for sem in data['semaphores']]

        if hasattr(self, 'required_projects'):
            data['required_projects'] = self.required_projects
        else:
            data['required_projects'] = {
                project_name: JobProject.fromDict(job_project)
                for (project_name, job_project)
                in data['required_projects'].items()}

        data['provides'] = frozenset(data['provides'])
        data['requires'] = frozenset(data['requires'])

        for job_data_key in self.job_data_attributes:
            job_data = data.pop(job_data_key, None)
            if job_data:
                # This is a dict which tells us where the actual data is.
                if job_data['storage'] == 'local':
                    # The data are stored locally in this dict
                    data['_' + job_data_key] = job_data['data']
                elif job_data['storage'] == 'offload':
                    existing_job_data = getattr(self, job_data_key, None)
                    if (getattr(existing_job_data, 'hash', None) ==
                        job_data['hash']):
                        # Re-use the existing object since it's the same
                        data['_' + job_data_key] = existing_job_data
                    else:
                        # Load the object from ZK
                        data['_' + job_data_key] = JobData.fromZK(
                            context, job_data['path'])
            else:
                data['_' + job_data_key] = None
        return data

    def setWaitingStatus(self, status):
        if self.waiting_status == status:
            return
        self.updateAttributes(
            self.buildset.item.pipeline.manager.current_context,
            waiting_status=status)

    def _getJobData(self, name):
        val = getattr(self, name, None)
        if isinstance(val, JobData):
            return val.data
        return val

    @property
    def parent_data(self):
        return self._getJobData('_parent_data')

    @property
    def secret_parent_data(self):
        return self._getJobData('_secret_parent_data')

    @property
    def artifact_data(self):
        return self._getJobData('_artifact_data')

    @property
    def extra_variables(self):
        return self._getJobData('_extra_variables')

    @property
    def group_variables(self):
        return self._getJobData('_group_variables')

    @property
    def host_variables(self):
        return self._getJobData('_host_variables')

    @property
    def variables(self):
        return self._getJobData('_variables')

    @property
    def secrets(self):
        return self._getJobData('_secrets')

    @property
    def affected_projects(self):
        return self._getJobData('_affected_projects')

    @property
    def combined_variables(self):
        """
        Combines the data that has been returned by parent jobs with the
        job variables where job variables have priority over parent data.
        """
        return Job._deepUpdate(self.parent_data or {}, self.variables)

    def getSafeAttributes(self):
        return Attributes(name=self.name)

    @staticmethod
    def updateParentData(parent_data, secret_parent_data, artifact_data,
                         other_build):
        # Update variables, but give the new values priority. If more than one
        # parent job returns the same variable, the value from the later job
        # in the job graph will take precedence.
        other_vars = other_build.result_data
        v = parent_data
        v = Job._deepUpdate(v, other_vars)
        # To avoid running afoul of checks that jobs don't set zuul
        # variables, remove them from parent data here.
        v.pop('zuul', None)
        # For safety, also drop nodepool and unsafe_vars
        v.pop('nodepool', None)
        v.pop('unsafe_vars', None)
        parent_data = v

        secret_other_vars = other_build.secret_result_data
        v = secret_parent_data
        v = Job._deepUpdate(secret_other_vars, v)
        if 'zuul' in v:
            del v['zuul']
        secret_parent_data = v

        artifacts = get_artifacts_from_result_data(other_vars)
        artifact_data = artifact_data[:]
        for a in artifacts:
            # Change here may be any ref type (tag, change, etc)
            ref = other_build.build_set.item.change
            a.update({'project': ref.project.name,
                      'job': other_build.job.name})
            # Change is a Branch
            if hasattr(ref, 'branch'):
                a.update({'branch': ref.branch})
                if hasattr(ref, 'number') and hasattr(ref, 'patchset'):
                    a.update({'change': str(ref.number),
                              'patchset': ref.patchset})
            # Otherwise we are ref type
            else:
                a.update({'ref': ref.ref,
                          'oldrev': ref.oldrev,
                          'newrev': ref.newrev})
                if hasattr(ref, 'tag'):
                    a.update({'tag': ref.tag})
            if a not in artifact_data:
                artifact_data.append(a)
        return parent_data, secret_parent_data, artifact_data

    def _makeJobData(self, context, name, data):
        # If the data is large, store it in another object
        if (len(json_dumps(data, sort_keys=True).encode('utf8')) >
            self.MAX_DATA_LEN):
            return JobData.new(
                context, _path=self.getPath() + '/' + name,
                data=data)
        # Otherwise we can store it as a local dict
        return data

    def setParentData(self, parent_data, secret_parent_data, artifact_data):
        context = self.buildset.item.pipeline.manager.current_context
        kw = {}
        if self.parent_data != parent_data:
            kw['_parent_data'] = self._makeJobData(
                context, 'parent_data', parent_data)
        if self.secret_parent_data != secret_parent_data:
            kw['_secret_parent_data'] = self._makeJobData(
                context, 'secret_parent_data', secret_parent_data)
        if self.artifact_data != artifact_data:
            kw['_artifact_data'] = self._makeJobData(
                context, 'artifact_data', artifact_data)
        if kw:
            self.updateAttributes(
                self.buildset.item.pipeline.manager.current_context,
                **kw)

    def setArtifactData(self, artifact_data):
        context = self.buildset.item.pipeline.manager.current_context
        if self.artifact_data != artifact_data:
            self.updateAttributes(
                context,
                _artifact_data=self._makeJobData(
                    context, 'artifact_data', artifact_data))


class Job(ConfigObject):
    """A Job represents the defintion of actions to perform.

    A Job is an abstract configuration concept.  It describes what,
    where, and under what circumstances something should be run
    (contrast this with Build which is a concrete single execution of
    a Job).

    NB: Do not modify attributes of this class, set them directly
    (e.g., "job.run = ..." rather than "job.run.append(...)").
    """

    # Pre-allocated empty nodeset so we don't have to allocate a new one
    # with every job variant.
    empty_nodeset = NodeSet()

    BASE_JOB_MARKER = object()

    def isBase(self):
        return self.parent is self.BASE_JOB_MARKER

    def toDict(self, tenant):
        '''
        Convert a Job object's attributes to a dictionary.
        '''
        d = {}
        d['name'] = self.name
        d['branches'] = self._branches
        d['override_checkout'] = self.override_checkout
        d['files'] = self._files
        d['irrelevant_files'] = self._irrelevant_files
        d['variant_description'] = self.variant_description
        if self.source_context:
            d['source_context'] = self.source_context.toDict()
        else:
            d['source_context'] = None
        d['description'] = self.description
        d['required_projects'] = []
        for project in self.required_projects.values():
            d['required_projects'].append(project.toDict())
        d['semaphores'] = [s.toDict() for s in self.semaphores]
        d['variables'] = self.variables
        d['extra_variables'] = self.extra_variables
        d['host_variables'] = self.host_variables
        d['group_variables'] = self.group_variables
        d['final'] = self.final
        d['abstract'] = self.abstract
        d['intermediate'] = self.intermediate
        d['protected'] = self.protected
        d['voting'] = self.voting
        d['timeout'] = self.timeout
        d['tags'] = list(self.tags)
        d['provides'] = list(self.provides)
        d['requires'] = list(self.requires)
        d['dependencies'] = list(map(lambda x: x.toDict(), self.dependencies))
        d['attempts'] = self.attempts
        d['roles'] = list(map(lambda x: x.toDict(), self.roles))
        d['run'] = list(map(lambda x: x.toSchemaDict(), self.run))
        d['pre_run'] = list(map(lambda x: x.toSchemaDict(), self.pre_run))
        d['post_run'] = list(map(lambda x: x.toSchemaDict(), self.post_run))
        d['cleanup_run'] = list(map(lambda x: x.toSchemaDict(),
                                    self.cleanup_run))
        d['post_review'] = self.post_review
        d['match_on_config_updates'] = self.match_on_config_updates
        if self.isBase():
            d['parent'] = None
        elif self.parent:
            d['parent'] = self.parent
        else:
            d['parent'] = tenant.default_base_job
        if isinstance(self.nodeset, str):
            ns = tenant.layout.nodesets.get(self.nodeset)
        else:
            ns = self.nodeset
        if ns:
            d['nodeset'] = ns.toDict()
        if self.ansible_version:
            d['ansible_version'] = self.ansible_version
        else:
            d['ansible_version'] = None
        d['workspace_scheme'] = self.workspace_scheme
        return d

    def __init__(self, name):
        super().__init__()
        # These attributes may override even the final form of a job
        # in the context of a project-pipeline.  They can not affect
        # the execution of the job, but only whether the job is run
        # and how it is reported.
        self.context_attributes = dict(
            voting=True,
            hold_following_changes=False,
            failure_message=None,
            success_message=None,
            branch_matcher=None,
            _branches=(),
            file_matcher=None,
            _files=(),
            irrelevant_file_matcher=None,  # skip-if
            _irrelevant_files=(),
            match_on_config_updates=True,
            tags=frozenset(),
            provides=frozenset(),
            requires=frozenset(),
            dependencies=frozenset(),
            ignore_allowed_projects=None,  # internal, but inherited
                                           # in the usual manner
        )

        # These attributes affect how the job is actually run and more
        # care must be taken when overriding them.  If a job is
        # declared "final", these may not be overridden in a
        # project-pipeline.
        self.execution_attributes = dict(
            parent=None,
            timeout=None,
            post_timeout=None,
            variables={},
            extra_variables={},
            host_variables={},
            group_variables={},
            nodeset=Job.empty_nodeset,
            workspace=None,
            pre_run=(),
            post_run=(),
            cleanup_run=(),
            run=(),
            ansible_version=None,
            semaphores=(),
            attempts=3,
            final=False,
            abstract=False,
            intermediate=False,
            protected=None,
            roles=(),
            required_projects={},
            allowed_projects=None,
            override_branch=None,
            override_checkout=None,
            post_review=None,
            workspace_scheme=SCHEME_GOLANG,
        )

        # These are generally internal attributes which are not
        # accessible via configuration.
        self.other_attributes = dict(
            name=None,
            source_context=None,
            start_mark=None,
            inheritance_path=(),
            parent_data=None,
            secret_parent_data=None,
            artifact_data=None,
            description=None,
            variant_description=None,
            protected_origin=None,
            secrets=(),  # secrets aren't inheritable
            queued=False,
            waiting_status=None,  # Text description of why its waiting
        )

        self.attributes = {}
        self.attributes.update(self.context_attributes)
        self.attributes.update(self.execution_attributes)
        self.attributes.update(self.other_attributes)

        self.name = name

    def _getAffectedProjects(self, tenant):
        """
        Gets all projects that are required to run this job. This includes
        required_projects, referenced playbooks, roles and dependent changes.
        """
        project_canonical_names = set()
        project_canonical_names.update(self.required_projects.keys())
        project_canonical_names.update(self._projectsFromPlaybooks(
            itertools.chain(self.pre_run, [self.run[0]], self.post_run,
                            self.cleanup_run), with_implicit=True))
        return list(project_canonical_names)

    def _projectsFromPlaybooks(self, playbooks, with_implicit=False):
        for playbook in playbooks:
            # noop job does not have source_context
            if playbook.source_context:
                yield playbook.source_context.project_canonical_name
            for role in playbook.roles:
                if role.implicit and not with_implicit:
                    continue
                yield role.project_canonical_name

    def _freezePlaybook(self, layout, item, playbook, redact_secrets_and_keys):
        d = playbook.toDict(redact_secrets=redact_secrets_and_keys)
        for role in d['roles']:
            if role['type'] != 'zuul':
                continue
            project_metadata = layout.getProjectMetadata(
                role['project_canonical_name'])
            if project_metadata:
                role['project_default_branch'] = \
                    project_metadata.default_branch
            else:
                role['project_default_branch'] = 'master'
            role_trusted, role_project = item.pipeline.tenant.getProject(
                role['project_canonical_name'])
            role_connection = role_project.source.connection
            role['connection'] = role_connection.connection_name
            role['project'] = role_project.name
        return d

    def _deduplicateSecrets(self, secrets, playbook):
        # secrets is a list of secrets accumulated so far
        # playbook is a frozen playbook from _freezePlaybook

        # Cast to list so we can modify in place
        for secret_key, secret_value in list(playbook['secrets'].items()):
            if secret_value in secrets:
                playbook['secrets'][secret_key] = secrets.index(secret_value)
            else:
                secrets.append(secret_value)
                playbook['secrets'][secret_key] = len(secrets) - 1

    def freezeJob(self, context, tenant, layout, item,
                  redact_secrets_and_keys):
        buildset = item.current_build_set
        kw = {}
        attributes = (set(FrozenJob.attributes) |
                      set(FrozenJob.job_data_attributes))
        # De-duplicate the secrets across all playbooks, store them in
        # this array, and then refer to them by index.
        attributes.discard('secrets')
        attributes.discard('affected_projects')
        attributes.discard('config_hash')
        secrets = []
        for k in attributes:
            # If this is a config object, it's frozen, so it's
            # safe to shallow copy.
            v = getattr(self, k)
            if isinstance(v, frozenset):
                v = list(v)
            if isinstance(v, (dict, types.MappingProxyType)):
                v = Freezable.thaw(v)
            # On a frozen job, parent=None means a base job
            if v is self.BASE_JOB_MARKER:
                v = None
            # Playbooks have a lot of objects that can be flattened at
            # this point to simplify serialization.
            if k in ('pre_run', 'run', 'post_run', 'cleanup_run'):
                v = [self._freezePlaybook(layout, item, pb,
                                          redact_secrets_and_keys)
                     for pb in v if pb.source_context]
                if not redact_secrets_and_keys:
                    # If we're redacting, don't de-duplicate so that
                    # it's clear that the value ("REDACTED") is
                    # redacted.
                    for pb in v:
                        self._deduplicateSecrets(secrets, pb)
            kw[k] = v
        kw['secrets'] = secrets
        kw['affected_projects'] = self._getAffectedProjects(tenant)
        kw['config_hash'] = self.getConfigHash(tenant)
        # Don't add buildset to attributes since it's not serialized
        kw['buildset'] = buildset
        return FrozenJob.new(context, **kw)

    def getConfigHash(self, tenant):
        # Make a hash of the job configuration for determining whether
        # it has been updated.
        hasher = hashlib.sha256()
        job_dict = Freezable.thaw(self.toDict(tenant))
        # Ignore changes to file matchers since they don't affect
        # the content of the job.
        for attr in ['files', 'irrelevant_files',
                     'source_context', 'description']:
            job_dict.pop(attr, None)
        # Use json_dumps to strip any ZuulMark entries
        hasher.update(json_dumps(job_dict, sort_keys=True).encode('utf8'))
        return hasher.hexdigest()

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        # Compare the name and all inheritable attributes to determine
        # whether two jobs with the same name are identically
        # configured.  Useful upon reconfiguration.
        if not isinstance(other, Job):
            return False
        if self.name != other.name:
            return False
        for k, v in self.attributes.items():
            if getattr(self, k) != getattr(other, k):
                return False
        return True

    __hash__ = object.__hash__

    def __str__(self):
        return self.name

    def __repr__(self):
        ln = 0
        if self.start_mark:
            ln = self.start_mark.line + 1
        return '<Job %s branches: %s source: %s#%s>' % (
            self.name,
            self.branch_matcher,
            self.source_context,
            ln)

    def __getattr__(self, name):
        v = self.__dict__.get(name)
        if v is None:
            return self.attributes[name]
        return v

    def _get(self, name):
        return self.__dict__.get(name)

    def setBase(self, layout):
        self.inheritance_path = self.inheritance_path + (repr(self),)
        if self._get('run') is not None:
            self.run = self.freezePlaybooks(self.run, layout)
        if self._get('pre_run') is not None:
            self.pre_run = self.freezePlaybooks(self.pre_run, layout)
        if self._get('post_run') is not None:
            self.post_run = self.freezePlaybooks(self.post_run, layout)
        if self._get('cleanup_run') is not None:
            self.cleanup_run = self.freezePlaybooks(self.cleanup_run, layout)

    def getNodeSet(self, layout):
        if isinstance(self.nodeset, str):
            # This references an existing named nodeset in the layout.
            ns = layout.nodesets.get(self.nodeset)
            if ns is None:
                raise Exception(
                    'The nodeset "{nodeset}" was not found.'.format(
                        nodeset=self.nodeset))
            return ns
        return self.nodeset

    def validateReferences(self, layout):
        # Verify that references to other objects in the layout are
        # valid.
        if not self.isBase() and self.parent:
            layout.getJob(self.parent)

        ns = self.getNodeSet(layout)
        if layout.tenant.max_nodes_per_job != -1 and \
           len(ns) > layout.tenant.max_nodes_per_job:
            raise Exception(
                'The job "{job}" exceeds tenant '
                'max-nodes-per-job {maxnodes}.'.format(
                    job=self.name,
                    maxnodes=layout.tenant.max_nodes_per_job))

        for pb in self.pre_run + self.run + self.post_run + self.cleanup_run:
            pb.validateReferences(layout)

    def addRoles(self, roles):
        newroles = []
        # Start with a copy of the existing roles, but if any of them
        # are implicit roles which are identified as explicit in the
        # new roles list, replace them with the explicit version.
        changed = False
        for existing_role in self.roles:
            if existing_role in roles:
                new_role = roles[roles.index(existing_role)]
            else:
                new_role = None
            if (new_role and
                isinstance(new_role, ZuulRole) and
                isinstance(existing_role, ZuulRole) and
                existing_role.implicit and not new_role.implicit):
                newroles.append(new_role)
                changed = True
            else:
                newroles.append(existing_role)
        # Now add the new roles.
        for role in reversed(roles):
            if role not in newroles:
                newroles.insert(0, role)
                changed = True
        if changed:
            self.roles = tuple(newroles)

    def getBranches(self):
        # Return the raw branch list that match this job
        return self._branches

    def setBranchMatcher(self, branches, implied=False):
        # Set the branch matcher to match any of the supplied branches
        self._branches = branches
        matchers = []
        if implied:
            matcher_class = change_matcher.ImpliedBranchMatcher
        else:
            matcher_class = change_matcher.BranchMatcher
        for branch in branches:
            matchers.append(matcher_class(branch))
        self.branch_matcher = change_matcher.MatchAny(matchers)

    def setFileMatcher(self, files):
        # Set the file matcher to match any of the change files
        self._files = files
        matchers = []
        for fn in files:
            matchers.append(change_matcher.FileMatcher(fn))
        self.file_matcher = change_matcher.MatchAnyFiles(matchers)

    def setIrrelevantFileMatcher(self, irrelevant_files):
        # Set the irrelevant file matcher to match any of the change files
        self._irrelevant_files = irrelevant_files
        matchers = []
        for fn in irrelevant_files:
            matchers.append(change_matcher.FileMatcher(fn))
        self.irrelevant_file_matcher = change_matcher.MatchAllFiles(matchers)

    def updateVariables(self, other_vars, other_extra_vars, other_host_vars,
                        other_group_vars):
        if other_vars is not None:
            self.variables = Job._deepUpdate(self.variables, other_vars)
        if other_extra_vars is not None:
            self.extra_variables = Job._deepUpdate(
                self.extra_variables, other_extra_vars)
        if other_host_vars is not None:
            self.host_variables = Job._deepUpdate(
                self.host_variables, other_host_vars)
        if other_group_vars is not None:
            self.group_variables = Job._deepUpdate(
                self.group_variables, other_group_vars)

    def updateProjectVariables(self, project_vars):
        # Merge project/template variables directly into the job
        # variables.  Job variables override project variables.
        self.variables = Job._deepUpdate(project_vars, self.variables)

    def updateProjects(self, other_projects):
        required_projects = self.required_projects.copy()
        required_projects.update(other_projects)
        self.required_projects = required_projects

    @staticmethod
    def _deepUpdate(a, b):
        # Merge nested dictionaries if possible, otherwise, overwrite
        # the value in 'a' with the value in 'b'.

        ret = {}
        for k, av in a.items():
            if k not in b:
                ret[k] = av
        for k, bv in b.items():
            av = a.get(k)
            if (isinstance(av, (dict, types.MappingProxyType)) and
                isinstance(bv, (dict, types.MappingProxyType))):
                ret[k] = Job._deepUpdate(av, bv)
            else:
                ret[k] = bv
        return ret

    def copy(self):
        job = Job(self.name)
        for k in self.attributes:
            v = self._get(k)
            if v is not None:
                # If this is a config object, it's frozen, so it's
                # safe to shallow copy.
                setattr(job, k, v)
        return job

    def freezePlaybooks(self, pblist, layout):
        """Take a list of playbooks, and return a copy of it updated with this
        job's roles.

        """

        ret = []
        for old_pb in pblist:
            pb = old_pb.copy()
            pb.roles = self.roles
            pb.freezeSecrets(layout)
            ret.append(pb)
        return tuple(ret)

    def applyVariant(self, other, layout):
        """Copy the attributes which have been set on the other job to this
        job."""
        if not isinstance(other, Job):
            raise Exception("Job unable to inherit from %s" % (other,))

        for k in self.execution_attributes:
            if (other._get(k) is not None and
                k not in set(['final', 'abstract', 'protected',
                              'intermediate'])):
                if self.final:
                    raise Exception("Unable to modify final job %s attribute "
                                    "%s=%s with variant %s" % (
                                        repr(self), k, other._get(k),
                                        repr(other)))
                if self.protected_origin:
                    # this is a protected job, check origin of job definition
                    this_origin = self.protected_origin
                    other_origin = other.source_context.project_canonical_name
                    if this_origin != other_origin:
                        raise Exception("Job %s which is defined in %s is "
                                        "protected and cannot be inherited "
                                        "from other projects."
                                        % (repr(self), this_origin))
                if k not in set(['pre_run', 'run', 'post_run', 'cleanup_run',
                                 'roles', 'variables', 'extra_variables',
                                 'host_variables', 'group_variables',
                                 'required_projects', 'allowed_projects',
                                 'semaphores']):
                    setattr(self, k, other._get(k))

        # Don't set final above so that we don't trip an error halfway
        # through assignment.
        if other.final != self.attributes['final']:
            self.final = other.final

        # Abstract may not be reset by a variant, it may only be
        # cleared by inheriting.
        if other.name != self.name:
            self.abstract = other.abstract
        elif other.abstract:
            self.abstract = True

        # An intermediate job may only be inherited by an abstract
        # job.  Note intermediate jobs must be also be abstract, that
        # has been enforced during config reading.  Similar to
        # abstract, it is cleared by inheriting.
        if self.intermediate and not other.abstract:
            raise Exception("Intermediate job %s may only inherit "
                            "to another abstract job" %
                            (repr(self)))
        if other.name != self.name:
            self.intermediate = other.intermediate
        elif other.intermediate:
            self.intermediate = True

        # Protected may only be set to true
        if other.protected is not None:
            # don't allow to reset protected flag
            if not other.protected and self.protected_origin:
                raise Exception("Unable to reset protected attribute of job"
                                " %s by job %s" % (
                                    repr(self), repr(other)))
            if not self.protected_origin:
                self.protected_origin = \
                    other.source_context.project_canonical_name

        # We must update roles before any playbook contexts
        if other._get('roles') is not None:
            self.addRoles(other.roles)

        # Freeze the nodeset
        self.nodeset = self.getNodeSet(layout)

        # Pass secrets to parents
        secrets_for_parents = [s for s in other.secrets if s.pass_to_parent]
        if secrets_for_parents:
            frozen_secrets = []
            for secret_use in secrets_for_parents:
                secret = layout.secrets.get(secret_use.name)
                if secret is None:
                    raise Exception("Secret %s not found" % (secret_use.name,))
                secret_name = secret_use.alias
                encrypted_secret_data = secret.serialize()
                # Use the other project, not the secret's, because we
                # want to decrypt with the other project's key key.
                connection_name = other.source_context.project_connection_name
                project_name = other.source_context.project_name
                frozen_secrets.append(FrozenSecret.construct_cached(
                    connection_name, project_name,
                    secret_name, encrypted_secret_data))

            # Add the secrets to any existing playbooks.  If any of
            # them are in an untrusted project, then we've just given
            # a secret to a playbook which can run in dynamic config,
            # therefore it's no longer safe to run this job
            # pre-review.  The only way pass-to-parent can work with
            # pre-review pipeline is if all playbooks are in the
            # trusted context.
            for pb in itertools.chain(
                    self.pre_run, self.run, self.post_run, self.cleanup_run):
                pb.addSecrets(frozen_secrets)
                if not pb.source_context.trusted:
                    self.post_review = True

        if other._get('run') is not None:
            other_run = self.freezePlaybooks(other.run, layout)
            self.run = other_run
        if other._get('pre_run') is not None:
            other_pre_run = self.freezePlaybooks(other.pre_run, layout)
            self.pre_run = self.pre_run + other_pre_run
        if other._get('post_run') is not None:
            other_post_run = self.freezePlaybooks(other.post_run, layout)
            self.post_run = other_post_run + self.post_run
        if other._get('cleanup_run') is not None:
            other_cleanup_run = self.freezePlaybooks(other.cleanup_run, layout)
            self.cleanup_run = other_cleanup_run + self.cleanup_run
        self.updateVariables(other.variables, other.extra_variables,
                             other.host_variables, other.group_variables)
        if other._get('required_projects') is not None:
            self.updateProjects(other.required_projects)
        if (other._get('allowed_projects') is not None and
            self._get('allowed_projects') is not None):
            self.allowed_projects = frozenset(
                self.allowed_projects.intersection(
                    other.allowed_projects))
        elif other._get('allowed_projects') is not None:
            self.allowed_projects = other.allowed_projects
        if other._get('semaphores') is not None:
            # Sort the list of semaphores to avoid issues with
            # contention (where two jobs try to start at the same time
            # and fail due to acquiring the same semaphores but in
            # reverse order.
            self.semaphores = tuple(
                sorted(other.semaphores + self.semaphores,
                       key=lambda x: x.name))

        for k in self.context_attributes:
            if (other._get(k) is not None and
                k not in set(['tags', 'requires', 'provides'])):
                setattr(self, k, other._get(k))

        for k in ('tags', 'requires', 'provides'):
            if other._get(k) is not None:
                setattr(self, k, getattr(self, k).union(other._get(k)))

        self.inheritance_path = self.inheritance_path + (repr(other),)

    def changeMatchesBranch(self, change, override_branch=None):
        if override_branch is None:
            branch_change = change
        else:
            # If an override branch is supplied, create a very basic
            # change (a Ref) and set its branch to the override
            # branch.
            branch_change = Ref(change.project)
            branch_change.ref = override_branch

        if self.branch_matcher and not self.branch_matcher.matches(
                branch_change):
            return False
        return True

    def changeMatchesFiles(self, change):
        if self.file_matcher and not self.file_matcher.matches(change):
            return False

        # NB: This is a negative match.
        if (self.irrelevant_file_matcher and
            self.irrelevant_file_matcher.matches(change)):
            return False

        return True


class JobProject(ConfigObject):
    """ A reference to a project from a job. """

    def __init__(self, project_name, override_branch=None,
                 override_checkout=None):
        super(JobProject, self).__init__()
        self.project_name = project_name
        self.override_branch = override_branch
        self.override_checkout = override_checkout

    def toDict(self):
        d = dict()
        d['project_name'] = self.project_name
        d['override_branch'] = self.override_branch
        d['override_checkout'] = self.override_checkout
        return d

    @classmethod
    def fromDict(cls, data):
        return cls(data['project_name'],
                   data['override_branch'],
                   data['override_checkout'])


class JobSemaphore(ConfigObject):
    """ A reference to a semaphore from a job. """

    def __init__(self, semaphore_name, resources_first=False):
        super().__init__()
        self.name = semaphore_name
        self.resources_first = resources_first

    def toDict(self):
        d = dict()
        d['name'] = self.name
        d['resources_first'] = self.resources_first
        return d

    @classmethod
    def fromDict(cls, data):
        return cls(data['name'], data['resources_first'])


class JobList(ConfigObject):
    """ A list of jobs in a project's pipeline. """

    def __init__(self):
        super(JobList, self).__init__()
        self.jobs = OrderedDict()  # job.name -> [job, ...]

    def addJob(self, job):
        if job.name in self.jobs:
            self.jobs[job.name].append(job)
        else:
            self.jobs[job.name] = [job]

    def inheritFrom(self, other):
        for jobname, jobs in other.jobs.items():
            joblist = self.jobs.setdefault(jobname, [])
            for job in jobs:
                if job not in joblist:
                    joblist.append(job)


class JobDependency(ConfigObject):
    """ A reference to another job in the project-pipeline-config. """
    def __init__(self, name, soft=False):
        super(JobDependency, self).__init__()
        self.name = name
        self.soft = soft

    def toDict(self):
        return {'name': self.name,
                'soft': self.soft}

    @classmethod
    def fromDict(cls, data):
        return cls(data['name'], data['soft'])


class JobGraph(object):
    """A JobGraph represents the dependency graph between Jobs.

    This class is an attribute of the BuildSet, and should not be
    modified after its initial creation.
    """

    def __init__(self, job_map):
        # The jobs parameter is a reference to an attribute on the
        # BuildSet (either the real list of jobs, or a cached list of
        # "old" jobs for comparison).
        self._job_map = job_map
        # An ordered list of jobs
        self.jobs = []
        # dependent_job_name -> dict(parent_job_name -> soft)
        self._dependencies = {}
        self.project_metadata = {}

    def __repr__(self):
        return '<JobGraph %s>' % (self.jobs)

    def toDict(self):
        data = {
            "jobs": self.jobs,
            "dependencies": self._dependencies,
            "project_metadata": {
                k: v.toDict() for (k, v) in self.project_metadata.items()
            },
        }
        return data

    @classmethod
    def fromDict(klass, data, job_map):
        self = klass(job_map)
        self.jobs = data['jobs']
        self._dependencies = data['dependencies']
        self.project_metadata = {
            k: ProjectMetadata.fromDict(v)
            for (k, v) in data['project_metadata'].items()
        }
        return self

    def addJob(self, job):
        # A graph must be created after the job list is frozen,
        # therefore we should only get one job with the same name.
        if job.name in self.jobs:
            raise Exception("Job %s already added" % (job.name,))
        self._job_map[job.name] = job
        self.jobs.append(job.name)
        # Append the dependency information
        self._dependencies.setdefault(job.name, {})
        try:
            for dependency in job.dependencies:
                # Make sure a circular dependency is never created
                ancestor_jobs = self._getParentJobNamesRecursively(
                    dependency.name, soft=True)
                ancestor_jobs.add(dependency.name)
                if any((job.name == anc_job) for anc_job in ancestor_jobs):
                    raise Exception("Dependency cycle detected in job %s" %
                                    (job.name,))
                self._dependencies[job.name][dependency.name] = \
                    dependency.soft
        except Exception:
            del self._job_map[job.name]
            self.jobs.pop()
            del self._dependencies[job.name]
            raise

    def getJobs(self):
        # Report in the order of layout cfg
        return list([self._job_map[x] for x in self.jobs])

    def getDirectDependentJobs(self, parent_job, skip_soft=False):
        ret = set()
        for dependent_name, parents in self._dependencies.items():
            part = parent_job in parents \
                and (not skip_soft or not parents[parent_job])
            if part:
                ret.add(dependent_name)
        return ret

    def getDependentJobsRecursively(self, parent_job, skip_soft=False):
        all_dependent_jobs = set()
        jobs_to_iterate = set([parent_job])
        while len(jobs_to_iterate) > 0:
            current_job = jobs_to_iterate.pop()
            current_dependent_jobs = self.getDirectDependentJobs(current_job,
                                                                 skip_soft)
            new_dependent_jobs = current_dependent_jobs - all_dependent_jobs
            jobs_to_iterate |= new_dependent_jobs
            all_dependent_jobs |= new_dependent_jobs
        return [self._job_map[name] for name in all_dependent_jobs]

    def getParentJobsRecursively(self, dependent_job, layout=None,
                                 skip_soft=False):
        return [self._job_map[name] for name in
                self._getParentJobNamesRecursively(dependent_job,
                                                   layout=layout,
                                                   skip_soft=skip_soft)]

    def _getParentJobNamesRecursively(self, dependent_job, soft=False,
                                      layout=None, skip_soft=False):
        all_parent_jobs = set()
        jobs_to_iterate = set([(dependent_job, False)])
        while len(jobs_to_iterate) > 0:
            (current_job, current_soft) = jobs_to_iterate.pop()
            current_parent_jobs = self._dependencies.get(current_job)
            if skip_soft:
                hard_parent_jobs = \
                    {d: s for d, s in current_parent_jobs.items() if not s}
                current_parent_jobs = hard_parent_jobs
            if current_parent_jobs is None:
                if soft or current_soft:
                    if layout:
                        # If the caller supplied a layout, verify that
                        # the job exists to provide a helpful error
                        # message.  Called for exception side effect:
                        layout.getJob(current_job)
                    current_parent_jobs = {}
                else:
                    raise Exception("Job %s depends on %s which was not run." %
                                    (dependent_job, current_job))
            elif dependent_job != current_job:
                all_parent_jobs.add(current_job)
            new_parent_jobs = set(current_parent_jobs.keys()) - all_parent_jobs
            for j in new_parent_jobs:
                jobs_to_iterate.add((j, current_parent_jobs[j]))
        return all_parent_jobs

    def getProjectMetadata(self, name):
        if name in self.project_metadata:
            return self.project_metadata[name]
        return None


@total_ordering
class JobRequest:
    # States:
    UNSUBMITTED = "unsubmitted"
    REQUESTED = "requested"
    HOLD = "hold"  # Used by tests to stall processing
    RUNNING = "running"
    COMPLETED = "completed"

    ALL_STATES = (UNSUBMITTED, REQUESTED, HOLD, RUNNING, COMPLETED)

    def __init__(self, uuid, precedence=None, state=None, result_path=None):
        self.uuid = uuid
        if precedence is None:
            self.precedence = 0
        else:
            self.precedence = precedence

        if state is None:
            self.state = self.UNSUBMITTED
        else:
            self.state = state
        # Path to the future result if requested
        self.result_path = result_path

        # ZK related data not serialized
        self.path = None
        self._zstat = None
        self.lock = None

    def toDict(self):
        return {
            "uuid": self.uuid,
            "state": self.state,
            "precedence": self.precedence,
            "result_path": self.result_path,
        }

    def updateFromDict(self, data):
        self.precedence = data["precedence"]
        self.state = data["state"]
        self.result_path = data["result_path"]

    @classmethod
    def fromDict(cls, data):
        return cls(
            data["uuid"],
            precedence=data["precedence"],
            state=data["state"],
            result_path=data["result_path"]
        )

    def __lt__(self, other):
        # Sort requests by precedence and their creation time in
        # ZooKeeper in ascending order to prevent older requests from
        # starving.
        if self.precedence == other.precedence:
            if self._zstat and other._zstat:
                return self._zstat.ctime < other._zstat.ctime
            # NOTE (felix): As the _zstat should always be set when retrieving
            # the request from ZooKeeper, this branch shouldn't matter
            # much. It's just there, because the _zstat could - theoretically -
            # be None.
            return self.uuid < other.uuid
        return self.precedence < other.precedence

    def __eq__(self, other):
        same_prec = self.precedence == other.precedence
        if self._zstat and other._zstat:
            same_ctime = self._zstat.ctime == other._zstat.ctime
        else:
            same_ctime = self.uuid == other.uuid
        return same_prec and same_ctime

    def __repr__(self):
        return (f"<JobRequest {self.uuid}, state={self.state}, "
                f"path={self.path} zone={self.zone}>")


class MergeRequest(JobRequest):

    # Types:
    MERGE = "merge"
    CAT = "cat"
    REF_STATE = "refstate"
    FILES_CHANGES = "fileschanges"

    def __init__(self, uuid, job_type, build_set_uuid, tenant_name,
                 pipeline_name, event_id, precedence=None, state=None,
                 result_path=None):
        super().__init__(uuid, precedence, state, result_path)
        self.job_type = job_type
        self.build_set_uuid = build_set_uuid
        self.tenant_name = tenant_name
        self.pipeline_name = pipeline_name
        self.event_id = event_id

    def toDict(self):
        d = super().toDict()
        d.update({
            "job_type": self.job_type,
            "build_set_uuid": self.build_set_uuid,
            "tenant_name": self.tenant_name,
            "pipeline_name": self.pipeline_name,
            "event_id": self.event_id,
        })
        return d

    @classmethod
    def fromDict(cls, data):
        return cls(
            data["uuid"],
            data["job_type"],
            data["build_set_uuid"],
            data["tenant_name"],
            data["pipeline_name"],
            data["event_id"],
            precedence=data["precedence"],
            state=data["state"],
            result_path=data["result_path"]
        )

    def __repr__(self):
        return (
            f"<MergeRequest {self.uuid}, job_type={self.job_type}, "
            f"state={self.state}, path={self.path}>"
        )


class BuildRequest(JobRequest):
    """A request for a build in a specific zone"""

    # States:
    PAUSED = 'paused'

    ALL_STATES = JobRequest.ALL_STATES + (PAUSED,)

    def __init__(self, uuid, zone, build_set_uuid, job_name, tenant_name,
                 pipeline_name, event_id, precedence=None, state=None,
                 result_path=None):
        super().__init__(uuid, precedence, state, result_path)
        self.zone = zone
        self.build_set_uuid = build_set_uuid
        self.job_name = job_name
        self.tenant_name = tenant_name
        self.pipeline_name = pipeline_name
        self.event_id = event_id
        # The executor sets the worker info when it locks the build
        # request so that zuul web can use this information to
        # build the url for the live log stream.
        self.worker_info = None

    def toDict(self):
        d = super().toDict()
        d.update({
            "zone": self.zone,
            "build_set_uuid": self.build_set_uuid,
            "job_name": self.job_name,
            "tenant_name": self.tenant_name,
            "pipeline_name": self.pipeline_name,
            "event_id": self.event_id,
            "worker_info": self.worker_info,
        })
        return d

    @classmethod
    def fromDict(cls, data):
        request = cls(
            data["uuid"],
            data["zone"],
            data["build_set_uuid"],
            data["job_name"],
            data["tenant_name"],
            data["pipeline_name"],
            data["event_id"],
            precedence=data["precedence"],
            state=data["state"],
            result_path=data["result_path"]
        )

        request.worker_info = data["worker_info"]

        return request

    def __repr__(self):
        return (
            f"<BuildRequest {self.uuid}, job={self.job_name}, "
            f"state={self.state}, path={self.path} zone={self.zone}>"
        )


class ResultData(zkobject.ShardedZKObject):
    # If the node exists already, it is probably a half-written state
    # from a crash; truncate it and continue.
    truncate_on_create = True

    def __init__(self):
        super().__init__()
        self._set(data={})

    def getPath(self):
        return self._path

    def serialize(self):
        data = {
            "data": self.data,
            "_path": self._path,
        }
        return json.dumps(data, sort_keys=True).encode("utf8")


class Build(zkobject.ZKObject):
    """A Build is an instance of a single execution of a Job.

    While a Job describes what to run, a Build describes an actual
    execution of that Job.  Each build is associated with exactly one
    Job (related builds are grouped together in a BuildSet).
    """

    log = logging.getLogger("zuul.Build")

    def __init__(self):
        super().__init__()
        self._set(
            job=None,
            build_set=None,
            uuid=uuid4().hex,
            url=None,
            result=None,
            _result_data=None,
            _secret_result_data=None,
            error_detail=None,
            execute_time=time.time(),
            start_time=None,
            end_time=None,
            estimated_time=None,
            canceled=False,
            paused=False,
            retry=False,
            held=False,
            zuul_event_id=None,
            build_request_ref=None,
        )

    def serialize(self):
        data = {
            "uuid": self.uuid,
            "url": self.url,
            "result": self.result,
            "_result_data": (self._result_data.getPath()
                             if self._result_data else None),
            "_secret_result_data": (self._secret_result_data.getPath()
                                    if self._secret_result_data else None),
            "error_detail": self.error_detail,
            "execute_time": self.execute_time,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "estimated_time": self.estimated_time,
            "canceled": self.canceled,
            "paused": self.paused,
            "retry": self.retry,
            "held": self.held,
            "zuul_event_id": self.zuul_event_id,
            "build_request_ref": self.build_request_ref,
        }
        return json.dumps(data, sort_keys=True).encode("utf8")

    def deserialize(self, raw, context):
        data = super().deserialize(raw, context)

        # Result data can change (between a pause and build
        # completion) so de-serialize it every time.
        for k in ('_result_data', '_secret_result_data'):
            try:
                if data[k]:
                    data[k] = ResultData.fromZK(context, data[k])
            except Exception:
                self.log.exception("Failed to restore result data")
                data[k] = None
        return data

    def getPath(self):
        return f"{self.job.getPath()}/build/{self.uuid}"

    def __repr__(self):
        return ('<Build %s of %s voting:%s>' %
                (self.uuid, self.job.name, self.job.voting))

    @property
    def result_data(self):
        if self._result_data:
            return self._result_data.data
        return {}

    @property
    def secret_result_data(self):
        if self._secret_result_data:
            return self._secret_result_data.data
        return {}

    def setResultData(self, result_data, secret_result_data):
        if not self._active_context:
            raise Exception(
                "setResultData must be used with a context manager")
        self._result_data = ResultData.new(
            self._active_context,
            data=result_data,
            _path=self.getPath() + '/result_data')
        self._secret_result_data = ResultData.new(
            self._active_context,
            data=secret_result_data,
            _path=self.getPath() + '/secret_result_data')

    @property
    def failed(self):
        if self.result and self.result not in ['SUCCESS', 'SKIPPED']:
            return True
        return False

    @property
    def pipeline(self):
        return self.build_set.item.pipeline

    @property
    def log_url(self):
        log_url = self.result_data.get('zuul', {}).get('log_url')
        if log_url and log_url[-1] != '/':
            log_url = log_url + '/'
        return log_url

    def getSafeAttributes(self):
        return Attributes(uuid=self.uuid,
                          result=self.result,
                          error_detail=self.error_detail,
                          result_data=self.result_data)


class RepoFiles(zkobject.ShardedZKObject):
    """RepoFiles holds config-file content for per-project job config.

    When Zuul asks a merger to prepare a future multiple-repo state
    and collect Zuul configuration files so that we can dynamically
    load our configuration, this class provides cached access to that
    data for use by the Change which updated the config files and any
    changes that follow it in a ChangeQueue.

    It is attached to a BuildSet since the content of Zuul
    configuration files can change with each new BuildSet.
    """

    # If the node exists already, it is probably a half-written state
    # from a crash; truncate it and continue.
    truncate_on_create = True

    def __init__(self):
        super().__init__()
        self._set(connections={})

    def __repr__(self):
        return '<RepoFiles %s>' % self.connections

    def getFile(self, connection_name, project_name, branch, fn):
        host = self.connections.get(connection_name, {})
        return host.get(project_name, {}).get(branch, {}).get(fn)

    def getPath(self):
        return f"{self._buildset_path}/files"

    def serialize(self):
        data = {
            "connections": self.connections,
            "_buildset_path": self._buildset_path,
        }
        return json.dumps(data, sort_keys=True).encode("utf8")


class BaseRepoState(zkobject.ShardedZKObject):
    """RepoState holds the repo state for a buildset

    When Zuul performs a speculative merge before enqueing an item,
    the starting state of the repo (and the repos in any items ahead)
    before that merge is encoded in a RepoState so the process can be
    repeated by the executor.

    If jobs add required-projects, a second merge operation is
    performed for any repos not in the original.  A second RepoState
    object holds the additional information.  A second object is used
    instead of updating the first since these objects are sharded --
    this simplifies error detection and recovery if a scheduler
    crashes while writing them.  They are effectively immutable once
    written.

    It is attached to a BuildSet since the content of Zuul
    configuration files can change with each new BuildSet.
    """

    # If the node exists already, it is probably a half-written state
    # from a crash; truncate it and continue.
    truncate_on_create = True

    def __init__(self):
        super().__init__()
        self._set(state={})

    def serialize(self):
        data = {
            "state": self.state,
            "_buildset_path": self._buildset_path,
        }
        return json.dumps(data, sort_keys=True).encode("utf8")


class MergeRepoState(BaseRepoState):
    def getPath(self):
        return f"{self._buildset_path}/merge_repo_state"


class ExtraRepoState(BaseRepoState):
    def getPath(self):
        return f"{self._buildset_path}/extra_repo_state"


class BuildSet(zkobject.ZKObject):
    """A collection of Builds for one specific potential future repository
    state.

    When Zuul executes Builds for a change, it creates a Build to
    represent each execution of each job and a BuildSet to keep track
    of all the Builds running for that Change.  When Zuul re-executes
    Builds for a Change with a different configuration, all of the
    running Builds in the BuildSet for that change are aborted, and a
    new BuildSet is created to hold the Builds for the Jobs being
    run with the new configuration.

    A BuildSet also holds the UUID used to produce the Zuul Ref that
    builders check out.

    """

    log = logging.getLogger("zuul.BuildSet")

    # Merge states:
    NEW = 1
    PENDING = 2
    COMPLETE = 3

    states_map = {
        1: 'NEW',
        2: 'PENDING',
        3: 'COMPLETE',
    }

    def __init__(self):
        super().__init__()
        self._set(
            item=None,
            builds={},
            retry_builds={},
            result=None,
            uuid=uuid4().hex,
            commit=None,
            dependent_changes=None,
            merger_items=None,
            unable_to_merge=False,
            config_errors=None,  # ConfigurationErrorList or None
            failing_reasons=[],
            debug_messages=[],
            warning_messages=[],
            merge_state=self.NEW,
            nodeset_info={},  # job -> dict of nodeset info
            node_requests={},  # job -> request id
            files=None,
            merge_repo_state=None,  # The repo_state of the original merge
            extra_repo_state=None,  # Repo state for any additional projects
            tries={},
            files_state=self.NEW,
            repo_state_state=self.NEW,
            configured=False,
            fail_fast=False,
            job_graph=None,
            jobs={},
            # Cached job graph of previous layout; not serialized
            _old_job_graph=None,
            _old_jobs={},
        )

    def setFiles(self, items):
        if self.files is not None:
            raise Exception("Repo files can not be updated")
        if not self._active_context:
            raise Exception("setFiles must be used with a context manager")
        connections = {}
        for item in items:
            connection = connections.setdefault(item['connection'], {})
            project = connection.setdefault(item['project'], {})
            branch = project.setdefault(item['branch'], {})
            branch.update(item['files'])
        repo_files = RepoFiles.new(self._active_context,
                                   connections=connections,
                                   _buildset_path=self.getPath())
        self.files = repo_files

    @property
    def repo_state(self):
        d = {}
        for rs in (self.merge_repo_state, self.extra_repo_state):
            if not rs:
                continue
            for connection in rs.state.keys():
                if connection not in d:
                    d[connection] = {}
                d[connection].update(rs.state.get(connection, {}))
        return d

    def setConfigErrors(self, config_errors):
        if not self._active_context:
            raise Exception("setConfigErrors must be used "
                            "with a context manager")
        path = self.getPath() + '/config_errors/' + uuid4().hex
        el = ConfigurationErrorList.new(self._active_context,
                                        errors=config_errors,
                                        _path=path)
        self.config_errors = el

    def setMergeRepoState(self, repo_state):
        if self.merge_repo_state is not None:
            raise Exception("Merge repo state can not be updated")
        if not self._active_context:
            raise Exception("setMergeRepoState must be used "
                            "with a context manager")
        rs = MergeRepoState.new(self._active_context,
                                state=repo_state,
                                _buildset_path=self.getPath())
        self.merge_repo_state = rs

    def setExtraRepoState(self, repo_state):
        if self.extra_repo_state is not None:
            raise Exception("Extra repo state can not be updated")
        if not self._active_context:
            raise Exception("setExtraRepoState must be used "
                            "with a context manager")
        rs = ExtraRepoState.new(self._active_context,
                                state=repo_state,
                                _buildset_path=self.getPath())
        self.extra_repo_state = rs

    def getPath(self):
        return f"{self.item.getPath()}/buildset/{self.uuid}"

    def serialize(self):
        data = {
            # "item": self.item,
            "builds": {j: b.getPath() for j, b in self.builds.items()},
            "retry_builds": {j: [b.getPath() for b in l]
                             for j, l in self.retry_builds.items()},
            "result": self.result,
            "uuid": self.uuid,
            "commit": self.commit,
            "dependent_changes": self.dependent_changes,
            "merger_items": self.merger_items,
            "unable_to_merge": self.unable_to_merge,
            "config_errors": (self.config_errors.getPath()
                              if self.config_errors else None),
            "failing_reasons": self.failing_reasons,
            "debug_messages": self.debug_messages,
            "warning_messages": self.warning_messages,
            "merge_state": self.merge_state,
            "nodeset_info": self.nodeset_info,
            "node_requests": self.node_requests,
            "files": self.files and self.files.getPath(),
            "merge_repo_state": (self.merge_repo_state.getPath()
                                 if self.merge_repo_state else None),
            "extra_repo_state": (self.extra_repo_state.getPath()
                                 if self.extra_repo_state else None),
            "tries": self.tries,
            "files_state": self.files_state,
            "repo_state_state": self.repo_state_state,
            "configured": self.configured,
            "fail_fast": self.fail_fast,
            "job_graph": (self.job_graph.toDict()
                          if self.job_graph else None),
            # jobs (serialize as separate objects)
        }
        return json.dumps(data, sort_keys=True).encode("utf8")

    def deserialize(self, raw, context):
        data = super().deserialize(raw, context)
        # Set our UUID so that getPath() returns the correct path for
        # child objects.
        self._set(uuid=data["uuid"])

        # If we already have a repo files, we don't need to
        # deserialize since it's immutable.
        if self.files is not None:
            data["files"] = self.files
        else:
            try:
                if data["files"]:
                    data["files"] = RepoFiles.fromZK(context, data["files"])
            except Exception:
                self.log.exception("Failed to restore repo files")
                data["files"] = None

        # If we already have a repo state, we don't need to
        # deserialize since it's immutable.
        if self.merge_repo_state is not None:
            data['merge_repo_state'] = self.merge_repo_state
        else:
            try:
                if data['merge_repo_state']:
                    data['merge_repo_state'] = MergeRepoState.fromZK(
                        context, data["merge_repo_state"])
            except Exception:
                self.log.exception("Failed to restore merge repo state")
                data['merge_repo_state'] = None

        if self.extra_repo_state is not None:
            data['extra_repo_state'] = self.extra_repo_state
        else:
            try:
                if data['extra_repo_state']:
                    data['extra_repo_state'] = ExtraRepoState.fromZK(
                        context, data["extra_repo_state"])
            except Exception:
                self.log.exception("Failed to restore extra repo state")
                data['extra_repo_state'] = None

        config_errors = data.get('config_errors')
        if config_errors:
            if (self.config_errors and
                self.config_errors._path == config_errors):
                data['config_errors'] = self.config_errors
            else:
                data['config_errors'] = ConfigurationErrorList.fromZK(
                    context, data['config_errors'],
                    _path=data['config_errors'])
        else:
            data['config_errors'] = None

        # Job graphs are immutable
        if self.job_graph is not None:
            data['job_graph'] = self.job_graph
        elif data['job_graph']:
            data['job_graph'] = JobGraph.fromDict(data['job_graph'], self.jobs)

        builds = {}
        retry_builds = defaultdict(list)
        # Flatten dict with lists of retried builds
        existing_retry_builds = {b.getPath(): b
                                 for bl in self.retry_builds.values()
                                 for b in bl}
        # jobs (deserialize as separate objects)
        if data['job_graph']:
            for job_name in data['job_graph'].jobs:
                if job_name in self.jobs:
                    job = self.jobs[job_name]
                    job.refresh(context)
                else:
                    job_path = FrozenJob.jobPath(job_name, self.getPath())
                    job = FrozenJob.fromZK(context, job_path, buildset=self)
                    self.jobs[job_name] = job

                build_path = data["builds"].get(job_name)
                if build_path:
                    build = self.builds.get(job_name)
                    if build and build.getPath() == build_path:
                        build.refresh(context)
                    else:
                        build = Build.fromZK(
                            context, build_path, job=job, build_set=self)
                    builds[job_name] = build

                for retry_path in data["retry_builds"].get(job_name, []):
                    retry_build = existing_retry_builds.get(retry_path)
                    if retry_build and retry_build.getPath() == retry_path:
                        retry_build.refresh(context)
                    else:
                        retry_build = Build.fromZK(
                            context, retry_path, job=job, build_set=self)
                    retry_builds[job_name].append(retry_build)

        data.update({
            "builds": builds,
            "retry_builds": retry_builds,
            # These are local cache objects only valid for one pipeline run
            '_old_job_graph': None,
            '_old_jobs': {},
        })
        return data

    @property
    def ref(self):
        # NOTE(jamielennox): The concept of buildset ref is to be removed and a
        # buildset UUID identifier available instead. Currently the ref is
        # checked to see if the BuildSet has been configured.
        return 'Z' + self.uuid if self.configured else None

    def __repr__(self):
        return '<BuildSet item: %s #builds: %s merge state: %s>' % (
            self.item,
            len(self.builds),
            self.getStateName(self.merge_state))

    def setConfiguration(self, context):
        with self.activeContext(context):
            # The change isn't enqueued until after it's created
            # so we don't know what the other changes ahead will be
            # until jobs start.
            if self.dependent_changes is None:
                items = []
                if self.item.bundle:
                    items.extend(reversed(self.item.bundle.items))
                else:
                    items.append(self.item)

                items.extend(i for i in self.item.items_ahead
                             if i not in items)
                items.reverse()

                self.dependent_changes = [i.change.toDict() for i in items]
                self.merger_items = [i.makeMergerItem() for i in items]
            self.configured = True

    def getStateName(self, state_num):
        return self.states_map.get(
            state_num, 'UNKNOWN (%s)' % state_num)

    def addBuild(self, build):
        with self.activeContext(self.item.pipeline.manager.current_context):
            self.builds[build.job.name] = build
            if build.job.name not in self.tries:
                self.tries[build.job.name] = 1

    def addRetryBuild(self, build):
        with self.activeContext(self.item.pipeline.manager.current_context):
            self.retry_builds.setdefault(build.job.name, []).append(build)

    def removeBuild(self, build):
        if build.job.name not in self.builds:
            return
        with self.activeContext(self.item.pipeline.manager.current_context):
            self.tries[build.job.name] += 1
            del self.builds[build.job.name]

    def getBuild(self, job_name):
        return self.builds.get(job_name)

    def getBuilds(self):
        keys = list(self.builds.keys())
        keys.sort()
        return [self.builds.get(x) for x in keys]

    def getRetryBuildsForJob(self, job_name):
        return self.retry_builds.get(job_name, [])

    def getJobNodeSetInfo(self, job_name):
        # Return None if not provisioned; dict of info about nodes otherwise
        return self.nodeset_info.get(job_name)

    def getJobNodeProvider(self, job_name):
        info = self.getJobNodeSetInfo(job_name)
        if info:
            return info.get('provider')

    def getJobNodeExecutorZone(self, job_name):
        info = self.getJobNodeSetInfo(job_name)
        if info:
            return info.get('zone')

    def getJobNodeList(self, job_name):
        info = self.getJobNodeSetInfo(job_name)
        if info:
            return info.get('nodes')

    def removeJobNodeSetInfo(self, job_name):
        if job_name not in self.nodeset_info:
            raise Exception("No job nodeset for %s" % (job_name))
        with self.activeContext(self.item.pipeline.manager.current_context):
            del self.nodeset_info[job_name]

    def setJobNodeRequestID(self, job_name, request_id):
        if job_name in self.node_requests:
            raise Exception("Prior node request for %s" % (job_name))
        with self.activeContext(self.item.pipeline.manager.current_context):
            self.node_requests[job_name] = request_id

    def getJobNodeRequestID(self, job_name):
        return self.node_requests.get(job_name)

    def removeJobNodeRequestID(self, job_name):
        if job_name in self.node_requests:
            del self.node_requests[job_name]

    def jobNodeRequestComplete(self, job_name, nodeset):
        if job_name in self.nodeset_info:
            raise Exception("Prior node request for %s" % (job_name))
        info = {}
        if nodeset.nodes:
            node = nodeset.getNodes()[0]
            if node.attributes:
                info['zone'] = node.attributes.get('executor-zone')
            else:
                info['zone'] = None
            info['provider'] = node.provider
            info['nodes'] = [n.id for n in nodeset.getNodes()]
        with self.activeContext(self.item.pipeline.manager.current_context):
            self.nodeset_info[job_name] = info

    def getTries(self, job_name):
        return self.tries.get(job_name, 0)

    def getMergeMode(self):
        # We may be called before this build set has a shadow layout
        # (ie, we are called to perform the merge to create that
        # layout).  It's possible that the change we are merging will
        # update the merge-mode for the project, but there's not much
        # we can do about that here.  Instead, do the best we can by
        # using the nearest shadow layout to determine the merge mode,
        # or if that fails, the current live layout, or if that fails,
        # use the default: merge-resolve.
        item = self.item
        project = self.item.change.project
        project_metadata = None
        while item:
            if item.current_build_set.job_graph:
                project_metadata = item.current_build_set.job_graph.\
                    getProjectMetadata(
                        project.canonical_name)
                if project_metadata:
                    break
            item = item.item_ahead
        if not project_metadata:
            layout = self.item.pipeline.tenant.layout
            if layout:
                project_metadata = layout.getProjectMetadata(
                    project.canonical_name
                )
        if project_metadata:
            return project_metadata.merge_mode
        return MERGER_MERGE_RESOLVE

    def getSafeAttributes(self):
        return Attributes(uuid=self.uuid)


class QueueItem(zkobject.ZKObject):

    """Represents the position of a Change in a ChangeQueue.

    All Changes are enqueued into ChangeQueue in a QueueItem. The QueueItem
    holds the current `BuildSet` as well as all previous `BuildSets` that were
    produced for this `QueueItem`.
    """

    log = logging.getLogger("zuul.QueueItem")

    def __init__(self):
        super().__init__()
        self._set(
            uuid=uuid4().hex,
            pipeline=None,
            queue=None,
            change=None,  # a ref
            dequeued_needing_change=False,
            current_build_set=None,
            item_ahead=None,
            items_behind=[],
            enqueue_time=None,
            report_time=None,
            dequeue_time=None,
            reported=False,
            reported_start=False,
            quiet=False,
            active=False,  # Whether an item is within an active window
            live=True,  # Whether an item is intended to be processed at all
            layout_uuid=None,
            _cached_sql_results={},
            event=None,  # The trigger event that lead to this queue item

            # Additional container for connection specifig information to be
            # used by reporters throughout the lifecycle
            dynamic_state=defaultdict(dict),

            # A bundle holds other queue items that have to be successful
            # for the current queue item to succeed
            bundle=None,
            dequeued_bundle_failing=False
        )

    @classmethod
    def new(klass, context, **kw):
        obj = klass()
        obj._set(**kw)
        data = obj._trySerialize(context)
        obj._save(context, data, create=True)
        files_state = (BuildSet.COMPLETE if obj.change.files is not None
                       else BuildSet.NEW)
        obj.updateAttributes(context, current_build_set=BuildSet.new(
            context, item=obj, files_state=files_state))
        return obj

    def getPath(self):
        return self.itemPath(PipelineState.pipelinePath(self.pipeline),
                             self.uuid)

    @classmethod
    def itemPath(cls, pipeline_path, item_uuid):
        return f"{pipeline_path}/item/{item_uuid}"

    def serialize(self):
        if isinstance(self.event, TriggerEvent):
            event_type = "TriggerEvent"
        else:
            event_type = self.event.__class__.__name__

        data = {
            "uuid": self.uuid,
            # TODO: we need to also store some info about the change in
            # Zookeeper in order to show the change info on the status page.
            # This needs change cache and the API to resolve change by key.
            "change": self.change.cache_key,
            "dequeued_needing_change": self.dequeued_needing_change,
            "current_build_set": (self.current_build_set and
                                  self.current_build_set.getPath()),
            "item_ahead": self.item_ahead and self.item_ahead.getPath(),
            "items_behind": [i.getPath() for i in self.items_behind],
            "enqueue_time": self.enqueue_time,
            "report_time": self.report_time,
            "dequeue_time": self.dequeue_time,
            "reported": self.reported,
            "reported_start": self.reported_start,
            "quiet": self.quiet,
            "active": self.active,
            "live": self.live,
            "layout_uuid": self.layout_uuid,
            "event": {
                "type": event_type,
                "data": self.event.toDict(),
            },
            "dynamic_state": self.dynamic_state,
            "bundle": self.bundle and self.bundle.serialize(),
            "dequeued_bundle_failing": self.dequeued_bundle_failing,
        }
        return json.dumps(data, sort_keys=True).encode("utf8")

    def deserialize(self, raw, context):
        data = super().deserialize(raw, context)
        # Set our UUID so that getPath() returns the correct path for
        # child objects.
        self._set(uuid=data["uuid"])

        event_type = data["event"]["type"]
        if event_type == "TriggerEvent":
            event_class = (
                self.pipeline.manager.sched.connections.getTriggerEventClass(
                    data["event"]["data"]["driver_name"])
            )
        else:
            event_class = EventTypeIndex.event_type_mapping.get(event_type)

        if event_class is None:
            raise NotImplementedError(
                f"Event type {event_type} not deserializable")

        event = event_class.fromDict(data["event"]["data"])
        change = self.pipeline.manager.resolveChangeReferences(
            [data["change"]])[0]

        build_set = self.current_build_set
        if build_set and build_set.getPath() == data["current_build_set"]:
            build_set.refresh(context)
        else:
            build_set = (data["current_build_set"] and
                         BuildSet.fromZK(context, data["current_build_set"],
                                         item=self))

        data.update({
            "event": event,
            "change": change,
            "log": get_annotated_logger(self.log, event),
            "dynamic_state": defaultdict(dict, data["dynamic_state"]),
            "current_build_set": build_set,
        })
        data['_item_ahead'] = data.pop('item_ahead')
        data['_items_behind'] = data.pop('items_behind')
        return data

    def annotateLogger(self, logger):
        """Return an annotated logger with the trigger event"""
        return get_annotated_logger(logger, self.event)

    def __repr__(self):
        if self.pipeline:
            pipeline = self.pipeline.name
        else:
            pipeline = None
        return '<QueueItem %s for %s in %s>' % (
            self.uuid, self.change, pipeline)

    def resetAllBuilds(self):
        context = self.pipeline.manager.current_context
        old_build_set = self.current_build_set
        files_state = (BuildSet.COMPLETE if self.change.files is not None
                       else BuildSet.NEW)
        self.updateAttributes(
            context,
            current_build_set=BuildSet.new(context, item=self,
                                           files_state=files_state),
            layout_uuid=None)
        old_build_set.delete(context)

    def addBuild(self, build):
        self.current_build_set.addBuild(build)

    def addRetryBuild(self, build):
        self.current_build_set.addRetryBuild(build)

    def removeBuild(self, build):
        self.current_build_set.removeBuild(build)

    def setReportedResult(self, result):
        self.updateAttributes(self.pipeline.manager.current_context,
                              report_time=time.time())
        self.current_build_set.updateAttributes(
            self.pipeline.manager.current_context, result=result)

    def warning(self, msg):
        with self.current_build_set.activeContext(
                self.pipeline.manager.current_context):
            self.current_build_set.warning_messages.append(msg)
        self.log.info(msg)

    def freezeJobGraph(self, layout, context,
                       skip_file_matcher,
                       redact_secrets_and_keys):
        """Find or create actual matching jobs for this item's change and
        store the resulting job tree."""

        # TODO: move this and related methods to BuildSet
        ppc = layout.getProjectPipelineConfig(self)
        try:
            if ppc and ppc.debug:
                debug_messages = ppc.debug_messages.copy()
            else:
                debug_messages = None
            job_graph = layout.createJobGraph(
                context, self, ppc, skip_file_matcher, redact_secrets_and_keys,
                debug_messages)
            for job in job_graph.getJobs():
                # Ensure that each jobs's dependencies are fully
                # accessible.  This will raise an exception if not.
                job_graph.getParentJobsRecursively(job.name, layout)

            # Copy project metadata to job_graph since this must be independent
            # of the layout as we need it in order to prepare the context for
            # job execution.
            # The layout might be no longer available at this point, as the
            # scheduler submitting the job can be different from the one that
            # created the layout.
            job_graph.project_metadata = layout.project_metadata

            if debug_messages is None:
                debug_messages = self.current_build_set.debug_messages

            if ppc:
                fail_fast = ppc.fail_fast
            else:
                fail_fast = self.current_build_set.fail_fast
            self.current_build_set.updateAttributes(
                context, job_graph=job_graph,
                fail_fast=fail_fast,
                debug_messages=debug_messages)

        except Exception:
            self.current_build_set.updateAttributes(
                context, job_graph=None, _old_job_graph=None)
            raise

    def hasJobGraph(self):
        """Returns True if the item has a job graph."""
        return self.current_build_set.job_graph is not None

    def getJobs(self):
        if not self.live or not self.current_build_set.job_graph:
            return []
        return self.current_build_set.job_graph.getJobs()

    def getJob(self, name):
        return self.current_build_set.jobs.get(name)

    @property
    def items_ahead(self):
        item_ahead = self.item_ahead
        while item_ahead:
            yield item_ahead
            item_ahead = item_ahead.item_ahead

    def getNonLiveItemsAhead(self):
        items = [item for item in self.items_ahead if not item.live]
        return reversed(items)

    def haveAllJobsStarted(self):
        if not self.hasJobGraph():
            return False
        for job in self.getJobs():
            build = self.current_build_set.getBuild(job.name)
            if not build or not build.start_time:
                return False
        return True

    def areAllJobsComplete(self):
        if (self.current_build_set.config_errors or
            self.current_build_set.unable_to_merge):
            return True
        if not self.hasJobGraph():
            return False
        for job in self.getJobs():
            build = self.current_build_set.getBuild(job.name)
            if not build or not build.result:
                return False
        return True

    def didAllJobsSucceed(self):
        """Check if all jobs have completed with status SUCCESS.

        Return True if all voting jobs have completed with status
        SUCCESS.  Non-voting jobs are ignored.  Skipped jobs are
        ignored, but skipping all jobs returns a failure.  Incomplete
        builds are considered a failure, hence this is unlikely to be
        useful unless all builds are complete.

        """
        if not self.hasJobGraph():
            return False

        all_jobs_skipped = True
        for job in self.getJobs():
            build = self.current_build_set.getBuild(job.name)
            if build:
                # If the build ran, record whether or not it was skipped
                # and return False if the build was voting and has an
                # unsuccessful return value
                if build.result != 'SKIPPED':
                    all_jobs_skipped = False
                if job.voting and build.result not in ['SUCCESS', 'SKIPPED']:
                    return False
            elif job.voting:
                # If the build failed to run and was voting that is an
                # unsuccessful build. But we don't count against it if not
                # voting.
                return False

        # NOTE(pabelanger): We shouldn't be able to skip all jobs.
        if all_jobs_skipped:
            return False

        return True

    def hasAnyJobFailed(self):
        """Check if any jobs have finished with a non-success result.

        Return True if any job in the job graph has returned with a
        status not equal to SUCCESS or SKIPPED, else return False.
        Non-voting and in-flight jobs are ignored.

        """
        if not self.hasJobGraph():
            return False
        for job in self.getJobs():
            if not job.voting:
                continue
            build = self.current_build_set.getBuild(job.name)
            if (build and build.result and
                    build.result not in ['SUCCESS', 'SKIPPED']):
                return True
        return False

    def isBundleFailing(self):
        if self.bundle:
            # We are only checking other items that share the same change
            # queue, since we don't need to wait for changes in other change
            # queues.
            return self.bundle.failed_reporting or any(
                i.hasAnyJobFailed() or i.didMergerFail()
                for i in self.bundle.items
                if i.live and i.queue == self.queue)
        return False

    def didBundleFinish(self):
        if self.bundle:
            # We are only checking other items that share the same change
            # queue, since we don't need to wait for changes in other change
            # queues.
            return all(i.areAllJobsComplete() for i in self.bundle.items if
                       i.live and i.queue == self.queue)
        return True

    def didBundleStartReporting(self):
        if self.bundle:
            return self.bundle.started_reporting
        return False

    def cannotMergeBundle(self):
        if self.bundle:
            return self.bundle.cannot_merge
        return False

    def didMergerFail(self):
        return self.current_build_set.unable_to_merge

    def getConfigErrors(self):
        if self.current_build_set.config_errors:
            return self.current_build_set.config_errors.errors
        return []

    def wasDequeuedNeedingChange(self):
        return self.dequeued_needing_change

    def includesConfigUpdates(self):
        includes_trusted = False
        includes_untrusted = False
        tenant = self.pipeline.tenant
        item = self

        if item.bundle:
            # Check all items in the bundle for config updates
            for bundle_item in item.bundle.items:
                if bundle_item.change.updatesConfig(tenant):
                    trusted, project = tenant.getProject(
                        bundle_item.change.project.canonical_name)
                    if trusted:
                        includes_trusted = True
                    else:
                        includes_untrusted = True
                if includes_trusted and includes_untrusted:
                    # We're done early
                    return includes_trusted, includes_untrusted

        while item:
            if item.change.updatesConfig(tenant):
                (trusted, project) = tenant.getProject(
                    item.change.project.canonical_name)
                if trusted:
                    includes_trusted = True
                else:
                    includes_untrusted = True
            if includes_trusted and includes_untrusted:
                # We're done early
                return (includes_trusted, includes_untrusted)
            item = item.item_ahead
        return (includes_trusted, includes_untrusted)

    def isHoldingFollowingChanges(self):
        if not self.live:
            return False
        if not self.hasJobGraph():
            return False
        for job in self.getJobs():
            if not job.hold_following_changes:
                continue
            build = self.current_build_set.getBuild(job.name)
            if not build:
                return True
            if build.result != 'SUCCESS':
                return True

        if not self.item_ahead:
            return False
        return self.item_ahead.isHoldingFollowingChanges()

    def _getRequirementsResultFromSQL(self, job):
        # This either returns data or raises an exception
        requirements = job.requires
        self.log.debug("Checking DB for requirements")
        requirements_tuple = tuple(sorted(requirements))
        if requirements_tuple not in self._cached_sql_results:
            conn = self.pipeline.manager.sched.connections.getSqlConnection()
            if conn:
                builds = conn.getBuilds(
                    tenant=self.pipeline.tenant.name,
                    project=self.change.project.name,
                    pipeline=self.pipeline.name,
                    change=self.change.number,
                    branch=self.change.branch,
                    patchset=self.change.patchset,
                    provides=requirements_tuple)
            else:
                builds = []
            # Just look at the most recent buildset.
            # TODO: query for a buildset instead of filtering.
            builds = [b for b in builds
                      if b.buildset.uuid == builds[0].buildset.uuid]
            self._cached_sql_results[requirements_tuple] = builds

        builds = self._cached_sql_results[requirements_tuple]
        data = []
        if not builds:
            self.log.debug("No artifacts matching requirements found in DB")
            return data

        for build in builds:
            if build.result != 'SUCCESS':
                provides = [x.name for x in build.provides]
                requirement = list(requirements.intersection(set(provides)))
                raise RequirementsError(
                    'Job %s requires artifact(s) %s provided by build %s '
                    '(triggered by change %s on project %s), but that build '
                    'failed with result "%s"' % (
                        job.name, ', '.join(requirement), build.uuid,
                        build.buildset.change, build.buildset.project,
                        build.result))
            else:
                for a in build.artifacts:
                    artifact = {'name': a.name,
                                'url': a.url,
                                'project': build.buildset.project,
                                'change': str(build.buildset.change),
                                'patchset': build.buildset.patchset,
                                'job': build.job_name}
                    if a.meta:
                        artifact['metadata'] = json.loads(a.meta)
                    data.append(artifact)
        self.log.debug("Found artifacts in DB: %s", repr(data))
        return data

    def providesRequirements(self, job, data, recurse=True):
        # Mutates data and returns true/false if requirements
        # satisfied.
        requirements = job.requires
        if not requirements:
            return True
        if not self.live:
            self.log.debug("Checking whether non-live item %s provides %s",
                           self, requirements)
            # Look for this item in other queues in the pipeline.
            item = None
            found = False
            for item in self.pipeline.getAllItems():
                if item.live and item.change == self.change:
                    found = True
                    break
            if found:
                if not item.providesRequirements(job, data,
                                                 recurse=False):
                    return False
            else:
                # Look for this item in the SQL DB.
                data += self._getRequirementsResultFromSQL(job)
        if self.hasJobGraph():
            for _job in self.getJobs():
                if _job.provides.intersection(requirements):
                    build = self.current_build_set.getBuild(_job.name)
                    if not build:
                        return False
                    if build.result and build.result != 'SUCCESS':
                        return False
                    if not build.result and not build.paused:
                        return False
                    artifacts = get_artifacts_from_result_data(
                        build.result_data,
                        logger=self.log)
                    for a in artifacts:
                        a.update({'project': self.change.project.name,
                                  'change': self.change.number,
                                  'patchset': self.change.patchset,
                                  'job': build.job.name})
                    self.log.debug("Found live artifacts: %s", repr(artifacts))
                    data += artifacts
        if not self.item_ahead:
            return True
        if not recurse:
            return True
        return self.item_ahead.providesRequirements(job, data)

    def jobRequirementsReady(self, job):
        if not self.item_ahead:
            return True
        try:
            data = []
            ret = self.item_ahead.providesRequirements(job, data)
            data.reverse()
            job.setArtifactData(data)
        except RequirementsError as e:
            self.warning(str(e))
            fakebuild = Build.new(self.pipeline.manager.current_context,
                                  job=job, build_set=self.current_build_set,
                                  result='FAILURE')
            self.addBuild(fakebuild)
            self.setResult(fakebuild)
            ret = False
        return ret

    def findJobsToRun(self, semaphore_handler):
        torun = []
        if not self.live:
            return []
        if not self.current_build_set.job_graph:
            return []
        if self.item_ahead:
            # Only run jobs if any 'hold' jobs on the change ahead
            # have completed successfully.
            if self.item_ahead.isHoldingFollowingChanges():
                return []

        job_graph = self.current_build_set.job_graph
        failed_job_names = set()  # Jobs that run and failed
        ignored_job_names = set()  # Jobs that were skipped or canceled
        unexecuted_job_names = set()  # Jobs that were not started yet
        jobs_not_started = set()
        for job in job_graph.getJobs():
            build = self.current_build_set.getBuild(job.name)
            if build:
                if build.result == 'SUCCESS' or build.paused:
                    pass
                elif build.result == 'SKIPPED':
                    ignored_job_names.add(job.name)
                else:  # elif build.result in ('FAILURE', 'CANCELED', ...):
                    failed_job_names.add(job.name)
            else:
                unexecuted_job_names.add(job.name)
                jobs_not_started.add(job)

        # Attempt to run jobs in the order they appear in
        # configuration.
        for job in job_graph.getJobs():
            if job not in jobs_not_started:
                continue
            if not self.jobRequirementsReady(job):
                continue
            all_parent_jobs_successful = True
            parent_builds_with_data = {}
            for parent_job in job_graph.getParentJobsRecursively(
                    job.name):
                if parent_job.name in unexecuted_job_names \
                        or parent_job.name in failed_job_names:
                    all_parent_jobs_successful = False
                    break
                parent_build = self.current_build_set.getBuild(parent_job.name)
                if parent_build.result_data:
                    parent_builds_with_data[parent_job.name] = parent_build

            for parent_job in job_graph.getParentJobsRecursively(
                    job.name, skip_soft=True):
                if parent_job.name in ignored_job_names:
                    all_parent_jobs_successful = False
                    break

            if all_parent_jobs_successful:
                # Iterate over all jobs of the graph (which is
                # in sorted config order) and apply parent data of the jobs we
                # already found.
                if len(parent_builds_with_data) > 0:
                    # We have all of the parent data here, so we can
                    # start from scratch each time.
                    new_parent_data = {}
                    new_secret_parent_data = {}
                    # We may have artifact data from
                    # jobRequirementsReady, so we preserve it.
                    # updateParentData de-duplicates it.
                    new_artifact_data = job.artifact_data or []
                    for parent_job in job_graph.getJobs():
                        parent_build = parent_builds_with_data.get(
                            parent_job.name)
                        if parent_build:
                            (new_parent_data,
                             new_secret_parent_data,
                             new_artifact_data) = FrozenJob.updateParentData(
                                 new_parent_data,
                                 new_secret_parent_data,
                                 new_artifact_data,
                                 parent_build)
                    job.setParentData(new_parent_data,
                                      new_secret_parent_data,
                                      new_artifact_data)

                nodeset = self.current_build_set.getJobNodeSetInfo(job.name)
                if nodeset is None:
                    # The nodes for this job are not ready, skip
                    # it for now.
                    continue
                if semaphore_handler.acquire(self, job, False):
                    # If this job needs a semaphore, either acquire it or
                    # make sure that we have it before running the job.
                    torun.append(job)
        return torun

    def findJobsToRequest(self, semaphore_handler):
        build_set = self.current_build_set
        toreq = []
        if not self.live:
            return []
        if not self.current_build_set.job_graph:
            return []
        if self.item_ahead:
            if self.item_ahead.isHoldingFollowingChanges():
                return []

        job_graph = self.current_build_set.job_graph
        failed_job_names = set()       # Jobs that run and failed
        ignored_job_names = set()      # Jobs that were skipped or canceled
        unexecuted_job_names = set()   # Jobs that were not started yet
        jobs_not_requested = set()
        for job in job_graph.getJobs():
            build = build_set.getBuild(job.name)
            if build and (build.result == 'SUCCESS' or build.paused):
                pass
            elif build and build.result == 'SKIPPED':
                ignored_job_names.add(job.name)
            elif build and build.result in ('FAILURE', 'CANCELED'):
                failed_job_names.add(job.name)
            else:
                unexecuted_job_names.add(job.name)
                nodeset = build_set.getJobNodeSetInfo(job.name)
                if nodeset is None:
                    req_id = build_set.getJobNodeRequestID(job.name)
                    if req_id is None:
                        jobs_not_requested.add(job)
                    else:
                        # This may have been reset due to a reconfig;
                        # since we know there is a queued request for
                        # it, set it here.
                        if job.queued is not True:
                            job.updateAttributes(
                                self.pipeline.manager.current_context,
                                queued=True)

        # Attempt to request nodes for jobs in the order jobs appear
        # in configuration.
        for job in job_graph.getJobs():
            if job not in jobs_not_requested:
                continue
            if not self.jobRequirementsReady(job):
                job.setWaitingStatus('requirements: {}'.format(
                    ', '.join(job.requires)))
                continue

            # Some set operations to figure out what jobs we really need:
            all_dep_jobs_successful = True
            # Every parent job (dependency), whether soft or hard:
            all_dep_job_names = set(
                [x.name for x in
                 job_graph.getParentJobsRecursively(job.name)])
            # Only the hard deps:
            hard_dep_job_names = set(
                [x.name for x in job_graph.getParentJobsRecursively(
                    job.name, skip_soft=True)])
            # Any dep that hasn't finished (or started) running
            unexecuted_dep_job_names = unexecuted_job_names & all_dep_job_names
            # Any dep that has finished and failed
            failed_dep_job_names = failed_job_names & all_dep_job_names
            ignored_hard_dep_job_names = hard_dep_job_names & ignored_job_names
            # We can't proceed if there are any:
            # * Deps that haven't finished running
            #     (this includes soft deps that haven't skipped)
            # * Deps that have failed
            # * Hard deps that were skipped
            required_dep_job_names = (
                unexecuted_dep_job_names |
                failed_dep_job_names |
                ignored_hard_dep_job_names)
            if required_dep_job_names:
                job.setWaitingStatus('dependencies: {}'.format(
                    ', '.join(required_dep_job_names)))
                all_dep_jobs_successful = False

            if all_dep_jobs_successful:
                if semaphore_handler.acquire(self, job, True):
                    # If this job needs a semaphore, either acquire it or
                    # make sure that we have it before requesting the nodes.
                    toreq.append(job)
                    if job.queued is not True:
                        job.updateAttributes(
                            self.pipeline.manager.current_context,
                            queued=True)
                else:
                    sem_names = ','.join([s.name for s in job.semaphores])
                    job.setWaitingStatus('semaphores: {}'.format(sem_names))
        return toreq

    def setResult(self, build):
        if build.retry:
            self.addRetryBuild(build)
            self.removeBuild(build)
            return

        buildset = self.current_build_set
        job_graph = self.current_build_set.job_graph
        skipped = []
        # NOTE(pabelanger): Check successful/paused jobs to see if
        # zuul_return includes zuul.child_jobs.
        build_result = build.result_data.get('zuul', {})
        if ((build.result == 'SUCCESS' or build.paused)
                and 'child_jobs' in build_result):
            zuul_return = build_result.get('child_jobs', [])
            dependent_jobs = job_graph.getDirectDependentJobs(
                build.job.name)

            if not zuul_return:
                # If zuul.child_jobs exists and is empty, the user
                # wants to skip all child jobs.
                to_skip = job_graph.getDependentJobsRecursively(
                    build.job.name, skip_soft=True)
                skipped += to_skip
            else:
                # The user supplied a list of jobs to run.
                intersect_jobs = dependent_jobs.intersection(zuul_return)

                for skip in (dependent_jobs - intersect_jobs):
                    s = buildset.jobs.get(skip)
                    skipped.append(s)
                    to_skip = job_graph.getDependentJobsRecursively(
                        skip, skip_soft=True)
                    skipped += to_skip

        elif build.result != 'SUCCESS' and not build.paused:
            to_skip = job_graph.getDependentJobsRecursively(
                build.job.name)
            skipped += to_skip

        for job in skipped:
            child_build = self.current_build_set.getBuild(job.name)
            if not child_build:
                fakebuild = Build.new(self.pipeline.manager.current_context,
                                      job=job,
                                      build_set=self.current_build_set,
                                      result='SKIPPED')
                self.addBuild(fakebuild)

    def setNodeRequestFailure(self, job):
        fakebuild = Build.new(
            self.pipeline.manager.current_context,
            job=job,
            build_set=self.current_build_set,
            start_time=time.time(),
            end_time=time.time(),
            result='NODE_FAILURE',
        )
        self.addBuild(fakebuild)
        self.setResult(fakebuild)

    def setDequeuedNeedingChange(self):
        self.updateAttributes(
            self.pipeline.manager.current_context,
            dequeued_needing_change=True)
        self._setAllJobsSkipped()

    def setDequeuedBundleFailing(self):
        self.updateAttributes(
            self.pipeline.manager.current_context,
            dequeued_bundle_failing=True)
        self._setMissingJobsSkipped()

    def setUnableToMerge(self):
        self.current_build_set.updateAttributes(
            self.pipeline.manager.current_context, unable_to_merge=True)
        self._setAllJobsSkipped()

    def setConfigError(self, error):
        err = ConfigurationError(None, None, error)
        self.setConfigErrors([err])

    def setConfigErrors(self, errors):
        # The manager may call us with the same errors object to
        # trigger side effects of setting jobs to 'skipped'.
        if (self.current_build_set.config_errors and
            self.current_build_set.config_errors != errors):
            # TODO: This is not expected, but if it happens we should
            # look into cleaning up leaked config_errors objects in
            # zk.
            self.log.warning("Differing config errors set on item %s",
                             self)
        if self.current_build_set.config_errors != errors:
            with self.current_build_set.activeContext(
                    self.pipeline.manager.current_context):
                self.current_build_set.setConfigErrors(errors)
        self._setAllJobsSkipped()

    def _setAllJobsSkipped(self):
        for job in self.getJobs():
            fakebuild = Build.new(self.pipeline.manager.current_context,
                                  job=job, build_set=self.current_build_set,
                                  result='SKIPPED')
            self.addBuild(fakebuild)

    def _setMissingJobsSkipped(self):
        for job in self.getJobs():
            if job.name in self.current_build_set.builds:
                # We already have a build for this job
                continue
            fakebuild = Build.new(self.pipeline.manager.current_context,
                                  job=job, build_set=self.current_build_set,
                                  result='SKIPPED')
            self.addBuild(fakebuild)

    def getNodePriority(self):
        return self.pipeline.manager.getNodePriority(self)

    def formatUrlPattern(self, url_pattern, job=None, build=None):
        url = None
        # Produce safe versions of objects which may be useful in
        # result formatting, but don't allow users to crawl through
        # the entire data structure where they might be able to access
        # secrets, etc.
        safe_change = self.change.getSafeAttributes()
        safe_pipeline = self.pipeline.getSafeAttributes()
        safe_tenant = self.pipeline.tenant.getSafeAttributes()
        safe_buildset = self.current_build_set.getSafeAttributes()
        safe_job = job.getSafeAttributes() if job else {}
        safe_build = build.getSafeAttributes() if build else {}
        try:
            url = url_pattern.format(change=safe_change,
                                     pipeline=safe_pipeline,
                                     tenant=safe_tenant,
                                     buildset=safe_buildset,
                                     job=safe_job,
                                     build=safe_build)
        except KeyError as e:
            self.log.error("Error while formatting url for job %s: unknown "
                           "key %s in pattern %s"
                           % (job, e.args[0], url_pattern))
        except AttributeError as e:
            self.log.error("Error while formatting url for job %s: unknown "
                           "attribute %s in pattern %s"
                           % (job, e.args[0], url_pattern))
        except Exception:
            self.log.exception("Error while formatting url for job %s with "
                               "pattern %s:" % (job, url_pattern))

        return url

    def formatJobResult(self, job, build=None):
        if build is None:
            build = self.current_build_set.getBuild(job.name)
        pattern = urllib.parse.urljoin(self.pipeline.tenant.web_root,
                                       'build/{build.uuid}')
        url = self.formatUrlPattern(pattern, job, build)
        result = build.result
        if result == 'SUCCESS':
            if job.success_message:
                result = job.success_message
        else:
            if job.failure_message:
                result = job.failure_message
        return (result, url)

    def formatStatusUrl(self):
        # If we don't have a web root set, we can't format any url
        if not self.pipeline.tenant.web_root:
            # Apparently we have no website
            return None

        if self.current_build_set.result:
            # We have reported (or are reporting) and so we should
            # send the buildset page url
            pattern = urllib.parse.urljoin(
                self.pipeline.tenant.web_root, "buildset/{buildset.uuid}"
            )
            return self.formatUrlPattern(pattern)

        # We haven't reported yet (or we don't have a database), so
        # the best we can do at the moment is send the status page
        # url.  TODO: require a database, insert buildsets into it
        # when they are created, and remove this case.
        pattern = urllib.parse.urljoin(
            self.pipeline.tenant.web_root,
            "status/change/{change.number},{change.patchset}",
        )
        return self.formatUrlPattern(pattern)

    def formatJSON(self, websocket_url=None):
        ret = {}
        ret['active'] = self.active
        ret['live'] = self.live
        if hasattr(self.change, 'url') and self.change.url is not None:
            ret['url'] = self.change.url
        else:
            ret['url'] = None
        if hasattr(self.change, 'ref') and self.change.ref is not None:
            ret['ref'] = self.change.ref
        else:
            ret['ref'] = None
        ret['id'] = self.change._id()
        if self.item_ahead:
            ret['item_ahead'] = self.item_ahead.change._id()
        else:
            ret['item_ahead'] = None
        ret['items_behind'] = [i.change._id() for i in self.items_behind]
        ret['failing_reasons'] = self.current_build_set.failing_reasons
        ret['zuul_ref'] = self.current_build_set.ref
        if self.change.project:
            ret['project'] = self.change.project.name
            ret['project_canonical'] = self.change.project.canonical_name
        else:
            # For cross-project dependencies with the depends-on
            # project not known to zuul, the project is None
            # Set it to a static value
            ret['project'] = "Unknown Project"
            ret['project_canonical'] = "Unknown Project"
        ret['enqueue_time'] = int(self.enqueue_time * 1000)
        ret['jobs'] = []
        if hasattr(self.change, 'owner'):
            ret['owner'] = self.change.owner
        else:
            ret['owner'] = None
        max_remaining = 0
        for job in self.getJobs():
            now = time.time()
            build = self.current_build_set.getBuild(job.name)
            elapsed = None
            remaining = None
            result = None
            build_url = None
            finger_url = None
            report_url = None
            if build:
                result = build.result
                finger_url = build.url
                # TODO(tobiash): add support for custom web root
                urlformat = 'stream/{build.uuid}?' \
                            'logfile=console.log'
                if websocket_url:
                    urlformat += '&websocket_url={websocket_url}'
                build_url = urlformat.format(
                    build=build, websocket_url=websocket_url)
                (unused, report_url) = self.formatJobResult(job)
                if build.start_time:
                    if build.end_time:
                        elapsed = int((build.end_time -
                                       build.start_time) * 1000)
                        remaining = 0
                    else:
                        elapsed = int((now - build.start_time) * 1000)
                        if build.estimated_time:
                            remaining = max(
                                int(build.estimated_time * 1000) - elapsed,
                                0)
            if remaining and remaining > max_remaining:
                max_remaining = remaining

            waiting_status = None
            if not (job.queued or result):
                waiting_status = job.waiting_status

            ret['jobs'].append({
                'name': job.name,
                'dependencies': [x.name for x in job.dependencies],
                'elapsed_time': elapsed,
                'remaining_time': remaining,
                'url': build_url,
                'finger_url': finger_url,
                'report_url': report_url,
                'result': result,
                'voting': job.voting,
                'uuid': build.uuid if build else None,
                'execute_time': build.execute_time if build else None,
                'start_time': build.start_time if build else None,
                'end_time': build.end_time if build else None,
                'estimated_time': build.estimated_time if build else None,
                'pipeline': build.pipeline.name if build else None,
                'canceled': build.canceled if build else None,
                'paused': build.paused if build else None,
                'retry': build.retry if build else None,
                'tries': self.current_build_set.getTries(job.name),
                'queued': job.queued,
                'waiting_status': waiting_status,
            })

        if self.haveAllJobsStarted():
            ret['remaining_time'] = max_remaining
        else:
            ret['remaining_time'] = None
        return ret

    def formatStatus(self, indent=0, html=False):
        indent_str = ' ' * indent
        ret = ''
        if html and getattr(self.change, 'url', None) is not None:
            ret += '%sProject %s change <a href="%s">%s</a>\n' % (
                indent_str,
                self.change.project.name,
                self.change.url,
                self.change._id())
        else:
            ret += '%sProject %s change %s based on %s\n' % (
                indent_str,
                self.change.project.name,
                self.change._id(),
                self.item_ahead)
        for job in self.getJobs():
            build = self.current_build_set.getBuild(job.name)
            if build:
                result = build.result
            else:
                result = None
            job_name = job.name
            if not job.voting:
                voting = ' (non-voting)'
            else:
                voting = ''
            if html:
                if build:
                    url = build.url
                else:
                    url = None
                if url is not None:
                    job_name = '<a href="%s">%s</a>' % (url, job_name)
            ret += '%s  %s: %s%s' % (indent_str, job_name, result, voting)
            ret += '\n'
        return ret

    def makeMergerItem(self):
        # Create a dictionary with all info about the item needed by
        # the merger.
        number = None
        patchset = None
        oldrev = None
        newrev = None
        branch = None
        if hasattr(self.change, 'number'):
            number = self.change.number
            patchset = self.change.patchset
        if hasattr(self.change, 'newrev'):
            oldrev = self.change.oldrev
            newrev = self.change.newrev
        if hasattr(self.change, 'branch'):
            branch = self.change.branch

        source = self.change.project.source
        connection_name = source.connection.connection_name
        project = self.change.project

        return dict(project=project.name,
                    connection=connection_name,
                    merge_mode=self.current_build_set.getMergeMode(),
                    ref=self.change.ref,
                    branch=branch,
                    buildset_uuid=self.current_build_set.uuid,
                    number=number,
                    patchset=patchset,
                    oldrev=oldrev,
                    newrev=newrev,
                    )

    def updatesJobConfig(self, job, layout):
        log = self.annotateLogger(self.log)
        layout_ahead = None
        if self.pipeline.manager:
            layout_ahead = self.pipeline.manager.getFallbackLayout(self)
        if layout_ahead and layout and layout is not layout_ahead:
            # This change updates the layout.  Calculate the job as it
            # would be if the layout had not changed.
            if self.current_build_set._old_job_graph is None:
                try:
                    ppc = layout_ahead.getProjectPipelineConfig(self)
                    log.debug("Creating job graph for config change detection")
                    self.current_build_set._set(
                        _old_job_graph=layout_ahead.createJobGraph(
                            None, self, ppc,
                            skip_file_matcher=True,
                            redact_secrets_and_keys=False,
                            debug_messages=None,
                            old=True))
                    log.debug("Done creating job graph for "
                              "config change detection")
                except Exception:
                    self.log.debug(
                        "Error freezing job graph in job update check:",
                        exc_info=True)
                    # The config was broken before, we have no idea
                    # which jobs have changed, so rather than run them
                    # all, just rely on the file matchers as-is.
                    return False
            old_job = self.current_build_set._old_jobs.get(job.name)
            if old_job is None:
                log.debug("Found a newly created job")
                return True  # A newly created job
            if (job.getConfigHash(self.pipeline.tenant) !=
                old_job.config_hash):
                log.debug("Found an updated job")
                return True  # This job's configuration has changed
        return False


class Bundle:
    """Identifies a collection of changes that must be treated as one unit."""

    def __init__(self, uuid=None):
        self.uuid = uuid or uuid4().hex
        self.items = []
        self.started_reporting = False
        self.failed_reporting = False
        self.cannot_merge = False

    def __repr__(self):
        return '<Bundle 0x{:x} {}'.format(id(self), self.items)

    def add_item(self, item):
        if item not in self.items:
            self.items.append(item)

    def updatesConfig(self, tenant):
        return any(i.change.updatesConfig(tenant) for i in self.items)

    def serialize(self):
        return {
            "uuid": self.uuid,
            "items": [i.getPath() for i in self.items],
            "started_reporting": self.started_reporting,
            "failed_reporting": self.failed_reporting,
            "cannot_merge": self.cannot_merge,
        }

    @classmethod
    def deserialize(cls, context, queue, items_by_path, data):
        bundle = cls(data["uuid"])
        bundle.items = [
            items_by_path.get(p) or QueueItem.fromZK(
                context, p, pipeline=queue.pipeline, queue=queue)
            for p in data["items"]
        ]
        bundle.started_reporting = data["started_reporting"]
        bundle.failed_reporting = data["failed_reporting"]
        bundle.cannot_merge = data["cannot_merge"]
        return bundle


# Cache info of a ref
CacheStat = namedtuple("CacheStat",
                       ["key", "uuid", "version", "last_modified"])


class Ref(object):
    """An existing state of a Project."""

    def __init__(self, project):
        self.project = project
        self.ref = None
        self.oldrev = None
        self.newrev = None
        self.files = []
        # The url for browsing the ref/tag/branch/change
        self.url = None
        # Cache info about this ref:
        # CacheStat(cache key, uuid, version, last_modified)
        self.cache_stat = None

    @property
    def cache_key(self):
        return self.cache_stat.key.reference

    @property
    def cache_version(self):
        return -1 if self.cache_stat is None else self.cache_stat.version

    def serialize(self):
        return {
            "project": self.project.name,
            "ref": self.ref,
            "oldrev": self.oldrev,
            "newrev": self.newrev,
            "files": self.files,
            "url": self.url,
        }

    def deserialize(self, data):
        self.ref = data.get("ref")
        self.oldrev = data.get("oldrev")
        self.newrev = data.get("newrev")
        self.files = data.get("files", [])
        self.url = data.get("url")

    def _id(self):
        return self.newrev

    def __repr__(self):
        rep = None
        pname = None
        if self.project and self.project.name:
            pname = self.project.name
        if self.newrev == '0000000000000000000000000000000000000000':
            rep = '<%s 0x%x %s deletes %s from %s' % (
                type(self).__name__, id(self), pname,
                self.ref, self.oldrev)
        elif self.oldrev == '0000000000000000000000000000000000000000':
            rep = '<%s 0x%x %s creates %s on %s>' % (
                type(self).__name__, id(self), pname,
                self.ref, self.newrev)
        else:
            # Catch all
            rep = '<%s 0x%x %s %s updated %s..%s>' % (
                type(self).__name__, id(self), pname,
                self.ref, self.oldrev, self.newrev)
        return rep

    def equals(self, other):
        if (self.project == other.project
            and self.ref == other.ref
            and self.newrev == other.newrev):
            return True
        return False

    def isUpdateOf(self, other):
        return False

    def getRelatedChanges(self, sched, related):
        """Recursively update a set of related changes

        :arg Scheduler sched: The scheduler instance
        :arg set related: The cache keys of changes which have been inspected
           so far.  Will be updated with additional changes by this method.
        """
        related.add(self.cache_stat.key)

    def updatesConfig(self, tenant):
        tpc = tenant.project_configs.get(self.project.canonical_name)
        if tpc is None:
            return False
        if self.files is None:
            # If self.files is None we don't know if this change updates the
            # config so assume it does as this is a safe default if we don't
            # know.
            return True
        for fn in self.files:
            if fn == 'zuul.yaml':
                return True
            if fn == '.zuul.yaml':
                return True
            if fn.startswith("zuul.d/"):
                return True
            if fn.startswith(".zuul.d/"):
                return True
            for ef in tpc.extra_config_files:
                if fn.startswith(ef):
                    return True
            for ed in tpc.extra_config_dirs:
                if fn.startswith(ed):
                    return True
        return False

    def getSafeAttributes(self):
        return Attributes(project=self.project,
                          ref=self.ref,
                          oldrev=self.oldrev,
                          newrev=self.newrev)

    def toDict(self):
        # Render to a dict to use in passing json to the executor
        d = dict()
        d['project'] = dict(
            name=self.project.name,
            short_name=self.project.name.split('/')[-1],
            canonical_hostname=self.project.canonical_hostname,
            canonical_name=self.project.canonical_name,
            src_dir=os.path.join('src', self.project.canonical_name),
        )
        return d


class Branch(Ref):
    """An existing branch state for a Project."""
    def __init__(self, project):
        super(Branch, self).__init__(project)
        self.branch = None

    def toDict(self):
        # Render to a dict to use in passing json to the executor
        d = super(Branch, self).toDict()
        d['branch'] = self.branch
        return d

    def serialize(self):
        d = super().serialize()
        d["branch"] = self.branch
        return d

    def deserialize(self, data):
        super().deserialize(data)
        self.branch = data.get("branch")


class Tag(Ref):
    """An existing tag state for a Project."""
    def __init__(self, project):
        super(Tag, self).__init__(project)
        self.tag = None
        self.containing_branches = []

    def serialize(self):
        d = super().serialize()
        d["containing_branches"] = self.containing_branches
        d["tag"] = self.tag
        return d

    def deserialize(self, data):
        super().deserialize(data)
        self.containing_branches = data.get("containing_branches")
        self.tag = data.get("tag")


class Change(Branch):
    """A proposed new state for a Project."""
    def __init__(self, project):
        super(Change, self).__init__(project)
        self.number = None
        # URIs for this change which may appear in depends-on headers.
        # Note this omits the scheme; i.e., is hostname/path.
        self.uris = []
        self.patchset = None

        # Changes that the source determined are needed due to the
        # git DAG:
        self.git_needs_changes = []
        self.git_needed_by_changes = []

        # Changes that the source determined are needed by backwards
        # compatible processing of Depends-On headers (Gerrit only):
        self.compat_needs_changes = []
        self.compat_needed_by_changes = []

        # Changes that the pipeline manager determined are needed due
        # to Depends-On headers (all drivers):
        self.commit_needs_changes = None

        self.is_current_patchset = True
        self.can_merge = False
        self.is_merged = False
        self.failed_to_merge = False
        self.open = None
        self.owner = None

        # This may be the commit message, or it may be a cover message
        # in the case of a PR.  Either way, it's the place where we
        # look for depends-on headers.
        self.message = None
        # This can be the commit id of the patchset enqueued or
        # in the case of a PR the id of HEAD of the branch.
        self.commit_id = None

    def deserialize(self, data):
        super().deserialize(data)
        self.number = data.get("number")
        self.uris = data.get("uris", [])
        self.patchset = data.get("patchset")
        self.git_needs_changes = data.get("git_needs_changes", [])
        self.git_needed_by_changes = data.get("git_needed_by_changes", [])
        self.compat_needs_changes = data.get("compat_needs_changes", [])
        self.compat_needed_by_changes = data.get(
            "compat_needed_by_changes", [])
        self.commit_needs_changes = (
            None if data.get("commit_needs_changes") is None
            else data.get("commit_needs_changes", [])
        )
        self.is_current_patchset = data.get("is_current_patchset", True)
        self.can_merge = data.get("can_merge", False)
        self.is_merged = data.get("is_merged", False)
        self.failed_to_merge = data.get("failed_to_merge", False)
        self.open = data.get("open")
        self.owner = data.get("owner")
        self.message = data.get("message")
        self.commit_id = data.get("commit_id")

    def serialize(self):
        d = super().serialize()
        d.update({
            "number": self.number,
            "uris": self.uris,
            "patchset": self.patchset,
            "git_needs_changes": self.git_needs_changes,
            "git_needed_by_changes": self.git_needed_by_changes,
            "compat_needs_changes": self.compat_needs_changes,
            "compat_needed_by_changes": self.git_needed_by_changes,
            "commit_needs_changes": self.commit_needs_changes,
            "is_current_patchset": self.is_current_patchset,
            "can_merge": self.can_merge,
            "is_merged": self.is_merged,
            "failed_to_merge": self.failed_to_merge,
            "open": self.open,
            "owner": self.owner,
            "message": self.message,
            "commit_id": self.commit_id,
        })
        return d

    def _id(self):
        return '%s,%s' % (self.number, self.patchset)

    def __repr__(self):
        pname = None
        if self.project and self.project.name:
            pname = self.project.name
        return '<Change 0x%x %s %s>' % (id(self), pname, self._id())

    def equals(self, other):
        if (super().equals(other) and
            isinstance(other, Change) and
            self.number == other.number and self.patchset == other.patchset):
            return True
        return False

    @property
    def needs_changes(self):
        commit_needs_changes = self.commit_needs_changes or []
        return (self.git_needs_changes + self.compat_needs_changes +
                commit_needs_changes)

    @property
    def needed_by_changes(self):
        return (self.git_needed_by_changes + self.compat_needed_by_changes)

    def isUpdateOf(self, other):
        if (self.project == other.project and
            (hasattr(other, 'number') and self.number == other.number) and
            (hasattr(other, 'patchset') and
             self.patchset is not None and
             other.patchset is not None and
             int(self.patchset) > int(other.patchset))):
            return True
        return False

    def getRelatedChanges(self, sched, related):
        """Recursively update a set of related changes

        :arg Scheduler sched: The scheduler instance
        :arg set related: The cache keys of changes which have been inspected
           so far.  Will be updated with additional changes by this method.
        """
        related.add(self.cache_stat.key)
        for reference in itertools.chain(self.needs_changes,
                                         self.needed_by_changes):
            key = ChangeKey.fromReference(reference)
            if key not in related:
                source = sched.connections.getSource(key.connection_name)
                change = source.getChangeByKey(key)
                change.getRelatedChanges(sched, related)

    def getSafeAttributes(self):
        return Attributes(project=self.project,
                          number=self.number,
                          patchset=self.patchset)

    def toDict(self):
        # Render to a dict to use in passing json to the executor
        d = super(Change, self).toDict()
        d['change'] = str(self.number)
        d['change_url'] = self.url
        d['patchset'] = str(self.patchset)
        return d


class EventTypeIndex(type(abc.ABC)):
    """A metaclass used to maintain a mapping of Event class names to
    class definitions when serializing and deserializing to and from
    ZooKeeper
    """
    event_type_mapping = {}

    def __init__(self, name, bases, clsdict):
        EventTypeIndex.event_type_mapping[name] = self
        super().__init__(name, bases, clsdict)


class AbstractEvent(abc.ABC, metaclass=EventTypeIndex):
    """Base class defining the interface for all events."""

    # Opaque identifier in order to acknowledge an event
    ack_ref = None

    @abc.abstractmethod
    def toDict(self):
        pass

    @abc.abstractmethod
    def updateFromDict(self, d) -> None:
        pass

    @classmethod
    def fromDict(cls, data):
        event = cls()
        event.updateFromDict(data)
        return event


class ConnectionEvent(AbstractEvent, UserDict):

    def toDict(self):
        return self.data

    def updateFromDict(self, d):
        self.data.update(d)


class ManagementEvent(AbstractEvent):
    """An event that should be processed within the main queue run loop"""

    def __init__(self):
        self.traceback = None
        self.zuul_event_id = None
        # Logical timestamp of the event (Zookeeper creation transaction ID).
        # This will be automatically set when the event is consumed from
        # the event queue in case it is None.
        self.zuul_event_ltime = None
        # Opaque identifier in order to report the result of an event
        self.result_ref = None

    def exception(self, tb: str):
        self.traceback = tb

    def toDict(self):
        return {
            "zuul_event_id": self.zuul_event_id,
            "zuul_event_ltime": self.zuul_event_ltime,
        }

    def updateFromDict(self, d):
        self.zuul_event_id = d.get("zuul_event_id")
        self.zuul_event_ltime = d.get("zuul_event_ltime")


class ReconfigureEvent(ManagementEvent):
    """Reconfigure the scheduler.  The layout will be (re-)loaded from
    the path specified in the configuration."""

    def __init__(self, smart=False):
        super(ReconfigureEvent, self).__init__()
        self.smart = smart

    def toDict(self):
        d = super().toDict()
        d["smart"] = self.smart
        return d

    @classmethod
    def fromDict(cls, data):
        event = cls(data.get("smart", False))
        event.updateFromDict(data)
        return event


class TenantReconfigureEvent(ManagementEvent):
    """Reconfigure the given tenant.  The layout will be (re-)loaded from
    the path specified in the configuration.

    :arg str tenant_name: the tenant to reconfigure
    :arg str project_name: if supplied, clear the cached configuration
         from this project first
    :arg str branch_name: if supplied along with project, only remove the
         configuration of the specific branch from the cache
    """
    def __init__(self, tenant_name, project_name, branch_name):
        super(TenantReconfigureEvent, self).__init__()
        self.tenant_name = tenant_name
        self.project_branches = set([(project_name, branch_name)])
        self.branch_cache_ltimes = {}
        self.merged_events = []

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        if not isinstance(other, TenantReconfigureEvent):
            return False
        # We don't check projects because they will get combined when
        # merged.
        return (self.tenant_name == other.tenant_name)

    def merge(self, other):
        if self.tenant_name != other.tenant_name:
            raise Exception("Can not merge events from different tenants")
        self.project_branches |= other.project_branches
        for connection_name, ltime in other.branch_cache_ltimes.items():
            self.branch_cache_ltimes[connection_name] = max(
                self.branch_cache_ltimes.get(connection_name, ltime), ltime)
        self.zuul_event_ltime = max(self.zuul_event_ltime,
                                    other.zuul_event_ltime)
        self.merged_events.append(other)

    def toDict(self):
        d = super().toDict()
        d["tenant_name"] = self.tenant_name
        d["project_branches"] = list(self.project_branches)
        d["branch_cache_ltimes"] = self.branch_cache_ltimes
        return d

    @classmethod
    def fromDict(cls, data):
        project, branch = next(iter(data["project_branches"]))
        event = cls(data.get("tenant_name"), project, branch)
        event.updateFromDict(data)
        # In case the dictionary was deserialized from JSON we get
        # [[project, branch]] instead of [(project, branch]).
        # Because of that we need to make sure we have a hashable
        # project-branch tuple.
        event.project_branches = set(
            tuple(pb) for pb in data["project_branches"]
        )
        event.branch_cache_ltimes = data.get("branch_cache_ltimes", {})
        return event


class PromoteEvent(ManagementEvent):
    """Promote one or more changes to the head of the queue.

    :arg str tenant_name: the name of the tenant
    :arg str pipeline_name: the name of the pipeline
    :arg list change_ids: a list of strings of change ids in the form
        1234,1
    """

    def __init__(self, tenant_name, pipeline_name, change_ids):
        super(PromoteEvent, self).__init__()
        self.tenant_name = tenant_name
        self.pipeline_name = pipeline_name
        self.change_ids = change_ids

    def toDict(self):
        d = super().toDict()
        d["tenant_name"] = self.tenant_name
        d["pipeline_name"] = self.pipeline_name
        d["change_ids"] = list(self.change_ids)
        return d

    @classmethod
    def fromDict(cls, data):
        event = cls(
            data.get("tenant_name"),
            data.get("pipeline_name"),
            list(data.get("change_ids", [])),
        )
        event.updateFromDict(data)
        return event


class ChangeManagementEvent(ManagementEvent):
    """Base class for events that dequeue/enqueue changes

    :arg str tenant_name: the name of the tenant
    :arg str pipeline_name: the name of the pipeline
    :arg str project_hostname: the hostname of the project
    :arg str project_name: the name of the project
    :arg str change: optional, the change
    :arg str ref: optional, the ref
    :arg str oldrev: optional, the old revision
    :arg str newrev: optional, the new revision
    """

    def __init__(self, tenant_name, pipeline_name, project_hostname,
                 project_name, change=None, ref=None, oldrev=None,
                 newrev=None):
        super().__init__()
        self.type = None
        self.tenant_name = tenant_name
        self.pipeline_name = pipeline_name
        self.project_hostname = project_hostname
        self.project_name = project_name
        self.change = change
        if change is not None:
            self.change_number, self.patch_number = change.split(',')
        else:
            self.change_number, self.patch_number = (None, None)
        self.ref = ref
        self.oldrev = oldrev or '0000000000000000000000000000000000000000'
        self.newrev = newrev or '0000000000000000000000000000000000000000'
        self.timestamp = time.time()

    def toDict(self):
        d = super().toDict()
        d["type"] = self.type
        d["tenant_name"] = self.tenant_name
        d["pipeline_name"] = self.pipeline_name
        d["project_hostname"] = self.project_hostname
        d["project_name"] = self.project_name
        d["change"] = self.change
        d["ref"] = self.ref
        d["oldrev"] = self.oldrev
        d["newrev"] = self.newrev
        d["timestamp"] = self.timestamp
        return d

    def updateFromDict(self, d):
        super().updateFromDict(d)
        self.type = d.get("type")
        self.timestamp = d.get("timestamp")

    @classmethod
    def fromDict(cls, data):
        event = cls(
            data.get("tenant_name"),
            data.get("pipeline_name"),
            data.get("project_hostname"),
            data.get("project_name"),
            data.get("change"),
            data.get("ref"),
            data.get("oldrev"),
            data.get("newrev"),
        )
        event.updateFromDict(data)
        return event


class DequeueEvent(ChangeManagementEvent):
    """Dequeue a change from a pipeline"""
    type = "dequeue"


class EnqueueEvent(ChangeManagementEvent):
    """Enqueue a change into a pipeline"""
    type = "enqueue"


class ResultEvent(AbstractEvent):
    """An event that needs to modify the pipeline state due to a
    result from an external system."""

    def updateFromDict(self, d) -> None:
        pass


class BuildResultEvent(ResultEvent):
    """Base class for all build result events.

    This class provides the common data structure for all build result
    events.

    :arg str build_uuid: The UUID of the build for which this event is
                         emitted.
    :arg str build_set_uuid: The UUID of the buildset of which the build
                             is part of.
    :arg str job_name: The name of the job the build is executed for.
    :arg str build_request_ref: The path to the build request that is
                                stored in ZooKeeper.
    :arg dict data: The event data.
    """

    def __init__(self, build_uuid, build_set_uuid, job_name, build_request_ref,
                 data, zuul_event_id=None):
        self.build_uuid = build_uuid
        self.build_set_uuid = build_set_uuid
        self.job_name = job_name
        self.build_request_ref = build_request_ref
        self.data = data
        self.zuul_event_id = zuul_event_id

    def toDict(self):
        return {
            "build_uuid": self.build_uuid,
            "build_set_uuid": self.build_set_uuid,
            "job_name": self.job_name,
            "build_request_ref": self.build_request_ref,
            "data": self.data,
            "zuul_event_id": self.zuul_event_id,
        }

    @classmethod
    def fromDict(cls, data):
        return cls(
            data.get("build_uuid"), data.get("build_set_uuid"),
            data.get("job_name"), data.get("build_request_ref"),
            data.get("data"), data.get("zuul_event_id"))

    def __repr__(self):
        return (
            f"<{self.__class__.__name__} build={self.build_uuid} "
            f"job={self.job_name}>"
        )


class BuildStartedEvent(BuildResultEvent):
    """A build has started."""

    pass


class BuildStatusEvent(BuildResultEvent):
    """Worker info and log URL for a build are available."""

    pass


class BuildPausedEvent(BuildResultEvent):
    """A build has been paused."""

    pass


class BuildCompletedEvent(BuildResultEvent):
    """A build has completed."""

    pass


class MergeCompletedEvent(ResultEvent):
    """A remote merge operation has completed

    :arg str request_uuid: The UUID of the merge request job.
    :arg str build_set_uuid: The UUID of the build_set which is ready.
    :arg bool merged: Whether the merge succeeded (changes with refs).
    :arg bool updated: Whether the repo was updated (changes without refs).
    :arg str commit: The SHA of the merged commit (changes with refs).
    :arg dict repo_state: The starting repo state before the merge.
    :arg list item_in_branches: A list of branches in which the final
        commit in the merge list appears (changes without refs).
    """

    def __init__(self, request_uuid, build_set_uuid, merged, updated,
                 commit, files, repo_state, item_in_branches):
        self.request_uuid = request_uuid
        self.build_set_uuid = build_set_uuid
        self.merged = merged
        self.updated = updated
        self.commit = commit
        self.files = files or []
        self.repo_state = repo_state or {}
        self.item_in_branches = item_in_branches or []

    def __repr__(self):
        return ('<MergeCompletedEvent job: %s buildset: %s merged: %s '
                'updated: %s commit: %s>' % (
                    self.request_uuid, self.build_set_uuid,
                    self.merged, self.updated, self.commit))

    def toDict(self):
        return {
            "request_uuid": self.request_uuid,
            "build_set_uuid": self.build_set_uuid,
            "merged": self.merged,
            "updated": self.updated,
            "commit": self.commit,
            "files": list(self.files),
            "repo_state": dict(self.repo_state),
            "item_in_branches": list(self.item_in_branches),
        }

    @classmethod
    def fromDict(cls, data):
        return cls(
            data.get("request_uuid"),
            data.get("build_set_uuid"),
            data.get("merged"),
            data.get("updated"),
            data.get("commit"),
            list(data.get("files", [])),
            dict(data.get("repo_state", {})),
            list(data.get("item_in_branches", [])),
        )


class FilesChangesCompletedEvent(ResultEvent):
    """A remote fileschanges operation has completed

    :arg BuildSet build_set: The build_set which is ready.
    :arg list files: List of files changed.
    """

    def __init__(self, build_set_uuid, files):
        self.build_set_uuid = build_set_uuid
        self.files = files or []

    def toDict(self):
        return {
            "build_set_uuid": self.build_set_uuid,
            "files": list(self.files),
        }

    @classmethod
    def fromDict(cls, data):
        return cls(
            data.get("build_set_uuid"),
            list(data.get("files", [])),
        )


class NodesProvisionedEvent(ResultEvent):
    """Nodes have been provisioned for a build_set

    :arg int request_id: The id of the fulfilled node request.
    :arg str job_name: The name of the job this node request belongs to.
    :arg str build_set_uuid: UUID of the buildset this node request belongs to
    """

    def __init__(self, request_id, build_set_uuid):
        self.request_id = request_id
        self.build_set_uuid = build_set_uuid

    def toDict(self):
        return {
            "request_id": self.request_id,
            "build_set_uuid": self.build_set_uuid,
        }

    @classmethod
    def fromDict(cls, data):
        return cls(
            data.get("request_id"),
            data.get("build_set_uuid"),
        )


class TriggerEvent(AbstractEvent):
    """Incoming event from an external system."""
    def __init__(self):
        # TODO(jeblair): further reduce this list
        self.data = None
        # common
        self.type = None
        self.branch_updated = False
        self.branch_created = False
        self.branch_deleted = False
        self.branch_protected = True
        self.ref = None
        # For management events (eg: enqueue / promote)
        self.tenant_name = None
        self.project_hostname = None
        self.project_name = None
        self.trigger_name = None
        self.connection_name = None
        # Representation of the user account that performed the event.
        self.account = None
        # patchset-created, comment-added, etc.
        self.change_number = None
        self.change_url = None
        self.patch_number = None
        self.branch = None
        self.comment = None
        self.state = None
        # ref-updated
        self.oldrev = None
        self.newrev = None
        # For events that arrive with a destination pipeline (eg, from
        # an admin command, etc):
        self.forced_pipeline = None
        # For logging
        self.zuul_event_id = None
        self.timestamp = None
        self.arrived_at_scheduler_timestamp = None
        self.driver_name = None
        self.branch_cache_ltime = -1

    def toDict(self):
        return {
            "data": self.data,
            "type": self.type,
            "branch_updated": self.branch_updated,
            "branch_created": self.branch_created,
            "branch_deleted": self.branch_deleted,
            "branch_protected": self.branch_protected,
            "ref": self.ref,
            "tenant_name": self.tenant_name,
            "project_hostname": self.project_hostname,
            "project_name": self.project_name,
            "trigger_name": self.trigger_name,
            "connection_name": self.connection_name,
            "account": self.account,
            "change_number": self.change_number,
            "change_url": self.change_url,
            "patch_number": self.patch_number,
            "branch": self.branch,
            "comment": self.comment,
            "state": self.state,
            "oldrev": self.oldrev,
            "newrev": self.newrev,
            "forced_pipeline": self.forced_pipeline,
            "zuul_event_id": self.zuul_event_id,
            "timestamp": self.timestamp,
            "arrived_at_scheduler_timestamp": (
                self.arrived_at_scheduler_timestamp
            ),
            "driver_name": self.driver_name,
            "branch_cache_ltime": self.branch_cache_ltime,
        }

    def updateFromDict(self, d):
        self.data = d["data"]
        self.type = d["type"]
        self.branch_updated = d["branch_updated"]
        self.branch_created = d["branch_created"]
        self.branch_deleted = d["branch_deleted"]
        self.branch_protected = d["branch_protected"]
        self.ref = d["ref"]
        self.tenant_name = d["tenant_name"]
        self.project_hostname = d["project_hostname"]
        self.project_name = d["project_name"]
        self.trigger_name = d["trigger_name"]
        self.connection_name = d["connection_name"]
        self.account = d["account"]
        self.change_number = d["change_number"]
        self.change_url = d["change_url"]
        self.patch_number = d["patch_number"]
        self.branch = d["branch"]
        self.comment = d["comment"]
        self.state = d["state"]
        self.oldrev = d["oldrev"]
        self.newrev = d["newrev"]
        self.forced_pipeline = d["forced_pipeline"]
        self.zuul_event_id = d["zuul_event_id"]
        self.timestamp = d["timestamp"]
        self.arrived_at_scheduler_timestamp = (
            d["arrived_at_scheduler_timestamp"]
        )
        self.driver_name = d["driver_name"]
        self.branch_cache_ltime = d.get("branch_cache_ltime", -1)

    @property
    def canonical_project_name(self):
        return self.project_hostname + '/' + self.project_name

    def isPatchsetCreated(self):
        return False

    def isMessageChanged(self):
        return False

    def isChangeAbandoned(self):
        return False

    def _repr(self):
        flags = [str(self.type)]
        if self.project_name:
            flags.append(self.project_name)
        if self.ref:
            flags.append(self.ref)
        if self.branch_updated:
            flags.append('branch_updated')
        if self.branch_created:
            flags.append('branch_created')
        if self.branch_deleted:
            flags.append('branch_deleted')
        return ' '.join(flags)

    def __repr__(self):
        return '<%s 0x%x %s>' % (self.__class__.__name__,
                                 id(self), self._repr())


class FalseWithReason(object):
    """Event filter result"""
    def __init__(self, reason):
        self.reason = reason

    def __str__(self):
        return self.reason

    def __bool__(self):
        return False


class BaseFilter(ConfigObject):
    """Base Class for filtering which Changes and Events to process."""
    pass


class EventFilter(BaseFilter):
    """Allows a Pipeline to only respond to certain events."""
    def __init__(self, connection_name, trigger):
        super(EventFilter, self).__init__()
        self.connection_name = connection_name
        self.trigger = trigger

    def matches(self, event, ref):
        # TODO(jeblair): consider removing ref argument

        # Event came from wrong connection
        if self.connection_name != event.connection_name:
            return False

        return True


class RefFilter(BaseFilter):
    """Allows a Manager to only enqueue Changes that meet certain criteria."""
    def __init__(self, connection_name):
        super(RefFilter, self).__init__()
        self.connection_name = connection_name

    def matches(self, change):
        return True


class TenantProjectConfig(object):
    """A project in the context of a tenant.

    A Project is globally unique in the system, however, when used in
    a tenant, some metadata about the project local to the tenant is
    stored in a TenantProjectConfig.
    """

    def __init__(self, project):
        self.project = project
        self.load_classes = set()
        self.shadow_projects = set()
        self.branches = []
        # The tenant's default setting of exclude_unprotected_branches will
        # be overridden by this one if not None.
        self.exclude_unprotected_branches = None
        self.parsed_branch_config = {}  # branch -> ParsedConfig
        # The list of paths to look for extra zuul config files
        self.extra_config_files = ()
        # The list of paths to look for extra zuul config dirs
        self.extra_config_dirs = ()
        # Load config from a different branch if this is a config project
        self.load_branch = None


class ProjectPipelineConfig(ConfigObject):
    # Represents a project cofiguration in the context of a pipeline
    def __init__(self):
        super(ProjectPipelineConfig, self).__init__()
        self.job_list = JobList()
        self.queue_name = None
        self.debug = False
        self.debug_messages = []
        self.fail_fast = None
        self.variables = {}

    def addDebug(self, msg):
        self.debug_messages.append(msg)

    def update(self, other):
        if not isinstance(other, ProjectPipelineConfig):
            raise Exception("Unable to update from %s" % (other,))
        if self.queue_name is None:
            self.queue_name = other.queue_name
        if other.debug:
            self.debug = other.debug
        if self.fail_fast is None:
            self.fail_fast = other.fail_fast
        self.job_list.inheritFrom(other.job_list)

    def updateVariables(self, other):
        # We need to keep this separate to update() because we wish to
        # apply the project variables all the time, even if its jobs
        # only come from templates.
        self.variables = Job._deepUpdate(self.variables, other)

    def toDict(self):
        d = {}
        d['queue_name'] = self.queue_name
        return d


class ProjectConfig(ConfigObject):
    # Represents a project configuration
    def __init__(self, name):
        super(ProjectConfig, self).__init__()
        self.name = name
        self.templates = []
        # Pipeline name -> ProjectPipelineConfig
        self.pipelines = {}
        self.branch_matcher = None
        self.variables = {}
        # These represent the values from the config file, but should
        # not be used directly; instead, use the ProjectMetadata to
        # find the computed value from across all project config
        # stanzas.
        self.merge_mode = None
        self.default_branch = None
        self.queue_name = None

    def __repr__(self):
        return '<ProjectConfig %s source: %s %s>' % (
            self.name, self.source_context, self.branch_matcher)

    def copy(self):
        r = self.__class__(self.name)
        r.source_context = self.source_context
        r.start_mark = self.start_mark
        r.templates = self.templates
        r.pipelines = self.pipelines
        r.branch_matcher = self.branch_matcher
        r.variables = self.variables
        r.merge_mode = self.merge_mode
        r.default_branch = self.default_branch
        r.queue_name = self.queue_name
        return r

    def setImpliedBranchMatchers(self, branches):
        if len(branches) == 0:
            self.branch_matcher = None
        elif len(branches) > 1:
            matchers = [change_matcher.ImpliedBranchMatcher(branch)
                        for branch in branches]
            self.branch_matcher = change_matcher.MatchAny(matchers)
        else:
            self.branch_matcher = change_matcher.ImpliedBranchMatcher(
                branches[0])

    def changeMatches(self, change):
        if self.branch_matcher and not self.branch_matcher.matches(change):
            return False
        return True

    def toDict(self):
        d = {}
        d['source_context'] = self.source_context.toDict()
        d['default_branch'] = self.default_branch
        if self.merge_mode:
            d['merge_mode'] = list(filter(lambda x: x[1] == self.merge_mode,
                                          MERGER_MAP.items()))[0][0]
        else:
            d['merge_mode'] = None
        d['templates'] = self.templates
        d['queue_name'] = self.queue_name
        return d


class ProjectMetadata:
    """Information about a Project

    A Layout holds one of these for each project it knows about.
    Information about the project which is synthesized from multiple
    ProjectConfig objects is stored here.
    """

    def __init__(self):
        self.merge_mode = None
        self.default_branch = None
        self.queue_name = None

    def toDict(self):
        return {
            'merge_mode': self.merge_mode,
            'default_branch': self.default_branch,
            'queue_name': self.queue_name,
        }

    @classmethod
    def fromDict(cls, data):
        o = cls()
        o.merge_mode = data['merge_mode']
        o.default_branch = data['default_branch']
        o.queue_name = data['queue_name']
        return o


class SystemAttributes:
    """Global system attributes from the Zuul config.

    Those runtime related settings are expected to be consistent on
    all schedulers and will be synchronized via Zookeeper.
    """

    def __init__(self):
        self.use_relative_priority = False
        self.max_hold_expiration = 0
        self.default_hold_expiration = 0
        self.default_ansible_version = None
        self.web_root = None
        self.web_status_url = ""
        self.websocket_url = None

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return (
            self.use_relative_priority == other.use_relative_priority
            and self.max_hold_expiration == other.max_hold_expiration
            and self.default_hold_expiration == other.default_hold_expiration
            and self.default_ansible_version == other.default_ansible_version
            and self.web_root == other.web_root
            and self.web_status_url == other.web_status_url
            and self.websocket_url == other.websocket_url)

    @classmethod
    def fromConfig(cls, config):
        sys_attrs = cls()
        sys_attrs.updateFromConfig(config)
        return sys_attrs

    def updateFromConfig(self, config):
        """Set runtime related system attributes from config."""
        self.use_relative_priority = False
        if config.has_option('scheduler', 'relative_priority'):
            if config.getboolean('scheduler', 'relative_priority'):
                self.use_relative_priority = True

        max_hold = get_default(config, 'scheduler', 'max_hold_expiration', 0)
        default_hold = get_default(
            config, 'scheduler', 'default_hold_expiration', max_hold)

        # If the max hold is not infinite, we need to make sure that
        # our default value does not exceed it.
        if (max_hold and default_hold != max_hold
                and (default_hold == 0 or default_hold > max_hold)):
            default_hold = max_hold
        self.max_hold_expiration = max_hold
        self.default_hold_expiration = default_hold

        # Reload the ansible manager in case the default ansible version
        # changed.
        self.default_ansible_version = get_default(
            config, 'scheduler', 'default_ansible_version', None)

        web_root = get_default(config, 'web', 'root', None)
        if web_root:
            web_root = urllib.parse.urljoin(web_root, 't/{tenant.name}/')
        self.web_root = web_root

        self.web_status_url = get_default(config, 'web', 'status_url', '')
        self.websocket_url = get_default(config, 'web', 'websocket_url', None)

    def toDict(self):
        return {
            "use_relative_priority": self.use_relative_priority,
            "max_hold_expiration": self.max_hold_expiration,
            "default_hold_expiration": self.default_hold_expiration,
            "default_ansible_version": self.default_ansible_version,
            "web_root": self.web_root,
            "web_status_url": self.web_status_url,
            "websocket_url": self.websocket_url,
        }

    @classmethod
    def fromDict(cls, data):
        sys_attrs = cls()
        sys_attrs.use_relative_priority = data["use_relative_priority"]
        sys_attrs.max_hold_expiration = data["max_hold_expiration"]
        sys_attrs.default_hold_expiration = data["default_hold_expiration"]
        sys_attrs.default_ansible_version = data["default_ansible_version"]
        sys_attrs.web_root = data["web_root"]
        sys_attrs.web_status_url = data["web_status_url"]
        sys_attrs.websocket_url = data["websocket_url"]
        return sys_attrs


# TODO(ianw) : this would clearly be better if it recorded the
# original file and made line-relative comments, however the contexts
# the subclasses are raised in don't have that info currently, so this
# is a best-effort to show you something that clues you into the
# error.
class ConfigItemErrorException(Exception):
    def __init__(self, conf):
        super(ConfigItemErrorException, self).__init__(
            self.message + self._generate_extract(conf))

    def _generate_extract(self, conf):
        context = textwrap.dedent("""\

        The incorrect values are around:

        """)
        # Not sorting the keys makes it look closer to what is in the
        # file and works best with >= Python 3.7 where dicts are
        # ordered by default.  If this is a foreign config file or
        # something the dump might be really long; hence the
        # truncation.
        extract = yaml.encrypted_dump(conf, sort_keys=False)
        lines = extract.split('\n')
        if len(lines) > 5:
            lines = lines[0:4]
            lines.append('...')

        return context + '\n'.join(lines)


class ConfigItemNotListError(ConfigItemErrorException):
    message = textwrap.dedent("""\
    Configuration file is not a list.  Each zuul.yaml configuration
    file must be a list of items, for example:

    - job:
        name: foo

    - project:
        name: bar

    Ensure that every item starts with "- " so that it is parsed as a
    YAML list.
    """)


class ConfigItemNotDictError(ConfigItemErrorException):
    message = textwrap.dedent("""\
    Configuration item is not a dictionary.  Each zuul.yaml
    configuration file must be a list of dictionaries, for
    example:

    - job:
        name: foo

    - project:
        name: bar

    Ensure that every item in the list is a dictionary with one
    key (in this example, 'job' and 'project').
    """)


class ConfigItemMultipleKeysError(ConfigItemErrorException):
    message = textwrap.dedent("""\
    Configuration item has more than one key.  Each zuul.yaml
    configuration file must be a list of dictionaries with a
    single key, for example:

    - job:
        name: foo

    - project:
        name: bar

    Ensure that every item in the list is a dictionary with only
    one key (in this example, 'job' and 'project').  This error
    may be caused by insufficient indentation of the keys under
    the configuration item ('name' in this example).
    """)


class ConfigItemUnknownError(ConfigItemErrorException):
    message = textwrap.dedent("""\
    Configuration item not recognized.  Each zuul.yaml
    configuration file must be a list of dictionaries, for
    example:

    - job:
        name: foo

    - project:
        name: bar

    The dictionary keys must match one of the configuration item
    types recognized by zuul (for example, 'job' or 'project').
    """)


class UnparsedAbideConfig(object):

    """A collection of yaml lists that has not yet been parsed into objects.

    An Abide is a collection of tenants and access rules to those tenants.
    """

    def __init__(self):
        self.uuid = uuid4().hex
        self.ltime = -1
        self.tenants = {}
        self.admin_rules = []

    def extend(self, conf):
        if isinstance(conf, UnparsedAbideConfig):
            self.tenants.update(conf.tenants)
            self.admin_rules.extend(conf.admin_rules)
            return

        if not isinstance(conf, list):
            raise ConfigItemNotListError(conf)

        for item in conf:
            if not isinstance(item, dict):
                raise ConfigItemNotDictError(item)
            if len(item.keys()) > 1:
                raise ConfigItemMultipleKeysError(item)
            key, value = list(item.items())[0]
            if key == 'tenant':
                if value["name"] in self.tenants:
                    raise Exception("Duplicate configuration for "
                                    f"tenant {value['name']}")
                self.tenants[value["name"]] = value
            elif key == 'admin-rule':
                self.admin_rules.append(value)
            else:
                raise ConfigItemUnknownError(item)

    def toDict(self):
        return {
            "uuid": self.uuid,
            "tenants": self.tenants,
            "admin_rules": self.admin_rules,
        }

    @classmethod
    def fromDict(cls, data, ltime):
        unparsed_abide = cls()
        unparsed_abide.uuid = data["uuid"]
        unparsed_abide.ltime = ltime
        unparsed_abide.tenants = data["tenants"]
        unparsed_abide.admin_rules = data["admin_rules"]
        return unparsed_abide


class UnparsedConfig(object):
    """A collection of yaml lists that has not yet been parsed into objects."""

    def __init__(self):
        self.pragmas = []
        self.pipelines = []
        self.jobs = []
        self.project_templates = []
        self.projects = []
        self.nodesets = []
        self.secrets = []
        self.semaphores = []
        self.queues = []

        # The list of files/dirs which this represents.
        self.files_examined = set()
        self.dirs_examined = set()

    def copy(self, trusted=None):
        # If trusted is not None, update the source context of each
        # object in the copy.
        r = UnparsedConfig()
        # Keep a cache of all the source contexts indexed by
        # project-branch-path so that we can share them across objects
        source_contexts = {}
        for attr in ['pragmas', 'pipelines', 'jobs', 'project_templates',
                     'projects', 'nodesets', 'secrets', 'semaphores',
                     'queues']:
            # Make a deep copy of each of our attributes
            old_objlist = getattr(self, attr)
            new_objlist = copy.deepcopy(old_objlist)
            setattr(r, attr, new_objlist)
            for i, new_obj in enumerate(new_objlist):
                old_obj = old_objlist[i]
                key = (old_obj['_source_context'].project_canonical_name,
                       old_obj['_source_context'].project_name,
                       old_obj['_source_context'].project_connection_name,
                       old_obj['_source_context'].branch,
                       old_obj['_source_context'].path)
                new_sc = source_contexts.get(key)
                if not new_sc:
                    new_sc = new_obj['_source_context']
                    if trusted is not None:
                        new_sc.trusted = trusted
                    source_contexts[key] = new_sc
                else:
                    new_obj['_source_context'] = new_sc
        return r

    def extend(self, conf):
        if isinstance(conf, UnparsedConfig):
            self.pragmas.extend(conf.pragmas)
            self.pipelines.extend(conf.pipelines)
            self.jobs.extend(conf.jobs)
            self.project_templates.extend(conf.project_templates)
            self.projects.extend(conf.projects)
            self.nodesets.extend(conf.nodesets)
            self.secrets.extend(conf.secrets)
            self.semaphores.extend(conf.semaphores)
            self.queues.extend(conf.queues)
            return

        if not isinstance(conf, list):
            raise ConfigItemNotListError(conf)

        for item in conf:
            if not isinstance(item, dict):
                raise ConfigItemNotDictError(item)
            if len(item.keys()) > 1:
                raise ConfigItemMultipleKeysError(item)
            key, value = list(item.items())[0]
            if key == 'project':
                self.projects.append(value)
            elif key == 'job':
                self.jobs.append(value)
            elif key == 'project-template':
                self.project_templates.append(value)
            elif key == 'pipeline':
                self.pipelines.append(value)
            elif key == 'nodeset':
                self.nodesets.append(value)
            elif key == 'secret':
                self.secrets.append(value)
            elif key == 'semaphore':
                self.semaphores.append(value)
            elif key == 'queue':
                self.queues.append(value)
            elif key == 'pragma':
                self.pragmas.append(value)
            else:
                raise ConfigItemUnknownError(item)


class ParsedConfig(object):
    """A collection of parsed config objects."""

    def __init__(self):
        self.pragmas = []
        self.pipelines = []
        self.jobs = []
        self.project_templates = []
        self.projects = []
        self.projects_by_regex = {}
        self.nodesets = []
        self.secrets = []
        self.semaphores = []
        self.queues = []

    def copy(self):
        r = ParsedConfig()
        r.pragmas = self.pragmas[:]
        r.pipelines = self.pipelines[:]
        r.jobs = self.jobs[:]
        r.project_templates = self.project_templates[:]
        r.projects = self.projects[:]
        r.projects_by_regex = copy.copy(self.projects_by_regex)
        r.nodesets = self.nodesets[:]
        r.secrets = self.secrets[:]
        r.semaphores = self.semaphores[:]
        r.queues = self.queues[:]
        return r

    def extend(self, conf):
        if isinstance(conf, ParsedConfig):
            self.pragmas.extend(conf.pragmas)
            self.pipelines.extend(conf.pipelines)
            self.jobs.extend(conf.jobs)
            self.project_templates.extend(conf.project_templates)
            self.projects.extend(conf.projects)
            self.nodesets.extend(conf.nodesets)
            self.secrets.extend(conf.secrets)
            self.semaphores.extend(conf.semaphores)
            self.queues.extend(conf.queues)
            for regex, projects in conf.projects_by_regex.items():
                self.projects_by_regex.setdefault(regex, []).extend(projects)
            return
        else:
            raise TypeError()


class Layout(object):
    """Holds all of the Pipelines."""

    log = logging.getLogger("zuul.layout")

    def __init__(self, tenant, uuid=None):
        # Allow setting the UUID in case we are re-creating the "same" layout
        # on another scheduler.
        # Queue items will reference their (dynamic) layout via the layout's
        # UUID. An item's layout UUID will change if any of it's input to the
        # layout creation changed. Those inputs are the tenant layout and list
        # of items ahead. This means that during a re-enqueue and in case of a
        # gate reset we will set the layout UUID of an item back to None.
        self.uuid = uuid or uuid4().hex
        self.tenant = tenant
        self.project_configs = {}
        self.project_templates = {}
        self.project_metadata = {}
        self.pipelines = OrderedDict()
        # This is a dictionary of name -> [jobs].  The first element
        # of the list is the first job added with that name.  It is
        # the reference definition for a given job.  Subsequent
        # elements are aspects of that job with different matchers
        # that override some attribute of the job.  These aspects all
        # inherit from the reference definition.
        noop = Job('noop')
        noop.description = 'A job that will always succeed, no operation.'
        noop.parent = noop.BASE_JOB_MARKER
        noop.run = (PlaybookContext(None, 'noop.yaml', [], []),)
        self.jobs = {'noop': [noop]}
        self.nodesets = {}
        self.secrets = {}
        self.semaphores = {}
        self.queues = {}
        self.loading_errors = LoadingErrors()

    def getJob(self, name):
        if name in self.jobs:
            return self.jobs[name][0]
        raise Exception("Job %s not defined" % (name,))

    def hasJob(self, name):
        return name in self.jobs

    def getJobs(self, name):
        return self.jobs.get(name, [])

    def addJob(self, job):
        # We can have multiple variants of a job all with the same
        # name, but these variants must all be defined in the same repo.
        prior_jobs = [j for j in self.getJobs(job.name) if
                      j.source_context.project_canonical_name !=
                      job.source_context.project_canonical_name]
        # Unless the repo is permitted to shadow another.  If so, and
        # the job we are adding is from a repo that is permitted to
        # shadow the one with the older jobs, skip adding this job.
        job_project = job.source_context.project_canonical_name
        job_tpc = self.tenant.project_configs[job_project]
        skip_add = False
        for prior_job in prior_jobs[:]:
            prior_project = prior_job.source_context.project_canonical_name
            if prior_project in job_tpc.shadow_projects:
                prior_jobs.remove(prior_job)
                skip_add = True

        if prior_jobs:
            raise Exception("Job %s in %s is not permitted to shadow "
                            "job %s in %s" % (
                                job,
                                job.source_context.project_name,
                                prior_jobs[0],
                                prior_jobs[0].source_context.project_name))
        if skip_add:
            return False
        if job.name in self.jobs:
            self.jobs[job.name].append(job)
        else:
            self.jobs[job.name] = [job]
        return True

    def addNodeSet(self, nodeset):
        # It's ok to have a duplicate nodeset definition, but only if
        # they are in different branches of the same repo, and have
        # the same values.
        other = self.nodesets.get(nodeset.name)
        if other is not None:
            if not nodeset.source_context.isSameProject(other.source_context):
                raise Exception(
                    "Nodeset %s already defined in project %s" %
                    (nodeset.name, other.source_context.project_name))
            if nodeset.source_context.branch == other.source_context.branch:
                raise Exception("Nodeset %s already defined" % (nodeset.name,))
            if nodeset != other:
                raise Exception("Nodeset %s does not match existing definition"
                                " in branch %s" %
                                (nodeset.name, other.source_context.branch))
            # Identical data in a different branch of the same project;
            # ignore the duplicate definition
            return
        self.nodesets[nodeset.name] = nodeset

    def addSecret(self, secret):
        # It's ok to have a duplicate secret definition, but only if
        # they are in different branches of the same repo, and have
        # the same values.
        other = self.secrets.get(secret.name)
        if other is not None:
            if not secret.source_context.isSameProject(other.source_context):
                raise Exception(
                    "Secret %s already defined in project %s" %
                    (secret.name, other.source_context.project_name))
            if secret.source_context.branch == other.source_context.branch:
                raise Exception("Secret %s already defined" % (secret.name,))
            if not secret.areDataEqual(other):
                raise Exception("Secret %s does not match existing definition"
                                " in branch %s" %
                                (secret.name, other.source_context.branch))
            # Identical data in a different branch of the same project;
            # ignore the duplicate definition
            return
        self.secrets[secret.name] = secret

    def addSemaphore(self, semaphore):
        # It's ok to have a duplicate semaphore definition, but only if
        # they are in different branches of the same repo, and have
        # the same values.
        other = self.semaphores.get(semaphore.name)
        if other is not None:
            if not semaphore.source_context.isSameProject(
                    other.source_context):
                raise Exception(
                    "Semaphore %s already defined in project %s" %
                    (semaphore.name, other.source_context.project_name))
            if semaphore.source_context.branch == other.source_context.branch:
                raise Exception("Semaphore %s already defined" %
                                (semaphore.name,))
            if semaphore != other:
                raise Exception("Semaphore %s does not match existing"
                                " definition in branch %s" %
                                (semaphore.name, other.source_context.branch))
            # Identical data in a different branch of the same project;
            # ignore the duplicate definition
            return
        self.semaphores[semaphore.name] = semaphore

    def addQueue(self, queue):
        # Change queues must be unique and cannot be overridden.
        if queue.name in self.queues:
            raise Exception('Queue %s is already defined' % queue.name)

        self.queues[queue.name] = queue

    def addPipeline(self, pipeline):
        if pipeline.tenant is not self.tenant:
            raise Exception("Pipeline created for tenant %s "
                            "may not be added to %s" % (
                                pipeline.tenant,
                                self.tenant))

        if pipeline.name in self.pipelines:
            raise Exception(
                "Pipeline %s is already defined" % pipeline.name)

        self.pipelines[pipeline.name] = pipeline

    def addProjectTemplate(self, project_template):
        template_list = self.project_templates.get(project_template.name)
        if template_list is not None:
            reference = template_list[0]
            if (reference.source_context.project_canonical_name !=
                project_template.source_context.project_canonical_name):
                raise Exception("Project template %s is already defined" %
                                (project_template.name,))
        else:
            template_list = self.project_templates.setdefault(
                project_template.name, [])
        template_list.append(project_template)

    def getProjectTemplates(self, name):
        pt = self.project_templates.get(name, None)
        if pt is None:
            raise TemplateNotFoundError("Project template %s not found" % name)
        return pt

    def addProjectConfig(self, project_config):
        if project_config.name in self.project_configs:
            self.project_configs[project_config.name].append(project_config)
        else:
            self.project_configs[project_config.name] = [project_config]
            self.project_metadata[project_config.name] = ProjectMetadata()
        md = self.project_metadata[project_config.name]
        if md.merge_mode is None and project_config.merge_mode is not None:
            md.merge_mode = project_config.merge_mode
        if (md.default_branch is None and
            project_config.default_branch is not None):
            md.default_branch = project_config.default_branch
        if (
            md.queue_name is None
            and project_config.queue_name is not None
        ):
            md.queue_name = project_config.queue_name

    def getProjectConfigs(self, name):
        return self.project_configs.get(name, [])

    def getAllProjectConfigs(self, name):
        # Get all the project configs (project and project-template
        # stanzas) for a project.
        try:
            ret = []
            for pc in self.getProjectConfigs(name):
                ret.append(pc)
                for template_name in pc.templates:
                    templates = self.getProjectTemplates(template_name)
                    ret.extend(templates)
            return ret
        except TemplateNotFoundError as e:
            self.log.warning("%s for project %s" % (e, name))
            return []

    def getProjectMetadata(self, name):
        if name in self.project_metadata:
            return self.project_metadata[name]
        return None

    def getProjectPipelineConfig(self, item):
        log = item.annotateLogger(self.log)
        # Create a project-pipeline config for the given item, taking
        # its branch (if any) into consideration.  If the project does
        # not participate in the pipeline at all (in this branch),
        # return None.

        # A pc for a project can appear only in a config-project
        # (unbranched, always applies), or in the project itself (it
        # should have an implied branch matcher and it must match the
        # item).
        ppc = ProjectPipelineConfig()
        project_in_pipeline = False
        for pc in self.getProjectConfigs(item.change.project.canonical_name):
            if not pc.changeMatches(item.change):
                msg = "Project %s did not match" % (pc,)
                ppc.addDebug(msg)
                log.debug("%s item %s", msg, item)
                continue
            msg = "Project %s matched" % (pc,)
            ppc.addDebug(msg)
            log.debug("%s item %s", msg, item)
            for template_name in pc.templates:
                templates = self.getProjectTemplates(template_name)
                for template in templates:
                    template_ppc = template.pipelines.get(item.pipeline.name)
                    if template_ppc:
                        if not template.changeMatches(item.change):
                            msg = "Project template %s did not match" % (
                                template,)
                            ppc.addDebug(msg)
                            log.debug("%s item %s", msg, item)
                            continue
                        msg = "Project template %s matched" % (
                            template,)
                        ppc.addDebug(msg)
                        log.debug("%s item %s", msg, item)
                        project_in_pipeline = True
                        ppc.update(template_ppc)
                        ppc.updateVariables(template.variables)

            # Now merge in project variables (they will override
            # template variables; later job variables may override
            # these again)
            ppc.updateVariables(pc.variables)

            project_ppc = pc.pipelines.get(item.pipeline.name)
            if project_ppc:
                project_in_pipeline = True
                ppc.update(project_ppc)
        if project_in_pipeline:
            return ppc
        return None

    def _updateOverrideCheckouts(self, override_checkouts, job):
        # Update the values in an override_checkouts dict with those
        # in a job.  Used in collectJobVariants.
        if job.override_checkout:
            override_checkouts[None] = job.override_checkout
        for req in job.required_projects.values():
            if req.override_checkout:
                override_checkouts[req.project_name] = req.override_checkout

    def _collectJobVariants(self, item, jobname, change, path, jobs, stack,
                            override_checkouts, indent, debug_messages):
        log = item.annotateLogger(self.log)
        matched = False
        local_override_checkouts = override_checkouts.copy()
        override_branch = None
        project = None
        for variant in self.getJobs(jobname):
            if project is None and variant.source_context:
                project = variant.source_context.project_canonical_name
                if override_checkouts.get(None) is not None:
                    override_branch = override_checkouts.get(None)
                override_branch = override_checkouts.get(
                    project, override_branch)
                branches = self.tenant.getProjectBranches(project)
                if override_branch not in branches:
                    override_branch = None
            if not variant.changeMatchesBranch(
                    change,
                    override_branch=override_branch):
                log.debug("Variant %s did not match %s", repr(variant), change)
                add_debug_line(debug_messages,
                               "Variant {variant} did not match".format(
                                   variant=repr(variant)), indent=indent)
                continue
            else:
                log.debug("Variant %s matched %s", repr(variant), change)
                add_debug_line(debug_messages,
                               "Variant {variant} matched".format(
                                   variant=repr(variant)), indent=indent)
            if not variant.isBase():
                parent = variant.parent
                if not jobs and parent is None:
                    parent = self.tenant.default_base_job
            else:
                parent = None
            self._updateOverrideCheckouts(local_override_checkouts, variant)
            if parent and parent not in path:
                if parent in stack:
                    raise Exception("Dependency cycle in jobs: %s" % stack)
                self.collectJobs(item, parent, change, path, jobs,
                                 stack + [jobname], local_override_checkouts,
                                 debug_messages=debug_messages)

            matched = True
            if variant not in jobs:
                jobs.append(variant)
        return matched

    def collectJobs(self, item, jobname, change, path=None, jobs=None,
                    stack=None, override_checkouts=None, debug_messages=None):
        log = item.annotateLogger(self.log)
        # Stack is the recursion stack of job parent names.  Each time
        # we go up a level, we add to stack, and it's popped as we
        # descend.
        if stack is None:
            stack = []
        # Jobs is the list of jobs we've accumulated.
        if jobs is None:
            jobs = []
        # Path is the list of job names we've examined.  It
        # accumulates and never reduces.  If more than one job has the
        # same parent, this will prevent us from adding it a second
        # time.
        if path is None:
            path = []
        # Override_checkouts is a dictionary of canonical project
        # names -> branch names.  It is not mutated, but instead new
        # copies are made and updated as we ascend the hierarchy, so
        # higher levels don't affect lower levels after we descend.
        # It's used to override the branch matchers for jobs.
        if override_checkouts is None:
            override_checkouts = {}
        path.append(jobname)
        matched = False
        indent = len(path) + 1
        msg = "Collecting job variants for {jobname}".format(jobname=jobname)
        log.debug(msg)
        add_debug_line(debug_messages, msg, indent=indent)
        matched = self._collectJobVariants(
            item, jobname, change, path, jobs, stack, override_checkouts,
            indent, debug_messages)
        if not matched:
            log.debug("No matching parents for job %s and change %s",
                      jobname, change)
            add_debug_line(debug_messages,
                           "No matching parents for {jobname}".format(
                               jobname=repr(jobname)), indent=indent)
            raise NoMatchingParentError()
        return jobs

    def _createJobGraph(self, context, item, ppc, job_graph,
                        skip_file_matcher, redact_secrets_and_keys,
                        debug_messages):
        log = item.annotateLogger(self.log)
        job_list = ppc.job_list
        change = item.change
        pipeline = item.pipeline
        add_debug_line(debug_messages, "Freezing job graph")
        for jobname in job_list.jobs:
            # This is the final job we are constructing
            frozen_job = None
            log.debug("Collecting jobs %s for %s", jobname, change)
            add_debug_line(debug_messages,
                           "Freezing job {jobname}".format(
                               jobname=jobname), indent=1)
            # Create the initial list of override_checkouts, which are
            # used as we walk up the hierarchy to expand the set of
            # jobs which match.
            override_checkouts = {}
            for variant in job_list.jobs[jobname]:
                if variant.changeMatchesBranch(change):
                    self._updateOverrideCheckouts(override_checkouts, variant)
            try:
                variants = self.collectJobs(
                    item, jobname, change,
                    override_checkouts=override_checkouts,
                    debug_messages=debug_messages)
            except NoMatchingParentError:
                variants = None
            log.debug("Collected jobs %s for %s", jobname, change)
            if not variants:
                # A change must match at least one defined job variant
                # (that is to say that it must match more than just
                # the job that is defined in the tree).
                add_debug_line(debug_messages,
                               "No matching variants for {jobname}".format(
                                   jobname=jobname), indent=2)
                continue
            for variant in variants:
                if frozen_job is None:
                    frozen_job = variant.copy()
                    frozen_job.setBase(self)
                else:
                    frozen_job.applyVariant(variant, self)
                    frozen_job.name = variant.name
            frozen_job.name = jobname

            # Now merge variables set from this parent ppc
            # (i.e. project+templates) directly into the job vars
            frozen_job.updateProjectVariables(ppc.variables)

            # If the job does not specify an ansible version default to the
            # tenant default.
            if not frozen_job.ansible_version:
                frozen_job.ansible_version = \
                    self.tenant.default_ansible_version

            log.debug("Froze job %s for %s", jobname, change)
            # Whether the change matches any of the project pipeline
            # variants
            matched = False
            for variant in job_list.jobs[jobname]:
                if variant.changeMatchesBranch(change):
                    frozen_job.applyVariant(variant, self)
                    matched = True
                    log.debug("Pipeline variant %s matched %s",
                              repr(variant), change)
                    add_debug_line(debug_messages,
                                   "Pipeline variant {variant} matched".format(
                                       variant=repr(variant)), indent=2)
                else:
                    log.debug("Pipeline variant %s did not match %s",
                              repr(variant), change)
                    add_debug_line(debug_messages,
                                   "Pipeline variant {variant} did not match".
                                   format(variant=repr(variant)), indent=2)
            if not matched:
                # A change must match at least one project pipeline
                # job variant.
                add_debug_line(debug_messages,
                               "No matching pipeline variants for {jobname}".
                               format(jobname=jobname), indent=2)
                continue
            updates_job_config = False
            if not skip_file_matcher and \
               not frozen_job.changeMatchesFiles(change):
                matched_files = False
                if frozen_job.match_on_config_updates:
                    updates_job_config = item.updatesJobConfig(
                        frozen_job, self)
            else:
                matched_files = True
            if not matched_files:
                if updates_job_config:
                    # Log the reason we're ignoring the file matcher
                    log.debug("The configuration of job %s is "
                              "changed by %s; ignoring file matcher",
                              repr(frozen_job), change)
                    add_debug_line(debug_messages,
                                   "The configuration of job {jobname} is "
                                   "changed; ignoring file matcher".
                                   format(jobname=jobname), indent=2)
                else:
                    log.debug("Job %s did not match files in %s",
                              repr(frozen_job), change)
                    add_debug_line(debug_messages,
                                   "Job {jobname} did not match files".
                                   format(jobname=jobname), indent=2)
                    continue
            if frozen_job.abstract:
                raise Exception("Job %s is abstract and may not be "
                                "directly run" %
                                (frozen_job.name,))
            if (not frozen_job.ignore_allowed_projects and
                frozen_job.allowed_projects is not None and
                change.project.name not in frozen_job.allowed_projects):
                raise Exception("Project %s is not allowed to run job %s" %
                                (change.project.name, frozen_job.name))
            if ((not pipeline.post_review) and frozen_job.post_review):
                raise Exception("Pre-review pipeline %s does not allow "
                                "post-review job %s" % (
                                    pipeline.name, frozen_job.name))
            if not frozen_job.run:
                raise Exception("Job %s does not specify a run playbook" % (
                    frozen_job.name,))

            job_graph.addJob(frozen_job.freezeJob(
                context, self.tenant, self, item,
                redact_secrets_and_keys))

    def createJobGraph(self, context, item, ppc, skip_file_matcher,
                       redact_secrets_and_keys, debug_messages, old=False):
        # NOTE(pabelanger): It is possible for a foreign project not to have a
        # configured pipeline, if so return an empty JobGraph.
        if old:
            job_map = item.current_build_set._old_jobs
            if context is not None:
                raise RuntimeError("Context should be none for old job graphs")
            context = zkobject.LocalZKContext(self.log)
        else:
            job_map = item.current_build_set.jobs
        job_graph = JobGraph(job_map)
        if ppc:
            self._createJobGraph(context, item, ppc, job_graph,
                                 skip_file_matcher, redact_secrets_and_keys,
                                 debug_messages)
        return job_graph


class Semaphore(ConfigObject):
    def __init__(self, name, max=1):
        super(Semaphore, self).__init__()
        self.name = name
        self.max = int(max)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        if not isinstance(other, Semaphore):
            return False
        return (self.name == other.name and
                self.max == other.max)


class Queue(ConfigObject):
    def __init__(self, name, per_branch=False,
                 allow_circular_dependencies=False):
        super().__init__()
        self.name = name
        self.per_branch = per_branch
        self.allow_circular_dependencies = allow_circular_dependencies

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        if not isinstance(other, Queue):
            return False
        return (
            self.name == other.name and
            self.per_branch == other.per_branch and
            self.allow_circular_dependencies ==
            other.allow_circular_dependencies
        )


class Tenant(object):
    def __init__(self, name):
        self.name = name
        self.max_nodes_per_job = 5
        self.max_job_timeout = 10800
        self.exclude_unprotected_branches = False
        self.default_base_job = None
        self.layout = None
        # The unparsed configuration from the main zuul config for
        # this tenant.
        self.unparsed_config = None
        # The list of projects from which we will read full
        # configuration.
        self.config_projects = []
        # The parsed config from those projects.
        self.config_projects_config = None
        # The list of projects from which we will read untrusted
        # in-repo configuration.
        self.untrusted_projects = []
        # The parsed config from those projects.
        self.untrusted_projects_config = None
        self.semaphore_handler = None
        # Metadata about projects for this tenant
        # canonical project name -> TenantProjectConfig
        self.project_configs = {}

        # A mapping of project names to projects.  project_name ->
        # VALUE where VALUE is a further dictionary of
        # canonical_hostname -> Project.
        self.projects = {}
        self.canonical_hostnames = set()

        # The per tenant default ansible version
        self.default_ansible_version = None

        self.authorization_rules = []
        self.default_auth_realm = None

    @property
    def all_projects(self):
        """
        Return a generator for all projects of the tenant.
        """
        for hostname_dict in self.projects.values():
            for project in hostname_dict.values():
                yield project

    def _addProject(self, tpc):
        """Add a project to the project index

        :arg TenantProjectConfig tpc: The TenantProjectConfig (with
        associated project) to add.

        """
        project = tpc.project
        self.canonical_hostnames.add(project.canonical_hostname)
        hostname_dict = self.projects.setdefault(project.name, {})
        if project.canonical_hostname in hostname_dict:
            raise Exception("Project %s is already in project index" %
                            (project,))
        hostname_dict[project.canonical_hostname] = project
        self.project_configs[project.canonical_name] = tpc

    def getProject(self, name):
        """Return a project given its name.

        :arg str name: The name of the project.  It may be fully
            qualified (E.g., "git.example.com/subpath/project") or may
            contain only the project name name may be supplied (E.g.,
            "subpath/project").

        :returns: A tuple (trusted, project) or (None, None) if the
            project is not found or ambiguous.  The "trusted" boolean
            indicates whether or not the project is trusted by this
            tenant.
        :rtype: (bool, Project)

        """
        path = name.split('/', 1)
        if path[0] in self.canonical_hostnames:
            hostname = path[0]
            project_name = path[1]
        else:
            hostname = None
            project_name = name
        hostname_dict = self.projects.get(project_name)
        project = None
        if hostname_dict:
            if hostname:
                project = hostname_dict.get(hostname)
            else:
                values = list(hostname_dict.values())
                if len(values) == 1:
                    project = values[0]
                else:
                    raise Exception("Project name '%s' is ambiguous, "
                                    "please fully qualify the project "
                                    "with a hostname" % (name,))
        if project is None:
            return (None, None)
        if project in self.config_projects:
            return (True, project)
        if project in self.untrusted_projects:
            return (False, project)
        # This should never happen:
        raise Exception("Project %s is neither trusted nor untrusted" %
                        (project,))

    def getProjectsByRegex(self, regex):
        """Return all projects with a full match to either project name or
        canonical project name.

        :arg str regex: The regex to match
        :returns: A list of tuples (trusted, project) describing the found
            projects. Raises an exception if the same project name is found
            several times across multiple hostnames.
        """

        matcher = re2.compile(regex)
        projects = []
        result = []

        for name, hostname_dict in self.projects.items():

            if matcher.fullmatch(name):
                # validate that this match is unambiguous
                values = list(hostname_dict.values())
                if len(values) > 1:
                    raise Exception("Project name '%s' is ambiguous, "
                                    "please fully qualify the project "
                                    "with a hostname. Valid hostnames "
                                    "are %s." % (name, hostname_dict.keys()))
                projects.append(values[0])
            else:
                # try to match canonical project names
                for project in hostname_dict.values():
                    if matcher.fullmatch(project.canonical_name):
                        projects.append(project)

        for project in projects:
            if project in self.config_projects:
                result.append((True, project))
            elif project in self.untrusted_projects:
                result.append((False, project))
            else:
                raise Exception("Project %s is neither trusted nor untrusted" %
                                (project,))
        return result

    def getProjectBranches(self, project_canonical_name):
        """Return a project's branches (filtered by this tenant config)

        :arg str project_canonical: The project's canonical name.

        :returns: A list of branch names.
        :rtype: [str]

        """
        tpc = self.project_configs[project_canonical_name]
        return tpc.branches

    def getExcludeUnprotectedBranches(self, project):
        # Evaluate if unprotected branches should be excluded or not. The first
        # match wins. The order is project -> tenant (default is false).
        project_config = self.project_configs.get(project.canonical_name)
        if project_config.exclude_unprotected_branches is not None:
            exclude_unprotected = project_config.exclude_unprotected_branches
        else:
            exclude_unprotected = self.exclude_unprotected_branches
        return exclude_unprotected

    def addConfigProject(self, tpc):
        self.config_projects.append(tpc.project)
        self._addProject(tpc)

    def addUntrustedProject(self, tpc):
        self.untrusted_projects.append(tpc.project)
        self._addProject(tpc)

    def getSafeAttributes(self):
        return Attributes(name=self.name)


class UnparsedBranchCache(object):
    """Cache information about a single branch"""
    def __init__(self):
        self.load_skipped = True
        self.extra_files_searched = set()
        self.extra_dirs_searched = set()
        self.files = {}
        self.ltime = -1

    def isValidFor(self, tpc, min_ltime):
        """Return True if this has valid cache results for the extra
        files/dirs in the tpc.
        """
        if self.load_skipped:
            return False
        if self.ltime < min_ltime:
            return False
        if (set(tpc.extra_config_files) <= self.extra_files_searched and
            set(tpc.extra_config_dirs) <= self.extra_dirs_searched):
            return True
        return False

    def setValidFor(self, tpc, ltime):
        self.ltime = ltime
        self.load_skipped = False
        self.extra_files_searched |= set(tpc.extra_config_files)
        self.extra_dirs_searched |= set(tpc.extra_config_dirs)

    def put(self, path, config):
        self.files[path] = config

    def get(self, tpc):
        ret = UnparsedConfig()
        files_list = self.files.keys()
        fns1 = []
        fns2 = []
        fns3 = []
        fns4 = []
        for fn in files_list:
            if fn.startswith("zuul.d/"):
                fns1.append(fn)
            if fn.startswith(".zuul.d/"):
                fns2.append(fn)
            for ef in tpc.extra_config_files:
                if fn.startswith(ef):
                    fns3.append(fn)
            for ed in tpc.extra_config_dirs:
                if fn.startswith(ed):
                    fns4.append(fn)
        fns = (["zuul.yaml"] + sorted(fns1) + [".zuul.yaml"] +
               sorted(fns2) + fns3 + sorted(fns4))
        for fn in fns:
            data = self.files.get(fn)
            if data is not None:
                ret.extend(data)
        return ret


class Abide(object):
    def __init__(self):
        self.admin_rules = {}
        self.tenants = {}
        # tenant -> project -> list(tpcs)
        # The project TPCs are stored as a list as we don't check for
        # duplicate projects here.
        self.config_tpcs = defaultdict(lambda: defaultdict(list))
        self.untrusted_tpcs = defaultdict(lambda: defaultdict(list))
        # project -> branch -> UnparsedBranchCache
        self.unparsed_project_branch_cache = {}

    def addConfigTPC(self, tenant_name, tpc):
        self.config_tpcs[tenant_name][tpc.project.name].append(tpc)

    def getConfigTPCs(self, tenant_name):
        return list(itertools.chain.from_iterable(
            self.config_tpcs[tenant_name].values()))

    def addUntrustedTPC(self, tenant_name, tpc):
        self.untrusted_tpcs[tenant_name][tpc.project.name].append(tpc)

    def getUntrustedTPCs(self, tenant_name):
        return list(itertools.chain.from_iterable(
            self.untrusted_tpcs[tenant_name].values()))

    def clearTPCs(self, tenant_name):
        self.config_tpcs[tenant_name].clear()
        self.untrusted_tpcs[tenant_name].clear()

    def _allProjectTPCs(self, project_name):
        # Flatten the lists of a project TPCs from all tenants
        return itertools.chain.from_iterable(
            tenant_tpcs.get(project_name, [])
            for tenant_tpcs in itertools.chain(self.config_tpcs.values(),
                                               self.untrusted_tpcs.values()))

    def getExtraConfigFiles(self, project_name):
        """Get all extra config files for a project accross tenants."""
        return set(itertools.chain.from_iterable(
            tpc.extra_config_files
            for tpc in self._allProjectTPCs(project_name)))

    def getExtraConfigDirs(self, project_name):
        """Get all extra config dirs for a project accross tenants."""
        return set(itertools.chain.from_iterable(
            tpc.extra_config_dirs
            for tpc in self._allProjectTPCs(project_name)))

    def hasUnparsedBranchCache(self, canonical_project_name, branch):
        project_branch_cache = self.unparsed_project_branch_cache.setdefault(
            canonical_project_name, {})
        cache = project_branch_cache.get(branch)
        if cache is None:
            return False
        return True

    def getUnparsedBranchCache(self, canonical_project_name, branch):
        project_branch_cache = self.unparsed_project_branch_cache.setdefault(
            canonical_project_name, {})
        cache = project_branch_cache.get(branch)
        if cache is not None:
            return cache
        project_branch_cache[branch] = UnparsedBranchCache()
        return project_branch_cache[branch]

    def clearUnparsedBranchCache(self, canonical_project_name, branch=None):
        if canonical_project_name in self.unparsed_project_branch_cache:
            project_branch_cache = \
                self.unparsed_project_branch_cache[canonical_project_name]

            if branch in project_branch_cache:
                del project_branch_cache[branch]

            if len(project_branch_cache) == 0 or branch is None:
                del self.unparsed_project_branch_cache[canonical_project_name]


class Capabilities(object):
    """The set of capabilities this Zuul installation has.

    Some plugins add elements to the external API. In order to
    facilitate consumers knowing if functionality is available
    or not, keep track of distinct capability flags.
    """
    def __init__(self, **kwargs):
        self.capabilities = kwargs

    def __repr__(self):
        return '<Capabilities 0x%x %s>' % (id(self), self._renderFlags())

    def _renderFlags(self):
        return " ".join(['{k}={v}'.format(k=k, v=repr(v))
                         for (k, v) in self.capabilities.items()])

    def copy(self):
        return Capabilities(**self.toDict())

    def toDict(self):
        return self.capabilities


class WebInfo(object):
    """Information about the system needed by zuul-web /info."""

    def __init__(self, websocket_url=None,
                 capabilities=None, stats_url=None,
                 stats_prefix=None, stats_type=None):
        _caps = capabilities
        if _caps is None:
            _caps = Capabilities(**capabilities_registry.capabilities)
        self.capabilities = _caps
        self.stats_prefix = stats_prefix
        self.stats_type = stats_type
        self.stats_url = stats_url
        self.tenant = None
        self.websocket_url = websocket_url

    def __repr__(self):
        return '<WebInfo 0x%x capabilities=%s>' % (
            id(self), str(self.capabilities))

    def copy(self):
        return WebInfo(
            capabilities=self.capabilities.copy(),
            stats_prefix=self.stats_prefix,
            stats_type=self.stats_type,
            stats_url=self.stats_url,
            websocket_url=self.websocket_url)

    @staticmethod
    def fromConfig(config):
        return WebInfo(
            stats_prefix=get_default(config, 'statsd', 'prefix'),
            stats_type=get_default(config, 'web', 'stats_type', 'graphite'),
            stats_url=get_default(config, 'web', 'stats_url', None),
            websocket_url=get_default(config, 'web', 'websocket_url', None),
        )

    def toDict(self):
        d = dict()
        d['capabilities'] = self.capabilities.toDict()
        d['websocket_url'] = self.websocket_url
        stats = dict()
        stats['prefix'] = self.stats_prefix
        stats['type'] = self.stats_type
        stats['url'] = self.stats_url
        d['stats'] = stats
        if self.tenant:
            d['tenant'] = self.tenant
        return d


class HoldRequest(object):
    def __init__(self):
        self.lock = None
        self.stat = None
        self.id = None
        self.expired = None
        self.tenant = None
        self.project = None
        self.job = None
        self.ref_filter = None
        self.reason = None
        self.node_expiration = None
        # When max_count == current_count, hold request can no longer be used.
        self.max_count = 1
        self.current_count = 0

        # The hold request 'nodes' attribute is a list of dictionaries
        # (one list entry per hold request count) containing the build
        # ID (build) and a list of nodes (nodes) held for that build.
        # Example:
        #
        #  hold_request.nodes = [
        #    { 'build': 'ca01...', 'nodes': ['00000001', '00000002'] },
        #    { 'build': 'fb72...', 'nodes': ['00000003', '00000004'] },
        #  ]
        self.nodes = []

    def __str__(self):
        return "<HoldRequest %s: tenant=%s project=%s job=%s ref_filter=%s>" \
            % (self.id, self.tenant, self.project, self.job, self.ref_filter)

    @staticmethod
    def fromDict(data):
        '''
        Return a new object from the given data dictionary.
        '''
        obj = HoldRequest()
        obj.expired = data.get('expired')
        obj.tenant = data.get('tenant')
        obj.project = data.get('project')
        obj.job = data.get('job')
        obj.ref_filter = data.get('ref_filter')
        obj.max_count = data.get('max_count')
        obj.current_count = data.get('current_count')
        obj.reason = data.get('reason')
        obj.node_expiration = data.get('node_expiration')
        obj.nodes = data.get('nodes', [])
        return obj

    def toDict(self):
        '''
        Return a dictionary representation of the object.
        '''
        d = dict()
        d['id'] = self.id
        d['expired'] = self.expired
        d['tenant'] = self.tenant
        d['project'] = self.project
        d['job'] = self.job
        d['ref_filter'] = self.ref_filter
        d['max_count'] = self.max_count
        d['current_count'] = self.current_count
        d['reason'] = self.reason
        d['node_expiration'] = self.node_expiration
        d['nodes'] = self.nodes
        return d

    def updateFromDict(self, d):
        '''
        Update current object with data from the given dictionary.
        '''
        self.expired = d.get('expired')
        self.tenant = d.get('tenant')
        self.project = d.get('project')
        self.job = d.get('job')
        self.ref_filter = d.get('ref_filter')
        self.max_count = d.get('max_count', 1)
        self.current_count = d.get('current_count', 0)
        self.reason = d.get('reason')
        self.node_expiration = d.get('node_expiration')

    def serialize(self):
        '''
        Return a representation of the object as a string.

        Used for storing the object data in ZooKeeper.
        '''
        return json.dumps(self.toDict(), sort_keys=True).encode('utf8')


# AuthZ models

class AuthZRule(object):
    """The base class for authorization rules"""

    def __ne__(self, other):
        return not self.__eq__(other)


class ClaimRule(AuthZRule):
    """This rule checks the value of a claim.
    The check tries to be smart by assessing the type of the tested value."""
    def __init__(self, claim=None, value=None):
        super(ClaimRule, self).__init__()
        self.claim = claim or 'sub'
        self.value = value

    def templated(self, value, tenant=None):
        template_dict = {}
        if tenant is not None:
            template_dict['tenant'] = tenant.getSafeAttributes()
        return value.format(**template_dict)

    def _match_jsonpath(self, claims, tenant):
        matches = [match.value
                   for match in jsonpath_rw.parse(self.claim).find(claims)]
        t_value = self.templated(self.value, tenant)
        if len(matches) == 1:
            match = matches[0]
            if isinstance(match, list):
                return t_value in match
            elif isinstance(match, str):
                return t_value == match
            else:
                # unsupported type - don't raise, but this should be notified
                return False
        else:
            # TODO we should differentiate no match and 2+ matches
            return False

    def _match_dict(self, claims, tenant):
        def _compare(value, claim):
            if isinstance(value, list):
                t_value = map(self.templated, value, [tenant] * len(value))
                if isinstance(claim, list):
                    # if the claim is empty, the value must be empty too:
                    if claim == []:
                        return t_value == []
                    else:
                        return (set(claim) <= set(t_value))
                else:
                    return claim in value
            elif isinstance(value, dict):
                if not isinstance(claim, dict):
                    return False
                elif value == {}:
                    return claim == {}
                else:
                    return all(_compare(value[x], claim.get(x, {}))
                               for x in value.keys())
            else:
                t_value = self.templated(value, tenant)
                return t_value == claim

        return _compare(self.value, claims.get(self.claim, {}))

    def __call__(self, claims, tenant=None):
        if isinstance(self.value, dict):
            return self._match_dict(claims, tenant)
        else:
            return self._match_jsonpath(claims, tenant)

    def __eq__(self, other):
        if not isinstance(other, ClaimRule):
            return False
        return (self.claim == other.claim and self.value == other.value)

    def __repr__(self):
        return '<ClaimRule "%s":"%s">' % (self.claim, self.value)

    def __hash__(self):
        return hash(repr(self))


class OrRule(AuthZRule):

    def __init__(self, subrules):
        super(OrRule, self).__init__()
        self.rules = set(subrules)

    def __call__(self, claims, tenant=None):
        return any(rule(claims, tenant) for rule in self.rules)

    def __eq__(self, other):
        if not isinstance(other, OrRule):
            return False
        return self.rules == other.rules

    def __repr__(self):
        return '<OrRule %s>' % ('  || '.join(repr(r) for r in self.rules))

    def __hash__(self):
        return hash(repr(self))


class AndRule(AuthZRule):

    def __init__(self, subrules):
        super(AndRule, self).__init__()
        self.rules = set(subrules)

    def __call__(self, claims, tenant=None):
        return all(rule(claims, tenant) for rule in self.rules)

    def __eq__(self, other):
        if not isinstance(other, AndRule):
            return False
        return self.rules == other.rules

    def __repr__(self):
        return '<AndRule %s>' % (' && '.join(repr(r) for r in self.rules))

    def __hash__(self):
        return hash(repr(self))


class AuthZRuleTree(object):

    def __init__(self, name):
        self.name = name
        # initialize actions as unauthorized
        self.ruletree = None

    def __call__(self, claims, tenant=None):
        return self.ruletree(claims, tenant)

    def __eq__(self, other):
        if not isinstance(other, AuthZRuleTree):
            return False
        return (self.name == other.name and
                self.ruletree == other.ruletree)

    def __repr__(self):
        return '<AuthZRuleTree [ %s ]>' % self.ruletree
