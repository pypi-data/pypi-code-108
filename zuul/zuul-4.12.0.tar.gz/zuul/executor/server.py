# Copyright 2014 OpenStack Foundation
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

import collections
import datetime
import json
import logging
import multiprocessing
import os
import psutil
import re
import shutil
import signal
import shlex
import socket
import subprocess
import tempfile
import threading
import time
import traceback
from concurrent.futures.process import ProcessPoolExecutor, BrokenProcessPool

from kazoo.exceptions import NoNodeError
import git
from urllib.parse import urlsplit

from zuul.lib.ansible import AnsibleManager
from zuul.lib.result_data import get_warnings_from_result_data
from zuul.lib import yamlutil as yaml
from zuul.lib.config import get_default
from zuul.lib.logutil import get_annotated_logger
from zuul.lib.monitoring import MonitoringServer
from zuul.lib.statsd import get_statsd
from zuul.lib import filecomments
from zuul.lib.keystorage import KeyStorage
from zuul.lib.varnames import check_varnames

import zuul.lib.repl
import zuul.merger.merger
import zuul.ansible.logconfig
from zuul.executor.sensors.cpu import CPUSensor
from zuul.executor.sensors.hdd import HDDSensor
from zuul.executor.sensors.pause import PauseSensor
from zuul.executor.sensors.startingbuilds import StartingBuildsSensor
from zuul.executor.sensors.ram import RAMSensor
from zuul.executor.common import zuul_params_from_job
from zuul.lib import commandsocket
from zuul.merger.server import BaseMergeServer, RepoLocks
from zuul.model import (
    BuildCompletedEvent,
    BuildPausedEvent,
    BuildRequest,
    BuildStartedEvent,
    BuildStatusEvent,
    ExtraRepoState,
    FrozenJob,
    MergeRepoState,
)
import zuul.model
from zuul.nodepool import Nodepool
from zuul.version import get_version_string
from zuul.zk.event_queues import PipelineResultEventQueue
from zuul.zk.components import ExecutorComponent
from zuul.zk.exceptions import JobRequestNotFound
from zuul.zk.executor import ExecutorApi
from zuul.zk.job_request_queue import JobRequestEvent
from zuul.zk.system import ZuulSystem
from zuul.zk.zkobject import ZKContext

BUFFER_LINES_FOR_SYNTAX = 200
COMMANDS = ['stop', 'pause', 'unpause', 'graceful', 'verbose',
            'unverbose', 'keep', 'nokeep', 'repl', 'norepl']
DEFAULT_FINGER_PORT = 7900
DEFAULT_STREAM_PORT = 19885
BLACKLISTED_ANSIBLE_CONNECTION_TYPES = [
    'network_cli', 'kubectl', 'project', 'namespace']
BLACKLISTED_VARS = dict(
    ansible_ssh_executable='ssh',
    ansible_ssh_common_args='-o PermitLocalCommand=no',
    ansible_sftp_extra_args='-o PermitLocalCommand=no',
    ansible_scp_extra_args='-o PermitLocalCommand=no',
    ansible_ssh_extra_args='-o PermitLocalCommand=no',
)


class NodeRequestError(Exception):
    pass


class StopException(Exception):
    """An exception raised when an inner loop is asked to stop."""
    pass


class ExecutorError(Exception):
    """A non-transient run-time executor error

    This class represents error conditions detected by the executor
    when preparing to run a job which we know are consistently fatal.
    Zuul should not reschedule the build in these cases.
    """
    pass


class RoleNotFoundError(ExecutorError):
    pass


class PluginFoundError(ExecutorError):
    pass


class DiskAccountant(object):
    ''' A single thread to periodically run du and monitor a base directory

    Whenever the accountant notices a dir over limit, it will call the
    given func with an argument of the job directory. That function
    should be used to remediate the problem, generally by killing the
    job producing the disk bloat). The function will be called every
    time the problem is noticed, so it should be handled synchronously
    to avoid stacking up calls.
    '''
    log = logging.getLogger("zuul.ExecutorDiskAccountant")

    def __init__(self, jobs_base, limit, func, cache_dir, usage_func=None):
        '''
        :param str jobs_base: absolute path name of dir to be monitored
        :param int limit: maximum number of MB allowed to be in use in any one
                          subdir
        :param callable func: Function to call with overlimit dirs
        :param str cache_dir: absolute path name of dir to be passed as the
                              first argument to du. This will ensure du does
                              not count any hardlinks to files in this
                              directory against a single job.
        :param callable usage_func: Optional function to call with usage
                                    for every dir _NOT_ over limit
        '''
        # Remove any trailing slash to ensure dirname equality tests work
        cache_dir = cache_dir.rstrip('/')
        jobs_base = jobs_base.rstrip('/')
        # Don't cross the streams
        if cache_dir == jobs_base:
            raise Exception("Cache dir and jobs dir cannot be the same")
        self.thread = threading.Thread(target=self._run,
                                       name='diskaccountant')
        self.thread.daemon = True
        self._running = False
        self.jobs_base = jobs_base
        self.limit = limit
        self.func = func
        self.cache_dir = cache_dir
        self.usage_func = usage_func
        self.stop_event = threading.Event()

    def _run(self):
        while self._running:
            # Walk job base
            before = time.time()
            du = subprocess.Popen(
                ['du', '-m', '--max-depth=1', self.cache_dir, self.jobs_base],
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            for line in du.stdout:
                (size, dirname) = line.rstrip().split()
                dirname = dirname.decode('utf8')
                if dirname == self.jobs_base or dirname == self.cache_dir:
                    continue
                if os.path.dirname(dirname) == self.cache_dir:
                    continue
                size = int(size)
                if size > self.limit:
                    self.log.warning(
                        "{job} is using {size}MB (limit={limit})"
                        .format(size=size, job=dirname, limit=self.limit))
                    self.func(dirname)
                elif self.usage_func:
                    self.log.debug(
                        "{job} is using {size}MB (limit={limit})"
                        .format(size=size, job=dirname, limit=self.limit))
                    self.usage_func(dirname, size)
            du.wait()
            du.stdout.close()
            after = time.time()
            # Sleep half as long as that took, or 1s, whichever is longer
            delay_time = max((after - before) / 2, 1.0)
            self.stop_event.wait(delay_time)

    def start(self):
        if self.limit < 0:
            # No need to start if there is no limit.
            return
        self._running = True
        self.thread.start()

    def stop(self):
        if not self.running:
            return
        self._running = False
        self.stop_event.set()
        self.thread.join()

    @property
    def running(self):
        return self._running


class Watchdog(object):
    def __init__(self, timeout, function, args):
        self.timeout = timeout
        self.function = function
        self.args = args
        self.thread = threading.Thread(target=self._run,
                                       name='watchdog')
        self.thread.daemon = True
        self.timed_out = None

        self.end = 0

        self._running = False
        self._stop_event = threading.Event()

    def _run(self):
        while self._running and time.time() < self.end:
            self._stop_event.wait(10)
        if self._running:
            self.timed_out = True
            self.function(*self.args)
        else:
            # Only set timed_out to false if we aren't _running
            # anymore. This means that we stopped running not because
            # of a timeout but because normal execution ended.
            self.timed_out = False

    def start(self):
        self._running = True
        self.end = time.time() + self.timeout
        self.thread.start()

    def stop(self):
        self._running = False
        self._stop_event.set()


class SshAgent(object):

    def __init__(self, zuul_event_id=None, build=None):
        self.env = {}
        self.ssh_agent = None
        self.log = get_annotated_logger(
            logging.getLogger("zuul.ExecutorServer"),
            zuul_event_id, build=build)

    def start(self):
        if self.ssh_agent:
            return
        with open('/dev/null', 'r+') as devnull:
            ssh_agent = subprocess.Popen(['ssh-agent'], close_fds=True,
                                         stdout=subprocess.PIPE,
                                         stderr=devnull,
                                         stdin=devnull)
        (output, _) = ssh_agent.communicate()
        output = output.decode('utf8')
        for line in output.split("\n"):
            if '=' in line:
                line = line.split(";", 1)[0]
                (key, value) = line.split('=')
                self.env[key] = value
        self.log.info('Started SSH Agent, {}'.format(self.env))

    def stop(self):
        if 'SSH_AGENT_PID' in self.env:
            try:
                os.kill(int(self.env['SSH_AGENT_PID']), signal.SIGTERM)
            except OSError:
                self.log.exception(
                    'Problem sending SIGTERM to agent {}'.format(self.env))
            self.log.debug('Sent SIGTERM to SSH Agent, {}'.format(self.env))
            self.env = {}

    def __del__(self):
        try:
            self.stop()
        except Exception:
            self.log.exception('Exception in SshAgent destructor')
        try:
            super().__del__(self)
        except AttributeError:
            pass

    def add(self, key_path):
        env = os.environ.copy()
        env.update(self.env)
        key_path = os.path.expanduser(key_path)
        self.log.debug('Adding SSH Key {}'.format(key_path))
        try:
            subprocess.check_output(['ssh-add', key_path], env=env,
                                    stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            self.log.exception('ssh-add failed. stdout: %s, stderr: %s',
                               e.output, e.stderr)
            raise
        self.log.info('Added SSH Key {}'.format(key_path))

    def addData(self, name, key_data):
        env = os.environ.copy()
        env.update(self.env)
        self.log.debug('Adding SSH Key {}'.format(name))
        try:
            subprocess.check_output(['ssh-add', '-'], env=env,
                                    input=key_data.encode('utf8'),
                                    stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            self.log.exception('ssh-add failed. stdout: %s, stderr: %s',
                               e.output, e.stderr)
            raise
        self.log.info('Added SSH Key {}'.format(name))

    def remove(self, key_path):
        env = os.environ.copy()
        env.update(self.env)
        key_path = os.path.expanduser(key_path)
        self.log.debug('Removing SSH Key {}'.format(key_path))
        subprocess.check_output(['ssh-add', '-d', key_path], env=env,
                                stderr=subprocess.PIPE)
        self.log.info('Removed SSH Key {}'.format(key_path))

    def list(self):
        if 'SSH_AUTH_SOCK' not in self.env:
            return None
        env = os.environ.copy()
        env.update(self.env)
        result = []
        for line in subprocess.Popen(['ssh-add', '-L'], env=env,
                                     stdout=subprocess.PIPE).stdout:
            line = line.decode('utf8')
            if line.strip() == 'The agent has no identities.':
                break
            result.append(line.strip())
        return result


class KubeFwd(object):
    kubectl_command = 'kubectl'

    def __init__(self, zuul_event_id, build, kubeconfig, context,
                 namespace, pod):
        self.port = None
        self.fwd = None
        self.log = get_annotated_logger(
            logging.getLogger("zuul.ExecutorServer"),
            zuul_event_id, build=build)
        self.kubeconfig = kubeconfig
        self.context = context
        self.namespace = namespace
        self.pod = pod

    def start(self):
        if self.fwd:
            return
        with open('/dev/null', 'r+') as devnull:
            fwd = subprocess.Popen(
                [self.kubectl_command, '--kubeconfig=%s' % self.kubeconfig,
                 '--context=%s' % self.context,
                 '-n', self.namespace,
                 'port-forward',
                 'pod/%s' % self.pod, ':19885'],
                close_fds=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=devnull)
        line = fwd.stdout.readline().decode('utf8')
        m = re.match(r'^Forwarding from 127.0.0.1:(\d+) -> 19885', line)
        if m:
            self.port = m.group(1)
        else:
            try:
                self.log.error("Could not find the forwarded port: %s", line)
                fwd.kill()
            except Exception:
                pass
            raise Exception("Unable to start kubectl port forward")
        self.fwd = fwd
        self.log.info('Started Kubectl port forward on port {}'.format(
            self.port))

    def stop(self):
        try:
            if self.fwd:
                self.fwd.kill()
                self.fwd.wait()

                # clear stdout buffer before its gone to not miss out on
                # potential connection errors
                fwd_stdout = [line.decode('utf8') for line in self.fwd.stdout]
                self.log.debug(
                    "Rest of kubectl port forward output was: %s",
                    "".join(fwd_stdout)
                )

                self.fwd = None
        except Exception:
            self.log.exception('Unable to stop kubectl port-forward:')

    def __del__(self):
        try:
            self.stop()
        except Exception:
            self.log.exception('Exception in KubeFwd destructor')
        try:
            super().__del__(self)
        except AttributeError:
            pass


class JobDirPlaybookRole(object):
    def __init__(self, root):
        self.root = root
        self.link_src = None
        self.link_target = None
        self.role_path = None
        self.checkout_description = None
        self.checkout = None

    def toDict(self, jobdir_root=None):
        # This is serialized to the zuul.playbook_context variable
        if jobdir_root:
            strip = len(jobdir_root) + 1
        else:
            strip = 0
        return dict(
            link_name=self.link_name[strip:],
            link_target=self.link_target[strip:],
            role_path=self.role_path[strip:],
            checkout_description=self.checkout_description,
            checkout=self.checkout,
        )


class JobDirPlaybook(object):
    def __init__(self, root):
        self.root = root
        self.trusted = None
        self.project_canonical_name = None
        self.branch = None
        self.canonical_name_and_path = None
        self.path = None
        self.roles = []
        self.roles_path = []
        self.ansible_config = os.path.join(self.root, 'ansible.cfg')
        self.inventory = os.path.join(self.root, 'inventory.yaml')
        self.project_link = os.path.join(self.root, 'project')
        self.secrets_root = os.path.join(self.root, 'group_vars')
        os.makedirs(self.secrets_root)
        self.secrets = os.path.join(self.secrets_root, 'all.yaml')
        self.secrets_content = None
        self.secrets_keys = set()

    def addRole(self):
        count = len(self.roles)
        root = os.path.join(self.root, 'role_%i' % (count,))
        os.makedirs(root)
        role_info = JobDirPlaybookRole(root)
        self.roles.append(role_info)
        return role_info


class JobDirProject(object):
    def __init__(self, root):
        self.root = root
        self.canonical_name = None
        self.checkout = None
        self.commit = None

    def toDict(self):
        # This is serialized to the zuul.playbook_context variable
        return dict(
            canonical_name=self.canonical_name,
            checkout=self.checkout,
            commit=self.commit,
        )


class JobDir(object):
    def __init__(self, root, keep, build_uuid):
        '''
        :param str root: Root directory for the individual job directories.
            Can be None to use the default system temp root directory.
        :param bool keep: If True, do not delete the job directory.
        :param str build_uuid: The unique build UUID. If supplied, this will
            be used as the temp job directory name. Using this will help the
            log streaming daemon find job logs.
        '''
        # root
        #   ansible (mounted in bwrap read-only)
        #     logging.json
        #     inventory.yaml
        #     vars_blacklist.yaml
        #     zuul_vars.yaml
        #   .ansible (mounted in bwrap read-write)
        #     fact-cache/localhost
        #     cp
        #   playbook_0 (mounted in bwrap for each playbook read-only)
        #     secrets.yaml
        #     project -> ../trusted/project_0/...
        #     role_0 -> ../trusted/project_0/...
        #   trusted (mounted in bwrap read-only)
        #     project_0
        #       <git.example.com>
        #         <project>
        #   untrusted (mounted in bwrap read-only)
        #     project_0
        #       <git.example.com>
        #         <project>
        #   work (mounted in bwrap read-write)
        #     .ssh
        #       known_hosts
        #     .kube
        #       config
        #     src
        #       <git.example.com>
        #         <project>
        #     logs
        #       job-output.txt
        #     tmp
        #     results.json
        self.keep = keep
        if root:
            tmpdir = root
        else:
            tmpdir = tempfile.gettempdir()
        self.root = os.path.realpath(os.path.join(tmpdir, build_uuid))
        os.mkdir(self.root, 0o700)
        self.work_root = os.path.join(self.root, 'work')
        os.makedirs(self.work_root)
        self.src_root = os.path.join(self.work_root, 'src')
        os.makedirs(self.src_root)
        self.log_root = os.path.join(self.work_root, 'logs')
        os.makedirs(self.log_root)
        # Create local tmp directory
        # NOTE(tobiash): This must live within the work root as it can be used
        # by ansible for temporary files which are path checked in untrusted
        # jobs.
        self.local_tmp = os.path.join(self.work_root, 'tmp')
        os.makedirs(self.local_tmp)
        self.ansible_root = os.path.join(self.root, 'ansible')
        os.makedirs(self.ansible_root)
        self.ansible_vars_blacklist = os.path.join(
            self.ansible_root, 'vars_blacklist.yaml')
        with open(self.ansible_vars_blacklist, 'w') as blacklist:
            blacklist.write(json.dumps(BLACKLISTED_VARS))
        self.zuul_vars = os.path.join(self.ansible_root, 'zuul_vars.yaml')
        self.trusted_root = os.path.join(self.root, 'trusted')
        os.makedirs(self.trusted_root)
        self.untrusted_root = os.path.join(self.root, 'untrusted')
        os.makedirs(self.untrusted_root)
        ssh_dir = os.path.join(self.work_root, '.ssh')
        os.mkdir(ssh_dir, 0o700)
        kube_dir = os.path.join(self.work_root, ".kube")
        os.makedirs(kube_dir)
        self.kubeconfig = os.path.join(kube_dir, "config")
        # Create ansible cache directory
        self.ansible_cache_root = os.path.join(self.root, '.ansible')
        self.fact_cache = os.path.join(self.ansible_cache_root, 'fact-cache')
        os.makedirs(self.fact_cache)
        self.control_path = os.path.join(self.ansible_cache_root, 'cp')
        self.job_unreachable_file = os.path.join(self.ansible_cache_root,
                                                 'nodes.unreachable')
        os.makedirs(self.control_path)

        localhost_facts = os.path.join(self.fact_cache, 'localhost')
        jobtime = datetime.datetime.utcnow()
        date_time_facts = {}
        date_time_facts['year'] = jobtime.strftime('%Y')
        date_time_facts['month'] = jobtime.strftime('%m')
        date_time_facts['weekday'] = jobtime.strftime('%A')
        date_time_facts['weekday_number'] = jobtime.strftime('%w')
        date_time_facts['weeknumber'] = jobtime.strftime('%W')
        date_time_facts['day'] = jobtime.strftime('%d')
        date_time_facts['hour'] = jobtime.strftime('%H')
        date_time_facts['minute'] = jobtime.strftime('%M')
        date_time_facts['second'] = jobtime.strftime('%S')
        date_time_facts['epoch'] = jobtime.strftime('%s')
        date_time_facts['date'] = jobtime.strftime('%Y-%m-%d')
        date_time_facts['time'] = jobtime.strftime('%H:%M:%S')
        date_time_facts['iso8601_micro'] = \
            jobtime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        date_time_facts['iso8601'] = \
            jobtime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        date_time_facts['iso8601_basic'] = jobtime.strftime("%Y%m%dT%H%M%S%f")
        date_time_facts['iso8601_basic_short'] = \
            jobtime.strftime("%Y%m%dT%H%M%S")

        # Set the TZ data manually as jobtime is naive.
        date_time_facts['tz'] = 'UTC'
        date_time_facts['tz_offset'] = '+0000'

        executor_facts = {}
        executor_facts['date_time'] = date_time_facts
        executor_facts['module_setup'] = True

        # NOTE(pabelanger): We do not want to leak zuul-executor facts to other
        # playbooks now that smart fact gathering is enabled by default.  We
        # can have ansible skip populating the cache with information by
        # writing a file with the minimum facts we want.
        with open(localhost_facts, 'w') as f:
            json.dump(executor_facts, f)

        self.result_data_file = os.path.join(self.work_root, 'results.json')
        with open(self.result_data_file, 'w'):
            pass
        self.known_hosts = os.path.join(ssh_dir, 'known_hosts')
        self.inventory = os.path.join(self.ansible_root, 'inventory.yaml')
        self.logging_json = os.path.join(self.ansible_root, 'logging.json')
        self.playbooks = []  # The list of candidate playbooks
        self.pre_playbooks = []
        self.post_playbooks = []
        self.cleanup_playbooks = []
        self.job_output_file = os.path.join(self.log_root, 'job-output.txt')
        # We need to create the job-output.txt upfront in order to close the
        # gap between url reporting and ansible creating the file. Otherwise
        # there is a period of time where the user can click on the live log
        # link on the status page but the log streaming fails because the file
        # is not there yet.
        with open(self.job_output_file, 'w') as job_output:
            job_output.write("{now} | Job console starting...\n".format(
                now=datetime.datetime.now()
            ))
        self.trusted_projects = {}
        self.untrusted_projects = {}

        # Create a JobDirPlaybook for the Ansible setup run.  This
        # doesn't use an actual playbook, but it lets us use the same
        # methods to write an ansible.cfg as the rest of the Ansible
        # runs.
        setup_root = os.path.join(self.ansible_root, 'setup_playbook')
        os.makedirs(setup_root)
        self.setup_playbook = JobDirPlaybook(setup_root)
        self.setup_playbook.trusted = True

        # Create a JobDirPlaybook for the Ansible variable freeze run.
        freeze_root = os.path.join(self.ansible_root, 'freeze_playbook')
        os.makedirs(freeze_root)
        self.freeze_playbook = JobDirPlaybook(freeze_root)
        self.freeze_playbook.trusted = False
        self.freeze_playbook.path = os.path.join(self.freeze_playbook.root,
                                                 'freeze_playbook.yaml')

    def addTrustedProject(self, canonical_name, branch):
        # Trusted projects are placed in their own directories so that
        # we can support using different branches of the same project
        # in different playbooks.
        count = len(self.trusted_projects)
        root = os.path.join(self.trusted_root, 'project_%i' % (count,))
        os.makedirs(root)
        project_info = JobDirProject(root)
        project_info.canonical_name = canonical_name
        project_info.checkout = branch
        self.trusted_projects[(canonical_name, branch)] = project_info
        return project_info

    def getTrustedProject(self, canonical_name, branch):
        return self.trusted_projects.get((canonical_name, branch))

    def addUntrustedProject(self, canonical_name, branch):
        # Similar to trusted projects, but these hold checkouts of
        # projects which are allowed to have speculative changes
        # applied.  They might, however, be different branches than
        # what is used in the working dir, so they need their own
        # location.  Moreover, we might avoid mischief if a job alters
        # the contents of the working dir.
        count = len(self.untrusted_projects)
        root = os.path.join(self.untrusted_root, 'project_%i' % (count,))
        os.makedirs(root)
        project_info = JobDirProject(root)
        project_info.canonical_name = canonical_name
        project_info.checkout = branch
        self.untrusted_projects[(canonical_name, branch)] = project_info
        return project_info

    def getUntrustedProject(self, canonical_name, branch):
        return self.untrusted_projects.get((canonical_name, branch))

    def addPrePlaybook(self):
        count = len(self.pre_playbooks)
        root = os.path.join(self.ansible_root, 'pre_playbook_%i' % (count,))
        os.makedirs(root)
        playbook = JobDirPlaybook(root)
        self.pre_playbooks.append(playbook)
        return playbook

    def addPostPlaybook(self):
        count = len(self.post_playbooks)
        root = os.path.join(self.ansible_root, 'post_playbook_%i' % (count,))
        os.makedirs(root)
        playbook = JobDirPlaybook(root)
        self.post_playbooks.append(playbook)
        return playbook

    def addCleanupPlaybook(self):
        count = len(self.cleanup_playbooks)
        root = os.path.join(
            self.ansible_root, 'cleanup_playbook_%i' % (count,))
        os.makedirs(root)
        playbook = JobDirPlaybook(root)
        self.cleanup_playbooks.append(playbook)
        return playbook

    def addPlaybook(self):
        count = len(self.playbooks)
        root = os.path.join(self.ansible_root, 'playbook_%i' % (count,))
        os.makedirs(root)
        playbook = JobDirPlaybook(root)
        self.playbooks.append(playbook)
        return playbook

    def cleanup(self):
        if not self.keep:
            shutil.rmtree(self.root)

    def __enter__(self):
        return self

    def __exit__(self, etype, value, tb):
        self.cleanup()


class UpdateTask(object):
    def __init__(self, connection_name, project_name, repo_state=None,
                 zuul_event_id=None, build=None):
        self.connection_name = connection_name
        self.project_name = project_name
        self.repo_state = repo_state
        self.canonical_name = None
        self.branches = None
        self.refs = None
        self.event = threading.Event()
        self.success = False

        # These variables are used for log annotation
        self.zuul_event_id = zuul_event_id
        self.build = build

    def __eq__(self, other):
        if (other and other.connection_name == self.connection_name and
            other.project_name == self.project_name and
            other.repo_state == self.repo_state):
            return True
        return False

    def wait(self):
        self.event.wait()

    def setComplete(self):
        self.event.set()


class DeduplicateQueue(object):
    def __init__(self):
        self.queue = collections.deque()
        self.condition = threading.Condition()

    def qsize(self):
        return len(self.queue)

    def put(self, item):
        # Returns the original item if added, or an equivalent item if
        # already enqueued.
        self.condition.acquire()
        ret = None
        try:
            for x in self.queue:
                if item == x:
                    ret = x
            if ret is None:
                ret = item
                self.queue.append(item)
                self.condition.notify()
        finally:
            self.condition.release()
        return ret

    def get(self):
        self.condition.acquire()
        try:
            while True:
                try:
                    ret = self.queue.popleft()
                    return ret
                except IndexError:
                    pass
                self.condition.wait()
        finally:
            self.condition.release()


def squash_variables(nodes, nodeset, jobvars, groupvars, extravars):
    """Combine the Zuul job variable parameters into a hostvars dictionary.

    This is used by the executor when freezing job variables.  It
    simulates the Ansible variable precedence to arrive at a single
    hostvars dict (ultimately, all variables in ansible are hostvars;
    therefore group vars and extra vars can be combined in such a way
    to present a single hierarchy of variables visible to each host).

    :param list nodes: A list of node dictionaries (as returned by
         getHostList)
    :param Nodeset nodeset: A nodeset (used for group membership).
    :param dict jobvars: A dictionary corresponding to Zuul's job.vars.
    :param dict groupvars: A dictionary keyed by group name with a value of
         a dictionary of variables for that group.
    :param dict extravars: A dictionary corresponding to Zuul's job.extra-vars.

    :returns: A dict keyed by hostname with a value of a dictionary of
         variables for the host.
    """

    # The output dictionary, keyed by hostname.
    ret = {}

    # Zuul runs ansible with the default hash behavior of 'replace';
    # this means we don't need to deep-merge dictionaries.
    groups = sorted(nodeset.getGroups(), key=lambda g: g.name)
    for node in nodes:
        hostname = node['name']
        ret[hostname] = {}
        # group 'all'
        ret[hostname].update(jobvars)
        # group vars
        if 'all' in groupvars:
            ret[hostname].update(groupvars.get('all', {}))
        for group in groups:
            if hostname in group.nodes:
                ret[hostname].update(groupvars.get(group.name, {}))
        # host vars
        ret[hostname].update(node['host_vars'])
        # extra vars
        ret[hostname].update(extravars)

    return ret


def make_setup_inventory_dict(nodes, hostvars):
    hosts = {}
    for node in nodes:
        if (hostvars[node['name']]['ansible_connection'] in
            BLACKLISTED_ANSIBLE_CONNECTION_TYPES):
            continue
        hosts[node['name']] = hostvars[node['name']]

    inventory = {
        'all': {
            'hosts': hosts,
        }
    }

    return inventory


def is_group_var_set(name, host, nodeset, job):
    for group in nodeset.getGroups():
        if host in group.nodes:
            group_vars = job.group_variables.get(group.name, {})
            if name in group_vars:
                return True
    return False


def make_inventory_dict(nodes, nodeset, hostvars, remove_keys=None):
    hosts = {}
    for node in nodes:
        node_hostvars = hostvars[node['name']].copy()
        if remove_keys:
            for k in remove_keys:
                node_hostvars.pop(k, None)
        hosts[node['name']] = node_hostvars

    # localhost has no hostvars, so we'll set what we froze for
    # localhost as the 'all' vars which will in turn be available to
    # localhost plays.
    all_hostvars = hostvars['localhost'].copy()
    if remove_keys:
        for k in remove_keys:
            all_hostvars.pop(k, None)

    inventory = {
        'all': {
            'hosts': hosts,
            'vars': all_hostvars,
        }
    }

    for group in nodeset.getGroups():
        if 'children' not in inventory['all']:
            inventory['all']['children'] = dict()

        group_hosts = {}
        for node_name in group.nodes:
            group_hosts[node_name] = None

        inventory['all']['children'].update({
            group.name: {
                'hosts': group_hosts,
            }})

    return inventory


class AnsibleJob(object):
    RESULT_NORMAL = 1
    RESULT_TIMED_OUT = 2
    RESULT_UNREACHABLE = 3
    RESULT_ABORTED = 4
    RESULT_DISK_FULL = 5

    RESULT_MAP = {
        RESULT_NORMAL: 'RESULT_NORMAL',
        RESULT_TIMED_OUT: 'RESULT_TIMED_OUT',
        RESULT_UNREACHABLE: 'RESULT_UNREACHABLE',
        RESULT_ABORTED: 'RESULT_ABORTED',
        RESULT_DISK_FULL: 'RESULT_DISK_FULL',
    }

    def __init__(self, executor_server, build_request, arguments):
        logger = logging.getLogger("zuul.AnsibleJob")
        self.arguments = arguments
        self.job = FrozenJob.fromZK(executor_server.zk_context,
                                    arguments["job_ref"])
        self.arguments["zuul"].update(zuul_params_from_job(self.job))

        self.zuul_event_id = self.arguments["zuul_event_id"]
        # Record ansible version being used for the cleanup phase
        self.ansible_version = self.job.ansible_version
        # TODO(corvus): Remove default setting after 4.3.0; this is to handle
        # scheduler/executor version skew.
        self.scheme = self.job.workspace_scheme or zuul.model.SCHEME_GOLANG
        self.log = get_annotated_logger(
            logger, self.zuul_event_id, build=build_request.uuid
        )
        self.executor_server = executor_server
        self.build_request = build_request
        self.nodeset = None
        self.node_request = None
        self.jobdir = None
        self.proc = None
        self.proc_lock = threading.Lock()
        self.running = False
        self.started = False  # Whether playbooks have started running
        self.time_starting_build = None
        self.paused = False
        self.aborted = False
        self.aborted_reason = None
        self.cleanup_started = False
        self._resume_event = threading.Event()
        self.thread = None
        self.project_info = {}
        self.private_key_file = get_default(self.executor_server.config,
                                            'executor', 'private_key_file',
                                            '~/.ssh/id_rsa')
        self.winrm_key_file = get_default(self.executor_server.config,
                                          'executor', 'winrm_cert_key_file',
                                          '~/.winrm/winrm_client_cert.key')
        self.winrm_pem_file = get_default(self.executor_server.config,
                                          'executor', 'winrm_cert_pem_file',
                                          '~/.winrm/winrm_client_cert.pem')
        self.winrm_operation_timeout = get_default(
            self.executor_server.config,
            'executor',
            'winrm_operation_timeout_sec')
        self.winrm_read_timeout = get_default(
            self.executor_server.config,
            'executor',
            'winrm_read_timeout_sec')
        self.ssh_agent = SshAgent(zuul_event_id=self.zuul_event_id,
                                  build=self.build_request.uuid)
        self.port_forwards = []
        self.executor_variables_file = None

        self.cpu_times = {'user': 0, 'system': 0,
                          'children_user': 0, 'children_system': 0}

        if self.executor_server.config.has_option('executor', 'variables'):
            self.executor_variables_file = self.executor_server.config.get(
                'executor', 'variables')

        plugin_dir = self.executor_server.ansible_manager.getAnsiblePluginDir(
            self.ansible_version)
        self.ara_callbacks = \
            self.executor_server.ansible_manager.getAraCallbackPlugin(
                self.ansible_version)
        self.library_dir = os.path.join(plugin_dir, 'library')
        self.action_dir = os.path.join(plugin_dir, 'action')
        self.action_dir_general = os.path.join(plugin_dir, 'actiongeneral')
        self.action_dir_trusted = os.path.join(plugin_dir, 'actiontrusted')
        self.callback_dir = os.path.join(plugin_dir, 'callback')
        self.lookup_dir = os.path.join(plugin_dir, 'lookup')
        self.filter_dir = os.path.join(plugin_dir, 'filter')
        self.ansible_callbacks = self.executor_server.ansible_callbacks
        # The result of getHostList
        self.host_list = None
        # The supplied job/host/group/extra vars, squashed.  Indexed
        # by hostname.
        self.original_hostvars = {}
        # The same, but frozen
        self.frozen_hostvars = {}
        # The zuul.* vars
        self.zuul_vars = {}

    def run(self):
        self.running = True
        self.thread = threading.Thread(target=self.execute,
                                       name=f"build-{self.build_request.uuid}")
        self.thread.start()

    def stop(self, reason=None):
        self.aborted = True
        self.aborted_reason = reason

        # if paused we need to resume the job so it can be stopped
        self.resume()
        self.abortRunningProc()

    def pause(self):
        self.log.info(
            "Pausing job %s for ref %s (change %s)" % (
                self.arguments['zuul']['job'],
                self.arguments['zuul']['ref'],
                self.arguments['zuul']['change_url']))
        with open(self.jobdir.job_output_file, 'a') as job_output:
            job_output.write(
                "{now} |\n"
                "{now} | Job paused\n".format(now=datetime.datetime.now()))

        self.paused = True

        result_data, secret_result_data = self.getResultData()
        data = {'paused': self.paused,
                'data': result_data,
                'secret_data': secret_result_data}
        self.executor_server.pauseBuild(self.build_request, data)
        self._resume_event.wait()

    def resume(self):
        if not self.paused:
            return

        self.log.info(
            "Resuming job %s for ref %s (change %s)" % (
                self.arguments['zuul']['job'],
                self.arguments['zuul']['ref'],
                self.arguments['zuul']['change_url']))
        with open(self.jobdir.job_output_file, 'a') as job_output:
            job_output.write(
                "{now} | Job resumed\n"
                "{now} |\n".format(now=datetime.datetime.now()))

        self.paused = False
        self.executor_server.resumeBuild(self.build_request)
        self._resume_event.set()

    def wait(self):
        if self.thread:
            self.thread.join()

    def execute(self):
        try:
            self.time_starting_build = time.monotonic()

            # report that job has been taken
            self.executor_server.startBuild(
                self.build_request, self._base_job_data()
            )

            self.setNodeInfo()
            self.loadRepoState()

            self.ssh_agent.start()
            self.ssh_agent.add(self.private_key_file)
            for key in self.arguments.get('ssh_keys', []):
                private_ssh_key, public_ssh_key = \
                    self.executor_server.keystore.getProjectSSHKeys(
                        key['connection_name'],
                        key['project_name'])
                name = '%s project key' % (key['project_name'])
                self.ssh_agent.addData(name, private_ssh_key)
            self.jobdir = JobDir(self.executor_server.jobdir_root,
                                 self.executor_server.keep_jobdir,
                                 str(self.build_request.uuid))
            self.lockNodes()
            self._execute()
        except NodeRequestError:
            result_data = dict(
                result="NODE_FAILURE", exception=traceback.format_exc()
            )
            self.executor_server.completeBuild(self.build_request, result_data)
        except BrokenProcessPool:
            # The process pool got broken, re-initialize it and send
            # ABORTED so we re-try the job.
            self.log.exception('Process pool got broken')
            self.executor_server.resetProcessPool()
            self._send_aborted()
        except ExecutorError as e:
            result_data = dict(result='ERROR', error_detail=e.args[0])
            self.log.debug("Sending result: %s", result_data)
            self.executor_server.completeBuild(self.build_request, result_data)
        except Exception:
            self.log.exception("Exception while executing job")
            data = {"exception": traceback.format_exc()}
            self.executor_server.completeBuild(self.build_request, data)
        finally:
            self.running = False
            if self.jobdir:
                try:
                    self.jobdir.cleanup()
                except Exception:
                    self.log.exception("Error cleaning up jobdir:")
            if self.ssh_agent:
                try:
                    self.ssh_agent.stop()
                except Exception:
                    self.log.exception("Error stopping SSH agent:")
            for fwd in self.port_forwards:
                try:
                    fwd.stop()
                except Exception:
                    self.log.exception("Error stopping port forward:")

            # Make sure we return the nodes to nodepool in any case.
            self.unlockNodes()
            try:
                self.executor_server.finishJob(self.build_request.uuid)
            except Exception:
                self.log.exception("Error finalizing job thread:")
            self.log.info("Job execution took: %.3f seconds",
                          self.end_time - self.time_starting_build)

    def setNodeInfo(self):
        try:
            # This shouldn't fail - but theoretically it could. So we handle
            # it similar to a NodeRequestError.
            self.nodeset = self.job.nodeset
        except KeyError:
            self.log.error("Unable to deserialize nodeset")
            raise NodeRequestError

        # Look up the NodeRequest with the provided ID from ZooKeeper. If
        # no ID is provided, this most probably means that the NodeRequest
        # wasn't submitted to ZooKeeper.
        node_request_id = self.arguments.get("noderequest_id")
        if node_request_id:
            zk_nodepool = self.executor_server.nodepool.zk_nodepool
            self.node_request = zk_nodepool.getNodeRequest(
                self.arguments["noderequest_id"])

            if self.node_request is None:
                self.log.error(
                    "Unable to retrieve NodeReqest %s from ZooKeeper",
                    node_request_id,
                )
                raise NodeRequestError

    def lockNodes(self):
        # If the node_request is not set, this probably means that the
        # NodeRequest didn't contain any nodes and thus was never submitted
        # to ZooKeeper. In that case we don't have anything to lock before
        # executing the build.
        if self.node_request:
            self.log.debug("Locking nodeset")
            try:
                self.executor_server.nodepool.acceptNodes(
                    self.node_request, self.nodeset)
            except Exception:
                self.log.exception(
                    "Error locking nodeset %s", self.nodeset
                )
                raise NodeRequestError

    def unlockNodes(self):
        if self.node_request:
            tenant_name = self.arguments["zuul"]["tenant"]
            project_name = self.arguments["zuul"]["project"]["canonical_name"]
            duration = self.end_time - self.time_starting_build
            try:
                self.executor_server.nodepool.returnNodeSet(
                    self.nodeset,
                    self.build_request,
                    tenant_name,
                    project_name,
                    duration,
                    zuul_event_id=self.zuul_event_id,
                )
            except Exception:
                self.log.exception(
                    "Unable to return nodeset %s", self.nodeset
                )

    def loadRepoState(self):
        merge_rs_path = self.arguments['merge_repo_state_ref']
        merge_repo_state = merge_rs_path and MergeRepoState.fromZK(
            self.executor_server.zk_context, merge_rs_path)
        extra_rs_path = self.arguments['extra_repo_state_ref']
        extra_repo_state = extra_rs_path and ExtraRepoState.fromZK(
            self.executor_server.zk_context, extra_rs_path)
        d = {}
        for rs in (merge_repo_state, extra_repo_state):
            if not rs:
                continue
            for connection in rs.state.keys():
                d.setdefault(connection, {}).update(
                    rs.state.get(connection, {}))
        self.repo_state = d

    def _base_job_data(self):
        data = {
            # TODO(mordred) worker_name is needed as a unique name for the
            # client to use for cancelling jobs on an executor. It's
            # defaulting to the hostname for now, but in the future we
            # should allow setting a per-executor override so that one can
            # run more than one executor on a host.
            'worker_name': self.executor_server.hostname,
            'worker_hostname': self.executor_server.hostname,
            'worker_log_port': self.executor_server.log_streaming_port,
        }
        if self.executor_server.zone:
            data['worker_zone'] = self.executor_server.zone
        return data

    def _send_aborted(self):
        result = dict(result='ABORTED')
        self.executor_server.completeBuild(self.build_request, result)

    def _execute(self):
        args = self.arguments
        self.log.info(
            "Beginning job %s for ref %s (change %s)" % (
                args['zuul']['job'],
                args['zuul']['ref'],
                args['zuul']['change_url']))
        self.log.debug("Job root: %s" % (self.jobdir.root,))
        tasks = []
        projects = set()

        with open(self.jobdir.job_output_file, 'a') as job_output:
            job_output.write("{now} | Updating repositories\n".format(
                now=datetime.datetime.now()
            ))
        # Make sure all projects used by the job are updated...
        for project in args['projects']:
            self.log.debug("Updating project %s" % (project,))
            tasks.append(self.executor_server.update(
                project['connection'], project['name'],
                repo_state=self.repo_state,
                zuul_event_id=self.zuul_event_id,
                build=self.build_request.uuid))
            projects.add((project['connection'], project['name']))

        # ...as well as all playbook and role projects.
        repos = []
        playbooks = (self.job.pre_run + self.job.run +
                     self.job.post_run + self.job.cleanup_run)
        for playbook in playbooks:
            repos.append(playbook)
            repos += playbook['roles']

        for repo in repos:
            key = (repo['connection'], repo['project'])
            if key not in projects:
                self.log.debug("Updating playbook or role %s" % (
                               repo['project'],))
                tasks.append(self.executor_server.update(
                    *key, repo_state=self.repo_state,
                    zuul_event_id=self.zuul_event_id,
                    build=self.build_request.uuid))
                projects.add(key)

        for task in tasks:
            task.wait()

            if not task.success:
                # On transient error retry the job
                if hasattr(task, 'transient_error') and task.transient_error:
                    result = dict(
                        result=None,
                        error_detail=f'Failed to update project '
                                     f'{task.project_name}')
                    self.job.sendWorkComplete(
                        json.dumps(result, sort_keys=True))
                    return

                raise ExecutorError(
                    'Failed to update project %s' % task.project_name)

            # Take refs and branches from repo state
            project_repo_state = \
                self.repo_state[task.connection_name][task.project_name]
            # All branch names
            branches = [
                ref[11:]  # strip refs/heads/
                for ref in project_repo_state
                if ref.startswith('refs/heads/')
            ]
            # All refs without refs/*/ prefix
            refs = []
            for ref in project_repo_state:
                r = '/'.join(ref.split('/')[2:])
                if r:
                    refs.append(r)
            self.project_info[task.canonical_name] = {
                'refs': refs,
                'branches': branches,
            }

        # Early abort if abort requested
        if self.aborted:
            self._send_aborted()
            return
        self.log.debug("Git updates complete")

        with open(self.jobdir.job_output_file, 'a') as job_output:
            job_output.write("{now} | Preparing job workspace\n".format(
                now=datetime.datetime.now()
            ))
        merger = self.executor_server._getMerger(
            self.jobdir.src_root,
            self.executor_server.merge_root,
            logger=self.log,
            scheme=self.scheme)
        repos = {}
        for project in args['projects']:
            self.log.debug("Cloning %s/%s" % (project['connection'],
                                              project['name'],))
            repo = merger.getRepo(
                project['connection'],
                project['name'],
                process_worker=self.executor_server.process_worker)
            repos[project['canonical_name']] = repo

        # The commit ID of the original item (before merging).  Used
        # later for line mapping.
        item_commit = None
        # The set of repos which have had their state restored
        restored_repos = set()

        merge_items = [i for i in args['items'] if i.get('number')]
        if merge_items:
            item_commit = self.doMergeChanges(
                merger, merge_items, self.repo_state, restored_repos)
            if item_commit is None:
                # There was a merge conflict and we have already sent
                # a work complete result, don't run any jobs
                return

        # Early abort if abort requested
        if self.aborted:
            self._send_aborted()
            return

        for project in args['projects']:
            if (project['connection'], project['name']) in restored_repos:
                continue
            merger.setRepoState(
                project['connection'], project['name'], self.repo_state,
                process_worker=self.executor_server.process_worker)

        # Early abort if abort requested
        if self.aborted:
            self._send_aborted()
            return

        for project in args['projects']:
            repo = repos[project['canonical_name']]
            # If this project is the Zuul project and this is a ref
            # rather than a change, checkout the ref.
            if (project['canonical_name'] ==
                args['zuul']['project']['canonical_name'] and
                (not args['zuul'].get('branch')) and
                args['zuul'].get('ref')):
                ref = args['zuul']['ref']
            else:
                ref = None
            selected_ref, selected_desc = self.resolveBranch(
                project['canonical_name'],
                ref,
                args['branch'],
                self.job.override_branch,
                self.job.override_checkout,
                project['override_branch'],
                project['override_checkout'],
                project['default_branch'])
            self.log.info("Checking out %s %s %s",
                          project['canonical_name'], selected_desc,
                          selected_ref)
            commit = repo.checkout(selected_ref)

            # Update the inventory variables to indicate the ref we
            # checked out
            p = args['zuul']['projects'][project['canonical_name']]
            p['checkout'] = selected_ref
            p['checkout_description'] = selected_desc
            p['commit'] = commit.hexsha

        # Set the URL of the origin remote for each repo to a bogus
        # value. Keeping the remote allows tools to use it to determine
        # which commits are part of the current change.
        for repo in repos.values():
            repo.setRemoteUrl('file:///dev/null')

        # Early abort if abort requested
        if self.aborted:
            self._send_aborted()
            return

        # We set the nodes to "in use" as late as possible. So in case
        # the build failed during the checkout phase, the node is
        # still untouched and nodepool can re-allocate it to a
        # different node request / build.  Below this point, we may
        # start to run tasks on nodes (prepareVars in particular uses
        # Ansible to freeze hostvars).
        if self.node_request:
            tenant_name = self.arguments["zuul"]["tenant"]
            project_name = self.arguments["zuul"]["project"]["canonical_name"]
            self.executor_server.nodepool.useNodeSet(
                self.nodeset, tenant_name, project_name, self.zuul_event_id)

        # This prepares each playbook and the roles needed for each.
        self.preparePlaybooks(args)
        self.writeLoggingConfig()
        zuul_resources = self.prepareNodes(args)  # set self.host_list
        self.prepareVars(args, zuul_resources)   # set self.original_hostvars
        self.writeDebugInventory()

        # Early abort if abort requested
        if self.aborted:
            self._send_aborted()
            return

        data = self._base_job_data()
        if self.executor_server.log_streaming_port != DEFAULT_FINGER_PORT:
            data['url'] = "finger://{hostname}:{port}/{uuid}".format(
                hostname=self.executor_server.hostname,
                port=self.executor_server.log_streaming_port,
                uuid=self.build_request.uuid)
        else:
            data['url'] = 'finger://{hostname}/{uuid}'.format(
                hostname=self.executor_server.hostname,
                uuid=self.build_request.uuid)

        self.executor_server.updateBuildStatus(self.build_request, data)

        result = self.runPlaybooks(args)
        success = result == 'SUCCESS'

        self.runCleanupPlaybooks(success)

        # Stop the persistent SSH connections.
        setup_status, setup_code = self.runAnsibleCleanup(
            self.jobdir.setup_playbook)

        if self.aborted_reason == self.RESULT_DISK_FULL:
            result = 'DISK_FULL'
        data, secret_data = self.getResultData()
        warnings = []
        self.mapLines(merger, args, data, item_commit, warnings)
        warnings.extend(get_warnings_from_result_data(data, logger=self.log))
        result_data = dict(result=result,
                           warnings=warnings,
                           data=data,
                           secret_data=secret_data)
        # TODO do we want to log the secret data here?
        self.log.debug("Sending result: %s", result_data)
        self.executor_server.completeBuild(self.build_request, result_data)

    def getResultData(self):
        data = {}
        secret_data = {}
        try:
            with open(self.jobdir.result_data_file) as f:
                file_data = f.read()
                if file_data:
                    file_data = json.loads(file_data)
                    data = file_data.get('data', {})
                    secret_data = file_data.get('secret_data', {})
            # Check the variable names for safety, but zuul is allowed.
            data_copy = data.copy()
            data_copy.pop('zuul', None)
            check_varnames(data_copy)
            secret_data_copy = data.copy()
            secret_data_copy.pop('zuul', None)
            check_varnames(secret_data_copy)
        except Exception:
            self.log.exception("Unable to load result data:")
        return data, secret_data

    def mapLines(self, merger, args, data, commit, warnings):
        # The data and warnings arguments are mutated in this method.

        # If we received file comments, map the line numbers before
        # we send the result.
        fc = data.get('zuul', {}).get('file_comments')
        if not fc:
            return
        disable = data.get('zuul', {}).get('disable_file_comment_line_mapping')
        if disable:
            return

        try:
            filecomments.validate(fc)
        except Exception as e:
            warnings.append("Job %s: validation error in file comments: %s" %
                            (args['zuul']['job'], str(e)))
            del data['zuul']['file_comments']
            return

        repo = None
        for project in args['projects']:
            if (project['canonical_name'] !=
                args['zuul']['project']['canonical_name']):
                continue
            repo = merger.getRepo(project['connection'],
                                  project['name'])
        # If the repo doesn't exist, abort
        if not repo:
            return

        # Check out the selected ref again in case the job altered the
        # repo state.
        p = args['zuul']['projects'][project['canonical_name']]
        selected_ref = p['checkout']

        self.log.info("Checking out %s %s for line mapping",
                      project['canonical_name'], selected_ref)
        try:
            repo.checkout(selected_ref)
        except Exception:
            # If checkout fails, abort
            self.log.exception("Error checking out repo for line mapping")
            warnings.append("Job %s: unable to check out repo "
                            "for file comments" % (args['zuul']['job']))
            return

        lines = filecomments.extractLines(fc)

        new_lines = {}
        for (filename, lineno) in lines:
            try:
                new_lineno = repo.mapLine(commit, filename, lineno)
            except Exception as e:
                # Log at debug level since it's likely a job issue
                self.log.debug("Error mapping line:", exc_info=True)
                if isinstance(e, git.GitCommandError):
                    msg = e.stderr
                else:
                    msg = str(e)
                warnings.append("Job %s: unable to map line "
                                "for file comments: %s" %
                                (args['zuul']['job'], msg))
                new_lineno = None
            if new_lineno is not None:
                new_lines[(filename, lineno)] = new_lineno

        filecomments.updateLines(fc, new_lines)

    def doMergeChanges(self, merger, items, repo_state, restored_repos):
        try:
            ret = merger.mergeChanges(
                items, repo_state=repo_state,
                process_worker=self.executor_server.process_worker)
        except ValueError:
            # Return ABORTED so that we'll try again. At this point all of
            # the refs we're trying to merge should be valid refs. If we
            # can't fetch them, it should resolve itself.
            self.log.exception("Could not fetch refs to merge from remote")
            result = dict(result='ABORTED')
            self.executor_server.completeBuild(self.build_request, result)
            return None
        if not ret:  # merge conflict
            result = dict(result='MERGER_FAILURE')
            if self.executor_server.statsd:
                base_key = "zuul.executor.{hostname}.merger"
                self.executor_server.statsd.incr(base_key + ".FAILURE")
            self.executor_server.completeBuild(self.build_request, result)
            return None

        if self.executor_server.statsd:
            base_key = "zuul.executor.{hostname}.merger"
            self.executor_server.statsd.incr(base_key + ".SUCCESS")
        recent = ret[3]
        orig_commit = ret[4]
        for key, commit in recent.items():
            (connection, project, branch) = key
            restored_repos.add((connection, project))
            # Compare the commit with the repo state. If it's included in the
            # repo state and it's the same we've set this ref already earlier
            # and don't have to set it again.
            project_repo_state = repo_state.get(
                connection, {}).get(project, {})
            repo_state_commit = project_repo_state.get(
                'refs/heads/%s' % branch)
            if repo_state_commit != commit:
                repo = merger.getRepo(connection, project)
                repo.setRef('refs/heads/' + branch, commit)
        return orig_commit

    def resolveBranch(self, project_canonical_name, ref, zuul_branch,
                      job_override_branch, job_override_checkout,
                      project_override_branch, project_override_checkout,
                      project_default_branch):
        branches = self.project_info[project_canonical_name]['branches']
        refs = self.project_info[project_canonical_name]['refs']
        selected_ref = None
        selected_desc = None
        if project_override_checkout in refs:
            selected_ref = project_override_checkout
            selected_desc = 'project override ref'
        elif project_override_branch in branches:
            selected_ref = project_override_branch
            selected_desc = 'project override branch'
        elif job_override_checkout in refs:
            selected_ref = job_override_checkout
            selected_desc = 'job override ref'
        elif job_override_branch in branches:
            selected_ref = job_override_branch
            selected_desc = 'job override branch'
        elif ref and ref.startswith('refs/heads/'):
            selected_ref = ref[len('refs/heads/'):]
            selected_desc = 'branch ref'
        elif ref and ref.startswith('refs/tags/'):
            selected_ref = ref[len('refs/tags/'):]
            selected_desc = 'tag ref'
        elif zuul_branch and zuul_branch in branches:
            selected_ref = zuul_branch
            selected_desc = 'zuul branch'
        elif project_default_branch in branches:
            selected_ref = project_default_branch
            selected_desc = 'project default branch'
        else:
            raise ExecutorError("Project %s does not have the "
                                "default branch %s" %
                                (project_canonical_name,
                                 project_default_branch))
        return (selected_ref, selected_desc)

    def getAnsibleTimeout(self, start, timeout):
        if timeout is not None:
            now = time.time()
            elapsed = now - start
            timeout = timeout - elapsed
        return timeout

    def runPlaybooks(self, args):
        result = None

        with open(self.jobdir.job_output_file, 'a') as job_output:
            job_output.write("{now} | Running Ansible setup...\n".format(
                now=datetime.datetime.now()
            ))
        # Run the Ansible 'setup' module on all hosts in the inventory
        # at the start of the job with a 60 second timeout.  If we
        # aren't able to connect to all the hosts and gather facts
        # within that timeout, there is likely a network problem
        # between here and the hosts in the inventory; return them and
        # reschedule the job.

        self.writeSetupInventory()
        setup_status, setup_code = self.runAnsibleSetup(
            self.jobdir.setup_playbook, self.ansible_version)
        if setup_status != self.RESULT_NORMAL or setup_code != 0:
            return result

        # Freeze the variables so that we have a copy of them without
        # any jinja templates for use in the trusted execution
        # context.
        self.writeInventory(self.jobdir.freeze_playbook,
                            self.original_hostvars)
        freeze_status, freeze_code = self.runAnsibleFreeze(
            self.jobdir.freeze_playbook, self.ansible_version)
        if freeze_status != self.RESULT_NORMAL or setup_code != 0:
            return result

        self.loadFrozenHostvars()
        pre_failed = False
        success = False
        if self.executor_server.statsd:
            key = "zuul.executor.{hostname}.starting_builds"
            self.executor_server.statsd.timing(
                key, (time.monotonic() - self.time_starting_build) * 1000)

        self.started = True
        time_started = time.time()
        # timeout value is "total" job timeout which accounts for
        # pre-run and run playbooks. post-run is different because
        # it is used to copy out job logs and we want to do our best
        # to copy logs even when the job has timed out.
        job_timeout = self.job.timeout
        for index, playbook in enumerate(self.jobdir.pre_playbooks):
            # TODOv3(pabelanger): Implement pre-run timeout setting.
            ansible_timeout = self.getAnsibleTimeout(time_started, job_timeout)
            pre_status, pre_code = self.runAnsiblePlaybook(
                playbook, ansible_timeout, self.ansible_version, phase='pre',
                index=index)
            if pre_status != self.RESULT_NORMAL or pre_code != 0:
                # These should really never fail, so return None and have
                # zuul try again
                pre_failed = True
                break

        self.log.debug(
            "Overall ansible cpu times: user=%.2f, system=%.2f, "
            "children_user=%.2f, children_system=%.2f" %
            (self.cpu_times['user'], self.cpu_times['system'],
             self.cpu_times['children_user'],
             self.cpu_times['children_system']))

        run_unreachable = False
        if not pre_failed:
            for index, playbook in enumerate(self.jobdir.playbooks):
                ansible_timeout = self.getAnsibleTimeout(
                    time_started, job_timeout)
                job_status, job_code = self.runAnsiblePlaybook(
                    playbook, ansible_timeout, self.ansible_version,
                    phase='run', index=index)
                if job_status == self.RESULT_ABORTED:
                    return 'ABORTED'
                elif job_status == self.RESULT_TIMED_OUT:
                    # Set the pre-failure flag so this doesn't get
                    # overridden by a post-failure.
                    pre_failed = True
                    result = 'TIMED_OUT'
                    break
                elif job_status == self.RESULT_UNREACHABLE:
                    # In case we encounter unreachable nodes we need to return
                    # None so the job can be retried. However we still want to
                    # run post playbooks to get a chance to upload logs.
                    pre_failed = True
                    run_unreachable = True
                    break
                elif job_status == self.RESULT_NORMAL:
                    success = (job_code == 0)
                    if success:
                        result = 'SUCCESS'
                    else:
                        result = 'FAILURE'
                        break
                else:
                    # The result of the job is indeterminate.  Zuul will
                    # run it again.
                    return None

        # check if we need to pause here
        result_data, secret_result_data = self.getResultData()
        pause = result_data.get('zuul', {}).get('pause')
        if success and pause:
            self.pause()
        if self.aborted:
            return 'ABORTED'

        post_timeout = self.job.post_timeout
        post_unreachable = False
        for index, playbook in enumerate(self.jobdir.post_playbooks):
            # Post timeout operates a little differently to the main job
            # timeout. We give each post playbook the full post timeout to
            # do its job because post is where you'll often record job logs
            # which are vital to understanding why timeouts have happened in
            # the first place.
            post_status, post_code = self.runAnsiblePlaybook(
                playbook, post_timeout, self.ansible_version, success,
                phase='post', index=index)
            if post_status == self.RESULT_ABORTED:
                return 'ABORTED'
            if post_status == self.RESULT_UNREACHABLE:
                # In case we encounter unreachable nodes we need to return None
                # so the job can be retried. However in the case of post
                # playbooks we should still try to run all playbooks to get a
                # chance to upload logs.
                post_unreachable = True
            if post_status != self.RESULT_NORMAL or post_code != 0:
                success = False
                # If we encountered a pre-failure, that takes
                # precedence over the post result.
                if not pre_failed:
                    result = 'POST_FAILURE'
                if (index + 1) == len(self.jobdir.post_playbooks):
                    self._logFinalPlaybookError()

        if run_unreachable or post_unreachable:
            return None

        return result

    def runCleanupPlaybooks(self, success):
        if not self.jobdir.cleanup_playbooks:
            return

        # TODO: make this configurable
        cleanup_timeout = 300

        with open(self.jobdir.job_output_file, 'a') as job_output:
            job_output.write("{now} | Running Ansible cleanup...\n".format(
                now=datetime.datetime.now()
            ))

        self.cleanup_started = True
        for index, playbook in enumerate(self.jobdir.cleanup_playbooks):
            self.runAnsiblePlaybook(
                playbook, cleanup_timeout, self.ansible_version,
                success=success, phase='cleanup', index=index)

    def _logFinalPlaybookError(self):
        # Failures in the final post playbook can include failures
        # uploading logs, which makes diagnosing issues difficult.
        # Grab the output from the last playbook from the json
        # file and log it.
        json_output = self.jobdir.job_output_file.replace('txt', 'json')
        self.log.debug("Final playbook failed")
        if not os.path.exists(json_output):
            self.log.debug("JSON logfile {logfile} is missing".format(
                logfile=json_output))
            return
        try:
            output = json.load(open(json_output, 'r'))
            last_playbook = output[-1]
            # Transform json to yaml - because it's easier to read and given
            # the size of the data it'll be extra-hard to read this as an
            # all on one line stringified nested dict.
            yaml_out = yaml.safe_dump(last_playbook, default_flow_style=False)
            for line in yaml_out.split('\n'):
                self.log.debug(line)
        except Exception:
            self.log.exception(
                "Could not decode json from {logfile}".format(
                    logfile=json_output))

    def getHostList(self, args, nodes):
        hosts = []
        for node in nodes:
            # NOTE(mordred): This assumes that the nodepool launcher
            # and the zuul executor both have similar network
            # characteristics, as the launcher will do a test for ipv6
            # viability and if so, and if the node has an ipv6
            # address, it will be the interface_ip.  force-ipv4 can be
            # set to True in the clouds.yaml for a cloud if this
            # results in the wrong thing being in interface_ip
            # TODO(jeblair): Move this notice to the docs.
            for name in node.name:
                ip = node.interface_ip
                port = node.connection_port
                host_vars = self.job.host_variables.get(name, {}).copy()
                check_varnames(host_vars)
                host_vars.update(dict(
                    ansible_host=ip,
                    ansible_user=self.executor_server.default_username,
                    ansible_port=port,
                    nodepool=dict(
                        label=node.label,
                        az=node.az,
                        cloud=node.cloud,
                        provider=node.provider,
                        region=node.region,
                        host_id=node.host_id,
                        external_id=getattr(node, 'external_id', None),
                        interface_ip=node.interface_ip,
                        public_ipv4=node.public_ipv4,
                        private_ipv4=node.private_ipv4,
                        public_ipv6=node.public_ipv6,
                        private_ipv6=node.private_ipv6)))

                # Ansible >=2.8 introduced "auto" as an
                # ansible_python_interpreter argument that looks up
                # which python to use on the remote host in an inbuilt
                # table and essentially "does the right thing"
                # (i.e. chooses python3 on 3-only hosts like later
                # Fedoras).
                # If ansible_python_interpreter is set either as a group
                # var or all-var, then don't do anything here; let the
                # user control.
                api = 'ansible_python_interpreter'
                if (api not in self.job.combined_variables and
                    not is_group_var_set(api, name, self.nodeset, self.job)):
                    python = getattr(node, 'python_path', 'auto')
                    host_vars.setdefault(api, python)

                username = node.username
                if username:
                    host_vars['ansible_user'] = username

                connection_type = node.connection_type
                if connection_type:
                    host_vars['ansible_connection'] = connection_type
                    if connection_type == "winrm":
                        host_vars['ansible_winrm_transport'] = 'certificate'
                        host_vars['ansible_winrm_cert_pem'] = \
                            self.winrm_pem_file
                        host_vars['ansible_winrm_cert_key_pem'] = \
                            self.winrm_key_file
                        # NOTE(tobiash): This is necessary when using default
                        # winrm self-signed certificates. This is probably what
                        # most installations want so hard code this here for
                        # now.
                        host_vars['ansible_winrm_server_cert_validation'] = \
                            'ignore'
                        if self.winrm_operation_timeout is not None:
                            host_vars['ansible_winrm_operation_timeout_sec'] =\
                                self.winrm_operation_timeout
                        if self.winrm_read_timeout is not None:
                            host_vars['ansible_winrm_read_timeout_sec'] = \
                                self.winrm_read_timeout
                    elif connection_type == "kubectl":
                        host_vars['ansible_kubectl_context'] = \
                            getattr(node, 'kubectl_context', None)

                shell_type = getattr(node, 'shell_type', None)
                if shell_type:
                    host_vars['ansible_shell_type'] = shell_type

                host_keys = []
                for key in getattr(node, 'host_keys', []):
                    if port != 22:
                        host_keys.append("[%s]:%s %s" % (ip, port, key))
                    else:
                        host_keys.append("%s %s" % (ip, key))
                if not getattr(node, 'host_keys', None):
                    host_vars['ansible_ssh_common_args'] = \
                        '-o StrictHostKeyChecking=false'

                hosts.append(dict(
                    name=name,
                    host_vars=host_vars,
                    host_keys=host_keys))
        return hosts

    def _blockPluginDirs(self, path):
        '''Prevent execution of playbooks or roles with plugins

        Plugins are loaded from roles and also if there is a plugin
        dir adjacent to the playbook.  Throw an error if the path
        contains a location that would cause a plugin to get loaded.

        '''
        for entry in os.listdir(path):
            entry = os.path.join(path, entry)
            if os.path.isdir(entry) and entry.endswith('_plugins'):
                raise PluginFoundError(
                    "Ansible plugin dir %s found adjacent to playbook %s in "
                    "non-trusted repo." % (entry, path))

    def findPlaybook(self, path, trusted=False):
        if os.path.exists(path):
            if not trusted:
                # Plugins can be defined in multiple locations within the
                # playbook's subtree.
                #
                #  1. directly within the playbook:
                #       block playbook_dir/*_plugins
                #
                #  2. within a role defined in playbook_dir/<rolename>:
                #       block playbook_dir/*/*_plugins
                #
                #  3. within a role defined in playbook_dir/roles/<rolename>:
                #       block playbook_dir/roles/*/*_plugins

                playbook_dir = os.path.dirname(os.path.abspath(path))
                paths_to_check = []

                def addPathsToCheck(root_dir):
                    if os.path.isdir(root_dir):
                        for entry in os.listdir(root_dir):
                            entry = os.path.join(root_dir, entry)
                            if os.path.isdir(entry):
                                paths_to_check.append(entry)

                # handle case 1
                paths_to_check.append(playbook_dir)

                # handle case 2
                addPathsToCheck(playbook_dir)

                # handle case 3
                addPathsToCheck(os.path.join(playbook_dir, 'roles'))

                for path_to_check in paths_to_check:
                    self._blockPluginDirs(path_to_check)

            return path
        raise ExecutorError("Unable to find playbook %s" % path)

    def preparePlaybooks(self, args):
        self.writeAnsibleConfig(self.jobdir.setup_playbook)
        self.writeAnsibleConfig(self.jobdir.freeze_playbook)

        for playbook in self.job.pre_run:
            jobdir_playbook = self.jobdir.addPrePlaybook()
            self.preparePlaybook(jobdir_playbook, playbook, args)

        job_playbook = None
        for playbook in self.job.run:
            jobdir_playbook = self.jobdir.addPlaybook()
            self.preparePlaybook(jobdir_playbook, playbook, args)
            if jobdir_playbook.path is not None:
                if job_playbook is None:
                    job_playbook = jobdir_playbook

        if job_playbook is None:
            raise ExecutorError("No playbook specified")

        for playbook in self.job.post_run:
            jobdir_playbook = self.jobdir.addPostPlaybook()
            self.preparePlaybook(jobdir_playbook, playbook, args)

        for playbook in self.job.cleanup_run:
            jobdir_playbook = self.jobdir.addCleanupPlaybook()
            self.preparePlaybook(jobdir_playbook, playbook, args)

    def preparePlaybook(self, jobdir_playbook, playbook, args):
        # Check out the playbook repo if needed and set the path to
        # the playbook that should be run.
        self.log.debug("Prepare playbook repo for %s: %s@%s" %
                       (playbook['trusted'] and 'trusted' or 'untrusted',
                        playbook['project'], playbook['branch']))
        source = self.executor_server.connections.getSource(
            playbook['connection'])
        project = source.getProject(playbook['project'])
        branch = playbook['branch']
        jobdir_playbook.trusted = playbook['trusted']
        jobdir_playbook.branch = branch
        jobdir_playbook.project_canonical_name = project.canonical_name
        jobdir_playbook.canonical_name_and_path = os.path.join(
            project.canonical_name, playbook['path'])
        path = None

        if not jobdir_playbook.trusted:
            path = self.checkoutUntrustedProject(project, branch, args)
        else:
            path = self.checkoutTrustedProject(project, branch, args)
        path = os.path.join(path, playbook['path'])

        jobdir_playbook.path = self.findPlaybook(
            path,
            trusted=jobdir_playbook.trusted)

        # If this playbook doesn't exist, don't bother preparing
        # roles.
        if not jobdir_playbook.path:
            return

        for role in playbook['roles']:
            self.prepareRole(jobdir_playbook, role, args)

        secrets = self.decryptSecrets(playbook['secrets'])
        secrets = self.mergeSecretVars(secrets)
        if secrets:
            check_varnames(secrets)
            secrets = yaml.mark_strings_unsafe(secrets)
            jobdir_playbook.secrets_content = yaml.ansible_unsafe_dump(
                secrets, default_flow_style=False)
            jobdir_playbook.secrets_keys = set(secrets.keys())

        self.writeAnsibleConfig(jobdir_playbook)

    def decryptSecrets(self, secrets):
        """Decrypt the secrets dictionary provided by the scheduler

        The input dictionary has a frozen secret dictionary as its
        value (with encrypted data and the project name of the key to
        use to decrypt it).

        The output dictionary simply has decrypted data as its value.

        :param dict secrets: The playbook secrets dictionary from the
            scheduler

        :returns: A decrypted secrets dictionary

        """
        ret = {}
        for secret_name, secret_index in secrets.items():
            frozen_secret = self.job.secrets[secret_index]
            secret = zuul.model.Secret(secret_name, None)
            secret.secret_data = yaml.encrypted_load(
                frozen_secret['encrypted_data'])
            private_secrets_key, public_secrets_key = \
                self.executor_server.keystore.getProjectSecretsKeys(
                    frozen_secret['connection_name'],
                    frozen_secret['project_name'])
            secret = secret.decrypt(private_secrets_key)
            ret[secret_name] = secret.secret_data
        return ret

    def checkoutTrustedProject(self, project, branch, args):
        pi = self.jobdir.getTrustedProject(project.canonical_name,
                                           branch)
        if not pi:
            pi = self.jobdir.addTrustedProject(project.canonical_name,
                                               branch)
            self.log.debug("Cloning %s@%s into new trusted space %s",
                           project, branch, pi.root)
            # We always use the golang scheme for playbook checkouts
            # (so that the path indicates the canonical repo name for
            # easy debugging; there are no concerns with collisions
            # since we only have one repo in the working dir).
            merger = self.executor_server._getMerger(
                pi.root,
                self.executor_server.merge_root,
                logger=self.log,
                scheme=zuul.model.SCHEME_GOLANG)
            commit = merger.checkoutBranch(
                project.connection_name, project.name,
                branch,
                repo_state=self.repo_state,
                process_worker=self.executor_server.process_worker,
                zuul_event_id=self.zuul_event_id)
            pi.commit = commit.hexsha
        else:
            self.log.debug("Using existing repo %s@%s in trusted space %s",
                           project, branch, pi.root)

        path = os.path.join(pi.root,
                            project.canonical_hostname,
                            project.name)
        return path

    def checkoutUntrustedProject(self, project, branch, args):
        pi = self.jobdir.getUntrustedProject(project.canonical_name,
                                             branch)
        if not pi:
            pi = self.jobdir.addUntrustedProject(project.canonical_name,
                                                 branch)
            # If the project is in the dependency chain, clone from
            # there so we pick up any speculative changes, otherwise,
            # clone from the cache.
            #
            # We always use the golang scheme for playbook checkouts
            # (so that the path indicates the canonical repo name for
            # easy debugging; there are no concerns with collisions
            # since we only have one repo in the working dir).
            merger = None
            for p in args['projects']:
                if (p['connection'] == project.connection_name and
                    p['name'] == project.name):
                    # We already have this repo prepared
                    self.log.debug("Found workdir repo for untrusted project")
                    merger = self.executor_server._getMerger(
                        pi.root,
                        self.jobdir.src_root,
                        logger=self.log,
                        scheme=zuul.model.SCHEME_GOLANG,
                        cache_scheme=self.scheme)
                    break

            repo_state = None
            if merger is None:
                merger = self.executor_server._getMerger(
                    pi.root,
                    self.executor_server.merge_root,
                    logger=self.log,
                    scheme=zuul.model.SCHEME_GOLANG)

                # If we don't have this repo yet prepared we need to restore
                # the repo state. Otherwise we have speculative merges in the
                # repo and must not restore the repo state again.
                repo_state = self.repo_state

            self.log.debug("Cloning %s@%s into new untrusted space %s",
                           project, branch, pi.root)
            commit = merger.checkoutBranch(
                project.connection_name, project.name,
                branch, repo_state=repo_state,
                process_worker=self.executor_server.process_worker,
                zuul_event_id=self.zuul_event_id)
            pi.commit = commit.hexsha
        else:
            self.log.debug("Using existing repo %s@%s in trusted space %s",
                           project, branch, pi.root)

        path = os.path.join(pi.root,
                            project.canonical_hostname,
                            project.name)
        return path

    def mergeSecretVars(self, secrets):
        '''
        Merge secret return data with secrets.

        :arg secrets dict: Actual Zuul secrets.
        '''

        secret_vars = self.job.secret_parent_data or {}

        # We need to handle secret vars specially.  We want to pass
        # them to Ansible as we do secrets, but we want them to have
        # the lowest priority.  In order to accomplish that, we will
        # simply remove any top-level secret var with the same name as
        # anything above it in precedence.

        other_vars = set()
        other_vars.update(self.job.combined_variables.keys())
        for group_vars in self.job.group_variables.values():
            other_vars.update(group_vars.keys())
        for host_vars in self.job.host_variables.values():
            other_vars.update(host_vars.keys())
        other_vars.update(self.job.extra_variables.keys())
        other_vars.update(secrets.keys())

        ret = secret_vars.copy()
        for key in other_vars:
            ret.pop(key, None)

        # Add in the actual secrets
        if secrets:
            ret.update(secrets)

        return ret

    def prepareRole(self, jobdir_playbook, role, args):
        if role['type'] == 'zuul':
            role_info = jobdir_playbook.addRole()
            self.prepareZuulRole(jobdir_playbook, role, args, role_info)

    def findRole(self, path, trusted=False):
        d = os.path.join(path, 'tasks')
        if os.path.isdir(d):
            # This is a bare role
            if not trusted:
                self._blockPluginDirs(path)
            # None signifies that the repo is a bare role
            return None
        d = os.path.join(path, 'roles')
        if os.path.isdir(d):
            # This repo has a collection of roles
            if not trusted:
                self._blockPluginDirs(d)
                for entry in os.listdir(d):
                    entry_path = os.path.join(d, entry)
                    if os.path.isdir(entry_path):
                        self._blockPluginDirs(entry_path)
            return d
        # It is neither a bare role, nor a collection of roles
        raise RoleNotFoundError("Unable to find role in %s" % (path,))

    def prepareZuulRole(self, jobdir_playbook, role, args, role_info):
        self.log.debug("Prepare zuul role for %s" % (role,))
        # Check out the role repo if needed
        source = self.executor_server.connections.getSource(
            role['connection'])
        project = source.getProject(role['project'])
        name = role['target_name']
        path = None

        # Find the branch to use for this role.  We should generally
        # follow the normal fallback procedure, unless this role's
        # project is the playbook's project, in which case we should
        # use the playbook branch.
        if jobdir_playbook.project_canonical_name == project.canonical_name:
            branch = jobdir_playbook.branch
            self.log.debug("Role project is playbook project, "
                           "using playbook branch %s", branch)
            role_info.checkout_description = 'playbook branch'
            role_info.checkout = branch
        else:
            # Find if the project is one of the job-specified projects.
            # If it is, we can honor the project checkout-override options.
            args_project = {}
            for p in args['projects']:
                if (p['canonical_name'] == project.canonical_name):
                    args_project = p
                    break

            branch, selected_desc = self.resolveBranch(
                project.canonical_name,
                None,
                args['branch'],
                self.job.override_branch,
                self.job.override_checkout,
                args_project.get('override_branch'),
                args_project.get('override_checkout'),
                role['project_default_branch'])
            self.log.debug("Role using %s %s", selected_desc, branch)
            role_info.checkout_description = selected_desc
            role_info.checkout = branch

        if not jobdir_playbook.trusted:
            path = self.checkoutUntrustedProject(project, branch, args)
        else:
            path = self.checkoutTrustedProject(project, branch, args)

        # The name of the symlink is the requested name of the role
        # (which may be the repo name or may be something else; this
        # can come into play if this is a bare role).
        link = os.path.join(role_info.root, name)
        link = os.path.realpath(link)
        if not link.startswith(os.path.realpath(role_info.root)):
            raise ExecutorError("Invalid role name %s" % name)
        os.symlink(path, link)

        role_info.link_name = link
        role_info.link_target = path
        try:
            role_path = self.findRole(link, trusted=jobdir_playbook.trusted)
        except RoleNotFoundError:
            if role['implicit']:
                self.log.debug("Implicit role not found in %s", link)
                return
            raise
        except PluginFoundError:
            if role['implicit']:
                self.log.info("Not adding implicit role %s due to "
                              "plugin", link)
                return
            raise
        if role_path is None:
            # In the case of a bare role, add the containing directory
            role_path = role_info.root
        role_info.role_path = role_path
        self.log.debug("Adding role path %s", role_path)
        jobdir_playbook.roles_path.append(role_path)

    def prepareKubeConfig(self, jobdir, data):
        kube_cfg_path = jobdir.kubeconfig
        if os.path.exists(kube_cfg_path):
            kube_cfg = yaml.safe_load(open(kube_cfg_path))
        else:
            kube_cfg = {
                'apiVersion': 'v1',
                'kind': 'Config',
                'preferences': {},
                'users': [],
                'clusters': [],
                'contexts': [],
                'current-context': None,
            }
        # Add cluster
        cluster_name = urlsplit(data['host']).netloc.replace('.', '-')

        # Do not add a cluster/server that already exists in the kubeconfig
        # because that leads to 'duplicate name' errors on multi-node builds.
        # Also, as the cluster name directly corresponds to a server, there
        # is no need to add it twice.
        if cluster_name not in [c['name'] for c in kube_cfg['clusters']]:
            cluster = {
                'server': data['host'],
            }
            if data.get('ca_crt'):
                cluster['certificate-authority-data'] = data['ca_crt']
            if data['skiptls']:
                cluster['insecure-skip-tls-verify'] = True
            kube_cfg['clusters'].append({
                'name': cluster_name,
                'cluster': cluster,
            })

        # Add user
        user_name = "%s:%s" % (data['namespace'], data['user'])
        kube_cfg['users'].append({
            'name': user_name,
            'user': {
                'token': data['token'],
            },
        })

        # Add context
        data['context_name'] = "%s/%s" % (user_name, cluster_name)
        kube_cfg['contexts'].append({
            'name': data['context_name'],
            'context': {
                'user': user_name,
                'cluster': cluster_name,
                'namespace': data['namespace']
            }
        })
        if not kube_cfg['current-context']:
            kube_cfg['current-context'] = data['context_name']

        with open(kube_cfg_path, "w") as of:
            of.write(yaml.safe_dump(kube_cfg, default_flow_style=False))

    def prepareNodes(self, args):
        # Returns the zuul.resources ansible variable for later user

        # The (non-resource) nodes we want to keep in the inventory
        inventory_nodes = []
        # The zuul.resources ansible variable
        zuul_resources = {}
        for node in self.nodeset.getNodes():
            if node.connection_type in (
                    'namespace', 'project', 'kubectl'):
                # TODO: decrypt resource data using scheduler key
                data = node.connection_port
                # Setup kube/config file
                self.prepareKubeConfig(self.jobdir, data)
                # Convert connection_port in kubectl connection parameters
                node.connection_port = None
                node.kubectl_namespace = data['namespace']
                node.kubectl_context = data['context_name']
                # Add node information to zuul.resources
                zuul_resources[node.name[0]] = {
                    'namespace': data['namespace'],
                    'context': data['context_name'],
                }
                if node.connection_type in ('project', 'namespace'):
                    # Project are special nodes that are not the inventory
                    pass
                else:
                    inventory_nodes.append(node)
                    # Add the real pod name to the resources_var
                    zuul_resources[node.name[0]]['pod'] = data['pod']

                    fwd = KubeFwd(zuul_event_id=self.zuul_event_id,
                                  build=self.build_request.uuid,
                                  kubeconfig=self.jobdir.kubeconfig,
                                  context=data['context_name'],
                                  namespace=data['namespace'],
                                  pod=data['pod'])
                    try:
                        fwd.start()
                        self.port_forwards.append(fwd)
                        zuul_resources[node.name[0]]['stream_port'] = \
                            fwd.port
                    except Exception:
                        self.log.exception("Unable to start port forward:")
                        self.log.error("Kubectl and socat are required for "
                                       "streaming logs")
            else:
                # A normal node to include in inventory
                inventory_nodes.append(node)

        self.host_list = self.getHostList(args, inventory_nodes)

        with open(self.jobdir.known_hosts, 'w') as known_hosts:
            for node in self.host_list:
                for key in node['host_keys']:
                    known_hosts.write('%s\n' % key)
        return zuul_resources

    def prepareVars(self, args, zuul_resources):
        all_vars = self.job.combined_variables.copy()
        check_varnames(all_vars)

        # Check the group and extra var names for safety; they'll get
        # merged later
        for group in self.nodeset.getGroups():
            group_vars = self.job.group_variables.get(group.name, {})
            check_varnames(group_vars)

        check_varnames(self.job.extra_variables)

        zuul_vars = {}
        # Start with what the client supplied
        zuul_vars = args['zuul'].copy()
        # Overlay the zuul.resources we set in prepareNodes
        zuul_vars.update({'resources': zuul_resources})

        # Add in executor info
        zuul_vars['executor'] = dict(
            hostname=self.executor_server.hostname,
            src_root=self.jobdir.src_root,
            log_root=self.jobdir.log_root,
            work_root=self.jobdir.work_root,
            result_data_file=self.jobdir.result_data_file,
            inventory_file=self.jobdir.inventory)

        # Add playbook_context info
        zuul_vars['playbook_context'] = dict(
            playbook_projects={},
            playbooks=[],
        )
        strip = len(self.jobdir.root) + 1
        for pi in self.jobdir.trusted_projects.values():
            root = os.path.join(pi.root[strip:], pi.canonical_name)
            zuul_vars['playbook_context']['playbook_projects'][
                root] = pi.toDict()
        for pi in self.jobdir.untrusted_projects.values():
            root = os.path.join(pi.root[strip:], pi.canonical_name)
            zuul_vars['playbook_context']['playbook_projects'][
                root] = pi.toDict()
        for pb in self.jobdir.playbooks:
            zuul_vars['playbook_context']['playbooks'].append(dict(
                path=pb.path[strip:],
                roles=[ri.toDict(self.jobdir.root) for ri in pb.roles
                       if ri.role_path is not None],
            ))

        with open(self.jobdir.zuul_vars, 'w') as zuul_vars_yaml:
            zuul_vars_yaml.write(
                yaml.safe_dump({'zuul': zuul_vars}, default_flow_style=False))
        self.zuul_vars = zuul_vars

        # Squash all and extra vars into localhost (it's not
        # explicitly listed).
        localhost = {
            'name': 'localhost',
            'host_vars': {},
        }
        host_list = self.host_list + [localhost]
        self.original_hostvars = squash_variables(
            host_list, self.nodeset, all_vars,
            self.job.group_variables, self.job.extra_variables)

    def loadFrozenHostvars(self):
        # Read in the frozen hostvars, and remove the frozen variable
        # from the fact cache.

        # localhost hold our "all" vars.
        localhost = {
            'name': 'localhost',
        }
        host_list = self.host_list + [localhost]
        for host in host_list:
            self.log.debug("Loading frozen vars for %s", host['name'])
            path = os.path.join(self.jobdir.fact_cache, host['name'])
            facts = {}
            if os.path.exists(path):
                with open(path) as f:
                    facts = json.loads(f.read())
            self.frozen_hostvars[host['name']] = facts.pop('_zuul_frozen', {})
            with open(path, 'w') as f:
                f.write(json.dumps(facts))

            # While we're here, update both hostvars dicts with
            # an !unsafe copy of the original input as well.
            unsafe = yaml.mark_strings_unsafe(
                self.original_hostvars[host['name']])
            self.frozen_hostvars[host['name']]['unsafe_vars'] = unsafe

            unsafe = yaml.mark_strings_unsafe(
                self.original_hostvars[host['name']])
            self.original_hostvars[host['name']]['unsafe_vars'] = unsafe

    def writeDebugInventory(self):
        # This file is unused by Zuul, but the base jobs copy it to logs
        # for debugging, so let's continue to put something there.
        inventory = make_inventory_dict(
            self.host_list, self.nodeset, self.original_hostvars)

        inventory['all']['vars']['zuul'] = self.zuul_vars
        with open(self.jobdir.inventory, 'w') as inventory_yaml:
            inventory_yaml.write(
                yaml.ansible_unsafe_dump(
                    inventory,
                    ignore_aliases=True,
                    default_flow_style=False))

    def writeSetupInventory(self):
        jobdir_playbook = self.jobdir.setup_playbook
        setup_inventory = make_setup_inventory_dict(
            self.host_list, self.original_hostvars)
        setup_inventory = yaml.mark_strings_unsafe(setup_inventory)

        with open(jobdir_playbook.inventory, 'w') as inventory_yaml:
            # Write this inventory with !unsafe tags to avoid mischief
            # since we're running without bwrap.
            inventory_yaml.write(
                yaml.ansible_unsafe_dump(setup_inventory,
                                         default_flow_style=False))

    def writeInventory(self, jobdir_playbook, hostvars):
        inventory = make_inventory_dict(
            self.host_list, self.nodeset, hostvars,
            remove_keys=jobdir_playbook.secrets_keys)

        with open(jobdir_playbook.inventory, 'w') as inventory_yaml:
            inventory_yaml.write(
                yaml.ansible_unsafe_dump(inventory, default_flow_style=False))

    def writeLoggingConfig(self):
        self.log.debug("Writing logging config for job %s %s",
                       self.jobdir.job_output_file,
                       self.jobdir.logging_json)
        logging_config = zuul.ansible.logconfig.JobLoggingConfig(
            job_output_file=self.jobdir.job_output_file)
        logging_config.writeJson(self.jobdir.logging_json)

    def writeAnsibleConfig(self, jobdir_playbook):
        trusted = jobdir_playbook.trusted

        # TODO(mordred) This should likely be extracted into a more generalized
        #               mechanism for deployers being able to add callback
        #               plugins.
        if self.ara_callbacks:
            callback_path = '%s:%s' % (
                self.callback_dir,
                os.path.dirname(self.ara_callbacks))
        else:
            callback_path = self.callback_dir
        with open(jobdir_playbook.ansible_config, 'w') as config:
            config.write('[defaults]\n')
            config.write('inventory = %s\n' % jobdir_playbook.inventory)
            config.write('local_tmp = %s\n' % self.jobdir.local_tmp)
            config.write('retry_files_enabled = False\n')
            config.write('gathering = smart\n')
            config.write('fact_caching = jsonfile\n')
            config.write('fact_caching_connection = %s\n' %
                         self.jobdir.fact_cache)
            config.write('library = %s\n'
                         % self.library_dir)
            config.write('command_warnings = False\n')
            # Disable the Zuul callback plugins for the freeze playbooks
            # as that output is verbose and would be confusing for users.
            if jobdir_playbook != self.jobdir.freeze_playbook:
                config.write('callback_plugins = %s\n' % callback_path)
                config.write('stdout_callback = zuul_stream\n')
            config.write('filter_plugins = %s\n'
                         % self.filter_dir)
            config.write('nocows = True\n')  # save useless stat() calls
            # bump the timeout because busy nodes may take more than
            # 10s to respond
            config.write('timeout = 30\n')

            # We need the general action dir to make the zuul_return plugin
            # available to every job.
            action_dirs = [self.action_dir_general]
            if not trusted:
                # Untrusted jobs add the action dir which makes sure localhost
                # modules are restricted where needed. Further the command
                # plugin needs to be restricted and also inject zuul_log_id
                # to make log streaming work.
                action_dirs.append(self.action_dir)
                config.write('lookup_plugins = %s\n'
                             % self.lookup_dir)
            else:
                # Trusted jobs add the actiontrusted dir which adds the
                # unrestricted command plugin to inject zuul_log_id to make
                # log streaming work.
                action_dirs.append(self.action_dir_trusted)

            config.write('action_plugins = %s\n'
                         % ':'.join(action_dirs))

            if jobdir_playbook.roles_path:
                config.write('roles_path = %s\n' % ':'.join(
                    jobdir_playbook.roles_path))

            # On playbooks with secrets we want to prevent the
            # printing of args since they may be passed to a task or a
            # role. Otherwise, printing the args could be useful for
            # debugging.
            config.write('display_args_to_stdout = %s\n' %
                         str(not jobdir_playbook.secrets_content))

            # Increase the internal poll interval of ansible.
            # The default interval of 0.001s is optimized for interactive
            # ui at the expense of CPU load. As we have a non-interactive
            # automation use case a longer poll interval is more suitable
            # and reduces CPU load of the ansible process.
            config.write('internal_poll_interval = 0.01\n')

            if self.ansible_callbacks:
                config.write('callback_whitelist =\n')
                for callback in self.ansible_callbacks.keys():
                    config.write('    %s,\n' % callback)

            config.write('[ssh_connection]\n')
            # NOTE(pabelanger): Try up to 3 times to run a task on a host, this
            # helps to mitigate UNREACHABLE host errors with SSH.
            config.write('retries = 3\n')
            # NB: when setting pipelining = True, keep_remote_files
            # must be False (the default).  Otherwise it apparently
            # will override the pipelining option and effectively
            # disable it.  Pipelining has a side effect of running the
            # command without a tty (ie, without the -tt argument to
            # ssh).  We require this behavior so that if a job runs a
            # command which expects interactive input on a tty (such
            # as sudo) it does not hang.
            config.write('pipelining = True\n')
            config.write('control_path_dir = %s\n' % self.jobdir.control_path)
            ssh_args = "-o ControlMaster=auto -o ControlPersist=60s " \
                "-o ServerAliveInterval=60 " \
                "-o UserKnownHostsFile=%s" % self.jobdir.known_hosts
            config.write('ssh_args = %s\n' % ssh_args)

            if self.ansible_callbacks:
                for cb_name, cb_config in self.ansible_callbacks.items():
                    config.write("[callback_%s]\n" % cb_name)
                    for k, n in cb_config.items():
                        config.write("%s = %s\n" % (k, n))

    def _ansibleTimeout(self, msg):
        self.log.warning(msg)
        self.abortRunningProc()

    def abortRunningProc(self):
        with self.proc_lock:
            if self.proc and not self.cleanup_started:
                self.log.debug("Abort: sending kill signal to job "
                               "process group")
                try:
                    pgid = os.getpgid(self.proc.pid)
                    os.killpg(pgid, signal.SIGKILL)
                except Exception:
                    self.log.exception(
                        "Exception while killing ansible process:")
            elif self.proc and self.cleanup_started:
                self.log.debug("Abort: cleanup is in progress")
            else:
                self.log.debug("Abort: no process is running")

    def runAnsible(self, cmd, timeout, playbook, ansible_version,
                   wrapped=True, cleanup=False):
        config_file = playbook.ansible_config
        env_copy = {key: value
                    for key, value in os.environ.copy().items()
                    if not key.startswith("ZUUL_")}
        env_copy.update(self.ssh_agent.env)
        if self.ara_callbacks:
            env_copy['ARA_LOG_CONFIG'] = self.jobdir.logging_json
        env_copy['ZUUL_JOB_LOG_CONFIG'] = self.jobdir.logging_json
        env_copy['ZUUL_JOBDIR'] = self.jobdir.root
        if self.executor_server.log_console_port != DEFAULT_STREAM_PORT:
            env_copy['ZUUL_CONSOLE_PORT'] = str(
                self.executor_server.log_console_port)
        env_copy['TMP'] = self.jobdir.local_tmp
        pythonpath = env_copy.get('PYTHONPATH')
        if pythonpath:
            pythonpath = [pythonpath]
        else:
            pythonpath = []

        ansible_dir = self.executor_server.ansible_manager.getAnsibleDir(
            ansible_version)
        pythonpath = [ansible_dir] + pythonpath
        env_copy['PYTHONPATH'] = os.path.pathsep.join(pythonpath)

        if playbook.trusted:
            opt_prefix = 'trusted'
        else:
            opt_prefix = 'untrusted'
        ro_paths = get_default(self.executor_server.config, 'executor',
                               '%s_ro_paths' % opt_prefix)
        rw_paths = get_default(self.executor_server.config, 'executor',
                               '%s_rw_paths' % opt_prefix)
        ro_paths = ro_paths.split(":") if ro_paths else []
        rw_paths = rw_paths.split(":") if rw_paths else []

        ro_paths.append(ansible_dir)
        ro_paths.append(
            self.executor_server.ansible_manager.getAnsibleInstallDir(
                ansible_version))
        ro_paths.append(self.jobdir.ansible_root)
        ro_paths.append(self.jobdir.trusted_root)
        ro_paths.append(self.jobdir.untrusted_root)
        ro_paths.append(playbook.root)

        rw_paths.append(self.jobdir.ansible_cache_root)

        if self.executor_variables_file:
            ro_paths.append(self.executor_variables_file)

        secrets = {}
        if playbook.secrets_content:
            secrets[playbook.secrets] = playbook.secrets_content

        if wrapped:
            wrapper = self.executor_server.execution_wrapper
        else:
            wrapper = self.executor_server.connections.drivers['nullwrap']

        context = wrapper.getExecutionContext(ro_paths, rw_paths, secrets)

        popen = context.getPopen(
            work_dir=self.jobdir.work_root,
            ssh_auth_sock=env_copy.get('SSH_AUTH_SOCK'))

        env_copy['ANSIBLE_CONFIG'] = config_file
        # NOTE(pabelanger): Default HOME variable to jobdir.work_root, as it is
        # possible we don't bind mount current zuul user home directory.
        env_copy['HOME'] = self.jobdir.work_root

        with self.proc_lock:
            if self.aborted and not cleanup:
                return (self.RESULT_ABORTED, None)
            self.log.debug("Ansible command: ANSIBLE_CONFIG=%s ZUUL_JOBDIR=%s "
                           "ZUUL_JOB_LOG_CONFIG=%s PYTHONPATH=%s TMP=%s %s",
                           env_copy['ANSIBLE_CONFIG'],
                           env_copy['ZUUL_JOBDIR'],
                           env_copy['ZUUL_JOB_LOG_CONFIG'],
                           env_copy['PYTHONPATH'],
                           env_copy['TMP'],
                           " ".join(shlex.quote(c) for c in cmd))
            self.proc = popen(
                cmd,
                cwd=self.jobdir.work_root,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                start_new_session=True,
                env=env_copy,
            )

        syntax_buffer = []
        ret = None
        if timeout:
            watchdog = Watchdog(timeout, self._ansibleTimeout,
                                ("Ansible timeout exceeded: %s" % timeout,))
            watchdog.start()
        try:
            ansible_log = get_annotated_logger(
                logging.getLogger("zuul.AnsibleJob.output"),
                self.zuul_event_id, build=self.build_request.uuid)

            # Use manual idx instead of enumerate so that RESULT lines
            # don't count towards BUFFER_LINES_FOR_SYNTAX
            idx = 0
            for line in iter(self.proc.stdout.readline, b''):
                if line.startswith(b'RESULT'):
                    # TODO(mordred) Process result commands if sent
                    continue
                else:
                    idx += 1
                if idx < BUFFER_LINES_FOR_SYNTAX:
                    syntax_buffer.append(line)

                if line.startswith(b'fatal'):
                    line = line[:8192].rstrip()
                else:
                    line = line[:1024].rstrip()

                ansible_log.debug("Ansible output: %s" % (line,))
            self.log.debug("Ansible output terminated")
            try:
                cpu_times = self.proc.cpu_times()
                self.log.debug("Ansible cpu times: user=%.2f, system=%.2f, "
                               "children_user=%.2f, "
                               "children_system=%.2f" %
                               (cpu_times.user, cpu_times.system,
                                cpu_times.children_user,
                                cpu_times.children_system))
                self.cpu_times['user'] += cpu_times.user
                self.cpu_times['system'] += cpu_times.system
                self.cpu_times['children_user'] += cpu_times.children_user
                self.cpu_times['children_system'] += cpu_times.children_system
            except psutil.NoSuchProcess:
                self.log.warn("Cannot get cpu_times for process %d. Is your"
                              "/proc mounted with hidepid=2"
                              " on an old linux kernel?", self.proc.pid)
            ret = self.proc.wait()
            self.log.debug("Ansible exit code: %s" % (ret,))
        finally:
            if timeout:
                watchdog.stop()
                self.log.debug("Stopped watchdog")
            self.log.debug("Stopped disk job killer")

        with self.proc_lock:
            self.proc.stdout.close()
            self.proc = None

        if timeout and watchdog.timed_out:
            return (self.RESULT_TIMED_OUT, None)
        # Note: Unlike documented ansible currently wrongly returns 4 on
        # unreachable so we have the zuul_unreachable callback module that
        # creates the file job-output.unreachable in case there were
        # unreachable nodes. This can be removed once ansible returns a
        # distinct value for unreachable.
        if ret == 3 or os.path.exists(self.jobdir.job_unreachable_file):
            # AnsibleHostUnreachable: We had a network issue connecting to
            # our zuul-worker.
            return (self.RESULT_UNREACHABLE, None)
        elif ret == -9:
            # Received abort request.
            return (self.RESULT_ABORTED, None)
        elif ret == 1:
            with open(self.jobdir.job_output_file, 'a') as job_output:
                found_marker = False
                for line in syntax_buffer:
                    if line.startswith(b'ERROR!'):
                        found_marker = True
                    if not found_marker:
                        continue
                    job_output.write("{now} | {line}\n".format(
                        now=datetime.datetime.now(),
                        line=line.decode('utf-8').rstrip()))
        elif ret == 4:
            # Ansible could not parse the yaml.
            self.log.debug("Ansible parse error")
            # TODO(mordred) If/when we rework use of logger in ansible-playbook
            # we'll want to change how this works to use that as well. For now,
            # this is what we need to do.
            # TODO(mordred) We probably want to put this into the json output
            # as well.
            with open(self.jobdir.job_output_file, 'a') as job_output:
                job_output.write("{now} | ANSIBLE PARSE ERROR\n".format(
                    now=datetime.datetime.now()))
                for line in syntax_buffer:
                    job_output.write("{now} | {line}\n".format(
                        now=datetime.datetime.now(),
                        line=line.decode('utf-8').rstrip()))
        elif ret == 250:
            # Unexpected error from ansible
            with open(self.jobdir.job_output_file, 'a') as job_output:
                job_output.write("{now} | UNEXPECTED ANSIBLE ERROR\n".format(
                    now=datetime.datetime.now()))
                found_marker = False
                for line in syntax_buffer:
                    if line.startswith(b'ERROR! Unexpected Exception'):
                        found_marker = True
                    if not found_marker:
                        continue
                    job_output.write("{now} | {line}\n".format(
                        now=datetime.datetime.now(),
                        line=line.decode('utf-8').rstrip()))
        elif ret == 2:
            with open(self.jobdir.job_output_file, 'a') as job_output:
                found_marker = False
                for line in syntax_buffer:
                    # This is a workaround to detect winrm connection failures
                    # that are not detected by ansible. These can be detected
                    # if the string 'FATAL ERROR DURING FILE TRANSFER' is in
                    # the ansible output. In this case we should treat the
                    # host as unreachable and retry the job.
                    if b'FATAL ERROR DURING FILE TRANSFER' in line:
                        return self.RESULT_UNREACHABLE, None

                    # Extract errors for special cases that are treated like
                    # task errors by Ansible (e.g. missing role when using
                    # 'include_role').
                    if line.startswith(b'ERROR!'):
                        found_marker = True
                    if not found_marker:
                        continue
                    job_output.write("{now} | {line}\n".format(
                        now=datetime.datetime.now(),
                        line=line.decode('utf-8').rstrip()))

        if self.aborted:
            return (self.RESULT_ABORTED, None)

        return (self.RESULT_NORMAL, ret)

    def runAnsibleSetup(self, playbook, ansible_version):
        if self.executor_server.verbose:
            verbose = '-vvv'
        else:
            verbose = '-v'

        # TODO: select correct ansible version from job
        ansible = self.executor_server.ansible_manager.getAnsibleCommand(
            ansible_version,
            command='ansible')
        cmd = [ansible, '*', verbose, '-m', 'setup',
               '-i', playbook.inventory,
               '-a', 'gather_subset=!all']
        if self.executor_variables_file is not None:
            cmd.extend(['-e@%s' % self.executor_variables_file])

        result, code = self.runAnsible(
            cmd=cmd, timeout=self.executor_server.setup_timeout,
            playbook=playbook, ansible_version=ansible_version, wrapped=False)
        self.log.debug("Ansible complete, result %s code %s" % (
            self.RESULT_MAP[result], code))
        if self.executor_server.statsd:
            base_key = "zuul.executor.{hostname}.phase.setup"
            self.executor_server.statsd.incr(base_key + ".%s" %
                                             self.RESULT_MAP[result])
        return result, code

    def runAnsibleFreeze(self, playbook, ansible_version):
        if self.executor_server.verbose:
            verbose = '-vvv'
        else:
            verbose = '-v'

        # Create a play for each host with set_fact, and every
        # top-level variable.
        plays = []
        localhost = {
            'name': 'localhost',
        }
        for host in self.host_list + [localhost]:
            tasks = [{
                'set_fact': {
                    '_zuul_frozen': {},
                    'cacheable': True,
                },
            }]
            for var in self.original_hostvars[host['name']].keys():
                val = "{{ _zuul_frozen | combine({'%s': %s}) }}" % (var, var)
                task = {
                    'set_fact': {
                        '_zuul_frozen': val,
                        'cacheable': True,
                    },
                    'ignore_errors': True,
                }
                tasks.append(task)
            play = {
                'hosts': host['name'],
                'tasks': tasks,
            }
            if host['name'] == 'localhost':
                play['gather_facts'] = False
            plays.append(play)

        self.log.debug("Freeze playbook: %s", repr(plays))
        with open(self.jobdir.freeze_playbook.path, 'w') as f:
            f.write(yaml.safe_dump(plays, default_flow_style=False))

        cmd = [self.executor_server.ansible_manager.getAnsibleCommand(
            ansible_version), verbose, playbook.path]

        if self.executor_variables_file is not None:
            cmd.extend(['-e@%s' % self.executor_variables_file])

        cmd.extend(['-e', '@' + self.jobdir.ansible_vars_blacklist])
        cmd.extend(['-e', '@' + self.jobdir.zuul_vars])

        result, code = self.runAnsible(
            cmd=cmd, timeout=self.executor_server.setup_timeout,
            playbook=playbook, ansible_version=ansible_version)
        self.log.debug("Ansible freeze complete, result %s code %s" % (
            self.RESULT_MAP[result], code))

        return result, code

    def runAnsibleCleanup(self, playbook):
        # TODO(jeblair): This requires a bugfix in Ansible 2.4
        # Once this is used, increase the controlpersist timeout.
        return (self.RESULT_NORMAL, 0)

        if self.executor_server.verbose:
            verbose = '-vvv'
        else:
            verbose = '-v'

        cmd = ['ansible', '*', verbose, '-m', 'meta',
               '-a', 'reset_connection']

        result, code = self.runAnsible(
            cmd=cmd, timeout=60, playbook=playbook,
            wrapped=False)
        self.log.debug("Ansible complete, result %s code %s" % (
            self.RESULT_MAP[result], code))
        if self.executor_server.statsd:
            base_key = "zuul.executor.{hostname}.phase.cleanup"
            self.executor_server.statsd.incr(base_key + ".%s" %
                                             self.RESULT_MAP[result])
        return result, code

    def emitPlaybookBanner(self, playbook, step, phase, result=None):
        # This is used to print a header and a footer, respectively at the
        # beginning and the end of each playbook execution.
        # We are doing it from the executor rather than from a callback because
        # the parameters are not made available to the callback until it's too
        # late.
        phase = phase or ''
        trusted = playbook.trusted
        trusted = 'trusted' if trusted else 'untrusted'
        branch = playbook.branch
        playbook = playbook.canonical_name_and_path

        if phase and phase != 'run':
            phase = '{phase}-run'.format(phase=phase)
        phase = phase.upper()

        if result is not None:
            result = self.RESULT_MAP[result]
            msg = "{phase} {step} {result}: [{trusted} : {playbook}@{branch}]"
            msg = msg.format(phase=phase, step=step, result=result,
                             trusted=trusted, playbook=playbook, branch=branch)
        else:
            msg = "{phase} {step}: [{trusted} : {playbook}@{branch}]"
            msg = msg.format(phase=phase, step=step, trusted=trusted,
                             playbook=playbook, branch=branch)

        with open(self.jobdir.job_output_file, 'a') as job_output:
            job_output.write("{now} | {msg}\n".format(
                now=datetime.datetime.now(),
                msg=msg))

    def runAnsiblePlaybook(self, playbook, timeout, ansible_version,
                           success=None, phase=None, index=None):
        if playbook.trusted or playbook.secrets_content:
            self.writeInventory(playbook, self.frozen_hostvars)
        else:
            self.writeInventory(playbook, self.original_hostvars)

        if self.executor_server.verbose:
            verbose = '-vvv'
        else:
            verbose = '-v'

        cmd = [self.executor_server.ansible_manager.getAnsibleCommand(
            ansible_version), verbose, playbook.path]

        if success is not None:
            cmd.extend(['-e', 'zuul_success=%s' % str(bool(success))])

        if phase:
            cmd.extend(['-e', 'zuul_execution_phase=%s' % phase])

        if index is not None:
            cmd.extend(['-e', 'zuul_execution_phase_index=%s' % index])

        cmd.extend(['-e', 'zuul_execution_trusted=%s' % str(playbook.trusted)])
        cmd.extend([
            '-e',
            'zuul_execution_canonical_name_and_path=%s'
            % playbook.canonical_name_and_path])
        cmd.extend(['-e', 'zuul_execution_branch=%s' % str(playbook.branch)])

        if self.executor_variables_file is not None:
            cmd.extend(['-e@%s' % self.executor_variables_file])

        if not playbook.trusted:
            cmd.extend(['-e', '@' + self.jobdir.ansible_vars_blacklist])
        cmd.extend(['-e', '@' + self.jobdir.zuul_vars])

        self.emitPlaybookBanner(playbook, 'START', phase)

        result, code = self.runAnsible(cmd, timeout, playbook, ansible_version,
                                       cleanup=phase == 'cleanup')
        self.log.debug("Ansible complete, result %s code %s" % (
            self.RESULT_MAP[result], code))
        if self.executor_server.statsd:
            base_key = "zuul.executor.{hostname}.phase.{phase}"
            self.executor_server.statsd.incr(
                base_key + ".{result}",
                result=self.RESULT_MAP[result],
                phase=phase or 'unknown')

        self.emitPlaybookBanner(playbook, 'END', phase, result=result)
        return result, code


class ExecutorServer(BaseMergeServer):
    log = logging.getLogger("zuul.ExecutorServer")
    _ansible_manager_class = AnsibleManager
    _job_class = AnsibleJob
    _repo_locks_class = RepoLocks

    # Number of seconds past node expiration a hold request will remain
    EXPIRED_HOLD_REQUEST_TTL = 24 * 60 * 60

    def __init__(
        self,
        config,
        connections=None,
        jobdir_root=None,
        keep_jobdir=False,
        log_streaming_port=DEFAULT_FINGER_PORT,
        log_console_port=DEFAULT_STREAM_PORT,
    ):
        super().__init__(config, 'executor', connections)

        self.keep_jobdir = keep_jobdir
        self.jobdir_root = jobdir_root
        self.keystore = KeyStorage(
            self.zk_client,
            password=self._get_key_store_password())
        self.zk_context = ZKContext(self.zk_client, None, None, self.log)
        self._running = False
        self._command_running = False
        # TODOv3(mordred): make the executor name more unique --
        # perhaps hostname+pid.
        self.hostname = get_default(self.config, 'executor', 'hostname',
                                    socket.getfqdn())
        self.component_info = ExecutorComponent(
            self.zk_client, self.hostname, version=get_version_string())
        self.component_info.register()
        self.monitoring_server = MonitoringServer(self.config, 'executor',
                                                  self.component_info)
        self.monitoring_server.start()
        self.log_streaming_port = log_streaming_port
        self.governor_lock = threading.Lock()
        self.run_lock = threading.Lock()
        self.verbose = False
        self.command_map = dict(
            stop=self.stop,
            pause=self.pause,
            unpause=self.unpause,
            graceful=self.graceful,
            verbose=self.verboseOn,
            unverbose=self.verboseOff,
            keep=self.keep,
            nokeep=self.nokeep,
            repl=self.start_repl,
            norepl=self.stop_repl,
        )
        self.log_console_port = log_console_port
        self.repl = None

        statsd_extra_keys = {'hostname': self.hostname}
        self.statsd = get_statsd(config, statsd_extra_keys)
        self.default_username = get_default(self.config, 'executor',
                                            'default_username', 'zuul')
        self.disk_limit_per_job = int(get_default(self.config, 'executor',
                                                  'disk_limit_per_job', 250))
        self.setup_timeout = int(get_default(self.config, 'executor',
                                             'ansible_setup_timeout', 60))
        self.zone = get_default(self.config, 'executor', 'zone')
        self.allow_unzoned = get_default(self.config, 'executor',
                                         'allow_unzoned', False)

        # Those attributes won't change, so it's enough to set them once on the
        # component info.
        self.component_info.zone = self.zone
        self.component_info.allow_unzoned = self.allow_unzoned

        self.ansible_callbacks = {}
        for section_name in self.config.sections():
            cb_match = re.match(r'^ansible_callback ([\'\"]?)(.*)(\1)$',
                                section_name, re.I)
            if not cb_match:
                continue
            cb_name = cb_match.group(2)
            self.ansible_callbacks[cb_name] = dict(
                self.config.items(section_name)
            )

        # TODO(tobiash): Take cgroups into account
        self.update_workers = multiprocessing.cpu_count()
        self.update_threads = []
        # If the execution driver ever becomes configurable again,
        # this is where it would happen.
        execution_wrapper_name = 'bubblewrap'
        self.accepting_work = True
        self.execution_wrapper = connections.drivers[execution_wrapper_name]

        self.update_queue = DeduplicateQueue()

        command_socket = get_default(
            self.config, 'executor', 'command_socket',
            '/var/lib/zuul/executor.socket')
        self.command_socket = commandsocket.CommandSocket(command_socket)

        state_dir = get_default(self.config, 'executor', 'state_dir',
                                '/var/lib/zuul', expand_user=True)

        # If keep is not set, ensure the job dir is empty on startup,
        # in case we were uncleanly shut down.
        if not self.keep_jobdir:
            for fn in os.listdir(self.jobdir_root):
                fn = os.path.join(self.jobdir_root, fn)
                if not os.path.isdir(fn):
                    continue
                self.log.info("Deleting stale jobdir %s", fn)
                # We use rm here instead of shutil because of
                # https://bugs.python.org/issue22040
                jobdir = os.path.join(self.jobdir_root, fn)
                # First we need to ensure all directories are
                # writable to avoid permission denied error
                subprocess.Popen([
                    "find", jobdir,
                    # Filter non writable perms
                    "-type", "d", "!", "-perm", "/u+w",
                    # Replace by writable perms
                    "-exec", "chmod", "0700", "{}", "+"]).wait()
                if subprocess.Popen(["rm", "-Rf", jobdir]).wait():
                    raise RuntimeError("Couldn't delete: " + jobdir)

        self.job_workers = {}
        self.disk_accountant = DiskAccountant(self.jobdir_root,
                                              self.disk_limit_per_job,
                                              self.stopJobDiskFull,
                                              self.merge_root)

        self.pause_sensor = PauseSensor(get_default(self.config, 'executor',
                                                    'paused_on_start', False))
        self.log.info("Starting executor (hostname: %s) in %spaused mode" % (
            self.hostname, "" if self.pause_sensor.pause else "un"))
        cpu_sensor = CPUSensor(config)
        self.sensors = [
            cpu_sensor,
            HDDSensor(config),
            self.pause_sensor,
            RAMSensor(config),
            StartingBuildsSensor(self, cpu_sensor.max_load_avg, config)
        ]

        manage_ansible = get_default(
            self.config, 'executor', 'manage_ansible', True)
        ansible_dir = os.path.join(state_dir, 'ansible')
        ansible_install_root = get_default(
            self.config, 'executor', 'ansible_root', None)
        if not ansible_install_root:
            # NOTE: Even though we set this value the zuul installation
            # adjacent virtualenv location is still checked by the ansible
            # manager. ansible_install_root's value is only used if those
            # default locations do not have venvs preinstalled.
            ansible_install_root = os.path.join(state_dir, 'ansible-bin')
        self.ansible_manager = self._ansible_manager_class(
            ansible_dir, runtime_install_root=ansible_install_root)
        if not self.ansible_manager.validate():
            if not manage_ansible:
                raise Exception('Error while validating ansible '
                                'installations. Please run '
                                'zuul-manage-ansible to install all supported '
                                'ansible versions.')
            else:
                self.ansible_manager.install()
        self.ansible_manager.copyAnsibleFiles()

        self.process_merge_jobs = get_default(self.config, 'executor',
                                              'merge_jobs', True)
        self.component_info.process_merge_jobs = self.process_merge_jobs

        self.system = ZuulSystem(self.zk_client)
        self.nodepool = Nodepool(self.zk_client, self.system.system_id,
                                 self.statsd)

        self.result_events = PipelineResultEventQueue.createRegistry(
            self.zk_client)
        self.build_worker = threading.Thread(
            target=self.runBuildWorker,
            name="ExecutorServerBuildWorkerThread",
        )

        self.build_loop_wake_event = threading.Event()

        zone_filter = [self.zone]
        if self.allow_unzoned:
            # In case we are allowed to execute unzoned jobs, make sure, we are
            # subscribed to the default zone.
            zone_filter.append(None)

        self.executor_api = ExecutorApi(
            self.zk_client,
            zone_filter=zone_filter,
            build_request_callback=self.build_loop_wake_event.set,
            build_event_callback=self._handleBuildEvent,
        )

        # Used to offload expensive operations to different processes
        self.process_worker = None

    def _get_key_store_password(self):
        try:
            return self.config["keystore"]["password"]
        except KeyError:
            raise RuntimeError("No key store password configured!")

    def _repoLock(self, connection_name, project_name):
        return self.repo_locks.getRepoLock(connection_name, project_name)

    # We use a property to reflect the accepting_work state on the component
    # since it might change quite often.
    @property
    def accepting_work(self):
        return self.component_info.accepting_work

    @accepting_work.setter
    def accepting_work(self, work):
        self.component_info.accepting_work = work

    def start(self):
        # Start merger worker only if we process merge jobs
        if self.process_merge_jobs:
            super().start()

        self._running = True
        self._command_running = True

        try:
            multiprocessing.set_start_method('spawn')
        except RuntimeError:
            # Note: During tests this can be called multiple times which
            # results in a runtime error. This is ok here as we've set this
            # already correctly.
            self.log.warning('Multiprocessing context has already been set')
        self.process_worker = ProcessPoolExecutor()

        self.build_worker.start()

        self.log.debug("Starting command processor")
        self.command_socket.start()
        self.command_thread = threading.Thread(target=self.runCommand,
                                               name='command')
        self.command_thread.daemon = True
        self.command_thread.start()

        self.log.debug("Starting %s update workers" % self.update_workers)
        for i in range(self.update_workers):
            update_thread = threading.Thread(target=self._updateLoop,
                                             name='update')
            update_thread.daemon = True
            update_thread.start()
            self.update_threads.append(update_thread)

        self.governor_stop_event = threading.Event()
        self.governor_thread = threading.Thread(target=self.run_governor,
                                                name='governor')
        self.governor_thread.daemon = True
        self.governor_thread.start()
        self.disk_accountant.start()
        self.component_info.state = self.component_info.RUNNING

    def register_work(self):
        if self._running:
            self.accepting_work = True
            self.build_loop_wake_event.set()

    def unregister_work(self):
        self.accepting_work = False

    def stop(self):
        self.log.debug("Stopping")
        self.component_info.state = self.component_info.STOPPED
        self.connections.stop()
        self.disk_accountant.stop()
        # The governor can change function registration, so make sure
        # it has stopped.
        self.governor_stop_event.set()
        self.governor_thread.join()
        # Tell the executor worker to abort any jobs it just accepted,
        # and grab the list of currently running job workers.
        with self.run_lock:
            self._running = False
            self._command_running = False
            workers = list(self.job_workers.values())

        for job_worker in workers:
            try:
                job_worker.stop()
            except Exception:
                self.log.exception("Exception sending stop command "
                                   "to worker:")
        for job_worker in workers:
            try:
                job_worker.wait()
            except Exception:
                self.log.exception("Exception waiting for worker "
                                   "to stop:")

        # Now that we aren't accepting any new jobs, and all of the
        # running jobs have stopped, tell the update processor to
        # stop.
        for _ in self.update_threads:
            self.update_queue.put(None)

        self.command_socket.stop()

        # All job results should have been sent by now, shutdown the
        # build and merger workers.
        self.build_loop_wake_event.set()
        self.build_worker.join()

        if self.process_worker is not None:
            self.process_worker.shutdown()

        if self.statsd:
            base_key = 'zuul.executor.{hostname}'
            self.statsd.gauge(base_key + '.load_average', 0)
            self.statsd.gauge(base_key + '.pct_used_ram', 0)
            self.statsd.gauge(base_key + '.running_builds', 0)

        # Use the BaseMergeServer's stop method to disconnect from
        # ZooKeeper.  We do this as one of the last steps to ensure
        # that all ZK related components can be stopped first.
        super().stop()
        self.stop_repl()
        self.monitoring_server.stop()
        self.log.debug("Stopped")

    def join(self):
        self.governor_thread.join()
        for update_thread in self.update_threads:
            update_thread.join()
        if self.process_merge_jobs:
            super().join()
        self.build_loop_wake_event.set()
        self.build_worker.join()
        self.command_thread.join()
        self.monitoring_server.join()

    def pause(self):
        self.log.debug('Pausing')
        self.component_info.state = self.component_info.PAUSED
        self.pause_sensor.pause = True
        if self.process_merge_jobs:
            super().pause()

    def unpause(self):
        self.log.debug('Resuming')
        self.component_info.state = self.component_info.RUNNING
        self.pause_sensor.pause = False
        if self.process_merge_jobs:
            super().unpause()

    def graceful(self):
        # This pauses the executor end shuts it down when there is no running
        # build left anymore
        self.log.info('Stopping graceful')
        self.pause()
        while self.job_workers:
            self.log.debug('Waiting for %s jobs to end', len(self.job_workers))
            time.sleep(30)
        try:
            self.stop()
        except Exception:
            self.log.exception('Error while stopping')

    def verboseOn(self):
        self.verbose = True

    def verboseOff(self):
        self.verbose = False

    def keep(self):
        self.keep_jobdir = True

    def nokeep(self):
        self.keep_jobdir = False

    def start_repl(self):
        if self.repl:
            return
        self.repl = zuul.lib.repl.REPLServer(self)
        self.repl.start()

    def stop_repl(self):
        if not self.repl:
            # not running
            return
        self.repl.stop()
        self.repl = None

    def runCommand(self):
        while self._command_running:
            try:
                command = self.command_socket.get().decode('utf8')
                if command != '_stop':
                    self.command_map[command]()
            except Exception:
                self.log.exception("Exception while processing command")

    def _updateLoop(self):
        while True:
            try:
                self._innerUpdateLoop()
            except StopException:
                return
            except Exception:
                self.log.exception("Exception in update thread:")

    def resetProcessPool(self):
        """
        This is called in order to re-initialize a broken process pool if it
        got broken e.g. by an oom killed child process
        """
        if self.process_worker:
            try:
                self.process_worker.shutdown()
            except Exception:
                self.log.exception('Failed to shutdown broken process worker')
            self.process_worker = ProcessPoolExecutor()

    def _innerUpdateLoop(self):
        # Inside of a loop that keeps the main repositories up to date
        task = self.update_queue.get()
        if task is None:
            # We are asked to stop
            raise StopException()
        log = get_annotated_logger(
            self.log, task.zuul_event_id, build=task.build)
        try:
            lock = self.repo_locks.getRepoLock(
                task.connection_name, task.project_name)
            with lock:
                log.info("Updating repo %s/%s",
                         task.connection_name, task.project_name)
                self.merger.updateRepo(
                    task.connection_name, task.project_name,
                    repo_state=task.repo_state,
                    zuul_event_id=task.zuul_event_id, build=task.build,
                    process_worker=self.process_worker)
                source = self.connections.getSource(task.connection_name)
                project = source.getProject(task.project_name)
                task.canonical_name = project.canonical_name
                log.debug("Finished updating repo %s/%s",
                          task.connection_name, task.project_name)
                task.success = True
        except BrokenProcessPool:
            # The process pool got broken. Reset it to unbreak it for further
            # requests.
            log.exception('Process pool got broken')
            self.resetProcessPool()
            task.transient_error = True
        except Exception:
            log.exception('Got exception while updating repo %s/%s',
                          task.connection_name, task.project_name)
        finally:
            task.setComplete()

    def update(self, connection_name, project_name, repo_state=None,
               zuul_event_id=None, build=None):
        # Update a repository in the main merger

        task = UpdateTask(connection_name, project_name, repo_state=repo_state,
                          zuul_event_id=zuul_event_id, build=build)
        task = self.update_queue.put(task)
        return task

    def _update(self, connection_name, project_name, zuul_event_id=None):
        """
        The executor overrides _update so it can do the update asynchronously.
        """
        log = get_annotated_logger(self.log, zuul_event_id)
        task = self.update(connection_name, project_name,
                           zuul_event_id=zuul_event_id)
        task.wait()
        if not task.success:
            msg = "Update of '{}' failed".format(project_name)
            log.error(msg)
            raise Exception(msg)

    def executeJob(self, build_request, params):
        zuul_event_id = params['zuul_event_id']
        log = get_annotated_logger(self.log, zuul_event_id)
        log.debug(
            "Got %s job: %s",
            params["zuul"]["job"],
            build_request.uuid,
        )
        if self.statsd:
            base_key = 'zuul.executor.{hostname}'
            self.statsd.incr(base_key + '.builds')
        self.job_workers[build_request.uuid] = self._job_class(
            self, build_request, params
        )
        # Run manageLoad before starting the thread mostly for the
        # benefit of the unit tests to make the calculation of the
        # number of starting jobs more deterministic.
        self.manageLoad()
        self.job_workers[build_request.uuid].run()

    def _handleBuildEvent(self, build_request, build_event):
        log = get_annotated_logger(
            self.log, build_request.event_id, build=build_request.uuid)
        log.debug(
            "Received %s event for build %s", build_event.name, build_request)
        # Fulfill the resume/cancel requests after our internal calls
        # to aid the test suite in avoiding races.
        if build_event == JobRequestEvent.CANCELED:
            self.stopJob(build_request)
            self.executor_api.fulfillCancel(build_request)
        elif build_event == JobRequestEvent.RESUMED:
            self.resumeJob(build_request)
            self.executor_api.fulfillResume(build_request)
        elif build_event == JobRequestEvent.DELETED:
            self.stopJob(build_request)

    def runBuildWorker(self):
        while self._running:
            self.build_loop_wake_event.wait()
            self.build_loop_wake_event.clear()
            try:
                for build_request in self.executor_api.next():
                    # Check the sensors again as they might have changed in the
                    # meantime. E.g. the last build started within the next()
                    # generator could have fulfilled the StartingBuildSensor.
                    if not self.accepting_work:
                        break
                    if not self._running:
                        break
                    self._runBuildWorker(build_request)
            except Exception:
                self.log.exception("Error in build loop:")
                time.sleep(5)

    def _runBuildWorker(self, build_request: BuildRequest):
        log = get_annotated_logger(
            self.log, event=None, build=build_request.uuid
        )
        # Lock and update the build request
        if not self.executor_api.lock(build_request, blocking=False):
            return

        # Ensure that the request is still in state requested. This method is
        # called based on cached data and there might be a mismatch between the
        # cached state and the real state of the request. The lock might
        # have been successful because the request is already completed and
        # thus unlocked.
        if build_request.state != BuildRequest.REQUESTED:
            self._retry(build_request.lock, log, self.executor_api.unlock,
                        build_request)

        try:
            params = self.executor_api.getParams(build_request)
            # Directly update the build in ZooKeeper, so we don't loop
            # over and try to lock it again and again.  Do this before
            # clearing the params so if we fail, no one tries to
            # re-run the job.
            build_request.state = BuildRequest.RUNNING
            # Set the hostname on the build request so it can be used by
            # zuul-web for the live log streaming.
            build_request.worker_info = {
                "hostname": self.hostname,
                "log_port": self.log_streaming_port,
            }
            self.executor_api.update(build_request)
        except Exception:
            log.exception("Exception while preparing to start worker")
            # If we failed at this point, we have not written anything
            # to ZK yet; the only thing we need to do is to ensure
            # that we release the lock, and another executor will be
            # able to grab the build.
            self._retry(build_request.lock, log, self.executor_api.unlock,
                        build_request)
            return

        try:
            self.executor_api.clearParams(build_request)
            log.debug("Next executed job: %s", build_request)
            self.executeJob(build_request, params)
        except Exception:
            # Note, this is not a finally clause, because if we
            # sucessfuly start executing the job, it's the
            # AnsibleJob's responsibility to call completeBuild and
            # unlock the request.
            log.exception("Exception while starting worker")
            result = {
                "result": "ERROR",
                "exception": traceback.format_exc(),
            }
            self.completeBuild(build_request, result)

    def run_governor(self):
        while not self.governor_stop_event.wait(10):
            try:
                self.manageLoad()
            except Exception:
                self.log.exception("Exception in governor thread:")

    def manageLoad(self):
        ''' Apply some heuristics to decide whether or not we should
            be asking for more jobs '''
        with self.governor_lock:
            return self._manageLoad()

    def _manageLoad(self):

        if self.accepting_work:
            # Don't unregister if we don't have any active jobs.
            for sensor in self.sensors:
                ok, message = sensor.isOk()
                if not ok:
                    self.log.info(
                        "Unregistering due to {}".format(message))
                    self.unregister_work()
                    break
        else:
            reregister = True
            limits = []
            for sensor in self.sensors:
                ok, message = sensor.isOk()
                limits.append(message)
                if not ok:
                    reregister = False
                    break
            if reregister:
                self.log.info("Re-registering as job is within its limits "
                              "{}".format(", ".join(limits)))
                self.register_work()
        if self.statsd:
            base_key = 'zuul.executor.{hostname}'
            for sensor in self.sensors:
                sensor.reportStats(self.statsd, base_key)

    def finishJob(self, unique):
        del(self.job_workers[unique])
        self.log.debug(
            "Finishing Job: %s, queue(%d): %s",
            unique,
            len(self.job_workers),
            self.job_workers,
        )

    def stopJobDiskFull(self, jobdir):
        unique = os.path.basename(jobdir)
        self.stopJobByUnique(unique, reason=AnsibleJob.RESULT_DISK_FULL)

    def resumeJob(self, build_request):
        log = get_annotated_logger(
            self.log, build_request.event_id, build=build_request.uuid)
        log.debug("Resume job")
        self.resumeJobByUnique(
            build_request.uuid, build_request.event_id
        )

    def stopJob(self, build_request):
        log = get_annotated_logger(
            self.log, build_request.event_id, build=build_request.uuid)
        log.debug("Stop job")
        self.stopJobByUnique(build_request.uuid, build_request.event_id)

    def resumeJobByUnique(self, unique, zuul_event_id=None):
        log = get_annotated_logger(self.log, zuul_event_id)
        job_worker = self.job_workers.get(unique)
        if not job_worker:
            log.debug("Unable to find worker for job %s", unique)
            return
        try:
            job_worker.resume()
        except Exception:
            log.exception("Exception sending resume command to worker:")

    def stopJobByUnique(self, unique, reason=None, zuul_event_id=None):
        log = get_annotated_logger(self.log, zuul_event_id)
        job_worker = self.job_workers.get(unique)
        if not job_worker:
            log.debug("Unable to find worker for job %s", unique)
            return
        try:
            job_worker.stop(reason)
        except Exception:
            log.exception("Exception sending stop command to worker:")

    def _handleExpiredHoldRequest(self, request):
        '''
        Check if a hold request is expired and delete it if it is.

        The 'expiration' attribute will be set to the clock time when the
        hold request was used for the last time. If this is NOT set, then
        the request is still active.

        If a node expiration time is set on the request, and the request is
        expired, *and* we've waited for a defined period past the node
        expiration (EXPIRED_HOLD_REQUEST_TTL), then we will delete the hold
        request.

        :param: request Hold request
        :returns: True if it is expired, False otherwise.
        '''
        if not request.expired:
            return False

        if not request.node_expiration:
            # Request has been used up but there is no node expiration, so
            # we don't auto-delete it.
            return True

        elapsed = time.time() - request.expired
        if elapsed < self.EXPIRED_HOLD_REQUEST_TTL + request.node_expiration:
            # Haven't reached our defined expiration lifetime, so don't
            # auto-delete it yet.
            return True

        try:
            self.nodepool.zk_nodepool.lockHoldRequest(request)
            self.log.info("Removing expired hold request %s", request)
            self.nodepool.zk_nodepool.deleteHoldRequest(request)
        except Exception:
            self.log.exception(
                "Failed to delete expired hold request %s", request
            )
        finally:
            try:
                self.nodepool.zk_nodepool.unlockHoldRequest(request)
            except Exception:
                pass

        return True

    def _getAutoholdRequest(self, args):
        autohold_key_base = (
            args["zuul"]["tenant"],
            args["zuul"]["project"]["canonical_name"],
            args["zuul"]["job"],
        )

        class Scope(object):
            """Enum defining a precedence/priority of autohold requests.

            Autohold requests for specific refs should be fulfilled first,
            before those for changes, and generic jobs.

            Matching algorithm goes over all existing autohold requests, and
            returns one with the highest number (in case of duplicated
            requests the last one wins).
            """
            NONE = 0
            JOB = 1
            CHANGE = 2
            REF = 3

        # Do a partial match of the autohold key against all autohold
        # requests, ignoring the last element of the key (ref filter),
        # and finally do a regex match between ref filter from
        # the autohold request and the build's change ref to check
        # if it matches. Lastly, make sure that we match the most
        # specific autohold request by comparing "scopes"
        # of requests - the most specific is selected.
        autohold = None
        scope = Scope.NONE
        self.log.debug("Checking build autohold key %s", autohold_key_base)
        for request_id in self.nodepool.zk_nodepool.getHoldRequests():
            request = self.nodepool.zk_nodepool.getHoldRequest(request_id)
            if not request:
                continue

            if self._handleExpiredHoldRequest(request):
                continue

            ref_filter = request.ref_filter

            if request.current_count >= request.max_count:
                # This request has been used the max number of times
                continue
            elif not (
                request.tenant == autohold_key_base[0]
                and request.project == autohold_key_base[1]
                and request.job == autohold_key_base[2]
            ):
                continue
            elif not re.match(ref_filter, args["zuul"]["ref"]):
                continue

            if ref_filter == ".*":
                candidate_scope = Scope.JOB
            elif ref_filter.endswith(".*"):
                candidate_scope = Scope.CHANGE
            else:
                candidate_scope = Scope.REF

            self.log.debug(
                "Build autohold key %s matched scope %s",
                autohold_key_base,
                candidate_scope,
            )
            if candidate_scope > scope:
                scope = candidate_scope
                autohold = request

        return autohold

    def _processAutohold(self, ansible_job, duration, result):
        # We explicitly only want to hold nodes for jobs if they have
        # failed / retry_limit / post_failure and have an autohold request.
        hold_list = ["FAILURE", "RETRY_LIMIT", "POST_FAILURE", "TIMED_OUT"]
        if result not in hold_list:
            return False

        request = self._getAutoholdRequest(ansible_job.arguments)
        if request is not None:
            self.log.debug("Got autohold %s", request)
            self.nodepool.holdNodeSet(
                ansible_job.nodeset, request, ansible_job.build_request,
                duration, ansible_job.zuul_event_id)
            return True
        return False

    def startBuild(self, build_request, data):
        data["start_time"] = time.time()

        event = BuildStartedEvent(
            build_request.uuid, build_request.build_set_uuid,
            build_request.job_name, build_request.path, data,
            build_request.event_id)
        self.result_events[build_request.tenant_name][
            build_request.pipeline_name].put(event)

    def updateBuildStatus(self, build_request, data):
        event = BuildStatusEvent(
            build_request.uuid, build_request.build_set_uuid,
            build_request.job_name, build_request.path, data,
            build_request.event_id)
        self.result_events[build_request.tenant_name][
            build_request.pipeline_name].put(event)

    def pauseBuild(self, build_request, data):
        build_request.state = BuildRequest.PAUSED
        try:
            self.executor_api.update(build_request)
        except JobRequestNotFound as e:
            self.log.warning("Could not pause build: %s", str(e))
            return

        event = BuildPausedEvent(
            build_request.uuid, build_request.build_set_uuid,
            build_request.job_name, build_request.path, data,
            build_request.event_id)
        self.result_events[build_request.tenant_name][
            build_request.pipeline_name].put(event)

    def resumeBuild(self, build_request):
        build_request.state = BuildRequest.RUNNING
        try:
            self.executor_api.update(build_request)
        except JobRequestNotFound as e:
            self.log.warning("Could not resume build: %s", str(e))
            return

    def completeBuild(self, build_request, result):
        result["end_time"] = time.time()

        log = get_annotated_logger(self.log, build_request.event_id,
                                   build=build_request.uuid)

        # NOTE (felix): We store the end_time on the ansible job to calculate
        # the in-use duration of locked nodes when the nodeset is returned.
        # NOTE: this method may be called before we create a job worker.
        ansible_job = self.job_workers.get(build_request.uuid)
        if ansible_job:
            ansible_job.end_time = time.monotonic()
            duration = ansible_job.end_time - ansible_job.time_starting_build

            params = ansible_job.arguments
            # If the result is None, check if the build has reached
            # its max attempts and if so set the result to
            # RETRY_LIMIT.  This must be done in order to correctly
            # process the autohold in the next step. Since we only
            # want to hold the node if the build has reached a final
            # result.
            if result.get("result") is None:
                attempts = params["zuul"]["attempts"]
                max_attempts = params["max_attempts"]
                if attempts >= max_attempts:
                    result["result"] = "RETRY_LIMIT"

            # Provide the hold information back to the scheduler via the build
            # result.
            try:
                held = self._processAutohold(ansible_job, duration,
                                             result.get("result"))
                result["held"] = held
                log.info("Held status set to %s", held)
            except Exception:
                log.exception("Unable to process autohold for %s",
                              build_request)

        def update_build_request(log, build_request):
            try:
                self.executor_api.update(build_request)
                return True
            except JobRequestNotFound as e:
                log.warning("Could not find build: %s", str(e))
                return False

        def put_complete_event(log, build_request, event):
            try:
                self.result_events[build_request.tenant_name][
                    build_request.pipeline_name].put(event)
            except NoNodeError:
                log.warning("Pipeline was removed: %s",
                            build_request.pipeline_name)

        build_request.state = BuildRequest.COMPLETED
        found = self._retry(build_request.lock, log,
                            update_build_request, log, build_request)
        lock_valid = build_request.lock.is_still_valid()
        if lock_valid:
            # We only need to unlock if we're still locked.
            self._retry(build_request.lock, log, self.executor_api.unlock,
                        build_request)

        if not found:
            # If the build request is gone, don't return a result.
            return

        if not lock_valid:
            # If we lost the lock at any point before updating the
            # state to COMPLETED, then the scheduler may have (or
            # will) detect it as an incomplete build and generate an
            # error event for us.  We don't need to submit a
            # completion event in that case.
            #
            # TODO: If we make the scheduler robust against receiving
            # duplicate completion events for the same build, we could
            # choose continue here and submit the completion event in
            # the hopes that we would win the race against the cleanup
            # thread.  That might (in some narrow circumstances)
            # rescue an otherwise acceptable build from being
            # discarded.
            return

        # TODO: This is racy.  Once we have set the build request to
        # completed, the only way for it to be deleted is for the
        # scheduler to process a BuildRequestCompleted event.  So we
        # need to try really hard to give it one.  But if we exit
        # between the section above and the section below, we won't,
        # which will mean that the scheduler will not automatically
        # delete the build request and we will not be able to recover.
        #
        # This is essentially a two-phase commit problem, but we are
        # unable to use transactions because the result event is
        # sharded.  We should be able to redesign the result reporting
        # mechanism to eliminate the race and be more convergent.
        event = BuildCompletedEvent(
            build_request.uuid, build_request.build_set_uuid,
            build_request.job_name, build_request.path, result,
            build_request.event_id)
        self._retry(None, log, put_complete_event, log,
                    build_request, event)
