# Copyright 2012 Hewlett-Packard Development Company, L.P.
# Copyright 2016 Red Hat, Inc.
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

import configparser
from collections import OrderedDict
from configparser import ConfigParser
from contextlib import contextmanager
import copy
import datetime
import errno
import gc
import hashlib
from io import StringIO
import itertools
import json
import logging
import os
import random
import re
from collections import defaultdict, namedtuple
from queue import Queue
from typing import Callable, Optional, Any, Iterable, Generator, List, Dict
from unittest.case import skipIf

import requests
import select
import shutil
import socket
import string
import subprocess
import sys
import tempfile
import threading
import traceback
import time
import uuid
import socketserver
import http.server
import urllib.parse

import git
import gear
import fixtures
import kazoo.client
import kazoo.exceptions
import pymysql
import psycopg2
import psycopg2.extensions
import testtools
import testtools.content
import testtools.content_type
from git.exc import NoSuchPathError
import yaml
import paramiko
import sqlalchemy
import requests_mock

from kazoo.exceptions import NoNodeError

from zuul import model
from zuul.model import BuildRequest, Change, MergeRequest, WebInfo
from zuul.rpcclient import RPCClient

from zuul.driver.zuul import ZuulDriver
from zuul.driver.git import GitDriver
from zuul.driver.smtp import SMTPDriver
from zuul.driver.github import GithubDriver
from zuul.driver.timer import TimerDriver
from zuul.driver.sql import SQLDriver
from zuul.driver.bubblewrap import BubblewrapDriver
from zuul.driver.nullwrap import NullwrapDriver
from zuul.driver.mqtt import MQTTDriver
from zuul.driver.pagure import PagureDriver
from zuul.driver.gitlab import GitlabDriver
from zuul.driver.gerrit import GerritDriver
from zuul.driver.github.githubconnection import GithubClientManager
from zuul.driver.elasticsearch import ElasticsearchDriver
from zuul.lib.collections import DefaultKeyDict
from zuul.lib.connections import ConnectionRegistry
from zuul.zk import zkobject, ZooKeeperClient
from zuul.zk.event_queues import ConnectionEventQueue
from zuul.zk.executor import ExecutorApi
from zuul.zk.locks import tenant_read_lock, pipeline_lock, SessionAwareLock
from zuul.zk.merger import MergerApi
from psutil import Popen

import zuul.driver.gerrit.gerritsource as gerritsource
import zuul.driver.gerrit.gerritconnection as gerritconnection
import zuul.driver.git.gitwatcher as gitwatcher
import zuul.driver.github.githubconnection as githubconnection
import zuul.driver.pagure.pagureconnection as pagureconnection
import zuul.driver.gitlab.gitlabconnection as gitlabconnection
import zuul.driver.github
import zuul.driver.elasticsearch.connection as elconnection
import zuul.driver.sql
import zuul.scheduler
import zuul.executor.server
import zuul.executor.client
import zuul.lib.ansible
import zuul.lib.connections
import zuul.lib.auth
import zuul.lib.keystorage
import zuul.merger.client
import zuul.merger.merger
import zuul.merger.server
import zuul.nodepool
import zuul.rpcclient
import zuul.configloader
from zuul.lib.config import get_default
from zuul.lib.logutil import get_annotated_logger

import tests.fakegithub
import tests.fakegitlab

FIXTURE_DIR = os.path.join(os.path.dirname(__file__), 'fixtures')

KEEP_TEMPDIRS = bool(os.environ.get('KEEP_TEMPDIRS', False))
SCHEDULER_COUNT = int(os.environ.get('ZUUL_SCHEDULER_COUNT', 1))


def skipIfMultiScheduler(reason=None):
    if not reason:
        reason = "Test is failing with multiple schedulers"
    return skipIf(SCHEDULER_COUNT > 1, reason)


def repack_repo(path):
    cmd = ['git', '--git-dir=%s/.git' % path, 'repack', '-afd']
    output = subprocess.Popen(cmd, close_fds=True,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
    out = output.communicate()
    if output.returncode:
        raise Exception("git repack returned %d" % output.returncode)
    return out


def random_sha1():
    return hashlib.sha1(str(random.random()).encode('ascii')).hexdigest()


def iterate_timeout(max_seconds, purpose):
    start = time.time()
    count = 0
    while (time.time() < start + max_seconds):
        count += 1
        yield count
        time.sleep(0.01)
    raise Exception("Timeout waiting for %s" % purpose)


def simple_layout(path, driver='gerrit'):
    """Specify a layout file for use by a test method.

    :arg str path: The path to the layout file.
    :arg str driver: The source driver to use, defaults to gerrit.

    Some tests require only a very simple configuration.  For those,
    establishing a complete config directory hierachy is too much
    work.  In those cases, you can add a simple zuul.yaml file to the
    test fixtures directory (in fixtures/layouts/foo.yaml) and use
    this decorator to indicate the test method should use that rather
    than the tenant config file specified by the test class.

    The decorator will cause that layout file to be added to a
    config-project called "common-config" and each "project" instance
    referenced in the layout file will have a git repo automatically
    initialized.
    """

    def decorator(test):
        test.__simple_layout__ = (path, driver)
        return test
    return decorator


def never_capture():
    """Never capture logs/output

    Due to high volume, log files are normally captured and attached
    to the subunit stream only on error.  This can make diagnosing
    some problems difficult.  Use this dectorator on a test to
    indicate that logs and output should not be captured.

    """

    def decorator(test):
        test.__never_capture__ = True
        return test
    return decorator


def registerProjects(source_name, client, config):
    path = config.get('scheduler', 'tenant_config')
    with open(os.path.join(FIXTURE_DIR, path)) as f:
        tenant_config = yaml.safe_load(f.read())
    for tenant in tenant_config:
        sources = tenant['tenant']['source']
        conf = sources.get(source_name)
        if not conf:
            return

        projects = conf.get('config-projects', [])
        projects.extend(conf.get('untrusted-projects', []))

        for project in projects:
            if isinstance(project, dict):
                # This can be a dict with the project as the only key
                client.addProjectByName(
                    list(project.keys())[0])
            else:
                client.addProjectByName(project)


class StatException(Exception):
    # Used by assertReportedStat
    pass


class GerritDriverMock(GerritDriver):
    def __init__(self, registry, changes: Dict[str, Dict[str, Change]],
                 upstream_root: str, additional_event_queues, poller_events,
                 add_cleanup: Callable[[Callable[[], None]], None]):
        super(GerritDriverMock, self).__init__()
        self.registry = registry
        self.changes = changes
        self.upstream_root = upstream_root
        self.additional_event_queues = additional_event_queues
        self.poller_events = poller_events
        self.add_cleanup = add_cleanup

    def getConnection(self, name, config):
        db = self.changes.setdefault(config['server'], {})
        poll_event = self.poller_events.setdefault(name, threading.Event())
        ref_event = self.poller_events.setdefault(name + '-ref',
                                                  threading.Event())
        connection = FakeGerritConnection(
            self, name, config,
            changes_db=db,
            upstream_root=self.upstream_root,
            poller_event=poll_event,
            ref_watcher_event=ref_event)
        if connection.web_server:
            self.add_cleanup(connection.web_server.stop)

        setattr(self.registry, 'fake_' + name, connection)
        return connection


class GithubDriverMock(GithubDriver):
    def __init__(self, registry, changes: Dict[str, Dict[str, Change]],
                 config: ConfigParser, upstream_root: str,
                 additional_event_queues, rpcclient: RPCClient,
                 git_url_with_auth: bool):
        super(GithubDriverMock, self).__init__()
        self.registry = registry
        self.changes = changes
        self.config = config
        self.upstream_root = upstream_root
        self.additional_event_queues = additional_event_queues
        self.rpcclient = rpcclient
        self.git_url_with_auth = git_url_with_auth

    def getConnection(self, name, config):
        server = config.get('server', 'github.com')
        db = self.changes.setdefault(server, {})
        connection = FakeGithubConnection(
            self, name, config, self.rpcclient,
            changes_db=db,
            upstream_root=self.upstream_root,
            git_url_with_auth=self.git_url_with_auth)
        setattr(self.registry, 'fake_' + name, connection)
        client = connection.getGithubClient(None)
        registerProjects(connection.source.name, client, self.config)
        return connection


class PagureDriverMock(PagureDriver):
    def __init__(self, registry, changes: Dict[str, Dict[str, Change]],
                 upstream_root: str, additional_event_queues,
                 rpcclient: RPCClient):
        super(PagureDriverMock, self).__init__()
        self.registry = registry
        self.changes = changes
        self.upstream_root = upstream_root
        self.additional_event_queues = additional_event_queues
        self.rpcclient = rpcclient

    def getConnection(self, name, config):
        server = config.get('server', 'pagure.io')
        db = self.changes.setdefault(server, {})
        connection = FakePagureConnection(
            self, name, config, self.rpcclient,
            changes_db=db,
            upstream_root=self.upstream_root)
        setattr(self.registry, 'fake_' + name, connection)
        return connection


class GitlabDriverMock(GitlabDriver):
    def __init__(self, registry, changes: Dict[str, Dict[str, Change]],
                 config: ConfigParser, upstream_root: str,
                 additional_event_queues, rpcclient: RPCClient):
        super(GitlabDriverMock, self).__init__()
        self.registry = registry
        self.changes = changes
        self.config = config
        self.upstream_root = upstream_root
        self.additional_event_queues = additional_event_queues
        self.rpcclient = rpcclient

    def getConnection(self, name, config):
        server = config.get('server', 'gitlab.com')
        db = self.changes.setdefault(server, {})
        connection = FakeGitlabConnection(
            self, name, config, self.rpcclient,
            changes_db=db,
            upstream_root=self.upstream_root)
        setattr(self.registry, 'fake_' + name, connection)
        registerProjects(connection.source.name, connection,
                         self.config)
        return connection


class TestConnectionRegistry(ConnectionRegistry):
    def __init__(self, changes: Dict[str, Dict[str, Change]],
                 config: ConfigParser, additional_event_queues,
                 upstream_root: str, rpcclient: RPCClient, poller_events,
                 git_url_with_auth: bool,
                 add_cleanup: Callable[[Callable[[], None]], None]):
        self.connections = OrderedDict()
        self.drivers = {}

        self.registerDriver(ZuulDriver())
        self.registerDriver(GerritDriverMock(
            self, changes, upstream_root, additional_event_queues,
            poller_events, add_cleanup))
        self.registerDriver(GitDriver())
        self.registerDriver(GithubDriverMock(
            self, changes, config, upstream_root, additional_event_queues,
            rpcclient, git_url_with_auth))
        self.registerDriver(SMTPDriver())
        self.registerDriver(TimerDriver())
        self.registerDriver(SQLDriver())
        self.registerDriver(BubblewrapDriver())
        self.registerDriver(NullwrapDriver())
        self.registerDriver(MQTTDriver())
        self.registerDriver(PagureDriverMock(
            self, changes, upstream_root, additional_event_queues, rpcclient))
        self.registerDriver(GitlabDriverMock(
            self, changes, config, upstream_root, additional_event_queues,
            rpcclient))
        self.registerDriver(ElasticsearchDriver())


class FakeAnsibleManager(zuul.lib.ansible.AnsibleManager):

    def validate(self):
        return True

    def copyAnsibleFiles(self):
        pass


class GerritChangeReference(git.Reference):
    _common_path_default = "refs/changes"
    _points_to_commits_only = True


class FakeGerritChange(object):
    categories = {'Approved': ('Approved', -1, 1),
                  'Code-Review': ('Code-Review', -2, 2),
                  'Verified': ('Verified', -2, 2)}

    def __init__(self, gerrit, number, project, branch, subject,
                 status='NEW', upstream_root=None, files={},
                 parent=None, merge_parents=None, merge_files=None):
        self.gerrit = gerrit
        self.source = gerrit
        self.reported = 0
        self.queried = 0
        self.patchsets = []
        self.number = number
        self.project = project
        self.branch = branch
        self.subject = subject
        self.latest_patchset = 0
        self.depends_on_change = None
        self.depends_on_patchset = None
        self.needed_by_changes = []
        self.fail_merge = False
        self.messages = []
        self.comments = []
        self.checks = {}
        self.checks_history = []
        self.data = {
            'branch': branch,
            'comments': self.comments,
            'commitMessage': subject,
            'createdOn': time.time(),
            'id': 'I' + random_sha1(),
            'lastUpdated': time.time(),
            'number': str(number),
            'open': status == 'NEW',
            'owner': {'email': 'user@example.com',
                      'name': 'User Name',
                      'username': 'username'},
            'patchSets': self.patchsets,
            'project': project,
            'status': status,
            'subject': subject,
            'submitRecords': [],
            'url': '%s/%s' % (self.gerrit.baseurl.rstrip('/'), number)}

        self.upstream_root = upstream_root
        if merge_parents:
            self.addMergePatchset(parents=merge_parents,
                                  merge_files=merge_files)
        else:
            self.addPatchset(files=files, parent=parent)
        if merge_parents:
            self.data['parents'] = merge_parents
        elif parent:
            self.data['parents'] = [parent]
        self.data['submitRecords'] = self.getSubmitRecords()
        self.open = status == 'NEW'

    def addFakeChangeToRepo(self, msg, files, large, parent):
        path = os.path.join(self.upstream_root, self.project)
        repo = git.Repo(path)
        if parent is None:
            parent = 'refs/tags/init'
        ref = GerritChangeReference.create(
            repo, '%s/%s/%s' % (str(self.number).zfill(2)[-2:],
                                self.number,
                                self.latest_patchset),
            parent)
        repo.head.reference = ref
        repo.head.reset(working_tree=True)
        repo.git.clean('-x', '-f', '-d')

        path = os.path.join(self.upstream_root, self.project)
        if not large:
            for fn, content in files.items():
                fn = os.path.join(path, fn)
                if content is None:
                    os.unlink(fn)
                    repo.index.remove([fn])
                else:
                    d = os.path.dirname(fn)
                    if not os.path.exists(d):
                        os.makedirs(d)
                    with open(fn, 'w') as f:
                        f.write(content)
                    repo.index.add([fn])
        else:
            for fni in range(100):
                fn = os.path.join(path, str(fni))
                f = open(fn, 'w')
                for ci in range(4096):
                    f.write(random.choice(string.printable))
                f.close()
                repo.index.add([fn])

        r = repo.index.commit(msg)
        repo.head.reference = 'master'
        repo.head.reset(working_tree=True)
        repo.git.clean('-x', '-f', '-d')
        repo.heads['master'].checkout()
        return r

    def addFakeMergeCommitChangeToRepo(self, msg, parents):
        path = os.path.join(self.upstream_root, self.project)
        repo = git.Repo(path)
        ref = GerritChangeReference.create(
            repo, '%s/%s/%s' % (str(self.number).zfill(2)[-2:],
                                self.number,
                                self.latest_patchset),
            parents[0])
        repo.head.reference = ref
        repo.head.reset(working_tree=True)
        repo.git.clean('-x', '-f', '-d')

        repo.index.merge_tree(parents[1])
        r = repo.index.commit(msg)

        repo.head.reference = 'master'
        repo.head.reset(working_tree=True)
        repo.git.clean('-x', '-f', '-d')
        repo.heads['master'].checkout()
        return r

    def addPatchset(self, files=None, large=False, parent=None):
        self.latest_patchset += 1
        if not files:
            fn = '%s-%s' % (self.branch.replace('/', '_'), self.number)
            data = ("test %s %s %s\n" %
                    (self.branch, self.number, self.latest_patchset))
            files = {fn: data}
        msg = self.subject + '-' + str(self.latest_patchset)
        c = self.addFakeChangeToRepo(msg, files, large, parent)
        ps_files = [{'file': '/COMMIT_MSG',
                     'type': 'ADDED'},
                    {'file': 'README',
                     'type': 'MODIFIED'}]
        for f in files:
            ps_files.append({'file': f, 'type': 'ADDED'})
        d = {'approvals': [],
             'createdOn': time.time(),
             'files': ps_files,
             'number': str(self.latest_patchset),
             'ref': 'refs/changes/%s/%s/%s' % (str(self.number).zfill(2)[-2:],
                                               self.number,
                                               self.latest_patchset),
             'revision': c.hexsha,
             'uploader': {'email': 'user@example.com',
                          'name': 'User name',
                          'username': 'user'}}
        self.data['currentPatchSet'] = d
        self.patchsets.append(d)
        self.data['submitRecords'] = self.getSubmitRecords()

    def addMergePatchset(self, parents, merge_files=None):
        self.latest_patchset += 1
        if not merge_files:
            merge_files = []
        msg = self.subject + '-' + str(self.latest_patchset)
        c = self.addFakeMergeCommitChangeToRepo(msg, parents)
        ps_files = [{'file': '/COMMIT_MSG',
                     'type': 'ADDED'},
                    {'file': '/MERGE_LIST',
                     'type': 'ADDED'}]
        for f in merge_files:
            ps_files.append({'file': f, 'type': 'ADDED'})
        d = {'approvals': [],
             'createdOn': time.time(),
             'files': ps_files,
             'number': str(self.latest_patchset),
             'ref': 'refs/changes/%s/%s/%s' % (str(self.number).zfill(2)[-2:],
                                               self.number,
                                               self.latest_patchset),
             'revision': c.hexsha,
             'uploader': {'email': 'user@example.com',
                          'name': 'User name',
                          'username': 'user'}}
        self.data['currentPatchSet'] = d
        self.patchsets.append(d)
        self.data['submitRecords'] = self.getSubmitRecords()

    def setCheck(self, checker, reset=False, **kw):
        if reset:
            self.checks[checker] = {'state': 'NOT_STARTED',
                                    'created': str(datetime.datetime.now())}
        chk = self.checks.setdefault(checker, {})
        chk['updated'] = str(datetime.datetime.now())
        for (key, default) in [
                ('state', None),
                ('repository', self.project),
                ('change_number', self.number),
                ('patch_set_id', self.latest_patchset),
                ('checker_uuid', checker),
                ('message', None),
                ('url', None),
                ('started', None),
                ('finished', None),
        ]:
            val = kw.get(key, chk.get(key, default))
            if val is not None:
                chk[key] = val
            elif key in chk:
                del chk[key]
        self.checks_history.append(copy.deepcopy(self.checks))

    def addComment(self, filename, line, message, name, email, username,
                   comment_range=None):
        comment = {
            'file': filename,
            'line': int(line),
            'reviewer': {
                'name': name,
                'email': email,
                'username': username,
            },
            'message': message,
        }
        if comment_range:
            comment['range'] = comment_range
        self.comments.append(comment)

    def getPatchsetCreatedEvent(self, patchset):
        event = {"type": "patchset-created",
                 "change": {"project": self.project,
                            "branch": self.branch,
                            "id": "I5459869c07352a31bfb1e7a8cac379cabfcb25af",
                            "number": str(self.number),
                            "subject": self.subject,
                            "owner": {"name": "User Name"},
                            "url": "https://hostname/3"},
                 "patchSet": self.patchsets[patchset - 1],
                 "uploader": {"name": "User Name"}}
        return event

    def getChangeRestoredEvent(self):
        event = {"type": "change-restored",
                 "change": {"project": self.project,
                            "branch": self.branch,
                            "id": "I5459869c07352a31bfb1e7a8cac379cabfcb25af",
                            "number": str(self.number),
                            "subject": self.subject,
                            "owner": {"name": "User Name"},
                            "url": "https://hostname/3"},
                 "restorer": {"name": "User Name"},
                 "patchSet": self.patchsets[-1],
                 "reason": ""}
        return event

    def getChangeAbandonedEvent(self):
        event = {"type": "change-abandoned",
                 "change": {"project": self.project,
                            "branch": self.branch,
                            "id": "I5459869c07352a31bfb1e7a8cac379cabfcb25af",
                            "number": str(self.number),
                            "subject": self.subject,
                            "owner": {"name": "User Name"},
                            "url": "https://hostname/3"},
                 "abandoner": {"name": "User Name"},
                 "patchSet": self.patchsets[-1],
                 "reason": ""}
        return event

    def getChangeCommentEvent(self, patchset, comment=None,
                              patchsetcomment=None):
        if comment is None and patchsetcomment is None:
            comment = "Patch Set %d:\n\nThis is a comment" % patchset
        elif comment:
            comment = "Patch Set %d:\n\n%s" % (patchset, comment)
        else:  # patchsetcomment is not None
            comment = "Patch Set %d:\n\n(1 comment)" % patchset

        commentevent = {"comment": comment}
        if patchsetcomment:
            commentevent.update(
                {'patchSetComments':
                    {"/PATCHSET_LEVEL": [{"message": patchsetcomment}]}
                }
            )

        event = {"type": "comment-added",
                 "change": {"project": self.project,
                            "branch": self.branch,
                            "id": "I5459869c07352a31bfb1e7a8cac379cabfcb25af",
                            "number": str(self.number),
                            "subject": self.subject,
                            "owner": {"name": "User Name"},
                            "url": "https://hostname/3"},
                 "patchSet": self.patchsets[patchset - 1],
                 "author": {"name": "User Name"},
                 "approvals": [{"type": "Code-Review",
                                "description": "Code-Review",
                                "value": "0"}]}
        event.update(commentevent)
        return event

    def getChangeMergedEvent(self):
        event = {"submitter": {"name": "Jenkins",
                               "username": "jenkins"},
                 "newRev": "29ed3b5f8f750a225c5be70235230e3a6ccb04d9",
                 "patchSet": self.patchsets[-1],
                 "change": self.data,
                 "type": "change-merged",
                 "eventCreatedOn": 1487613810}
        return event

    def getRefUpdatedEvent(self):
        path = os.path.join(self.upstream_root, self.project)
        repo = git.Repo(path)
        oldrev = repo.heads[self.branch].commit.hexsha

        event = {
            "type": "ref-updated",
            "submitter": {
                "name": "User Name",
            },
            "refUpdate": {
                "oldRev": oldrev,
                "newRev": self.patchsets[-1]['revision'],
                "refName": self.branch,
                "project": self.project,
            }
        }
        return event

    def addApproval(self, category, value, username='reviewer_john',
                    granted_on=None, message='', tag=None):
        if not granted_on:
            granted_on = time.time()
        approval = {
            'description': self.categories[category][0],
            'type': category,
            'value': str(value),
            'by': {
                'username': username,
                'email': username + '@example.com',
            },
            'grantedOn': int(granted_on),
            '__tag': tag,  # Not available in ssh api
        }
        for i, x in enumerate(self.patchsets[-1]['approvals'][:]):
            if x['by']['username'] == username and x['type'] == category:
                del self.patchsets[-1]['approvals'][i]
        self.patchsets[-1]['approvals'].append(approval)
        event = {'approvals': [approval],
                 'author': {'email': 'author@example.com',
                            'name': 'Patchset Author',
                            'username': 'author_phil'},
                 'change': {'branch': self.branch,
                            'id': 'Iaa69c46accf97d0598111724a38250ae76a22c87',
                            'number': str(self.number),
                            'owner': {'email': 'owner@example.com',
                                      'name': 'Change Owner',
                                      'username': 'owner_jane'},
                            'project': self.project,
                            'subject': self.subject,
                            'topic': 'master',
                            'url': 'https://hostname/459'},
                 'comment': message,
                 'patchSet': self.patchsets[-1],
                 'type': 'comment-added'}
        self.data['submitRecords'] = self.getSubmitRecords()
        return json.loads(json.dumps(event))

    def setWorkInProgress(self, wip):
        # Gerrit only includes 'wip' in the data returned via ssh if
        # the value is true.
        if wip:
            self.data['wip'] = True
        elif 'wip' in self.data:
            del self.data['wip']

    def getSubmitRecords(self):
        status = {}
        for cat in self.categories:
            status[cat] = 0

        for a in self.patchsets[-1]['approvals']:
            cur = status[a['type']]
            cat_min, cat_max = self.categories[a['type']][1:]
            new = int(a['value'])
            if new == cat_min:
                cur = new
            elif abs(new) > abs(cur):
                cur = new
            status[a['type']] = cur

        labels = []
        ok = True
        for typ, cat in self.categories.items():
            cur = status[typ]
            cat_min, cat_max = cat[1:]
            if cur == cat_min:
                value = 'REJECT'
                ok = False
            elif cur == cat_max:
                value = 'OK'
            else:
                value = 'NEED'
                ok = False
            labels.append({'label': cat[0], 'status': value})
        if ok:
            return [{'status': 'OK'}]
        return [{'status': 'NOT_READY',
                 'labels': labels}]

    def setDependsOn(self, other, patchset):
        self.depends_on_change = other
        self.depends_on_patchset = patchset
        d = {'id': other.data['id'],
             'number': other.data['number'],
             'ref': other.patchsets[patchset - 1]['ref']
             }
        self.data['dependsOn'] = [d]

        other.needed_by_changes.append((self, len(self.patchsets)))
        needed = other.data.get('neededBy', [])
        d = {'id': self.data['id'],
             'number': self.data['number'],
             'ref': self.patchsets[-1]['ref'],
             'revision': self.patchsets[-1]['revision']
             }
        needed.append(d)
        other.data['neededBy'] = needed

    def query(self):
        self.queried += 1
        d = self.data.get('dependsOn')
        if d:
            d = d[0]
            if (self.depends_on_change.patchsets[-1]['ref'] == d['ref']):
                d['isCurrentPatchSet'] = True
            else:
                d['isCurrentPatchSet'] = False
        return json.loads(json.dumps(self.data))

    def queryHTTP(self):
        self.queried += 1
        labels = {}
        for cat in self.categories:
            labels[cat] = {}
        for app in self.patchsets[-1]['approvals']:
            label = labels[app['type']]
            _, label_min, label_max = self.categories[app['type']]
            val = int(app['value'])
            label_all = label.setdefault('all', [])
            approval = {
                "value": val,
                "username": app['by']['username'],
                "email": app['by']['email'],
                "date": str(datetime.datetime.fromtimestamp(app['grantedOn'])),
            }
            if app.get('__tag') is not None:
                approval['tag'] = app['__tag']
            label_all.append(approval)
            if val == label_min:
                label['blocking'] = True
                if 'rejected' not in label:
                    label['rejected'] = app['by']
            if val == label_max:
                if 'approved' not in label:
                    label['approved'] = app['by']
        revisions = {}
        rev = self.patchsets[-1]
        num = len(self.patchsets)
        files = {}
        for f in rev['files']:
            if f['file'] == '/COMMIT_MSG':
                continue
            files[f['file']] = {"status": f['type'][0]}  # ADDED -> A
        parent = '0000000000000000000000000000000000000000'
        if self.depends_on_change:
            parent = self.depends_on_change.patchsets[
                self.depends_on_patchset - 1]['revision']
        revisions[rev['revision']] = {
            "kind": "REWORK",
            "_number": num,
            "created": rev['createdOn'],
            "uploader": rev['uploader'],
            "ref": rev['ref'],
            "commit": {
                "subject": self.subject,
                "message": self.data['commitMessage'],
                "parents": [{
                    "commit": parent,
                }]
            },
            "files": files
        }
        data = {
            "id": self.project + '~' + self.branch + '~' + self.data['id'],
            "project": self.project,
            "branch": self.branch,
            "hashtags": [],
            "change_id": self.data['id'],
            "subject": self.subject,
            "status": self.data['status'],
            "created": self.data['createdOn'],
            "updated": self.data['lastUpdated'],
            "_number": self.number,
            "owner": self.data['owner'],
            "labels": labels,
            "current_revision": self.patchsets[-1]['revision'],
            "revisions": revisions,
            "requirements": [],
            "work_in_progresss": self.data.get('wip', False)
        }
        if 'parents' in self.data:
            data['parents'] = self.data['parents']
        return json.loads(json.dumps(data))

    def queryRevisionHTTP(self, revision):
        for ps in self.patchsets:
            if ps['revision'] == revision:
                break
        else:
            return None
        changes = []
        if self.depends_on_change:
            changes.append({
                "commit": {
                    "commit": self.depends_on_change.patchsets[
                        self.depends_on_patchset - 1]['revision'],
                },
                "_change_number": self.depends_on_change.number,
                "_revision_number": self.depends_on_patchset
            })
        for (needed_by_change, needed_by_patchset) in self.needed_by_changes:
            changes.append({
                "commit": {
                    "commit": needed_by_change.patchsets[
                        needed_by_patchset - 1]['revision'],
                },
                "_change_number": needed_by_change.number,
                "_revision_number": needed_by_patchset,
            })
        return {"changes": changes}

    def queryFilesHTTP(self, revision):
        for rev in self.patchsets:
            if rev['revision'] == revision:
                break
        else:
            return None

        files = {}
        for f in rev['files']:
            files[f['file']] = {"status": f['type'][0]}  # ADDED -> A
        return files

    def setMerged(self):
        if (self.depends_on_change and
                self.depends_on_change.data['status'] != 'MERGED'):
            return
        if self.fail_merge:
            return
        self.data['status'] = 'MERGED'
        self.open = False

        path = os.path.join(self.upstream_root, self.project)
        repo = git.Repo(path)

        repo.head.reference = self.branch
        repo.head.reset(working_tree=True)
        repo.git.merge('-s', 'resolve', self.patchsets[-1]['ref'])
        repo.heads[self.branch].commit = repo.head.commit

    def setReported(self):
        self.reported += 1


class GerritWebServer(object):

    def __init__(self, fake_gerrit):
        super(GerritWebServer, self).__init__()
        self.fake_gerrit = fake_gerrit

    def start(self):
        fake_gerrit = self.fake_gerrit

        class Server(http.server.SimpleHTTPRequestHandler):
            log = logging.getLogger("zuul.test.FakeGerritConnection")
            review_re = re.compile('/a/changes/(.*?)/revisions/(.*?)/review')
            submit_re = re.compile('/a/changes/(.*?)/submit')
            pending_checks_re = re.compile(
                r'/a/plugins/checks/checks\.pending/\?'
                r'query=checker:(.*?)\+\(state:(.*?)\)')
            update_checks_re = re.compile(
                r'/a/changes/(.*)/revisions/(.*?)/checks/(.*)')
            list_checkers_re = re.compile('/a/plugins/checks/checkers/')
            change_re = re.compile(r'/a/changes/(.*)\?o=.*')
            related_re = re.compile(r'/a/changes/(.*)/revisions/(.*)/related')
            files_re = re.compile(r'/a/changes/(.*)/revisions/(.*)/files'
                                  r'\?parent=1')
            change_search_re = re.compile(r'/a/changes/\?n=500.*&q=(.*)')
            version_re = re.compile(r'/a/config/server/version')

            def do_POST(self):
                path = self.path
                self.log.debug("Got POST %s", path)

                data = self.rfile.read(int(self.headers['Content-Length']))
                data = json.loads(data.decode('utf-8'))
                self.log.debug("Got data %s", data)

                m = self.review_re.match(path)
                if m:
                    return self.review(m.group(1), m.group(2), data)
                m = self.submit_re.match(path)
                if m:
                    return self.submit(m.group(1), data)
                m = self.update_checks_re.match(path)
                if m:
                    return self.update_checks(
                        m.group(1), m.group(2), m.group(3), data)
                self.send_response(500)
                self.end_headers()

            def do_GET(self):
                path = self.path
                self.log.debug("Got GET %s", path)

                m = self.change_re.match(path)
                if m:
                    return self.get_change(m.group(1))
                m = self.related_re.match(path)
                if m:
                    return self.get_related(m.group(1), m.group(2))
                m = self.files_re.match(path)
                if m:
                    return self.get_files(m.group(1), m.group(2))
                m = self.change_search_re.match(path)
                if m:
                    return self.get_changes(m.group(1))
                m = self.pending_checks_re.match(path)
                if m:
                    return self.get_pending_checks(m.group(1), m.group(2))
                m = self.list_checkers_re.match(path)
                if m:
                    return self.list_checkers()
                m = self.version_re.match(path)
                if m:
                    return self.version()
                self.send_response(500)
                self.end_headers()

            def _404(self):
                self.send_response(404)
                self.end_headers()

            def _get_change(self, change_id):
                change_id = urllib.parse.unquote(change_id)
                project, branch, change = change_id.split('~')
                for c in fake_gerrit.changes.values():
                    if (c.data['id'] == change and
                        c.data['branch'] == branch and
                        c.data['project'] == project):
                        return c

            def review(self, change_id, revision, data):
                change = self._get_change(change_id)
                if not change:
                    return self._404()

                message = data['message']
                b_len = len(message.encode('utf-8'))
                if b_len > gerritconnection.GERRIT_HUMAN_MESSAGE_LIMIT:
                    self.send_response(400, message='Message length exceeded')
                    self.end_headers()
                    return
                labels = data.get('labels', {})
                comments = data.get('robot_comments', data.get('comments', {}))
                tag = data.get('tag', None)
                fake_gerrit._test_handle_review(
                    int(change.data['number']), message, False, labels,
                    comments, tag=tag)
                self.send_response(200)
                self.end_headers()

            def submit(self, change_id, data):
                change = self._get_change(change_id)
                if not change:
                    return self._404()

                message = None
                labels = {}
                fake_gerrit._test_handle_review(
                    int(change.data['number']), message, True, labels)
                self.send_response(200)
                self.end_headers()

            def update_checks(self, change_id, revision, checker, data):
                self.log.debug("Update checks %s %s %s",
                               change_id, revision, checker)
                change = self._get_change(change_id)
                if not change:
                    return self._404()

                change.setCheck(checker, **data)
                self.send_response(200)
                # TODO: return the real data structure, but zuul
                # ignores this now.
                self.end_headers()

            def get_pending_checks(self, checker, state):
                self.log.debug("Get pending checks %s %s", checker, state)
                ret = []
                for c in fake_gerrit.changes.values():
                    if checker not in c.checks:
                        continue
                    patchset_pending_checks = {}
                    if c.checks[checker]['state'] == state:
                        patchset_pending_checks[checker] = {
                            'state': c.checks[checker]['state'],
                        }
                    if patchset_pending_checks:
                        ret.append({
                            'patch_set': {
                                'repository': c.project,
                                'change_number': c.number,
                                'patch_set_id': c.latest_patchset,
                            },
                            'pending_checks': patchset_pending_checks,
                        })
                self.send_data(ret)

            def list_checkers(self):
                self.log.debug("Get checkers")
                self.send_data(fake_gerrit.fake_checkers)

            def get_change(self, number):
                change = fake_gerrit.changes.get(int(number))
                if not change:
                    return self._404()

                self.send_data(change.queryHTTP())
                self.end_headers()

            def get_related(self, number, revision):
                change = fake_gerrit.changes.get(int(number))
                if not change:
                    return self._404()
                data = change.queryRevisionHTTP(revision)
                if data is None:
                    return self._404()
                self.send_data(data)
                self.end_headers()

            def get_files(self, number, revision):
                change = fake_gerrit.changes.get(int(number))
                if not change:
                    return self._404()
                data = change.queryFilesHTTP(revision)
                if data is None:
                    return self._404()
                self.send_data(data)
                self.end_headers()

            def get_changes(self, query):
                self.log.debug("simpleQueryHTTP: %s", query)
                query = urllib.parse.unquote(query)
                fake_gerrit.queries.append(query)
                results = []
                if query.startswith('(') and 'OR' in query:
                    query = query[1:-1]
                    for q in query.split(' OR '):
                        for r in fake_gerrit._simpleQuery(q, http=True):
                            if r not in results:
                                results.append(r)
                else:
                    results = fake_gerrit._simpleQuery(query, http=True)
                self.send_data(results)
                self.end_headers()

            def version(self):
                self.send_data('3.0.0-some-stuff')
                self.end_headers()

            def send_data(self, data):
                data = json.dumps(data).encode('utf-8')
                data = b")]}'\n" + data
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', len(data))
                self.end_headers()
                self.wfile.write(data)

            def log_message(self, fmt, *args):
                self.log.debug(fmt, *args)

        self.httpd = socketserver.ThreadingTCPServer(('', 0), Server)
        self.port = self.httpd.socket.getsockname()[1]
        self.thread = threading.Thread(name='GerritWebServer',
                                       target=self.httpd.serve_forever)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.httpd.shutdown()
        self.thread.join()


class FakeGerritPoller(gerritconnection.GerritPoller):
    """A Fake Gerrit poller for use in tests.

    This subclasses
    :py:class:`~zuul.connection.gerrit.GerritPoller`.
    """

    poll_interval = 1

    def _poll(self, *args, **kw):
        r = super(FakeGerritPoller, self)._poll(*args, **kw)
        # Set the event so tests can confirm that the poller has run
        # after they changed something.
        self.connection._poller_event.set()
        return r


class FakeGerritRefWatcher(gitwatcher.GitWatcher):
    """A Fake Gerrit ref watcher.

    This subclasses
    :py:class:`~zuul.connection.git.GitWatcher`.
    """

    def __init__(self, *args, **kw):
        super(FakeGerritRefWatcher, self).__init__(*args, **kw)
        self.baseurl = self.connection.upstream_root
        self.poll_delay = 1

    def _poll(self, *args, **kw):
        r = super(FakeGerritRefWatcher, self)._poll(*args, **kw)
        # Set the event so tests can confirm that the watcher has run
        # after they changed something.
        self.connection._ref_watcher_event.set()
        return r


class FakeElasticsearchConnection(elconnection.ElasticsearchConnection):

    log = logging.getLogger("zuul.test.FakeElasticsearchConnection")

    def __init__(self, driver, connection_name, connection_config):
        self.driver = driver
        self.connection_name = connection_name
        self.source_it = None

    def add_docs(self, source_it, index):
        self.source_it = source_it
        self.index = index


class FakeGerritConnection(gerritconnection.GerritConnection):
    """A Fake Gerrit connection for use in tests.

    This subclasses
    :py:class:`~zuul.connection.gerrit.GerritConnection` to add the
    ability for tests to add changes to the fake Gerrit it represents.
    """

    log = logging.getLogger("zuul.test.FakeGerritConnection")
    _poller_class = FakeGerritPoller
    _ref_watcher_class = FakeGerritRefWatcher

    def __init__(self, driver, connection_name, connection_config,
                 changes_db=None, upstream_root=None, poller_event=None,
                 ref_watcher_event=None):

        if connection_config.get('password'):
            self.web_server = GerritWebServer(self)
            self.web_server.start()
            url = 'http://localhost:%s' % self.web_server.port
            connection_config['baseurl'] = url
        else:
            self.web_server = None

        super(FakeGerritConnection, self).__init__(driver, connection_name,
                                                   connection_config)

        self.fixture_dir = os.path.join(FIXTURE_DIR, 'gerrit')
        self.change_number = 0
        self.changes = changes_db
        self.queries = []
        self.upstream_root = upstream_root
        self.fake_checkers = []
        self._poller_event = poller_event
        self._ref_watcher_event = ref_watcher_event

    def onStop(self):
        super().onStop()
        if self.web_server:
            self.web_server.stop()

    def addFakeChecker(self, **kw):
        self.fake_checkers.append(kw)

    def addFakeChange(self, project, branch, subject, status='NEW',
                      files=None, parent=None, merge_parents=None,
                      merge_files=None):
        """Add a change to the fake Gerrit."""
        self.change_number += 1
        c = FakeGerritChange(self, self.change_number, project, branch,
                             subject, upstream_root=self.upstream_root,
                             status=status, files=files, parent=parent,
                             merge_parents=merge_parents,
                             merge_files=merge_files)
        self.changes[self.change_number] = c
        return c

    def addFakeTag(self, project, branch, tag):
        path = os.path.join(self.upstream_root, project)
        repo = git.Repo(path)
        commit = repo.heads[branch].commit
        newrev = commit.hexsha
        ref = 'refs/tags/' + tag

        git.Tag.create(repo, tag, commit)

        event = {
            "type": "ref-updated",
            "submitter": {
                "name": "User Name",
            },
            "refUpdate": {
                "oldRev": 40 * '0',
                "newRev": newrev,
                "refName": ref,
                "project": project,
            }
        }
        return event

    def getFakeBranchCreatedEvent(self, project, branch):
        path = os.path.join(self.upstream_root, project)
        repo = git.Repo(path)
        oldrev = 40 * '0'

        event = {
            "type": "ref-updated",
            "submitter": {
                "name": "User Name",
            },
            "refUpdate": {
                "oldRev": oldrev,
                "newRev": repo.heads[branch].commit.hexsha,
                "refName": 'refs/heads/' + branch,
                "project": project,
            }
        }
        return event

    def getFakeBranchDeletedEvent(self, project, branch):
        oldrev = '4abd38457c2da2a72d4d030219ab180ecdb04bf0'
        newrev = 40 * '0'

        event = {
            "type": "ref-updated",
            "submitter": {
                "name": "User Name",
            },
            "refUpdate": {
                "oldRev": oldrev,
                "newRev": newrev,
                "refName": 'refs/heads/' + branch,
                "project": project,
            }
        }
        return event

    def review(self, item, message, submit, labels, checks_api, file_comments,
               zuul_event_id=None):
        if self.web_server:
            return super(FakeGerritConnection, self).review(
                item, message, submit, labels, checks_api, file_comments,
                zuul_event_id)
        self._test_handle_review(int(item.change.number), message, submit,
                                 labels)

    def _test_handle_review(self, change_number, message, submit, labels,
                            file_comments=None, tag=None):
        # Handle a review action from a test
        change = self.changes[change_number]

        # Add the approval back onto the change (ie simulate what gerrit would
        # do).
        # Usually when zuul leaves a review it'll create a feedback loop where
        # zuul's review enters another gerrit event (which is then picked up by
        # zuul). However, we can't mimic this behaviour (by adding this
        # approval event into the queue) as it stops jobs from checking what
        # happens before this event is triggered. If a job needs to see what
        # happens they can add their own verified event into the queue.
        # Nevertheless, we can update change with the new review in gerrit.

        for cat in labels:
            change.addApproval(cat, labels[cat], username=self.user,
                               tag=tag)

        if message:
            change.messages.append(message)

        if file_comments:
            for filename, commentlist in file_comments.items():
                for comment in commentlist:
                    change.addComment(filename, comment['line'],
                                      comment['message'], 'Zuul',
                                      'zuul@example.com', self.user,
                                      comment.get('range'))
        if submit:
            change.setMerged()
        if message:
            change.setReported()

    def queryChangeSSH(self, number, event=None):
        self.log.debug("Query change SSH: %s", number)
        change = self.changes.get(int(number))
        if change:
            return change.query()
        return {}

    def _simpleQuery(self, query, http=False):
        if http:
            def queryMethod(change):
                return change.queryHTTP()
        else:
            def queryMethod(change):
                return change.query()
        # the query can be in parenthesis so strip them if needed
        if query.startswith('('):
            query = query[1:-1]
        if query.startswith('change:'):
            # Query a specific changeid
            changeid = query[len('change:'):]
            l = [queryMethod(change) for change in self.changes.values()
                 if (change.data['id'] == changeid or
                     change.data['number'] == changeid)]
        elif query.startswith('message:'):
            # Query the content of a commit message
            msg = query[len('message:'):].strip()
            # Remove quoting if it is there
            if msg.startswith('{') and msg.endswith('}'):
                msg = msg[1:-1]
            l = [queryMethod(change) for change in self.changes.values()
                 if msg in change.data['commitMessage']]
        elif query.startswith("status:"):
            cut_off_time = 0
            parts = query.split(" ")
            for part in parts:
                if part.startswith("-age"):
                    _, _, age = part.partition(":")
                    cut_off_time = (
                        datetime.datetime.now().timestamp() - float(age[:-1])
                    )
            l = [
                queryMethod(change) for change in self.changes.values()
                if change.data["lastUpdated"] >= cut_off_time
            ]
        else:
            # Query all open changes
            l = [queryMethod(change) for change in self.changes.values()]
        return l

    def simpleQuerySSH(self, query, event=None):
        log = get_annotated_logger(self.log, event)
        log.debug("simpleQuerySSH: %s", query)
        self.queries.append(query)
        results = []
        if query.startswith('(') and 'OR' in query:
            query = query[1:-1]
            for q in query.split(' OR '):
                for r in self._simpleQuery(q):
                    if r not in results:
                        results.append(r)
        else:
            results = self._simpleQuery(query)
        return results

    def _start_watcher_thread(self, *args, **kw):
        pass

    def _uploadPack(self, project):
        ret = ('00a31270149696713ba7e06f1beb760f20d359c4abed HEAD\x00'
               'multi_ack thin-pack side-band side-band-64k ofs-delta '
               'shallow no-progress include-tag multi_ack_detailed no-done\n')
        path = os.path.join(self.upstream_root, project.name)
        repo = git.Repo(path)
        for ref in repo.refs:
            if ref.path.endswith('.lock'):
                # don't treat lockfiles as ref
                continue
            r = ref.object.hexsha + ' ' + ref.path + '\n'
            ret += '%04x%s' % (len(r) + 4, r)
        ret += '0000'
        return ret

    def getGitUrl(self, project):
        return 'file://' + os.path.join(self.upstream_root, project.name)


class PagureChangeReference(git.Reference):
    _common_path_default = "refs/pull"
    _points_to_commits_only = True


class FakePagurePullRequest(object):
    log = logging.getLogger("zuul.test.FakePagurePullRequest")

    def __init__(self, pagure, number, project, branch,
                 subject, upstream_root, files={}, number_of_commits=1,
                 initial_comment=None):
        self.pagure = pagure
        self.source = pagure
        self.number = number
        self.project = project
        self.branch = branch
        self.subject = subject
        self.upstream_root = upstream_root
        self.number_of_commits = 0
        self.status = 'Open'
        self.initial_comment = initial_comment
        self.uuid = uuid.uuid4().hex
        self.comments = []
        self.flags = []
        self.files = {}
        self.tags = []
        self.cached_merge_status = ''
        self.threshold_reached = False
        self.commit_stop = None
        self.commit_start = None
        self.threshold_reached = False
        self.upstream_root = upstream_root
        self.cached_merge_status = 'MERGE'
        self.url = "https://%s/%s/pull-request/%s" % (
            self.pagure.server, self.project, self.number)
        self.is_merged = False
        self.pr_ref = self._createPRRef()
        self._addCommitInPR(files=files)
        self._updateTimeStamp()

    def _getPullRequestEvent(self, action, pull_data_field='pullrequest'):
        name = 'pg_pull_request'
        data = {
            'msg': {
                pull_data_field: {
                    'branch': self.branch,
                    'comments': self.comments,
                    'commit_start': self.commit_start,
                    'commit_stop': self.commit_stop,
                    'date_created': '0',
                    'tags': self.tags,
                    'initial_comment': self.initial_comment,
                    'id': self.number,
                    'project': {
                        'fullname': self.project,
                    },
                    'status': self.status,
                    'subject': self.subject,
                    'uid': self.uuid,
                }
            },
            'msg_id': str(uuid.uuid4()),
            'timestamp': 1427459070,
            'topic': action
        }
        if action == 'pull-request.flag.added':
            data['msg']['flag'] = self.flags[0]
        if action == 'pull-request.tag.added':
            data['msg']['tags'] = self.tags
        return (name, data)

    def getPullRequestOpenedEvent(self):
        return self._getPullRequestEvent('pull-request.new')

    def getPullRequestClosedEvent(self, merged=True):
        if merged:
            self.is_merged = True
            self.status = 'Merged'
        else:
            self.is_merged = False
            self.status = 'Closed'
        return self._getPullRequestEvent('pull-request.closed')

    def getPullRequestUpdatedEvent(self):
        self._addCommitInPR()
        self.addComment(
            "**1 new commit added**\n\n * ``Bump``\n",
            True)
        return self._getPullRequestEvent('pull-request.comment.added')

    def getPullRequestCommentedEvent(self, message):
        self.addComment(message)
        return self._getPullRequestEvent('pull-request.comment.added')

    def getPullRequestInitialCommentEvent(self, message):
        self.initial_comment = message
        self._updateTimeStamp()
        return self._getPullRequestEvent('pull-request.initial_comment.edited')

    def getPullRequestTagAddedEvent(self, tags, reset=True):
        if reset:
            self.tags = []
        _tags = set(self.tags)
        _tags.update(set(tags))
        self.tags = list(_tags)
        self.addComment(
            "**Metadata Update from @pingou**:\n- " +
            "Pull-request tagged with: %s" % ', '.join(tags),
            True)
        self._updateTimeStamp()
        return self._getPullRequestEvent(
            'pull-request.tag.added', pull_data_field='pull_request')

    def getPullRequestStatusSetEvent(self, status, username="zuul"):
        self.addFlag(
            status, "https://url", "Build %s" % status, username)
        return self._getPullRequestEvent('pull-request.flag.added')

    def insertFlag(self, flag):
        to_pop = None
        for i, _flag in enumerate(self.flags):
            if _flag['uid'] == flag['uid']:
                to_pop = i
        if to_pop is not None:
            self.flags.pop(to_pop)
        self.flags.insert(0, flag)

    def addFlag(self, status, url, comment, username="zuul"):
        flag_uid = "%s-%s-%s" % (username, self.number, self.project)
        flag = {
            "username": "Zuul CI",
            "user": {
                "name": username
            },
            "uid": flag_uid[:32],
            "comment": comment,
            "status": status,
            "url": url
        }
        self.insertFlag(flag)
        self._updateTimeStamp()

    def editInitialComment(self, initial_comment):
        self.initial_comment = initial_comment
        self._updateTimeStamp()

    def addComment(self, message, notification=False, fullname=None):
        self.comments.append({
            'comment': message,
            'notification': notification,
            'date_created': str(int(time.time())),
            'user': {
                'fullname': fullname or 'Pingou'
            }}
        )
        self._updateTimeStamp()

    def getPRReference(self):
        return '%s/head' % self.number

    def _getRepo(self):
        repo_path = os.path.join(self.upstream_root, self.project)
        return git.Repo(repo_path)

    def _createPRRef(self):
        repo = self._getRepo()
        return PagureChangeReference.create(
            repo, self.getPRReference(), 'refs/tags/init')

    def addCommit(self, files={}):
        """Adds a commit on top of the actual PR head."""
        self._addCommitInPR(files=files)
        self._updateTimeStamp()

    def forcePush(self, files={}):
        """Clears actual commits and add a commit on top of the base."""
        self._addCommitInPR(files=files, reset=True)
        self._updateTimeStamp()

    def _addCommitInPR(self, files={}, reset=False):
        repo = self._getRepo()
        ref = repo.references[self.getPRReference()]
        if reset:
            self.number_of_commits = 0
            ref.set_object('refs/tags/init')
        self.number_of_commits += 1
        repo.head.reference = ref
        repo.git.clean('-x', '-f', '-d')

        if files:
            self.files = files
        else:
            fn = '%s-%s' % (self.branch.replace('/', '_'), self.number)
            self.files = {fn: "test %s %s\n" % (self.branch, self.number)}
        msg = self.subject + '-' + str(self.number_of_commits)
        for fn, content in self.files.items():
            fn = os.path.join(repo.working_dir, fn)
            with open(fn, 'w') as f:
                f.write(content)
            repo.index.add([fn])

        self.commit_stop = repo.index.commit(msg).hexsha
        if not self.commit_start:
            self.commit_start = self.commit_stop

        repo.create_head(self.getPRReference(), self.commit_stop, force=True)
        self.pr_ref.set_commit(self.commit_stop)
        repo.head.reference = 'master'
        repo.git.clean('-x', '-f', '-d')
        repo.heads['master'].checkout()

    def _updateTimeStamp(self):
        self.last_updated = str(int(time.time()))


class FakePagureAPIClient(pagureconnection.PagureAPIClient):
    log = logging.getLogger("zuul.test.FakePagureAPIClient")

    def __init__(self, baseurl, api_token, project,
                 pull_requests_db={}):
        super(FakePagureAPIClient, self).__init__(
            baseurl, api_token, project)
        self.session = None
        self.pull_requests = pull_requests_db
        self.return_post_error = None

    def gen_error(self, verb, custom_only=False):
        if verb == 'POST' and self.return_post_error:
            return {
                'error': self.return_post_error['error'],
                'error_code': self.return_post_error['error_code']
            }, 401, "", 'POST'
            self.return_post_error = None
        if not custom_only:
            return {
                'error': 'some error',
                'error_code': 'some error code'
            }, 503, "", verb

    def _get_pr(self, match):
        project, number = match.groups()
        pr = self.pull_requests.get(project, {}).get(number)
        if not pr:
            return self.gen_error("GET")
        return pr

    def get(self, url):
        self.log.debug("Getting resource %s ..." % url)

        match = re.match(r'.+/api/0/(.+)/pull-request/(\d+)$', url)
        if match:
            pr = self._get_pr(match)
            return {
                'branch': pr.branch,
                'subject': pr.subject,
                'status': pr.status,
                'initial_comment': pr.initial_comment,
                'last_updated': pr.last_updated,
                'comments': pr.comments,
                'commit_stop': pr.commit_stop,
                'threshold_reached': pr.threshold_reached,
                'cached_merge_status': pr.cached_merge_status,
                'tags': pr.tags,
            }, 200, "", "GET"

        match = re.match(r'.+/api/0/(.+)/pull-request/(\d+)/flag$', url)
        if match:
            pr = self._get_pr(match)
            return {'flags': pr.flags}, 200, "", "GET"

        match = re.match('.+/api/0/(.+)/git/branches$', url)
        if match:
            # project = match.groups()[0]
            return {'branches': ['master']}, 200, "", "GET"

        match = re.match(r'.+/api/0/(.+)/pull-request/(\d+)/diffstats$', url)
        if match:
            pr = self._get_pr(match)
            return pr.files, 200, "", "GET"

    def post(self, url, params=None):

        self.log.info(
            "Posting on resource %s, params (%s) ..." % (url, params))

        # Will only match if return_post_error is set
        err = self.gen_error("POST", custom_only=True)
        if err:
            return err

        match = re.match(r'.+/api/0/(.+)/pull-request/(\d+)/merge$', url)
        if match:
            pr = self._get_pr(match)
            pr.status = 'Merged'
            pr.is_merged = True
            return {}, 200, "", "POST"

        match = re.match(r'.+/api/0/-/whoami$', url)
        if match:
            return {"username": "zuul"}, 200, "", "POST"

        if not params:
            return self.gen_error("POST")

        match = re.match(r'.+/api/0/(.+)/pull-request/(\d+)/flag$', url)
        if match:
            pr = self._get_pr(match)
            params['user'] = {"name": "zuul"}
            pr.insertFlag(params)

        match = re.match(r'.+/api/0/(.+)/pull-request/(\d+)/comment$', url)
        if match:
            pr = self._get_pr(match)
            pr.addComment(params['comment'])

        return {}, 200, "", "POST"


class FakePagureConnection(pagureconnection.PagureConnection):
    log = logging.getLogger("zuul.test.FakePagureConnection")

    def __init__(self, driver, connection_name, connection_config, rpcclient,
                 changes_db=None, upstream_root=None):
        super(FakePagureConnection, self).__init__(driver, connection_name,
                                                   connection_config)
        self.connection_name = connection_name
        self.pr_number = 0
        self.pull_requests = changes_db
        self.statuses = {}
        self.upstream_root = upstream_root
        self.reports = []
        self.rpcclient = rpcclient
        self.cloneurl = self.upstream_root

    def get_project_api_client(self, project):
        client = FakePagureAPIClient(
            self.baseurl, None, project,
            pull_requests_db=self.pull_requests)
        if not self.username:
            self.set_my_username(client)
        return client

    def get_project_webhook_token(self, project):
        return 'fake_webhook_token-%s' % project

    def emitEvent(self, event, use_zuulweb=False, project=None,
                  wrong_token=False):
        name, payload = event
        if use_zuulweb:
            if not wrong_token:
                secret = 'fake_webhook_token-%s' % project
            else:
                secret = ''
            payload = json.dumps(payload).encode('utf-8')
            signature, _ = pagureconnection._sign_request(payload, secret)
            headers = {'x-pagure-signature': signature,
                       'x-pagure-project': project}
            return requests.post(
                'http://127.0.0.1:%s/api/connection/%s/payload'
                % (self.zuul_web_port, self.connection_name),
                data=payload, headers=headers)
        else:
            data = {'payload': payload}
            self.event_queue.put(data)
            return data

    def openFakePullRequest(self, project, branch, subject, files=[],
                            initial_comment=None):
        self.pr_number += 1
        pull_request = FakePagurePullRequest(
            self, self.pr_number, project, branch, subject, self.upstream_root,
            files=files, initial_comment=initial_comment)
        self.pull_requests.setdefault(
            project, {})[str(self.pr_number)] = pull_request
        return pull_request

    def getGitReceiveEvent(self, project):
        name = 'pg_push'
        repo_path = os.path.join(self.upstream_root, project)
        repo = git.Repo(repo_path)
        headsha = repo.head.commit.hexsha
        data = {
            'msg': {
                'project_fullname': project,
                'branch': 'master',
                'end_commit': headsha,
                'old_commit': '1' * 40,
            },
            'msg_id': str(uuid.uuid4()),
            'timestamp': 1427459070,
            'topic': 'git.receive',
        }
        return (name, data)

    def getGitTagCreatedEvent(self, project, tag, rev):
        name = 'pg_push'
        data = {
            'msg': {
                'project_fullname': project,
                'tag': tag,
                'rev': rev
            },
            'msg_id': str(uuid.uuid4()),
            'timestamp': 1427459070,
            'topic': 'git.tag.creation',
        }
        return (name, data)

    def getGitBranchEvent(self, project, branch, type, rev):
        name = 'pg_push'
        data = {
            'msg': {
                'project_fullname': project,
                'branch': branch,
                'rev': rev,
            },
            'msg_id': str(uuid.uuid4()),
            'timestamp': 1427459070,
            'topic': 'git.branch.%s' % type,
        }
        return (name, data)

    def setZuulWebPort(self, port):
        self.zuul_web_port = port


FakeGitlabBranch = namedtuple('Branch', ('name', 'protected'))


class FakeGitlabConnection(gitlabconnection.GitlabConnection):
    log = logging.getLogger("zuul.test.FakeGitlabConnection")

    def __init__(self, driver, connection_name, connection_config, rpcclient,
                 changes_db=None, upstream_root=None):
        self.merge_requests = changes_db
        self.rpcclient = rpcclient
        self.upstream_root = upstream_root
        self.mr_number = 0

        self._test_web_server = tests.fakegitlab.GitlabWebServer(changes_db)
        self._test_web_server.start()
        self._test_baseurl = 'http://localhost:%s' % self._test_web_server.port
        connection_config['baseurl'] = self._test_baseurl

        super(FakeGitlabConnection, self).__init__(driver, connection_name,
                                                   connection_config)

    def onStop(self):
        super().onStop()
        self._test_web_server.stop()

    def addProject(self, project):
        super(FakeGitlabConnection, self).addProject(project)
        self.addProjectByName(project.name)

    def addProjectByName(self, project_name):
        owner, proj = project_name.split('/')
        repo = self._test_web_server.fake_repos[(owner, proj)]
        branch = FakeGitlabBranch('master', False)
        if 'master' not in repo:
            repo.append(branch)

    def protectBranch(self, owner, project, branch, protected=True):
        if branch in self._test_web_server.fake_repos[(owner, project)]:
            del self._test_web_server.fake_repos[(owner, project)][branch]
        fake_branch = FakeGitlabBranch(branch, protected=protected)
        self._test_web_server.fake_repos[(owner, project)].append(fake_branch)

    def deleteBranch(self, owner, project, branch):
        if branch in self._test_web_server.fake_repos[(owner, project)]:
            del self._test_web_server.fake_repos[(owner, project)][branch]

    def getGitUrl(self, project):
        return 'file://' + os.path.join(self.upstream_root, project.name)

    def real_getGitUrl(self, project):
        return super(FakeGitlabConnection, self).getGitUrl(project)

    def openFakeMergeRequest(self, project,
                             branch, title, description='', files=[]):
        self.mr_number += 1
        merge_request = FakeGitlabMergeRequest(
            self, self.mr_number, project, branch, title, self.upstream_root,
            files=files, description=description)
        self.merge_requests.setdefault(
            project, {})[str(self.mr_number)] = merge_request
        return merge_request

    def emitEvent(self, event, use_zuulweb=False, project=None):
        name, payload = event
        if use_zuulweb:
            payload = json.dumps(payload).encode('utf-8')
            headers = {'x-gitlab-token': self.webhook_token}
            return requests.post(
                'http://127.0.0.1:%s/api/connection/%s/payload'
                % (self.zuul_web_port, self.connection_name),
                data=payload, headers=headers)
        else:
            data = {'payload': payload}
            self.event_queue.put(data)
            return data

    def setZuulWebPort(self, port):
        self.zuul_web_port = port

    def getPushEvent(
            self, project, before=None, after=None,
            branch='refs/heads/master'):
        name = 'gl_push'
        if not after:
            repo_path = os.path.join(self.upstream_root, project)
            repo = git.Repo(repo_path)
            after = repo.head.commit.hexsha
        data = {
            'object_kind': 'push',
            'before': before or '1' * 40,
            'after': after,
            'ref': branch,
            'project': {
                'path_with_namespace': project
            },
        }
        return (name, data)

    def getGitTagEvent(self, project, tag, sha):
        name = 'gl_push'
        data = {
            'object_kind': 'tag_push',
            'before': '0' * 40,
            'after': sha,
            'ref': 'refs/tags/%s' % tag,
            'project': {
                'path_with_namespace': project
            },
        }
        return (name, data)

    @contextmanager
    def enable_community_edition(self):
        self._test_web_server.options['community_edition'] = True
        yield
        self._test_web_server.options['community_edition'] = False


class GitlabChangeReference(git.Reference):
    _common_path_default = "refs/merge-requests"
    _points_to_commits_only = True


class FakeGitlabMergeRequest(object):
    log = logging.getLogger("zuul.test.FakeGitlabMergeRequest")

    def __init__(self, gitlab, number, project, branch,
                 subject, upstream_root, files=[], description=''):
        self.gitlab = gitlab
        self.source = gitlab
        self.number = number
        self.project = project
        self.branch = branch
        self.subject = subject
        self.description = description
        self.upstream_root = upstream_root
        self.number_of_commits = 0
        self.created_at = datetime.datetime.now(datetime.timezone.utc)
        self.updated_at = self.created_at
        self.merged_at = None
        self.sha = None
        self.state = 'opened'
        self.is_merged = False
        self.merge_status = 'can_be_merged'
        self.labels = []
        self.notes = []
        self.url = "https://%s/%s/merge_requests/%s" % (
            self.gitlab.server, self.project, self.number)
        self.approved = False
        self.mr_ref = self._createMRRef()
        self._addCommitInMR(files=files)

    def _getRepo(self):
        repo_path = os.path.join(self.upstream_root, self.project)
        return git.Repo(repo_path)

    def _createMRRef(self):
        repo = self._getRepo()
        return GitlabChangeReference.create(
            repo, self.getMRReference(), 'refs/tags/init')

    def getMRReference(self):
        return '%s/head' % self.number

    def addNote(self, body):
        self.notes.append(
            {
                "body": body,
                "created_at": datetime.datetime.now(datetime.timezone.utc),
            }
        )

    def addCommit(self, files=[]):
        self._addCommitInMR(files=files)
        self._updateTimeStamp()

    def closeMergeRequest(self):
        self.state = 'closed'
        self._updateTimeStamp()

    def mergeMergeRequest(self):
        self.state = 'merged'
        self.is_merged = True
        self._updateTimeStamp()
        self.merged_at = self.updated_at

    def reopenMergeRequest(self):
        self.state = 'opened'
        self._updateTimeStamp()
        self.merged_at = None

    def _addCommitInMR(self, files=[], reset=False):
        repo = self._getRepo()
        ref = repo.references[self.getMRReference()]
        if reset:
            self.number_of_commits = 0
            ref.set_object('refs/tags/init')
        self.number_of_commits += 1
        repo.head.reference = ref
        repo.git.clean('-x', '-f', '-d')

        if files:
            self.files = files
        else:
            fn = '%s-%s' % (self.branch.replace('/', '_'), self.number)
            self.files = {fn: "test %s %s\n" % (self.branch, self.number)}
        msg = self.subject + '-' + str(self.number_of_commits)
        for fn, content in self.files.items():
            fn = os.path.join(repo.working_dir, fn)
            with open(fn, 'w') as f:
                f.write(content)
            repo.index.add([fn])

        self.sha = repo.index.commit(msg).hexsha

        repo.create_head(self.getMRReference(), self.sha, force=True)
        self.mr_ref.set_commit(self.sha)
        repo.head.reference = 'master'
        repo.git.clean('-x', '-f', '-d')
        repo.heads['master'].checkout()

    def _updateTimeStamp(self):
        self.updated_at = datetime.datetime.now(datetime.timezone.utc)

    def getMergeRequestEvent(self, action, include_labels=False):
        name = 'gl_merge_request'
        data = {
            'object_kind': 'merge_request',
            'project': {
                'path_with_namespace': self.project
            },
            'object_attributes': {
                'title': self.subject,
                'created_at': self.created_at.strftime(
                    '%Y-%m-%d %H:%M:%S.%f%z'),
                'updated_at': self.updated_at.strftime(
                    '%Y-%m-%d %H:%M:%S UTC'),
                'iid': self.number,
                'target_branch': self.branch,
                'last_commit': {'id': self.sha},
                'action': action
            },
        }
        data['labels'] = [{'title': label} for label in self.labels]
        data['changes'] = {}

        if include_labels:
            data['changes']['labels'] = {
                'previous': [],
                'current': data['labels']
            }
        return (name, data)

    def getMergeRequestOpenedEvent(self):
        return self.getMergeRequestEvent(action='open')

    def getMergeRequestUpdatedEvent(self):
        self.addCommit()
        return self.getMergeRequestEvent(action='update')

    def getMergeRequestMergedEvent(self):
        self.mergeMergeRequest()
        return self.getMergeRequestEvent(action='merge')

    def getMergeRequestApprovedEvent(self):
        self.approved = True
        return self.getMergeRequestEvent(action='approved')

    def getMergeRequestUnapprovedEvent(self):
        self.approved = False
        return self.getMergeRequestEvent(action='unapproved')

    def getMergeRequestLabeledEvent(self, labels):
        self.labels = labels
        return self.getMergeRequestEvent(action='update', include_labels=True)

    def getMergeRequestCommentedEvent(self, note):
        self.addNote(note)
        note_date = self.notes[-1]['created_at'].strftime(
            '%Y-%m-%d %H:%M:%S UTC')
        name = 'gl_merge_request'
        data = {
            'object_kind': 'note',
            'project': {
                'path_with_namespace': self.project
            },
            'merge_request': {
                'title': self.subject,
                'iid': self.number,
                'target_branch': self.branch,
                'last_commit': {'id': self.sha}
            },
            'object_attributes': {
                'created_at': note_date,
                'updated_at': note_date,
                'note': self.notes[-1]['body'],
            },
        }
        return (name, data)


class GithubChangeReference(git.Reference):
    _common_path_default = "refs/pull"
    _points_to_commits_only = True


class FakeGithubPullRequest(object):

    def __init__(self, github, number, project, branch,
                 subject, upstream_root, files=[], number_of_commits=1,
                 writers=[], body=None, body_text=None, draft=False,
                 base_sha=None):
        """Creates a new PR with several commits.
        Sends an event about opened PR."""
        self.github = github
        self.source = github
        self.number = number
        self.project = project
        self.branch = branch
        self.subject = subject
        self.body = body
        self.body_text = body_text
        self.draft = draft
        self.number_of_commits = 0
        self.upstream_root = upstream_root
        self.files = []
        self.comments = []
        self.labels = []
        self.statuses = {}
        self.reviews = []
        self.writers = []
        self.admins = []
        self.updated_at = None
        self.head_sha = None
        self.is_merged = False
        self.merge_message = None
        self.state = 'open'
        self.url = 'https://%s/%s/pull/%s' % (github.server, project, number)
        self._createPRRef(base_sha=base_sha)
        self._addCommitToRepo(files=files)
        self._updateTimeStamp()

    def addCommit(self, files=[]):
        """Adds a commit on top of the actual PR head."""
        self._addCommitToRepo(files=files)
        self._updateTimeStamp()

    def forcePush(self, files=[]):
        """Clears actual commits and add a commit on top of the base."""
        self._addCommitToRepo(files=files, reset=True)
        self._updateTimeStamp()

    def getPullRequestOpenedEvent(self):
        return self._getPullRequestEvent('opened')

    def getPullRequestSynchronizeEvent(self):
        return self._getPullRequestEvent('synchronize')

    def getPullRequestReopenedEvent(self):
        return self._getPullRequestEvent('reopened')

    def getPullRequestClosedEvent(self):
        return self._getPullRequestEvent('closed')

    def getPullRequestEditedEvent(self, old_body=None):
        return self._getPullRequestEvent('edited', old_body)

    def addComment(self, message):
        self.comments.append(message)
        self._updateTimeStamp()

    def getIssueCommentAddedEvent(self, text):
        name = 'issue_comment'
        data = {
            'action': 'created',
            'issue': {
                'number': self.number
            },
            'comment': {
                'body': text
            },
            'repository': {
                'full_name': self.project
            },
            'sender': {
                'login': 'ghuser'
            }
        }
        return (name, data)

    def getCommentAddedEvent(self, text):
        name, data = self.getIssueCommentAddedEvent(text)
        # A PR comment has an additional 'pull_request' key in the issue data
        data['issue']['pull_request'] = {
            'url': 'http://%s/api/v3/repos/%s/pull/%s' % (
                self.github.server, self.project, self.number)
        }
        return (name, data)

    def getReviewAddedEvent(self, review):
        name = 'pull_request_review'
        data = {
            'action': 'submitted',
            'pull_request': {
                'number': self.number,
                'title': self.subject,
                'updated_at': self.updated_at,
                'base': {
                    'ref': self.branch,
                    'repo': {
                        'full_name': self.project
                    }
                },
                'head': {
                    'sha': self.head_sha
                }
            },
            'review': {
                'state': review
            },
            'repository': {
                'full_name': self.project
            },
            'sender': {
                'login': 'ghuser'
            }
        }
        return (name, data)

    def addLabel(self, name):
        if name not in self.labels:
            self.labels.append(name)
            self._updateTimeStamp()
            return self._getLabelEvent(name)

    def removeLabel(self, name):
        if name in self.labels:
            self.labels.remove(name)
            self._updateTimeStamp()
            return self._getUnlabelEvent(name)

    def _getLabelEvent(self, label):
        name = 'pull_request'
        data = {
            'action': 'labeled',
            'pull_request': {
                'number': self.number,
                'updated_at': self.updated_at,
                'base': {
                    'ref': self.branch,
                    'repo': {
                        'full_name': self.project
                    }
                },
                'head': {
                    'sha': self.head_sha
                }
            },
            'label': {
                'name': label
            },
            'sender': {
                'login': 'ghuser'
            }
        }
        return (name, data)

    def _getUnlabelEvent(self, label):
        name = 'pull_request'
        data = {
            'action': 'unlabeled',
            'pull_request': {
                'number': self.number,
                'title': self.subject,
                'updated_at': self.updated_at,
                'base': {
                    'ref': self.branch,
                    'repo': {
                        'full_name': self.project
                    }
                },
                'head': {
                    'sha': self.head_sha,
                    'repo': {
                        'full_name': self.project
                    }
                }
            },
            'label': {
                'name': label
            },
            'sender': {
                'login': 'ghuser'
            }
        }
        return (name, data)

    def editBody(self, body):
        old_body = self.body
        self.body = body
        self._updateTimeStamp()
        return self.getPullRequestEditedEvent(old_body=old_body)

    def _getRepo(self):
        repo_path = os.path.join(self.upstream_root, self.project)
        return git.Repo(repo_path)

    def _createPRRef(self, base_sha=None):
        base_sha = base_sha or 'refs/tags/init'
        repo = self._getRepo()
        GithubChangeReference.create(
            repo, self.getPRReference(), base_sha)

    def _addCommitToRepo(self, files=[], reset=False):
        repo = self._getRepo()
        ref = repo.references[self.getPRReference()]
        if reset:
            self.number_of_commits = 0
            ref.set_object('refs/tags/init')
        self.number_of_commits += 1
        repo.head.reference = ref
        repo.head.reset(working_tree=True)
        repo.git.clean('-x', '-f', '-d')

        if files:
            self.files = files
        else:
            fn = '%s-%s' % (self.branch.replace('/', '_'), self.number)
            self.files = {fn: "test %s %s\n" % (self.branch, self.number)}
        msg = self.subject + '-' + str(self.number_of_commits)
        for fn, content in self.files.items():
            fn = os.path.join(repo.working_dir, fn)
            with open(fn, 'w') as f:
                f.write(content)
            repo.index.add([fn])

        self.head_sha = repo.index.commit(msg).hexsha
        repo.create_head(self.getPRReference(), self.head_sha, force=True)
        # Create an empty set of statuses for the given sha,
        # each sha on a PR may have a status set on it
        self.statuses[self.head_sha] = []
        repo.head.reference = 'master'
        repo.head.reset(working_tree=True)
        repo.git.clean('-x', '-f', '-d')
        repo.heads['master'].checkout()

    def _updateTimeStamp(self):
        self.updated_at = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.localtime())

    def getPRHeadSha(self):
        repo = self._getRepo()
        return repo.references[self.getPRReference()].commit.hexsha

    def addReview(self, user, state, granted_on=None):
        gh_time_format = '%Y-%m-%dT%H:%M:%SZ'
        # convert the timestamp to a str format that would be returned
        # from github as 'submitted_at' in the API response

        if granted_on:
            granted_on = datetime.datetime.utcfromtimestamp(granted_on)
            submitted_at = time.strftime(
                gh_time_format, granted_on.timetuple())
        else:
            # github timestamps only down to the second, so we need to make
            # sure reviews that tests add appear to be added over a period of
            # time in the past and not all at once.
            if not self.reviews:
                # the first review happens 10 mins ago
                offset = 600
            else:
                # subsequent reviews happen 1 minute closer to now
                offset = 600 - (len(self.reviews) * 60)

            granted_on = datetime.datetime.utcfromtimestamp(
                time.time() - offset)
            submitted_at = time.strftime(
                gh_time_format, granted_on.timetuple())

        self.reviews.append(tests.fakegithub.FakeGHReview({
            'state': state,
            'user': {
                'login': user,
                'email': user + "@example.com",
            },
            'submitted_at': submitted_at,
        }))

    def getPRReference(self):
        return '%s/head' % self.number

    def _getPullRequestEvent(self, action, old_body=None):
        name = 'pull_request'
        data = {
            'action': action,
            'number': self.number,
            'pull_request': {
                'number': self.number,
                'title': self.subject,
                'updated_at': self.updated_at,
                'base': {
                    'ref': self.branch,
                    'repo': {
                        'full_name': self.project
                    }
                },
                'head': {
                    'sha': self.head_sha,
                    'repo': {
                        'full_name': self.project
                    }
                },
                'body': self.body
            },
            'sender': {
                'login': 'ghuser'
            },
            'repository': {
                'full_name': self.project,
            },
            'installation': {
                'id': 123,
            },
            'changes': {},
            'labels': [{'name': l} for l in self.labels]
        }
        if old_body:
            data['changes']['body'] = {'from': old_body}
        return (name, data)

    def getCommitStatusEvent(self, context, state='success', user='zuul'):
        name = 'status'
        data = {
            'state': state,
            'sha': self.head_sha,
            'name': self.project,
            'description': 'Test results for %s: %s' % (self.head_sha, state),
            'target_url': 'http://zuul/%s' % self.head_sha,
            'branches': [],
            'context': context,
            'sender': {
                'login': user
            }
        }
        return (name, data)

    def getCheckRunRequestedEvent(self, cr_name, app="zuul"):
        name = "check_run"
        data = {
            "action": "rerequested",
            "check_run": {
                "head_sha": self.head_sha,
                "name": cr_name,
                "app": {
                    "slug": app,
                },
            },
            "repository": {
                "full_name": self.project,
            },
        }
        return (name, data)

    def getCheckRunAbortEvent(self, check_run):
        # A check run aborted event can only be created from a FakeCheckRun as
        # we need some information like external_id which is "calculated"
        # during the creation of the check run.
        name = "check_run"
        data = {
            "action": "requested_action",
            "requested_action": {
                "identifier": "abort",
            },
            "check_run": {
                "head_sha": self.head_sha,
                "name": check_run["name"],
                "app": {
                    "slug": check_run["app"]
                },
                "external_id": check_run["external_id"],
            },
            "repository": {
                "full_name": self.project,
            },
        }

        return (name, data)

    def setMerged(self, commit_message):
        self.is_merged = True
        self.merge_message = commit_message

        repo = self._getRepo()
        repo.heads[self.branch].commit = repo.commit(self.head_sha)


class FakeGithubClientManager(GithubClientManager):
    github_class = tests.fakegithub.FakeGithubClient
    github_enterprise_class = tests.fakegithub.FakeGithubEnterpriseClient

    log = logging.getLogger("zuul.test.FakeGithubClientManager")

    def __init__(self, connection_config):
        super().__init__(connection_config)
        self.record_clients = False
        self.recorded_clients = []
        self.github_data = None

    def getGithubClient(self,
                        project_name=None,
                        zuul_event_id=None):
        client = super().getGithubClient(
            project_name=project_name,
            zuul_event_id=zuul_event_id)

        # Some tests expect the installation id as part of the
        if self.app_id:
            inst_id = self.installation_map.get(project_name)
            client.setInstId(inst_id)

        # The super method creates a fake github client with empty data so
        # add it here.
        client.setData(self.github_data)

        if self.record_clients:
            self.recorded_clients.append(client)
        return client

    def _prime_installation_map(self):
        # Only valid if installed as a github app
        if not self.app_id:
            return

        # github_data.repos is a hash like
        # { ('org', 'project1'): <dataobj>
        #   ('org', 'project2'): <dataobj>,
        #   ('org2', 'project1'): <dataobj>, ... }
        #
        # we don't care about the value. index by org, e.g.
        #
        #  {
        #    'org': ('project1', 'project2')
        #    'org2': ('project1', 'project2')
        #  }
        orgs = defaultdict(list)
        project_id = 1
        for org, project in self.github_data.repos:
            # Each entry is in the format for "repositories" response
            # of GET /installation/repositories
            orgs[org].append({
                'id': project_id,
                'name': project,
                'full_name': '%s/%s' % (org, project)
                # note, lots of other stuff that's not relevant
            })
            project_id += 1

        self.log.debug("GitHub installation mapped to: %s" % orgs)

        # Mock response to GET /app/installations
        app_json = []
        app_projects = []
        app_id = 1

        # Ensure that we ignore suspended apps
        app_json.append(
            {
                'id': app_id,
                'suspended_at': '2021-09-23T01:43:44Z',
                'suspended_by': {
                    'login': 'ianw',
                    'type': 'User',
                    'id': 12345
                }
            })
        app_projects.append([])
        app_id += 1

        for org, projects in orgs.items():
            # We respond as if each org is a different app instance
            #
            # Below we will be sent the app_id in a token to query
            # what projects this app exports.  Keep the projects in a
            # sequential list so we can just look up "projects for app
            # X" == app_projects[X]
            app_projects.append(projects)
            app_json.append(
                {
                    'id': app_id,
                    # Acutally none of this matters, and there's lots
                    # more in a real response.  Padded out just for
                    # example sake.
                    'account': {
                        'login': org,
                        'id': 1234,
                        'type': 'User',
                    },
                    'permissions': {
                        'checks': 'write',
                        'metadata': 'read',
                        'contents': 'read'
                    },
                    'events': ['push',
                               'pull_request'
                               ],
                    'suspended_at': None,
                    'suspended_by': None,
                }
            )
            app_id += 1

        # TODO(ianw) : we could exercise the pagination paths ...
        with requests_mock.Mocker() as m:
            m.get('%s/app/installations' % self.base_url, json=app_json)

            def repositories_callback(request, context):
                # FakeGithubSession gives us an auth token "token
                # token-X" where "X" corresponds to the app id we want
                # the projects for.  apps start at id "1", so the projects
                # to return for this call are app_projects[token-1]
                token = int(request.headers['Authorization'][12:])
                projects = app_projects[token - 1]
                return {
                    'total_count': len(projects),
                    'repositories': projects
                }
            m.get('%s/installation/repositories?per_page=100' % self.base_url,
                  json=repositories_callback)

            # everything mocked now, call real implementation
            super()._prime_installation_map()


class FakeGithubConnection(githubconnection.GithubConnection):
    log = logging.getLogger("zuul.test.FakeGithubConnection")
    client_manager_class = FakeGithubClientManager

    def __init__(self, driver, connection_name, connection_config, rpcclient,
                 changes_db=None, upstream_root=None, git_url_with_auth=False):
        super(FakeGithubConnection, self).__init__(driver, connection_name,
                                                   connection_config)
        self.connection_name = connection_name
        self.pr_number = 0
        self.pull_requests = changes_db
        self.statuses = {}
        self.upstream_root = upstream_root
        self.merge_failure = False
        self.merge_not_allowed_count = 0

        self.github_data = tests.fakegithub.FakeGithubData(changes_db)
        self._github_client_manager.github_data = self.github_data

        self.git_url_with_auth = git_url_with_auth
        self.rpcclient = rpcclient

    def setZuulWebPort(self, port):
        self.zuul_web_port = port

    def openFakePullRequest(self, project, branch, subject, files=[],
                            body=None, body_text=None, draft=False,
                            base_sha=None):
        self.pr_number += 1
        pull_request = FakeGithubPullRequest(
            self, self.pr_number, project, branch, subject, self.upstream_root,
            files=files, body=body, body_text=body_text, draft=draft,
            base_sha=base_sha)
        self.pull_requests[self.pr_number] = pull_request
        return pull_request

    def getPushEvent(self, project, ref, old_rev=None, new_rev=None,
                     added_files=None, removed_files=None,
                     modified_files=None):
        if added_files is None:
            added_files = []
        if removed_files is None:
            removed_files = []
        if modified_files is None:
            modified_files = []
        if not old_rev:
            old_rev = '0' * 40
        if not new_rev:
            new_rev = random_sha1()
        name = 'push'
        data = {
            'ref': ref,
            'before': old_rev,
            'after': new_rev,
            'repository': {
                'full_name': project
            },
            'commits': [
                {
                    'added': added_files,
                    'removed': removed_files,
                    'modified': modified_files
                }
            ]
        }
        return (name, data)

    def emitEvent(self, event, use_zuulweb=False):
        """Emulates sending the GitHub webhook event to the connection."""
        name, data = event
        payload = json.dumps(data).encode('utf8')
        secret = self.connection_config['webhook_token']
        signature = githubconnection._sign_request(payload, secret)
        headers = {'x-github-event': name,
                   'x-hub-signature': signature,
                   'x-github-delivery': str(uuid.uuid4())}

        if use_zuulweb:
            return requests.post(
                'http://127.0.0.1:%s/api/connection/%s/payload'
                % (self.zuul_web_port, self.connection_name),
                json=data, headers=headers)
        else:
            data = {'headers': headers, 'body': data}
            self.event_queue.put(data)
            return data

    def addProject(self, project):
        # use the original method here and additionally register it in the
        # fake github
        super(FakeGithubConnection, self).addProject(project)
        self.getGithubClient(project.name).addProject(project)

    def getGitUrl(self, project):
        if self.git_url_with_auth:
            auth_token = ''.join(
                random.choice(string.ascii_lowercase) for x in range(8))
            prefix = 'file://x-access-token:%s@' % auth_token
        else:
            prefix = ''
        return prefix + os.path.join(self.upstream_root, str(project))

    def real_getGitUrl(self, project):
        return super(FakeGithubConnection, self).getGitUrl(project)

    def setCommitStatus(self, project, sha, state, url='', description='',
                        context='default', user='zuul', zuul_event_id=None):
        # record that this got reported and call original method
        self.github_data.reports.append(
            (project, sha, 'status', (user, context, state)))
        super(FakeGithubConnection, self).setCommitStatus(
            project, sha, state,
            url=url, description=description, context=context)

    def labelPull(self, project, pr_number, label, zuul_event_id=None):
        # record that this got reported
        self.github_data.reports.append((project, pr_number, 'label', label))
        pull_request = self.pull_requests[int(pr_number)]
        pull_request.addLabel(label)

    def unlabelPull(self, project, pr_number, label, zuul_event_id=None):
        # record that this got reported
        self.github_data.reports.append((project, pr_number, 'unlabel', label))
        pull_request = self.pull_requests[pr_number]
        pull_request.removeLabel(label)


class BuildHistory(object):
    def __init__(self, **kw):
        self.__dict__.update(kw)

    def __repr__(self):
        return ("<Completed build, result: %s name: %s uuid: %s "
                "changes: %s ref: %s>" %
                (self.result, self.name, self.uuid,
                 self.changes, self.ref))


class FakeStatsd(threading.Thread):
    log = logging.getLogger("zuul.test.FakeStatsd")

    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        self.sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        self.sock.bind(('', 0))
        self.port = self.sock.getsockname()[1]
        self.wake_read, self.wake_write = os.pipe()
        self.stats = []

    def clear(self):
        self.stats = []

    def run(self):
        while True:
            poll = select.poll()
            poll.register(self.sock, select.POLLIN)
            poll.register(self.wake_read, select.POLLIN)
            ret = poll.poll()
            for (fd, event) in ret:
                if fd == self.sock.fileno():
                    data = self.sock.recvfrom(1024)
                    if not data:
                        return
                    # self.log.debug("Appending: %s" % data[0])
                    self.stats.append(data[0])
                if fd == self.wake_read:
                    return

    def stop(self):
        os.write(self.wake_write, b'1\n')
        self.join()
        self.sock.close()


class FakeBuild(object):
    log = logging.getLogger("zuul.test")

    def __init__(self, executor_server, build_request, params):
        self.daemon = True
        self.executor_server = executor_server
        self.build_request = build_request
        self.jobdir = None
        self.uuid = build_request.uuid
        self.parameters = params
        self.job = model.FrozenJob.fromZK(executor_server.zk_context,
                                          params["job_ref"])
        self.parameters["zuul"].update(
            zuul.executor.server.zuul_params_from_job(self.job))
        # TODOv3(jeblair): self.node is really "the label of the node
        # assigned".  We should rename it (self.node_label?) if we
        # keep using it like this, or we may end up exposing more of
        # the complexity around multi-node jobs here
        # (self.nodes[0].label?)
        self.node = None
        if len(self.job.nodeset.nodes) == 1:
            self.node = next(iter(self.job.nodeset.nodes.values())).label
        self.unique = self.parameters['zuul']['build']
        self.pipeline = self.parameters['zuul']['pipeline']
        self.project = self.parameters['zuul']['project']['name']
        self.name = self.job.name
        self.wait_condition = threading.Condition()
        self.waiting = False
        self.paused = False
        self.aborted = False
        self.requeue = False
        self.created = time.time()
        self.changes = None
        items = self.parameters['zuul']['items']
        self.changes = ' '.join(['%s,%s' % (x['change'], x['patchset'])
                                 for x in items if 'change' in x])
        if 'change' in items[-1]:
            self.change = ' '.join((items[-1]['change'],
                                    items[-1]['patchset']))
        else:
            self.change = None

    def __repr__(self):
        waiting = ''
        if self.waiting:
            waiting = ' [waiting]'
        return '<FakeBuild %s:%s %s%s>' % (self.pipeline, self.name,
                                           self.changes, waiting)

    def release(self):
        """Release this build."""
        self.wait_condition.acquire()
        self.wait_condition.notify()
        self.waiting = False
        self.log.debug("Build %s released" % self.unique)
        self.wait_condition.release()

    def isWaiting(self):
        """Return whether this build is being held.

        :returns: Whether the build is being held.
        :rtype: bool
        """

        self.wait_condition.acquire()
        if self.waiting:
            ret = True
        else:
            ret = False
        self.wait_condition.release()
        return ret

    def _wait(self):
        self.wait_condition.acquire()
        self.waiting = True
        self.log.debug("Build %s waiting" % self.unique)
        self.wait_condition.wait()
        self.wait_condition.release()

    def run(self):
        self.log.debug('Running build %s' % self.unique)

        if self.executor_server.hold_jobs_in_build:
            self.log.debug('Holding build %s' % self.unique)
            self._wait()
        self.log.debug("Build %s continuing" % self.unique)

        self.writeReturnData()

        result = (RecordingAnsibleJob.RESULT_NORMAL, 0)  # Success
        if self.shouldFail():
            result = (RecordingAnsibleJob.RESULT_NORMAL, 1)  # Failure
        if self.aborted:
            result = (RecordingAnsibleJob.RESULT_ABORTED, None)
        if self.requeue:
            result = (RecordingAnsibleJob.RESULT_UNREACHABLE, None)

        return result

    def shouldFail(self):
        changes = self.executor_server.fail_tests.get(self.name, [])
        for change in changes:
            if self.hasChanges(change):
                return True
        return False

    def writeReturnData(self):
        changes = self.executor_server.return_data.get(self.name, {})
        data = changes.get(self.change)
        if data is None:
            return
        with open(self.jobdir.result_data_file, 'w') as f:
            f.write(json.dumps({'data': data}))

    def hasChanges(self, *changes):
        """Return whether this build has certain changes in its git repos.

        :arg FakeChange changes: One or more changes (varargs) that
            are expected to be present (in order) in the git repository of
            the active project.

        :returns: Whether the build has the indicated changes.
        :rtype: bool

        """
        for change in changes:
            hostname = change.source.canonical_hostname
            path = os.path.join(self.jobdir.src_root, hostname, change.project)
            try:
                repo = git.Repo(path)
            except NoSuchPathError as e:
                self.log.debug('%s' % e)
                return False
            repo_messages = [c.message.strip() for c in repo.iter_commits()]
            commit_message = '%s-1' % change.subject
            self.log.debug("Checking if build %s has changes; commit_message "
                           "%s; repo_messages %s" % (self, commit_message,
                                                     repo_messages))
            if commit_message not in repo_messages:
                self.log.debug("  messages do not match")
                return False
        self.log.debug("  OK")
        return True

    def getWorkspaceRepos(self, projects):
        """Return workspace git repo objects for the listed projects

        :arg list projects: A list of strings, each the canonical name
                            of a project.

        :returns: A dictionary of {name: repo} for every listed
                  project.
        :rtype: dict

        """

        repos = {}
        for project in projects:
            path = os.path.join(self.jobdir.src_root, project)
            repo = git.Repo(path)
            repos[project] = repo
        return repos


class RecordingAnsibleJob(zuul.executor.server.AnsibleJob):
    result = None

    def _execute(self):
        for _ in iterate_timeout(60, 'wait for merge'):
            if not self.executor_server.hold_jobs_in_start:
                break
            time.sleep(1)

        super()._execute()

    def doMergeChanges(self, *args, **kw):
        # Get a merger in order to update the repos involved in this job.
        commit = super(RecordingAnsibleJob, self).doMergeChanges(
            *args, **kw)
        if not commit:  # merge conflict
            self.recordResult('MERGER_FAILURE')

        return commit

    def recordResult(self, result):
        self.executor_server.lock.acquire()
        build = self.executor_server.job_builds.get(self.build_request.uuid)
        if not build:
            self.executor_server.lock.release()
            # Already recorded
            return
        self.executor_server.build_history.append(
            BuildHistory(name=build.name, result=result, changes=build.changes,
                         node=build.node, uuid=build.unique, job=build.job,
                         ref=build.parameters['zuul']['ref'],
                         newrev=build.parameters['zuul'].get('newrev'),
                         parameters=build.parameters, jobdir=build.jobdir,
                         pipeline=build.parameters['zuul']['pipeline'],
                         build_request_ref=build.build_request.path)
        )
        self.executor_server.running_builds.remove(build)
        del self.executor_server.job_builds[self.build_request.uuid]
        self.executor_server.lock.release()

    def runPlaybooks(self, args):
        build = self.executor_server.job_builds[self.build_request.uuid]
        build.jobdir = self.jobdir

        self.result = super(RecordingAnsibleJob, self).runPlaybooks(args)
        if self.result is None:
            # Record result now because cleanup won't be performed
            self.recordResult(None)
        return self.result

    def runCleanupPlaybooks(self, success):
        super(RecordingAnsibleJob, self).runCleanupPlaybooks(success)
        if self.result is not None:
            self.recordResult(self.result)

    def runAnsible(self, cmd, timeout, playbook, ansible_version,
                   wrapped=True, cleanup=False):
        build = self.executor_server.job_builds[self.build_request.uuid]

        if self.executor_server._run_ansible:
            # Call run on the fake build omitting the result so we also can
            # hold real ansible jobs.
            if playbook not in [self.jobdir.setup_playbook,
                                self.jobdir.freeze_playbook]:
                build.run()

            result = super(RecordingAnsibleJob, self).runAnsible(
                cmd, timeout, playbook, ansible_version, wrapped, cleanup)
        else:
            if playbook not in [self.jobdir.setup_playbook,
                                self.jobdir.freeze_playbook]:
                result = build.run()
            else:
                result = (self.RESULT_NORMAL, 0)
        return result

    def getHostList(self, args, nodes):
        self.log.debug("hostlist %s", nodes)
        hosts = super(RecordingAnsibleJob, self).getHostList(args, nodes)
        for host in hosts:
            if not host['host_vars'].get('ansible_connection'):
                host['host_vars']['ansible_connection'] = 'local'
        return hosts

    def pause(self):
        build = self.executor_server.job_builds[self.build_request.uuid]
        build.paused = True
        super().pause()

    def resume(self):
        build = self.executor_server.job_builds.get(self.build_request.uuid)
        if build:
            build.paused = False
        super().resume()

    def _send_aborted(self):
        self.recordResult('ABORTED')
        super()._send_aborted()


FakeMergeRequest = namedtuple(
    "FakeMergeRequest", ("uuid", "job_type", "payload")
)


class HoldableMergerApi(MergerApi):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hold_in_queue = False
        self.history = {}

    def submit(self, request, params, needs_result=False):
        self.log.debug("Appending merge job to history: %s", request.uuid)
        self.history.setdefault(request.job_type, [])
        self.history[request.job_type].append(
            FakeMergeRequest(request.uuid, request.job_type, params)
        )
        return super().submit(request, params, needs_result)

    @property
    def initial_state(self):
        if self.hold_in_queue:
            return MergeRequest.HOLD
        return MergeRequest.REQUESTED


class TestingMergerApi(HoldableMergerApi):

    log = logging.getLogger("zuul.test.TestingMergerApi")

    def _test_getMergeJobsInState(self, *states):
        # As this method is used for assertions in the tests, it should look up
        # the merge requests directly from ZooKeeper and not from a cache
        # layer.
        all_merge_requests = []
        for merge_uuid in self._getAllRequestIds():
            merge_request = self.get("/".join(
                [self.REQUEST_ROOT, merge_uuid]))
            if merge_request and (not states or merge_request.state in states):
                all_merge_requests.append(merge_request)

        return sorted(all_merge_requests)

    def release(self, merge_request=None):
        """
        Releases a merge request which was previously put on hold for testing.

        If no merge_request is provided, all merge request that are currently
        in state HOLD will be released.
        """
        # Either release all jobs in HOLD state or the one specified.
        if merge_request is not None:
            merge_request.state = MergeRequest.REQUESTED
            self.update(merge_request)
            return

        for merge_request in self._test_getMergeJobsInState(MergeRequest.HOLD):
            merge_request.state = MergeRequest.REQUESTED
            self.update(merge_request)

    def queued(self):
        return self._test_getMergeJobsInState(
            MergeRequest.REQUESTED, MergeRequest.HOLD
        )

    def all(self):
        return self._test_getMergeJobsInState()


class HoldableMergeClient(zuul.merger.client.MergeClient):

    _merger_api_class = HoldableMergerApi


class HoldableExecutorApi(ExecutorApi):
    def __init__(self, *args, **kwargs):
        self.hold_in_queue = False
        super().__init__(*args, **kwargs)

    def _getInitialState(self):
        if self.hold_in_queue:
            return BuildRequest.HOLD
        return BuildRequest.REQUESTED


class TestingExecutorApi(HoldableExecutorApi):
    log = logging.getLogger("zuul.test.TestingExecutorApi")

    def _test_getBuildsInState(self, *states):
        # As this method is used for assertions in the tests, it
        # should look up the build requests directly from ZooKeeper
        # and not from a cache layer.

        all_builds = []
        for zone in self._getAllZones():
            queue = self.zone_queues[zone]
            for build_uuid in queue._getAllRequestIds():
                build = queue.get(f'{queue.REQUEST_ROOT}/{build_uuid}')
                if build and (not states or build.state in states):
                    all_builds.append(build)

        all_builds.sort()
        return all_builds

    def _getJobForBuildRequest(self, build_request):
        # The parameters for the build request are removed immediately
        # after the job starts in order to reduce impact to ZK, so if
        # we want to inspect them in the tests, we need to save them.
        # This adds them to a private internal cache for that purpose.
        if not hasattr(self, '_test_build_request_job_map'):
            self._test_build_request_job_map = {}
        if build_request.uuid in self._test_build_request_job_map:
            return self._test_build_request_job_map[build_request.uuid]
        d = self.getParams(build_request)
        if d:
            data = d.get('job_ref', '').split('/')[-1]
        else:
            data = ''
        self._test_build_request_job_map[build_request.uuid] = data
        return data

    def release(self, what=None):
        """
        Releases a build request which was previously put on hold for testing.

        The what parameter specifies what to release. This can be a concrete
        build request or a regular expression matching a job name.
        """
        self.log.debug("Releasing builds matching %s", what)
        if isinstance(what, BuildRequest):
            self.log.debug("Releasing build %s", what)
            what.state = BuildRequest.REQUESTED
            self.update(what)
            return

        for build_request in self._test_getBuildsInState(
                BuildRequest.HOLD):
            # Either release all build requests in HOLD state or the ones
            # matching the given job name pattern.
            if what is None or (
                    re.match(what,
                             self._getJobForBuildRequest(build_request))):
                self.log.debug("Releasing build %s", build_request)
                build_request.state = BuildRequest.REQUESTED
                self.update(build_request)

    def queued(self):
        return self._test_getBuildsInState(
            BuildRequest.REQUESTED, BuildRequest.HOLD
        )

    def all(self):
        return self._test_getBuildsInState()


class HoldableExecutorClient(zuul.executor.client.ExecutorClient):
    _executor_api_class = HoldableExecutorApi


class RecordingExecutorServer(zuul.executor.server.ExecutorServer):
    """An Ansible executor to be used in tests.

    :ivar bool hold_jobs_in_build: If true, when jobs are executed
        they will report that they have started but then pause until
        released before reporting completion.  This attribute may be
        changed at any time and will take effect for subsequently
        executed builds, but previously held builds will still need to
        be explicitly released.

    """

    _job_class = RecordingAnsibleJob

    def __init__(self, *args, **kw):
        self._run_ansible = kw.pop('_run_ansible', False)
        self._test_root = kw.pop('_test_root', False)
        if self._run_ansible:
            self._ansible_manager_class = zuul.lib.ansible.AnsibleManager
        else:
            self._ansible_manager_class = FakeAnsibleManager
        super(RecordingExecutorServer, self).__init__(*args, **kw)
        self.hold_jobs_in_build = False
        self.hold_jobs_in_start = False
        self.lock = threading.Lock()
        self.running_builds = []
        self.build_history = []
        self.fail_tests = {}
        self.return_data = {}
        self.job_builds = {}

    def failJob(self, name, change):
        """Instruct the executor to report matching builds as failures.

        :arg str name: The name of the job to fail.
        :arg Change change: The :py:class:`~tests.base.FakeChange`
            instance which should cause the job to fail.  This job
            will also fail for changes depending on this change.

        """
        l = self.fail_tests.get(name, [])
        l.append(change)
        self.fail_tests[name] = l

    def returnData(self, name, change, data):
        """Instruct the executor to return data for this build.

        :arg str name: The name of the job to return data.
        :arg Change change: The :py:class:`~tests.base.FakeChange`
            instance which should cause the job to return data.
        :arg dict data: The data to return

        """
        # TODO(clarkb) We are incredibly change focused here and in FakeBuild
        # above. This makes it very difficult to test non change items with
        # return data. We currently rely on the hack that None is used as a
        # key for the changes dict, but we should improve that to look up
        # refnames or similar.
        changes = self.return_data.setdefault(name, {})
        if hasattr(change, 'number'):
            cid = ' '.join((str(change.number), str(change.latest_patchset)))
        else:
            # Not actually a change, but a ref update event for tags/etc
            # In this case a key of None is used by writeReturnData
            cid = None
        changes[cid] = data

    def release(self, regex=None, change=None):
        """Release a held build.

        :arg str regex: A regular expression which, if supplied, will
            cause only builds with matching names to be released.  If
            not supplied, all builds will be released.

        """
        builds = self.running_builds[:]
        if len(builds) == 0:
            self.log.debug('No running builds to release')
            return

        self.log.debug("Releasing build %s (%s)" % (regex, len(builds)))
        for build in builds:
            if (not regex or re.match(regex, build.name) and
                not change or build.change == change):
                self.log.debug("Releasing build %s" %
                               (build.parameters['zuul']['build']))
                build.release()
            else:
                self.log.debug("Not releasing build %s" %
                               (build.parameters['zuul']['build']))
        self.log.debug("Done releasing builds %s (%s)" %
                       (regex, len(builds)))

    def executeJob(self, build_request, params):
        build = FakeBuild(self, build_request, params)
        self.running_builds.append(build)
        self.job_builds[build_request.uuid] = build
        params['zuul']['_test'] = dict(test_root=self._test_root)
        super(RecordingExecutorServer, self).executeJob(build_request, params)

    def stopJob(self, build_request: BuildRequest):
        self.log.debug("handle stop")
        uuid = build_request.uuid
        for build in self.running_builds:
            if build.unique == uuid:
                build.aborted = True
                build.release()
        super(RecordingExecutorServer, self).stopJob(build_request)

    def stop(self):
        for build in self.running_builds:
            build.release()
        super(RecordingExecutorServer, self).stop()


class TestScheduler(zuul.scheduler.Scheduler):
    _merger_client_class = HoldableMergeClient
    _executor_client_class = HoldableExecutorClient


class FakeGearmanServer(gear.Server):
    """A Gearman server for use in tests.

    :ivar bool hold_jobs_in_queue: If true, submitted jobs will be
        added to the queue but will not be distributed to workers
        until released.  This attribute may be changed at any time and
        will take effect for subsequently enqueued jobs, but
        previously held jobs will still need to be explicitly
        released.

    """

    def __init__(self, use_ssl=False):
        self.hold_jobs_in_queue = False
        self.hold_merge_jobs_in_queue = False
        self.jobs_history = []
        if use_ssl:
            ssl_ca = os.path.join(FIXTURE_DIR, 'gearman/root-ca.pem')
            ssl_cert = os.path.join(FIXTURE_DIR, 'gearman/server.pem')
            ssl_key = os.path.join(FIXTURE_DIR, 'gearman/server.key')
        else:
            ssl_ca = None
            ssl_cert = None
            ssl_key = None

        super(FakeGearmanServer, self).__init__(0, ssl_key=ssl_key,
                                                ssl_cert=ssl_cert,
                                                ssl_ca=ssl_ca)

    def getJobForConnection(self, connection, peek=False):
        for job_queue in [self.high_queue, self.normal_queue, self.low_queue]:
            for job in job_queue:
                self.jobs_history.append(job)
                if not hasattr(job, 'waiting'):
                    if job.name.startswith(b'merger:'):
                        job.waiting = self.hold_merge_jobs_in_queue
                    else:
                        job.waiting = False
                if job.waiting:
                    continue
                if job.name in connection.functions:
                    if not peek:
                        job_queue.remove(job)
                        connection.related_jobs[job.handle] = job
                        job.worker_connection = connection
                    job.running = True
                    return job
        return None

    def release(self, regex=None):
        """Release a held job.

        :arg str regex: A regular expression which, if supplied, will
            cause only jobs with matching names to be released.  If
            not supplied, all jobs will be released.
        """
        released = False
        qlen = (len(self.high_queue) + len(self.normal_queue) +
                len(self.low_queue))
        self.log.debug("releasing queued job %s (%s)" % (regex, qlen))
        for job in self.getQueue():
            match = False
            if job.name.startswith(b'executor:execute'):
                parameters = json.loads(job.arguments.decode('utf8'))
                if not regex or re.match(regex, parameters.get('job')):
                    match = True
            if job.name.startswith(b'merger:'):
                if not regex:
                    match = True
            if match:
                self.log.debug("releasing queued job %s" %
                               job.unique)
                job.waiting = False
                released = True
            else:
                self.log.debug("not releasing queued job %s" %
                               job.unique)
        if released:
            self.wakeConnections()
        qlen = (len(self.high_queue) + len(self.normal_queue) +
                len(self.low_queue))
        self.log.debug("done releasing queued jobs %s (%s)" % (regex, qlen))


class FakeSMTP(object):
    log = logging.getLogger('zuul.FakeSMTP')

    def __init__(self, messages, server, port):
        self.server = server
        self.port = port
        self.messages = messages

    def sendmail(self, from_email, to_email, msg):
        self.log.info("Sending email from %s, to %s, with msg %s" % (
                      from_email, to_email, msg))

        headers = msg.split('\n\n', 1)[0]
        body = msg.split('\n\n', 1)[1]

        self.messages.append(dict(
            from_email=from_email,
            to_email=to_email,
            msg=msg,
            headers=headers,
            body=body,
        ))

        return True

    def quit(self):
        return True


class FakeNodepool(object):
    REQUEST_ROOT = '/nodepool/requests'
    NODE_ROOT = '/nodepool/nodes'
    LAUNCHER_ROOT = '/nodepool/launchers'

    log = logging.getLogger("zuul.test.FakeNodepool")

    def __init__(self, zk_chroot_fixture):
        self.complete_event = threading.Event()
        self.host_keys = None

        self.client = kazoo.client.KazooClient(
            hosts='%s:%s%s' % (
                zk_chroot_fixture.zookeeper_host,
                zk_chroot_fixture.zookeeper_port,
                zk_chroot_fixture.zookeeper_chroot),
            use_ssl=True,
            keyfile=zk_chroot_fixture.zookeeper_key,
            certfile=zk_chroot_fixture.zookeeper_cert,
            ca=zk_chroot_fixture.zookeeper_ca,
        )
        self.client.start()
        self.registerLauncher()
        self._running = True
        self.paused = False
        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True
        self.thread.start()
        self.fail_requests = set()
        self.remote_ansible = False
        self.attributes = None
        self.resources = None
        self.python_path = 'auto'
        self.shell_type = None
        self.connection_port = None

    def stop(self):
        self._running = False
        self.thread.join()
        self.client.stop()
        self.client.close()

    def pause(self):
        self.complete_event.wait()
        self.paused = True

    def unpause(self):
        self.paused = False

    def run(self):
        while self._running:
            self.complete_event.clear()
            try:
                self._run()
            except Exception:
                self.log.exception("Error in fake nodepool:")
            self.complete_event.set()
            time.sleep(0.1)

    def _run(self):
        if self.paused:
            return
        for req in self.getNodeRequests():
            self.fulfillRequest(req)

    def registerLauncher(self, labels=["label1"], id="FakeLauncher"):
        path = os.path.join(self.LAUNCHER_ROOT, id)
        data = {'id': id, 'supported_labels': labels}
        self.client.create(
            path, json.dumps(data).encode('utf8'), makepath=True)

    def getNodeRequests(self):
        try:
            reqids = self.client.get_children(self.REQUEST_ROOT)
        except kazoo.exceptions.NoNodeError:
            return []
        reqs = []
        for oid in reqids:
            path = self.REQUEST_ROOT + '/' + oid
            try:
                data, stat = self.client.get(path)
                data = json.loads(data.decode('utf8'))
                data['_oid'] = oid
                reqs.append(data)
            except kazoo.exceptions.NoNodeError:
                pass
        reqs.sort(key=lambda r: (r['_oid'].split('-')[0],
                                 r['relative_priority'],
                                 r['_oid'].split('-')[1]))
        return reqs

    def getNodes(self):
        try:
            nodeids = self.client.get_children(self.NODE_ROOT)
        except kazoo.exceptions.NoNodeError:
            return []
        nodes = []
        for oid in sorted(nodeids):
            path = self.NODE_ROOT + '/' + oid
            data, stat = self.client.get(path)
            data = json.loads(data.decode('utf8'))
            data['_oid'] = oid
            try:
                lockfiles = self.client.get_children(path + '/lock')
            except kazoo.exceptions.NoNodeError:
                lockfiles = []
            if lockfiles:
                data['_lock'] = True
            else:
                data['_lock'] = False
            nodes.append(data)
        return nodes

    def makeNode(self, request_id, node_type):
        now = time.time()
        path = '/nodepool/nodes/'
        remote_ip = os.environ.get('ZUUL_REMOTE_IPV4', '127.0.0.1')
        if self.remote_ansible and not self.host_keys:
            self.host_keys = self.keyscan(remote_ip)
        if self.host_keys is None:
            host_keys = ["fake-key1", "fake-key2"]
        else:
            host_keys = self.host_keys
        data = dict(type=node_type,
                    cloud='test-cloud',
                    provider='test-provider',
                    region='test-region',
                    az='test-az',
                    attributes=self.attributes,
                    host_id='test-host-id',
                    interface_ip=remote_ip,
                    public_ipv4=remote_ip,
                    private_ipv4=None,
                    public_ipv6=None,
                    private_ipv6=None,
                    python_path=self.python_path,
                    shell_type=self.shell_type,
                    allocated_to=request_id,
                    state='ready',
                    state_time=now,
                    created_time=now,
                    updated_time=now,
                    image_id=None,
                    host_keys=host_keys,
                    executor='fake-nodepool',
                    hold_expiration=None)
        if self.resources:
            data['resources'] = self.resources
        if self.remote_ansible:
            data['connection_type'] = 'ssh'
        if 'fakeuser' in node_type:
            data['username'] = 'fakeuser'
        if 'windows' in node_type:
            data['connection_type'] = 'winrm'
        if 'network' in node_type:
            data['connection_type'] = 'network_cli'
        if self.connection_port:
            data['connection_port'] = self.connection_port
        if 'kubernetes-namespace' in node_type or 'fedora-pod' in node_type:
            data['connection_type'] = 'namespace'
            data['connection_port'] = {
                'name': 'zuul-ci',
                'namespace': 'zuul-ci-abcdefg',
                'host': 'localhost',
                'skiptls': True,
                'token': 'FakeToken',
                'ca_crt': 'FakeCA',
                'user': 'zuul-worker',
            }
            if 'fedora-pod' in node_type:
                data['connection_type'] = 'kubectl'
                data['connection_port']['pod'] = 'fedora-abcdefg'

        data = json.dumps(data).encode('utf8')
        path = self.client.create(path, data,
                                  makepath=True,
                                  sequence=True)
        nodeid = path.split("/")[-1]
        return nodeid

    def removeNode(self, node):
        path = self.NODE_ROOT + '/' + node["_oid"]
        self.client.delete(path, recursive=True)

    def addFailRequest(self, request):
        self.fail_requests.add(request['_oid'])

    def fulfillRequest(self, request):
        if request['state'] != 'requested':
            return
        request = request.copy()
        oid = request['_oid']
        del request['_oid']

        if oid in self.fail_requests:
            request['state'] = 'failed'
        else:
            request['state'] = 'fulfilled'
            nodes = request.get('nodes', [])
            for node in request['node_types']:
                nodeid = self.makeNode(oid, node)
                nodes.append(nodeid)
            request['nodes'] = nodes

        request['state_time'] = time.time()
        path = self.REQUEST_ROOT + '/' + oid
        data = json.dumps(request).encode('utf8')
        self.log.debug("Fulfilling node request: %s %s" % (oid, data))
        try:
            self.client.set(path, data)
        except kazoo.exceptions.NoNodeError:
            self.log.debug("Node request %s %s disappeared" % (oid, data))

    def keyscan(self, ip, port=22, timeout=60):
        '''
        Scan the IP address for public SSH keys.

        Keys are returned formatted as: "<type> <base64_string>"
        '''
        addrinfo = socket.getaddrinfo(ip, port)[0]
        family = addrinfo[0]
        sockaddr = addrinfo[4]

        keys = []
        key = None
        for count in iterate_timeout(timeout, "ssh access"):
            sock = None
            t = None
            try:
                sock = socket.socket(family, socket.SOCK_STREAM)
                sock.settimeout(timeout)
                sock.connect(sockaddr)
                t = paramiko.transport.Transport(sock)
                t.start_client(timeout=timeout)
                key = t.get_remote_server_key()
                break
            except socket.error as e:
                if e.errno not in [
                        errno.ECONNREFUSED, errno.EHOSTUNREACH, None]:
                    self.log.exception(
                        'Exception with ssh access to %s:' % ip)
            except Exception as e:
                self.log.exception("ssh-keyscan failure: %s", e)
            finally:
                try:
                    if t:
                        t.close()
                except Exception as e:
                    self.log.exception('Exception closing paramiko: %s', e)
                try:
                    if sock:
                        sock.close()
                except Exception as e:
                    self.log.exception('Exception closing socket: %s', e)

        # Paramiko, at this time, seems to return only the ssh-rsa key, so
        # only the single key is placed into the list.
        if key:
            keys.append("%s %s" % (key.get_name(), key.get_base64()))

        return keys


class ChrootedKazooFixture(fixtures.Fixture):
    def __init__(self, test_id):
        super(ChrootedKazooFixture, self).__init__()

        if 'ZOOKEEPER_2181_TCP' in os.environ:
            # prevent any nasty hobbits^H^H^H suprises
            if 'NODEPOOL_ZK_HOST' in os.environ:
                raise Exception(
                    'Looks like tox-docker is being used but you have also '
                    'configured NODEPOOL_ZK_HOST. Either avoid using the '
                    'docker environment or unset NODEPOOL_ZK_HOST.')

            zk_host = 'localhost:' + os.environ['ZOOKEEPER_2181_TCP']
        elif 'NODEPOOL_ZK_HOST' in os.environ:
            zk_host = os.environ['NODEPOOL_ZK_HOST']
        else:
            zk_host = 'localhost'

        if ':' in zk_host:
            host, port = zk_host.split(':')
        else:
            host = zk_host
            port = None

        zk_ca = os.environ.get('ZUUL_ZK_CA', None)
        if not zk_ca:
            zk_ca = os.path.join(os.path.dirname(__file__),
                                 '../tools/ca/certs/cacert.pem')
        self.zookeeper_ca = zk_ca
        zk_cert = os.environ.get('ZUUL_ZK_CERT', None)
        if not zk_cert:
            zk_cert = os.path.join(os.path.dirname(__file__),
                                   '../tools/ca/certs/client.pem')
        self.zookeeper_cert = zk_cert
        zk_key = os.environ.get('ZUUL_ZK_KEY', None)
        if not zk_key:
            zk_key = os.path.join(os.path.dirname(__file__),
                                  '../tools/ca/keys/clientkey.pem')
        self.zookeeper_key = zk_key
        self.zookeeper_host = host

        if not port:
            self.zookeeper_port = 2281
        else:
            self.zookeeper_port = int(port)

        self.test_id = test_id

    def _setUp(self):
        # Make sure the test chroot paths do not conflict
        random_bits = ''.join(random.choice(string.ascii_lowercase +
                                            string.ascii_uppercase)
                              for x in range(8))

        rand_test_path = '%s_%s_%s' % (random_bits, os.getpid(), self.test_id)
        self.zookeeper_chroot = f"/test/{rand_test_path}"

        self.zk_hosts = '%s:%s%s' % (
            self.zookeeper_host,
            self.zookeeper_port,
            self.zookeeper_chroot)

        self.addCleanup(self._cleanup)

        # Ensure the chroot path exists and clean up any pre-existing znodes.
        _tmp_client = kazoo.client.KazooClient(
            hosts=f'{self.zookeeper_host}:{self.zookeeper_port}', timeout=10,
            use_ssl=True,
            keyfile=self.zookeeper_key,
            certfile=self.zookeeper_cert,
            ca=self.zookeeper_ca,
        )
        _tmp_client.start()

        if _tmp_client.exists(self.zookeeper_chroot):
            _tmp_client.delete(self.zookeeper_chroot, recursive=True)

        _tmp_client.ensure_path(self.zookeeper_chroot)
        _tmp_client.stop()
        _tmp_client.close()

    def _cleanup(self):
        '''Remove the chroot path.'''
        # Need a non-chroot'ed client to remove the chroot path
        _tmp_client = kazoo.client.KazooClient(
            hosts='%s:%s' % (self.zookeeper_host, self.zookeeper_port),
            use_ssl=True,
            keyfile=self.zookeeper_key,
            certfile=self.zookeeper_cert,
            ca=self.zookeeper_ca,
        )
        _tmp_client.start()
        _tmp_client.delete(self.zookeeper_chroot, recursive=True)
        _tmp_client.stop()
        _tmp_client.close()


class WebProxyFixture(fixtures.Fixture):
    def __init__(self, rules):
        super(WebProxyFixture, self).__init__()
        self.rules = rules

    def _setUp(self):
        rules = self.rules

        class Proxy(http.server.SimpleHTTPRequestHandler):
            log = logging.getLogger('zuul.WebProxyFixture.Proxy')

            def do_GET(self):
                path = self.path
                for (pattern, replace) in rules:
                    path = re.sub(pattern, replace, path)
                resp = requests.get(path)
                self.send_response(resp.status_code)
                if resp.status_code >= 300:
                    self.end_headers()
                    return
                for key, val in resp.headers.items():
                    self.send_header(key, val)
                self.end_headers()
                self.wfile.write(resp.content)

            def log_message(self, fmt, *args):
                self.log.debug(fmt, *args)

        self.httpd = socketserver.ThreadingTCPServer(('', 0), Proxy)
        self.port = self.httpd.socket.getsockname()[1]
        self.thread = threading.Thread(target=self.httpd.serve_forever)
        self.thread.start()
        self.addCleanup(self._cleanup)

    def _cleanup(self):
        self.httpd.shutdown()
        self.thread.join()


class ZuulWebFixture(fixtures.Fixture):
    def __init__(self,
                 changes: Dict[str, Dict[str, Change]], config: ConfigParser,
                 additional_event_queues, upstream_root: str,
                 rpcclient: RPCClient, poller_events, git_url_with_auth: bool,
                 add_cleanup: Callable[[Callable[[], None]], None],
                 test_root: str, info: Optional[WebInfo] = None):
        super(ZuulWebFixture, self).__init__()
        self.config = config
        self.connections = TestConnectionRegistry(
            changes, config, additional_event_queues, upstream_root, rpcclient,
            poller_events, git_url_with_auth, add_cleanup)
        self.connections.configure(config)

        self.authenticators = zuul.lib.auth.AuthenticatorRegistry()
        self.authenticators.configure(config)
        if info is None:
            self.info = WebInfo.fromConfig(config)
        else:
            self.info = info
        self.test_root = test_root

    def _setUp(self):
        # Start the web server
        self.web = zuul.web.ZuulWeb(
            config=self.config,
            info=self.info,
            connections=self.connections,
            authenticators=self.authenticators)
        self.connections.load(self.web.zk_client)
        self.web.start()
        self.addCleanup(self.stop)

        self.host = 'localhost'
        # Wait until web server is started
        while True:
            self.port = self.web.port
            try:
                with socket.create_connection((self.host, self.port)):
                    break
            except ConnectionRefusedError:
                pass

    def stop(self):
        self.web.stop()
        self.connections.stop()


class MySQLSchemaFixture(fixtures.Fixture):
    def setUp(self):
        super(MySQLSchemaFixture, self).setUp()

        random_bits = ''.join(random.choice(string.ascii_lowercase +
                                            string.ascii_uppercase)
                              for x in range(8))
        self.name = '%s_%s' % (random_bits, os.getpid())
        self.passwd = uuid.uuid4().hex
        self.host = os.environ.get('ZUUL_MYSQL_HOST', '127.0.0.1')
        self.port = int(os.environ.get('ZUUL_MYSQL_PORT', 3306))
        db = pymysql.connect(host=self.host,
                             port=self.port,
                             user="openstack_citest",
                             passwd="openstack_citest",
                             db="openstack_citest")
        try:
            with db.cursor() as cur:
                cur.execute("create database %s" % self.name)
                cur.execute(
                    "create user '{user}'@'' identified by '{passwd}'".format(
                        user=self.name, passwd=self.passwd))
                cur.execute("grant all on {name}.* to '{name}'@''".format(
                    name=self.name))
                cur.execute("flush privileges")
        finally:
            db.close()

        self.dburi = 'mysql+pymysql://{name}:{passwd}@{host}:{port}/{name}'\
            .format(
                name=self.name,
                passwd=self.passwd,
                host=self.host,
                port=self.port
            )
        self.addDetail('dburi', testtools.content.text_content(self.dburi))
        self.addCleanup(self.cleanup)

    def cleanup(self):
        db = pymysql.connect(host=self.host,
                             port=self.port,
                             user="openstack_citest",
                             passwd="openstack_citest",
                             db="openstack_citest")
        try:
            with db.cursor() as cur:
                cur.execute("drop database %s" % self.name)
                cur.execute("drop user '%s'@''" % self.name)
                cur.execute("flush privileges")
        finally:
            db.close()


class PostgresqlSchemaFixture(fixtures.Fixture):
    def setUp(self):
        super(PostgresqlSchemaFixture, self).setUp()

        # Postgres lowercases user and table names during creation but not
        # during authentication. Thus only use lowercase chars.
        random_bits = ''.join(random.choice(string.ascii_lowercase)
                              for x in range(8))
        self.name = '%s_%s' % (random_bits, os.getpid())
        self.passwd = uuid.uuid4().hex
        self.host = os.environ.get('ZUUL_POSTGRES_HOST', '127.0.0.1')
        db = psycopg2.connect(host=self.host,
                              user="openstack_citest",
                              password="openstack_citest",
                              database="openstack_citest")
        db.autocommit = True
        cur = db.cursor()
        cur.execute("create role %s with login password '%s';" % (
            self.name, self.passwd))
        cur.execute("create database %s OWNER %s TEMPLATE template0 "
                    "ENCODING 'UTF8';" % (self.name, self.name))

        self.dburi = 'postgresql://{name}:{passwd}@{host}/{name}'.format(
            name=self.name, passwd=self.passwd, host=self.host)

        self.addDetail('dburi', testtools.content.text_content(self.dburi))
        self.addCleanup(self.cleanup)

    def cleanup(self):
        db = psycopg2.connect(host=self.host,
                              user="openstack_citest",
                              password="openstack_citest",
                              database="openstack_citest")
        db.autocommit = True
        cur = db.cursor()
        cur.execute("drop database %s" % self.name)
        cur.execute("drop user %s" % self.name)


class FakeCPUTimes:
    def __init__(self):
        self.user = 0
        self.system = 0
        self.children_user = 0
        self.children_system = 0


def cpu_times(self):
    return FakeCPUTimes()


class BaseTestCase(testtools.TestCase):
    log = logging.getLogger("zuul.test")
    wait_timeout = 90

    def attachLogs(self, *args):
        def reader():
            self._log_stream.seek(0)
            while True:
                x = self._log_stream.read(4096)
                if not x:
                    break
                yield x.encode('utf8')
        content = testtools.content.content_from_reader(
            reader,
            testtools.content_type.UTF8_TEXT,
            False)
        self.addDetail('logging', content)

    def shouldNeverCapture(self):
        test_name = self.id().split('.')[-1]
        test = getattr(self, test_name)
        if hasattr(test, '__never_capture__'):
            return getattr(test, '__never_capture__')
        return False

    def setUp(self):
        super(BaseTestCase, self).setUp()
        test_timeout = os.environ.get('OS_TEST_TIMEOUT', 0)
        try:
            test_timeout = int(test_timeout)
        except ValueError:
            # If timeout value is invalid do not set a timeout.
            test_timeout = 0
        if test_timeout > 0:
            # Try a gentle timeout first and as a safety net a hard timeout
            # later.
            self.useFixture(fixtures.Timeout(test_timeout, gentle=True))
            self.useFixture(fixtures.Timeout(test_timeout + 20, gentle=False))

        if not self.shouldNeverCapture():
            if (os.environ.get('OS_STDOUT_CAPTURE') == 'True' or
                os.environ.get('OS_STDOUT_CAPTURE') == '1'):
                stdout = self.useFixture(
                    fixtures.StringStream('stdout')).stream
                self.useFixture(fixtures.MonkeyPatch('sys.stdout', stdout))
            if (os.environ.get('OS_STDERR_CAPTURE') == 'True' or
                os.environ.get('OS_STDERR_CAPTURE') == '1'):
                stderr = self.useFixture(
                    fixtures.StringStream('stderr')).stream
                self.useFixture(fixtures.MonkeyPatch('sys.stderr', stderr))
            if (os.environ.get('OS_LOG_CAPTURE') == 'True' or
                os.environ.get('OS_LOG_CAPTURE') == '1'):
                self._log_stream = StringIO()
                self.addOnException(self.attachLogs)
            else:
                self._log_stream = sys.stdout
        else:
            self._log_stream = sys.stdout

        handler = logging.StreamHandler(self._log_stream)
        formatter = logging.Formatter('%(asctime)s %(name)-32s '
                                      '%(levelname)-8s %(message)s')
        handler.setFormatter(formatter)

        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)

        # Make sure we don't carry old handlers around in process state
        # which slows down test runs
        self.addCleanup(logger.removeHandler, handler)

        # NOTE(notmorgan): Extract logging overrides for specific
        # libraries from the OS_LOG_DEFAULTS env and create loggers
        # for each. This is used to limit the output during test runs
        # from libraries that zuul depends on such as gear.
        log_defaults_from_env = os.environ.get(
            'OS_LOG_DEFAULTS',
            'git.cmd=INFO,gear=WARNING,'
            'kazoo.client=WARNING,kazoo.recipe=WARNING')

        if log_defaults_from_env:
            for default in log_defaults_from_env.split(','):
                try:
                    name, level_str = default.split('=', 1)
                    level = getattr(logging, level_str, logging.DEBUG)
                    logger = logging.getLogger(name)
                    logger.setLevel(level)
                    logger.addHandler(handler)
                    self.addCleanup(logger.removeHandler, handler)
                    logger.propagate = False
                except ValueError:
                    # NOTE(notmorgan): Invalid format of the log default,
                    # skip and don't try and apply a logger for the
                    # specified module
                    pass
        self.addCleanup(handler.close)
        self.addCleanup(handler.flush)

        if sys.platform == 'darwin':
            # Popen.cpu_times() is broken on darwin so patch it with a fake.
            Popen.cpu_times = cpu_times

    def setupZK(self):
        self.zk_chroot_fixture = self.useFixture(
            ChrootedKazooFixture(self.id())
        )

    def getZKWatches(self):
        # TODO: The client.command method used here returns only the
        # first 8k of data.  That means this method can return {} when
        # there actually are watches (and this happens in practice in
        # heavily loaded test environments).  We should replace that
        # method with something more robust.
        chroot = self.zk_chroot_fixture.zookeeper_chroot
        data = self.zk_client.client.command(b'wchp')
        ret = {}
        sessions = None
        for line in data.split('\n'):
            if line.startswith('\t'):
                if sessions is not None:
                    sessions.append(line.strip())
            else:
                line = line.strip()
                if not line:
                    continue
                if line.startswith(chroot):
                    line = line[len(chroot):]
                    sessions = []
                    ret[line] = sessions
                else:
                    sessions = None
        return ret

    def getZKTree(self, path, ret=None):
        """Return the contents of a ZK tree as a dictionary"""
        if ret is None:
            ret = {}
        for key in self.zk_client.client.get_children(path):
            subpath = os.path.join(path, key)
            ret[subpath] = self.zk_client.client.get(
                os.path.join(path, key))[0]
            self.getZKTree(subpath, ret)
        return ret

    def getZKPaths(self, path):
        return list(self.getZKTree(path).keys())


class SymLink(object):
    def __init__(self, target):
        self.target = target


class SchedulerTestApp:
    def __init__(self, log, config, changes, additional_event_queues,
                 upstream_root, rpcclient, poller_events,
                 git_url_with_auth, add_cleanup, validate_tenants,
                 instance_id):
        self.log = log
        self.config = config
        self.changes = changes
        self.validate_tenants = validate_tenants

        # Register connections from the config using fakes
        self.connections = TestConnectionRegistry(
            self.changes,
            self.config,
            additional_event_queues,
            upstream_root,
            rpcclient,
            poller_events,
            git_url_with_auth,
            add_cleanup,
        )
        self.connections.configure(self.config)

        self.sched = TestScheduler(self.config, self.connections, self)
        self.sched.log = logging.getLogger(f"zuul.Scheduler-{instance_id}")
        self.sched._stats_interval = 1

        if validate_tenants is None:
            self.connections.registerScheduler(self.sched)
            self.connections.load(self.sched.zk_client)

        # TODO (swestphahl): Can be removed when we no longer use global
        # management events.
        self.event_queues = [
            self.sched.reconfigure_event_queue,
        ]

    def start(self, validate_tenants=None):
        self.sched.start()
        if validate_tenants is None:
            self.sched.prime(self.config)
        else:
            self.sched.validateTenants(self.config, validate_tenants)

    def fullReconfigure(self):
        try:
            self.sched.reconfigure(self.config)
        except Exception:
            self.log.exception("Reconfiguration failed:")

    def smartReconfigure(self, command_socket=False):
        try:
            if command_socket:
                command_socket = self.sched.config.get(
                    'scheduler', 'command_socket')
                with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
                    s.connect(command_socket)
                    s.sendall('smart-reconfigure\n'.encode('utf8'))
            else:
                self.sched.reconfigure(self.config, smart=True)
        except Exception:
            self.log.exception("Reconfiguration failed:")


class SchedulerTestManager:
    def __init__(self, validate_tenants):
        self.instances = []
        self.validate_tenants = validate_tenants

    def create(self, log, config, changes, additional_event_queues,
               upstream_root, rpcclient, poller_events,
               git_url_with_auth, add_cleanup, validate_tenants):
        # Since the config contains a regex we cannot use copy.deepcopy()
        # as this will raise an exception with Python <3.7
        config_data = StringIO()
        config.write(config_data)
        config_data.seek(0)
        scheduler_config = ConfigParser()
        scheduler_config.read_file(config_data)

        instance_id = len(self.instances)
        # Ensure a unique command socket per scheduler instance
        command_socket = os.path.join(
            os.path.dirname(config.get("scheduler", "command_socket")),
            f"scheduler-{instance_id}.socket"
        )
        scheduler_config.set("scheduler", "command_socket", command_socket)

        app = SchedulerTestApp(log, scheduler_config, changes,
                               additional_event_queues, upstream_root,
                               rpcclient, poller_events,
                               git_url_with_auth, add_cleanup,
                               validate_tenants, instance_id)
        self.instances.append(app)
        return app

    def __len__(self) -> int:
        return len(self.instances)

    def __getitem__(self, item: int) -> SchedulerTestApp:
        return self.instances[item]

    def __setitem__(self, key: int, value: SchedulerTestApp):
        raise Exception("Not implemented, use create method!")

    def __delitem__(self, key):
        del self.instances[key]

    def __iter__(self):
        return iter(self.instances)

    @property
    def first(self) -> SchedulerTestApp:
        if len(self.instances) == 0:
            raise Exception("No scheduler!")
        return self.instances[0]

    def filter(self, matcher=None) -> Iterable[SchedulerTestApp]:
        fcn = None  # type: Optional[Callable[[int, SchedulerTestApp], bool]]
        if type(matcher) == list:
            def fcn(_: int, app: SchedulerTestApp) -> bool:
                return app in matcher
        elif type(matcher).__name__ == 'function':
            fcn = matcher
        return [e[1] for e in enumerate(self.instances)
                if fcn is None or fcn(e[0], e[1])]

    def execute(self, function: Callable[[Any], None], matcher=None) -> None:
        for instance in self.filter(matcher):
            function(instance)


class ZuulTestCase(BaseTestCase):
    """A test case with a functioning Zuul.

    The following class variables are used during test setup and can
    be overidden by subclasses but are effectively read-only once a
    test method starts running:

    :cvar str config_file: This points to the main zuul config file
        within the fixtures directory.  Subclasses may override this
        to obtain a different behavior.

    :cvar str tenant_config_file: This is the tenant config file
        (which specifies from what git repos the configuration should
        be loaded).  It defaults to the value specified in
        `config_file` but can be overidden by subclasses to obtain a
        different tenant/project layout while using the standard main
        configuration.  See also the :py:func:`simple_layout`
        decorator.

    :cvar str tenant_config_script_file: This is the tenant config script
        file. This attribute has the same meaning than tenant_config_file
        except that the tenant configuration is loaded from a script.
        When this attribute is set then tenant_config_file is ignored
        by the scheduler.

    :cvar bool create_project_keys: Indicates whether Zuul should
        auto-generate keys for each project, or whether the test
        infrastructure should insert dummy keys to save time during
        startup.  Defaults to False.

    :cvar int log_console_port: The zuul_stream/zuul_console port.

    The following are instance variables that are useful within test
    methods:

    :ivar FakeGerritConnection fake_<connection>:
        A :py:class:`~tests.base.FakeGerritConnection` will be
        instantiated for each connection present in the config file
        and stored here.  For instance, `fake_gerrit` will hold the
        FakeGerritConnection object for a connection named `gerrit`.

    :ivar FakeGearmanServer gearman_server: An instance of
        :py:class:`~tests.base.FakeGearmanServer` which is the Gearman
        server that all of the Zuul components in this test use to
        communicate with each other.

    :ivar RecordingExecutorServer executor_server: An instance of
        :py:class:`~tests.base.RecordingExecutorServer` which is the
        Ansible execute server used to run jobs for this test.

    :ivar list builds: A list of :py:class:`~tests.base.FakeBuild` objects
        representing currently running builds.  They are appended to
        the list in the order they are executed, and removed from this
        list upon completion.

    :ivar list history: A list of :py:class:`~tests.base.BuildHistory`
        objects representing completed builds.  They are appended to
        the list in the order they complete.

    """

    config_file: str = 'zuul.conf'
    run_ansible: bool = False
    create_project_keys: bool = False
    use_ssl: bool = False
    git_url_with_auth: bool = False
    log_console_port: int = 19885
    validate_tenants = None
    scheduler_count = SCHEDULER_COUNT

    def __getattr__(self, name):
        """Allows to access fake connections the old way, e.g., using
        `fake_gerrit` for FakeGerritConnection.

        This will access the connection of the first (default) scheduler
        (`self.scheds.first`). To access connections of a different
        scheduler use `self.scheds[{X}].connections.fake_{NAME}`.
        """
        if name.startswith('fake_') and\
                hasattr(self.scheds.first.connections, name):
            return getattr(self.scheds.first.connections, name)
        raise AttributeError("'ZuulTestCase' object has no attribute '%s'"
                             % name)

    def _startMerger(self):
        self.merge_server = zuul.merger.server.MergeServer(
            self.config, self.scheds.first.connections
        )
        self.merge_server.start()

    def setUp(self):
        super(ZuulTestCase, self).setUp()

        self.setupZK()
        self.fake_nodepool = FakeNodepool(self.zk_chroot_fixture)

        if not KEEP_TEMPDIRS:
            tmp_root = self.useFixture(fixtures.TempDir(
                rootdir=os.environ.get("ZUUL_TEST_ROOT"))
            ).path
        else:
            tmp_root = tempfile.mkdtemp(
                dir=os.environ.get("ZUUL_TEST_ROOT", None))
        self.test_root = os.path.join(tmp_root, "zuul-test")
        self.upstream_root = os.path.join(self.test_root, "upstream")
        self.merger_src_root = os.path.join(self.test_root, "merger-git")
        self.executor_src_root = os.path.join(self.test_root, "executor-git")
        self.state_root = os.path.join(self.test_root, "lib")
        self.merger_state_root = os.path.join(self.test_root, "merger-lib")
        self.executor_state_root = os.path.join(self.test_root, "executor-lib")
        self.jobdir_root = os.path.join(self.test_root, "builds")

        if os.path.exists(self.test_root):
            shutil.rmtree(self.test_root)
        os.makedirs(self.test_root)
        os.makedirs(self.upstream_root)
        os.makedirs(self.state_root)
        os.makedirs(self.merger_state_root)
        os.makedirs(self.executor_state_root)
        os.makedirs(self.jobdir_root)

        # Make per test copy of Configuration.
        self.config = self.setup_config(self.config_file)
        self.private_key_file = os.path.join(self.test_root, 'test_id_rsa')
        if not os.path.exists(self.private_key_file):
            src_private_key_file = os.environ.get(
                'ZUUL_SSH_KEY',
                os.path.join(FIXTURE_DIR, 'test_id_rsa'))
            shutil.copy(src_private_key_file, self.private_key_file)
            shutil.copy('{}.pub'.format(src_private_key_file),
                        '{}.pub'.format(self.private_key_file))
            os.chmod(self.private_key_file, 0o0600)
        for cfg_attr in ('tenant_config', 'tenant_config_script'):
            if self.config.has_option('scheduler', cfg_attr):
                cfg_value = self.config.get('scheduler', cfg_attr)
                self.config.set(
                    'scheduler', cfg_attr,
                    os.path.join(FIXTURE_DIR, cfg_value))

        self.config.set('scheduler', 'state_dir', self.state_root)
        self.config.set(
            'scheduler', 'command_socket',
            os.path.join(self.test_root, 'scheduler.socket'))
        if not self.config.has_option("keystore", "password"):
            self.config.set("keystore", "password", 'keystorepassword')
        self.config.set('merger', 'git_dir', self.merger_src_root)
        self.config.set('executor', 'git_dir', self.executor_src_root)
        self.config.set('executor', 'private_key_file', self.private_key_file)
        self.config.set('executor', 'state_dir', self.executor_state_root)
        self.config.set(
            'executor', 'command_socket',
            os.path.join(self.test_root, 'executor.socket'))
        self.config.set(
            'merger', 'command_socket',
            os.path.join(self.test_root, 'merger.socket'))
        self.config.set('web', 'listen_address', '::')
        self.config.set('web', 'port', '0')
        self.config.set(
            'web', 'command_socket',
            os.path.join(self.test_root, 'web.socket'))

        self.statsd = FakeStatsd()
        if self.config.has_section('statsd'):
            self.config.set('statsd', 'port', str(self.statsd.port))
        self.statsd.start()

        self.gearman_server = FakeGearmanServer(self.use_ssl)

        self.config.set('gearman', 'port', str(self.gearman_server.port))
        self.log.info("Gearman server on port %s" %
                      (self.gearman_server.port,))
        if self.use_ssl:
            self.log.info('SSL enabled for gearman')
            self.config.set(
                'gearman', 'ssl_ca',
                os.path.join(FIXTURE_DIR, 'gearman/root-ca.pem'))
            self.config.set(
                'gearman', 'ssl_cert',
                os.path.join(FIXTURE_DIR, 'gearman/client.pem'))
            self.config.set(
                'gearman', 'ssl_key',
                os.path.join(FIXTURE_DIR, 'gearman/client.key'))

        self.config.set('zookeeper', 'hosts', self.zk_chroot_fixture.zk_hosts)
        self.config.set('zookeeper', 'session_timeout', '30')
        self.config.set('zookeeper', 'tls_cert',
                        self.zk_chroot_fixture.zookeeper_cert)
        self.config.set('zookeeper', 'tls_key',
                        self.zk_chroot_fixture.zookeeper_key)
        self.config.set('zookeeper', 'tls_ca',
                        self.zk_chroot_fixture.zookeeper_ca)

        self.rpcclient = zuul.rpcclient.RPCClient(
            self.config.get('gearman', 'server'),
            self.gearman_server.port,
            get_default(self.config, 'gearman', 'ssl_key'),
            get_default(self.config, 'gearman', 'ssl_cert'),
            get_default(self.config, 'gearman', 'ssl_ca'))

        gerritsource.GerritSource.replication_timeout = 1.5
        gerritsource.GerritSource.replication_retry_interval = 0.5
        gerritconnection.GerritEventConnector.delay = 0.0

        self.changes: Dict[str, Dict[str, Change]] = {}

        self.additional_event_queues = []
        self.zk_client = ZooKeeperClient.fromConfig(self.config)
        self.zk_client.connect()

        self._context_lock = SessionAwareLock(
            self.zk_client.client, f"/test/{uuid.uuid4().hex}")

        self.connection_event_queues = DefaultKeyDict(
            lambda cn: ConnectionEventQueue(self.zk_client, cn)
        )
        # requires zk client
        self.setupAllProjectKeys(self.config)

        self.poller_events = {}
        self._configureSmtp()
        self._configureMqtt()
        self._configureElasticsearch()

        executor_connections = TestConnectionRegistry(
            self.changes, self.config, self.additional_event_queues,
            self.upstream_root, self.rpcclient, self.poller_events,
            self.git_url_with_auth, self.addCleanup)
        executor_connections.configure(self.config,
                                       source_only=True)
        self.executor_api = TestingExecutorApi(self.zk_client)
        self.merger_api = TestingMergerApi(self.zk_client)
        self.executor_server = RecordingExecutorServer(
            self.config,
            executor_connections,
            jobdir_root=self.jobdir_root,
            _run_ansible=self.run_ansible,
            _test_root=self.test_root,
            keep_jobdir=KEEP_TEMPDIRS,
            log_console_port=self.log_console_port)
        self.executor_server.start()
        self.history = self.executor_server.build_history
        self.builds = self.executor_server.running_builds

        self.scheds = SchedulerTestManager(self.validate_tenants)
        for _ in range(self.scheduler_count):
            self.createScheduler()

        self.merge_server = None

        # Cleanups are run in reverse order
        self.addCleanup(self.assertCleanShutdown)
        self.addCleanup(self.shutdown)
        self.addCleanup(self.assertFinalState)

        self.scheds.execute(
            lambda app: app.start(self.validate_tenants))

    def createScheduler(self):
        return self.scheds.create(
            self.log, self.config, self.changes,
            self.additional_event_queues, self.upstream_root, self.rpcclient,
            self.poller_events, self.git_url_with_auth,
            self.addCleanup, self.validate_tenants)

    def createZKContext(self, lock=None):
        if lock is None:
            # Just make sure the lock is acquired
            self._context_lock.acquire(blocking=False)
            lock = self._context_lock
        return zkobject.ZKContext(self.zk_client, lock,
                                  stop_event=None, log=self.log)

    def __event_queues(self, matcher) -> List[Queue]:
        # TODO (swestphahl): Can be removed when we no longer use global
        # management events.
        sched_queues = map(lambda app: app.event_queues,
                           self.scheds.filter(matcher))
        return [item for sublist in sched_queues for item in sublist] + \
            self.additional_event_queues

    def _configureSmtp(self):
        # Set up smtp related fakes
        # TODO(jhesketh): This should come from lib.connections for better
        # coverage
        # Register connections from the config
        self.smtp_messages = []

        def FakeSMTPFactory(*args, **kw):
            args = [self.smtp_messages] + list(args)
            return FakeSMTP(*args, **kw)

        self.useFixture(fixtures.MonkeyPatch('smtplib.SMTP', FakeSMTPFactory))

    def _configureMqtt(self):
        # Set up mqtt related fakes
        self.mqtt_messages = []

        def fakeMQTTPublish(_, topic, msg, qos, zuul_event_id):
            log = logging.getLogger('zuul.FakeMQTTPubish')
            log.info('Publishing message via mqtt')
            self.mqtt_messages.append({'topic': topic, 'msg': msg, 'qos': qos})
        self.useFixture(fixtures.MonkeyPatch(
            'zuul.driver.mqtt.mqttconnection.MQTTConnection.publish',
            fakeMQTTPublish))

    def _configureElasticsearch(self):
        # Set up Elasticsearch related fakes
        def getElasticsearchConnection(driver, name, config):
            con = FakeElasticsearchConnection(
                driver, name, config)
            return con

        self.useFixture(fixtures.MonkeyPatch(
            'zuul.driver.elasticsearch.ElasticsearchDriver.getConnection',
            getElasticsearchConnection))

    def setup_config(self, config_file: str):
        # This creates the per-test configuration object.  It can be
        # overridden by subclasses, but should not need to be since it
        # obeys the config_file and tenant_config_file attributes.
        config = configparser.ConfigParser()
        config.read(os.path.join(FIXTURE_DIR, config_file))

        sections = [
            'zuul', 'scheduler', 'executor', 'merger', 'web', 'zookeeper',
            'keystore', 'database',
        ]
        for section in sections:
            if not config.has_section(section):
                config.add_section(section)

        def _setup_fixture(config, section_name):
            if (config.get(section_name, 'dburi') ==
                    '$MYSQL_FIXTURE_DBURI$'):
                f = MySQLSchemaFixture()
                self.useFixture(f)
                config.set(section_name, 'dburi', f.dburi)
            elif (config.get(section_name, 'dburi') ==
                  '$POSTGRESQL_FIXTURE_DBURI$'):
                f = PostgresqlSchemaFixture()
                self.useFixture(f)
                config.set(section_name, 'dburi', f.dburi)

        for section_name in config.sections():
            con_match = re.match(r'^connection ([\'\"]?)(.*)(\1)$',
                                 section_name, re.I)
            if not con_match:
                continue

            if config.get(section_name, 'driver') == 'sql':
                _setup_fixture(config, section_name)

        if 'database' in config.sections():
            _setup_fixture(config, 'database')

        if not self.setupSimpleLayout(config):
            tenant_config = None
            for cfg_attr in ('tenant_config', 'tenant_config_script'):
                if hasattr(self, cfg_attr + '_file'):
                    if getattr(self, cfg_attr + '_file'):
                        value = getattr(self, cfg_attr + '_file')
                        config.set('scheduler', cfg_attr, value)
                        tenant_config = value
                    else:
                        config.remove_option('scheduler', cfg_attr)

            if tenant_config:
                git_path = os.path.join(
                    os.path.dirname(
                        os.path.join(FIXTURE_DIR, tenant_config)),
                    'git')
                if os.path.exists(git_path):
                    for reponame in os.listdir(git_path):
                        project = reponame.replace('_', '/')
                        self.copyDirToRepo(project,
                                           os.path.join(git_path, reponame))
        # Make test_root persist after ansible run for .flag test
        config.set('executor', 'trusted_rw_paths', self.test_root)

        return config

    def setupSimpleLayout(self, config: ConfigParser):
        # If the test method has been decorated with a simple_layout,
        # use that instead of the class tenant_config_file.  Set up a
        # single config-project with the specified layout, and
        # initialize repos for all of the 'project' entries which
        # appear in the layout.
        test_name = self.id().split('.')[-1]
        test = getattr(self, test_name)
        if hasattr(test, '__simple_layout__'):
            path, driver = getattr(test, '__simple_layout__')
        else:
            return False

        files = {}
        path = os.path.join(FIXTURE_DIR, path)
        with open(path) as f:
            data = f.read()
            layout = yaml.safe_load(data)
            files['zuul.yaml'] = data
        untrusted_projects = []
        for item in layout:
            if 'project' in item:
                name = item['project']['name']
                if name.startswith('^'):
                    continue
                untrusted_projects.append(name)
                self.init_repo(name)
                self.addCommitToRepo(name, 'initial commit',
                                     files={'README': ''},
                                     branch='master', tag='init')
            if 'job' in item:
                if 'run' in item['job']:
                    files['%s' % item['job']['run']] = ''
                for fn in zuul.configloader.as_list(
                        item['job'].get('pre-run', [])):
                    files['%s' % fn] = ''
                for fn in zuul.configloader.as_list(
                        item['job'].get('post-run', [])):
                    files['%s' % fn] = ''

        root = os.path.join(self.test_root, "config")
        if not os.path.exists(root):
            os.makedirs(root)
        f = tempfile.NamedTemporaryFile(dir=root, delete=False)
        temp_config = [{
            'tenant': {
                'name': 'tenant-one',
                'source': {
                    driver: {
                        'config-projects': ['org/common-config'],
                        'untrusted-projects': untrusted_projects}}}}]
        f.write(yaml.dump(temp_config).encode('utf8'))
        f.close()
        config.set('scheduler', 'tenant_config',
                   os.path.join(FIXTURE_DIR, f.name))

        self.init_repo('org/common-config')
        self.addCommitToRepo('org/common-config', 'add content from fixture',
                             files, branch='master', tag='init')

        return True

    def setupAllProjectKeys(self, config: ConfigParser):
        if self.create_project_keys:
            return

        path = config.get('scheduler', 'tenant_config')
        with open(os.path.join(FIXTURE_DIR, path)) as f:
            tenant_config = yaml.safe_load(f.read())
        for tenant in tenant_config:
            if 'tenant' not in tenant.keys():
                continue
            sources = tenant['tenant']['source']
            for source, conf in sources.items():
                for project in conf.get('config-projects', []):
                    self.setupProjectKeys(source, project)
                for project in conf.get('untrusted-projects', []):
                    self.setupProjectKeys(source, project)

    def setupProjectKeys(self, source, project):
        # Make sure we set up an RSA key for the project so that we
        # don't spend time generating one:
        if isinstance(project, dict):
            project = list(project.keys())[0]

        password = self.config.get("keystore", "password")
        keystore = zuul.lib.keystorage.KeyStorage(
            self.zk_client, password=password)
        import_keys = {}
        import_data = {'keys': import_keys}

        path = keystore.getProjectSecretsKeysPath(source, project)
        with open(os.path.join(FIXTURE_DIR, 'secrets.json'), 'rb') as i:
            import_keys[path] = json.load(i)

        # ssh key
        path = keystore.getSSHKeysPath(source, project)
        with open(os.path.join(FIXTURE_DIR, 'ssh.json'), 'rb') as i:
            import_keys[path] = json.load(i)

        keystore.importKeys(import_data, False)

    def copyDirToRepo(self, project, source_path):
        self.init_repo(project)

        files = {}
        for (dirpath, dirnames, filenames) in os.walk(source_path):
            for filename in filenames:
                test_tree_filepath = os.path.join(dirpath, filename)
                common_path = os.path.commonprefix([test_tree_filepath,
                                                    source_path])
                relative_filepath = test_tree_filepath[len(common_path) + 1:]
                with open(test_tree_filepath, 'rb') as f:
                    content = f.read()
                    # dynamically create symlinks if the content is of the form
                    # symlink: <target>
                    match = re.match(rb'symlink: ([^\s]+)', content)
                    if match:
                        content = SymLink(match.group(1))

                files[relative_filepath] = content
        self.addCommitToRepo(project, 'add content from fixture',
                             files, branch='master', tag='init')

    def assertNodepoolState(self):
        # Make sure that there are no pending requests

        requests = None
        for x in iterate_timeout(30, "zk getNodeRequests"):
            try:
                requests = self.fake_nodepool.getNodeRequests()
                break
            except kazoo.exceptions.ConnectionLoss:
                # NOTE(pabelanger): We lost access to zookeeper, iterate again
                pass
        self.assertEqual(len(requests), 0)

        nodes = None

        for x in iterate_timeout(30, "zk getNodeRequests"):
            try:
                nodes = self.fake_nodepool.getNodes()
                break
            except kazoo.exceptions.ConnectionLoss:
                # NOTE(pabelanger): We lost access to zookeeper, iterate again
                pass

        for node in nodes:
            self.assertFalse(node['_lock'], "Node %s is locked" %
                             (node['_oid'],))

    def assertNoGeneratedKeys(self):
        # Make sure that Zuul did not generate any project keys
        # (unless it was supposed to).

        if self.create_project_keys:
            return

        test_keys = []
        key_fns = ['private.pem', 'ssh.pem']
        for fn in key_fns:
            with open(os.path.join(FIXTURE_DIR, fn)) as i:
                test_keys.append(i.read())

        key_root = os.path.join(self.state_root, 'keys')
        for root, dirname, files in os.walk(key_root):
            for fn in files:
                if fn == '.version':
                    continue
                with open(os.path.join(root, fn)) as f:
                    self.assertTrue(f.read() in test_keys)

    def assertSQLState(self):
        reporter = self.scheds.first.connections.getSqlReporter(None)
        with self.scheds.first.connections.getSqlConnection().\
             engine.connect() as conn:

            try:
                result = conn.execute(
                    sqlalchemy.sql.select(
                        reporter.connection.zuul_buildset_table)
                )
            except sqlalchemy.exc.ProgrammingError:
                # Table doesn't exist
                return

            for buildset in result.fetchall():
                self.assertIsNotNone(buildset.result)

            result = conn.execute(
                sqlalchemy.sql.select(reporter.connection.zuul_build_table)
            )

            for build in result.fetchall():
                self.assertIsNotNone(build.result)
                self.assertIsNotNone(build.start_time)
                self.assertIsNotNone(build.end_time)

    def assertFinalState(self):
        self.log.debug("Assert final state")
        # Make sure no jobs are running
        self.assertEqual({}, self.executor_server.job_workers)
        # Make sure that git.Repo objects have been garbage collected.
        gc.disable()
        try:
            gc.collect()
            for obj in gc.get_objects():
                if isinstance(obj, git.Repo):
                    self.log.debug("Leaked git repo object: 0x%x %s" %
                                   (id(obj), repr(obj)))
        finally:
            gc.enable()
        if len(self.scheds) > 1:
            self.refreshPipelines(self.scheds.first.sched)
        self.assertEmptyQueues()
        self.assertNodepoolState()
        self.assertNoGeneratedKeys()
        self.assertSQLState()
        self.assertCleanZooKeeper()
        ipm = zuul.manager.independent.IndependentPipelineManager
        for tenant in self.scheds.first.sched.abide.tenants.values():
            for pipeline in tenant.layout.pipelines.values():
                if isinstance(pipeline.manager, ipm):
                    self.assertEqual(len(pipeline.queues), 0)

    def shutdown(self):
        self.log.debug("Shutting down after tests")
        self.executor_server.hold_jobs_in_build = False
        self.executor_server.release()
        self.scheds.execute(lambda app: app.sched.executor.stop())
        if self.merge_server:
            self.merge_server.stop()
            self.merge_server.join()

        self.executor_server.stop()
        self.executor_server.join()
        self.scheds.execute(lambda app: app.sched.stop())
        self.scheds.execute(lambda app: app.sched.join())
        self.statsd.stop()
        self.statsd.join()
        self.rpcclient.shutdown()
        self.gearman_server.shutdown()
        self.fake_nodepool.stop()
        self.zk_client.disconnect()
        self.printHistory()
        # We whitelist watchdog threads as they have relatively long delays
        # before noticing they should exit, but they should exit on their own.
        whitelist = ['watchdog',
                     'socketserver_Thread',
                     'cleanup start',
                     ]
        # Ignore threads that start with
        # * Thread- : Kazoo TreeCache
        # * Dummy-  : Seen during debugging in VS Code
        # * pydevd  : Debug helper threads of pydevd (used by many IDEs)
        # * ptvsd   : Debug helper threads used by VS Code
        threads = [t for t in threading.enumerate()
                   if t.name not in whitelist
                   and not t.name.startswith("Thread-")
                   and not t.name.startswith('Dummy-')
                   and not t.name.startswith('pydevd.')
                   and not t.name.startswith('ptvsd.')
                   ]
        if len(threads) > 1:
            thread_map = dict(map(lambda x: (x.ident, x.name),
                                  threading.enumerate()))
            log_str = ""
            for thread_id, stack_frame in sys._current_frames().items():
                log_str += "Thread id: %s, name: %s\n" % (
                    thread_id, thread_map.get(thread_id, 'UNKNOWN'))
                log_str += "".join(traceback.format_stack(stack_frame))
            self.log.debug(log_str)
            raise Exception("More than one thread is running: %s" % threads)

    def assertCleanShutdown(self):
        pass

    def init_repo(self, project, tag=None):
        parts = project.split('/')
        path = os.path.join(self.upstream_root, *parts[:-1])
        if not os.path.exists(path):
            os.makedirs(path)
        path = os.path.join(self.upstream_root, project)
        repo = git.Repo.init(path)

        with repo.config_writer() as config_writer:
            config_writer.set_value('user', 'email', 'user@example.com')
            config_writer.set_value('user', 'name', 'User Name')

        repo.index.commit('initial commit')
        master = repo.create_head('master')
        if tag:
            repo.create_tag(tag)

        repo.head.reference = master
        repo.head.reset(working_tree=True)
        repo.git.clean('-x', '-f', '-d')

    def create_branch(self, project, branch, commit_filename='README'):
        path = os.path.join(self.upstream_root, project)
        repo = git.Repo(path)
        fn = os.path.join(path, commit_filename)

        branch_head = repo.create_head(branch)
        repo.head.reference = branch_head
        f = open(fn, 'a')
        f.write("test %s\n" % branch)
        f.close()
        repo.index.add([fn])
        repo.index.commit('%s commit' % branch)

        repo.head.reference = repo.heads['master']
        repo.head.reset(working_tree=True)
        repo.git.clean('-x', '-f', '-d')

    def delete_branch(self, project, branch):
        path = os.path.join(self.upstream_root, project)
        repo = git.Repo(path)
        repo.head.reference = repo.heads['master']
        repo.head.reset(working_tree=True)
        repo.delete_head(repo.heads[branch], force=True)

    def create_commit(self, project, files=None, head='master',
                      message='Creating a fake commit', **kwargs):
        path = os.path.join(self.upstream_root, project)
        repo = git.Repo(path)
        repo.head.reference = repo.heads[head]
        repo.head.reset(index=True, working_tree=True)

        files = files or {"README": "creating fake commit\n"}
        for name, content in files.items():
            file_name = os.path.join(path, name)
            with open(file_name, 'a') as f:
                f.write(content)
            repo.index.add([file_name])
        commit = repo.index.commit(message, **kwargs)
        return commit.hexsha

    def orderedRelease(self, count=None):
        # Run one build at a time to ensure non-race order:
        i = 0
        while len(self.builds):
            self.release(self.builds[0])
            self.waitUntilSettled()
            i += 1
            if count is not None and i >= count:
                break

    def getSortedBuilds(self):
        "Return the list of currently running builds sorted by name"

        return sorted(self.builds, key=lambda x: x.name)

    def getCurrentBuilds(self):
        for tenant in self.scheds.first.sched.abide.tenants.values():
            for pipeline in tenant.layout.pipelines.values():
                for item in pipeline.getAllItems():
                    for build in item.current_build_set.builds.values():
                        yield build

    def release(self, job):
        job.release()

    @property
    def sched_zk_nodepool(self):
        return self.scheds.first.sched.nodepool.zk_nodepool

    @property
    def hold_jobs_in_queue(self):
        return self.executor_api.hold_in_queue

    @hold_jobs_in_queue.setter
    def hold_jobs_in_queue(self, hold_in_queue):
        """Helper method to set hold_in_queue on all involved Executor APIs"""

        self.executor_api.hold_in_queue = hold_in_queue
        for app in self.scheds:
            app.sched.executor.executor_api.hold_in_queue = hold_in_queue

    @property
    def hold_merge_jobs_in_queue(self):
        return self.merger_api.hold_in_queue

    @hold_merge_jobs_in_queue.setter
    def hold_merge_jobs_in_queue(self, hold_in_queue):
        """Helper method to set hold_in_queue on all involved Merger APIs"""

        self.merger_api.hold_in_queue = hold_in_queue
        for app in self.scheds:
            app.sched.merger.merger_api.hold_in_queue = hold_in_queue

    @property
    def merge_job_history(self):
        history = defaultdict(list)
        for app in self.scheds:
            for job_type, jobs in app.sched.merger.merger_api.history.items():
                history[job_type].extend(jobs)
        return history

    @merge_job_history.deleter
    def merge_job_history(self):
        for app in self.scheds:
            app.sched.merger.merger_api.history.clear()

    def waitUntilNodeCacheSync(self, zk_nodepool):
        """Wait until the node cache on the zk_nodepool object is in sync"""
        for _ in iterate_timeout(60, 'wait for node cache sync'):
            cache_state = {}
            zk_state = {}
            for n in self.fake_nodepool.getNodes():
                zk_state[n['_oid']] = n['state']
            for nid in zk_nodepool.getNodes(cached=True):
                n = zk_nodepool.getNode(nid)
                cache_state[n.id] = n.state
            if cache_state == zk_state:
                return

    def __haveAllBuildsReported(self):
        # The build requests will be deleted from ZooKeeper once the
        # scheduler processed their result event. Thus, as long as
        # there are build requests left in ZooKeeper, the system is
        # not stable.
        for build in self.history:
            try:
                self.zk_client.client.get(build.build_request_ref)
            except NoNodeError:
                # It has already been reported
                continue
            # It hasn't been reported yet.
            return False
        return True

    def __areAllBuildsWaiting(self):
        # Look up the queued build requests directly from ZooKeeper
        queued_build_requests = list(self.executor_api.all())
        seen_builds = set()
        # Always ignore builds which are on hold
        for build_request in queued_build_requests:
            seen_builds.add(build_request.uuid)
            if build_request.state in (BuildRequest.HOLD):
                continue
            # Check if the build is currently processed by the
            # RecordingExecutorServer.
            worker_build = self.executor_server.job_builds.get(
                build_request.uuid)
            if worker_build:
                if worker_build.paused:
                    # Avoid a race between setting the resume flag and
                    # the job actually resuming.  If the build is
                    # paused, make sure that there is no resume flag
                    # and if that's true, that the build is still
                    # paused.  If there's no resume flag between two
                    # checks of the paused attr, it should still be
                    # paused.
                    if not self.zk_client.client.exists(
                            build_request.path + '/resume'):
                        if worker_build.paused:
                            continue
                if worker_build.isWaiting():
                    continue
                self.log.debug("%s is running", worker_build)
                return False
            else:
                self.log.debug("%s is unassigned", build_request)
                return False
        # Wait until all running builds have finished on the executor
        # and that all job workers are cleaned up. Otherwise there
        # could be a short window in which the build is finished
        # (and reported), but the job cleanup is not yet finished on
        # the executor. During this time the test could settle, but
        # assertFinalState() will fail because there are still
        # job_workers present on the executor.
        for build_uuid in self.executor_server.job_workers.keys():
            if build_uuid not in seen_builds:
                log = get_annotated_logger(
                    self.log, event=None, build=build_uuid
                )
                log.debug("Build is not finalized")
                return False
        return True

    def __areAllNodeRequestsComplete(self, matcher) -> bool:
        if self.fake_nodepool.paused:
            return True
        # Check ZK and the scheduler cache and make sure they are
        # in sync.
        for app in self.scheds.filter(matcher):
            sched = app.sched
            nodepool = app.sched.nodepool
            with nodepool.zk_nodepool._callback_lock:
                for req in self.fake_nodepool.getNodeRequests():
                    if req['state'] != model.STATE_FULFILLED:
                        return False
                    r2 = nodepool.zk_nodepool._node_request_cache.get(
                        req['_oid'])
                    if r2 and r2.state != req['state']:
                        return False
                    if req and not r2:
                        return False
                    tenant_name = r2.tenant_name
                    pipeline_name = r2.pipeline_name
                    if sched.pipeline_result_events[tenant_name][
                            pipeline_name
                    ].hasEvents():
                        return False
        return True

    def __areAllMergeJobsWaiting(self, matcher) -> bool:
        # Look up the queued merge jobs directly from ZooKeeper
        queued_merge_jobs = list(self.merger_api.all())
        # Always ignore merge jobs which are on hold
        for job in queued_merge_jobs:
            if job.state != MergeRequest.HOLD:
                return False
        return True

    def __eventQueuesEmpty(self, matcher=None) -> Generator[bool, None, None]:
        for event_queue in self.__event_queues(matcher):
            yield not event_queue.unfinished_tasks

    def __eventQueuesJoin(self, matcher) -> None:
        for app in self.scheds.filter(matcher):
            for event_queue in app.event_queues:
                event_queue.join()
        for event_queue in self.additional_event_queues:
            event_queue.join()

    def __areZooKeeperEventQueuesEmpty(self, matcher=None) -> bool:
        for sched in map(lambda app: app.sched, self.scheds.filter(matcher)):
            for connection_name in sched.connections.connections:
                if self.connection_event_queues[connection_name].hasEvents():
                    return False
            for tenant in sched.abide.tenants.values():
                if sched.management_events[tenant.name].hasEvents():
                    return False
                if sched.trigger_events[tenant.name].hasEvents():
                    return False
                for pipeline_name in tenant.layout.pipelines:
                    if sched.pipeline_management_events[tenant.name][
                        pipeline_name
                    ].hasEvents():
                        return False
                    if sched.pipeline_trigger_events[tenant.name][
                        pipeline_name
                    ].hasEvents():
                        return False
                    if sched.pipeline_result_events[tenant.name][
                        pipeline_name
                    ].hasEvents():
                        return False
        return True

    def __areAllSchedulersPrimed(self, matcher=None):
        for app in self.scheds.filter(matcher):
            if app.sched.last_reconfigured is None:
                return False
        return True

    def waitUntilSettled(self, msg="", matcher=None) -> None:
        self.log.debug("Waiting until settled... (%s)", msg)
        start = time.time()
        i = 0
        while True:
            i = i + 1
            if time.time() - start > self.wait_timeout:
                self.log.error("Timeout waiting for Zuul to settle")
                self.log.debug("All schedulers primed: %s",
                               self.__areAllSchedulersPrimed(matcher))
                self._logQueueStatus(
                    self.log.error, matcher,
                    self.__areZooKeeperEventQueuesEmpty(matcher),
                    self.__areAllMergeJobsWaiting(matcher),
                    self.__haveAllBuildsReported(),
                    self.__areAllBuildsWaiting(),
                    self.__areAllNodeRequestsComplete(matcher),
                    all(self.__eventQueuesEmpty(matcher))
                )
                raise Exception("Timeout waiting for Zuul to settle")

            # Make sure no new events show up while we're checking
            self.executor_server.lock.acquire()

            # have all build states propogated to zuul?
            if self.__haveAllBuildsReported():
                # Join ensures that the queue is empty _and_ events have been
                # processed
                self.__eventQueuesJoin(matcher)
                for sched in map(lambda app: app.sched,
                                 self.scheds.filter(matcher)):
                    sched.run_handler_lock.acquire()
                if (self.__areAllSchedulersPrimed(matcher) and
                    self.__areAllMergeJobsWaiting(matcher) and
                    self.__haveAllBuildsReported() and
                    self.__areAllBuildsWaiting() and
                    self.__areAllNodeRequestsComplete(matcher) and
                    self.__areZooKeeperEventQueuesEmpty(matcher) and
                    all(self.__eventQueuesEmpty(matcher))):
                    # The queue empty check is placed at the end to
                    # ensure that if a component adds an event between
                    # when locked the run handler and checked that the
                    # components were stable, we don't erroneously
                    # report that we are settled.
                    for sched in map(lambda app: app.sched,
                                     self.scheds.filter(matcher)):
                        if len(self.scheds) > 1:
                            self.refreshPipelines(sched)
                        sched.run_handler_lock.release()
                    self.executor_server.lock.release()
                    self.log.debug("...settled after %.3f ms / %s loops (%s)",
                                   time.time() - start, i, msg)
                    self.logState()
                    return
                for sched in map(lambda app: app.sched,
                                 self.scheds.filter(matcher)):
                    sched.run_handler_lock.release()
            self.executor_server.lock.release()
            for sched in map(lambda app: app.sched,
                             self.scheds.filter(matcher)):
                sched.wake_event.wait(0.1)
            # Let other threads work
            time.sleep(0.1)

    def refreshPipelines(self, sched):
        for tenant in sched.abide.tenants.values():
            with tenant_read_lock(self.zk_client, tenant.name):
                for pipeline in tenant.layout.pipelines.values():
                    with pipeline_lock(
                        self.zk_client, tenant.name, pipeline.name
                    ) as lock:
                        ctx = self.createZKContext(lock)
                        with pipeline.manager.currentContext(ctx):
                            pipeline.state.refresh(ctx)

    def _logQueueStatus(self, logger, matcher, all_zk_queues_empty,
                        all_merge_jobs_waiting, all_builds_reported,
                        all_builds_waiting, all_node_requests_completed,
                        all_event_queues_empty):
        logger("Queue status:")
        for event_queue in self.__event_queues(matcher):
            is_empty = not event_queue.unfinished_tasks
            self.log.debug("  %s: %s", event_queue, is_empty)
        logger("All ZK event queues empty: %s", all_zk_queues_empty)
        logger("All merge jobs waiting: %s", all_merge_jobs_waiting)
        logger("All builds reported: %s", all_builds_reported)
        logger("All builds waiting: %s", all_builds_waiting)
        logger("All requests completed: %s", all_node_requests_completed)
        logger("All event queues empty: %s", all_event_queues_empty)

    def waitForPoll(self, poller, timeout=30):
        self.log.debug("Wait for poll on %s", poller)
        self.poller_events[poller].clear()
        self.log.debug("Waiting for poll 1 on %s", poller)
        self.poller_events[poller].wait(timeout)
        self.poller_events[poller].clear()
        self.log.debug("Waiting for poll 2 on %s", poller)
        self.poller_events[poller].wait(timeout)
        self.log.debug("Done waiting for poll on %s", poller)

    def logState(self):
        """ Log the current state of the system """
        self.log.info("Begin state dump --------------------")
        for build in self.history:
            self.log.info("Completed build: %s" % build)
        for build in self.builds:
            self.log.info("Running build: %s" % build)
        for tenant in self.scheds.first.sched.abide.tenants.values():
            for pipeline in tenant.layout.pipelines.values():
                for pipeline_queue in pipeline.queues:
                    if len(pipeline_queue.queue) != 0:
                        status = ''
                        for item in pipeline_queue.queue:
                            status += item.formatStatus()
                        self.log.info(
                            'Tenant %s pipeline %s queue %s contents:' % (
                                tenant.name, pipeline.name,
                                pipeline_queue.name))
                        for l in status.split('\n'):
                            if l.strip():
                                self.log.info(l)
        self.log.info("End state dump --------------------")

    def countJobResults(self, jobs, result):
        jobs = filter(lambda x: x.result == result, jobs)
        return len(list(jobs))

    def getBuildByName(self, name):
        for build in self.builds:
            if build.name == name:
                return build
        raise Exception("Unable to find build %s" % name)

    def assertJobNotInHistory(self, name, project=None):
        for job in self.history:
            if (project is None or
                job.parameters['zuul']['project']['name'] == project):
                self.assertNotEqual(job.name, name,
                                    'Job %s found in history' % name)

    def getJobFromHistory(self, name, project=None, result=None, branch=None):
        for job in self.history:
            if (job.name == name and
                (project is None or
                 job.parameters['zuul']['project']['name'] == project) and
                (result is None or job.result == result) and
                (branch is None or
                 job.parameters['zuul']['branch'] == branch)):
                return job
        raise Exception("Unable to find job %s in history" % name)

    def assertEmptyQueues(self):
        # Make sure there are no orphaned jobs
        for tenant in self.scheds.first.sched.abide.tenants.values():
            for pipeline in tenant.layout.pipelines.values():
                for pipeline_queue in pipeline.queues:
                    if len(pipeline_queue.queue) != 0:
                        print('pipeline %s queue %s contents %s' % (
                            pipeline.name, pipeline_queue.name,
                            pipeline_queue.queue))
                    self.assertEqual(len(pipeline_queue.queue), 0,
                                     "Pipelines queues should be empty")

    def assertCleanZooKeeper(self):
        # Make sure there are no extraneous ZK nodes
        client = self.merger_api
        self.assertEqual(self.getZKPaths(client.REQUEST_ROOT), [])
        self.assertEqual(self.getZKPaths(client.PARAM_ROOT), [])
        self.assertEqual(self.getZKPaths(client.RESULT_ROOT), [])
        self.assertEqual(self.getZKPaths(client.RESULT_DATA_ROOT), [])
        self.assertEqual(self.getZKPaths(client.WAITER_ROOT), [])
        self.assertEqual(self.getZKPaths(client.LOCK_ROOT), [])

    def assertReportedStat(self, key, value=None, kind=None, timeout=5):
        """Check statsd output

        Check statsd return values.  A ``value`` should specify a
        ``kind``, however a ``kind`` may be specified without a
        ``value`` for a generic match.  Leave both empy to just check
        for key presence.

        :arg str key: The statsd key
        :arg str value: The expected value of the metric ``key``
        :arg str kind: The expected type of the metric ``key``  For example

          - ``c`` counter
          - ``g`` gauge
          - ``ms`` timing
          - ``s`` set

        :arg int timeout: How long to wait for the stat to appear

        :returns: The value
        """

        if value:
            self.assertNotEqual(kind, None)

        start = time.time()
        while time.time() <= (start + timeout):
            # Note our fake statsd just queues up results in a queue.
            # We just keep going through them until we find one that
            # matches, or fail out.  If statsd pipelines are used,
            # large single packets are sent with stats separated by
            # newlines; thus we first flatten the stats out into
            # single entries.
            stats = list(itertools.chain.from_iterable(
                [s.decode('utf-8').split('\n') for s in self.statsd.stats]))

            # Check that we don't have already have a counter value
            # that we then try to extend a sub-key under; this doesn't
            # work on the server.  e.g.
            #  zuul.new.stat            is already a counter
            #  zuul.new.stat.sub.value  will silently not work
            #
            # note only valid for gauges and counters; timers are
            # slightly different because statsd flushes them out but
            # actually writes a bunch of different keys like "mean,
            # std, count", so the "key" isn't so much a key, but a
            # path to the folder where the actual values will be kept.
            # Thus you can extend timer keys OK.
            already_set_keys = set()
            for stat in stats:
                k, v = stat.split(':')
                s_value, s_kind = v.split('|')
                if s_kind == 'c' or s_kind == 'g':
                    already_set_keys.update([k])
            for k in already_set_keys:
                if key != k and key.startswith(k):
                    raise StatException(
                        "Key %s is a gauge/counter and "
                        "we are trying to set subkey %s" % (k, key))

            for stat in stats:
                k, v = stat.split(':')
                s_value, s_kind = v.split('|')

                if key == k:
                    if kind is None:
                        # key with no qualifiers is found
                        return s_value

                    # if no kind match, look for other keys
                    if kind != s_kind:
                        continue

                    if value:
                        # special-case value|ms because statsd can turn
                        # timing results into float of indeterminate
                        # length, hence foiling string matching.
                        if kind == 'ms':
                            if float(value) == float(s_value):
                                return s_value
                        if value == s_value:
                            return s_value
                        # otherwise keep looking for other matches
                        continue

                    # this key matches
                    return s_value
            time.sleep(0.1)

        raise StatException("Key %s not found in reported stats" % key)

    def assertUnReportedStat(self, key, value=None, kind=None):
        try:
            value = self.assertReportedStat(key, value=value,
                                            kind=kind, timeout=0)
        except StatException:
            return
        raise StatException("Key %s found in reported stats: %s" %
                            (key, value))

    def assertBuilds(self, builds):
        """Assert that the running builds are as described.

        The list of running builds is examined and must match exactly
        the list of builds described by the input.

        :arg list builds: A list of dictionaries.  Each item in the
            list must match the corresponding build in the build
            history, and each element of the dictionary must match the
            corresponding attribute of the build.

        """
        try:
            self.assertEqual(len(self.builds), len(builds))
            for i, d in enumerate(builds):
                for k, v in d.items():
                    self.assertEqual(
                        getattr(self.builds[i], k), v,
                        "Element %i in builds does not match" % (i,))
        except Exception:
            if not self.builds:
                self.log.error("No running builds")
            for build in self.builds:
                self.log.error("Running build: %s" % build)
            raise

    def assertHistory(self, history, ordered=True):
        """Assert that the completed builds are as described.

        The list of completed builds is examined and must match
        exactly the list of builds described by the input.

        :arg list history: A list of dictionaries.  Each item in the
            list must match the corresponding build in the build
            history, and each element of the dictionary must match the
            corresponding attribute of the build.

        :arg bool ordered: If true, the history must match the order
            supplied, if false, the builds are permitted to have
            arrived in any order.

        """
        def matches(history_item, item):
            for k, v in item.items():
                if getattr(history_item, k) != v:
                    return False
            return True
        try:
            self.assertEqual(len(self.history), len(history))
            if ordered:
                for i, d in enumerate(history):
                    if not matches(self.history[i], d):
                        raise Exception(
                            "Element %i in history does not match %s" %
                            (i, self.history[i]))
            else:
                unseen = self.history[:]
                for i, d in enumerate(history):
                    found = False
                    for unseen_item in unseen:
                        if matches(unseen_item, d):
                            found = True
                            unseen.remove(unseen_item)
                            break
                    if not found:
                        raise Exception("No match found for element %i "
                                        "in history" % (i,))
                if unseen:
                    raise Exception("Unexpected items in history")
        except Exception:
            for build in self.history:
                self.log.error("Completed build: %s" % build)
            if not self.history:
                self.log.error("No completed builds")
            raise

    def printHistory(self):
        """Log the build history.

        This can be useful during tests to summarize what jobs have
        completed.

        """
        if not self.history:
            self.log.debug("Build history: no builds ran")
            return

        self.log.debug("Build history:")
        for build in self.history:
            self.log.debug(build)

    def updateConfigLayout(self, path):
        root = os.path.join(self.test_root, "config")
        if not os.path.exists(root):
            os.makedirs(root)
        f = tempfile.NamedTemporaryFile(dir=root, delete=False)
        f.write("""
- tenant:
    name: openstack
    source:
      gerrit:
        config-projects:
          - %s
        untrusted-projects:
          - org/project
          - org/project1
          - org/project2\n""" % path)
        f.close()
        self.config.set('scheduler', 'tenant_config',
                        os.path.join(FIXTURE_DIR, f.name))
        self.setupAllProjectKeys(self.config)

    def addTagToRepo(self, project, name, sha):
        path = os.path.join(self.upstream_root, project)
        repo = git.Repo(path)
        repo.git.tag(name, sha)

    def delTagFromRepo(self, project, name):
        path = os.path.join(self.upstream_root, project)
        repo = git.Repo(path)
        repo.git.tag('-d', name)

    def addCommitToRepo(self, project, message, files,
                        branch='master', tag=None):
        path = os.path.join(self.upstream_root, project)
        repo = git.Repo(path)
        repo.head.reference = branch
        repo.head.reset(working_tree=True)
        for fn, content in files.items():
            fn = os.path.join(path, fn)
            try:
                os.makedirs(os.path.dirname(fn))
            except OSError:
                pass
            if isinstance(content, SymLink):
                os.symlink(content.target, fn)
            else:
                mode = 'w'
                if isinstance(content, bytes):
                    # the file fixtures are loaded as bytes such that
                    # we also support binary files
                    mode = 'wb'
                with open(fn, mode) as f:
                    f.write(content)
            repo.index.add([fn])
        commit = repo.index.commit(message)
        before = repo.heads[branch].commit
        repo.heads[branch].commit = commit
        repo.head.reference = branch
        repo.git.clean('-x', '-f', '-d')
        repo.heads[branch].checkout()
        if tag:
            repo.create_tag(tag)
        return before

    def commitConfigUpdate(self, project_name, source_name):
        """Commit an update to zuul.yaml

        This overwrites the zuul.yaml in the specificed project with
        the contents specified.

        :arg str project_name: The name of the project containing
            zuul.yaml (e.g., common-config)

        :arg str source_name: The path to the file (underneath the
            test fixture directory) whose contents should be used to
            replace zuul.yaml.
        """

        source_path = os.path.join(FIXTURE_DIR, source_name)
        files = {}
        with open(source_path, 'r') as f:
            data = f.read()
            layout = yaml.safe_load(data)
            files['zuul.yaml'] = data
        for item in layout:
            if 'job' in item:
                jobname = item['job']['name']
                files['playbooks/%s.yaml' % jobname] = ''
        before = self.addCommitToRepo(
            project_name, 'Pulling content from %s' % source_name,
            files)
        return before

    def newTenantConfig(self, source_name):
        """ Use this to update the tenant config file in tests

        This will update self.tenant_config_file to point to a temporary file
        for the duration of this particular test. The content of that file will
        be taken from FIXTURE_DIR/source_name

        After the test the original value of self.tenant_config_file will be
        restored.

        :arg str source_name: The path of the file under
            FIXTURE_DIR that will be used to populate the new tenant
            config file.
        """
        source_path = os.path.join(FIXTURE_DIR, source_name)
        orig_tenant_config_file = self.tenant_config_file
        with tempfile.NamedTemporaryFile(
            delete=False, mode='wb') as new_tenant_config:
            self.tenant_config_file = new_tenant_config.name
            with open(source_path, mode='rb') as source_tenant_config:
                new_tenant_config.write(source_tenant_config.read())
        for app in self.scheds.instances:
            app.config['scheduler']['tenant_config'] = self.tenant_config_file
        self.config['scheduler']['tenant_config'] = self.tenant_config_file
        self.setupAllProjectKeys(self.config)
        self.log.debug(
            'tenant_config_file = {}'.format(self.tenant_config_file))

        def _restoreTenantConfig():
            self.log.debug(
                'restoring tenant_config_file = {}'.format(
                    orig_tenant_config_file))
            os.unlink(self.tenant_config_file)
            self.tenant_config_file = orig_tenant_config_file
            self.config['scheduler']['tenant_config'] = orig_tenant_config_file
        self.addCleanup(_restoreTenantConfig)

    def addEvent(self, connection, event):
        """Inject a Fake (Gerrit) event.

        This method accepts a JSON-encoded event and simulates Zuul
        having received it from Gerrit.  It could (and should)
        eventually apply to any connection type, but is currently only
        used with Gerrit connections.  The name of the connection is
        used to look up the corresponding server, and the event is
        simulated as having been received by all Zuul connections
        attached to that server.  So if two Gerrit connections in Zuul
        are connected to the same Gerrit server, and you invoke this
        method specifying the name of one of them, the event will be
        received by both.

        .. note::

            "self.fake_gerrit.addEvent" calls should be migrated to
            this method.

        :arg str connection: The name of the connection corresponding
            to the gerrit server.
        :arg str event: The JSON-encoded event.

        """
        specified_conn = self.scheds.first.connections.connections[connection]
        for conn in self.scheds.first.connections.connections.values():
            if (isinstance(conn, specified_conn.__class__) and
                specified_conn.server == conn.server):
                conn.addEvent(event)

    def getUpstreamRepos(self, projects):
        """Return upstream git repo objects for the listed projects

        :arg list projects: A list of strings, each the canonical name
                            of a project.

        :returns: A dictionary of {name: repo} for every listed
                  project.
        :rtype: dict

        """

        repos = {}
        for project in projects:
            # FIXME(jeblair): the upstream root does not yet have a
            # hostname component; that needs to be added, and this
            # line removed:
            tmp_project_name = '/'.join(project.split('/')[1:])
            path = os.path.join(self.upstream_root, tmp_project_name)
            repo = git.Repo(path)
            repos[project] = repo
        return repos


class AnsibleZuulTestCase(ZuulTestCase):
    """ZuulTestCase but with an actual ansible executor running"""
    run_ansible = True

    @contextmanager
    def jobLog(self, build):
        """Print job logs on assertion errors

        This method is a context manager which, if it encounters an
        ecxeption, adds the build log to the debug output.

        :arg Build build: The build that's being asserted.
        """
        try:
            yield
        except Exception:
            path = os.path.join(self.jobdir_root, build.uuid,
                                'work', 'logs', 'job-output.txt')
            with open(path) as f:
                self.log.debug(f.read())
            path = os.path.join(self.jobdir_root, build.uuid,
                                'work', 'logs', 'job-output.json')
            with open(path) as f:
                self.log.debug(f.read())
            raise


class SSLZuulTestCase(ZuulTestCase):
    """ZuulTestCase but using SSL when possible"""
    use_ssl = True


class ZuulGithubAppTestCase(ZuulTestCase):
    def setup_config(self, config_file: str):
        config = super(ZuulGithubAppTestCase, self).setup_config(config_file)
        for section_name in config.sections():
            con_match = re.match(r'^connection ([\'\"]?)(.*)(\1)$',
                                 section_name, re.I)
            if not con_match:
                continue

            if config.get(section_name, 'driver') == 'github':
                if (config.get(section_name, 'app_key',
                               fallback=None) ==
                    '$APP_KEY_FIXTURE$'):
                    config.set(section_name, 'app_key',
                               os.path.join(FIXTURE_DIR, 'app_key'))
        return config
