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

import logging
from uuid import uuid4

from zuul.lib.config import get_default
from zuul.lib.logutil import get_annotated_logger
from zuul.model import (
    FilesChangesCompletedEvent,
    MergeCompletedEvent,
    MergeRequest,
    PRECEDENCE_HIGH,
    PRECEDENCE_NORMAL,
)
from zuul.zk.event_queues import PipelineResultEventQueue
from zuul.zk.merger import MergerApi
from zuul.zk.exceptions import JobRequestNotFound
from kazoo.exceptions import BadVersionError, NoNodeError


class MergeClient(object):
    log = logging.getLogger("zuul.MergeClient")

    _merger_api_class = MergerApi

    def __init__(self, config, sched):
        self.config = config
        self.sched = sched
        self.git_timeout = get_default(
            self.config, 'merger', 'git_timeout', 300)
        self.merger_api = self._merger_api_class(self.sched.zk_client)
        self.result_events = PipelineResultEventQueue.createRegistry(
            self.sched.zk_client
        )

    def submitJob(
        self,
        job_type,
        data,
        build_set,
        precedence=PRECEDENCE_NORMAL,
        needs_result=False,
        event=None,
    ):
        # We need the tenant, pipeline and queue names to put the merge result
        # in the correct queue. The only source for those values in this
        # context is the buildset. If no buildset is provided, we can't provide
        # a result event. In those cases a user of this function can fall back
        # to the return value which provides the result as a future stored in a
        # ZooKeeper path.
        build_set_uuid = None
        tenant_name = None
        pipeline_name = None

        if build_set is not None:
            build_set_uuid = build_set.uuid
            tenant_name = build_set.item.pipeline.tenant.name
            pipeline_name = build_set.item.pipeline.name

        uuid = str(uuid4().hex)

        log = get_annotated_logger(self.log, event)
        log.debug("Submitting job %s with data %s", uuid, data)

        request = MergeRequest(
            uuid=uuid,
            job_type=job_type,
            build_set_uuid=build_set_uuid,
            tenant_name=tenant_name,
            pipeline_name=pipeline_name,
            event_id=event.zuul_event_id if event else None,
            precedence=precedence
        )
        return self.merger_api.submit(request, data,
                                      needs_result=needs_result)

    def mergeChanges(self, items, build_set, files=None, dirs=None,
                     repo_state=None, precedence=PRECEDENCE_NORMAL,
                     branches=None, event=None):
        data = dict(items=items,
                    files=files,
                    dirs=dirs,
                    repo_state=repo_state,
                    branches=branches)
        self.submitJob(
            MergeRequest.MERGE, data, build_set, precedence, event=event)

    def getRepoState(self, items, build_set, precedence=PRECEDENCE_NORMAL,
                     branches=None, event=None):
        data = dict(items=items, branches=branches)
        self.submitJob(
            MergeRequest.REF_STATE, data, build_set, precedence, event=event)

    def getFiles(self, connection_name, project_name, branch, files, dirs=[],
                 precedence=PRECEDENCE_HIGH, event=None):
        data = dict(connection=connection_name,
                    project=project_name,
                    branch=branch,
                    files=files,
                    dirs=dirs)
        job = self.submitJob(
            MergeRequest.CAT,
            data,
            None,
            precedence,
            needs_result=True,
            event=event,
        )
        return job

    def getFilesChanges(self, connection_name, project_name, branch,
                        tosha=None, precedence=PRECEDENCE_HIGH,
                        build_set=None, needs_result=False, event=None):
        data = dict(connection=connection_name,
                    project=project_name,
                    branch=branch,
                    tosha=tosha)
        job = self.submitJob(
            MergeRequest.FILES_CHANGES,
            data,
            build_set,
            precedence,
            needs_result=needs_result,
            event=event,
        )
        return job

    def cleanupLostMergeRequests(self):
        for merge_request in self.merger_api.lostRequests():
            try:
                self.cleanupLostMergeRequest(merge_request)
            except Exception:
                self.log.exception("Exception cleaning up lost merge request:")

    def cleanupLostMergeRequest(self, merge_request):
        # Provide a result either via a result future or a result event
        if merge_request.result_path:
            self.log.debug(
                "Merge request cleanup providing synchronous result "
                "via future for %s", merge_request)
            result = {}
            self.merger_api.reportResult(merge_request, result)

        elif merge_request.build_set_uuid:
            self.log.debug(
                "Merge request cleanup providing asynchronous result "
                "via result event for %s", merge_request)
            if merge_request.job_type == MergeRequest.FILES_CHANGES:
                event = FilesChangesCompletedEvent(
                    merge_request.build_set_uuid, files=None
                )
            else:
                event = MergeCompletedEvent(
                    merge_request.uuid,
                    merge_request.build_set_uuid,
                    merged=False,
                    updated=False,
                    commit=None,
                    files=None,
                    repo_state=None,
                    item_in_branches=None,
                )
            try:
                self.result_events[merge_request.tenant_name][
                    merge_request.pipeline_name].put(event)
            except NoNodeError:
                self.log.warning("Pipeline was removed: %s",
                                 merge_request.pipeline_name)

        merge_request.state = MergeRequest.COMPLETED
        try:
            self.merger_api.update(merge_request)
            # No need to unlock the build, as it is by definition unlocked.
            # TODO (felix): If we want to optimize ZK requests, we could only
            # call the remove() here.
            self.merger_api.remove(merge_request)
        except JobRequestNotFound as e:
            self.log.warning("Could not complete merge: %s", str(e))
            # In case we re-created the lock directory, still remove
            # the request for the side effect of removing the lock.
            self.merger_api.remove(merge_request)
            return
        except BadVersionError:
            # There could be a race condition:
            # The merge request is found by lost_merge_requests in
            # state RUNNING but gets completed/unlocked before the
            # is_locked() check. Since we use the znode version, the
            # update will fail in this case and we can simply ignore
            # the exception.
            return

    def cancel(self, job):
        try:
            # Try to remove the request first
            request = self.merger_api.get(job.request_path)
            if request:
                if self.merger_api.lock(request, blocking=False):
                    try:
                        self.merger_api.remove(request)
                    finally:
                        self.merger_api.unlock(request)
        finally:
            # Regardless of that, remove the waiter node
            job.cancel()
