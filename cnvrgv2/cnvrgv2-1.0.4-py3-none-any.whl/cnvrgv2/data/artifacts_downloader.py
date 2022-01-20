import os
import json

from cnvrgv2.proxy import HTTP
from cnvrgv2.utils.url_utils import urljoin
from cnvrgv2.data.remote_files_handler import RemoteFilesHandler


class ArtifactsDownloader(RemoteFilesHandler):
    def __init__(
        self,
        data_owner,
        num_workers=40,
        queue_size=5000,
        chunk_size=1000,
        force=False,
        base_commit_sha1=None,
        commit_sha1=None,
        progress_bar_enabled=False,
    ):
        """
        Multithreaded file downloader - download artifacts files from server (by compare commit to base_commit)
        @param data_owner: Cnvrg dataset / project object
        @param num_workers: Number of threads to handle files
        @param queue_size: Max number of file meta to put in queue
        @param chunk_size: File meta chunk size to fetch from the server
        @param force: Force rewrite existing files
        @param base_commit_sha1: Base commit sha1 of the comparision
        @param commit_sha1: Commit sha1 of the comparision
        @param progress_bar_enabled: Boolean indicating whenever or not to print a progress bar. In use of the cli
        """
        super().__init__(
            data_owner,
            num_workers=num_workers,
            queue_size=queue_size,
            chunk_size=chunk_size,
            force=force,
            base_commit_sha1=base_commit_sha1,
            commit_sha1=commit_sha1,
            progress_bar_enabled=progress_bar_enabled
        )

    def _collector_function(self, page_after=None):
        """
        Function to collect files that should be downloaded
        @param page_after: The id of the next file that the iteration of the pagination should start from
        @return: Should return array of files metadata
        """
        if not self.base_commit_sha1:
            raise AttributeError("base commit must be sent")

        data = {
            "base_commit_sha1": self.base_commit_sha1,
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
                urljoin(self.data_owner._route, "commits", self.commit_sha1, "compare"),
                "page[after]={}&page[size]=1000&sort=id".format(page_after)
            ),
            http_method=HTTP.GET,
            payload=data
        )

        file_dict = []
        for file in response.items:
            file_dict.append(dict(file.attributes))

        return {
            "file_dict": file_dict,
            "total_files": response.meta["total"],
            "total_files_size": response.meta["total_files_size"],
            "next": response.meta["next"]
        }

    def _handle_file_function(self, local_path, progress_bar=None, **kwargs):
        """
        Function that download single file
        @param local_path: File location locally
        @param progress_bar: A progress bar object to be used during the download
        @param kwargs: Needs to be object_path of the file in the bucket
        @return: None
        """
        if self.force or not os.path.exists(local_path):
            self.storage_client.download_single_file(local_path, kwargs["object_path"], progress_bar)

        self.handle_queue.task_done()
        self.progress_queue.put(local_path)
