# Copyright 2019 Red Hat, Inc.
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
import voluptuous as v
from zuul.driver.gitlab.gitlabmodel import GitlabEventFilter
from zuul.trigger import BaseTrigger
from zuul.driver.util import scalar_or_list, to_list


class GitlabTrigger(BaseTrigger):
    name = 'gitlab'
    log = logging.getLogger("zuul.trigger.GitlabTrigger")

    def getEventFilters(self, connection_name, trigger_config):
        efilters = []
        for trigger in to_list(trigger_config):
            f = GitlabEventFilter(
                connection_name=connection_name,
                trigger=self,
                types=to_list(trigger['event']),
                actions=to_list(trigger.get('action')),
                comments=to_list(trigger.get('comment')),
                refs=to_list(trigger.get('ref')),
                labels=to_list(trigger.get('labels')),
            )
            efilters.append(f)
        return efilters

    def onPullRequest(self, payload):
        pass


def getSchema():
    gitlab_trigger = {
        v.Required('event'):
            scalar_or_list(
                v.Any(
                    'gl_merge_request',
                    'gl_push',
                )),
        'action': scalar_or_list(str),
        'comment': scalar_or_list(str),
        'ref': scalar_or_list(str),
        'labels': scalar_or_list(str)
    }
    return gitlab_trigger
