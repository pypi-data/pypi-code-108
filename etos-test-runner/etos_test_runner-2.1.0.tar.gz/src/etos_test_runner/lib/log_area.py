# Copyright 2020-2021 Axis Communications AB.
#
# For a full list of individual contributors, please see the commit history.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""ETR log area handler."""
import logging
import traceback
import time
from copy import deepcopy
from pathlib import Path
from shutil import make_archive, rmtree
from json.decoder import JSONDecodeError

from requests.auth import HTTPBasicAuth, HTTPDigestAuth
from requests.exceptions import HTTPError
from urllib3.exceptions import MaxRetryError, NewConnectionError


class LogArea:
    """Library for uploading logs to log area."""

    logger = logging.getLogger(__name__)

    def __init__(self, etos):
        """Initialize with an ETOS instance.

        :param etos: Instance of ETOS library.
        :type etos: :obj:`etos_lib.etos.Etos`
        """
        self.etos = etos
        self.suite_name = self.etos.config.get("test_config").get("name").replace(" ", "-")
        self.log_area = self.etos.config.get("test_config").get("log_area")
        self.logs = []
        self.artifacts = []

    @property
    def persistent_logs(self):
        """All persistent log formatted for EiffelTestSuiteFinishedEvent.

        :return: All persistent logs.
        :rtype: list
        """
        return [{"name": log["name"], "uri": log["uri"]} for log in self.logs]

    def _fix_name(self, path, test_name=None):
        """Fix the name of a file.

        "Fixing" means:

            - Prepend test name if file was gathered by a test case.
            - Prepend "log_info" if supplied by environment provider.
            - Reduce the size of the filename if it's too large.
            - Prepend a counter if filename already exists.

        :param path: Path to a file to fix.
        :type path: :obj:`pathlib.Path`
        :param test_name: Test name if this file was gathered during a test case.
        :type test_name: str
        :return: A new and improved path and filename.
        :rtype: :obj:`pathlib.Path`
        """
        directory, filename = path.parent, path.name
        if test_name is not None:
            self.logger.info("File collected as part of test case. Prepending %r", test_name)
            filename = f"{test_name}_{filename}"
            self.logger.info("Result: %r", filename)
        if self.log_area.get("logs"):
            prepend = self.log_area.get("logs").get("prepend", "")
            join_character = self.log_area.get("logs").get("join_character", "_")
            self.logger.info(
                "Log instructions added by environment provider. Prepending %r", prepend
            )
            filename = f"{prepend}{join_character}{filename}"
            self.logger.info("Result: %r", filename)
        if len(filename) + 5 > 255:  # +5 as to be able to prepend counter.
            self.logger.info(
                "Filename is too long at %r. Reduce size to %r.", len(filename) + 5, 250
            )
            filename = filename[: 250 - len(path.suffix)] + path.suffix
            self.logger.info("Result: %r", filename)
        log_names = [item["name"] for item in self.logs + self.artifacts]
        index = 0
        while filename in log_names:
            index += 1
            filename = f"{index}_{filename}"
            self.logger.info("Log name already exists. Rename to %r.", filename)
        return path.rename(directory.joinpath(filename))

    def collect(self, path):
        """Collect logs and artifacts from path.

        :param path: Path to collect logs and artifacts from.
        :type path: :obj:`pathlib.Path`
        :return: Filenames and paths.
        :rtype: list
        """
        test_name = self.etos.config.get("current_test")
        items = []
        self.logger.info("Collecting logs/artifacts for %r", test_name or "global")
        for item in path.iterdir():
            if item.is_dir():
                compressed_item = make_archive(
                    item.relative_to(Path.cwd()),
                    format="gztar",
                    root_dir=path,
                    base_dir=item.name,
                    logger=self.logger,
                )
                rmtree(item)
                item = Path(compressed_item)
            item = self._fix_name(item, test_name)
            items.append({"name": item.name, "file": item})
        return items

    def upload_logs(self, logs):
        """Upload logs to log area.

        :param logs: Logs to upload.
        :type logs: list
        """
        log_area_folder = (
            f"{self.etos.config.get('main_suite_id')}/{self.etos.config.get('sub_suite_id')}"
        )
        for log in logs:
            log["uri"] = self.__upload(
                self.etos.config.get("context"),
                log["file"],
                log["name"],
                log_area_folder,
            )
            self.logs.append(log)
            log["file"].unlink()

    def _artifact_created(self, artifacts):
        """Send artifact created event.

        :param artifacts: Artifacts that exists within this event.
        :type artifacts: list
        """
        test_name = self.etos.config.get("current_test")
        if test_name:
            identity = f"pkg:etos-test-output/{self.suite_name}/{test_name}"
        else:
            identity = f"pkg:etos-test-output/{self.suite_name}"
        file_information = []
        for artifact in artifacts:
            file_information.append({"name": artifact["file"].name})
        return self.etos.events.send_artifact_created_event(
            identity,
            fileInformation=file_information,
            links={
                "CONTEXT": self.etos.config.get("context"),
                "CAUSE": self.etos.config.get("sub_suite_id"),
            },
        )

    def _artifact_published(self, artifact_created, published_url):
        """Send artifact published event.

        :param artifact_created: The created artifact to publish.
        :type artifact_created: :obj:`eiffellib.events.EiffelArtifactCreatedEvent`
        :param published_url: URL to the published directory.
        :type published_url: str
        """
        log_area_type = self.log_area.get("type", "OTHER")
        locations = [{"uri": published_url, "type": log_area_type}]
        self.etos.events.send_artifact_published_event(
            locations,
            artifact_created,
            links={"CONTEXT": self.etos.config.get("context")},
        )

    def upload_artifacts(self, artifacts):
        """Upload artifacts to log area.

        :param artifacts: Artifacs to upload.
        :type artifacts: list
        :return: Artifact name and URI
        :rtype: tuple
        """
        if not artifacts:
            return
        log_area_folder = (
            f"{self.etos.config.get('main_suite_id')}/{self.etos.config.get('sub_suite_id')}"
        )
        self.logger.info("Uploading artifacts %r to log area", artifacts)
        artifact_created = self._artifact_created(artifacts)

        for artifact in artifacts:
            artifact["uri"] = self.__upload(
                self.etos.config.get("context"),
                artifact["file"],
                artifact["name"],
                log_area_folder,
            )
            self.artifacts.append(artifact)
            artifact["file"].unlink()

        upload = deepcopy(self.log_area.get("upload"))
        data = {
            "context": self.etos.config.get("context"),
            "folder": log_area_folder,
            "name": "",
        }
        published_url = upload["url"].format(**data)
        self._artifact_published(artifact_created, published_url)

    def __upload(self, context, log, name, folder):
        """Upload log to a storage location.

        :param context: Context for the http request.
        :type context: str
        :param log: Path to the log to upload.
        :type log: str
        :param name: Name of file to upload.
        :type name: str
        :param folder: Folder to upload to.
        :type folder: str
        :return: URI where log was uploaded to.
        :rtype: str
        """
        upload = deepcopy(self.log_area.get("upload"))
        data = {"context": context, "name": name, "folder": folder}

        # ETOS Library, for some reason, uses the key 'verb' instead of 'method'
        # for HTTP method.
        upload["verb"] = upload.pop("method")
        upload["url"] = upload["url"].format(**data)
        upload["timeout"] = upload.get("timeout", 30)
        if upload.get("auth"):
            upload["auth"] = self.__auth(**upload["auth"])

        with open(log, "rb") as log_file:
            for _ in range(3):
                request_generator = self.__retry_upload(log_file=log_file, **upload)
                try:
                    for response in request_generator:
                        self.logger.debug("%r", response)
                        if not upload.get("as_json", True):
                            self.logger.debug("%r", response.text)
                        self.logger.info("Uploaded log %r.", log)
                        self.logger.info("Upload URI          %r", upload["url"])
                        self.logger.info("Data:               %r", data)
                        break
                    break
                except:  # noqa pylint:disable=bare-except
                    self.logger.error("%r", traceback.format_exc())
                    self.logger.error("Failed to upload log!")
                    self.logger.error("Attempted upload of %r", log)
        return upload["url"]

    def __retry_upload(
        self, verb, url, log_file, timeout=None, as_json=True, **requests_kwargs
    ):  # pylint:disable=too-many-arguments
        """Attempt to connect to url for x time.

        :param verb: Which HTTP verb to use. GET, PUT, POST
                     (DELETE omitted)
        :type verb: str
        :param url: URL to retry upload request
        :type url: str
        :param log_file: Opened log file to upload.
        :type log_file: file
        :param timeout: How long, in seconds, to retry request.
        :type timeout: int or None
        :param as_json: Whether or not to return json instead of response.
        :type as_json: bool
        :param request_kwargs: Keyword arguments for the requests command.
        :type request_kwargs: dict
        :return: HTTP response or json.
        :rtype: Response or dict
        """
        if timeout is None:
            timeout = self.etos.debug.default_http_timeout
        end_time = time.time() + timeout
        self.logger.debug("Retrying URL %s for %d seconds with a %s request.", url, timeout, verb)
        iteration = 0
        while time.time() < end_time:
            iteration += 1
            self.logger.debug("Iteration: %d", iteration)
            try:
                # Seek back to the start of the file so that the uploaded file
                # is not 0 bytes in size.
                log_file.seek(0)
                yield self.etos.http.request(verb, url, as_json, data=log_file, **requests_kwargs)
                break
            except (
                ConnectionError,
                HTTPError,
                NewConnectionError,
                MaxRetryError,
                TimeoutError,
                JSONDecodeError,
            ):
                self.logger.warning("%r", traceback.format_exc())
                time.sleep(2)
        else:
            raise ConnectionError(f"Unable to {verb} {url} with params {requests_kwargs}")

    @staticmethod
    def __auth(username, password, type="basic"):  # pylint:disable=redefined-builtin
        """Create an authentication for HTTP request.

        :param username: Username to authenticate.
        :type username: str
        :param password: Password to authenticate with.
        :type password: str
        :param type: Type of authentication. 'basic' or 'digest'.
        :type type: str
        :return: Authentication method.
        :rtype: :obj:`requests.auth`
        """
        if type.lower() == "basic":
            return HTTPBasicAuth(username, password)
        return HTTPDigestAuth(username, password)
