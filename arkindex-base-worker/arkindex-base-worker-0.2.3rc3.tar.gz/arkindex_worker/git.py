#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import shutil
import time
from datetime import datetime
from pathlib import Path

import gitlab
import requests
import sh

from arkindex_worker import logger

NOTHING_TO_COMMIT_MSG = "nothing to commit, working tree clean"
MR_HAS_CONFLICTS_ERROR_CODE = 406


class GitlabHelper:
    """Helper class to save files to GitLab repository"""

    def __init__(
        self,
        project_id,
        gitlab_url,
        gitlab_token,
        branch,
        rebase_wait_period=1,
        delete_source_branch=True,
        max_rebase_tries=10,
    ):
        """
        :param project_id: the id of the gitlab project
        :param gitlab_url: gitlab server url
        :param gitlab_token: gitlab private token of user with permission to accept merge requests
        :param branch: name of the branch to where the exported branch will be merged
        :param rebase_wait_period: seconds to wait between each poll to check whether rebase has finished
        :param delete_source_branch: should delete the source branch after merging?
        :param max_rebase_tries: max number of tries to rebase when merging before giving up
        """
        self.project_id = project_id
        self.gitlab_url = gitlab_url
        self.gitlab_token = str(gitlab_token).strip()
        self.branch = branch
        self.rebase_wait_period = rebase_wait_period
        self.delete_source_branch = delete_source_branch
        self.max_rebase_tries = max_rebase_tries

        logger.info("Creating a Gitlab client")
        self._api = gitlab.Gitlab(self.gitlab_url, private_token=self.gitlab_token)
        self.project = self._api.projects.get(self.project_id)
        self.is_rebase_finished = False

    def merge(self, branch_name, title) -> bool:
        """
        Create a merge request and try to merge.
        Always rebase first to avoid conflicts from MRs made in parallel
        :param branch_name: source branch name
        :param title: title of the merge request
        :return: was the branch successfully merged?
        """
        mr = None
        # always rebase first, because other workers might have merged already
        for i in range(self.max_rebase_tries):
            logger.info(f"Trying to merge, try nr: {i}")
            try:
                if mr is None:
                    mr = self._create_merge_request(branch_name, title)

                mr.rebase()
                rebase_success = self._wait_for_rebase_to_finish(mr.iid)
                if not rebase_success:
                    logger.error("Rebase failed, won't be able to merge!")
                    return False

                mr.merge(should_remove_source_branch=self.delete_source_branch)
                logger.info("Merge successful")
                return True
            except gitlab.GitlabMRClosedError as e:
                if e.response_code == MR_HAS_CONFLICTS_ERROR_CODE:
                    logger.info("Merge failed, trying to rebase and merge again.")
                    continue
                else:
                    logger.error(f"Merge was not successful: {e}")
                    return False
            except gitlab.GitlabError as e:
                logger.error(f"Gitlab error: {e}")
                if 400 <= e.response_code < 500:
                    # 4XX errors shouldn't be fixed by retrying
                    raise e
            except requests.exceptions.ConnectionError as e:
                logger.error(f"Server connection error, will wait and retry: {e}")
                time.sleep(self.rebase_wait_period)

        return False

    def _create_merge_request(self, branch_name, title):
        logger.info(f"Creating a merge request for {branch_name}")
        # retry_transient_error will retry the request on 50X errors
        # https://github.com/python-gitlab/python-gitlab/blob/265dbbdd37af88395574564aeb3fd0350288a18c/gitlab/__init__.py#L539
        mr = self.project.mergerequests.create(
            {
                "source_branch": branch_name,
                "target_branch": self.branch,
                "title": title,
            },
        )
        return mr

    def _get_merge_request(self, merge_request_id, include_rebase_in_progress=True):
        return self.project.mergerequests.get(
            merge_request_id, include_rebase_in_progress=include_rebase_in_progress
        )

    def _wait_for_rebase_to_finish(self, merge_request_id) -> bool:
        """
        Poll the merge request until it has finished rebasing
        :param merge_request_id:
        :return: rebase finished successfully?
        """

        logger.info("Checking if rebase has finished..")
        self.is_rebase_finished = False
        while not self.is_rebase_finished:
            time.sleep(self.rebase_wait_period)
            mr = self._get_merge_request(merge_request_id)
            self.is_rebase_finished = not mr.rebase_in_progress
        if mr.merge_error is None:
            logger.info("Rebase has finished")
            return True

        logger.error(f"Rebase failed: {mr.merge_error}")
        return False


def make_backup(path):
    """
    Create a backup file in the same directory with timestamp as suffix ".bak_{timestamp}"
    :param path: file to be backed up
    """
    path = Path(path)
    if not path.exists():
        raise ValueError(f"No file to backup! File not found: {path}")
    # timestamp with milliseconds
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    backup_path = Path(str(path) + f".bak_{timestamp}")
    shutil.copy(path, backup_path)
    logger.info(f"Made a backup {backup_path}")


def prepare_git_key(
    private_key,
    known_hosts,
    private_key_path="~/.ssh/id_ed25519",
    known_hosts_path="~/.ssh/known_hosts",
):
    """
    Prepare the git keys (put them in to the correct place) so that git could be used.
    Fixes some whitespace problems that come from arkindex secrets store (Django admin).

    Also creates a backup of the previous keys if they exist, to avoid losing the
    original keys of the developers.

    :param private_key: git private key contents
    :param known_hosts: git known_hosts contents
    :param private_key_path: path where to put the private key
    :param known_hosts_path: path where to put the known_hosts
    """
    # secrets admin UI seems to strip the trailing whitespace
    # but git requires the key file to have a new line at the end
    # for some reason uses CRLF line endings, but git doesn't like that
    private_key = private_key.replace("\r", "") + "\n"
    known_hosts = known_hosts.replace("\r", "") + "\n"

    private_key_path = Path(private_key_path).expanduser()
    known_hosts_path = Path(known_hosts_path).expanduser()

    if private_key_path.exists():
        if private_key_path.read_text() != private_key:
            make_backup(private_key_path)

    if known_hosts_path.exists():
        if known_hosts_path.read_text() != known_hosts:
            make_backup(known_hosts_path)

    private_key_path.write_text(private_key)
    # private key must be private, otherwise git will fail
    # expecting octal for permissions
    private_key_path.chmod(0o600)
    known_hosts_path.write_text(known_hosts)

    logger.info(f"Private key size after: {private_key_path.stat().st_size}")
    logger.info(f"Known size after: {known_hosts_path.stat().st_size}")


class GitHelper:
    """
    A helper class for running git commands

    At the beginning of the workflow call `run_clone_in_background`.
    When all the files are ready to be added to git then call
    `save_files` to move the files in to the git repository
    and try to push them.

    Pseudo code example:
        in worker.configure() configure the git helper and start the cloning:
        ```
        gitlab = GitlabHelper(...)
        workflow_id = os.environ["ARKINDEX_PROCESS_ID"]
        prepare_git_key(...)
        self.git_helper = GitHelper(workflow_id=workflow_id, gitlab_helper=gitlab, ...)
        self.git_helper.run_clone_in_background()
        ```

        at the end of the workflow (at the end of worker.run()) push the files to git:
        ```
        self.git_helper.save_files(self.out_dir)
        ```
    """

    def __init__(
        self,
        repo_url,
        git_dir,
        export_path,
        workflow_id,
        gitlab_helper: GitlabHelper,
        git_clone_wait_period=1,
    ):
        """

        :param repo_url: the url of the git repository where the export will be pushed
        :param git_dir: the directory where to clone the git repository
        :param export_path: the path inside the git repository where to put the exported files
        :param workflow_id: the process id to see the workflow graph in the frontend
        :param gitlab_helper: helper for gitlab
        :param git_clone_wait_period: check if clone has finished every N seconds at the end of the workflow
        """
        logger.info("Creating git helper")
        self.repo_url = repo_url
        self.git_dir = Path(git_dir)
        self.export_path = self.git_dir / export_path
        self.workflow_id = workflow_id
        self.gitlab_helper = gitlab_helper
        self.git_clone_wait_period = git_clone_wait_period
        self.is_clone_finished = False
        self.cmd = None
        self.success = None
        self.exit_code = None

        self.git_dir.mkdir(parents=True, exist_ok=True)
        # run git commands outside of the repository (no need to change dir)
        self._git = sh.git.bake("-C", self.git_dir)

    def _clone_done(self, cmd, success, exit_code):
        """
        Method that is called when git clone has finished in the background
        """
        logger.info("Finishing cloning")
        self.cmd = cmd
        self.success = success
        self.exit_code = exit_code
        self.is_clone_finished = True
        if not success:
            logger.error(f"Clone failed: {cmd} : {success} : {exit_code}")
        logger.info("Cloning finished")

    def run_clone_in_background(self):
        """
        Clones the git repository in the background in to the self.git_dir directory.

        `self.is_clone_finished` can be used to know whether the cloning has finished
        or not.
        """
        logger.info(f"Starting clone {self.repo_url} in background")
        cmd = sh.git.clone(
            self.repo_url, self.git_dir, _bg=True, _done=self._clone_done
        )
        logger.info(f"Continuing clone {self.repo_url} in background")
        return cmd

    def _wait_for_clone_to_finish(self):
        logger.info("Checking if cloning has finished..")
        while not self.is_clone_finished:
            time.sleep(self.git_clone_wait_period)
        logger.info("Cloning has finished")

        if not self.success:
            logger.error("Clone was not a success")
            logger.error(f"Clone error exit code: {str(self.exit_code)}")
            raise ValueError("Clone was not a success")

    def save_files(self, export_out_dir: Path):
        """
        Move files in export_out_dir to the cloned git repository
        and try to merge the created files if possible.
        """
        self._wait_for_clone_to_finish()

        # move exported files to git directory
        file_count = self._move_files_to_git(export_out_dir)

        # use timestamp to avoid branch name conflicts with multiple chunks
        current_timestamp = datetime.isoformat(datetime.now())
        # ":" is not allowed in a branch name
        branch_timestamp = current_timestamp.replace(":", ".")
        # add files to a new branch
        branch_name = f"workflow_{self.workflow_id}_{branch_timestamp}"
        self._git.checkout("-b", branch_name)
        self._git.add("-A")
        try:
            self._git.commit(
                "-m",
                f"Exported files from workflow: {self.workflow_id} at {current_timestamp}",
            )
        except sh.ErrorReturnCode as e:
            if NOTHING_TO_COMMIT_MSG in str(e.stdout):
                logger.warning("Nothing to commit (no changes)")
                return
            else:
                logger.error(f"Commit failed:: {e}")
                raise e

        # count the number of lines in the output
        wc_cmd_out = str(
            sh.wc(self._git.show("--stat", "--name-status", "--oneline", "HEAD"), "-l")
        )
        # -1 because the of the git command header
        files_committed = int(wc_cmd_out.strip()) - 1
        logger.info(f"Committed {files_committed} files")
        if file_count != files_committed:
            logger.warning(
                f"Of {file_count} added files only {files_committed} were committed"
            )

        self._git.push("-u", "origin", "HEAD")

        if self.gitlab_helper:
            try:
                self.gitlab_helper.merge(branch_name, f"Merge {branch_name}")
            except Exception as e:
                logger.error(f"Merge failed: {e}")
                raise e
        else:
            logger.info(
                "No gitlab_helper defined, not trying to merge the pushed branch"
            )

    def _move_files_to_git(self, export_out_dir: Path) -> int:
        """
        Move all files in the export_out_dir to the git repository
        while keeping the same directory structure
        """
        file_count = 0
        file_names = [
            file_name for file_name in export_out_dir.rglob("*") if file_name.is_file()
        ]
        for file in file_names:
            rel_file_path = file.relative_to(export_out_dir)
            out_file = self.export_path / rel_file_path
            if not out_file.exists():
                out_file.parent.mkdir(parents=True, exist_ok=True)
            # rename does not work if the source and destination are not on the same mounts
            # it will give an error: "OSError: [Errno 18] Invalid cross-device link:"
            shutil.copy(file, out_file)
            file.unlink()
            file_count += 1
        logger.info(f"Moved {file_count} files")
        return file_count
