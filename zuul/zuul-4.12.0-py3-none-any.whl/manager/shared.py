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

from abc import ABCMeta

from zuul import model
from zuul.lib.logutil import get_annotated_logger
from zuul.manager import PipelineManager, StaticChangeQueueContextManager
from zuul.manager import DynamicChangeQueueContextManager


class ChangeQueueManager:

    def __init__(self, pipeline_manager, name=None, per_branch=False):
        self.log = pipeline_manager.log
        self.pipeline_manager = pipeline_manager
        self.name = name
        self.per_branch = per_branch
        self.projects = []
        self.created_for_branches = {}

    def addProject(self, project):
        self.projects.append(project)

    def getOrCreateQueue(self, project, branch):
        change_queue = self.created_for_branches.get(branch)

        if not change_queue:
            p = self.pipeline_manager.pipeline
            name = self.name or project.name
            change_queue = self.pipeline_manager.constructChangeQueue(name)
            p.addQueue(change_queue)
            self.created_for_branches[branch] = change_queue

        if not change_queue.matches(project.canonical_name, branch):
            change_queue.addProject(project, branch)
            self.log.debug("Added project %s to queue: %s" %
                           (project, change_queue))

        return change_queue


class SharedQueuePipelineManager(PipelineManager, metaclass=ABCMeta):
    """Intermediate class that adds the shared-queue behavior.

    This is not a full pipeline manager; it just adds the shared-queue
    behavior to the base class and is used by the dependent and serial
    managers.
    """

    changes_merge = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.change_queue_managers = []

    def buildChangeQueues(self, layout):
        self.log.debug("Building shared change queues")
        change_queues_managers = {}
        tenant = self.pipeline.tenant
        layout_project_configs = layout.project_configs

        for project_name, project_configs in layout_project_configs.items():
            (trusted, project) = tenant.getProject(project_name)
            project_queue_name = None
            pipeline_queue_name = None
            project_in_pipeline = False
            for project_config in layout.getAllProjectConfigs(project_name):
                project_pipeline_config = project_config.pipelines.get(
                    self.pipeline.name)
                if not project_queue_name:
                    project_queue_name = project_config.queue_name
                if project_pipeline_config is None:
                    continue
                project_in_pipeline = True
                # TODO(tobiash): Remove pipeline_queue_name after deprecation
                if not pipeline_queue_name:
                    pipeline_queue_name = project_pipeline_config.queue_name
            if not project_in_pipeline:
                continue

            # Note: we currently support queue name per pipeline and per
            # project while project has precedence.
            queue_name = project_queue_name or pipeline_queue_name

            # Check if the queue is global or per branch
            queue = layout.queues.get(queue_name)
            per_branch = queue and queue.per_branch

            if queue_name and queue_name in change_queues_managers:
                change_queue_manager = change_queues_managers[queue_name]
            else:
                change_queue_manager = ChangeQueueManager(
                    self, name=queue_name, per_branch=per_branch)
                if queue_name:
                    # If this is a named queue, keep track of it in
                    # case it is referenced again.  Otherwise, it will
                    # have a name automatically generated from its
                    # constituent projects.
                    change_queues_managers[queue_name] = change_queue_manager
                self.change_queue_managers.append(change_queue_manager)
                self.log.debug("Created queue: %s" % change_queue_manager)
            change_queue_manager.addProject(project)
            self.log.debug("Added project %s to queue managers: %s" %
                           (project, change_queue_manager))

    def getChangeQueue(self, change, event, existing=None):
        log = get_annotated_logger(self.log, event)

        # Ignore the existing queue, since we can always get the correct queue
        # from the pipeline. This avoids enqueuing changes in a wrong queue
        # e.g. during re-configuration.
        queue = self.pipeline.getQueue(change.project.canonical_name,
                                       change.branch)
        if queue:
            return StaticChangeQueueContextManager(queue)
        else:
            # Change queues in the dependent pipeline manager are created
            # lazy so first check the managers for the project.
            matching_managers = [t for t in self.change_queue_managers
                                 if change.project in t.projects]
            if matching_managers:
                manager = matching_managers[0]
                branch = None
                if manager.per_branch:
                    # The change queue is not existing yet for this branch
                    branch = change.branch

                # We have a queue manager but no queue yet, so create it
                return StaticChangeQueueContextManager(
                    manager.getOrCreateQueue(change.project, branch)
                )

            # No specific per-branch queue matched so look again with no branch
            queue = self.pipeline.getQueue(change.project.canonical_name, None)
            if queue:
                return StaticChangeQueueContextManager(queue)

            # There is no existing queue for this change. Create a
            # dynamic one for this one change's use
            change_queue = model.ChangeQueue.new(
                self.pipeline.manager.current_context,
                pipeline=self.pipeline,
                dynamic=True)
            change_queue.addProject(change.project, None)
            self.pipeline.addQueue(change_queue)
            log.debug("Dynamically created queue %s", change_queue)
            return DynamicChangeQueueContextManager(change_queue)
