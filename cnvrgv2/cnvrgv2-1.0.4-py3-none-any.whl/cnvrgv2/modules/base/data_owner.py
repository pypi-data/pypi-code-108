import os
import re
import abc
import time
import json
import shutil
from datetime import datetime
from itertools import chain

from cnvrgv2.modules.folder import Folder
from cnvrgv2.proxy import HTTP
from cnvrgv2.errors import CnvrgFileError, CnvrgArgumentsError
from cnvrgv2.cli.utils.progress_bar_utils import init_progress_bar_for_cli

from cnvrgv2.config.routes import COMMIT_REMOVE_FILES
from cnvrgv2.config import CONFIG_FOLDER_NAME
from cnvrgv2.config import Config
from cnvrgv2.config import error_messages

from cnvrgv2.data import FileCompare
from cnvrgv2.data import FileUploader
from cnvrgv2.data import FileDownloader
from cnvrgv2.data import RemoteFileDeleter
from cnvrgv2.data import ArtifactsDownloader

from cnvrgv2.utils.converters import convert_bytes
from cnvrgv2.utils.url_utils import urljoin
from cnvrgv2.utils.filter_utils import list_to_multiple_conditions, Operators
from cnvrgv2.utils.storage_utils import get_files_and_dirs_recursive, create_dir_if_not_exists, filter_by_mimetypes
from cnvrgv2.utils.api_list_generator import api_list_generator

from cnvrgv2.modules.file import File
from cnvrgv2.modules.base.dynamic_attributes import DynamicAttributes


class DataOwner(DynamicAttributes):
    TMP_FOLDER_NAME = ".tmp"

    def __init__(self):
        # Data attributes
        self._config = Config()
        self._working_dir = None
        self._storage_meta = None
        self._storage_meta_update_time = None
        self._local_commit = None
        self.query = None

    @property
    def storage_meta(self):
        """
        Retrieve the storage meta of the data owner
        @return: storage meta in a dict
        """
        # Calculate minutes diff from last update. If over 5 minutes - update storage meta.
        minutes_diff = 0
        if self._storage_meta_update_time is not None:
            minutes_diff = (datetime.now() - self._storage_meta_update_time).total_seconds() / 60
        if self._storage_meta is None or minutes_diff > 5:
            response = self._proxy.call_api(
                route=urljoin(self._route, "storage_client"),
                http_method=HTTP.GET
            )
            storage_meta = response.meta["storage"]
            self._storage_meta = storage_meta
            self._storage_meta_update_time = datetime.now()

        return self._storage_meta

    @abc.abstractmethod
    def _validate_config_ownership(self):
        """
        Returns if local config file is matched with current object
        """
        pass

    @property
    def local_commit(self):
        """
        Returns the current commit for the data owner
        @return: string denoting current/active commit
        """
        config_commit = None

        if self._validate_config_ownership():
            config_commit = self._config.commit_sha1

        return self._local_commit or config_commit

    @local_commit.setter
    def local_commit(self, commit_sha1):
        self._local_commit = commit_sha1

    @property
    def working_dir(self):
        """
        Returns the local working dir for the data owner
        @return: string denoting the path to the working dir
        """
        if self._working_dir:
            return self._working_dir
        else:
            return os.curdir

    @working_dir.setter
    def working_dir(self, working_dir):
        """
        Sets the working directory
        @param working_dir: string denoting the path to the working dir
        @return: None
        """
        self._working_dir = working_dir

    def _start_commit(self, message="", source="sdk", parent_sha1=None, blank=False, force=False, job_slug=None):
        """
        Starts a new commit
        @param message: Commit message string (Optional)
        @param source: Source of the commit string (Optional)
        @param parent_sha1: Commit sha1 of the parent of the new commit
        @param blank: Start from a blank state or from a previous commit
        @param force: Start from a blank state or from a previous commit
        @param job_slug: Job that this commit related to
        @return: Dict containing commit data
        """
        data = {
            "force": force,
            "blank": blank,
            "job_slug": job_slug,
            "parent_sha1": parent_sha1,
            "source": source,
            "message": message
        }
        response = self._proxy.call_api(
            route=urljoin(self._route, "commits"),
            http_method=HTTP.POST,
            payload=data
        )

        return response.attributes["sha1"]

    def _end_commit(self, commit_sha1, tag_images=False):
        """
        End the commit after uploading/deleting files from the dataset.
        @commit_sha1: the commit sha1 to end
        @param tag_images: Will cause images in this commit to be tagged so they can be
            displayed in specific places on front
        @return: None
        """
        self._proxy.call_api(
            route=urljoin(self._route, "commits", commit_sha1, "end_commit"),
            http_method=HTTP.PUT,
            payload={'tag_images': tag_images, 'workflow_slug': self.slug}
        )

    def reload(self):
        """
        Performs hard reload for the module attributes and config
        @return: None
        """
        super().reload()
        self._config = Config()
        self._local_commit = None
        # check ownership of local config, unless remove the config
        if not self._validate_config_ownership():
            self._config.local_config = {}

    def put_files(
        self,
        paths,
        pattern="*",
        message="",
        job_slug=None,
        blank=False,
        override=False,
        force=False,
        upload=False,
        tag_images=False,
        progress_bar_enabled=False,
        git_diff=False
    ):
        """
        Uploads the files and folders given.
        If a folder is given all the relevant files in that folder (that confirms to the regex) will be uploaded.
        @param paths: List of file/folder paths
        @param pattern: String defining the filename pattern
        @param message: String defining the commit message
        @param job_slug: Slug of a job to upload the files to
        @param blank: Start from a blank state or from a previous commit
        @param override: Boolean stating whether or not we should re-upload even if the file already exists
        @param force: Boolean stating whether or not we the new commit should copy files from parent
        @param upload: Boolean gives info if the put files comes from upload or not
        @param tag_images: Boolean indicating if we want to allow only images to be uploaded. used by exp.log_image
        @param progress_bar_enabled: Boolean indicating whenever or not to print a progress bar. In use of the cli
        @param git_diff: upload files from git diff output in addition to the given paths
        @return: string - The Commit sha1 that was created
        """
        fullpaths = []
        last_commit = None
        filters = []

        if tag_images:
            filters = ['image']

        paths_to_upload = paths

        if git_diff:
            git_diff_files = list(filter(None, self.get_git_diff()))  # Clean from falsy values
            paths_to_upload = paths_to_upload + git_diff_files

        for path in paths_to_upload:
            is_dir = os.path.isdir(path)
            is_file = os.path.isfile(path)

            if is_dir:
                fullpaths += get_files_and_dirs_recursive(root_dir=path, regex=pattern, not_tmp=True, filters=filters)
            elif is_file:
                if filter_by_mimetypes(filters, path):
                    fullpaths.append(path)
                else:
                    print("{} does not match any filter skipping it".format(path))
            else:
                # path sent might be a regex
                files_by_regex = get_files_and_dirs_recursive(
                    root_dir=".",
                    regex=path,
                    not_tmp=True,
                    filters=filters
                )
                if files_by_regex:
                    fullpaths += files_by_regex
                else:
                    # TODO: different handling?
                    print("{} does not exists skipping it".format(path))

        unique_fullpaths = list(set(fullpaths) - {"./", ".", "/", "//"})

        if not unique_fullpaths and not upload:
            # TODO: different handling?
            return

        if job_slug is not None:
            last_commit = self.last_commit or self.start_commit["sha1"]

        new_unique_fullpaths = []
        tmp_folder = "{}/{}".format(self.working_dir, DataOwner.TMP_FOLDER_NAME)
        for up in unique_fullpaths:
            deleted_file = "{}/{}.deleted".format(tmp_folder, up)

            if not os.path.isfile(deleted_file):
                new_unique_fullpaths.append(up)

        commit_sha1 = self._start_commit(
            message=message,
            blank=blank,
            parent_sha1=last_commit,
            job_slug=job_slug,
            force=force
        )

        uploader = FileUploader(
            self,
            new_unique_fullpaths,
            commit=commit_sha1,
            override=override,
            progress_bar_enabled=progress_bar_enabled
        )

        while uploader.in_progress:
            time.sleep(0.1)

        # TODO: Decide on error behaviour later
        if uploader.errors:
            raise uploader.errors[0]

        if upload:
            self.reload()
            deleter = RemoteFileDeleter(self, commit=commit_sha1)
            while deleter.in_progress:
                time.sleep(0.1)

        self._end_commit(commit_sha1=commit_sha1, tag_images=tag_images)

        return commit_sha1

    def remove_files(self, paths, message="", progress_bar_enabled=False):
        """
        Removes the given files remotely
        @param paths: List of file paths to remove (regex and wildcards allowed)
        @param message: Commit message
        @param progress_bar_enabled: Boolean indicating whenever or not to print a progress bar. In use of the cli
        @return: None
        """
        progress_bar = None
        commit_sha1 = self._start_commit(message=message)

        data = {
            "filter": json.dumps({
                "operator": 'OR',
                "conditions": list_to_multiple_conditions("fullpath", Operators.LIKE, paths),
            })
        }

        meta = self._remove_api_call(commit_sha1=commit_sha1, data=data)

        total_files_count = meta["total"]
        total_files_size = float(meta["total_size"])
        removed_files_count = meta["removed_files_count"]

        if progress_bar_enabled and total_files_size > 0:
            progress_bar = init_progress_bar_for_cli("Removing", total_files_size) if progress_bar_enabled else None

        while True:
            if progress_bar:
                converted_bytes, unit = convert_bytes(float(meta["removed_files_size"]), progress_bar.unit)
                progress_bar.throttled_next(converted_bytes)

            if removed_files_count >= total_files_count:
                break

            meta = self._remove_api_call(commit_sha1=commit_sha1, data=data)
            removed_files_count += meta["removed_files_count"]

        self._end_commit(commit_sha1=commit_sha1)

    def _remove_api_call(self, commit_sha1, data):
        """
        Performs API call to the server with the data to remove
        @param data: Hash containing the paths to remove
        @return: Hash with metadata regarding the remove action
        """
        route = urljoin(self._route, COMMIT_REMOVE_FILES.format(commit_sha1))
        return self._proxy.call_api(
            route=route,
            http_method=HTTP.POST,
            payload=data
        ).meta

    def clone(self, progress_bar_enabled=False, override=False):
        """
        Clones the remote project / dataset
        @param progress_bar_enabled: Boolean indicating whenever or not to print a progress bar. In use of the cli
        @param override: Boolean stating whether or not we should re-clone even if the project / dataset already cloned
        @return: None
        """

        self.reload()

        if not os.path.exists(self.slug):
            os.makedirs(self.slug)
        elif os.path.exists(self.slug + '/' + CONFIG_FOLDER_NAME) and not override:
            # If already cloned and override set to false - won't clone again
            return

        old_working_dir = self.working_dir
        self.working_dir = "{}/{}".format(old_working_dir, self.slug)

        downloader = FileDownloader(self, progress_bar_enabled=progress_bar_enabled)

        while downloader.in_progress:
            time.sleep(1)

        self.local_commit = self.last_commit
        self.save_config(local_config_path=self.working_dir + '/' + CONFIG_FOLDER_NAME)

        self.reload()
        self.working_dir = old_working_dir

    def upload(self, sync=False, job_slug=None, progress_bar_enabled=False, git_diff=False):
        """
        Uploads files to remote project / dataset
        @param sync: Boolean gives info if the put files comes from sync or not
        @param job_slug: Slug of a job to upload the files to
        @param progress_bar_enabled: Boolean indicating whenever or not to print a progress bar. In use of the cli
        @param git_diff: upload only files from git diff output
        @return: None
        """

        # We want to make sure we are in a project/dataset folder in order to continue with the action
        self.reload()
        if not self._validate_config_ownership():
            raise CnvrgFileError(error_messages.CONFIG_YAML_NOT_FOUND)

        new_commit_sha1 = self.put_files(
            ["."],
            upload=True,
            job_slug=job_slug,
            progress_bar_enabled=progress_bar_enabled,
            git_diff=git_diff
        )

        if sync:
            self.move_files_from_tmp()

        self.local_commit = new_commit_sha1
        self.save_config()

    def download(self, sync=False, progress_bar_enabled=False, commit_sha1=None):
        """
        Download files from remote project / dataset
        @param sync: Boolean gives info if the put files comes from sync or not
        @param progress_bar_enabled: Boolean indicating whenever or not to print a progress bar. In use of the cli
        @param commit_sha1: Sha1 of a specific commit to download
        @return: None
        """

        # We want to make sure we are in a project/dataset folder in order to continue with the action
        self.reload()
        if not self._validate_config_ownership():
            raise CnvrgFileError(error_messages.CONFIG_YAML_NOT_FOUND)

        """
        download files from last commit on the server and put them in .tmp folder
        will be fetched at the end out of .tmp
        """
        # create .tmp dir
        if not os.path.exists(DataOwner.TMP_FOLDER_NAME):
            os.makedirs(DataOwner.TMP_FOLDER_NAME)

        old_working_dir = self.working_dir
        self.working_dir = "{}/{}".format(self.working_dir, DataOwner.TMP_FOLDER_NAME)
        downloader = ArtifactsDownloader(
            self,
            base_commit_sha1=self.local_commit,
            commit_sha1=commit_sha1 or self.last_commit,
            progress_bar_enabled=progress_bar_enabled
        )
        while downloader.in_progress:
            time.sleep(1)

        self.working_dir = old_working_dir

        # TODO fix and uncomment
        """
        # remove all folders needed that should be deleted
        folder_deleter = LocalFileDeleter(self, mode="folders")
        while folder_deleter.in_progress:
            time.sleep(1)

        # put all files that need to be deleted at .tmp with .deleted extension
        file_deleter = LocalFileDeleter(self)
        while file_deleter.in_progress:
            time.sleep(1)
        """

        if not sync:
            self.move_files_from_tmp()
            self.local_commit = commit_sha1 or self.last_commit
            self.save_config()

    def sync(self, job_slug=None, git_diff=False):
        """
        Sync local project / dataset to remote
        @param job_slug: Slug of a job to upload the files to
        @param git_diff: upload only files from git diff output
        @return: None
        """
        try:
            self.download(sync=True)
            self.upload(sync=True, job_slug=job_slug, git_diff=git_diff)
        finally:
            # make sure the tmp folder used by download and upload will be deleted
            if os.path.exists(DataOwner.TMP_FOLDER_NAME):
                shutil.rmtree(DataOwner.TMP_FOLDER_NAME)

    def list_files(self, commit_sha1=None, query=None, query_raw=None, sort="-id"):
        """
        List all files in a specific query
        @param commit_sha1: Sha1 of the commit to list
        @param query: Query slug to list files from
        @param query_raw: Raw query to list files (e.g. {color: yellow})
        @param sort: key to sort the list by (-key -> DESC | key -> ASC)
        @raise: HttpError
        @return: Generator that yields file objects
        """
        return self._list("files", commit_sha1=commit_sha1, query=query, query_raw=query_raw, sort=sort)

    def list_folders(self, commit_sha1=None, query=None, query_raw=None, sort="-id"):
        """
        List all folders in a specific query
        @param commit_sha1: Sha1 of the commit to list
        @param query: Query slug to list folders from
        @param query_raw: Raw query to list folders (e.g. {color: yellow})
        @param sort: key to sort the list by (-key -> DESC | key -> ASC)
        @raise: HttpError
        @return: Generator that yields folder objects
        """
        return self._list("folders", commit_sha1=commit_sha1, query=query, query_raw=query_raw, sort=sort)

    def list(self, commit_sha1=None, query=None, query_raw=None, sort="-id"):
        """
        List all files and folders in a specific query
        @param commit_sha1: Sha1 of the commit to list
        @param query: Query slug to list files and folders from
        @param query_raw: Raw query to list files and folders (e.g. {color: yellow})
        @param sort: key to sort the list by (-key -> DESC | key -> ASC)
        @raise: HttpError
        @return: Generator that yields files and folders objects
        """
        list_folders = self.list_folders(commit_sha1=commit_sha1, query=query, query_raw=query_raw, sort=sort)
        list_files = self.list_files(commit_sha1=commit_sha1, query=query, query_raw=query_raw, sort=sort)
        return chain(list_folders, list_files)

    def move_files_from_tmp(self):
        """
        Takes files from .tmp folder and complete the sync/download/upload operation
        @return: None
        """
        tmp_folder = "{}/{}".format(self.working_dir, DataOwner.TMP_FOLDER_NAME)
        try:
            fullpaths = get_files_and_dirs_recursive(root_dir='.', not_tmp=True)
            unique_fullpaths = list(set(fullpaths) - {"./", ".", "/", "//"})

            if unique_fullpaths:
                compare = FileCompare(self, unique_fullpaths)
                while compare.in_progress:
                    time.sleep(1)

            downloaded_files = get_files_and_dirs_recursive(root_dir=tmp_folder, only_files=True)
            for df in downloaded_files:
                if df == ".tmp/" or df == ".tmp/.cnvrgignore":
                    continue

                if df.endswith('.deleted'):
                    original_file = re.sub(DataOwner.TMP_FOLDER_NAME, self.working_dir, df)
                    original_file = re.sub(".deleted", "", original_file)
                    if(os.path.isfile(original_file)):
                        os.remove(original_file)
                    continue

                new_path = re.sub(DataOwner.TMP_FOLDER_NAME, self.working_dir, df)
                create_dir_if_not_exists(new_path)
                os.rename(df, new_path)
        finally:
            if os.path.exists(tmp_folder):
                shutil.rmtree(tmp_folder)

    def get_git_diff(self):
        """
        collects file names from git diff output
        @return: list of file names from git diff command
        """
        command = "git diff --name-only"
        return os.popen(command).read().strip().split("\n")

    def _list(self, mode, commit_sha1=None, query=None, query_raw=None, sort="-id"):

        if query and query_raw:
            raise CnvrgArgumentsError(error_messages.QUERY_LIST_FAULTY_PARAMS.format("query and query_raw"))

        if query and commit_sha1:
            raise CnvrgArgumentsError(error_messages.QUERY_LIST_FAULTY_PARAMS.format("query and commit_sha1"))

        if not commit_sha1:
            self.reload()
            commit_sha1 = self.local_commit or self.last_commit

        list_object = Folder if mode == "folders" else File

        return api_list_generator(
            context=self._context,
            route=urljoin(self._route, "commits", commit_sha1, "files?mode={}".format(mode)),
            object=list_object,
            sort=sort,
            identifier="fullpath",
            pagination_type="offset",
            data={
                "query": query,
                "query_raw": query_raw
            }
        )
