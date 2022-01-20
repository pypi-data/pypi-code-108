from cnvrgv2.proxy import HTTP
from cnvrgv2.utils.url_utils import urljoin
from cnvrgv2.data.local_files_handler import LocalFilesHandler


class FileUploader(LocalFilesHandler):
    def __init__(
        self,
        data_owner,
        files,
        commit,
        override=False,
        num_workers=40,
        chunk_size=1000,
        queue_size=5000,
        progress_bar_enabled=False
    ):
        """
        Multithreaded local file uploader
        @param data_owner: Cnvrg dataset / project object
        @param files: List of files to upload
        @param commit: The commit sha1 to which we upload the files
        @param override: Boolean stating whether or not we should re-upload even if the file already exists
        @param num_workers: Number of threads to use for concurrent file uploading
        @param chunk_size: File meta chunk size to fetch from the server
        @param queue_size: Max number of file meta to put in queue
        @param progress_bar_enabled: Boolean indicating whenever or not to print a progress bar. In use of the cli
        """
        self.commit = commit
        super().__init__(
            data_owner,
            files=files,
            override=override,
            num_workers=num_workers,
            chunk_size=chunk_size,
            queue_size=queue_size,
            progress_bar_enabled=progress_bar_enabled
        )

    def _handle_file_progress_function(self, uploaded_ids):
        """
        Function to progress the upload
        @param uploaded_ids: Uploaded file ids
        @return: None
        """
        data = {"file_ids": uploaded_ids}
        self.data_owner._proxy.call_api(
            route=urljoin(self.data_owner._route, "commits", self.commit, "upload_files_save"),
            http_method=HTTP.POST,
            payload=data
        )

    def _file_handler_function(self, local_path, object_path, progress_bar=None):
        """
        Function to upload single file
        @param local_path: File location locally
        @param object_path: File location in bucket
        @return: None
        """
        self.storage_client.upload_single_file(local_path, object_path, progress_bar)

    def _file_collector_function(self, files_metadata):
        """
        Function to collect files metadata from server
        @param files_metadata: Local files metadata to sent to the server for getting files to upload
        @return: Array of files metadata
        """
        data = {
            "files": files_metadata,
            "override": self.override,
        }
        response = self.data_owner._proxy.call_api(
            route=urljoin(self.data_owner._route, "commits", self.commit, "upload_files"),
            http_method=HTTP.POST,
            payload=data
        )

        blob_array = []
        for blob in response.items:
            blob_array.append({"id": blob.id, **blob.attributes})

        return blob_array
