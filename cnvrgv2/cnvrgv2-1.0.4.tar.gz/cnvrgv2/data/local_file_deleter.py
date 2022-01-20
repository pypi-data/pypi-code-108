import os
import json
import re
import shutil
import cnvrgv2.utils.storage_utils as storage
from cnvrgv2.proxy import HTTP
from cnvrgv2.utils.url_utils import urljoin
from cnvrgv2.data.remote_files_handler import RemoteFilesHandler


class LocalFileDeleter(RemoteFilesHandler):
    def __init__(self, data_owner, num_workers=40, queue_size=5000, chunk_size=1000, force=False, mode="files"):
        """
        Multithreaded local file deleter - deleting files from local if they deleted on server
        @param data_owner: Cnvrg dataset / project object
        @param num_workers: Number of threads to handle files
        @param queue_size: Max number of file meta to put in queue
        @param chunk_size: File meta chunk size to fetch from the server
        @param force: Force rewrite existing files
        """
        self.mode = mode
        super().__init__(
            data_owner,
            num_workers=num_workers,
            queue_size=queue_size,
            chunk_size=chunk_size,
            force=force,
            base_commit_sha1=data_owner.last_commit,
            commit_sha1=data_owner.local_commit
        )

    def _collector_function(self, page_after=None):
        """
        Function to collect files that should be delete locally
        @param page_after: The id of the next file that the iteration of the pagination should start from
        @return: Should return array of files metadata
        """
        if not self.base_commit_sha1:
            raise AttributeError("base commit must be sent")

        data = {
            "base_commit_sha1": self.base_commit_sha1,
            "get_deleted": True,
            "mode": self.mode,
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
            "next": response.meta["next"]
        }

    def _handle_file_function(self, local_path, **kwargs):
        """
        Function that creates fullpath.deleted file in .tmp that in the end of the
        whole task will cause deletion of fullpath
        @param local_path: File location locally
        @param kwargs: Needs to be fullpath of the file
        @return: None
        """

        tmp_folder_name = "{}/.tmp".format(self.data_owner.working_dir)

        if self.mode == "folders":
            original_folder = re.sub(self.data_owner.TMP_FOLDER_NAME, self.data_owner.working_dir, kwargs["fullpath"])
            if os.path.isdir(original_folder):
                shutil.rmtree(original_folder)
        else:
            storage.create_dir_if_not_exists("{}/{}".format(tmp_folder_name, os.path.dirname(kwargs["fullpath"])))
            new_path = "{}/{}.deleted".format(tmp_folder_name, kwargs["fullpath"])
            open(new_path, 'a').close()

        self.handle_queue.task_done()
        self.progress_queue.put(local_path)
