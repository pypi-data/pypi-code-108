import argparse
import json
import logging
import os
import tempfile
from datetime import datetime
from urllib.parse import quote

import requests

from brevettiai.interfaces import vue_schema_utils as vue
from brevettiai.io import io_tools
from brevettiai.io.serialization import ObjectJsonEncoder
from brevettiai.platform import backend, Dataset
from brevettiai.platform.platform_credentials import DefaultJobCredentialsChain
from brevettiai.utils.dict_utils import dict_merger

log = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', help='path to platform host', default=None)
    parser.add_argument('--data_bucket', help='location of dataset buckets, for from_s3 call', default=None)
    parser.add_argument('--job_dir', help='location to write checkpoints and export models', default=None)
    parser.add_argument('--model_id', help='Assigned id to model', default='unknown')
    parser.add_argument('--test_id', help='Assigned id to model', default='unknown')
    parser.add_argument('--api_key', help="Job api key", default=None)
    parser.add_argument('--info_file', type=str, help='Info file with test job info', required=False)
    parser.add_argument('--cache_path', type=str, help='Cache path', required=False)
    parser.add_argument('--raygun_api_key', help='api key for raygun', default=None)
    return parser.parse_known_args()


class Job:
    """
    Interface for reading jobs from criterion.ai
    """

    class Settings(vue.VueSettingsModule):
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

    def __init__(self, job_dir, id, name, datasets, api_key, host_name, charts_url, complete_url, schema,
                 remote_url=None, security_credentials_url=None, settings=None, tags=[],
                 cache_path=None, models=None, new_datasets=True, run_id=None,
                 resolve_access_rights=True, io=io_tools, **kwargs):
        """
        :param schema: JSON schema used for model definition
        :param parameters: setup parameters overwriting default schema values
        """
        self.io = io
        self.run_id = run_id or datetime.now().strftime("%Y-%m-%dT%H%M%S")
        self.job_dir = job_dir
        self.id = id
        self.name = name
        self.datasets = datasets
        if new_datasets:
            self.datasets = [d if isinstance(d, Dataset)
                             else Dataset(**d, resolve_access_rights=False) for d in self.datasets]

        self.models = models
        self._schema = schema
        dict_merger(vue.parse_settings_args(schema), settings)
        settings = vue.apply_schema_to_model(schema, settings)
        self.settings = self.Settings.from_settings(settings or {})
        self.tags = tags

        self.api_key = api_key
        self.host_name = host_name
        self.api_endpoints = dict(
            charts=charts_url,
            complete=complete_url,
            remote=remote_url,
            security_credentials=security_credentials_url,
        )
        self._temporary_path = cache_path or tempfile.TemporaryDirectory(prefix="config-id-" + self.id + "-")
        self._job_output = {}
        self.model_path = None
        self.__dict__.update(kwargs)
        if resolve_access_rights:
            self.resolve_access_rights()

    def resolve_access_rights(self):
        """
        Resolve access rights of this config object
        :return:
        """
        self.io.resolve_access_rights(path=self.job_dir, resource_id=self.id, resource_type="job", mode="w")
        for ds in self.datasets:
            ds.resolve_access_rights()

    @classmethod
    def from_model_spec(cls, model, schema=None, config=None, **kwargs):
        """
        Build job object from model specification
        :param model:
        :param schema:
        :param config:
        :param kwargs:
        :return:
        """
        cdict = {} if config is None else config.__dict__

        if schema is None:
            schema = vue.SchemaBuilder().schema

        if isinstance(model["settings"], str):
            model["settings"] = json.loads(model["settings"])

        config = cls(
            name=model["name"],
            id=model["id"],
            job_dir=model["bucket"],
            settings=model["settings"],
            tags=model.get("tags", []),
            schema=schema,
            datasets=cdict.get("datasets", []),
            api_key=cdict.get("api_key"),
            charts_url=cdict.get("charts_url"),
            complete_url=cdict.get("complete_url"),
            remote_url=cdict.get("remote_url"),
            host_name=cdict.get("host_name"),
            **kwargs,
        )
        config.model_path = model.get("model_path", None)
        return config

    @classmethod
    def from_job_dir(cls, job_dir, schema_path, info_file=None, settings_overload=None, **kwargs):
        """
        Get Job from job directory and local schema
        :param job_dir: google storage bucket of job
        :param schema_path: path for model schema, or SchemaBuilder
        :param args: extra arguments to be parsed with argparse to settings
        :return: CriterionConfig object
        """

        info_file = info_file or io_tools.path.join(job_dir, "info.json")
        log.info("Config args found at: '%s'" % info_file)
        parameters = json.loads(str(io_tools.read_file(info_file), "utf-8"))
        log.debug(json.dumps(parameters, indent=2))

        if isinstance(schema_path, vue.SchemaBuilder):
            schema = schema_path
        else:
            try:
                with open(schema_path, 'r') as fp:
                    schema = json.load(fp)
            except FileNotFoundError:
                log.error("Could not find schema at location '{}'".format(schema_path))
                log.error("Install application or run 'python setup.py sdist --formats=gztar'"
                          " on the application to generate it")
                exit()

        # Overload settings
        settings_overload = settings_overload or {}
        settings = parameters.get("settings", {})
        dict_merger(settings_overload, settings)
        # Load settings
        parameters["settings"] = settings

        config = cls(
            job_dir=job_dir,
            schema=schema,
            **kwargs,
            **parameters
        )
        log.debug(config)
        return config

    @classmethod
    def init(cls, schema_path=None, job_dir=None, info_file=None, cache_remote_files=True, cache_path=None,
             log_level=logging.INFO, on_sagemaker=None, init_raygun=True, io=io_tools,
             api_key=None, job_id=None, host=None, data_bucket=None, **kwargs):
        """
        Initialize application and generate configuration object.
        Most of the parameters may also be set as args via sys.argv

        :param host: Host name of platform
        :param data_bucket: Bucket to use for unspecified data sources (sources not accessed via info.json)
        :param job_id: Job GUID
        :param api_key: Job API key to access remote sources
        :param schema_path: Path to application schema or SchemaBuilder
        :param job_dir: job directory, with artifacts, info.json, etc.
        :param info_file: to info.json from job dir
        :param cache_path: Specific path to cache objects on
        :param cache_remote_files: enable caching of remote files (default True)
        :param log_level: logging level
        :param on_sagemaker: force sagemaker run
        :param init_raygun: use raygun as error management service
        :param io: io object
        :param kwargs: Extra keyword args for configuration factory
        :return:
        """

        # Setup logging
        logging.basicConfig()
        log.root.setLevel(log_level)
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("charset_normalizer").setLevel(logging.WARNING)

        # Determine runtime
        on_sagemaker = on_sagemaker or os.environ.get("AWS_CONTAINER_CREDENTIALS_RELATIVE_URI") is not None

        # Initialize services
        if on_sagemaker:
            from brevettiai.interfaces import sagemaker
            sagemaker.load_hyperparameters_cmd_args()

        # Settings
        schema_path = schema_path or cls.Settings.get_schema()

        # Parse args
        args, _ = parse_args()
        # Platform
        backend.host = (host or args.host) or backend.host
        backend.data_bucket = (data_bucket or args.data_bucket) or backend.data_bucket
        # Job API: from input or input args
        job_id = job_id or args.test_id if args.model_id is "unknown" else args.model_id
        api_key = api_key or args.api_key
        job_dir = (job_dir or args.job_dir) or backend.job_dir(job_id)
        info_file = info_file or args.info_file
        cache_path = cache_path or args.cache_path

        credentials = DefaultJobCredentialsChain()
        io.minio.credentials = credentials

        if (info_file is not None and not os.path.exists(info_file)) or not os.path.exists(job_dir):
            credentials.set_credentials(job_id, api_key)
        io.resolve_access_rights(job_dir, resource_id=job_id, resource_type="job", mode="w")

        if init_raygun:
            from brevettiai.interfaces import raygun
            raygun.setup_raygun(api_key=args.raygun_api_key)

        # Initialize job
        job = cls.from_job_dir(job_dir=job_dir, schema_path=schema_path, info_file=info_file,
                               cache_path=cache_path, resolve_access_rights=False, **kwargs)
        credentials.set_credentials(job.id, job.api_key)
        if cache_remote_files:
            io.set_cache_root(job.temp_path("cache", dir=True))
        job.resolve_access_rights()

        job.upload_job_output()
        return job

    def temp_path(self, *paths, dir=False):
        """
        Get path in the temp directory tree
        :param paths: N path arguments
        :param dir: this is a directory
        :return:
        """
        dir_ = paths if dir else paths[:-1]
        folder = self.io.path.join(
            self._temporary_path if isinstance(self._temporary_path, str) else self._temporary_path.name, *dir_)
        self.io.make_dirs(folder)
        if dir:
            return folder
        else:
            return self.io.path.join(folder, paths[-1])

    def artifact_path(self, *paths, dir=False):
        """
        Get path in the artifact directory tree
        :param paths: N path arguments
        :param dir: this is a directory
        :return:
        """
        dir_ = paths if dir else paths[:-1]
        folder = self.io.path.join(self.job_dir, "artifacts", *dir_)
        self.io.make_dirs(folder)
        if dir:
            return folder
        else:
            return self.io.path.join(folder, paths[-1])

    def upload_artifact(self, artifact_name, payload, is_file=False):
        """
        Upload an artifact with a given name
        :param artifact_name: target artifact name
        :param payload: source
        :param is_file: payload is string to file location
        :return:
        """
        artifact_path = self.artifact_path(*((artifact_name,) if isinstance(artifact_name, str) else artifact_name))
        log.info('Uploading {} to {}'.format(artifact_name, artifact_path))
        if is_file:
            self.io.copy(payload, artifact_path)
        else:
            self.io.write_file(artifact_path, payload)

        return artifact_path.replace(self.io.path.join(self.job_dir, ''), '')

    def get_url(self, *file_path):
        """
        Get direct url through the platform
        :param file_path:
        :return:
        """
        return f"{self.host_name}/download?path={self.io.get_uri(self.io.path.join(self.job_dir, *file_path))}"

    def get_root_tags(self):
        r = requests.get(f"{self.host_name}/api/resources/roottags?key={self.api_key}&id={self.id}")
        try:
            return r.json()
        except ValueError:
            return None

    def upload_chart(self, name, vegalite_json):
        charts_url = f'{self.host_name}{self.api_endpoints["charts"]}&name={name}'
        try:
            return requests.post(charts_url, headers={'Content-Type': 'application/json'}, data=vegalite_json)
        except requests.exceptions.HTTPError as e:
            log.warning("HTTP error on complete job", exc_info=e)
        except requests.exceptions.RequestException as e:
            log.warning("No Response on complete job", exc_info=e)

    def add_output_metric(self, key, metric):
        """
        Add an output metric for the job comparison module
        :param key:
        :param metric:
        :return:
        """
        self._job_output[key] = metric

    def add_output_metrics(self, metrics):
        """
        Add a number of metrics to the job
        :param metrics:
        :return:
        """
        self._job_output.update(metrics)

    def upload_job_output(self, path="output.json", include_config=True):
        """
        Upload / update the output.json artifact containing parsed settings, etc.
        :param path:
        :param include_config:
        :return:
        """
        payload = dict(
            output=self._job_output,
            environment={x: os.getenv(x) for x in ("BUILD_ID",)},
            config=self
        )
        payload = ObjectJsonEncoder(indent=2, sort_keys=False).encode(payload)
        payload = payload.replace(self.api_key, "*" * len(self.api_key))
        return self.upload_artifact(path, payload)

    def complete_job(self, tmp_package_path=None, package_path=None, output_args=''):
        """
        Complete job by uploading package to gcs and notifying api
        :param tmp_package_path: Path to tar archive with python package
        :param package_path: package path on gcs
        :return:
        """

        complete_url = self.host_name + self.api_endpoints['complete']
        if package_path is None:
            if tmp_package_path is not None:
                artifact_path = self.artifact_path("saved_model.tar.gz")
                self.io.copy(tmp_package_path, artifact_path)
                complete_url += quote(artifact_path)
                self.model_path = artifact_path
        else:
            artifact_path = self.io.path.relpath(package_path, self.job_dir)
            assert ".." not in artifact_path, "Illegal package path. It should be an artifact of the model"
            complete_url += quote(artifact_path)
            self.model_path = artifact_path

        complete_url += output_args
        try:
            r = requests.post(complete_url)
            log.info(f'Job completed: {complete_url.split("&", 1)[-1]}')
            return r
        except requests.exceptions.HTTPError as e:
            log.warning("HTTP error on complete job", exc_info=e)
        except requests.exceptions.RequestException as e:
            log.warning("No Response on complete job", exc_info=e)

        if not isinstance(self._temporary_path, str):
            self._temporary_path.cleanup()

    def get_remote_monitor(self):
        from brevettiai.interfaces.remote_monitor import RemoteMonitor
        return RemoteMonitor(root=self.host_name, path=self.api_endpoints["remote"])

    @property
    def model_path(self):
        return self.__model_path

    @model_path.setter
    def model_path(self, path):
        if path is None:
            self.__model_path = None
        else:
            self.__model_path = self.io.path.join(self.job_dir, path)

    def __str__(self):
        return ObjectJsonEncoder(indent=2).encode(self)
