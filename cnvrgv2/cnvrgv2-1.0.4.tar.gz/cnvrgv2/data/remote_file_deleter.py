import os
import json
import time

from queue import Empty

from cnvrgv2.proxy import HTTP
from cnvrgv2.utils.url_utils import urljoin
from cnvrgv2.data.remote_files_handler import RemoteFilesHandler


class RemoteFileDeleter(RemoteFilesHandler):
    def __init__(self, data_owner, commit, queue_size=5000, chunk_size=1000, force=False, files=None):
        """
        Multithreaded remote file deleter - deleting files from server if they deleted locally
        @param data_owner: Cnvrg dataset / project object
        @param chunk_size: File meta chunk size to fetch from the server
        @param force: Force rewrite existing files
        @param queue_size: Max number of file meta to put in queue
        """
        self.files = files
        self.mode = "files"
        self.commit = commit
        self.files_to_delete = []
        self.folders_to_delete = []

        total_files = data_owner._proxy.call_api(
            route="{}?{}".format(
                urljoin(data_owner._route, "commits", data_owner.local_commit, "files"),
                "page[after]={}&page[size]={}&sort=id&mode={}".format('', 0, "files")
            ),
            http_method=HTTP.GET
        ).meta["total"]

        total_folders = data_owner._proxy.call_api(
            route="{}?{}".format(
                urljoin(data_owner._route, "commits", data_owner.local_commit, "files"),
                "page[after]={}&page[size]={}&sort=id&mode={}".format('', 0, "folders")
            ),
            http_method=HTTP.GET
        ).meta["total"]

        super().__init__(
            data_owner,
            num_workers=1,
            queue_size=queue_size,
            chunk_size=chunk_size,
            force=force
        )

        self.total_files = total_files + total_folders

    def _collector_function(self, page_after=None, folders=None):
        """
        Function to collect exists files metadata from server to check if they deleted locally
        @param page_after: The id of the next file that the iteration of the pagination should start from
        @return: Should return array of files metadata
        """
        # Reset the cursor
        page_after = 0 if page_after == -100 else page_after

        if self.files:
            files_index = page_after - 1
            return {
                "file_dict": self.files[files_index:(files_index + self.chunk_size + 1)],
                "total_files": len(self.files),
                "next": page_after + self.chunk_size
            }
        else:
            data = {
                "filter": json.dumps({
                    "operator": 'OR',
                    "conditions": [
                        {
                            "key": 'fullpath',
                            "operator": 'like',
                            "value": "*",
                        }
                    ],
                })
            }

            response = self.data_owner._proxy.call_api(
                route="{}?{}".format(
                    urljoin(self.data_owner._route, "commits", self.data_owner.local_commit, "files"),
                    "page[after]={}&page[size]={}&sort=id&mode={}".format(page_after, self.chunk_size, self.mode)
                ),
                http_method=HTTP.GET,
                payload=data
            )

            # Once we are out of files we want to move to deleting folders
            if response.meta["next"] == '' and self.mode == "files":
                self.mode = "folders"
                return {
                    "file_dict": [],
                    "total_files": 0,
                    "next": -100  # placeholder in order to nullify the cursor
                }

            file_dict = []
            for file in response.items:
                file_attr = dict(file.attributes)
                fullpath = file_attr["fullpath"]
                file_attr["type"] = self.mode
                local_path = "{}/{}".format(self.data_owner.working_dir, fullpath)
                if os.path.isfile(local_path) and self.mode == "files":
                    self.progress_queue.put(file_attr)
                elif os.path.isdir(local_path) and self.mode == "folders":
                    self.progress_queue.put(file_attr)
                else:
                    file_dict.append(file_attr)

            return {
                "file_dict": file_dict,
                "total_files": response.meta["total"],
                "next": response.meta["next"]
            }

    def file_handler(self):
        """
        Overrides default behavior to handle chunks of files
        @return: None
        """
        # Run as long as we have files to delete
        while self.task_active.is_set():
            try:
                # Get file non-blocking way, otherwise thread will hang forever
                file = self.handle_queue.get_nowait()
            except Empty:
                file = None

            if file:
                # If we have a file/folder to delete we add it to the deletion list
                local_path = "{}/{}".format(self.data_owner.working_dir, file["fullpath"])
                file["local_path"] = local_path
                if file.get("type", "files") == "files":
                    self.files_to_delete.append(file["fullpath"])
                elif file.get("type", "files") == "folders":
                    self.folders_to_delete.append(file["fullpath"])

            try:
                # Try to delete a chunk of files/folders
                if len(self.files_to_delete) + len(self.folders_to_delete) >= self.chunk_size or \
                   len(self.files_to_delete) + len(self.folders_to_delete) >= (self.total_files - self.handled_files):
                    self._handle_file_function()
            except Exception as e:
                # Should not be possible to enter here, safeguard against deadlock
                print("An unhandled exception in downloader thread has occurred:")
                print(e)
                with self.progress_lock:
                    self.handled_files += len(self.files_to_delete) + len(self.folders_to_delete)
                    self.files_to_delete = []
                    self.folders_to_delete = []

            if file is None:
                time.sleep(0.1)

    def _handle_file_function(self, **kwargs):
        """
        Function to that collect 1000 files that need to be deleted and then delete them from remote
        @param local_path: File location locally
        @param kwargs: Needs to be fullpath of the file
        @return: None
        """

        with self.progress_lock:
            try:
                self.data_owner._proxy.call_api(
                    urljoin(self.data_owner._route, "commits", self.commit, "delete_files"),
                    http_method=HTTP.POST,
                    payload={"files": self.files_to_delete, "mode": "files"}
                )
                self.data_owner._proxy.call_api(
                    urljoin(self.data_owner._route, "commits", self.commit, "delete_files"),
                    http_method=HTTP.POST,
                    payload={"files": self.folders_to_delete, "mode": "folders"}
                )
            finally:
                for f in self.files_to_delete:
                    self.handle_queue.task_done()
                    self.progress_queue.put(f)
                for f in self.folders_to_delete:
                    self.handle_queue.task_done()
                    self.progress_queue.put(f)
                self.files_to_delete = []
                self.folders_to_delete = []
