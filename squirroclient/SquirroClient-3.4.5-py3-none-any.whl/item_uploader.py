"""Sends items to Squirro."""
import base64
import copy
import logging
import math
import os
import sys
import time
from numbers import Number

try:
    from ConfigParser import SafeConfigParser as ConfigParser
except ImportError:
    from configparser import ConfigParser

import six

from .base import SquirroClient
from .exceptions import NotFoundError
from .util import deprecation

try:
    import ujson as json
except ImportError:
    import json


log = logging.getLogger(__name__)

# Some magic for providing test support for the Squirro Client. squirro.common
# is not available on customer's machines, so we don't use get_injected there.
try:
    from squirro.common.dependency import DependencyNotFound, get_injected

    def get_client_cls():
        try:
            return get_injected("squirro_client_cls")
        except DependencyNotFound:
            return SquirroClient


except ImportError:

    def get_client_cls():
        return SquirroClient


class ItemUploader(object):
    """Item uploader class. Defaults are loaded from the ``.squirrorc`` file in
    the current user's home directory.

    :param token: User refresh token.
    :param project_id: Identifier of the project, optional but one of
        ``project_id`` or ``project_title`` has to be passed in.
    :param project_title:  Title of the project. This will use the first
        project found with the given title. If two projects with the same
        title exist the project being used is not predictable.
    :param object_id: This parameter is deprecated, and is no longer needed.
    :param source_name: Name of the source to be used. If a source with this
        name does not exist, then a new source with this name is created. If
        more than one sources with this name exist, then the processing is
        aborted and can only be resumed by specifying the `source_id` of the
        desired source to load into.
    :param source_ext_id: External identifier of the source, if not
        provided defaults to ``source_name``.
    :param cluster: Cluster to connect to. This only needs to be changed
        for on-premise installations.
    :param batch_size: Number of items to send in one request. This should
        be lower than 100 depending on your setup. If set to -1 the optimal
        batch size is calculated from the items. Defaults to -1.
    :param config_file: Configuration file to use, defaults to
        ~/.squirrorc
    :param config_section: Section of the .ini file to use, defaults to
        ``squirro``.
    :param source_id: Source which should be used. If a source with the id
        exists, then no source is created
    :param source_secret: This option is deprecated now and is ignored.
    :param pipeline_workflow_name: Pipeline workflow name. Either name or id
        need to be set.
    :param pipeline_workflow_id: Pipeline workflow ID.
    :param dataloader_options: Dataloader options to store along with a creation of a
        new data source.
    :param dataloader_plugin_options: Dataloader plugin options to store with a creation
        of a new data source.
    :param non_retry_list: List of status codes for which we don't want a
        retry/backoff logic. Defaults to `[200, 202, 401, 403, 400, 404]`.

        200, 202
            Successful codes.

        401, 403
            Already have a retry block in the _perform_request method of
            Squirro Client.

        400, 404
            Does not make sense to retry for these codes as retrying won't fix
            the underlying issue.

    Typical usage::

        >>> from squirro_client import ItemUploader
        >>> uploader = ItemUploader(project_title='My Project',
        ...                         token='<your token>')
        >>> items = [{'id': 'squirro-item1',
        ...           'title': 'Items arrived in Squirro!'}]
        >>> uploader.upload(items)

    Project selection:

    The `ItemUploader` creates a source in your project. The project must
    exist before the `ItemUploader` is instantiated.

    Source selection:

    The source will be created or re-used, the above parameter define
    how the source will be named.

    Configuration:

    The :class:`ItemUploader` can load its settings from a configuration file
    The default section is ``squirro`` and may be overridden by the parameter
    ``config_section`` to allow for multiple sources/projects.

    Example configuration::

        [squirro]
        project_id = 2sic33jZTi-ifflvQAVcfw
        token = 9c2d1a9002a8a152395d74880528fbe4acadc5a1

    """

    def __init__(
        self,
        token=None,
        project_id=None,
        project_title=None,
        object_id=None,
        source_name=None,
        source_ext_id=None,
        cluster=None,
        client_cls=None,
        batch_size=None,
        config_file=None,
        config_section=None,
        processing_config=None,
        steps_config=None,
        source_id=None,
        source_secret=None,
        pipeline_workflow_name=None,
        pipeline_workflow_id=None,
        timeout_secs=None,
        dataloader_options=None,
        dataloader_plugin_options=None,
        non_retry_list=[200, 202, 400, 401, 403, 404],
        **kwargs,
    ):
        self.non_retry_list = non_retry_list
        if source_secret:
            msg = (
                "`source_secret` parameter is deperecated and is not "
                "necessary anymore."
            )
            deprecation(msg)
            raise NotImplementedError(msg)

        if object_id:
            msg = (
                "`object_id` parameter is deperecated and is not necessary " "anymore."
            )
            deprecation(msg)
            raise NotImplementedError(msg)

        if processing_config:
            msg = (
                "`processing_config` parameter is deperecated and is not "
                "supported anymore. Please use steps_config or "
                "pipeline_workflow_name or pipeline_workflow_id instead."
            )
            deprecation(msg)
            raise NotImplementedError(msg)

        # possibly deprecated bits
        self.config = None
        kwargs.update(locals())
        del kwargs["self"]
        self._load_config(kwargs)
        self._validate_config()

        # Do not create a new SqiurroClient if an authenticated client instance
        # has been supplied already
        self.client = None
        if kwargs.get("client_instance"):
            self.client = kwargs.get("client_instance")
        else:
            self._create_squirro_client(
                client_cls,
                retry_status_forcelist=frozenset([502, 503, 504]),
                timeout_secs=timeout_secs,
            )

        self._lookup_project()

        if source_id:
            # Use existing source if exists
            # Otherwise fail
            # Warn ignoring fields if given
            if any([pipeline_workflow_id, pipeline_workflow_name, steps_config]):
                log.warning(
                    "Ignoring parameters: `pipeline_workflow_id`, "
                    "`pipeline_workflow_name`, and `steps_config`"
                )

            self.source_id = self._lookup_source(source_id=source_id)["id"]
            return

        elif pipeline_workflow_id:
            # Use existing pipeline workflow if exists
            # Otherwise fail
            # Warn ignoring fields if given
            if any([pipeline_workflow_name, steps_config]):
                log.warning(
                    "Ignoring parameters: `pipeline_workflow_name`, "
                    "and `steps_config`"
                )
            workflow = self._lookup_workflow(uuid=pipeline_workflow_id)

        elif steps_config:
            # Create pipeline workflow with steps config
            # Warn ignoring fields if given

            if pipeline_workflow_name:
                # If name is given, use it
                # Fail if name exists
                workflow = self._lookup_workflow(name=pipeline_workflow_name)

            else:
                pipeline_workflow_name = "Item Uploader"
                workflow = self.client.new_pipeline_workflow(
                    self.project_id, pipeline_workflow_name, steps=steps_config
                )

        elif pipeline_workflow_name:
            # Use workflow with this name
            # Fail if name doesn't exist
            workflow = self._lookup_workflow(name=pipeline_workflow_name)

        else:
            # Use default
            workflow = self._lookup_workflow()

        # get or create source
        try:
            source = self._lookup_source(source_name=source_name)
            if source["pipeline_workflow_id"] != workflow["id"]:
                raise ValueError(
                    "Specified source {} exists, but is incompatible with "
                    "provided `pipeline_workflow_name`, `pipeline_workflow_id`"
                    ", or `steps_config`".format(source)
                )
        except NotFoundError:
            log.info(
                "Source %r in Project %r not present. Creating one",
                source_id,
                self.project_id,
            )
            source = self._create_source(
                source_name=source_name,
                pipeline_workflow_id=workflow["id"],
                dataloader_options=dataloader_options,
                dataloader_plugin_options=dataloader_plugin_options,
            )
            log.info("New source created with id %r", source["id"])

        self.source_id = source["id"]

        log.info(
            "Using source id %r with pipeline workflow id %r in project %r",
            self.source_id,
            workflow["id"],
            self.project_id,
        )

    def _lookup_workflow(self, name=None, uuid=None):
        """Returns the workflow for a given workflow `name` or `uuid`.
        If the `uuid` is set but not 'default' this takes precedence over the
        name. If neither is set (or uuid is set to 'default') the project
        default workflow is returned.
        If no workflow is found a NotFoundError is raised."""
        workflows = self.client.get_pipeline_workflows(self.project_id)

        if uuid and uuid != "default":
            for workflow in workflows:
                if workflow["id"] == uuid:
                    return workflow

        elif name:
            for workflow in workflows:
                if workflow["name"] == name:
                    return workflow

        elif not uuid or uuid == "default":
            for workflow in workflows:
                if workflow["project_default"]:
                    return workflow

        raise NotFoundError('Workflow "%s" with id "%s" was not found!' % (name, uuid))

    def _load_config(self, kwargs):
        """Loads the configuration from file and merges it with the passed-in
        arguments"""
        parser = ConfigParser()
        file_names = kwargs.get("config_file")
        if not file_names:
            file_names = [os.path.expanduser("~/.squirrorc")]
        parser.read(file_names)

        # initialize with defaults
        config = copy.deepcopy(self.DEFAULTS)

        # read from config-file
        config_section = kwargs.get("config_section")
        if not config_section:
            config_section = "squirro"
        if parser.has_section(config_section):
            config.update(dict(parser.items(config_section)))

        # update with kwargs actually passed in
        config.update(dict([(k, v) for k, v in kwargs.items() if v is not None]))
        config = dict([(k, v) for k, v in config.items() if k in self.CONFIG_KEYS])

        # transform integer arguments
        for key in self.INT_OPTIONS:
            if not config.get("key") is None:
                config[key] = int(config[key])

        # adjust the cluster URL
        if config.get("cluster"):
            config["cluster"] = config["cluster"].rstrip("/")

        if not config.get("source_ext_id"):
            config["source_ext_id"] = config.get("source_name")

        self.config = config

    def _validate_config(self):
        """Validates mandatory parameters and checks invalid combination.
        Raises a `ValueError` if something is off"""

        if not any([self.config.get("project_id"), self.config.get("project_title")]):
            raise ValueError('Parameters ("project_id"/"project_title") is required')

        if self.config.get("source_id") and self.config.get("steps_config"):
            raise ValueError(
                'Parameters "source_id" and "steps_config" ' "are mutually exclusive."
            )

        if not self.config.get("token"):
            raise ValueError('Mandatory parameter "token" is missing')

        manual_config = [
            self.config.get("topic_api_url"),
            self.config.get("user_api_url"),
            self.config.get("provider_api_url"),
        ]
        if not self.config.get("cluster") and not all(manual_config):
            raise ValueError('Mandatory parameter "cluster" is missing')

        if all([self.config.get("project_id"), self.config.get("project_title")]):
            raise ValueError(
                'Parameters "project_id" and "project_title" are ' "mutually exclusive"
            )

    def _create_squirro_client(self, client_cls, **kwargs):
        """Creates a Squirro client"""
        if all(
            [
                self.config.get("topic_api_url"),
                self.config.get("user_api_url"),
                self.config.get("provider_api_url"),
            ]
        ):
            kwargs.update(
                {
                    "topic_api_url": self.config["topic_api_url"],
                    "user_api_url": self.config["user_api_url"],
                }
            )
        else:
            kwargs["cluster"] = self.config["cluster"]

        if not client_cls:
            client_cls = get_client_cls()

        self.client = client_cls(None, None, **kwargs)
        self.client.authenticate(refresh_token=self.config["token"])

    def _lookup_project(self):
        """Looks up the project either by `project_id` or `project_title`"""
        if self.config.get("project_id"):
            project_id = self.config["project_id"]
            self.client.get_project(project_id)
            self.project_id = project_id
        else:
            project_title = self.config["project_title"]
            projects = self.client.get_user_projects()
            for project in projects:
                if project["title"] == project_title:
                    self.project_id = project["id"]
                    break

            if getattr(self, "project_id", None) is None:
                raise NotFoundError(
                    "No project with title {0!r} found".format(project_title)
                )

    def _lookup_source(self, source_id=None, source_name=None):
        """Looks up a source with `source_id` called `source_name`."""

        if source_id:
            try:
                source = self.client.get_source(self.project_id, source_id)
                if source_name and source.get("name") != source_name:
                    raise ValueError(
                        "Source %r in project %r does not have name %r",
                        source_id,
                        self.project_id,
                        source_name,
                    )
            except NotFoundError:
                log.exception(
                    "Source %r in project %r not present.", source_id, self.project_id
                )
                raise

        elif source_name:
            sources = [
                source
                for source in self.client.get_sources(self.project_id)
                if source["name"] == source_name
            ]
            source_ids = [source["id"] for source in sources]
            log.debug("Sources %r with name %r", source_ids, source_name)
            if len(source_ids) > 1:
                raise ValueError(
                    "Multiple sources with ids {} found with name {} in "
                    " project {}. Please set the source_id parameter".format(
                        source_ids, source_name, self.project_id
                    )
                )
            elif len(source_ids) == 1:
                source = sources[0]
            else:
                raise NotFoundError(
                    "Source with name {} in project {} not found.".format(
                        source_name, self.project_id
                    )
                )

        else:
            raise NotFoundError("Must define either `source_id` or `source_name`.")

        return source

    def _create_source(
        self,
        source_name,
        pipeline_workflow_id,
        dataloader_options=None,
        dataloader_plugin_options=None,
    ):
        default_dataloader_options = {
            "project_id": self.project_id,
            "plugin_name": "ITEMUPLOADER",
            "runs_on_client": True,
        }
        default_dataloader_plugin_options = {}

        source_config = {}

        if dataloader_options:
            source_config["dataloader_options"] = dataloader_options
            source_config["dataloader_options"]["runs_on_client"] = True
        else:
            source_config["dataloader_options"] = default_dataloader_options

        if dataloader_plugin_options:
            source_config["dataloader_plugin_options"] = dataloader_plugin_options
        else:
            source_config[
                "dataloader_plugin_options"
            ] = default_dataloader_plugin_options

        res = self.client.new_source(
            project_id=self.project_id,
            name=source_name or self.DEFAULTS["source_name"],
            config=source_config,
            scheduling_options={"force_stop_scheduling": True},
            pipeline_workflow_id=pipeline_workflow_id,
        )
        return res

    def upload(
        self,
        items,
        priority=0,
        pipeline_workflow_id=None,
        num_retries=10,
        delay=1,
        backoff=2,
    ):
        """Sends ``items`` to Squirro.

        :param items: A list of items. See the `Item Format`_ documentation for
            the keys and values of the individual items.
        :param priority: int, describing the priority of ingestion for the
            dataset to be loaded. Currently only supports a value of `0` or `1`.
            `0` means that the items are loaded in an asynchronous fashion and
            `1` would mean that the items are loaded in a synchronous fashion.
        :param pipeline_workflow_id: str, id of an existing pipeline
            workflow which should be used to process the current batch of
            items. Can only be used with parameter `priority` set to 1.
        :param num_retries: int, Number of retries to make when a service is
            unavailable.
        :param delay: int, Initial delay in seconds between retries.
        :param backoff: int, Backoff multiplier, e.g. value of 2 will double
            the delay each retry.
        """

        self._validate_upload_parameters(priority, pipeline_workflow_id)
        if not self.config.get("provider_api_url"):
            cluster = self.config["cluster"]
            url = "{0}/api/provider/v1/{1}/projects/{2}/sources/{3}/push_items".format(
                cluster, self.client.tenant, self.project_id, self.source_id
            )
        else:
            endpoint = self.config["provider_api_url"]
            url = "{0}/v1/{1}/projects/{2}/sources/{3}/push_items".format(
                endpoint, self.client.tenant, self.project_id, self.source_id
            )
        headers = {"Content-Type": "application/json"}
        params = {"priority": priority}
        if pipeline_workflow_id is not None:
            params.update({"pipeline_workflow_id": pipeline_workflow_id})

        self._upload(items, url, params, headers, num_retries, delay, backoff)

    def upload_rows(
        self,
        rows,
        priority=0,
        pipeline_workflow_id=None,
        num_retries=10,
        delay=1,
        backoff=2,
    ):
        """Sends ``rows`` to Squirro.

        :param rows: A list of rows. Row means a single row of data that will eventually
            transformed, enriched, and become a Squirro item. In other words, a row is a
            single data point/sample of raw data, as extracted by a Squirro dataloader
            plugin.
        :param priority: int, describing the priority of ingestion for the dataset to be
            loaded. Currently only supports a value of `0` or `1`.
            `0` means that the items are loaded in an asynchronous fashion and
            `1` would mean that the items are loaded in a synchronous fashion.
        :param pipeline_workflow_id: str, id of an existing pipeline workflow which
            should be used to process the current batch of items. Can only be used with
            parameter `priority` set to 1.
        :param num_retries: int, Number of retries to make when a service is
            unavailable.
        :param delay: int, Initial delay in seconds between retries.
        :param backoff: int, Backoff multiplier, e.g. value of 2 will double
            the delay each retry.
        """
        self._validate_upload_parameters(priority, pipeline_workflow_id)
        if not self.config.get("provider_api_url"):
            cluster = self.config["cluster"]
            url = "{0}/api/provider/v1/{1}/projects/{2}/sources/{3}/push_rows".format(
                cluster, self.client.tenant, self.project_id, self.source_id
            )
        else:
            endpoint = self.config["provider_api_url"]
            url = "{0}/v1/{1}/projects/{2}/sources/{3}/push_rows".format(
                endpoint, self.client.tenant, self.project_id, self.source_id
            )
        headers = {"Content-Type": "application/json"}
        params = {"priority": priority}
        if pipeline_workflow_id is not None:
            params.update({"pipeline_workflow_id": pipeline_workflow_id})

        # in order to dump successfully the rows to json, we need first to transform any
        # binary data to text (e.g. `file_data` of a PDF file)
        base64_encoded_columns = set()
        for row in rows:
            for column_name, value in row.items():
                if isinstance(value, (bytes, bytearray)):
                    row[column_name] = base64.b64encode(value).decode()
                    base64_encoded_columns.add(column_name)

        if base64_encoded_columns:
            # cannot pass it as a param to the endpoint with a list value
            base64_encoded_columns = ",".join(col for col in base64_encoded_columns)
            params.update({"base64_encoded_columns": base64_encoded_columns})

        self._upload(rows, url, params, headers, num_retries, delay, backoff)

    def _validate_upload_parameters(self, priority, pipeline_workflow_id):
        """Validations for parameters to the `upload` function."""
        if priority != 1 and pipeline_workflow_id:
            raise ValueError(
                "Can not specify a `pipeline_workflow_id` in priority"
                " {}".format(priority)
            )

        if pipeline_workflow_id:
            self._lookup_workflow(uuid=pipeline_workflow_id)

    def _get_batch_size(self, items):
        """Gets the batch size from config or calculates the optimal size based
        on the items if batch_size is set to -1.
        """
        MAX_BYTE_SIZE = 5e7  # 50MB, allows for some json dumps overhead and
        # ES bulk action instructions

        batch_size = self.config["batch_size"]

        if batch_size == -1:
            items_bytes_size = sys.getsizeof(json.dumps(items))
            if items_bytes_size < MAX_BYTE_SIZE:
                batch_size = len(items)
            else:
                # how many chunks do we split the items into?
                nof_chunks = math.ceil(float(items_bytes_size) / MAX_BYTE_SIZE)
                assert nof_chunks >= 1
                batch_size = max(1, int(math.floor(float(len(items)) / nof_chunks)))

        # Never return a batch_size of zero.
        if batch_size < 1:
            batch_size = 1

        return int(batch_size)

    def _fixup_keywords(self, item):
        """Validates and fixes keywords of `item`"""
        if item.get("keywords") is None:
            return

        keywords = item["keywords"]
        for key, value in keywords.items():
            if isinstance(value, (Number, six.string_types)):
                keywords[key] = [value]
            elif isinstance(value, list):
                keywords[key] = value
            elif isinstance(value, set):
                keywords[key] = list(value)
            else:
                raise TypeError(
                    "Cannot validate the keyword {0}. Type {1} "
                    "is not supported".format(key, type(value))
                )

    def _upload(self, items, url, params, headers, num_retries, delay, backoff):
        if not items:
            log.info("Asked to upload empty item list. Skipping.")
            return

        batch_size = self._get_batch_size(items)
        num_batches = math.ceil(len(items) / batch_size)
        for idx in range(0, len(items), batch_size):
            mdelay = delay
            for item in items[idx : idx + batch_size]:
                self._fixup_keywords(item)
            data = json.dumps(items[idx : idx + batch_size])
            for i in range(num_retries + 1):
                if i != 0:
                    log.warning(f"Retrying {i} of {num_retries}")
                res = self.client._perform_request(
                    "post", url, params=params, data=data, headers=headers
                )
                if res.status_code in self.non_retry_list:
                    self.client._process_response(res, [202])
                    break
                else:
                    log.warning(
                        f"Failed to upload batch {int(idx / batch_size) + 1} of "
                        f"{num_batches}, returned status code {res.status_code}. "
                        f"Sleeping for {mdelay} seconds."
                    )
                    time.sleep(mdelay)
                    mdelay *= backoff

    # default values for arguments
    DEFAULTS = {
        "source_name": "Upload",
        "cluster": "https://demo.squirro.net",
        "batch_size": -1,  # auto calculate
    }

    # options to be converted to int
    INT_OPTIONS = ["batch_size"]

    # arguments that can be passed in the constructor/ini-file
    CONFIG_KEYS = [
        "token",
        "cluster",
        "project_id",
        "project_title",
        "source_name",
        "source_ext_id",
        "batch_size",
        "user_api_url",
        "topic_api_url",
        "provider_api_url",
        "source_id",
    ]
