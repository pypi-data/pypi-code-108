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
from zuul.manager.shared import SharedQueuePipelineManager


class SerialPipelineManager(SharedQueuePipelineManager):
    """PipelineManager with shared queues and a window of 1"""

    changes_merge = False
    type = 'serial'

    def constructChangeQueue(self, queue_name):
        return model.ChangeQueue.new(
            self.pipeline.manager.current_context,
            pipeline=self.pipeline,
            window=1,
            window_floor=1,
            window_increase_type='none',
            window_decrease_type='none',
            name=queue_name)

    def dequeueItem(self, item):
        super(SerialPipelineManager, self).dequeueItem(item)
        # If this was a dynamic queue from a speculative change,
        # remove the queue (if empty)
        if item.queue.dynamic:
            if not item.queue.queue:
                self.pipeline.removeQueue(item.queue)
