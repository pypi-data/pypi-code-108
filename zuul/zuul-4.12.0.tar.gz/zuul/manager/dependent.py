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

from zuul import model
from zuul.lib.logutil import get_annotated_logger
from zuul.manager.shared import SharedQueuePipelineManager


class DependentPipelineManager(SharedQueuePipelineManager):
    """PipelineManager for handling interrelated Changes.

    The DependentPipelineManager puts Changes that share a Pipeline
    into a shared :py:class:`~zuul.model.ChangeQueue`. It then processes them
    using the Optimistic Branch Prediction logic with Nearest Non-Failing Item
    reparenting algorithm for handling errors.
    """
    changes_merge = True
    type = 'dependent'

    def __init__(self, *args, **kwargs):
        super(DependentPipelineManager, self).__init__(*args, **kwargs)

    def constructChangeQueue(self, queue_name):
        p = self.pipeline
        return model.ChangeQueue.new(
            p.manager.current_context,
            pipeline=p,
            window=p.window,
            window_floor=p.window_floor,
            window_increase_type=p.window_increase_type,
            window_increase_factor=p.window_increase_factor,
            window_decrease_type=p.window_decrease_type,
            window_decrease_factor=p.window_decrease_factor,
            name=queue_name)

    def getNodePriority(self, item):
        with self.getChangeQueue(item.change, item.event) as change_queue:
            items = change_queue.queue
            return items.index(item)

    def isChangeReadyToBeEnqueued(self, change, event):
        log = get_annotated_logger(self.log, event)
        source = change.project.source
        if not source.canMerge(change, self.getSubmitAllowNeeds(),
                               event=event):
            log.debug("Change %s can not merge", change)
            return False
        return True

    def canMergeCycle(self, bundle):
        """Check if the cycle still fulfills the pipeline's ready criteria."""
        for item in bundle.items:
            source = item.change.project.source
            if not source.canMerge(
                item.change,
                self.getSubmitAllowNeeds(),
                event=item.event,
                allow_refresh=True,
            ):
                log = get_annotated_logger(self.log, item.event)
                log.debug("Change %s can no longer be merged", item.change)
                return False
        return True

    def enqueueChangesBehind(self, change, event, quiet, ignore_requirements,
                             change_queue, history=None,
                             dependency_graph=None):
        log = get_annotated_logger(self.log, event)
        history = history if history is not None else []

        log.debug("Checking for changes needing %s:" % change)
        if not hasattr(change, 'needed_by_changes'):
            log.debug("  %s does not support dependencies" % type(change))
            return

        # for project in change_queue, project.source get changes, then dedup.
        projects = [self.pipeline.tenant.getProject(pcn)[1] for pcn, _ in
                    change_queue.project_branches]
        sources = {p.source for p in projects}

        needed_by_changes = self.resolveChangeReferences(
            change.needed_by_changes)
        seen = set(needed_by_changes)
        for source in sources:
            log.debug("  Checking source: %s", source)
            for c in source.getChangesDependingOn(change,
                                                  projects,
                                                  self.pipeline.tenant):
                if c not in seen:
                    seen.add(c)
                    needed_by_changes.append(c)

        log.debug("  Following changes: %s", needed_by_changes)

        to_enqueue = []
        change_dependencies = dependency_graph.get(change, [])
        for other_change in needed_by_changes:
            if other_change in change_dependencies:
                # Only consider the change if it is not part of a cycle, as
                # cycle changes will otherwise be partially enqueued without
                # any error handling
                self.log.debug(
                    "    Skipping change %s due to dependency cycle"
                )
                continue

            with self.getChangeQueue(other_change,
                                     event) as other_change_queue:
                if other_change_queue != change_queue:
                    log.debug("  Change %s in project %s can not be "
                              "enqueued in the target queue %s" %
                              (other_change, other_change.project,
                               change_queue))
                    continue
            source = other_change.project.source
            if source.canMerge(other_change, self.getSubmitAllowNeeds(),
                               event=event):
                log.debug("  Change %s needs %s and is ready to merge",
                          other_change, change)
                to_enqueue.append(other_change)

        if not to_enqueue:
            log.debug("  No changes need %s" % change)

        for other_change in to_enqueue:
            self.addChange(other_change, event, quiet=quiet,
                           ignore_requirements=ignore_requirements,
                           change_queue=change_queue, history=history,
                           dependency_graph=dependency_graph)

    def enqueueChangesAhead(self, change, event, quiet, ignore_requirements,
                            change_queue, history=None, dependency_graph=None):
        log = get_annotated_logger(self.log, event)

        history = history if history is not None else []
        if hasattr(change, 'number'):
            history.append(change)
        else:
            # Don't enqueue dependencies ahead of a non-change ref.
            return True

        ret = self.checkForChangesNeededBy(change, change_queue, event,
                                           dependency_graph=dependency_graph)
        if ret in [True, False]:
            return ret
        log.debug("  Changes %s must be merged ahead of %s", ret, change)
        for needed_change in ret:
            # If the change is already in the history, but the change also has
            # a git level dependency, we need to enqueue it before the current
            # change.
            if (needed_change not in history or
                    needed_change.cache_key in change.git_needs_changes):
                r = self.addChange(needed_change, event, quiet=quiet,
                                   ignore_requirements=ignore_requirements,
                                   change_queue=change_queue, history=history,
                                   dependency_graph=dependency_graph)
                if not r:
                    return False
        return True

    def checkForChangesNeededBy(self, change, change_queue, event,
                                dependency_graph=None):
        log = get_annotated_logger(self.log, event)

        # Return true if okay to proceed enqueing this change,
        # false if the change should not be enqueued.
        log.debug("Checking for changes needed by %s:" % change)
        if not hasattr(change, 'needs_changes'):
            log.debug("  %s does not support dependencies", type(change))
            return True
        if not change.needs_changes:
            log.debug("  No changes needed")
            return True
        changes_needed = []
        # Ignore supplied change_queue
        with self.getChangeQueue(change, event) as change_queue:
            for needed_change in self.resolveChangeReferences(
                    change.needs_changes):
                log.debug("  Change %s needs change %s:" % (
                    change, needed_change))
                if needed_change.is_merged:
                    log.debug("  Needed change is merged")
                    continue

                if dependency_graph is not None:
                    log.debug("  Adding change %s to dependency graph for "
                              "change %s", needed_change, change)
                    node = dependency_graph.setdefault(change, [])
                    node.append(needed_change)

                with self.getChangeQueue(needed_change,
                                         event) as needed_change_queue:
                    if needed_change_queue != change_queue:
                        log.debug("  Change %s in project %s does not "
                                  "share a change queue with %s "
                                  "in project %s",
                                  needed_change, needed_change.project,
                                  change, change.project)
                        return False
                if not needed_change.is_current_patchset:
                    log.debug("  Needed change is not the current patchset")
                    return False
                if self.isChangeAlreadyInQueue(needed_change, change_queue):
                    log.debug("  Needed change is already ahead in the queue")
                    continue
                if needed_change.project.source.canMerge(
                        needed_change, self.getSubmitAllowNeeds(),
                        event=event):
                    log.debug("  Change %s is needed", needed_change)
                    if needed_change not in changes_needed:
                        changes_needed.append(needed_change)
                        continue
                # The needed change can't be merged.
                log.debug("  Change %s is needed but can not be merged",
                          needed_change)
                return False
        if changes_needed:
            return changes_needed
        return True

    def getFailingDependentItems(self, item):
        if not hasattr(item.change, 'needs_changes'):
            return None
        if not item.change.needs_changes:
            return None
        failing_items = set()
        for needed_change in self.resolveChangeReferences(
                item.change.needs_changes):
            needed_item = self.getItemForChange(needed_change)
            if not needed_item:
                continue
            if needed_item.current_build_set.failing_reasons:
                failing_items.add(needed_item)
        if item.isBundleFailing():
            failing_items.update(item.bundle.items)
            failing_items.remove(item)
        if failing_items:
            return failing_items
        return None

    def dequeueItem(self, item):
        super(DependentPipelineManager, self).dequeueItem(item)
        # If this was a dynamic queue from a speculative change,
        # remove the queue (if empty)
        if item.queue.dynamic:
            if not item.queue.queue:
                self.pipeline.removeQueue(item.queue)
