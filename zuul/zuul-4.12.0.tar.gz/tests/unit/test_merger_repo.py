# Copyright 2012 Hewlett-Packard Development Company, L.P.
# Copyright 2014 Wikimedia Foundation Inc.
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

import datetime
import logging
import os

import git
import testtools

from zuul.merger.merger import MergerTree, Repo
import zuul.model
from zuul.model import MergeRequest
from tests.base import (
    BaseTestCase, ZuulTestCase, FIXTURE_DIR, simple_layout, iterate_timeout
)


class TestMergerRepo(ZuulTestCase):

    log = logging.getLogger("zuul.test.merger.repo")
    tenant_config_file = 'config/single-tenant/main.yaml'
    workspace_root = None

    def setUp(self):
        super(TestMergerRepo, self).setUp()
        self.workspace_root = os.path.join(self.test_root, 'workspace')

    def test_create_head_path(self):
        parent_path = os.path.join(self.upstream_root, 'org/project1')
        parent_repo = git.Repo(parent_path)
        parent_repo.create_head("refs/heads/foobar")
        parent_repo.create_head("refs/heads/refs/heads/foobar")

        work_repo = Repo(parent_path, self.workspace_root,
                         'none@example.org', 'User Name', '0', '0')
        repo = work_repo.createRepoObject(None)
        self.assertIn('foobar', repo.branches)
        self.assertIn('refs/heads/foobar', repo.branches)
        self.assertNotIn('refs/heads/refs/heads/foobar', repo.branches)

    def test_create_head_at_char(self):
        """Test that we can create branches containing the '@' char.

        This is a regression test to make sure we are not using GitPython
        APIs that interpret the '@' as a special char.
        """
        parent_path = os.path.join(self.upstream_root, 'org/project1')
        parent_repo = git.Repo(parent_path)
        parent_repo.create_head("refs/heads/foo@bar")

        work_repo = Repo(parent_path, self.workspace_root,
                         'none@example.org', 'User Name', '0', '0')
        repo = work_repo.createRepoObject(None)
        self.assertIn('foo@bar', repo.branches)

    def test_ensure_cloned(self):
        parent_path = os.path.join(self.upstream_root, 'org/project1')

        # Forge a repo having a submodule
        parent_repo = git.Repo(parent_path)
        parent_repo.git.submodule('add', os.path.join(
            self.upstream_root, 'org/project2'), 'subdir')
        parent_repo.index.commit('Adding project2 as a submodule in subdir')
        # git 1.7.8 changed .git from being a directory to a file pointing
        # to the parent repository /.git/modules/*
        self.assertTrue(os.path.exists(
            os.path.join(parent_path, 'subdir', '.git')),
            msg='.git file in submodule should be a file')

        work_repo = Repo(parent_path, self.workspace_root,
                         'none@example.org', 'User Name', '0', '0')
        self.assertTrue(
            os.path.isdir(os.path.join(self.workspace_root, 'subdir')),
            msg='Cloned repository has a submodule placeholder directory')
        self.assertFalse(os.path.exists(
            os.path.join(self.workspace_root, 'subdir', '.git')),
            msg='Submodule is not initialized')

        sub_repo = Repo(
            os.path.join(self.upstream_root, 'org/project2'),
            os.path.join(self.workspace_root, 'subdir'),
            'none@example.org', 'User Name', '0', '0')
        self.assertTrue(os.path.exists(
            os.path.join(self.workspace_root, 'subdir', '.git')),
            msg='Cloned over the submodule placeholder')

        self.assertEqual(
            os.path.join(self.upstream_root, 'org/project1'),
            work_repo.createRepoObject(None).remotes[0].url,
            message="Parent clone still point to upstream project1")

        self.assertEqual(
            os.path.join(self.upstream_root, 'org/project2'),
            sub_repo.createRepoObject(None).remotes[0].url,
            message="Sub repository points to upstream project2")

    def test_repo_reset_branch_conflict(self):
        """Test correct reset with conflicting branch names"""
        parent_path = os.path.join(self.upstream_root, 'org/project1')

        parent_repo = git.Repo(parent_path)
        parent_repo.create_head("foobar")

        work_repo = Repo(parent_path, self.workspace_root,
                         'none@example.org', 'User Name', '0', '0')

        # Checkout branch that will be deleted from the remote repo
        work_repo.checkout("foobar")

        # Delete remote branch and create a branch that conflicts with
        # the branch checked out locally.
        parent_repo.delete_head("foobar")
        parent_repo.create_head("foobar/sub")

        work_repo.update()
        work_repo.reset()
        work_repo.checkout("foobar/sub")

        # Try the reverse conflict
        parent_path = os.path.join(self.upstream_root, 'org/project2')

        parent_repo = git.Repo(parent_path)
        parent_repo.create_head("foobar/sub")

        work_repo = Repo(parent_path, self.workspace_root,
                         'none@example.org', 'User Name', '0', '0')

        # Checkout branch that will be deleted from the remote repo
        work_repo.checkout("foobar/sub")

        # Delete remote branch and create a branch that conflicts with
        # the branch checked out locally.
        parent_repo.delete_head("foobar/sub")

        # Note: Before git 2.13 deleting a a ref foo/bar leaves an empty
        # directory foo behind that will block creating the reference foo
        # in the future. As a workaround we must clean up empty directories
        # in .git/refs.
        if parent_repo.git.version_info[:2] < (2, 13):
            Repo._cleanup_leaked_ref_dirs(parent_path, None, [])

        parent_repo.create_head("foobar")

        work_repo.update()
        work_repo.reset()
        work_repo.checkout("foobar")

    def test_set_refs(self):
        parent_path = os.path.join(self.upstream_root, 'org/project1')
        remote_sha = self.create_commit('org/project1')
        self.create_branch('org/project1', 'foobar')

        work_repo = Repo(parent_path, self.workspace_root,
                         'none@example.org', 'User Name', '0', '0')
        repo = git.Repo(self.workspace_root)
        new_sha = repo.heads.foobar.commit.hexsha

        work_repo.setRefs({'refs/heads/master': new_sha}, True)
        self.assertEqual(work_repo.getBranchHead('master').hexsha, new_sha)
        self.assertIn('master', repo.remotes.origin.refs)

        work_repo.setRefs({'refs/heads/master': remote_sha})
        self.assertEqual(work_repo.getBranchHead('master').hexsha, remote_sha)
        self.assertNotIn('master', repo.remotes.origin.refs)

    def test_set_remote_ref(self):
        parent_path = os.path.join(self.upstream_root, 'org/project1')
        commit_sha = self.create_commit('org/project1')
        self.create_commit('org/project1')

        work_repo = Repo(parent_path, self.workspace_root,
                         'none@example.org', 'User Name', '0', '0')
        work_repo.setRemoteRef('master', commit_sha)
        work_repo.setRemoteRef('invalid', commit_sha)

        repo = git.Repo(self.workspace_root)
        self.assertEqual(repo.remotes.origin.refs.master.commit.hexsha,
                         commit_sha)
        self.assertNotIn('invalid', repo.remotes.origin.refs)

    def test_clone_timeout(self):
        parent_path = os.path.join(self.upstream_root, 'org/project1')
        self.patch(git.Git, 'GIT_PYTHON_GIT_EXECUTABLE',
                   os.path.join(FIXTURE_DIR, 'fake_git.sh'))
        self.patch(Repo, 'retry_attempts', 1)
        work_repo = Repo(parent_path, self.workspace_root,
                         'none@example.org', 'User Name', '0', '0',
                         git_timeout=0.001)
        # TODO: have the merger and repo classes catch fewer
        # exceptions, including this one on initialization.  For the
        # test, we try cloning again.
        with testtools.ExpectedException(git.exc.GitCommandError,
                                         r'.*exit code\(-9\)'):
            work_repo._ensure_cloned(None)

    def test_fetch_timeout(self):
        parent_path = os.path.join(self.upstream_root, 'org/project1')
        self.patch(Repo, 'retry_attempts', 1)
        work_repo = Repo(parent_path, self.workspace_root,
                         'none@example.org', 'User Name', '0', '0')
        work_repo.git_timeout = 0.001
        self.patch(git.Git, 'GIT_PYTHON_GIT_EXECUTABLE',
                   os.path.join(FIXTURE_DIR, 'fake_git.sh'))
        with testtools.ExpectedException(git.exc.GitCommandError,
                                         r'.*exit code\(-9\)'):
            work_repo.update()

    def test_fetch_retry(self):
        parent_path = os.path.join(self.upstream_root, 'org/project1')
        self.patch(Repo, 'retry_interval', 1)
        work_repo = Repo(parent_path, self.workspace_root,
                         'none@example.org', 'User Name', '0', '0')
        self.patch(git.Git, 'GIT_PYTHON_GIT_EXECUTABLE',
                   os.path.join(FIXTURE_DIR, 'git_fetch_error.sh'))
        work_repo.update()
        # This is created on the first fetch
        self.assertTrue(os.path.exists(os.path.join(
            self.workspace_root, 'stamp1')))
        # This is created on the second fetch
        self.assertTrue(os.path.exists(os.path.join(
            self.workspace_root, 'stamp2')))

    def test_deleted_local_ref(self):
        parent_path = os.path.join(self.upstream_root, 'org/project1')
        self.create_branch('org/project1', 'foobar')

        work_repo = Repo(parent_path, self.workspace_root,
                         'none@example.org', 'User Name', '0', '0')

        # Delete local ref on the cached repo. This leaves us with a remote
        # ref but no local ref anymore.
        gitrepo = git.Repo(work_repo.local_path)
        gitrepo.delete_head('foobar', force=True)

        # Delete the branch upstream.
        self.delete_branch('org/project1', 'foobar')

        # And now reset the repo again. This should not crash
        work_repo.reset()

    def test_branch_rename(self):
        parent_path = os.path.join(self.upstream_root, 'org/project1')
        # Clone upstream so that current head is master
        work_repo = Repo(parent_path, self.workspace_root,
                         'none@example.org', 'User Name', '0', '0')

        # Rename master to main in upstream repo
        gitrepo = git.Repo(parent_path)
        main_branch = gitrepo.create_head('main')
        gitrepo.head.reference = main_branch
        gitrepo.delete_head(gitrepo.heads['master'], force=True)

        # And now reset the repo. This should not crash
        work_repo.reset()

    def test_broken_cache(self):
        parent_path = os.path.join(self.upstream_root, 'org/project1')
        work_repo = Repo(parent_path, self.workspace_root,
                         'none@example.org', 'User Name', '0', '0')
        self.waitUntilSettled()

        # Break the work repo
        path = work_repo.local_path
        os.remove(os.path.join(path, '.git/HEAD'))

        # And now reset the repo again. This should not crash
        work_repo.reset()

        # Now open a cache repo and break it in a way that git.Repo is happy
        # at first but git won't be because of a broken HEAD revision.
        merger = self.executor_server.merger
        cache_repo = merger.getRepo('gerrit', 'org/project')
        with open(os.path.join(cache_repo.local_path, '.git/HEAD'), 'w'):
            pass
        cache_repo.update()

        # Now open a cache repo and break it in a way that git.Repo is happy
        # at first but git won't be because of a corrupt object file.
        #
        # To construct this we create a commit so we have a guaranteed free
        # object file, then we break it by truncating it.
        fn = os.path.join(cache_repo.local_path, 'commit_filename')
        with open(fn, 'a') as f:
            f.write("test")
        repo = cache_repo.createRepoObject(None)
        repo.index.add([fn])
        repo.index.commit('test commit')

        # Pick the first object file we find and break it
        objects_path = os.path.join(cache_repo.local_path, '.git', 'objects')
        object_dir = os.path.join(
            objects_path,
            [d for d in os.listdir(objects_path) if len(d) == 2][0])
        object_to_break = os.path.join(object_dir, os.listdir(object_dir)[0])
        self.log.error(os.stat(object_to_break))
        os.chmod(object_to_break, 644)
        with open(object_to_break, 'w'):
            pass
        os.chmod(object_to_break, 444)
        cache_repo.update()

    def test_broken_gitmodules(self):
        parent_path = os.path.join(self.upstream_root, 'org/project1')
        work_repo = Repo(parent_path, self.workspace_root,
                         'none@example.org', 'User Name', '0', '0')
        self.waitUntilSettled()

        # Break the gitmodules with uncommited changes
        path = work_repo.local_path
        with open(os.path.join(path, '.gitmodules'), 'w') as f:
            f.write('[submodule "libfoo"]\n'
                    'path = include/foo\n'
                    '---\n'
                    'url = git://example.com/git/lib.git')

        # And now reset the repo. This should not crash
        work_repo.reset()

        # Break the gitmodules with a commit
        path = work_repo.local_path
        with open(os.path.join(path, '.gitmodules'), 'w') as f:
            f.write('[submodule "libfoo"]\n'
                    'path = include/foo\n'
                    '---\n'
                    'url = git://example.com/git/lib.git')
        git_repo = work_repo._createRepoObject(work_repo.local_path,
                                               work_repo.env)
        git_repo.git.add('.gitmodules')
        git_repo.index.commit("Broken gitmodule")
        # And now reset the repo. This should not crash
        work_repo.reset()

    def test_files_changes(self):
        parent_path = os.path.join(self.upstream_root, 'org/project1')
        self.create_branch('org/project1', 'feature')
        files = {'feature.txt': 'feature'}
        self.create_commit('org/project1', files=files, head='feature',
                           message='Add feature file')

        # Let the master diverge from the feature branch. This new file should
        # NOT be included in the changed files list.
        files = {'must-not-be-in-changelist.txt': 'FAIL'}
        self.create_commit('org/project1', files=files, head='master',
                           message='Add master file')

        work_repo = Repo(parent_path, self.workspace_root,
                         'none@example.org', 'User Name', '0', '0')
        changed_files = work_repo.getFilesChanges('feature', 'master')

        self.assertEqual(sorted(['README', 'feature.txt']),
                         sorted(changed_files))

    def test_files_changes_master_fork_merges(self):
        """Regression test for getFilesChanges()

        Check if correct list of changed files is listed for a messy
        branch that has a merge of a fork, with the fork including a
        merge of a new master revision.

        The previously used "git merge-base" approach did not handle this
        case correctly.
        """
        parent_path = os.path.join(self.upstream_root, 'org/project1')
        repo = git.Repo(parent_path)

        self.create_branch('org/project1', 'messy',
                           commit_filename='messy1.txt')

        # Let time pass to reproduce the order for this error case
        commit_date = datetime.datetime.now() + datetime.timedelta(seconds=5)
        commit_date = commit_date.replace(microsecond=0).isoformat()

        # Create a commit on 'master' so we can merge it into the fork
        files = {"master.txt": "master"}
        master_ref = self.create_commit('org/project1', files=files,
                                        message="Add master.txt",
                                        commit_date=commit_date)
        repo.refs.master.commit = master_ref

        # Create a fork of the 'messy' branch and merge
        # 'master' into the fork (no fast-forward)
        repo.create_head("messy-fork")
        repo.heads["messy-fork"].commit = "messy"
        repo.head.reference = 'messy'
        repo.head.reset(index=True, working_tree=True)
        repo.git.checkout('messy-fork')
        repo.git.merge('master', no_ff=True)

        # Merge fork back into 'messy' branch (no fast-forward)
        repo.head.reference = 'messy'
        repo.head.reset(index=True, working_tree=True)
        repo.git.checkout('messy')
        repo.git.merge('messy-fork', no_ff=True)

        # Create another commit on top of 'messy'
        files = {"messy2.txt": "messy2"}
        messy_ref = self.create_commit('org/project1', files=files,
                                       head='messy', message="Add messy2.txt")
        repo.refs.messy.commit = messy_ref

        # Check that we get all changes for the 'messy' but not 'master' branch
        work_repo = Repo(parent_path, self.workspace_root,
                         'none@example.org', 'User Name', '0', '0')
        changed_files = work_repo.getFilesChanges('messy', 'master')
        self.assertEqual(sorted(['messy1.txt', 'messy2.txt']),
                         sorted(changed_files))

    def test_update_needed(self):
        parent_path = os.path.join(self.upstream_root, 'org/project1')
        repo = git.Repo(parent_path)
        self.create_branch('org/project1', 'stable')

        proj_repo_state_no_update_master = {
            'refs/heads/master': repo.commit('refs/heads/master').hexsha,
        }
        proj_repo_state_no_update = {
            'refs/heads/master': repo.commit('refs/heads/master').hexsha,
            'refs/heads/stable': repo.commit('refs/heads/stable').hexsha,
        }
        repo_state_no_update = {
            'gerrit': {'org/project1': proj_repo_state_no_update}
        }

        proj_repo_state_update_ref = {
            'refs/heads/master': repo.commit('refs/heads/master').hexsha,
            'refs/heads/stable': repo.commit('refs/heads/stable').hexsha,
            # New branch based on master
            'refs/heads/test': repo.commit('refs/heads/master').hexsha,
        }
        repo_state_update_ref = {
            'gerrit': {'org/project1': proj_repo_state_update_ref}
        }

        proj_repo_state_update_rev = {
            'refs/heads/master': repo.commit('refs/heads/master').hexsha,
            # Commit changed on existing branch
            'refs/heads/stable': '1234567',
        }
        repo_state_update_rev = {
            'gerrit': {'org/project1': proj_repo_state_update_rev}
        }

        work_repo = Repo(parent_path, self.workspace_root,
                         'none@example.org', 'User Name', '0', '0')
        self.assertFalse(work_repo.isUpdateNeeded(
            proj_repo_state_no_update_master))
        self.assertFalse(work_repo.isUpdateNeeded(proj_repo_state_no_update))
        self.assertTrue(work_repo.isUpdateNeeded(proj_repo_state_update_ref))
        self.assertTrue(work_repo.isUpdateNeeded(proj_repo_state_update_rev))

        # Get repo and update for the first time.
        merger = self.executor_server.merger
        merger.updateRepo('gerrit', 'org/project1')
        repo = merger.getRepo('gerrit', 'org/project1')
        repo.reset()

        # Branches master and stable must exist
        self.assertEqual(['master', 'stable'], repo.getBranches())

        # Test new ref causes update
        # Now create an additional branch in the parent repo
        self.create_branch('org/project1', 'stable2')

        # Update with repo state and expect no update done
        self.log.info('Calling updateRepo with repo_state_no_update')
        merger.updateRepo('gerrit', 'org/project1',
                          repo_state=repo_state_no_update)
        repo = merger.getRepo('gerrit', 'org/project1')
        repo.reset()
        self.assertEqual(['master', 'stable'], repo.getBranches())

        # Update with repo state and expect update
        self.log.info('Calling updateRepo with repo_state_update_ref')
        merger.updateRepo('gerrit', 'org/project1',
                          repo_state=repo_state_update_ref)
        repo = merger.getRepo('gerrit', 'org/project1')
        repo.reset()
        self.assertEqual(['master', 'stable', 'stable2'], repo.getBranches())

        # Test new rev causes update
        # Now create an additional branch in the parent repo
        self.create_branch('org/project1', 'stable3')

        # Update with repo state and expect no update done
        self.log.info('Calling updateRepo with repo_state_no_update')
        merger.updateRepo('gerrit', 'org/project1',
                          repo_state=repo_state_no_update)
        repo = merger.getRepo('gerrit', 'org/project1')
        repo.reset()
        self.assertEqual(['master', 'stable', 'stable2'], repo.getBranches())

        # Update with repo state and expect update
        self.log.info('Calling updateRepo with repo_state_update_rev')
        merger.updateRepo('gerrit', 'org/project1',
                          repo_state=repo_state_update_rev)
        repo = merger.getRepo('gerrit', 'org/project1')
        repo.reset()
        self.assertEqual(['master', 'stable', 'stable2', 'stable3'],
                         repo.getBranches())

        # Make sure that we always update repos that aren't in the
        # repo_state.  Prime a second project.
        self.log.info('Calling updateRepo for project2')
        merger.updateRepo('gerrit', 'org/project2',
                          repo_state=repo_state_no_update)
        repo = merger.getRepo('gerrit', 'org/project2')
        repo.reset()
        self.assertEqual(['master'],
                         repo.getBranches())

        # Then update it, passing in a repo_state where project2 is
        # not present and ensure that we perform the update.
        self.log.info('Creating stable branch for project2')
        self.create_branch('org/project2', 'stable')
        merger.updateRepo('gerrit', 'org/project2',
                          repo_state=repo_state_no_update)
        repo = merger.getRepo('gerrit', 'org/project2')
        repo.reset()
        self.assertEqual(['master', 'stable'],
                         repo.getBranches())

    def test_garbage_collect(self):
        '''Tests that git gc doesn't prune FETCH_HEAD'''
        parent_path = os.path.join(self.upstream_root, 'org/project1')
        repo = git.Repo(parent_path)
        change_ref = 'refs/changes/01/1'

        self.log.info('Creating a commit on %s', change_ref)
        repo.head.reference = repo.head.commit
        files = {"README": "creating fake commit\n"}
        for name, content in files.items():
            file_name = os.path.join(parent_path, name)
            with open(file_name, 'a') as f:
                f.write(content)
            repo.index.add([file_name])
        commit = repo.index.commit('Test commit')
        ref = git.refs.Reference(repo, change_ref)
        ref.set_commit(commit)

        self.log.info('Cloning parent repo')
        work_repo = Repo(parent_path, self.workspace_root,
                         'none@example.org', 'User Name', '0', '0')

        self.log.info('Fetch %s', change_ref)
        work_repo.fetch(change_ref)

        self.log.info('Checkout master and run garbage collection')
        work_repo_object = work_repo.createRepoObject(None)
        work_repo.checkout('master')
        result = work_repo_object.git.gc('--prune=now')
        self.log.info(result)

        self.log.info('Dereferencing FETCH_HEAD')
        commit = work_repo_object.commit('FETCH_HEAD')
        self.assertIsNotNone(commit)

    def test_delete_upstream_tag(self):
        # Test that we can delete a tag from upstream and that our
        # working dir will prune it.
        parent_path = os.path.join(self.upstream_root, 'org/project1')
        parent_repo = git.Repo(parent_path)

        # Tag upstream
        self.addTagToRepo('org/project1', 'testtag', 'HEAD')
        commit = parent_repo.commit('testtag')

        # Update downstream and verify tag matches
        work_repo = Repo(parent_path, self.workspace_root,
                         'none@example.org', 'User Name', '0', '0')
        work_repo_underlying = git.Repo(work_repo.local_path)
        work_repo.update()
        result = work_repo_underlying.commit('testtag')
        self.assertEqual(commit, result)

        # Delete tag upstream
        self.delTagFromRepo('org/project1', 'testtag')

        # Update downstream and verify tag is gone
        work_repo.update()
        with testtools.ExpectedException(git.exc.BadName):
            result = work_repo_underlying.commit('testtag')

        # Make a new empty commit
        new_commit = parent_repo.index.commit('test commit')
        self.assertNotEqual(commit, new_commit)

        # Tag the new commit
        self.addTagToRepo('org/project1', 'testtag', new_commit)
        new_tag_commit = parent_repo.commit('testtag')
        self.assertEqual(new_commit, new_tag_commit)

        # Verify that the downstream tag matches
        work_repo.update()
        new_result = work_repo_underlying.commit('testtag')
        self.assertEqual(new_commit, new_result)

    def test_move_upstream_tag(self):
        # Test that if an upstream tag moves, our local copy moves
        # too.
        parent_path = os.path.join(self.upstream_root, 'org/project1')
        parent_repo = git.Repo(parent_path)

        # Tag upstream
        self.addTagToRepo('org/project1', 'testtag', 'HEAD')
        commit = parent_repo.commit('testtag')

        # Update downstream and verify tag matches
        work_repo = Repo(parent_path, self.workspace_root,
                         'none@example.org', 'User Name', '0', '0')
        work_repo_underlying = git.Repo(work_repo.local_path)
        work_repo.update()
        result = work_repo_underlying.commit('testtag')
        self.assertEqual(commit, result)

        # Make an empty commit
        new_commit = parent_repo.index.commit('test commit')
        self.assertNotEqual(commit, new_commit)

        # Re-tag upstream
        self.delTagFromRepo('org/project1', 'testtag')
        self.addTagToRepo('org/project1', 'testtag', new_commit)
        new_tag_commit = parent_repo.commit('testtag')
        self.assertEqual(new_commit, new_tag_commit)

        # Verify our downstream tag has moved
        work_repo.update()
        new_result = work_repo_underlying.commit('testtag')
        self.assertEqual(new_commit, new_result)


class TestMergerWithAuthUrl(ZuulTestCase):
    config_file = 'zuul-github-driver.conf'

    git_url_with_auth = True

    @simple_layout('layouts/merging-github.yaml', driver='github')
    def test_changing_url(self):
        """
        This test checks that if getGitUrl returns different urls for the same
        repo (which happens if an access token is part of the url) then the
        remote urls are changed in the merger accordingly. This tests directly
        the merger.
        """

        merger = self.executor_server.merger
        repo = merger.getRepo('github', 'org/project')
        first_url = repo.remote_url

        repo = merger.getRepo('github', 'org/project')
        second_url = repo.remote_url

        # the urls should differ
        self.assertNotEqual(first_url, second_url)

    @simple_layout('layouts/merging-github.yaml', driver='github')
    def test_changing_url_end_to_end(self):
        """
        This test checks that if getGitUrl returns different urls for the same
        repo (which happens if an access token is part of the url) then the
        remote urls are changed in the merger accordingly. This is an end to
        end test.
        """

        A = self.fake_github.openFakePullRequest('org/project', 'master',
                                                 'PR title')
        self.fake_github.emitEvent(A.getCommentAddedEvent('merge me'))
        self.waitUntilSettled()
        self.assertTrue(A.is_merged)

        # get remote url of org/project in merger
        repo = self.executor_server.merger.repos.get('github.com/org/project')
        self.assertIsNotNone(repo)
        git_repo = git.Repo(repo.local_path)
        first_url = list(git_repo.remotes[0].urls)[0]

        B = self.fake_github.openFakePullRequest('org/project', 'master',
                                                 'PR title')
        self.fake_github.emitEvent(B.getCommentAddedEvent('merge me again'))
        self.waitUntilSettled()
        self.assertTrue(B.is_merged)

        repo = self.executor_server.merger.repos.get('github.com/org/project')
        self.assertIsNotNone(repo)
        git_repo = git.Repo(repo.local_path)
        second_url = list(git_repo.remotes[0].urls)[0]

        # the urls should differ
        self.assertNotEqual(first_url, second_url)


class TestMerger(ZuulTestCase):

    tenant_config_file = 'config/single-tenant/main.yaml'

    @staticmethod
    def _item_from_fake_change(fake_change):
        return dict(
            number=fake_change.number,
            patchset=1,
            ref=fake_change.patchsets[0]['ref'],
            connection='gerrit',
            branch=fake_change.branch,
            project=fake_change.project,
            buildset_uuid='fake-uuid',
            merge_mode=zuul.model.MERGER_MERGE_RESOLVE,
        )

    def test_merge_multiple_items(self):
        """
        Tests that the merger merges and returns the requested file changes per
        change and in the correct order.
        """

        merger = self.executor_server.merger
        files = ['zuul.yaml', '.zuul.yaml']
        dirs = ['zuul.d', '.zuul.d']

        # Simple change A
        file_dict_a = {'zuul.d/a.yaml': 'a'}
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A',
                                           files=file_dict_a)
        item_a = self._item_from_fake_change(A)

        # Simple change B
        file_dict_b = {'zuul.d/b.yaml': 'b'}
        B = self.fake_gerrit.addFakeChange('org/project', 'master', 'B',
                                           files=file_dict_b)
        item_b = self._item_from_fake_change(B)

        # Simple change C on top of A
        file_dict_c = {'zuul.d/a.yaml': 'a-with-c'}
        C = self.fake_gerrit.addFakeChange('org/project', 'master', 'C',
                                           files=file_dict_c,
                                           parent=A.patchsets[0]['ref'])
        item_c = self._item_from_fake_change(C)

        # Change in different project
        file_dict_d = {'zuul.d/a.yaml': 'a-in-project1'}
        D = self.fake_gerrit.addFakeChange('org/project1', 'master', 'D',
                                           files=file_dict_d)
        item_d = self._item_from_fake_change(D)

        # Merge A
        result = merger.mergeChanges([item_a], files=files, dirs=dirs)
        self.assertIsNotNone(result)
        hexsha, read_files, repo_state, ret_recent, orig_commit = result
        self.assertEqual(len(read_files), 1)
        self.assertEqual(read_files[0]['project'], 'org/project')
        self.assertEqual(read_files[0]['branch'], 'master')
        self.assertEqual(read_files[0]['files']['zuul.d/a.yaml'], 'a')

        # Merge A -> B
        result = merger.mergeChanges([item_a, item_b], files=files, dirs=dirs)
        self.assertIsNotNone(result)
        hexsha, read_files, repo_state, ret_recent, orig_commit = result
        self.assertEqual(len(read_files), 2)
        self.assertEqual(read_files[0]['project'], 'org/project')
        self.assertEqual(read_files[0]['branch'], 'master')
        self.assertEqual(read_files[0]['files']['zuul.d/a.yaml'], 'a')
        self.assertEqual(read_files[1]['project'], 'org/project')
        self.assertEqual(read_files[1]['branch'], 'master')
        self.assertEqual(read_files[1]['files']['zuul.d/b.yaml'], 'b')

        # Merge A -> B -> C
        result = merger.mergeChanges([item_a, item_b, item_c], files=files,
                                     dirs=dirs)
        self.assertIsNotNone(result)
        hexsha, read_files, repo_state, ret_recent, orig_commit = result
        self.assertEqual(len(read_files), 3)
        self.assertEqual(read_files[0]['project'], 'org/project')
        self.assertEqual(read_files[0]['branch'], 'master')
        self.assertEqual(read_files[0]['files']['zuul.d/a.yaml'], 'a')
        self.assertEqual(read_files[1]['project'], 'org/project')
        self.assertEqual(read_files[1]['branch'], 'master')
        self.assertEqual(read_files[1]['files']['zuul.d/b.yaml'], 'b')
        self.assertEqual(read_files[2]['project'], 'org/project')
        self.assertEqual(read_files[2]['branch'], 'master')
        self.assertEqual(read_files[2]['files']['zuul.d/a.yaml'],
                         'a-with-c')

        # Merge A -> B -> C -> D
        result = merger.mergeChanges([item_a, item_b, item_c, item_d],
                                     files=files, dirs=dirs)
        self.assertIsNotNone(result)
        hexsha, read_files, repo_state, ret_recent, orig_commit = result

        self.assertEqual(len(read_files), 4)
        self.assertEqual(read_files[0]['project'], 'org/project')
        self.assertEqual(read_files[0]['branch'], 'master')
        self.assertEqual(read_files[0]['files']['zuul.d/a.yaml'], 'a')
        self.assertEqual(read_files[1]['project'], 'org/project')
        self.assertEqual(read_files[1]['branch'], 'master')
        self.assertEqual(read_files[1]['files']['zuul.d/b.yaml'], 'b')
        self.assertEqual(read_files[2]['project'], 'org/project')
        self.assertEqual(read_files[2]['branch'], 'master')
        self.assertEqual(read_files[2]['files']['zuul.d/a.yaml'],
                         'a-with-c')
        self.assertEqual(read_files[3]['project'], 'org/project1')
        self.assertEqual(read_files[3]['branch'], 'master')
        self.assertEqual(read_files[3]['files']['zuul.d/a.yaml'],
                         'a-in-project1')

    def test_merge_temp_refs(self):
        """
        Test that the merge updates local zuul refs in order to avoid
        garbage collection of needed objects.
        """
        merger = self.executor_server.merger

        parent_path = os.path.join(self.upstream_root, 'org/project')
        parent_repo = git.Repo(parent_path)
        parent_repo.create_head("foo/bar")

        # Simple change A
        A = self.fake_gerrit.addFakeChange('org/project', 'master', 'A')
        item_a = self._item_from_fake_change(A)

        # Simple change B on branch foo/bar
        B = self.fake_gerrit.addFakeChange('org/project', 'foo/bar', 'B')
        item_b = self._item_from_fake_change(B)

        # Simple change C
        C = self.fake_gerrit.addFakeChange('org/project', 'master', 'C')
        item_c = self._item_from_fake_change(C)

        # Merge A -> B -> C
        # TODO(corvus): remove this if we update in mergeChanges
        for item in [item_a, item_b, item_c]:
            merger.updateRepo(item['connection'], item['project'])
        result = merger.mergeChanges([item_a, item_b, item_c])
        self.assertIsNotNone(result)
        merge_state = result[3]

        cache_repo = merger.getRepo('gerrit', 'org/project')
        repo = cache_repo.createRepoObject(zuul_event_id="dummy")

        # Make sure zuul refs are updated
        foobar_zuul_ref = Repo.refNameToZuulRef("foo/bar")
        master_zuul_ref = Repo.refNameToZuulRef("master")
        ref_map = {r.path: r for r in repo.refs}
        self.assertIn(foobar_zuul_ref, ref_map)
        self.assertIn(master_zuul_ref, ref_map)

        self.assertEqual(
            ref_map[master_zuul_ref].commit.hexsha,
            merge_state[("gerrit", "org/project", "master")]
        )
        self.assertEqual(
            ref_map[foobar_zuul_ref].commit.hexsha,
            merge_state[("gerrit", "org/project", "foo/bar")]
        )

        # Delete the remote branch so a reset cleanes up the local branch
        parent_repo.delete_head('foo/bar', force=True)

        # Note: Before git 2.13 deleting a a ref foo/bar leaves an empty
        # directory foo behind that will block creating the reference foo
        # in the future. As a workaround we must clean up empty directories
        # in .git/refs.
        if parent_repo.git.version_info[:2] < (2, 13):
            Repo._cleanup_leaked_ref_dirs(parent_path, None, [])

        cache_repo.update()
        cache_repo.reset()
        self.assertNotIn(foobar_zuul_ref, [r.path for r in repo.refs])

        # Create another head 'foo' that can't be created if the 'foo/bar'
        # branch wasn't cleaned up properly
        parent_repo.create_head("foo")

        # Change B now on branch 'foo'
        B = self.fake_gerrit.addFakeChange('org/project', 'foo', 'B')
        item_b = self._item_from_fake_change(B)

        # Merge A -> B -> C
        # TODO(corvus): remove this if we update in mergeChanges
        for item in [item_a, item_b, item_c]:
            merger.updateRepo(item['connection'], item['project'])
        result = merger.mergeChanges([item_a, item_b, item_c])
        self.assertIsNotNone(result)
        merge_state = result[3]

        foo_zuul_ref = Repo.refNameToZuulRef("foo")
        ref_map = {r.path: r for r in repo.refs}

        self.assertIn(foo_zuul_ref, ref_map)
        self.assertIn(master_zuul_ref, ref_map)
        self.assertEqual(
            ref_map[master_zuul_ref].commit.hexsha,
            merge_state[("gerrit", "org/project", "master")]
        )
        self.assertEqual(
            ref_map[foo_zuul_ref].commit.hexsha,
            merge_state[("gerrit", "org/project", "foo")]
        )

    def test_stale_index_lock_cleanup(self):
        # Stop the running executor's merger. We needed it running to merge
        # things during test boostrapping but now it is just in the way.
        self.executor_server._merger_running = False
        self.executor_server.merger_loop_wake_event.set()
        self.executor_server.merger_thread.join()
        # Start a dedicated merger and do a merge to populate the repo on disk
        self._startMerger()

        A = self.fake_gerrit.addFakeChange('org/project1', 'master', 'A')
        A.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(A.addApproval('Approved', 1))
        self.waitUntilSettled()
        self.assertEqual(A.data['status'], 'MERGED')

        # Stop the merger so we can modify the git repo
        self.merge_server.stop()
        self.merge_server.join()

        # Add an index.lock file
        fpath = os.path.join(self.merger_src_root, 'review.example.com',
                             'org', 'org%2Fproject1', '.git', 'index.lock')
        with open(fpath, 'w'):
            pass
        self.assertTrue(os.path.exists(fpath))

        # Start a new merger and check that we can still merge things
        self._startMerger()

        # This will fail if git can't modify the repo due to a stale lock file.
        B = self.fake_gerrit.addFakeChange('org/project1', 'master', 'B')
        B.addApproval('Code-Review', 2)
        self.fake_gerrit.addEvent(B.addApproval('Approved', 1))
        self.waitUntilSettled()
        self.assertEqual(B.data['status'], 'MERGED')

        self.assertFalse(os.path.exists(fpath))

    def test_update_after_ff_merge(self):
        # Test update to branch from pre existing fast forwardable commit
        # causes the branch to update
        parent_path = os.path.join(self.upstream_root, 'org/project1')
        upstream_repo = git.Repo(parent_path)

        # Get repo and update for the first time.
        merger = self.executor_server.merger
        merger.updateRepo('gerrit', 'org/project1')
        repo = merger.getRepo('gerrit', 'org/project1')

        # Branch master must exist
        self.assertEqual(['master'], repo.getBranches())
        self.log.debug("Upstream master %s",
                       upstream_repo.commit('master').hexsha)

        # Create a new change in the upstream repo
        A = self.fake_gerrit.addFakeChange('org/project1', 'master', 'A')
        item_a = self._item_from_fake_change(A)
        change_sha = A.data['currentPatchSet']['revision']
        change_ref = 'refs/changes/01/1/1'

        # This will pull the upstream change into the zuul repo
        self.log.info('Merge the new change so it is present in the zuul repo')
        merger.mergeChanges([item_a], zuul_event_id='testeventid')
        repo = merger.getRepo('gerrit', 'org/project1')
        zuul_repo = git.Repo(repo.local_path)
        zuul_ref = repo.refNameToZuulRef('master')
        self.log.debug("Upstream commit %s",
                       upstream_repo.commit(change_ref).hexsha)
        self.log.debug("Zuul commit %s",
                       zuul_repo.commit(zuul_ref).hexsha)
        self.assertEqual(upstream_repo.commit(change_ref).hexsha,
                         zuul_repo.commit(zuul_ref).hexsha)
        self.assertNotEqual(upstream_repo.commit(change_ref).hexsha,
                            zuul_repo.commit('refs/heads/master').hexsha)

        # Update upstream master to point at the change commit simulating a
        # fast forward merge of a change
        upstream_repo.refs.master.commit = change_sha
        self.assertEqual(upstream_repo.commit('refs/heads/master').hexsha,
                         change_sha)
        # Construct a repo state to simulate it being created by
        # another merger.
        repo_state_update_branch_ff_rev = {
            'gerrit': {
                'org/project1': {
                    'refs/heads/master': change_sha,
                }
            }
        }
        self.log.debug("Upstream master %s",
                       upstream_repo.commit('master').hexsha)

        # This should update master
        self.log.info('Update the repo and ensure it has updated properly')
        merger.updateRepo('gerrit', 'org/project1',
                          repo_state=repo_state_update_branch_ff_rev)
        merger.checkoutBranch('gerrit', 'org/project1', 'master',
                              repo_state=repo_state_update_branch_ff_rev)
        repo = merger.getRepo('gerrit', 'org/project1')
        zuul_repo = git.Repo(repo.local_path)
        self.log.debug("Zuul master %s",
                       zuul_repo.commit('master').hexsha)

        # It's not important for the zuul ref to match; it's only used
        # to avoid garbage collection, so we don't check that here.
        self.assertEqual(upstream_repo.commit('refs/heads/master').hexsha,
                         zuul_repo.commit('refs/heads/master').hexsha)
        self.assertEqual(upstream_repo.commit(change_ref).hexsha,
                         zuul_repo.commit('refs/heads/master').hexsha)
        self.assertEqual(upstream_repo.commit(change_ref).hexsha,
                         zuul_repo.commit('HEAD').hexsha)

    def test_lost_merge_requests(self):
        # Test the cleanupLostMergeRequests method of the merger
        # client.  This is normally called from apsched from the
        # scheduler.  To exercise it, we need to produce a fake lost
        # merge request and then invoke it ourselves.

        # Stop the actual merger which will see this as garbage:
        self.executor_server._merger_running = False
        self.executor_server.merger_loop_wake_event.set()
        self.executor_server.merger_thread.join()

        merger_client = self.scheds.first.sched.merger
        merger_api = merger_client.merger_api

        # Create a fake lost merge request.  This is based on
        # test_lost_merge_requests in test_zk.

        payload = {'merge': 'test'}
        merger_api.submit(MergeRequest(
            uuid='B',
            job_type=MergeRequest.MERGE,
            build_set_uuid='BB',
            tenant_name='tenant',
            pipeline_name='check',
            event_id='1',
        ), payload)

        b = merger_api.get(f"{merger_api.REQUEST_ROOT}/B")

        b.state = MergeRequest.RUNNING
        merger_api.update(b)

        # Wait until the latest state transition is reflected in the Merger
        # APIs cache. Using a DataWatch for this purpose could lead to race
        # conditions depending on which DataWatch is executed first. The
        # DataWatch might be triggered for the correct event, but the cache
        # might still be outdated as the DataWatch that updates the cache
        # itself wasn't triggered yet.
        cache = merger_api._cached_requests
        for _ in iterate_timeout(30, "cache to be up-to-date"):
            if (cache and cache[b.path].state == MergeRequest.RUNNING):
                break

        # The lost_merges method should only return merges which are running
        # but not locked by any merger, in this case merge b
        lost_merge_requests = list(merger_api.lostRequests())

        self.assertEqual(1, len(lost_merge_requests))
        self.assertEqual(b.path, lost_merge_requests[0].path)

        # Exercise the cleanup code
        self.log.debug("Removing lost merge requests")
        merger_client.cleanupLostMergeRequests()

        cache = merger_api._cached_requests
        for _ in iterate_timeout(30, "cache to be empty"):
            if not cache:
                break


class TestMergerTree(BaseTestCase):

    def test_tree(self):
        t = MergerTree()

        t.add('/root/component')
        t.add('/root/component2')
        with testtools.ExpectedException(Exception):
            t.add('/root/component/subcomponent')
        t.add('/root/foo/bar/baz')
        with testtools.ExpectedException(Exception):
            t.add('/root/foo')


class TestMergerSchemes(ZuulTestCase):
    tenant_config_file = 'config/single-tenant/main.yaml'

    def setUp(self):
        super().setUp()
        self.work_root = os.path.join(self.test_root, 'workspace')
        self.cache_root = os.path.join(self.test_root, 'cache')

    def _getMerger(self, work_root=None, cache_root=None, scheme=None):
        work_root = work_root or self.work_root
        return self.executor_server._getMerger(
            work_root, cache_root=cache_root, scheme=scheme)

    def _assertScheme(self, root, scheme):
        if scheme == 'unique':
            self.assertTrue(os.path.exists(
                os.path.join(root, 'review.example.com',
                             'org/org%2Fproject1')))
        else:
            self.assertFalse(os.path.exists(
                os.path.join(root, 'review.example.com',
                             'org/org%2Fproject1')))

        if scheme == 'golang':
            self.assertTrue(os.path.exists(
                os.path.join(root, 'review.example.com',
                             'org/project1')))
        else:
            self.assertFalse(os.path.exists(
                os.path.join(root, 'review.example.com',
                             'org/project1')))

        if scheme == 'flat':
            self.assertTrue(os.path.exists(
                os.path.join(root, 'project1')))
        else:
            self.assertFalse(os.path.exists(
                os.path.join(root, 'project1')))

    def test_unique_scheme(self):
        merger = self._getMerger(scheme=zuul.model.SCHEME_UNIQUE)
        merger.getRepo('gerrit', 'org/project1')
        self._assertScheme(self.work_root, 'unique')

    def test_golang_scheme(self):
        cache_merger = self._getMerger(work_root=self.cache_root)
        cache_merger.updateRepo('gerrit', 'org/project1')
        self._assertScheme(self.cache_root, 'unique')

        merger = self._getMerger(
            cache_root=self.cache_root,
            scheme=zuul.model.SCHEME_GOLANG)
        merger.getRepo('gerrit', 'org/project1')
        self._assertScheme(self.work_root, 'golang')

    def test_flat_scheme(self):
        cache_merger = self._getMerger(work_root=self.cache_root)
        cache_merger.updateRepo('gerrit', 'org/project1')
        self._assertScheme(self.cache_root, 'unique')

        merger = self._getMerger(
            cache_root=self.cache_root,
            scheme=zuul.model.SCHEME_FLAT)
        merger.getRepo('gerrit', 'org/project1')
        self._assertScheme(self.work_root, 'flat')

    @simple_layout('layouts/overlapping-repos.yaml')
    def test_golang_collision(self):
        merger = self._getMerger(scheme=zuul.model.SCHEME_GOLANG)
        repo = merger.getRepo('gerrit', 'component')
        self.assertIsNotNone(repo)
        repo = merger.getRepo('gerrit', 'component/subcomponent')
        self.assertIsNone(repo)

    @simple_layout('layouts/overlapping-repos.yaml')
    def test_flat_collision(self):
        merger = self._getMerger(scheme=zuul.model.SCHEME_FLAT)
        repo = merger.getRepo('gerrit', 'component')
        self.assertIsNotNone(repo)
        repo = merger.getRepo('gerrit', 'component/component')
        self.assertIsNone(repo)


class TestOverlappingRepos(ZuulTestCase):

    @simple_layout('layouts/overlapping-repos.yaml')
    def test_overlapping_repos(self):
        self.executor_server.keep_jobdir = True
        A = self.fake_gerrit.addFakeChange('component', 'master', 'A')

        self.fake_gerrit.addEvent(A.getPatchsetCreatedEvent(1))
        self.waitUntilSettled()
        self.assertHistory([
            dict(name='test-job', result='SUCCESS', changes='1,1')],
            ordered=False)

        build = self.getJobFromHistory('test-job')
        jobdir_git_dir = os.path.join(build.jobdir.src_root,
                                      'component', '.git')
        self.assertTrue(os.path.exists(jobdir_git_dir))
        jobdir_git_dir = os.path.join(build.jobdir.src_root,
                                      'subcomponent', '.git')
        self.assertTrue(os.path.exists(jobdir_git_dir))


class TestMergerUpgrade(ZuulTestCase):
    tenant_config_file = 'config/single-tenant/main.yaml'

    def test_merger_upgrade(self):
        work_root = os.path.join(self.test_root, 'workspace')

        # Simulate existing repos
        org_project = os.path.join(work_root, 'review.example.com', 'org',
                                   'project', '.git')
        os.makedirs(org_project)
        scheme_file = os.path.join(work_root, '.zuul_merger_scheme')

        # Verify that an executor merger doesn't "upgrade" or write a
        # scheme file.
        self.executor_server._getMerger(
            work_root, cache_root=None, scheme=zuul.model.SCHEME_FLAT)
        self.assertTrue(os.path.exists(org_project))
        self.assertFalse(os.path.exists(scheme_file))

        # Verify that a "real" merger does upgrade.
        self.executor_server._getMerger(
            work_root, cache_root=None,
            execution_context=False)

        self.assertFalse(os.path.exists(org_project))
        self.assertTrue(os.path.exists(scheme_file))
        with open(scheme_file) as f:
            self.assertEqual(f.read().strip(), 'unique')

        # Verify that the next time it starts, we don't upgrade again.
        flag_dir = os.path.join(work_root, 'flag')
        os.makedirs(flag_dir)
        self.executor_server._getMerger(
            work_root, cache_root=None,
            execution_context=False)

        self.assertFalse(os.path.exists(org_project))
        self.assertTrue(os.path.exists(scheme_file))
        self.assertTrue(os.path.exists(flag_dir))
