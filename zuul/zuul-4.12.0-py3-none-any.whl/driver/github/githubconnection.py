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

import collections
import concurrent.futures
import datetime
import logging
import hmac
import hashlib
import threading
import time
import json
from collections import OrderedDict, defaultdict
from collections.abc import Mapping
from itertools import chain
from json.decoder import JSONDecodeError
from typing import List, Optional

import cherrypy
import cachecontrol
from cachecontrol.cache import DictCache
from cachecontrol.heuristics import BaseHeuristic
import cachetools
import iso8601
import jwt
import requests
import github3
import github3.exceptions
import github3.pulls
from github3.session import AppInstallationTokenAuth

from zuul.connection import (
    BaseConnection, ZKChangeCacheMixin, ZKBranchCacheMixin
)
from zuul.driver.github.graphql import GraphQLClient
from zuul.web.handler import BaseWebController
from zuul.lib.logutil import get_annotated_logger
from zuul.model import Ref, Branch, Tag, Project
from zuul.exceptions import MergeFailure
from zuul.driver.github.githubmodel import PullRequest, GithubTriggerEvent
from zuul.model import DequeueEvent
from zuul.zk.branch_cache import BranchCache
from zuul.zk.change_cache import (
    AbstractChangeCache,
    ChangeKey,
    ConcurrentUpdateError,
)
from zuul.zk.event_queues import ConnectionEventQueue

GITHUB_BASE_URL = 'https://api.github.com'
PREVIEW_JSON_ACCEPT = 'application/vnd.github.machine-man-preview+json'
PREVIEW_DRAFT_ACCEPT = 'application/vnd.github.shadow-cat-preview+json'
PREVIEW_CHECKS_ACCEPT = 'application/vnd.github.antiope-preview+json'

# NOTE (felix): Using log levels for file comments / annotations is IMHO more
# convenient than the values Github expects. Having in mind that those comments
# most probably come from various linters, "info", "warning" and "error"
# should be more general terms than "notice", "warning" and "failure".
ANNOTATION_LEVELS = {
    "info": "notice",
    "warning": "warning",
    "error": "failure",
}

EventTuple = collections.namedtuple(
    "EventTuple", ["timestamp", "body", "event_type", "delivery"]
)


def _sign_request(body, secret):
    signature = 'sha1=' + hmac.new(
        secret.encode('utf-8'), body, hashlib.sha1).hexdigest()
    return signature


class UTC(datetime.tzinfo):
    """UTC"""

    def utcoffset(self, dt):
        return datetime.timedelta(0)

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return datetime.timedelta(0)


utc = UTC()


class GithubChangeCache(AbstractChangeCache):
    log = logging.getLogger("zuul.driver.GithubChangeCache")

    CHANGE_TYPE_MAP = {
        "Ref": Ref,
        "Tag": Tag,
        "Branch": Branch,
        "PullRequest": PullRequest,
    }


class GithubRequestLogger:

    def __init__(self, zuul_event_id):
        log = logging.getLogger("zuul.GithubRequest")
        self.log = get_annotated_logger(log, zuul_event_id)

    def log_request(self, response, *args, **kwargs):
        fields = OrderedDict()
        fields['result'] = response.status_code
        fields['size'] = len(response.content)
        fields['duration'] = int(response.elapsed.microseconds / 1000)
        if response.url.endswith('/graphql'):
            body = json.loads(response.request.body)
            for key, value in body.get('variables', {}).items():
                fields[key] = value
        info = ', '.join(['%s: %s' % (key, value)
                          for key, value in fields.items()])
        self.log.debug('%s %s %s',
                       response.request.method, response.url, info)


class GithubRateLimitHandler:
    """
    The GithubRateLimitHandler supplies the method handle_response that can be
    added to the requests session hooks. It will transparently catch API rate
    limit triggered 403 responses from github and retry the request after the
    wait time github tells us.
    """

    def __init__(self, github, log_rate_limit, zuul_event_id):
        log = logging.getLogger("zuul.GithubRateLimitHandler")
        self.log = get_annotated_logger(log, zuul_event_id)
        self.github = github
        self.rate_limit_logging_enabled = log_rate_limit

    def _log_rate_limit(self, response):
        if not self.rate_limit_logging_enabled:
            return

        rate_limit_remaining = response.headers.get('x-ratelimit-remaining')
        rate_limit_reset = response.headers.get('x-ratelimit-reset')

        # Determine rate limit resource from the path.
        path = response.request.path_url
        if path.startswith('/api/v3'):
            path = path[len('/api/v3'):]
        if path.startswith('/search/'):
            rate_limit_resource = 'search'
        else:
            rate_limit_resource = 'core'

        # Log the rate limits if enabled.
        if self.github._zuul_user_id:
            self.log.debug(
                'GitHub API rate limit (%s, %s) resource: %s, '
                'remaining: %s, reset: %s',
                self.github._zuul_project, self.github._zuul_user_id,
                rate_limit_resource, rate_limit_remaining, rate_limit_reset)
        else:
            self.log.debug(
                'GitHub API rate limit resource: %s, '
                'remaining: %s, reset: %s',
                rate_limit_resource, rate_limit_remaining, rate_limit_reset)

    def _handle_rate_limit(self, response):
        # We've hit the rate limit so calculate the time we need to wait based
        # on the x-ratelimit-reset header. After waiting we can retry the
        # original request and return it to the caller.
        reset = response.headers.get('x-ratelimit-reset')
        wait_time = int(reset) - int(time.time()) + 1
        self.log.warning('API rate limit reached, need to wait for '
                         '%s seconds', wait_time)
        time.sleep(wait_time)
        return self.github.session.send(response.request)

    def _handle_abuse(self, response):
        try:
            retry_after = int(response.headers.get('retry-after'))
        except Exception:
            # This should not happen but if it does we cannot handle it.
            # In this case the caller will need to handle the 403.
            self.log.error('Missing retry-after header while trying to handle '
                           'abuse error.')
            return response
        self.log.error('We triggered abuse detection, need to wait for '
                       '%s seconds', retry_after)
        time.sleep(retry_after + 1)
        return self.github.session.send(response.request)

    def handle_response(self, response, *args, **kwargs):

        rate_limit = response.headers.get('x-ratelimit-limit')

        if rate_limit:
            self._log_rate_limit(response)

        # If we got a 403 we could potentially have hit the rate limit. For
        # any other response we're finished here.
        if response.status_code != 403:
            return

        # Decode the body and check if we hit the rate limit.
        try:
            body = json.loads(response.content)
            message = body.get('message', '')

            # Catch rate limit and abuse detection responses. Every other 403
            # needs to be handled by the caller.
            if message.startswith('API rate limit exceeded'):
                return self._handle_rate_limit(response)
            elif message.startswith('You have triggered an abuse detection'):
                return self._handle_abuse(response)
        except Exception:
            # If we cannot decode the response body, log it here and return so
            # the caller can handle the response.
            self.log.exception("Couldn't json decode the response body.")


class GithubRetryHandler:
    """
    The GithubRetrHandler supplies the method handle_response that can be added
    to the requests session hooks. It will transparently handle 5xx errors on
    GET requests and retry them using an exponential backoff.
    """

    def __init__(self, github, retries, max_delay, zuul_event_id):
        log = logging.getLogger("zuul.GithubRetryHandler")
        self.log = get_annotated_logger(log, zuul_event_id)

        self.github = github
        self.max_retries = retries
        self.max_delay = max_delay
        self.initial_delay = 5

    def handle_response(self, response, *args, **kwargs):
        # Only handle GET requests that failed with 5xx. Retrying other request
        # types like POST can be dangerous because we cannot know if they
        # already might have altered the state on the server side.
        if response.request.method != 'GET':
            return
        if not 500 <= response.status_code < 600:
            return

        try:
            data = response.json()
            errors = data.get('errors', [])
            for error in errors:
                resource = error.get('resource')
                field = error.get('field')
                code = error.get('code')
                if (resource == 'PullRequest' and
                        field == 'diff' and
                        code == 'not_available'):
                    # Github responds with 500 if the diff is too large so we
                    # need to ignore it because retries won't help.
                    return
        except JSONDecodeError:
            # If there is no json just continue with retry handling.
            pass

        if hasattr(response.request, 'zuul_retry_count'):
            retry_count = response.request.zuul_retry_count
            retry_delay = min(response.request.zuul_retry_delay * 2,
                              self.max_delay)
        else:
            retry_count = 0
            retry_delay = self.initial_delay

        if retry_count >= self.max_retries:
            # We've reached the max retries so let the caller handle thr 503.
            self.log.error('GET Request failed with %s (%s/%s retries), '
                           'won\'t retry again.', response.status_code,
                           retry_count, self.max_retries)
            return

        self.log.warning('GET Request failed with %s (%s/%s retries), '
                         'retrying in %s seconds', response.status_code,
                         retry_count, self.max_retries, retry_delay)
        time.sleep(retry_delay)

        # Store retry information in the request object and perform the retry.
        retry_count += 1
        response.request.zuul_retry_count = retry_count
        response.request.zuul_retry_delay = retry_delay
        return self.github.session.send(response.request)


class GithubShaCache(object):
    def __init__(self):
        self.projects = {}

    def update(self, project_name, pr):
        project_cache = self.projects.setdefault(
            project_name,
            # Cache up to 4k shas for each project
            # Note we cache the actual sha for a PR and the
            # merge_commit_sha so we make this fairly large.
            cachetools.LRUCache(4096)
        )
        sha = pr['head']['sha']
        number = pr['number']
        cached_prs = project_cache.setdefault(sha, set())
        cached_prs.add(number)
        merge_commit_sha = pr.get('merge_commit_sha')
        if merge_commit_sha:
            cached_prs = project_cache.setdefault(merge_commit_sha, set())
            cached_prs.add(number)

    def get(self, project_name, sha):
        project_cache = self.projects.get(project_name, {})
        cached_prs = project_cache.get(sha, set())
        return cached_prs


class GithubEventProcessor(object):
    def __init__(self, connector, event_tuple, connection_event):
        self.connector = connector
        self.connection = connector.connection
        self.ts, self.body, self.event_type, self.delivery = event_tuple
        logger = logging.getLogger("zuul.GithubEventProcessor")
        self.zuul_event_id = self.delivery
        self.log = get_annotated_logger(logger, self.zuul_event_id)
        self.connection_event = connection_event
        self.event = None

    def run(self):
        self.log.debug("Starting event processing")
        try:
            self._process_event()
        except Exception:
            self.log.exception("Exception when processing event:")
        finally:
            self.log.debug("Finished event processing")
        return self.event, self.connection_event

    def _process_event(self):
        if self.connector._stopped:
            return

        # If there's any installation mapping information in the body then
        # update the project mapping before any requests are made.
        installation_id = self.body.get('installation', {}).get('id')
        project_name = self.body.get('repository', {}).get('full_name')

        if installation_id and project_name:
            installation_map = \
                self.connection._github_client_manager.installation_map
            old_id = installation_map.get(project_name)

            if old_id and old_id != installation_id:
                msg = "Unexpected installation_id change for %s. %d -> %d."
                self.log.warning(msg, project_name, old_id, installation_id)

            installation_map[project_name] = installation_id

        try:
            method = getattr(self, '_event_' + self.event_type)
        except AttributeError:
            # TODO(jlk): Gracefully handle event types we don't care about
            # instead of logging an exception.
            message = "Unhandled X-Github-Event: {0}".format(self.event_type)
            self.log.debug(message)
            # Returns empty on unhandled events
            return

        self.log.debug("Handling %s event", self.event_type)
        event = None
        try:
            event = method()
        except Exception:
            # NOTE(pabelanger): We should report back to the PR we could
            # not process the event, to give the user a chance to
            # retrigger.
            self.log.exception('Exception when handling event:')

        if event:

            # Note we limit parallel requests per installation id to avoid
            # triggering abuse detection.
            with self.connection.get_request_lock(installation_id):
                event.delivery = self.delivery
                event.zuul_event_id = self.delivery
                event.timestamp = self.ts
                project = self.connection.source.getProject(event.project_name)
                change = None
                if event.change_number:
                    change = self.connection._getChange(
                        project,
                        event.change_number,
                        event.patch_number,
                        refresh=True,
                        event=event)
                    self.log.debug("Refreshed change %s,%s",
                                   event.change_number, event.patch_number)

                # If this event references a branch and we're excluding
                # unprotected branches, we might need to check whether the
                # branch is now protected.
                if hasattr(event, "branch") and event.branch:
                    protected = None
                    if change:
                        # PR based events already have the information if the
                        # target branch is protected so take the information
                        # from there.
                        protected = change.branch_protected
                    self.connection.checkBranchCache(project.name, event,
                                                     protected=protected)

            event.project_hostname = self.connection.canonical_hostname
            self.event = event

    def _event_push(self):
        base_repo = self.body.get('repository')

        event = GithubTriggerEvent()
        event.connection_name = self.connection.connection_name
        event.trigger_name = 'github'
        event.project_name = base_repo.get('full_name')
        event.type = 'push'

        event.ref = self.body.get('ref')
        event.oldrev = self.body.get('before')
        event.newrev = self.body.get('after')
        event.commits = self.body.get('commits')

        ref_parts = event.ref.split('/', 2)  # ie, ['refs', 'heads', 'foo/bar']

        if ref_parts[1] == "heads":
            # necessary for the scheduler to match against particular branches
            event.branch = ref_parts[2]

        self.connection.clearConnectionCacheOnBranchEvent(event)

        return event

    def _event_pull_request(self):
        action = self.body.get('action')
        pr_body = self.body.get('pull_request')

        event = self._pull_request_to_event(pr_body)
        event.account = self._get_sender(self.body)

        event.type = 'pull_request'
        if action == 'opened':
            event.action = 'opened'
        elif action == 'synchronize':
            event.action = 'changed'
        elif action == 'closed':
            event.action = 'closed'
        elif action == 'reopened':
            event.action = 'reopened'
        elif action == 'labeled':
            event.action = 'labeled'
            event.label = self.body['label']['name']
        elif action == 'unlabeled':
            event.action = 'unlabeled'
            event.label = self.body['label']['name']
        elif action == 'edited':
            event.action = 'edited'
            if 'body' in self.body.get('changes', {}):
                event.body_edited = True
        else:
            return None

        return event

    def _event_issue_comment(self):
        """Handles pull request comments"""
        action = self.body.get('action')
        if action != 'created':
            return
        if not self.body.get('issue', {}).get('pull_request'):
            # Do not process non-PR issue comment
            return
        pr_body = self._issue_to_pull_request(self.body)
        if pr_body is None:
            return

        event = self._pull_request_to_event(pr_body)
        event.account = self._get_sender(self.body)
        event.comment = self.body.get('comment').get('body')
        event.type = 'pull_request'
        event.action = 'comment'
        return event

    def _event_pull_request_review(self):
        """Handles pull request reviews"""
        pr_body = self.body.get('pull_request')
        if pr_body is None:
            return

        review = self.body.get('review')
        if review is None:
            return

        event = self._pull_request_to_event(pr_body)
        event.state = review.get('state')
        event.account = self._get_sender(self.body)
        event.type = 'pull_request_review'
        event.action = self.body.get('action')
        return event

    def _event_status(self):
        action = self.body.get('action')
        if action == 'pending':
            return
        project = self.body.get('name')
        pr_body = self.connection.getPullBySha(
            self.body['sha'], project, self.zuul_event_id)
        if pr_body is None:
            return

        event = self._pull_request_to_event(pr_body)
        event.account = self._get_sender(self.body)
        event.type = 'pull_request'
        event.action = 'status'
        # Github API is silly. Webhook blob sets author data in
        # 'sender', but API call to get status puts it in 'creator'.
        # Duplicate the data so our code can look in one place
        self.body['creator'] = self.body['sender']
        event.status = "%s:%s:%s" % _status_as_tuple(self.body)
        return event

    def _event_check_run(self):
        """Handles check_run requests.

        This maps to the "Re-run" action on a check run and the "Re-run failed
        checks" on a check suite in Github.

        This event should be handled similar to a PR commnent or a push.
        """
        action = self.body.get("action")

        # NOTE (felix): We could also handle "requested" events here, which are
        # sent by Github whenever a change is pushed. But as we are already
        # listening to push events, this would result in two trigger events
        # for the same Github event.
        if action not in ["rerequested", "completed", "requested_action"]:
            return

        # The head_sha identifies the commit the check_run is requested for
        # (similar to Github's status API).
        check_run = self.body.get("check_run")
        if not check_run:
            # This shouldn't happen but in case something went wrong it should
            # also not cause an exception in the event handling
            return

        project = self.body.get("repository", {}).get("full_name")
        head_sha = check_run.get("head_sha")

        # Zuul will only accept Github changes that are part of a PR, thus we
        # must look up the PR first.
        pr_body = self.connection.getPullBySha(
            head_sha, project, self.zuul_event_id)
        if pr_body is None:
            self.log.debug(
                "Could not find appropriate PR for SHA %s. "
                "Skipping check_run event",
                head_sha
            )
            return

        # In case a "requested_action" event was triggered, we must first
        # evaluate the contained action (identifier), to build the right
        # event that will e.g. abort/dequeue a buildset.
        if action == "requested_action":
            # Look up the action's identifier from the payload
            identifier = self.body.get("requested_action", {}).get(
                "identifier"
            )

            # currently we only support "abort" identifier
            if identifier != "abort":
                return

            # In case of an abort (which is currently the only supported
            # action), we will build a dequeue event and return this rather
            # than a trigger event.
            return self._check_run_action_to_event(check_run, project)

        # If no requested_action was supplied, we build a trigger event for the
        # check run request
        event = self._pull_request_to_event(pr_body)
        event.type = "check_run"

        event.action = action

        check_run_tuple = "%s:%s:%s" % _check_as_tuple(check_run)
        event.check_run = check_run_tuple
        return event

    def _check_run_action_to_event(self, check_run, project):
        # Extract necessary values from the check's external id to dequeue
        # the corresponding change in Zuul
        dequeue_attrs = json.loads(check_run["external_id"])
        # The dequeue operations needs the change in format
        # <pr_number>,<commit_sha>
        change = "{},{}".format(dequeue_attrs["change"], check_run["head_sha"])

        # Instead of a trigger event, we directly dequeue the change by calling
        # the appropriate method on the scheduler.
        event = DequeueEvent(
            dequeue_attrs["tenant"],
            dequeue_attrs["pipeline"],
            self.connection.canonical_hostname,
            project,
            change,
            ref=None
        )
        return event

    def _issue_to_pull_request(self, body):
        number = body.get('issue').get('number')
        project_name = body.get('repository').get('full_name')
        pr_body, pr_obj = self.connection.getPull(
            project_name, number, self.zuul_event_id)
        if pr_body is None:
            self.log.debug('Pull request #%s not found in project %s' %
                           (number, project_name))
        return pr_body

    def _pull_request_to_event(self, pr_body):
        event = GithubTriggerEvent()
        event.connection_name = self.connection.connection_name
        event.trigger_name = 'github'

        base = pr_body.get('base')
        base_repo = base.get('repo')
        head = pr_body.get('head')

        event.project_name = base_repo.get('full_name')
        event.change_number = pr_body.get('number')
        event.change_url = self.connection.getPullUrl(event.project_name,
                                                      event.change_number)
        event.updated_at = pr_body.get('updated_at')
        event.branch = base.get('ref')
        event.ref = "refs/pull/" + str(pr_body.get('number')) + "/head"
        event.patch_number = head.get('sha')

        event.title = pr_body.get('title')

        return event

    def _get_sender(self, body):
        return body.get('sender').get('login')


class GithubEventConnector:
    """Move events from GitHub into the scheduler"""

    log = logging.getLogger("zuul.GithubEventConnector")

    def __init__(self, connection):
        self.connection = connection
        self.event_queue = connection.event_queue
        self._stopped = False
        self._events_in_progress = set()
        self._dispatcher_wake_event = threading.Event()
        self._event_dispatcher = threading.Thread(
            name='GithubEventDispatcher', target=self.run_event_dispatcher,
            daemon=True)
        self._thread_pool = concurrent.futures.ThreadPoolExecutor()
        self._event_forward_queue = collections.deque()

    def stop(self):
        self._stopped = True
        self._dispatcher_wake_event.set()
        self.event_queue.election.cancel()
        self._event_dispatcher.join()

        self._thread_pool.shutdown()

    def start(self):
        self._event_dispatcher.start()

    def _onNewEvent(self):
        self._dispatcher_wake_event.set()
        # Stop the data watch in case the connector was stopped
        return not self._stopped

    def run_event_dispatcher(self):
        # Wait for the scheduler to prime its config so that we have
        # the full tenant list before we start moving events.
        self.connection.sched.primed_event.wait()
        if self._stopped:
            return
        self.event_queue.registerEventWatch(self._onNewEvent)
        # Set the wake event so we get an initial run
        self._dispatcher_wake_event.set()
        while not self._stopped:
            try:
                self.event_queue.election.run(self._dispatchEventsMain)
            except Exception:
                self.log.exception("Exception handling GitHub event:")
            # In case we caught an exception with events in progress,
            # reset these in case we run the loop again.
            self._events_in_progress = set()
            self._event_forward_queue = collections.deque()

    def _dispatchEventsMain(self):
        while True:
            # We can start processing events as long as we're running;
            # if we are stopping, then we need to continue this loop
            # until previously processed events are completed but not
            # start processing any new events.
            if self._dispatcher_wake_event.is_set() and not self._stopped:
                self._dispatcher_wake_event.clear()
                self._dispatchEvents()

            # Now process the futures from this or any previous
            # iterations of the loop.
            if len(self._event_forward_queue):
                self._forwardEvents()

            # If there are no futures, we can sleep until there are
            # new events (or stop altogether); otherwise we need to
            # continue processing futures.
            if not len(self._event_forward_queue):
                if self._stopped:
                    return
                self._dispatcher_wake_event.wait(10)
            else:
                # Sleep a small amount of time to give the futures
                # time to complete.
                self._dispatcher_wake_event.wait(0.1)

    def _dispatchEvents(self):
        # This is the first half of the event dispatcher.  It reads
        # events from the webhook event queue and passes them to a
        # concurrent executor for pre-processing.
        for event in self.event_queue:
            if self._stopped:
                break
            if event.ack_ref in self._events_in_progress:
                continue
            etuple = self._eventAsTuple(event)
            log = get_annotated_logger(self.log, etuple.delivery)
            log.debug("Github Webhook Received")
            log.debug("X-Github-Event: %s", etuple.event_type)
            processor = GithubEventProcessor(self, etuple, event)
            future = self._thread_pool.submit(processor.run)

            # Events are acknowledged in the event forwarder loop after
            # pre-processing. This way we can ensure that no events are
            # lost.
            self._events_in_progress.add(event.ack_ref)
            self._event_forward_queue.append(future)

    def _forwardEvents(self):
        # This is the second half of the event dispatcher.  It
        # collects pre-processed events from the concurrent executor
        # and forwards them to the scheduler queues.
        while True:
            try:
                if not len(self._event_forward_queue):
                    return
                # Peek at the next event and see if it's done or if we
                # need to wait for the next loop iteration.
                if not self._event_forward_queue[0].done():
                    return
                future = self._event_forward_queue.popleft()
                event, connection_event = future.result()
                try:
                    if not event:
                        continue
                    self.connection.logEvent(event)
                    if isinstance(event, DequeueEvent):
                        self.connection.sched.addChangeManagementEvent(event)
                    else:
                        self.connection.sched.addTriggerEvent(
                            self.connection.driver_name, event
                        )
                finally:
                    # Ack event in Zookeeper
                    self.event_queue.ack(connection_event)
                    self._events_in_progress.remove(connection_event.ack_ref)
            except Exception:
                self.log.exception("Exception moving GitHub event:")

    @staticmethod
    def _eventAsTuple(event):
        body = event.get("body")
        headers = event.get("headers", {})
        event_type = headers.get('x-github-event')
        delivery = headers.get('x-github-delivery')
        return EventTuple(time.time(), body, event_type, delivery)


class GithubUser(Mapping):
    log = logging.getLogger('zuul.GithubUser')

    def __init__(self, username, connection, project_name):
        self._connection = connection
        self._username = username
        self._data = None
        self._project_name = project_name

    def __getitem__(self, key):
        self._init_data()
        return self._data[key]

    def __iter__(self):
        self._init_data()
        return iter(self._data)

    def __len__(self):
        self._init_data()
        return len(self._data)

    def _init_data(self):
        if self._data is None:
            github = self._connection.getGithubClient(self._project_name)
            user = github.user(self._username)
            self.log.debug("Initialized data for user %s", self._username)
            self._data = {
                'username': user.login,
                'name': user.name,
                'email': user.email,
                'html_url': user.html_url,
            }


class GithubClientManager:
    log = logging.getLogger('zuul.GithubConnection.GithubClientManager')
    github_class = github3.GitHub
    github_enterprise_class = github3.GitHubEnterprise

    def __init__(self, connection_config):
        self.connection_config = connection_config
        self.server = self.connection_config.get('server', 'github.com')

        if self.server == 'github.com':
            self.api_base_url = GITHUB_BASE_URL
            self.base_url = GITHUB_BASE_URL
        else:
            self.api_base_url = 'https://%s/api' % self.server
            self.base_url = 'https://%s/api/v3' % self.server

        # ssl verification must default to true
        verify_ssl = self.connection_config.get('verify_ssl', 'true')
        self.verify_ssl = True
        if verify_ssl.lower() == 'false':
            self.verify_ssl = False

        # NOTE(jamielennox): Better here would be to cache to memcache or file
        # or something external - but zuul already sucks at restarting so in
        # memory probably doesn't make this much worse.

        # NOTE(tobiash): Unlike documented cachecontrol doesn't priorize
        # the etag caching but doesn't even re-request until max-age was
        # elapsed.
        #
        # Thus we need to add a custom caching heuristic which simply drops
        # the cache-control header containing max-age. This way we force
        # cachecontrol to only rely on the etag headers.
        #
        # http://cachecontrol.readthedocs.io/en/latest/etags.html
        # http://cachecontrol.readthedocs.io/en/latest/custom_heuristics.html
        class NoAgeHeuristic(BaseHeuristic):
            def update_headers(self, response):
                if 'cache-control' in response.headers:
                    del response.headers['cache-control']

        self.cache_adapter = cachecontrol.CacheControlAdapter(
            DictCache(),
            cache_etags=True,
            heuristic=NoAgeHeuristic())

        # Logging of rate limit is optional as this does additional requests
        rate_limit_logging = self.connection_config.get(
            'rate_limit_logging', 'true')
        self._log_rate_limit = True
        if rate_limit_logging.lower() == 'false':
            self._log_rate_limit = False

        self.app_id = None
        self.app_key = None
        self._initialized = False

        self._installation_map_lock = threading.Lock()
        self.installation_map = {}
        self.installation_token_cache = {}

        # The version of github enterprise stays None for github.com
        self._github_version = None

    def initialize(self):
        self.log.info('Authing to GitHub')
        self._authenticateGithubAPI()
        self._prime_installation_map()
        self._initialized = True

    @property
    def initialized(self):
        return self._initialized

    @property
    def usesAppAuthentication(self):
        return True if self.app_id else False

    def _authenticateGithubAPI(self):
        config = self.connection_config

        app_id = config.get('app_id')
        app_key = None
        app_key_file = config.get('app_key')

        if app_key_file:
            try:
                with open(app_key_file, 'r') as f:
                    app_key = f.read()
            except IOError:
                m = "Failed to open app key file for reading: %s"
                self.log.error(m, app_key_file)

        if (app_id or app_key) and \
                not (app_id and app_key):
            self.log.warning("You must provide an app_id and "
                             "app_key to use installation based "
                             "authentication")
            return

        if app_id:
            self.app_id = int(app_id)
        if app_key:
            self.app_key = app_key

    def _createGithubClient(self, zuul_event_id=None):
        session = github3.session.GitHubSession(default_read_timeout=300)

        if self.server != 'github.com':
            url = 'https://%s/' % self.server
            if not self.verify_ssl:
                # disabling ssl verification is evil so emit a warning
                self.log.warning("SSL verification disabled for "
                                 "GitHub Enterprise")
            github = self.github_enterprise_class(
                url, session=session, verify=self.verify_ssl)
            if not self._github_version:
                version = github.meta().get('installed_version')
                self._github_version = tuple(
                    [int(v) for v in version.split('.', 2)])
        else:
            github = self.github_class(session=session)

        # Attach a version number to the github client so we can support per
        # version features.
        github.version = self._github_version

        # anything going through requests to http/s goes through cache
        github.session.mount('http://', self.cache_adapter)
        github.session.mount('https://', self.cache_adapter)

        # Log all requests with attached event id
        request_logger = GithubRequestLogger(zuul_event_id)
        github.session.hooks['response'].append(request_logger.log_request)

        # Install hook for handling rate limit errors transparently
        rate_limit_handler = GithubRateLimitHandler(
            github, self._log_rate_limit, zuul_event_id)
        github.session.hooks['response'].append(
            rate_limit_handler.handle_response)

        # Install hook for handling retries of GET requests transparently
        retry_handler = GithubRetryHandler(github, 5, 30, zuul_event_id)
        github.session.hooks['response'].append(retry_handler.handle_response)

        # Add properties to store project and user for logging later
        github._zuul_project = None
        github._zuul_user_id = None
        return github

    def _get_app_auth_headers(self):
        now = datetime.datetime.now(utc)
        expiry = now + datetime.timedelta(minutes=5)

        data = {'iat': now, 'exp': expiry, 'iss': self.app_id}
        app_token = jwt.encode(data,
                               self.app_key,
                               algorithm='RS256')

        headers = {'Accept': PREVIEW_JSON_ACCEPT,
                   'Authorization': 'Bearer %s' % app_token}

        return headers

    def get_installation_key(self, project_name, inst_id=None,
                             reprime=True):
        installation_id = inst_id
        if project_name is not None:
            installation_id = self.installation_map.get(project_name)

        if not installation_id:
            if reprime:
                # prime installation map and try again without refreshing
                self._prime_installation_map()
                return self.get_installation_key(project_name,
                                                 inst_id=inst_id,
                                                 reprime=False)

            self.log.error("No installation ID available for project %s",
                           project_name)
            return ''

        now = datetime.datetime.now(utc)
        token, expiry = self.installation_token_cache.get(installation_id,
                                                          (None, None))

        if ((not expiry) or (not token) or (now >= expiry)):
            headers = self._get_app_auth_headers()

            url = "%s/app/installations/%s/access_tokens" % (
                self.base_url, installation_id)

            github = self._createGithubClient()
            response = github.session.post(url, headers=headers, json=None)
            response.raise_for_status()

            data = response.json()

            expiry = iso8601.parse_date(data['expires_at'])
            expiry -= datetime.timedelta(minutes=5)
            token = data['token']

            self.installation_token_cache[installation_id] = (token, expiry)

        return token

    def _get_repos_of_installation(self, inst_id, headers):
        url = '%s/installation/repositories?per_page=100' % self.base_url
        project_names = []
        while url:
            self.log.debug("Fetching repos for install %s" % inst_id)
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            repos = response.json()

            for repo in repos.get('repositories'):
                project_name = repo.get('full_name')
                project_names.append(project_name)

            # check if we need to do further paged calls
            url = response.links.get('next', {}).get('url')
        return project_names

    def _prime_installation_map(self):
        """Walks each app install for the repos to prime install IDs"""

        if not self.app_id:
            return

        if self._installation_map_lock.acquire(blocking=False):
            try:
                url = '%s/app/installations' % self.base_url
                installations = []
                headers = self._get_app_auth_headers()
                page = 1
                while url:
                    self.log.debug("Fetching installations for GitHub app "
                                   "(page %s)" % page)
                    page += 1
                    response = requests.get(url, headers=headers)
                    response.raise_for_status()
                    for i in response.json():
                        # admins can hit "suspend app" which populates
                        # this in the app response.  A suspended app
                        # will just get back 400 "This installation
                        # has been suspended" responses.
                        if i.get('suspended_at'):
                            self.log.info("Skipping GitHub installation %s due"
                                          " to admin suspension (by %s @ %s)" %
                                          (i['id'], i['suspended_by']['login'],
                                           i['suspended_at']))
                        else:
                            installations.append(i)

                    # check if we need to do further paged calls
                    url = response.links.get(
                        'next', {}).get('url')

                headers_per_inst = {}
                with concurrent.futures.ThreadPoolExecutor() as executor:

                    token_by_inst = {}
                    for install in installations:
                        inst_id = install.get('id')
                        token_by_inst[inst_id] = executor.submit(
                            self.get_installation_key, project_name=None,
                            inst_id=inst_id)

                    for inst_id, result in token_by_inst.items():
                        token = result.result()
                        headers_per_inst[inst_id] = {
                            'Accept': PREVIEW_JSON_ACCEPT,
                            'Authorization': 'token %s' % token
                        }

                    project_names_by_inst = {}
                    for install in installations:
                        inst_id = install.get('id')
                        headers = headers_per_inst[inst_id]

                        project_names_by_inst[inst_id] = executor.submit(
                            self._get_repos_of_installation, inst_id, headers)

                    for inst_id, result in project_names_by_inst.items():
                        project_names = result.result()
                        for project_name in project_names:
                            self.installation_map[project_name] = inst_id
            finally:
                self._installation_map_lock.release()
        else:
            self.log.debug(
                'Already fetching installations, waiting to finish.')
            with self._installation_map_lock:
                self.log.debug('Finished waiting for fetching installations')

    def getGithubClientsForProjects(self, projects):
        # Get a list of projects with unique installation ids
        installation_ids = set()
        installation_projects = set()

        for project in projects:
            installation_id = self.installation_map.get(project.name)
            if installation_id not in installation_ids:
                installation_ids.add(installation_id)
                installation_projects.add(project.name)

        clients = [self.getGithubClient(project_name)
                   for project_name in installation_projects]
        return clients

    def getGithubClient(self,
                        project_name=None,
                        zuul_event_id=None):
        github = self._createGithubClient(zuul_event_id)

        # if you're authenticating for a project and you're an integration then
        # you need to use the installation specific token.
        if project_name and self.app_id:
            # Call get_installation_key to ensure the token gets refresehd in
            # case it's expired.
            token = self.get_installation_key(project_name)

            # Only set the auth header if we have a token. If not, just don't
            # set any auth header so we will be treated as anonymous. That's
            # also what the github.login() method would do if the token is not
            # set.
            if token:
                # To set the AppInstallationAuthToken on the github session, we
                # also need the expiry date, but in the correct ISO format.
                installation_id = self.installation_map.get(project_name)
                _, expiry = self.installation_token_cache.get(installation_id)
                format_expiry = datetime.datetime.strftime(
                    expiry, "%Y-%m-%dT%H:%M:%SZ"
                )

                # Usually one should use github.login_as_app_installation() to
                # authenticate as github app. This method will then request the
                # access token for the installation or refresh it if necessary
                # and set the correct class on the github.session.auth
                # attribute to be identified as github app. As we are already
                # managing the installation tokens by ourselves, we just have
                # to set the correct TokenAuth class on the github.session.auth
                # attribute.
                github.session.auth = AppInstallationTokenAuth(
                    token, format_expiry
                )

            github._zuul_project = project_name
            github._zuul_user_id = self.installation_map.get(project_name)

        # if we're using api_token authentication then use the provided token,
        # else anonymous is the best we have.
        else:
            api_token = self.connection_config.get('api_token')
            if api_token:
                github.login(token=api_token)

        return github


class GithubConnection(ZKChangeCacheMixin, ZKBranchCacheMixin, BaseConnection):
    driver_name = 'github'
    log = logging.getLogger("zuul.GithubConnection")
    payload_path = 'payload'
    client_manager_class = GithubClientManager
    _event_connector_class = GithubEventConnector

    def __init__(self, driver, connection_name, connection_config):
        super(GithubConnection, self).__init__(driver, connection_name,
                                               connection_config)
        self._change_update_lock = {}
        self.projects = {}
        self.git_ssh_key = self.connection_config.get('sshkey')
        self.server = self.connection_config.get('server', 'github.com')
        self.canonical_hostname = self.connection_config.get(
            'canonical_hostname', self.server)
        self.source = driver.getSource(self)
        self._sha_pr_cache = GithubShaCache()

        self._request_locks = {}
        self.max_threads_per_installation = int(self.connection_config.get(
            'max_threads_per_installation', 1))

        self._github_client_manager = self.client_manager_class(
            self.connection_config)

        self.sched = None

        self.graphql_client = GraphQLClient(
            '%s/graphql' % self._github_client_manager.api_base_url)

    def toDict(self):
        d = super().toDict()
        d.update({
            "baseurl": self._github_client_manager.base_url,
            "canonical_hostname": self.canonical_hostname,
            "server": self.server,
        })
        return d

    def onLoad(self, zk_client):
        self.log.info('Starting GitHub connection: %s', self.connection_name)
        self._github_client_manager.initialize()

        # Set the project branch cache to read only if no scheduler is
        # provided to prevent fetching the branches from the connection.
        self.read_only = not self.sched

        self.log.debug('Creating Zookeeper branch cache')
        self._branch_cache = BranchCache(zk_client, self)

        self.log.debug('Creating Zookeeper event queue')
        self.event_queue = ConnectionEventQueue(
            zk_client, self.connection_name
        )

        # If the connection was not loaded by a scheduler, but by e.g.
        # zuul-web, we want to stop here.
        if not self.sched:
            return

        self.log.debug('Creating Zookeeper change cache')
        self._change_cache = GithubChangeCache(zk_client, self)

        self.log.info('Starting event connector')
        self._start_event_connector()

    def onStop(self):
        # TODO(jeblair): remove this check which is here only so that
        # zuul-web can call connections.stop to shut down the sql
        # connection.
        if hasattr(self, 'github_event_connector'):
            self._stop_event_connector()

    def _start_event_connector(self):
        self.github_event_connector = self._event_connector_class(self)
        self.github_event_connector.start()

    def _stop_event_connector(self):
        if self.github_event_connector:
            self.github_event_connector.stop()

    @staticmethod
    def _append_accept_header(github, value):
        old_header = github.session.headers.get('Accept', None)
        if old_header:
            new_value = '%s,%s' % (old_header, value)
        else:
            new_value = value
        github.session.headers['Accept'] = new_value

    def get_request_lock(self, installation_id):
        return self._request_locks.setdefault(
            installation_id, threading.Semaphore(
                value=self.max_threads_per_installation))

    def getGithubClient(self,
                        project_name=None,
                        zuul_event_id=None):
        return self._github_client_manager.getGithubClient(
            project_name=project_name, zuul_event_id=zuul_event_id)

    def getChange(self, event, refresh=False):
        """Get the change representing an event."""

        project = self.source.getProject(event.project_name)
        if event.change_number:
            change = self._getChange(project, event.change_number,
                                     event.patch_number, refresh=refresh,
                                     event=event)
        else:
            if event.ref and event.ref.startswith('refs/tags/'):
                change = self._getTag(project, event)
            elif event.ref and event.ref.startswith('refs/heads/'):
                change = self._getBranch(project, event)
            else:
                change = self._getRef(project, event)
        return change

    def _getChange(self, project, number, patchset=None, refresh=False,
                   event=None):
        # Note(tobiash): We force the pull request number to int centrally here
        # because it can originate from different sources (github event, manual
        # enqueue event) where some might just parse the string and forward it.
        number = int(number)
        key = ChangeKey(self.connection_name, project.name,
                        'PullRequest', str(number),
                        str(patchset))
        change = self._change_cache.get(key)
        if change and not refresh:
            return change
        if not change:
            change = PullRequest(project.name)
            change.project = project
            change.number = number
            change.patchset = patchset

        # This can be called multi-threaded during github event
        # preprocessing. In order to avoid data races perform locking
        # by cached key. Try to acquire the lock non-blocking at first.
        # If the lock is already taken we're currently updating the very
        # same chnange right now and would likely get the same data again.
        lock = self._change_update_lock.setdefault(key, threading.Lock())
        if lock.acquire(blocking=False):
            try:
                pull = self.getPull(change.project.name, change.number,
                                    event=event)

                def _update_change(c):
                    self._updateChange(c, event, pull)

                change = self._change_cache.updateChangeWithRetry(
                    key, change, _update_change)
            finally:
                # We need to remove the lock here again so we don't leak
                # them.
                del self._change_update_lock[key]
                lock.release()
        else:
            # We didn't get the lock so we don't need to update the same
            # change again, but to be correct we should at least wait until
            # the other thread is done updating the change.
            log = get_annotated_logger(self.log, event)
            log.debug("Change %s is currently being updated, "
                      "waiting for it to finish", change)
            with lock:
                log.debug('Finished updating change %s', change)
        return change

    def _getTag(self, project, event):
        tag = event.ref[len('refs/tags/'):]
        key = ChangeKey(self.connection_name, project.name,
                        'Tag', tag, event.newrev)
        change = self._change_cache.get(key)
        if change:
            return change
        change = Tag(project)
        change.tag = tag
        change.ref = event.ref
        change.oldrev = event.oldrev
        change.newrev = event.newrev
        # Build the url pointing to this tag/release on GitHub.
        change.url = self.getGitwebUrl(project, sha=event.newrev, tag=tag)
        if hasattr(event, 'commits'):
            change.files = self.getPushedFileNames(event)
        try:
            self._change_cache.set(key, change)
        except ConcurrentUpdateError:
            change = self._change_cache.get(key)
        return change

    def _getBranch(self, project, event):
        branch = event.ref[len('refs/heads/'):]
        key = ChangeKey(self.connection_name, project.name,
                        'Branch', branch, event.newrev)
        change = self._change_cache.get(key)
        if change:
            return change
        change = Branch(project)
        change.branch = branch
        change.ref = event.ref
        change.oldrev = event.oldrev
        change.newrev = event.newrev
        change.url = self.getGitwebUrl(project, sha=event.newrev)
        if hasattr(event, 'commits'):
            change.files = self.getPushedFileNames(event)
        try:
            self._change_cache.set(key, change)
        except ConcurrentUpdateError:
            change = self._change_cache.get(key)
        return change

    def _getRef(self, project, event):
        key = ChangeKey(self.connection_name, project.name,
                        'Ref', event.ref, event.newrev)
        change = self._change_cache.get(key)
        if change:
            return change
        change = Ref(project)
        change.ref = event.ref
        change.oldrev = event.oldrev
        change.newrev = event.newrev
        change.url = self.getGitwebUrl(project, sha=event.newrev)
        if hasattr(event, 'commits'):
            change.files = self.getPushedFileNames(event)
        try:
            self._change_cache.set(key, change)
        except ConcurrentUpdateError:
            change = self._change_cache.get(key)
        return change

    def getChangesDependingOn(self, change, projects, tenant):
        changes = []
        if not change.uris:
            return changes

        if not projects:
            # We aren't in the context of a change queue and we just
            # need to query all installations of this tenant. This currently
            # only happens if certain features of the zuul trigger are
            # used; generally it should be avoided.
            projects = [p for p in tenant.all_projects
                        if p.connection_name == self.connection_name]
        # Otherwise we use the input projects list and look for changes in the
        # supplied projects.
        clients = self._github_client_manager.getGithubClientsForProjects(
            projects)

        keys = set()
        # TODO: Max of 5 OR operators can be used per query and
        # query can be max of 256 characters long
        # If making changes to this pattern you may need to update
        # tests/fakegithub.py
        pattern = ' OR '.join(['"Depends-On: %s"' % x for x in change.uris])
        query = '%s type:pr is:open in:body' % pattern
        # Repeat the search for each client (project)
        for github in clients:
            for issue in github.search_issues(query=query):
                pr = issue.issue.pull_request().as_dict()
                if not pr.get('url'):
                    continue
                # the issue provides no good description of the project :\
                org, proj, _, num = pr.get('url').split('/')[-4:]
                proj = pr.get('base').get('repo').get('full_name')
                sha = pr.get('head').get('sha')
                # This is not a ChangeKey
                key = (proj, num, sha)

                # A single tenant could have multiple projects with the same
                # name on different sources. Ensure we use the canonical name
                # to handle that case.
                s_project = self.source.getProject(proj)
                trusted, t_project = tenant.getProject(
                    s_project.canonical_name)
                # ignore projects zuul doesn't know about
                if not t_project:
                    continue

                if key in keys:
                    continue
                self.log.debug("Found PR %s/%s needs %s/%s" %
                               (proj, num, change.project.name,
                                change.number))
                keys.add(key)
            self.log.debug("Ran search issues: %s", query)

        for key in keys:
            (proj, num, sha) = key
            project = self.source.getProject(proj)
            change = self._getChange(project, int(num), patchset=sha)
            changes.append(change)

        return changes

    def _updateChange(self, change, event, pull):
        log = get_annotated_logger(self.log, event)
        log.info("Updating %s" % (change,))
        change.pr, pr_obj = pull
        change.is_current_patchset = (change.pr.get('head').get('sha') ==
                                      change.patchset)
        change.ref = "refs/pull/%s/head" % change.number
        change.branch = change.pr.get('base').get('ref')
        change.commit_id = change.pr.get('head').get('sha')
        change.owner = change.pr.get('user').get('login')
        # Don't overwrite the files list. The change object is bound to a
        # specific revision and thus the changed files won't change. This is
        # important if we got the files later because of the 300 files limit.
        if not change.files:
            change.files = change.pr.get('files')
            # Github's pull requests files API only returns at max
            # the first 300 changed files of a PR in alphabetical order.
            # https://developer.github.com/v3/pulls/#list-pull-requests-files
            if change.files is None:
                log.warning("Got no files of PR.")
            elif len(change.files) < change.pr.get('changed_files', 0):
                log.warning("Got only %s files but PR has %s files.",
                            len(change.files),
                            change.pr.get('changed_files', 0))
                # In this case explicitly set change.files to None to signalize
                # that we need to ask the mergers later in pipeline processing.
                # We cannot query the files here using the mergers because this
                # can slow down the github event queue considerably.
                change.files = None
        change.title = change.pr.get('title')
        change.open = change.pr.get('state') == 'open'

        # Never change the is_merged attribute back to unmerged. This is
        # crucial so this cannot race with mergePull wich sets this attribute
        # after a successful merge.
        if not change.is_merged:
            change.is_merged = change.pr.get('merged')

        change.reviews = self.getPullReviews(
            pr_obj, change.project, change.number, event)
        change.labels = change.pr.get('labels')
        # ensure message is at least an empty string
        message = change.pr.get("body") or ""
        if change.title:
            if message:
                message = "{}\n\n{}".format(change.title, message)
            else:
                message = change.title
        change.message = message
        change.body_text = change.pr.get("body_text")

        # Note(tobiash): The updated_at timestamp is a moving target that is
        # not bound to the pull request 'version' we can solve that by just not
        # updating the timestamp if the pull request is updated in the cache.
        # This way the old pull request object retains its old timestamp and
        # the update check works.
        if not change.updated_at:
            change.updated_at = int(time.mktime(self._ghTimestampToDate(
                change.pr.get('updated_at'))))

        # Note: Github returns different urls for the pr:
        #  - url: this is the url meant for api use
        #  - html_url: this is the url meant for use in browser (this is what
        #              change.url means)
        change.url = change.pr.get('html_url')
        change.uris = [
            'https://%s/%s/pull/%s' % (
                self.server, change.project.name, change.number),
        ]

        self._updateCanMergeInfo(change, event)

        return change

    def _updateCanMergeInfo(self, change, event):
        # NOTE: The 'mergeable' field may get a false (null) while GitHub is
        # calculating if it can merge. The Github API will just return
        # that as false. This could lead to false negatives. So don't get this
        # field here and only evaluate branch protection settings. Any merge
        # conflicts which would block merging finally will be detected by
        # the zuul-mergers anyway.
        github = self.getGithubClient(change.project.name, zuul_event_id=event)

        # Append accept headers so we get the draft status and checks api
        self._append_accept_header(github, PREVIEW_DRAFT_ACCEPT)
        self._append_accept_header(github, PREVIEW_CHECKS_ACCEPT)

        # For performance reasons fetch all needed data upfront using a
        # single graphql call.
        canmerge_data = self.graphql_client.fetch_canmerge(
            github, change, zuul_event_id=event)

        change.contexts = self._get_contexts(canmerge_data)
        change.draft = canmerge_data.get('isDraft', False)
        change.review_decision = canmerge_data['reviewDecision']
        change.required_contexts = set(
            canmerge_data['requiredStatusCheckContexts']
        )
        change.branch_protected = canmerge_data['protected']

    def getGitUrl(self, project: Project):
        if self.git_ssh_key:
            return 'ssh://git@%s/%s.git' % (self.server, project.name)

        # if app_id is configured but self.app_id is empty we are not
        # authenticated yet against github as app
        if not self._github_client_manager.initialized:
            self._github_client_manager.initialize()

        if self._github_client_manager.usesAppAuthentication:
            # We may be in the context of a merger or executor here. The
            # mergers and executors don't receive webhook events so they miss
            # new repository installations. In order to cope with this we need
            # to reprime the installation map if we don't find the repo there.
            installation_key = \
                self._github_client_manager.get_installation_key(
                    project.name, reprime=True)
            return 'https://x-access-token:%s@%s/%s' % (installation_key,
                                                        self.server,
                                                        project.name)

        return 'https://%s/%s' % (self.server, project.name)

    def getGitwebUrl(self, project, sha=None, tag=None):
        url = 'https://%s/%s' % (self.server, project)
        if tag is not None:
            url += '/releases/tag/%s' % tag
        elif sha is not None:
            url += '/commit/%s' % sha
        return url

    def getProject(self, name):
        return self.projects.get(name)

    def addProject(self, project):
        self.projects[project.name] = project

    def _fetchProjectBranches(self, project: Project,
                              exclude_unprotected: bool) -> List[str]:
        github = self.getGithubClient(project.name)
        url = github.session.build_url('repos', project.name,
                                       'branches')

        headers = {'Accept': 'application/vnd.github.loki-preview+json'}
        params = {'per_page': 100}
        if exclude_unprotected:
            params['protected'] = 1

        branches = []
        while url:
            resp = github.session.get(
                url, headers=headers, params=params)

            # check if we need to do further paged calls
            url = resp.links.get('next', {}).get('url')

            if resp.status_code == 403:
                self.log.error(str(resp))
                rate_limit = github.rate_limit()
                if rate_limit['resources']['core']['remaining'] == 0:
                    self.log.warning(
                        "Rate limit exceeded, using empty branch list")
                return []
            elif resp.status_code == 404:
                raise Exception("Got status code 404 when listing branches "
                                "of project %s" % project.name)

            branches.extend([x['name'] for x in resp.json()])

        return branches

    def isBranchProtected(self, project_name: str, branch_name: str,
                          zuul_event_id=None) -> Optional[bool]:
        github = self.getGithubClient(
            project_name, zuul_event_id=zuul_event_id)

        # Note that we directly use a web request here because if we use the
        # github3.py api directly we need a repository object which needs
        # an unneeded web request during creation.
        url = github.session.build_url('repos', project_name, 'branches',
                                       branch_name)

        resp = github.session.get(url)

        if resp.status_code == 404:
            return None

        return resp.json().get('protected')

    def getPullUrl(self, project, number):
        return '%s/pull/%s' % (self.getGitwebUrl(project), number)

    def getPull(self, project_name, number, event=None):
        log = get_annotated_logger(self.log, event)
        github = self.getGithubClient(project_name, zuul_event_id=event)
        owner, proj = project_name.split('/')
        for retry in range(5):
            try:
                probj = github.pull_request(owner, proj, number)
                if probj is not None:
                    break
                self.log.warning("Pull request #%s of %s/%s returned None!" % (
                                 number, owner, proj))
            except github3.exceptions.GitHubException:
                self.log.warning(
                    "Failed to get pull request #%s of %s/%s; retrying" %
                    (number, owner, proj))
            time.sleep(1)
        else:
            raise Exception("Failed to get pull request #%s of %s/%s" % (
                number, owner, proj))
        pr = probj.as_dict()
        try:
            if pr.get('changed_files', 0) > 999:
                # Don't request more than ten pages. If we exceed this we
                # need to determine the files via the mergers asynchronously
                # in order to not block the event processing by iterating on
                # too many pages.
                self.log.warning('Pull request #%s of %s/%s has too many '
                                 'files. Files will be requested '
                                 'asynchronously', number, owner, proj)
                pr['files'] = None
            else:
                pr['files'] = [f.filename for f in probj.files()]
        except github3.exceptions.ServerError as exc:
            # NOTE: For PRs with a lot of lines changed, Github will return
            # an error (HTTP 500) because it can't generate the diff.
            self.log.warning("Failed to get list of files from Github. "
                             "Using empty file list to trigger update "
                             "via the merger: %s", exc)
            pr['files'] = None

        labels = [l['name'] for l in pr['labels']]
        pr['labels'] = labels

        self._sha_pr_cache.update(project_name, pr)

        log.debug('Got PR %s#%s', project_name, number)
        return (pr, probj)

    def canMerge(self, change, allow_needs, event=None, allow_refresh=False):
        log = get_annotated_logger(self.log, event)

        if allow_refresh:
            self._updateCanMergeInfo(change, event)

        # If the PR is a draft it cannot be merged.
        if change.draft:
            log.debug('Change %s can not merge because it is a draft', change)
            return False

        missing_status_checks = self._getMissingStatusChecks(
            change, allow_needs)
        if missing_status_checks:
            log.debug('Change %s can not merge because required status checks '
                      'are missing: %s', change, missing_status_checks)
            return False

        if change.review_decision and change.review_decision != 'APPROVED':
            # If we got a review decision it must be approved
            log.debug('Change %s can not merge because it is not approved',
                      change)
            return False

        return True

    def getPullBySha(self, sha, project_name, event):
        log = get_annotated_logger(self.log, event)

        # Serve from the cache if existing
        cached_pr_numbers = self._sha_pr_cache.get(project_name, sha)
        if len(cached_pr_numbers) > 1:
            raise Exception('Multiple pulls found with head sha %s' % sha)
        project = self.getProject(project_name)
        if len(cached_pr_numbers) == 1:
            for pr in cached_pr_numbers:
                pr_body = self._getChange(project, pr, sha, event=event).pr
                return pr_body

        github = self.getGithubClient(project_name, zuul_event_id=event)
        issues = list(github.search_issues(sha))

        log.debug('Got PR on project %s for sha %s', project_name, sha)
        if len(issues) == 0:
            return None

        # Github returns all issues that contain the sha, not only the ones
        # with that sha as head_sha so we need to get and update all those
        # changes and then filter for the head sha before we can error out
        # with multiple pulls found.
        found_pr_body = None
        for item in issues:
            pr_body = self._getChange(
                project, item.issue.number, sha, event=event).pr
            self._sha_pr_cache.update(project_name, pr_body)
            if pr_body['head']['sha'] == sha:
                if found_pr_body:
                    raise Exception(
                        'Multiple pulls found with head sha %s' % sha)
                found_pr_body = pr_body

        return found_pr_body

    def getPullReviews(self, pr_obj, project, number, event):
        log = get_annotated_logger(self.log, event)
        # make a list out of the reviews so that we complete our
        # API transaction
        revs = [review.as_dict() for review in pr_obj.reviews()]
        log.debug('Got reviews for PR %s#%s', project, number)

        permissions = {}
        reviews = {}

        for rev in revs:
            login = rev.get('user').get('login')
            user = self.getUser(login, project.name)

            review = {
                'by': {
                    'username': user.get('username'),
                    'email': user.get('email'),
                    'name': user.get('name')
                },
                'grantedOn': int(time.mktime(self._ghTimestampToDate(
                                             rev.get('submitted_at')))),
            }

            review['type'] = rev.get('state').lower()
            review['submitted_at'] = rev.get('submitted_at')

            # Get user's rights. A user always has read to leave a review
            review['permission'] = 'read'

            if login in permissions:
                permission = permissions[login]
            else:
                permission = self.getRepoPermission(project.name, login)
                permissions[login] = permission

            if permission == 'write':
                review['permission'] = 'write'
            if permission == 'admin':
                review['permission'] = 'admin'

            if login not in reviews:
                reviews[login] = review
            else:
                # if there are multiple reviews per user, keep the newest
                # note that this breaks the ability to set the 'older-than'
                # option on a review requirement.
                # BUT do not keep the latest if it's a 'commented' type and the
                # previous review was 'approved' or 'changes_requested', as
                # the GitHub model does not change the vote if a comment is
                # added after the fact. THANKS GITHUB!
                if review['grantedOn'] > reviews[login]['grantedOn']:
                    if (review['type'] == 'commented' and
                        reviews[login]['type'] in
                        ('approved', 'changes_requested')):
                        log.debug("Discarding comment review %s due to "
                                  "an existing vote %s" % (review,
                                                           reviews[login]))
                        pass
                    else:
                        reviews[login] = review

        return reviews.values()

    def _getBranchProtection(self, project_name: str, branch: str,
                             zuul_event_id=None):
        github = self.getGithubClient(
            project_name, zuul_event_id=zuul_event_id)
        url = github.session.build_url('repos', project_name,
                                       'branches', branch,
                                       'protection')

        headers = {'Accept': 'application/vnd.github.loki-preview+json'}
        resp = github.session.get(url, headers=headers)

        if resp.status_code == 404:
            return {}

        return resp.json()

    @staticmethod
    def _getMissingStatusChecks(change, allow_needs):
        if not change.required_contexts:
            # There are no required contexts -> ok by definition
            return set()

        # Strip allow_needs as we will set this in the gate ourselves
        required_contexts = set(
            x for x in change.required_contexts if x not in allow_needs
        )

        # Remove successful checks from the required contexts to get the
        # remaining missing required status.
        return required_contexts.difference(change.successful_contexts)

    @cachetools.cached(cache=cachetools.TTLCache(maxsize=2048, ttl=3600),
                       key=lambda self, login, project:
                       (self.connection_name, login))
    def getUser(self, login, project_name):
        """
        Get a Github user

        The returned user only contains static information so this can be
        cached. For the cache omit the project as this is only used for
        requesting the data and doesn't affect the properties of the user.
        """
        return GithubUser(login, self, project_name)

    def getRepoPermission(self, project, login):
        github = self.getGithubClient(project)
        owner, proj = project.split('/')
        # This gets around a missing API call
        # need preview header
        headers = {'Accept': 'application/vnd.github.korra-preview'}

        # Create a repo object
        repository = github.repository(owner, proj)

        if not repository:
            return 'none'

        # Build up a URL
        url = repository._build_url('collaborators', login, 'permission',
                                    base_url=repository._api)
        # Get the data
        perms = repository._get(url, headers=headers)

        self.log.debug("Got repo permissions for %s/%s", owner, proj)

        # no known user, maybe deleted since review?
        if perms.status_code == 404:
            return 'none'

        # get permissions from the data
        return perms.json().get('permission', 'none')

    def commentPull(self, project, pr_number, message, zuul_event_id=None):
        log = get_annotated_logger(self.log, zuul_event_id)
        github = self.getGithubClient(project, zuul_event_id=zuul_event_id)
        url = github.session.build_url('repos', project,
                                       'issues', str(pr_number), 'comments')
        resp = github.session.post(url, json={'body': message})
        resp.raise_for_status()
        log.debug("Commented on PR %s#%s", project, pr_number)

    def mergePull(self, project, pr_number, commit_message='', sha=None,
                  method='merge', zuul_event_id=None):
        log = get_annotated_logger(self.log, zuul_event_id)
        github = self.getGithubClient(project, zuul_event_id=zuul_event_id)
        url = github.session.build_url("repos", project, "pulls",
                                       str(pr_number), "merge")

        payload = {
            "merge_method": method,
        }
        if sha:
            payload["sha"] = sha
        if commit_message:
            payload["commit_message"] = commit_message

        try:
            resp = github.session.put(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            if not data:
                result = False
            else:
                result = data["merged"]
        except Exception as e:
            if hasattr(e, 'response'):
                response = e.response
                try:
                    raise MergeFailure('Pull request merge failed: '
                                       '%s' % response.json().get('message'))
                except ValueError:
                    # There was no json body so use the generic message below.
                    pass
            raise MergeFailure('Pull request merge failed: %s' % e)

        if not result:
            raise MergeFailure('Pull request was not merged')
        log.debug("Merged PR %s#%s", project, pr_number)

    def _getCommit(self, repository, sha, retries=5):
        try:
            return repository.commit(sha)
        except github3.exceptions.NotFoundError:
            self.log.warning("Commit %s of project %s returned None",
                             sha, repository.name)
            if retries <= 0:
                raise
            time.sleep(1)
            return self._getCommit(repository, sha, retries - 1)

    def getCommitStatuses(self, project_name, sha, zuul_event_id=None):
        log = get_annotated_logger(self.log, zuul_event_id)
        github = self.getGithubClient(
            project_name, zuul_event_id=zuul_event_id)
        url = github.session.build_url('repos', project_name,
                                       'commits', sha, 'statuses')
        params = {'per_page': 100}
        resp = github.session.get(url, params=params)
        resp.raise_for_status()

        log.debug("Got commit statuses for sha %s on %s", sha, project_name)
        return resp.json()

    def setCommitStatus(self, project, sha, state, url='', description='',
                        context='', zuul_event_id=None):
        log = get_annotated_logger(self.log, zuul_event_id)
        github = self.getGithubClient(project, zuul_event_id=zuul_event_id)
        owner, proj = project.split('/')
        repository = github.repository(owner, proj)
        repository.create_status(sha, state, url, description, context)
        log.debug("Set commit status to %s for sha %s on %s",
                  state, sha, project)

    def getCommitChecks(self, project_name, sha, zuul_event_id=None):
        log = get_annotated_logger(self.log, zuul_event_id)
        if not self._github_client_manager.usesAppAuthentication:
            log.debug(
                "Not authenticated as Github app. Unable to retrieve commit "
                "checks for sha %s on %s",
                sha, project_name
            )
            return []

        github = self.getGithubClient(
            project_name, zuul_event_id=zuul_event_id
        )
        self._append_accept_header(github, PREVIEW_CHECKS_ACCEPT)
        url = github.session.build_url(
            "repos", project_name, "commits", sha, "check-runs")
        params = {"per_page": 100}
        resp = github.session.get(url, params=params)
        resp.raise_for_status()

        log.debug("Got commit checks for sha %s on %s", sha, project_name)
        return resp.json().get("check_runs", [])

    def reviewPull(self, project, pr_number, sha, review, body,
                   zuul_event_id=None):
        github = self.getGithubClient(project, zuul_event_id=zuul_event_id)
        owner, proj = project.split('/')
        pull_request = github.pull_request(owner, proj, pr_number)
        event = review.replace('-', '_')
        event = event.upper()
        pull_request.create_review(body=body, commit_id=sha, event=event)

    def labelPull(self, project, pr_number, label, zuul_event_id=None):
        log = get_annotated_logger(self.log, zuul_event_id)
        github = self.getGithubClient(project, zuul_event_id=zuul_event_id)
        owner, proj = project.split('/')
        pull_request = github.issue(owner, proj, pr_number)
        pull_request.add_labels(label)
        log.debug("Added label %s to %s#%s", label, proj, pr_number)

    def unlabelPull(self, project, pr_number, label, zuul_event_id=None):
        log = get_annotated_logger(self.log, zuul_event_id)
        github = self.getGithubClient(project, zuul_event_id=zuul_event_id)
        owner, proj = project.split('/')
        pull_request = github.issue(owner, proj, pr_number)
        try:
            pull_request.remove_label(label)
        except github3.exceptions.NotFoundError:
            # The label is not existing, so everything ok
            log.debug('Label %s not found on %s#%s', label, proj, pr_number)
        log.debug("Removed label %s from %s#%s", label, proj, pr_number)

    def _create_or_update_check(self, github, project_name, check_run_id,
                                **kwargs):
        if check_run_id:
            # Update an existing check run
            url = github.session.build_url(
                'repos', project_name, 'check-runs', str(check_run_id))
            resp = github.session.patch(url, json=kwargs)
        else:
            # Create a new check run
            url = github.session.build_url(
                'repos', project_name, 'check-runs')
            resp = github.session.post(url, json=kwargs)
        resp.raise_for_status()
        return resp.json().get('id')

    def updateCheck(self, project, pr_number, sha, status, completed, context,
                    details_url, message, file_comments, external_id,
                    zuul_event_id=None, check_run_id=None):
        log = get_annotated_logger(self.log, zuul_event_id)
        github = self.getGithubClient(project, zuul_event_id=zuul_event_id)
        self._append_accept_header(github, PREVIEW_CHECKS_ACCEPT)

        # Always provide an empty list of actions by default
        actions = []

        # Track a list of failed check run operations to report back to Github
        errors = []

        if not self._github_client_manager.usesAppAuthentication:
            # We don't try to update check runs, if we aren't authenticated as
            # Github app at all. If we are, we still have to ensure that we
            # don't crash on missing permissions.
            log.debug(
                "Not authenticated as Github app. Unable to create or update "
                "check run '%s' for sha %s on %s",
                context, sha, project
            )

            errors.append(
                "Unable to create or update check {}. Must be authenticated "
                "as app integration.".format(
                    context
                )
            )
            return None, errors

        output = {"title": "Summary", "summary": message}

        if file_comments:
            # Build the list of annotations to be applied on the check run
            output["annotations"] = self._buildAnnotationsFromComments(
                file_comments
            )

        # Currently, the GithubReporter only supports start and end reporting.
        # During the build no further update will be reported.
        if completed:
            # As the buildset itself does not provide a proper end time, we
            # use the current time instead. Otherwise, we would have to query
            # all builds contained in the buildset and search for the latest
            # build.end_time available.
            completed_at = datetime.datetime.now(utc).isoformat()

            # When reporting the completion of a check_run, we must set the
            # conclusion, as the status will always be "completed".
            conclusion = status

            if not check_run_id:
                log.debug("Could not find check run %s for %s#%s on sha %s. "
                          "Creating a new one", context, project, pr_number,
                          sha)
                action = 'create'
                arguments = dict(
                    name=context,
                    head_sha=sha,
                    conclusion=conclusion,
                    completed_at=completed_at,
                    output=output,
                    details_url=details_url,
                    external_id=external_id,
                    actions=actions,
                )
            else:
                log.debug("Updating existing check run %s for %s#%s on sha %s "
                          "with status %s", context, project, pr_number, sha,
                          status)
                action = 'update'
                arguments = dict(
                    conclusion=conclusion,
                    completed_at=completed_at,
                    output=output,
                    details_url=details_url,
                    external_id=external_id,
                    actions=actions,
                )
        else:
            # Add an abort/dequeue action to running check runs
            actions.append(
                {
                    "label": "Abort",
                    "description": "Abort this check run",
                    # Usually Github wants us to provide an identifier for our
                    # system here, so we can identify this action. But as zuul
                    # is already identifying this event based on the check run
                    # this shouldn't be necessary.
                    "identifier": "abort",
                }
            )

            action = 'create'
            arguments = dict(
                name=context,
                head_sha=sha,
                status=status,
                output=output,
                details_url=details_url,
                external_id=external_id,
                actions=actions,
            )

        # Create/update the check run
        try:
            check_run_id = self._create_or_update_check(
                github,
                project,
                check_run_id,
                **arguments,
            )

        except requests.exceptions.HTTPError as exc:
            log.error("Failed to %s check run %s for %s#%s on sha %s: %s",
                      action, context, project, pr_number, sha, str(exc))
            errors.append("Failed to {} check run {}: {}".format(
                action, context, str(exc)))

        return check_run_id, errors

    def _buildAnnotationsFromComments(self, file_comments):
        annotations = []
        for fn, comments in file_comments.items():
            for comment in comments:

                if "message" not in comment:
                    # Github doesn't accept anntoations without a message.
                    # Faking a message doesn't make munch sense to me.
                    continue

                start_column = None
                end_column = None
                start_line = None
                end_line = None

                if "line" in comment:
                    start_line = comment.get("line")
                    end_line = comment.get("line")

                if "range" in comment:
                    rng = comment["range"]
                    # Look up the start_ and end_line from the range and use
                    # the line as fallback
                    start_line = rng.get("start_line")
                    end_line = rng.get("end_line")

                    # Github only accepts column parameters if they apply to
                    # the same line.
                    if start_line == end_line:
                        start_column = rng.get("start_character")
                        end_column = rng.get("end_character")

                # Map the level coming from zuul_return to the ones Github
                # expects. Each Github annotation must provide a level, so
                # we fall back to "warning" in case no or an invalid level
                # is provided.
                annotation_level = ANNOTATION_LEVELS.get(
                    comment.get("level"), "warning"
                )

                # A Github check annotation requires at least the following
                # attributes: "path", "start_line", "end_line", "message" and
                # "annotation_level"
                raw_annotation = {
                    "path": fn,
                    "annotation_level": annotation_level,
                    "message": comment["message"],
                    "start_line": start_line,
                    "end_line": end_line,
                    "start_column": start_column,
                    "end_column": end_column,
                }

                # Filter out None values from the annotation. Otherwise
                # github will complain about column values being None:
                # "For 'properties/start_column', nil is not an integer."
                # "For 'properties/end_column', nil is not an integer."
                annotation = {
                    k: v for k, v in raw_annotation.items()
                    if v is not None
                }

                # Don't provide an annotation without proper start_ and
                # end_line as this will make the whole check run update fail.
                if not {"start_line", "end_line"} <= set(annotation):
                    continue

                annotations.append(annotation)

        def _sortUniqueness(annotations):
            """
            This method is intended to spread the annotations by uniqueness
            so we have an as diverse as possible list of annotations.
            """
            # First group
            per_message = defaultdict(list)
            for annotation in annotations:
                per_message[annotation['message']].append(annotation)

            # Sort the lists by length. This way we get the messages that
            # occur less frequently at first.
            annotation_lists = sorted(list(per_message.values()),
                                      key=lambda l: len(l))

            return list(chain(*annotation_lists))

        if len(annotations) > 50:
            # We cannot report more than 50 file comments so sort them by
            # uniqueness in order to give the user a diverse set of annotations
            annotations = _sortUniqueness(annotations)

        return annotations[:50]

    def getPushedFileNames(self, event):
        files = set()
        for c in event.commits:
            for f in c.get('added') + c.get('modified') + c.get('removed'):
                files.add(f)
        return list(files)

    def _ghTimestampToDate(self, timestamp):
        return time.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ')

    def _get_contexts(self, canmerge_data):
        contexts = set(
            _status_as_tuple(s) for s in canmerge_data["status"].values()
        )
        contexts.update(set(
            _check_as_tuple(c) for c in canmerge_data["checks"].values()
        ))
        return contexts

    def getWebController(self, zuul_web):
        return GithubWebController(zuul_web, self)

    def getEventQueue(self):
        return getattr(self, "event_queue", None)

    def validateWebConfig(self, config, connections):
        if 'webhook_token' not in self.connection_config:
            raise Exception(
                "webhook_token not found in config for connection %s" %
                self.connection_name)
        return True


class GithubWebController(BaseWebController):

    log = logging.getLogger("zuul.GithubWebController")

    def __init__(self, zuul_web, connection):
        self.connection = connection
        self.zuul_web = zuul_web
        self.event_queue = ConnectionEventQueue(
            self.zuul_web.zk_client,
            self.connection.connection_name
        )
        self.token = self.connection.connection_config.get('webhook_token')

    def _validate_signature(self, body, headers):
        try:
            request_signature = headers['x-hub-signature']
        except KeyError:
            raise cherrypy.HTTPError(401, 'X-Hub-Signature header missing.')

        payload_signature = _sign_request(body, self.token)

        self.log.debug("Payload Signature: {0}".format(str(payload_signature)))
        self.log.debug("Request Signature: {0}".format(str(request_signature)))
        if not hmac.compare_digest(
            str(payload_signature), str(request_signature)):
            raise cherrypy.HTTPError(
                401,
                'Request signature does not match calculated payload '
                'signature. Check that secret is correct.')

        return True

    @cherrypy.expose
    @cherrypy.tools.json_out(content_type='application/json; charset=utf-8')
    def payload(self):
        # Note(tobiash): We need to normalize the headers. Otherwise we will
        # have trouble to get them from the dict afterwards.
        # e.g.
        # GitHub: sent: X-GitHub-Event received: X-GitHub-Event
        # urllib: sent: X-GitHub-Event received: X-Github-Event
        #
        # We cannot easily solve this mismatch as every http processing lib
        # modifies the header casing in its own way and by specification http
        # headers are case insensitive so just lowercase all so we don't have
        # to take care later.
        # Note(corvus): Don't use cherrypy's json_in here so that we
        # can validate the signature.
        headers = dict()
        for key, value in cherrypy.request.headers.items():
            headers[key.lower()] = value
        body = cherrypy.request.body.read()
        self._validate_signature(body, headers)
        # We cannot send the raw body through zookeeper, so it's easy to just
        # encode it as json, after decoding it as utf-8
        json_body = json.loads(body.decode('utf-8'))

        data = {'headers': headers, 'body': json_body}
        self.event_queue.put(data)
        return data


def _status_as_tuple(status):
    """Translate a status into a tuple of user, context, state"""

    creator = status.get('creator')
    if not creator:
        user = "Unknown"
    else:
        user = creator.get('login')
    context = status.get('context')
    state = status.get('state')
    # Normalize state to lowercase as the Graphql and REST API are not
    # consistent in this regard.
    state = state.lower() if state else state
    return (user, context, state)


def _check_as_tuple(check):
    """Translate a check into a tuple of app, name, conclusion"""

    # A check_run does not contain any "creator" information like a status, but
    # only the app for/by which it was created.
    app = check.get("app")
    if app:
        slug = app.get("slug")
    else:
        slug = "Unknown"
    name = check.get("name")
    conclusion = check.get("conclusion")
    # Normalize conclusion to lowercase as the Graphql and REST API are not
    # consistent in this regard.
    conclusion = conclusion.lower() if conclusion else conclusion
    return (slug, name, conclusion)
