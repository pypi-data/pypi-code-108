# Copyright 2014 OpenStack Foundation
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
import os
import socket
import sys
import threading
import time
from abc import ABCMeta
from configparser import ConfigParser

from kazoo.exceptions import NoNodeError

from zuul.lib import commandsocket
from zuul.lib.config import get_default
from zuul.lib.logutil import get_annotated_logger
from zuul.merger import merger
from zuul.merger.merger import nullcontext
from zuul.model import (
    FilesChangesCompletedEvent, MergeCompletedEvent, MergeRequest
)
from zuul.lib.monitoring import MonitoringServer
from zuul.version import get_version_string
from zuul.zk import ZooKeeperClient
from zuul.zk.components import MergerComponent
from zuul.zk.event_queues import PipelineResultEventQueue
from zuul.zk.merger import MergerApi

COMMANDS = ['stop', 'pause', 'unpause']


class BaseRepoLocks(metaclass=ABCMeta):

    def getRepoLock(self, connection_name, project_name):
        return nullcontext()


class RepoLocks(BaseRepoLocks):

    def __init__(self):
        self.locks = {}

    def getRepoLock(self, connection_name, project_name):
        key = '%s:%s' % (connection_name, project_name)
        self.locks.setdefault(key, threading.Lock())
        return self.locks[key]


class BaseMergeServer(metaclass=ABCMeta):
    log = logging.getLogger("zuul.BaseMergeServer")

    _repo_locks_class = BaseRepoLocks

    def __init__(
        self,
        config: ConfigParser,
        component: str,
        connections,
    ):
        self.connections = connections
        self._merger_running = False
        self._merger_paused = False
        self.merge_email = get_default(config, 'merger', 'git_user_email',
                                       'zuul.merger.default@example.com')
        self.merge_name = get_default(config, 'merger', 'git_user_name',
                                      'Zuul Merger Default')
        self.merge_speed_limit = get_default(
            config, 'merger', 'git_http_low_speed_limit', '1000')
        self.merge_speed_time = get_default(
            config, 'merger', 'git_http_low_speed_time', '30')
        self.git_timeout = get_default(config, 'merger', 'git_timeout', 300)

        self.merge_root = get_default(config, component, 'git_dir',
                                      '/var/lib/zuul/{}-git'.format(component))

        self.config = config

        self.zk_client = ZooKeeperClient.fromConfig(self.config)
        self.zk_client.connect()

        self.result_events = PipelineResultEventQueue.createRegistry(
            self.zk_client
        )

        self.merger_thread = threading.Thread(
            target=self.runMerger,
            name="Merger",
        )

        self.merger_loop_wake_event = threading.Event()

        self.merger_api = MergerApi(
            self.zk_client,
            merge_request_callback=self.merger_loop_wake_event.set,
        )

        # This merger and its git repos are used to maintain
        # up-to-date copies of all the repos that are used by jobs, as
        # well as to support the merger:cat functon to supply
        # configuration information to Zuul when it starts.
        self.merger = self._getMerger(self.merge_root, None,
                                      execution_context=False)

        # Repo locking is needed on the executor
        self.repo_locks = self._repo_locks_class()

    def _getMerger(self, root, cache_root, logger=None,
                   execution_context=True, scheme=None,
                   cache_scheme=None):
        return merger.Merger(
            root,
            self.connections,
            self.zk_client,
            self.merge_email,
            self.merge_name,
            self.merge_speed_limit,
            self.merge_speed_time,
            cache_root,
            logger,
            execution_context=execution_context,
            git_timeout=self.git_timeout,
            scheme=scheme,
            cache_scheme=cache_scheme,
        )

    def _repoLock(self, connection_name, project_name):
        # The merger does not need locking so return a null lock.
        return nullcontext()

    def _update(self, connection_name, project_name, zuul_event_id=None):
        # The executor overrides _update so it can do the update
        # asynchronously.
        self.merger.updateRepo(connection_name, project_name,
                               zuul_event_id=zuul_event_id)

    def start(self):
        self.log.debug('Starting merger')
        self.log.debug('Cleaning any stale git index.lock files')
        for (dirpath, dirnames, filenames) in os.walk(self.merge_root):
            if '.git' in dirnames:
                # Only recurse into .git dirs
                dirnames.clear()
                dirnames.append('.git')
            elif dirpath.endswith('/.git'):
                # Recurse no further
                dirnames.clear()
                if 'index.lock' in filenames:
                    fp = os.path.join(dirpath, 'index.lock')
                    try:
                        os.unlink(fp)
                        self.log.debug('Removed stale git lock: %s' % fp)
                    except Exception:
                        self.log.exception(
                            'Unable to remove stale git lock: '
                            '%s this may result in failed merges' % fp)
        self._merger_running = True
        self.merger_thread.start()

    def stop(self):
        self.log.debug('Stopping merger')
        self._merger_running = False
        self.merger_loop_wake_event.set()
        self.zk_client.disconnect()

    def join(self):
        self.merger_loop_wake_event.set()
        self.merger_thread.join()

    def pause(self):
        self.log.debug('Pausing merger')
        self._merger_paused = True

    def unpause(self):
        self.log.debug('Resuming merger')
        self._merger_paused = False
        self.merger_loop_wake_event.set()

    def runMerger(self):
        while self._merger_running:
            self.merger_loop_wake_event.wait()
            self.merger_loop_wake_event.clear()
            if self._merger_paused:
                continue
            try:
                for merge_request in self.merger_api.next():
                    if not self._merger_running:
                        break
                    self._runMergeJob(merge_request)
            except Exception:
                self.log.exception("Error in merge thread:")
                time.sleep(5)
                self.merger_loop_wake_event.set()

    def _runMergeJob(self, merge_request):
        log = get_annotated_logger(
            self.log, merge_request.event_id
        )
        # Lock and update the merge request
        if not self.merger_api.lock(merge_request, blocking=False):
            return

        # Ensure that the request is still in state requested. This method is
        # called based on cached data and there might be a mismatch between the
        # cached state and the real state of the request. The lock might
        # have been successful because the request is already completed and
        # thus unlocked.
        if merge_request.state != MergeRequest.REQUESTED:
            self._retry(merge_request.lock, log, self.merger_api.unlock,
                        merge_request)

        try:
            merge_request.state = MergeRequest.RUNNING
            params = self.merger_api.getParams(merge_request)
        except Exception:
            log.exception("Exception while preparing to start merge job")
            # If we failed at this point, we have not written anything
            # to ZK yet; the only thing we need to do is to ensure
            # that we release the lock, and another merger will be
            # able to grab the request.
            self._retry(merge_request.lock, log, self.merger_api.unlock,
                        merge_request)
            return

        result = None
        try:
            self.merger_api.clearParams(merge_request)
            # Directly update the merge request in ZooKeeper, so we
            # don't loop over and try to lock it again and again.
            self.merger_api.update(merge_request)
            self.log.debug("Next executed merge job: %s", merge_request)
            try:
                result = self.executeMergeJob(merge_request, params)
            except Exception:
                log.exception("Error running merge job:")
        finally:
            self.completeMergeJob(merge_request, result)

    def executeMergeJob(self, merge_request, params):
        result = None
        if merge_request.job_type == MergeRequest.MERGE:
            result = self.merge(merge_request, params)
        elif merge_request.job_type == MergeRequest.CAT:
            result = self.cat(merge_request, params)
        elif merge_request.job_type == MergeRequest.REF_STATE:
            result = self.refstate(merge_request, params)
        elif merge_request.job_type == MergeRequest.FILES_CHANGES:
            result = self.fileschanges(merge_request, params)
        return result

    def cat(self, merge_request, args):
        self.log.debug("Got cat job: %s", merge_request.uuid)

        connection_name = args['connection']
        project_name = args['project']

        lock = self.repo_locks.getRepoLock(connection_name, project_name)
        try:
            self._update(connection_name, project_name)
            with lock:
                files = self.merger.getFiles(connection_name, project_name,
                                             args['branch'], args['files'],
                                             args.get('dirs'))
        except Exception:
            result = dict(update=False)
        else:
            result = dict(updated=True, files=files)

        return result

    def merge(self, merge_request, args):
        self.log.debug("Got merge job: %s", merge_request.uuid)
        zuul_event_id = merge_request.event_id

        for item in args['items']:
            self._update(item['connection'], item['project'])
        ret = self.merger.mergeChanges(
            args['items'], args.get('files'),
            args.get('dirs', []),
            args.get('repo_state'),
            branches=args.get('branches'),
            repo_locks=self.repo_locks,
            zuul_event_id=zuul_event_id)

        result = dict(merged=(ret is not None))
        if ret is None:
            result['commit'] = result['files'] = result['repo_state'] = None
        else:
            (result['commit'], result['files'], result['repo_state'],
             recent, orig_commit) = ret
        result['zuul_event_id'] = zuul_event_id
        return result

    def refstate(self, merge_request, args):
        self.log.debug("Got refstate job: %s", merge_request.uuid)
        zuul_event_id = merge_request.event_id
        success, repo_state, item_in_branches = \
            self.merger.getRepoState(
                args['items'], self.repo_locks, branches=args.get('branches'))
        result = dict(updated=success,
                      repo_state=repo_state,
                      item_in_branches=item_in_branches)
        result['zuul_event_id'] = zuul_event_id
        return result

    def fileschanges(self, merge_request, args):
        self.log.debug("Got fileschanges job: %s", merge_request.uuid)
        zuul_event_id = merge_request.event_id

        connection_name = args['connection']
        project_name = args['project']

        lock = self.repo_locks.getRepoLock(connection_name, project_name)
        try:
            self._update(connection_name, project_name,
                         zuul_event_id=zuul_event_id)
            with lock:
                files = self.merger.getFilesChanges(
                    connection_name, project_name,
                    args['branch'], args['tosha'],
                    zuul_event_id=zuul_event_id)
        except Exception:
            result = dict(update=False)
        else:
            result = dict(updated=True, files=files)

        result['zuul_event_id'] = zuul_event_id
        return result

    def completeMergeJob(self, merge_request, result):
        log = get_annotated_logger(self.log, merge_request.event_id)

        # Always provide a result event, even if we have no
        # information; otherwise items can get stuck in the queue.
        if result is None:
            result = {}

        payload = json.dumps(result, sort_keys=True)
        self.log.debug("Completed %s job %s: payload size: %s",
                       merge_request.job_type, merge_request.uuid,
                       sys.getsizeof(payload))
        merged = result.get("merged", False)
        updated = result.get("updated", False)
        commit = result.get("commit")
        repo_state = result.get("repo_state", {})
        item_in_branches = result.get("item_in_branches", [])
        files = result.get("files", {})

        log.info(
            "Merge %s complete, merged: %s, updated: %s, commit: %s, "
            "branches: %s",
            merge_request,
            merged,
            updated,
            commit,
            item_in_branches,
        )

        lock_valid = merge_request.lock.is_still_valid()
        if not lock_valid:
            return

        # Provide a result either via a result future or a result event
        if merge_request.result_path:
            log.debug(
                "Providing synchronous result via future for %s",
                merge_request,
            )
            self._retry(merge_request.lock, log,
                        self.merger_api.reportResult, merge_request, result)

        elif merge_request.build_set_uuid:
            log.debug(
                "Providing asynchronous result via result event for %s",
                merge_request,
            )
            if merge_request.job_type == MergeRequest.FILES_CHANGES:
                event = FilesChangesCompletedEvent(
                    merge_request.build_set_uuid, files
                )
            else:
                event = MergeCompletedEvent(
                    merge_request.uuid,
                    merge_request.build_set_uuid,
                    merged,
                    updated,
                    commit,
                    files,
                    repo_state,
                    item_in_branches,
                )

            def put_complete_event(log, merge_request, event):
                try:
                    self.result_events[merge_request.tenant_name][
                        merge_request.pipeline_name].put(event)
                except NoNodeError:
                    log.warning("Pipeline was removed: %s",
                                merge_request.pipeline_name)

            self._retry(merge_request.lock, log,
                        put_complete_event, log, merge_request, event)

        # Set the merge request to completed, unlock and delete it. Although
        # the state update is mainly for consistency reasons, it might come in
        # handy in case the deletion or unlocking failes. Thus, we know that
        # the merge request was already processed and we have a result in the
        # result queue.
        merge_request.state = MergeRequest.COMPLETED
        self._retry(merge_request.lock, log,
                    self.merger_api.update, merge_request)
        self._retry(merge_request.lock, log,
                    self.merger_api.unlock, merge_request)
        # TODO (felix): If we want to optimize ZK requests, we could only call
        # the remove() here.
        self.merger_api.remove(merge_request)

    def _retry(self, lock, log, fn, *args, **kw):
        """Retry a method to deal with ZK connection issues

        This is a helper method to retry ZK operations as long as it
        makes sense to do so.  If we have encountered a suspended
        connection, we can probably just retry the ZK operation until
        it succeeds.  If we have fully lost the connection, then we
        have lost the lock, so we may not care in that case.

        This method exits when one of the following occurs:

        * The callable function completes.
        * This server stops.
        * The lock (if supplied) is invalidated due to connection loss.

        Pass None as the lock parameter if the lock issue is not
        relevant.
        """
        while True:
            if lock and not lock.is_still_valid():
                return
            try:
                return fn(*args, **kw)
            except Exception:
                log.exception("Exception retrying %s", fn)
            if not self._running:
                return
            time.sleep(5)


class MergeServer(BaseMergeServer):
    log = logging.getLogger("zuul.MergeServer")

    def __init__(
        self,
        config: ConfigParser,
        connections,
    ):
        super().__init__(config, 'merger', connections)
        self.hostname = socket.getfqdn()
        self.component_info = MergerComponent(
            self.zk_client, self.hostname, version=get_version_string())
        self.component_info.register()

        self.monitoring_server = MonitoringServer(self.config, 'merger',
                                                  self.component_info)
        self.monitoring_server.start()

        self.command_map = dict(
            stop=self.stop,
            pause=self.pause,
            unpause=self.unpause,
        )
        command_socket = get_default(
            self.config, 'merger', 'command_socket',
            '/var/lib/zuul/merger.socket')
        self.command_socket = commandsocket.CommandSocket(command_socket)

        self._command_running = False

    def start(self):
        super().start()
        self._command_running = True
        self.log.debug("Starting command processor")
        self.command_socket.start()
        self.command_thread = threading.Thread(
            target=self.runCommand, name='command')
        self.command_thread.daemon = True
        self.command_thread.start()
        self.component_info.state = self.component_info.RUNNING

    def stop(self):
        self.log.debug("Stopping")
        self.component_info.state = self.component_info.STOPPED
        super().stop()
        self._command_running = False
        self.command_socket.stop()
        self.monitoring_server.stop()
        self.log.debug("Stopped")

    def join(self):
        super().join()
        self.monitoring_server.join()

    def pause(self):
        self.log.debug('Pausing')
        self.component_info.state = self.component_info.PAUSED
        super().pause()

    def unpause(self):
        self.log.debug('Resuming')
        super().unpause()
        self.component_info.state = self.component_info.RUNNING

    def runCommand(self):
        while self._command_running:
            try:
                command = self.command_socket.get().decode('utf8')
                if command != '_stop':
                    self.command_map[command]()
            except Exception:
                self.log.exception("Exception while processing command")
