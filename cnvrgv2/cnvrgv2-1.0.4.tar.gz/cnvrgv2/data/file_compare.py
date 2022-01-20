import os
import re

from cnvrgv2.proxy import HTTP
from cnvrgv2.utils.url_utils import urljoin
from cnvrgv2.data.local_files_handler import LocalFilesHandler
from cnvrgv2.utils.storage_utils import create_dir_if_not_exists


class FileCompare(LocalFilesHandler):
    def __init__(self, data_owner, files, override=False, num_workers=40, chunk_size=1000, queue_size=5000):
        """
        Multithreaded file compare for cnvrg datasets - used to compare between files that should be uploaded
        so we can mark conflicts

        @param data_owner: Cnvrg dataset / project object
        @param files: list of files to upload
        @param override: Boolean stating whether or not we should re-upload even if the file already exists
        @param num_workers: Number of threads to use for concurrent file upload
        @param chunk_size: File meta chunk size to fetch from the server
        @param queue_size: Max number of file meta to prefetch from the server
        """
        super().__init__(
            data_owner,
            files=files,
            override=override,
            num_workers=num_workers,
            chunk_size=chunk_size,
            queue_size=queue_size
        )

    def _file_handler_function(self, local_path, object_path, progress_bar=None):
        """
        Function to mark conflicts
        @param local_path: file location locally
        @param object_path: file location in bucket
        @return: None
        """
        tmp_folder = "{}/.tmp".format(self.data_owner.working_dir)
        downloaded_file = "{}/{}".format(tmp_folder, local_path)
        if os.path.isfile(downloaded_file):
            new_path = re.sub(tmp_folder, self.data_owner.working_dir, downloaded_file)
            create_dir_if_not_exists(new_path)
            os.rename(downloaded_file, "{}.conflict".format(new_path))

        if os.path.isfile("{}.deleted".format(downloaded_file)):
            os.remove("{}.deleted".format(downloaded_file))
            exists_file = "{}/{}".format(self.data_owner.working_dir, local_path)
            create_dir_if_not_exists(exists_file)
            os.rename(exists_file, "{}.deleted".format(exists_file))

    def _file_collector_function(self, files_metadata):
        """
        Function to collect files metadata from server
        @param files_metadata: Local files metadata to sent to the server for getting files to compare
        @return: Array of files metadata
        """
        data = {
            "files": files_metadata,
            "override": self.override,
        }
        response = self.data_owner._proxy.call_api(
            route=urljoin(self.data_owner._route, "commits", self.data_owner.local_commit, "compare_local"),
            http_method=HTTP.POST,
            payload=data
        )

        blob_array = []
        for blob in response.items:
            blob_array.append({"id": blob.id, **blob.attributes})

        return blob_array
