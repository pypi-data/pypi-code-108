# Copyright 2012 Hewlett-Packard Development Company, L.P.
# Copyright 2013-2014 OpenStack Foundation
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

from contextlib import contextmanager
from logging import Logger
from typing import Optional
from urllib.parse import urlsplit, urlunsplit, urlparse
import hashlib
import logging
import os
import re
import shutil
import time

import git
import gitdb
import paramiko
from zuul.zk import ZooKeeperClient
from zuul.lib import strings

import zuul.model

from zuul.lib.logutil import get_annotated_logger

NULL_REF = '0000000000000000000000000000000000000000'


def redact_url(url):
    parsed = urlsplit(url)
    if parsed.password is None:
        return url

    # items[1] is the netloc containing credentials and hostname
    items = list(parsed)
    items[1] = re.sub('.*@', '******@', items[1])
    return urlunsplit(items)


@contextmanager
def timeout_handler(path):
    try:
        yield
    except git.exc.GitCommandError as e:
        if e.status == -9:
            # Timeout.  The repo could be in a bad state, so delete it.
            if os.path.exists(path):
                shutil.rmtree(path)
        raise


@contextmanager
def nullcontext():
    yield


class Repo(object):
    commit_re = re.compile(r'^commit ([0-9a-f]{40})$')
    diff_re = re.compile(r'^@@ -\d+,\d \+(\d+),\d @@$')
    retry_attempts = 3
    retry_interval = 30

    def __init__(self, remote, local, email, username, speed_limit, speed_time,
                 sshkey=None, cache_path=None, logger=None, git_timeout=300,
                 zuul_event_id=None):
        if logger is None:
            self.log = logging.getLogger("zuul.Repo")
        else:
            self.log = logger
        log = get_annotated_logger(self.log, zuul_event_id)
        self.env = {
            'GIT_HTTP_LOW_SPEED_LIMIT': speed_limit,
            'GIT_HTTP_LOW_SPEED_TIME': speed_time,
        }
        self.git_timeout = git_timeout
        self.sshkey = sshkey
        if sshkey:
            self.env['GIT_SSH_COMMAND'] = 'ssh -i %s' % (sshkey,)

        self.remote_url = remote
        self.local_path = local
        self.email = email
        self.username = username
        self.cache_path = cache_path
        self._initialized = False
        try:
            self._setup_known_hosts()
        except Exception:
            log.exception("Unable to set up known_hosts for %s", remote)
        try:
            self._ensure_cloned(zuul_event_id)
            self._git_set_remote_url(
                git.Repo(self.local_path), self.remote_url)
        except Exception:
            log.exception("Unable to initialize repo for %s", remote)

    def __repr__(self):
        return "<Repo {} {}>".format(hex(id(self)), self.local_path)

    def _setup_known_hosts(self):
        url = urlparse(self.remote_url)
        if 'ssh' not in url.scheme:
            return

        port = url.port or 22
        username = url.username or self.username

        path = os.path.expanduser('~/.ssh')
        os.makedirs(path, exist_ok=True)
        path = os.path.expanduser('~/.ssh/known_hosts')
        if not os.path.exists(path):
            with open(path, 'w'):
                pass

        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.load_host_keys(path)
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            client.connect(url.hostname,
                           username=username,
                           port=port,
                           key_filename=self.sshkey)
        finally:
            # If we don't close on exceptions to connect we can leak the
            # connection and DoS Gerrit.
            client.close()

    def _ensure_cloned(self, zuul_event_id, build=None):
        log = get_annotated_logger(self.log, zuul_event_id, build=build)
        repo_is_cloned = os.path.exists(os.path.join(self.local_path, '.git'))
        if self._initialized and repo_is_cloned:
            try:
                # validate that the repo isn't corrupt
                git.Repo(self.local_path)
                return
            except Exception:
                # the repo is corrupt, delete the local path
                shutil.rmtree(self.local_path)
                repo_is_cloned = False
                self._initialized = False

        # If the repo does not exist, clone the repo.
        rewrite_url = False
        if not repo_is_cloned:
            if self.cache_path:
                clone_url = self.cache_path
                rewrite_url = True
            else:
                clone_url = self.remote_url

            log.debug("Cloning from %s to %s",
                      redact_url(clone_url), self.local_path)
            self._git_clone(clone_url, zuul_event_id, build=build)

        repo = git.Repo(self.local_path)
        repo.git.update_environment(**self.env)
        # Create local branches corresponding to all the remote branches
        if not repo_is_cloned:
            origin = repo.remotes.origin
            for ref in origin.refs:
                if ref.remote_head == 'HEAD':
                    continue
                repo.create_head('refs/heads/' + ref.remote_head,
                                 ref.commit,
                                 force=True)
        with repo.config_writer() as config_writer:
            if self.email:
                config_writer.set_value('user', 'email', self.email)
            if self.username:
                config_writer.set_value('user', 'name', self.username)

            # By default automatic garbage collection in git runs
            # asynchronously in the background. This can lead to broken repos
            # caused by a race in the following scenario:
            #  1. git fetch (eventually triggers async gc)
            #  2. zuul deletes all refs as part of reset
            #  3. git gc looks for unreachable objects
            #  4. zuul re-creates all refs as part of reset
            #  5. git gc deletes unreachable objects it found
            # Result is a repo with refs pointing to not existing objects.
            # To prevent this race autoDetach can be disabled so git fetch
            # returns after the gc finished.
            config_writer.set_value('gc', 'autoDetach', 'false')

            # Lower the threshold of how many loose objects can trigger
            # automatic garbage collection. With the default value of 6700
            # we observed that with some repos automatic garbage collection
            # simply refused to do its job because it refuses to prune if the
            # number of unreachable objects it needs to prune exceeds a certain
            # threshold. Thus lower the threshold to trigger automatic garbage
            # collection more often.
            config_writer.set_value('gc', 'auto', '512')

            # By default garbage collection keeps unreachable objects for two
            # weeks. However we don't need to carry around any unreachable
            # objects so just prune them all when gc kicks in.
            config_writer.set_value('gc', 'pruneExpire', 'now')

            # By default git keeps a reflog of each branch for 90 days. Objects
            # that are reachable from a reflog entry are not considered
            # unrechable and thus won't be pruned for 90 days. This can blow up
            # the repo significantly over time. Since the reflog is only really
            # useful for humans working with repos we can just drop all the
            # reflog when gc kicks in.
            config_writer.set_value('gc', 'reflogExpire', 'now')

            config_writer.write()
        if rewrite_url:
            self._git_set_remote_url(repo, self.remote_url)
        self._initialized = True

    def isInitialized(self):
        return self._initialized

    def _git_clone(self, url, zuul_event_id, build=None):
        log = get_annotated_logger(self.log, zuul_event_id, build=build)
        mygit = git.cmd.Git(os.getcwd())
        mygit.update_environment(**self.env)

        for attempt in range(1, self.retry_attempts + 1):
            try:
                with timeout_handler(self.local_path):
                    mygit.clone(git.cmd.Git.polish_url(url), self.local_path,
                                kill_after_timeout=self.git_timeout)
                break
            except Exception:
                if attempt < self.retry_attempts:
                    time.sleep(self.retry_interval)
                    log.warning("Retry %s: Clone %s", attempt, self.local_path)
                else:
                    raise

    def _git_fetch(self, repo, remote, zuul_event_id, ref=None, **kwargs):
        log = get_annotated_logger(self.log, zuul_event_id)
        for attempt in range(1, self.retry_attempts + 1):
            try:
                with timeout_handler(self.local_path):
                    ref_to_fetch = ref
                    if ref_to_fetch:
                        ref_to_fetch += ':refs/zuul/fetch'
                    repo.git.fetch(remote, ref_to_fetch,
                                   kill_after_timeout=self.git_timeout, f=True,
                                   **kwargs)
                break
            except Exception as e:
                if attempt < self.retry_attempts:
                    if 'fatal: bad config' in e.stderr.lower():
                        # This error can be introduced by a merge conflict
                        # or someone committing faulty configuration
                        # in the .gitmodules which was left by the last
                        # merge operation. In this case reset and clean
                        # the repo and try again immediately.
                        reset_ref = 'HEAD'
                        try:
                            if not repo.is_dirty():
                                reset_ref = "{}^".format(repo.git.log(
                                    '--diff-filter=A',
                                    '-n', '1',
                                    '--pretty=format:%H',
                                    '--', '.gitmodules'))
                            repo.head.reset(reset_ref, working_tree=True)
                            repo.git.clean('-x', '-f', '-d')
                        except Exception:
                            # If we get here there probably isn't
                            # a valid commit we can easily find so
                            # delete the repo to make sure it doesn't
                            # get stuck in a broken state.
                            shutil.rmtree(self.local_path)
                    elif 'fatal: not a git repository' in e.stderr.lower():
                        # If we get here the git.Repo object was happy with its
                        # lightweight way of checking if this is a valid git
                        # repository. However if e.g. the .git/HEAD file is
                        # empty git operations fail. So there is something
                        # fundamentally broken with the repo and we need to
                        # delete it before advancing to _ensure_cloned.
                        shutil.rmtree(self.local_path)
                    elif 'error: object file' in e.stderr.lower():
                        # If we get here the git.Repo object was happy with its
                        # lightweight way of checking if this is a valid git
                        # repository. However if git complains about corrupt
                        # object files the repository is essentially broken and
                        # needs to be cloned cleanly.
                        shutil.rmtree(self.local_path)
                    else:
                        time.sleep(self.retry_interval)
                    log.exception("Retry %s: Fetch %s %s %s" % (
                        attempt, self.local_path, remote, ref))
                    self._ensure_cloned(zuul_event_id)
                else:
                    raise

    def _git_set_remote_url(self, repo, url):
        with repo.remotes.origin.config_writer as config_writer:
            config_writer.set('url', url)

    @staticmethod
    def _createRepoObject(path, env):
        repo = git.Repo(path)
        repo.git.update_environment(**env)
        return repo

    def createRepoObject(self, zuul_event_id, build=None):
        self._ensure_cloned(zuul_event_id, build=build)
        return self._createRepoObject(self.local_path, self.env)

    @staticmethod
    def _cleanup_leaked_ref_dirs(local_path, log, messages):
        for root, dirs, files in os.walk(
                os.path.join(local_path, '.git/refs'), topdown=False):
            if not os.listdir(root) and not root.endswith('.git/refs'):
                if log:
                    log.debug("Cleaning empty ref dir %s", root)
                else:
                    messages.append("Cleaning empty ref dir %s" % root)
                os.rmdir(root)

    @staticmethod
    def refNameToZuulRef(ref_name: str) -> str:
        return "refs/zuul/{}".format(
            hashlib.sha1(ref_name.encode("utf-8")).hexdigest()
        )

    @staticmethod
    def _reset(local_path, env, log=None):
        messages = []
        repo = Repo._createRepoObject(local_path, env)
        origin = repo.remotes.origin

        # Detach HEAD so we can work with references without interfering
        # with any active branch. Any remote ref will do as long as it can
        # be dereferenced to an existing commit.
        for ref in origin.refs:
            try:
                repo.head.reference = ref.commit
                break
            except Exception:
                if log:
                    log.debug("Unable to detach HEAD to %s", ref)
                else:
                    messages.append("Unable to detach HEAD to %s" % ref)
        else:
            raise Exception("Couldn't detach HEAD to any existing commit")

        # Delete local heads that no longer exist on the remote end
        zuul_refs_to_keep = [
            "refs/zuul/fetch",  # ref to last FETCH_HEAD
        ]
        remote_heads = {r.remote_head for r in origin.refs}
        for ref in repo.heads:
            if ref.name not in remote_heads:
                if log:
                    log.debug("Delete stale local ref %s", ref)
                else:
                    messages.append("Delete stale local ref %s" % ref)
                repo.delete_head(ref, force=True)
            else:
                zuul_refs_to_keep.append(Repo.refNameToZuulRef(ref.name))

        # Delete local zuul refs when the related branch no longer exists
        for ref in (r for r in repo.refs if r.path.startswith("refs/zuul/")):
            if ref.path in zuul_refs_to_keep:
                continue
            if log:
                log.debug("Delete stale Zuul ref %s", ref)
            else:
                messages.append("Delete stale Zuul ref {}".format(ref))
            Repo._deleteRef(ref.path, repo)

        # Note: Before git 2.13 deleting a a ref foo/bar leaves an empty
        # directory foo behind that will block creating the reference foo
        # in the future. As a workaround we must clean up empty directories
        # in .git/refs.
        if repo.git.version_info[:2] < (2, 13):
            Repo._cleanup_leaked_ref_dirs(local_path, log, messages)

        # Update our local heads to match the remote
        for ref in origin.refs:
            if ref.remote_head == 'HEAD':
                continue
            repo.create_head('refs/heads/' + ref.remote_head,
                             ref.commit,
                             force=True)
        return messages

    def reset(self, zuul_event_id=None, build=None, process_worker=None):
        log = get_annotated_logger(self.log, zuul_event_id, build=build)
        log.debug("Resetting repository %s", self.local_path)
        self.createRepoObject(zuul_event_id, build=build)

        if process_worker is None:
            self._reset(self.local_path, self.env, log)
        else:
            job = process_worker.submit(Repo._reset, self.local_path, self.env)
            messages = job.result()
            for message in messages:
                log.debug(message)

    def getBranchHead(self, branch, zuul_event_id=None):
        repo = self.createRepoObject(zuul_event_id)
        branch_head = repo.heads[branch]
        return branch_head.commit

    def setBranchHead(self, branch, head_ref, repo=None, zuul_event_id=None):
        if repo is None:
            repo = self.createRepoObject(zuul_event_id)
        repo.create_head(branch, head_ref, force=True)

    def hasBranch(self, branch, zuul_event_id=None):
        repo = self.createRepoObject(zuul_event_id)
        origin = repo.remotes.origin
        return branch in origin.refs

    def getBranches(self, zuul_event_id=None):
        # TODO(jeblair): deprecate with override-branch; replaced by
        # getRefs().
        repo = self.createRepoObject(zuul_event_id)
        return [x.name for x in repo.heads]

    def getCommitFromRef(self, refname, zuul_event_id=None):
        repo = self.createRepoObject(zuul_event_id)
        if refname not in repo.refs:
            return None
        ref = repo.refs[refname]
        return ref.commit

    def getRefs(self, zuul_event_id=None):
        repo = self.createRepoObject(zuul_event_id)
        return repo.refs

    def setRef(self, path, hexsha, repo=None, zuul_event_id=None):
        ref_log = get_annotated_logger(
            logging.getLogger("zuul.Repo.Ref"), zuul_event_id)
        ref_log.debug("Create reference %s at %s in %s",
                      path, hexsha, self.local_path)
        if repo is None:
            repo = self.createRepoObject(zuul_event_id)
        self._setRef(path, hexsha, repo)

    @staticmethod
    def _setRef(path, hexsha, repo):
        binsha = gitdb.util.to_bin_sha(hexsha)
        obj = git.objects.Object.new_from_sha(repo, binsha)
        git.refs.Reference.create(repo, path, obj, force=True)
        return 'Created reference %s at %s in %s' % (
            path, hexsha, repo.git_dir)

    def setRefs(self, refs, keep_remotes=False, zuul_event_id=None):
        repo = self.createRepoObject(zuul_event_id)
        ref_log = get_annotated_logger(
            logging.getLogger("zuul.Repo.Ref"), zuul_event_id)
        self._setRefs(repo, refs, keep_remotes=keep_remotes, log=ref_log)

    @staticmethod
    def setRefsAsync(local_path, refs, keep_remotes=False):
        repo = git.Repo(local_path)
        messages = Repo._setRefs(repo, refs, keep_remotes=keep_remotes)
        return messages

    @staticmethod
    def _setRefs(repo, refs, keep_remotes=False, log=None):
        messages = []
        current_refs = {}
        for ref in repo.refs:
            current_refs[ref.path] = ref
        unseen = set(current_refs.keys())
        for path, hexsha in refs.items():
            if log:
                log.debug("Create reference %s at %s in %s",
                          path, hexsha, repo.git_dir)
            message = Repo._setRef(path, hexsha, repo)
            messages.append(message)
            unseen.discard(path)
            ref = current_refs.get(path)
            if keep_remotes and ref:
                unseen.discard('refs/remotes/origin/{}'.format(ref.name))
        for path in unseen:
            if log:
                log.debug("Delete reference %s", path)
            message = Repo._deleteRef(path, repo)
            messages.append(message)
        return messages

    def setRemoteRef(self, branch, rev, zuul_event_id=None):
        log = get_annotated_logger(self.log, zuul_event_id)
        repo = self.createRepoObject(zuul_event_id)
        try:
            origin_ref = repo.remotes.origin.refs[branch]
        except IndexError:
            log.warning("No remote ref found for branch %s", branch)
            return
        log.debug("Updating remote reference %s to %s", origin_ref, rev)
        origin_ref.commit = rev

    def deleteRef(self, path, repo=None, zuul_event_id=None):
        ref_log = get_annotated_logger(
            logging.getLogger("zuul.Repo.Ref"), zuul_event_id)
        if repo is None:
            repo = self.createRepoObject(zuul_event_id)
        ref_log.debug("Delete reference %s", path)
        Repo._deleteRef(path, repo)

    @staticmethod
    def _deleteRef(path, repo):
        git.refs.SymbolicReference.delete(repo, path)
        return "Deleted reference %s" % path

    def checkout(self, ref, zuul_event_id=None):
        log = get_annotated_logger(self.log, zuul_event_id)
        repo = self.createRepoObject(zuul_event_id)
        # NOTE(pabelanger): We need to check for detached repo head, otherwise
        # gitpython will raise an exception if we access the reference.
        if not repo.head.is_detached and repo.head.reference == ref:
            log.debug("Repo is already at %s" % ref)
        else:
            log.debug("Checking out %s" % ref)
            # Perform a hard reset to the correct ref before checking out so
            # that we clean up anything that might be left over from a merge
            # while still only preparing the working copy once.
            repo.head.reference = ref
            repo.head.reset(working_tree=True)
            repo.git.clean('-x', '-f', '-d')
            repo.git.checkout(ref)

        return repo.head.commit

    def cherryPick(self, ref, zuul_event_id=None):
        log = get_annotated_logger(self.log, zuul_event_id)
        repo = self.createRepoObject(zuul_event_id)
        log.debug("Cherry-picking %s", ref)
        self.fetch(ref, zuul_event_id=zuul_event_id)
        repo.git.cherry_pick("FETCH_HEAD")
        return repo.head.commit

    def merge(self, ref, strategy=None, zuul_event_id=None):
        log = get_annotated_logger(self.log, zuul_event_id)
        repo = self.createRepoObject(zuul_event_id)
        args = []
        if strategy:
            args += ['-s', strategy]
        args.append('FETCH_HEAD')
        self.fetch(ref, zuul_event_id=zuul_event_id)
        log.debug("Merging %s with args %s", ref, args)
        repo.git.merge(*args)
        return repo.head.commit

    def squash_merge(self, item, zuul_event_id=None):
        log = get_annotated_logger(self.log, zuul_event_id)
        repo = self.createRepoObject(zuul_event_id)
        args = ['--squash', 'FETCH_HEAD']
        ref = item['ref']
        self.fetch(ref, zuul_event_id=zuul_event_id)
        log.debug("Squash-Merging %s with args %s", ref, args)
        repo.git.merge(*args)
        repo.index.commit(
            'Merge change %s,%s' % (item['number'], item['patchset']))
        return repo.head.commit

    def fetch(self, ref, zuul_event_id=None):
        repo = self.createRepoObject(zuul_event_id)
        # NOTE: The following is currently not applicable, but if we
        # switch back to fetch methods from GitPython, we need to
        # consider it:
        #   The git.remote.fetch method may read in git progress info and
        #   interpret it improperly causing an AssertionError. Because the
        #   data was fetched properly subsequent fetches don't seem to fail.
        #   So try again if an AssertionError is caught.
        self._git_fetch(repo, 'origin', zuul_event_id, ref=ref)

    def revParse(self, ref, zuul_event_id=None):
        repo = self.createRepoObject(zuul_event_id)
        return repo.git.rev_parse(ref)

    def fetchFrom(self, repository, ref, zuul_event_id=None):
        repo = self.createRepoObject(zuul_event_id)
        self._git_fetch(repo, repository, zuul_event_id, ref=ref)

    def push(self, local, remote, zuul_event_id=None):
        log = get_annotated_logger(self.log, zuul_event_id)
        repo = self.createRepoObject(zuul_event_id)
        log.debug("Pushing %s:%s to %s", local, remote, self.remote_url)
        repo.remotes.origin.push('%s:%s' % (local, remote))

    def update(self, zuul_event_id=None, build=None):
        log = get_annotated_logger(self.log, zuul_event_id, build=build)
        repo = self.createRepoObject(zuul_event_id, build=build)
        log.debug("Updating repository %s" % self.local_path)
        if repo.git.version_info[:2] < (1, 9):
            # Before 1.9, 'git fetch --tags' did not include the
            # behavior covered by 'git --fetch', so we run both
            # commands in that case.  Starting with 1.9, 'git fetch
            # --tags' is all that is necessary.  See
            # https://github.com/git/git/blob/master/Documentation/RelNotes/1.9.0.txt#L18-L20
            self._git_fetch(repo, 'origin', zuul_event_id)
        self._git_fetch(repo, 'origin', zuul_event_id, tags=True,
                        prune=True, prune_tags=True)

    def isUpdateNeeded(self, project_repo_state, zuul_event_id=None):
        repo = self.createRepoObject(zuul_event_id)
        refs = [x.path for x in repo.refs]
        for ref, rev in project_repo_state.items():
            # Check that each ref exists and that each commit exists
            if ref not in refs:
                return True
            try:
                repo.commit(rev)
            except Exception:
                # GitPython throws an error if a revision does not
                # exist
                return True
        return False

    def getFiles(self, files, dirs=[], branch=None, commit=None,
                 zuul_event_id=None):
        log = get_annotated_logger(self.log, zuul_event_id)
        ret = {}
        repo = self.createRepoObject(zuul_event_id)
        if branch:
            tree = repo.heads[branch].commit.tree
        else:
            tree = repo.commit(commit).tree
        for fn in files:
            if fn in tree:
                if tree[fn].type != 'blob':
                    log.warning(
                        "%s: object %s is not a blob", self.local_path, fn)
                ret[fn] = tree[fn].data_stream.read().decode('utf8')
            else:
                ret[fn] = None
        if dirs:
            for dn in dirs:
                if dn not in tree:
                    continue

                # Some people like to keep playbooks, etc. grouped
                # under their zuul config dirs; record the leading
                # directories of any .zuul.ignore files and prune them
                # from the config read.
                to_ignore = []
                for blob in tree[dn].traverse():
                    if blob.path.endswith(".zuul.ignore"):
                        to_ignore.append(os.path.split(blob.path)[0])

                def _ignored(blob):
                    for prefix in to_ignore:
                        if blob.path.startswith(prefix):
                            return True
                    return False

                for blob in tree[dn].traverse():
                    if not _ignored(blob) and blob.path.endswith(".yaml"):
                        ret[blob.path] = blob.data_stream.read().decode(
                            'utf-8')
        return ret

    def getFilesChanges(self, branch, tosha=None, zuul_event_id=None):
        repo = self.createRepoObject(zuul_event_id)
        self.fetch(branch, zuul_event_id=zuul_event_id)
        head = repo.commit(
            self.revParse('FETCH_HEAD', zuul_event_id=zuul_event_id))
        files = set()

        if tosha:
            commit_diff = "{}..{}".format(tosha, head.hexsha)
            for cmt in repo.iter_commits(commit_diff, no_merges=True):
                files.update(cmt.stats.files.keys())
        else:
            files.update(head.stats.files.keys())
        return list(files)

    def deleteRemote(self, remote, zuul_event_id=None):
        repo = self.createRepoObject(zuul_event_id)
        repo.delete_remote(repo.remotes[remote])

    def setRemoteUrl(self, url, zuul_event_id=None):
        if self.remote_url == url:
            return
        log = get_annotated_logger(self.log, zuul_event_id)
        log.debug("Set remote url to %s", redact_url(url))
        self.remote_url = url
        self._git_set_remote_url(
            self.createRepoObject(zuul_event_id),
            self.remote_url)

    def mapLine(self, commit, filename, lineno, zuul_event_id=None):
        repo = self.createRepoObject(zuul_event_id)
        # Trace the specified line back to the specified commit and
        # return the line number in that commit.
        cur_commit = None
        out = repo.git.log(L='%s,%s:%s' % (lineno, lineno, filename))
        for l in out.split('\n'):
            if cur_commit is None:
                m = self.commit_re.match(l)
                if m:
                    if m.group(1) == commit:
                        cur_commit = commit
                continue
            m = self.diff_re.match(l)
            if m:
                return int(m.group(1))
        return None

    def contains(self, hexsha, zuul_event_id=None):
        repo = self.createRepoObject(zuul_event_id)
        log = get_annotated_logger(self.log, zuul_event_id)
        try:
            branches = repo.git.branch(contains=hexsha, color='never')
        except git.GitCommandError as e:
            if e.status == 129:
                log.debug("Found commit %s in no branches", hexsha)
                return []
        branches = [x.replace('*', '').strip() for x in branches.split('\n')]
        branches = [x for x in branches if x != '(no branch)']
        log.debug("Found commit %s in branches: %s", hexsha, branches)
        return branches


class MergerTree:
    """
    A tree structure for quickly determining if a repo collides with
    another in the same merger workspace.

    Each node is a dictionary represents a path element.  The keys are
    child path elements and their values are either another dictionary
    for another node, or None if the child node is a git repo.
    """

    def __init__(self):
        self.root = {}

    def add(self, path):
        parts = path.split('/')
        root = self.root
        for i, part in enumerate(parts[:-1]):
            root = root.setdefault(part, {})
            if root is None:
                other = '/'.join(parts[:i])
                raise Exception(f"Repo {path} collides with {other}")
        last = parts[-1]
        if last in root:
            raise Exception(f"Repo {path} collides with "
                            "an existing repo with a longer path")
        root[last] = None


class Merger(object):

    def __init__(
        self,
        working_root: str,
        connections,
        zk_client: ZooKeeperClient,
        email: str,
        username: str,
        speed_limit: str,
        speed_time: str,
        cache_root: Optional[str] = None,
        logger: Optional[Logger] = None,
        execution_context: bool = False,
        git_timeout: int = 300,
        scheme: str = None,
        cache_scheme: str = None,
    ):
        self.logger = logger
        if logger is None:
            self.log = logging.getLogger("zuul.Merger")
        else:
            self.log = logger
        self.repos = {}
        self.working_root = working_root
        os.makedirs(working_root, exist_ok=True)
        self.connections = connections
        self.zk_client = zk_client
        self.email = email
        self.username = username
        self.speed_limit = speed_limit
        self.speed_time = speed_time
        self.git_timeout = git_timeout
        self.cache_root = cache_root
        self.scheme = scheme or zuul.model.SCHEME_UNIQUE
        self.cache_scheme = cache_scheme or zuul.model.SCHEME_UNIQUE
        # Flag to determine if the merger is used for preparing repositories
        # for job execution. This flag can be used to enable executor specific
        # behavior e.g. to keep the 'origin' remote intact.
        self.execution_context = execution_context
        # A tree of repos in our working root for detecting collisions
        self.repo_roots = MergerTree()
        # If we're not in an execution context, then check to see if
        # our working root needs a "schema" upgrade.
        if not execution_context:
            self._upgradeRootScheme()

    def _upgradeRootScheme(self):
        # If the scheme for the root directory has changed, delete all
        # the repos so they can be re-cloned.
        try:
            with open(os.path.join(self.working_root,
                                   '.zuul_merger_scheme')) as f:
                scheme = f.read().strip()
        except FileNotFoundError:
            # The previous default was golang
            scheme = zuul.model.SCHEME_GOLANG
        if scheme == self.scheme:
            return
        if os.listdir(self.working_root):
            self.log.info(f"Existing merger scheme {scheme} does not match "
                          f"requested scheme {self.scheme}, deleting merger "
                          "root (repositories will be re-cloned).")
            shutil.rmtree(self.working_root)
            os.makedirs(self.working_root)
        with open(os.path.join(self.working_root,
                               '.zuul_merger_scheme'), 'w') as f:
            f.write(self.scheme)

    def _addProject(self, hostname, connection_name, project_name, url, sshkey,
                    zuul_event_id, process_worker=None):
        repo = None
        key = '/'.join([hostname, project_name])
        try:
            path = os.path.join(self.working_root,
                                strings.workspace_project_path(
                                    hostname, project_name, self.scheme))
            self.repo_roots.add(path)
            if self.cache_root:
                cache_path = os.path.join(
                    self.cache_root,
                    strings.workspace_project_path(
                        hostname, project_name, self.cache_scheme))
            else:
                cache_path = None
            repo = Repo(
                url, path, self.email, self.username, self.speed_limit,
                self.speed_time, sshkey=sshkey, cache_path=cache_path,
                logger=self.logger, git_timeout=self.git_timeout,
                zuul_event_id=zuul_event_id)

            self.repos[key] = repo
        except Exception:
            log = get_annotated_logger(self.log, zuul_event_id)
            log.exception("Unable to add project %s/%s",
                          hostname, project_name)
        return repo

    def getRepo(self, connection_name, project_name,
                zuul_event_id=None, process_worker=None):
        source = self.connections.getSource(connection_name)
        project = source.getProject(project_name)
        hostname = project.canonical_hostname
        url = source.getGitUrl(project)
        key = '/'.join([hostname, project_name])
        if key in self.repos:
            repo = self.repos[key]
            repo.setRemoteUrl(url)
            return repo
        sshkey = self.connections.connections.get(connection_name).\
            connection_config.get('sshkey')
        if not url:
            raise Exception("Unable to set up repo for project %s/%s"
                            " without a url" %
                            (connection_name, project_name,))
        return self._addProject(hostname, connection_name, project_name, url,
                                sshkey, zuul_event_id,
                                process_worker=process_worker)

    def updateRepo(self, connection_name, project_name, repo_state=None,
                   zuul_event_id=None,
                   build=None, process_worker=None):
        """Fetch from origin if needed

        If repo_state is None, then this will always git fetch.
        If repo_state is provided, then this may no-op if
        the shas specified by repo_state are already present.
        """

        log = get_annotated_logger(self.log, zuul_event_id, build=build)
        repo = self.getRepo(connection_name, project_name,
                            zuul_event_id=zuul_event_id)
        if repo_state:
            projects = repo_state.get(connection_name, {})
            project_repo_state = projects.get(project_name, None)
        else:
            project_repo_state = None

        try:
            # Check if we need an update if we got a repo_state and
            # our project appears in it (otherwise we always update).
            if project_repo_state and not repo.isUpdateNeeded(
                    project_repo_state, zuul_event_id=zuul_event_id):
                log.info("Skipping updating local repository %s/%s",
                         connection_name, project_name)
            else:
                log.info("Updating local repository %s/%s",
                         connection_name, project_name)
                repo.update(zuul_event_id=zuul_event_id, build=build)
        except Exception:
            log.exception("Unable to update %s/%s",
                          connection_name, project_name)
            raise

    def checkoutBranch(self, connection_name, project_name, branch,
                       repo_state=None, zuul_event_id=None,
                       process_worker=None):
        """Check out a branch

        Call Merger.updateRepo() first.  This does not reset the repo,
        and is expected to be called only after a fresh clone.

        """
        log = get_annotated_logger(self.log, zuul_event_id)
        log.info("Checking out %s/%s branch %s",
                 connection_name, project_name, branch)
        repo = self.getRepo(connection_name, project_name,
                            process_worker=process_worker,
                            zuul_event_id=zuul_event_id)
        # We don't need to reset because this is only called by the
        # executor after a clone.
        if repo_state:
            self._restoreRepoState(connection_name, project_name, repo,
                                   repo_state, zuul_event_id,
                                   process_worker=process_worker)
        return repo.checkout(branch, zuul_event_id=zuul_event_id)

    def _saveRepoState(self, connection_name, project_name, repo,
                       repo_state, recent, branches):
        projects = repo_state.setdefault(connection_name, {})
        project = projects.setdefault(project_name, {})
        for ref in repo.getRefs():
            if ref.path.startswith('refs/zuul/'):
                continue
            if ref.path.startswith('refs/remotes/'):
                continue
            if ref.path.startswith('refs/heads/'):
                branch = ref.path[len('refs/heads/'):]
                if branches is not None and branch not in branches:
                    continue
                key = (connection_name, project_name, branch)
                if key not in recent:
                    recent[key] = ref.object
            project[ref.path] = ref.object.hexsha

    def _alterRepoState(self, connection_name, project_name,
                        repo_state, path, hexsha):
        projects = repo_state.setdefault(connection_name, {})
        project = projects.setdefault(project_name, {})
        if hexsha == NULL_REF:
            if path in project:
                del project[path]
        else:
            project[path] = hexsha

    def _restoreRepoState(self, connection_name, project_name, repo,
                          repo_state, zuul_event_id,
                          process_worker=None):
        log = get_annotated_logger(self.log, zuul_event_id)
        projects = repo_state.get(connection_name, {})
        project = projects.get(project_name, {})
        if not project:
            # We don't have a state for this project.
            return
        log.debug("Restore repo state for project %s/%s",
                  connection_name, project_name)
        if process_worker is None:
            repo.setRefs(project, keep_remotes=self.execution_context,
                         zuul_event_id=zuul_event_id)
        else:
            job = process_worker.submit(
                Repo.setRefsAsync, repo.local_path, project,
                keep_remotes=self.execution_context)
            messages = job.result()
            ref_log = get_annotated_logger(
                logging.getLogger("zuul.Repo.Ref"), zuul_event_id)
            for message in messages:
                ref_log.debug(message)

    def _mergeChange(self, item, ref, zuul_event_id):
        log = get_annotated_logger(self.log, zuul_event_id)
        repo = self.getRepo(item['connection'], item['project'],
                            zuul_event_id=zuul_event_id)
        try:
            repo.checkout(ref, zuul_event_id=zuul_event_id)
        except Exception:
            log.exception("Unable to checkout %s", ref)
            return None, None

        try:
            mode = item['merge_mode']
            if mode == zuul.model.MERGER_MERGE:
                commit = repo.merge(item['ref'], zuul_event_id=zuul_event_id)
            elif mode == zuul.model.MERGER_MERGE_RESOLVE:
                commit = repo.merge(item['ref'], 'resolve',
                                    zuul_event_id=zuul_event_id)
            elif mode == zuul.model.MERGER_CHERRY_PICK:
                commit = repo.cherryPick(item['ref'],
                                         zuul_event_id=zuul_event_id)
            elif mode == zuul.model.MERGER_SQUASH_MERGE:
                commit = repo.squash_merge(
                    item, zuul_event_id=zuul_event_id)
            else:
                raise Exception("Unsupported merge mode: %s" % mode)
        except git.GitCommandError:
            # Log git exceptions at debug level because they are
            # usually benign merge conflicts
            log.debug("Unable to merge %s", item, exc_info=True)
            return None, None
        except Exception:
            log.exception("Exception while merging a change:")
            return None, None

        orig_commit = repo.revParse('FETCH_HEAD')
        return orig_commit, commit

    def _mergeItem(self, item, recent, repo_state, zuul_event_id,
                   branches=None, process_worker=None):
        log = get_annotated_logger(self.log, zuul_event_id)
        log.debug("Processing ref %s for project %s/%s / %s uuid %s" %
                  (item['ref'], item['connection'],
                   item['project'], item['branch'],
                   item['buildset_uuid']))
        repo = self.getRepo(item['connection'], item['project'])
        key = (item['connection'], item['project'], item['branch'])

        # We need to merge the change
        # Get the most recent commit for this project-branch
        base = recent.get(key)
        if not base:
            # There is none, so use the branch tip
            # we need to reset here in order to call getBranchHead
            log.debug("No base commit found for %s" % (key,))
            try:
                repo.reset(zuul_event_id=zuul_event_id,
                           process_worker=process_worker)
            except Exception:
                log.exception("Unable to reset repo %s" % repo)
                return None, None
            self._restoreRepoState(item['connection'], item['project'], repo,
                                   repo_state, zuul_event_id,
                                   process_worker=process_worker)

            base = repo.getBranchHead(item['branch'])
            # Save the repo state so that later mergers can repeat
            # this process.
            self._saveRepoState(item['connection'], item['project'], repo,
                                repo_state, recent, branches)
        else:
            log.debug("Found base commit %s for %s" % (base, key,))

        if self.execution_context:
            # Set origin branch to the rev of the current (speculative) base.
            # This allows tools to determine the commits that are part of a
            # change by looking at origin/master..master.
            repo.setRemoteRef(item['branch'], base,
                              zuul_event_id=zuul_event_id)

        # Merge the change
        orig_commit, commit = self._mergeChange(item, base, zuul_event_id)
        if not commit:
            return None, None
        # Store this commit as the most recent for this project-branch
        recent[key] = commit

        # Make sure to have a local ref that points to the  most recent
        # (intermediate) speculative state of a branch, so commits are not
        # garbage collected. The branch name is hashed to not cause any
        # problems with empty directories in case of branch names containing
        # slashes. In order to prevent issues with Git garbage collection
        # between merger and executor jobs, we create refs in "refs/zuul"
        # instead of updating local branch heads.
        repo.setRef(Repo.refNameToZuulRef(item["branch"]),
                    commit.hexsha, zuul_event_id=zuul_event_id)

        return orig_commit, commit

    def mergeChanges(self, items, files=None, dirs=None, repo_state=None,
                     repo_locks=None, branches=None, zuul_event_id=None,
                     process_worker=None):
        """Merge changes

        Call Merger.updateRepo() first.
        """
        # _mergeItem calls reset as necessary.
        log = get_annotated_logger(self.log, zuul_event_id)
        # connection+project+branch -> commit
        recent = {}
        commit = None
        read_files = []
        # connection -> project -> ref -> commit
        if repo_state is None:
            repo_state = {}
        for item in items:
            # If we're in the executor context we have the repo_locks object
            # and perform per repo locking.
            if repo_locks is not None:
                lock = repo_locks.getRepoLock(
                    item['connection'], item['project'])
            else:
                lock = nullcontext()
            with lock:
                log.debug("Merging for change %s,%s" %
                          (item["number"], item["patchset"]))
                orig_commit, commit = self._mergeItem(
                    item, recent, repo_state, zuul_event_id, branches=branches,
                    process_worker=process_worker)
                if not commit:
                    return None
                if files or dirs:
                    repo = self.getRepo(item['connection'], item['project'])
                    repo_files = repo.getFiles(files, dirs, commit=commit)
                    read_files.append(dict(
                        connection=item['connection'],
                        project=item['project'],
                        branch=item['branch'],
                        files=repo_files))
        ret_recent = {}
        for k, v in recent.items():
            ret_recent[k] = v.hexsha
        return commit.hexsha, read_files, repo_state, ret_recent, orig_commit

    def setRepoState(self, connection_name, project_name, repo_state,
                     zuul_event_id=None, process_worker=None):
        """Set the repo state

        Call Merger.updateRepo() first.
        """
        repo = self.getRepo(connection_name, project_name,
                            zuul_event_id=zuul_event_id)

        # TODO: why is reset required here?
        repo.reset(zuul_event_id=zuul_event_id,
                   process_worker=process_worker)

        self._restoreRepoState(connection_name, project_name, repo,
                               repo_state, zuul_event_id)

    def getRepoState(self, items, repo_locks, branches=None):
        """Gets the repo state for items.

        This will perform repo updates as needed, so there is no need
        to call Merger.updateRepo() first.

        """
        # Generally this will be called in any non-change pipeline.  We
        # will return the repo state for each item, but manipulated with
        # any information in the item (eg, if it creates a ref, that
        # will be in the repo state regardless of the actual state).

        seen = set()
        recent = {}
        repo_state = {}
        for item in items:
            # If we're in the executor context we need to lock the repo.
            # If not repo_locks will give us a fake lock.
            lock = repo_locks.getRepoLock(item['connection'], item['project'])
            with lock:
                repo = self.getRepo(item['connection'], item['project'])
                key = (item['connection'], item['project'])
                if key not in seen:
                    try:
                        repo.update()
                        repo.reset()
                        seen.add(key)
                    except Exception:
                        self.log.exception("Unable to reset repo %s" % repo)
                        return (False, {}, [])

                    self._saveRepoState(item['connection'], item['project'],
                                        repo, repo_state, recent, branches)

                if item.get('newrev'):
                    # This is a ref update rather than a branch tip, so make
                    # sure our returned state includes this change.
                    self._alterRepoState(
                        item['connection'], item['project'], repo_state,
                        item['ref'], item['newrev'])
        item = items[-1]
        repo = self.getRepo(item['connection'], item['project'])
        # A list of branch names the last item appears in.
        item_in_branches = []
        if item.get('newrev'):
            item_in_branches = repo.contains(item['newrev'])
        return (True, repo_state, item_in_branches)

    def getFiles(self, connection_name, project_name, branch, files, dirs=[]):
        """Get file contents on branch.

        Call Merger.updateRepo() first to make sure the repo is up to
        date.

        """
        # We don't update the repo so that it can happen outside the
        # lock.
        repo = self.getRepo(connection_name, project_name)
        # TODO: why is reset required here?
        repo.reset()
        # This does not fetch, update, or reset, it operates on the
        # working state.
        return repo.getFiles(files, dirs, branch=branch)

    def getFilesChanges(self, connection_name, project_name, branch,
                        tosha=None, zuul_event_id=None):
        """Get a list of files changed in one or more commits

        Gets files changed between tosha and branch (or just the
        commit on branch if tosha is not specified).

        Call Merger.updateRepo() first to make sure the repo is up to
        date.
        """
        # Note, the arguments to this method should be reworked.  We
        # fetch branch, and therefore it is typically actually a
        # change ref.  tosha is typically the branch name.
        repo = self.getRepo(connection_name, project_name,
                            zuul_event_id=zuul_event_id)
        # This performs a fetch, and therefore update/reset are not
        # required.
        return repo.getFilesChanges(branch, tosha, zuul_event_id=zuul_event_id)
