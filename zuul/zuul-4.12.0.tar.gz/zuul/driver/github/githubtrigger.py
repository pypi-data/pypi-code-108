# Copyright 2015 Hewlett-Packard Development Company, L.P.
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
from zuul.trigger import BaseTrigger
from zuul.driver.github.githubmodel import GithubEventFilter
from zuul.driver.util import scalar_or_list, to_list


class GithubTrigger(BaseTrigger):
    name = 'github'
    log = logging.getLogger("zuul.trigger.GithubTrigger")

    def __init__(self, driver, connection, config=None):

        # This is a compatibility layer to map the action 'requested' back
        # to the original action 'rerequested'.
        # TODO: Remove after zuul 5.0
        for item in config:
            if item.get('action') == 'requested':
                item['action'] = 'rerequested'

        super().__init__(driver, connection, config=config)

    def getEventFilters(self, connection_name, trigger_config):
        efilters = []
        for trigger in to_list(trigger_config):
            f = GithubEventFilter(
                connection_name=connection_name,
                trigger=self,
                types=to_list(trigger['event']),
                actions=to_list(trigger.get('action')),
                branches=to_list(trigger.get('branch')),
                refs=to_list(trigger.get('ref')),
                comments=to_list(trigger.get('comment')),
                check_runs=to_list(trigger.get('check')),
                labels=to_list(trigger.get('label')),
                unlabels=to_list(trigger.get('unlabel')),
                states=to_list(trigger.get('state')),
                statuses=to_list(trigger.get('status')),
                required_statuses=to_list(trigger.get('require-status'))
            )
            efilters.append(f)

        return efilters

    def onPullRequest(self, payload):
        pass


def getSchema():
    github_trigger = {
        v.Required('event'):
            scalar_or_list(v.Any('pull_request',
                                 'pull_request_review',
                                 'push',
                                 'check_run')),
        'action': scalar_or_list(str),
        'branch': scalar_or_list(str),
        'ref': scalar_or_list(str),
        'comment': scalar_or_list(str),
        'label': scalar_or_list(str),
        'unlabel': scalar_or_list(str),
        'state': scalar_or_list(str),
        'require-status': scalar_or_list(str),
        'status': scalar_or_list(str),
        'check': scalar_or_list(str),
    }

    return github_trigger
