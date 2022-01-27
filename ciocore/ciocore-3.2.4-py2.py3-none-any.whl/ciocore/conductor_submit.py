#!/usr/bin/env python

"""General Submitter for sending jobs and uploads to Conductor"""

import getpass
import json
import logging
import os

from ciocore import config
from ciocore import file_utils, api_client, uploader
from ciocore.common import CONDUCTOR_LOGGER_NAME

logger = logging.getLogger(CONDUCTOR_LOGGER_NAME)


class Submit(object):
    """Conductor Submission object."""

    def __init__(self, args):
        """
        Initialize the payload and some other properties needed for preparing uploads.

        Payload properties must not be None. Any property that has None for the default value must
        be provided in the args.
        """
        self.upload_paths = list(args.get("upload_paths", []))
        self.md5_caching = args.get("md5_caching", True)
        self.enforced_md5s = args.get("enforced_md5s", {})
        self.database_filepath = args.get("database_filepath", "")
        self.api_client = api_client.ApiClient()

        self.payload = {
            # Attributes that have default==None, indicate that the coresponding arg is required.
            "instance_type": None,
            "project": None,
            "tasks_data": None,
            "output_path": None,
            # Attributes below are optional.
            "autoretry_policy": {},
            "docker_image": "",
            "environment": {},
            "job_title": "Unknown job title",
            "local_upload": True,
            "location": "",
            "preemptible": False,
            "metadata": {},
            "priority": 5,
            "scout_frames": "",
            "software_package_ids": [],
            "max_instances": 0,
            "chunk_size": 1,
            "owner": getpass.getuser(),
            "notify": [],
            # Attributes below are set during main run.
            "upload_files": [],
            "upload_size": 0,
        }

        for arg in self.payload:
            default = self.payload[arg]
            try:
                self.payload[arg] = args[arg]
            except KeyError:
                if default is None:
                    logger.error("Submit: You must provide the '{}' argument.".format(arg))
                    raise

        self.payload["notify"] = {"emails": self.payload["notify"]}

        for arg in self.payload:
            if arg not in ["tasks_data", "upload_paths"]:
                logger.debug("{}:{}".format(arg, self.payload[arg]))

    def main(self):
        """
        Submit the job

        There are two possible submission flows.
        1. local_upload=True: md5 calcs and uploads are performed on the artist's machine in the
           session.

        2. local_upload=False: md5 calcs and uploads are performed on on any machine with access to
           the filesystem on which the files reside, and by the same paths as the submission machine.
        """
        processed_filepaths =  file_utils.process_upload_filepaths(self.upload_paths)
        file_map = {path: None for path in processed_filepaths}

        if self.payload["local_upload"]:
            file_map = self._handle_local_upload(file_map)
        elif self.enforced_md5s:
            file_map = self._enforce_md5s(file_map)

        for path in file_map:
            expanded = self._expand_stats(path, file_map[path])
            self.payload["upload_files"].append(expanded)
            self.payload["upload_size"] += expanded["st_size"]

        logger.info("Sending Job...")
        response, response_code = self.api_client.make_request(
            uri_path="jobs/", 
            data=json.dumps(self.payload), 
            raise_on_error=False, 
            use_api_key=True
        )

        if response_code not in [201, 204]:
            raise Exception("Job Submission failed: Error %s ...\n%s" % (response_code, response))

        return json.loads(response), response_code

    def _handle_local_upload(self, file_map):
        """
        Call on the uploader to upload the files in the session.

        Returns {"path1': md5_1, path2: md5_2}
        """
        cfg = config.config().config
        api_client.read_conductor_credentials(use_api_key=True)
        uploader_args = {
            "location": self.payload["location"],
            "database_filepath": self.database_filepath,
            "thread_count": cfg["thread_count"],
            "md5_caching": self.md5_caching,
        }
        uploader_ = uploader.Uploader(uploader_args)
        upload_error_message = uploader_.handle_upload_response(
            self.payload["project"], file_map
        )
        if upload_error_message:
            raise Exception("Could not upload files:\n%s" % upload_error_message)
        # Get the resulting dictionary of the file's and their corresponding md5 hashes
        upload_md5s = uploader_.return_md5s()
        for path in upload_md5s:
            md5 = upload_md5s[path]
            file_map[path] = md5

        return file_map

    def _enforce_md5s(self, file_map):
        """
        Only ca.

        Returns {"path1': enforced_md5_1, path2: enforced_md5_2}
        """
        for filepath in self.enforced_md5s:
            md5 = self.enforced_md5s[filepath]
            logger.debug("filepath is %s" % filepath)
            processed_filepaths = file_utils.process_upload_filepath(filepath)
            assert len(processed_filepaths) == 1, (
                "Did not get exactly one filepath: %s" % processed_filepaths
            )
            file_map[processed_filepaths[0]] = md5

        return file_map

    @staticmethod
    def _expand_stats(file, md5):
        filestat = os.stat(file)
        return {
            "md5": md5,
            "destination": file,
            "st_mode": filestat.st_mode,
            "st_ino": filestat.st_ino,
            "st_dev": filestat.st_dev,
            "st_nlink": filestat.st_nlink,
            "st_uid": filestat.st_uid,
            "st_gid": filestat.st_gid,
            "st_size": filestat.st_size,
            "st_atime": filestat.st_atime,
            "st_mtime": filestat.st_mtime,
            "st_ctime": filestat.st_ctime,
        }
