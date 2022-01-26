# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Contains functionality to manage data context of datastores and datasets. Internal use only."""
import logging
import os
import re
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

from six import raise_from

module_logger = logging.getLogger(__name__)
http_pattern = re.compile(r"^https?://", re.IGNORECASE)
# If we are not running on Training Compute (aka BatchAI), we will by default leave 1GB free
_free_space_required = 1024 * 1024 * 1024
_bai_disk_buffer = 100 * 1024 * 1024

_logger = None


def _get_logger():
    from azureml.data._loggerfactory import _LoggerFactory

    global _logger
    if _logger is None:
        _logger = _LoggerFactory.get_logger(__name__)
    return _logger


def _log_trace(message):
    from azureml.data._loggerfactory import trace

    trace(_get_logger(), message)


def _log_and_print(msg):
    from datetime import datetime
    now = datetime.utcnow().isoformat(timespec='milliseconds')
    module_logger.debug(msg)
    print(f"[{now}] {msg}")


def _safe_mkdirs(dir_path):
    try:
        os.makedirs(dir_path, exist_ok=True)
    except Exception:
        # Handle race condition to mkdirs
        # This can be different nodes attemping so against a shared path (e.g. blob mount).
        if not os.path.exists(dir_path):
            raise
        _logger.warning('directory to make already exists. skipped making it.')


class _CommonContextManager(object):
    """Context manager common part."""

    def __init__(self, config):
        """Class _CommonContextManager constructor.

        :param config: The configuration passed to the context manager.
        :type config: dict
        """
        self._config = config
        module_logger.debug("Get config {}".format(config))
        self._workspace = self._get_workspace()

    @staticmethod
    def _get_workspace():
        from azureml.core.workspace import Workspace
        from azureml.core.authentication import AzureMLTokenAuthentication
        from azureml.exceptions import RunEnvironmentException

        try:
            # Load authentication scope environment variables
            subscription_id = os.environ["AZUREML_ARM_SUBSCRIPTION"]
            resource_group = os.environ["AZUREML_ARM_RESOURCEGROUP"]
            workspace_name = os.environ["AZUREML_ARM_WORKSPACE_NAME"]
            experiment_name = os.environ["AZUREML_ARM_PROJECT_NAME"]
            run_id = os.environ["AZUREML_RUN_ID"]

            # Initialize an AMLToken auth, authorized for the current run
            token, token_expiry_time = AzureMLTokenAuthentication._get_initial_token_and_expiry()
            url = os.environ["AZUREML_SERVICE_ENDPOINT"]
            location = re.compile("//(.*?)\\.").search(url).group(1)
        except KeyError as key_error:
            raise_from(RunEnvironmentException(), key_error)
        else:
            auth = AzureMLTokenAuthentication.create(token,
                                                     AzureMLTokenAuthentication._convert_to_datetime(
                                                         token_expiry_time),
                                                     url,
                                                     subscription_id,
                                                     resource_group,
                                                     workspace_name,
                                                     experiment_name,
                                                     run_id)
            # Disabling service check as this code executes in the remote context, without arm token.
            workspace_object = Workspace(subscription_id, resource_group, workspace_name,
                                         auth=auth, _location=location, _disable_service_check=True)
            return workspace_object


class DatasetContextManager(_CommonContextManager):
    """Manage the context for dataset download and mount actions. This class is not intended to be used directly."""

    def __init__(self, config, ignore_already_mounted_error=False):
        """Class DatasetContextManager constructor.

        :param config: The configuration passed to the context manager.
        :type config: dict

        :param ignore_already_mounted_error: Ignore mount error if something is already mounted to the same folder.
        :type ignore_already_mounted_error: bool
        """
        _log_and_print("Initialize DatasetContextManager.")
        super(self.__class__, self).__init__(config)
        self._mount_contexts = {}
        self._ignore_already_mounted_error = ignore_already_mounted_error

    def __enter__(self):
        """Download and mount datasets."""
        _log_and_print("Enter __enter__ of DatasetContextManager")
        DatasetContextManager._log_session_info()

        def is_input(config):
            return bool(config.get("DataLocation"))

        def is_output(config):
            return bool(config.get("OutputLocation"))

        for key, value in self._config.items():
            _log_and_print("Processing '{}'.".format(key))
            if "Mechanism" in value:
                _log_and_print("Mode: '{}'.".format(value["Mechanism"].lower()))
            else:
                _log_and_print("Mode is not defined")
            _log_and_print("Path on compute is specified: '{}'.".format(
                "AdditionalOptions" in value and "PathOnCompute" in value["AdditionalOptions"] and
                value["AdditionalOptions"]["PathOnCompute"]))

            if is_input(value):
                data_configuration = self.__class__._to_input_config(value)

                if DatasetContextManager._is_download(data_configuration) or \
                        DatasetContextManager._is_mount(data_configuration):
                    self._mount_or_download(key, data_configuration)
            elif is_output(value):
                from azureml.data.constants import MOUNT_MODE

                if value["Mechanism"].lower() == MOUNT_MODE:
                    self._mount_write(key, value)
            else:
                from azureml.exceptions import UserErrorException

                raise UserErrorException(
                    "Invalid configuration for input/output named {}. ".format(key) +
                    "If it is an input, please make sure the input's DataLocation property in the "
                    "Data section is created properly and if it is an output, please make sure the "
                    "output's OutputLocation property in the OutputData section is created properly."
                )
        self._mount_in_threads()
        _log_and_print("Exit __enter__ of DatasetContextManager")

    def __exit__(self, *exc_details):
        """Unmount mounted datasets."""
        _log_and_print("Enter __exit__ of DatasetContextManager")

        # exc_details is a tuple
        # if exception happens: (<class 'Exception'>, Exception('error message',), <traceback object>)
        # else: (None, None, None)
        if len(exc_details) == 3 and \
                "ModuleExceptionMessage:ModuleOutOfMemory" in getattr(exc_details[1], 'message', repr(exc_details[1])):
            _log_and_print("Skip __exit__ of DatasetContextManager because of OutOfMemory error")
        else:
            for context in self._mount_contexts.values():
                _log_and_print("Unmounting {}.".format(context.mount_point))
                context.__exit__()
                _log_and_print("Finishing unmounting {}.".format(context.mount_point))

            for key, value in self._config.items():
                from azureml.data.constants import UPLOAD_MODE

                if value["Mechanism"].lower() == UPLOAD_MODE:
                    _log_and_print("Uploading output '{}'.".format(key))
                    self._upload(key, value)

        _log_and_print("Exit __exit__ of DatasetContextManager")

    def _mount_in_threads(self):
        from multiprocessing.pool import ThreadPool
        from multiprocessing import cpu_count

        def mount(name):
            context = self._mount_contexts[name]
            _log_and_print("Mounting {} to {}.".format(name, context.mount_point))
            try:
                context.__enter__()
            except Exception as e:
                if self._ignore_already_mounted_error and os.path.ismount(context.mount_point):
                    _log_and_print("Failed to mount dataset {} to {} path"
                                   " but mount is already running for this path."
                                   " Conrinue execution.".format(name, context.mount_point))
                    del self._mount_contexts[name]  # as mount failed we don't need to try unmount
                else:
                    raise e
            _log_and_print("Mounted {} to {}.".format(name, context.mount_point))

        with ThreadPool(processes=cpu_count() * 4) as pool:
            pool.map(mount, self._mount_contexts)

    def _mount_or_download(self, name, data_configuration):
        from azureml.data._dataset import _Dataset
        from azureml.data.file_dataset import FileDataset

        target_path = os.environ.get(data_configuration.environment_variable_name) or \
            os.environ.get(data_configuration.environment_variable_name.upper())

        if data_configuration.data_location.uri and data_configuration.data_location.uri.path:
            from azureml.exceptions import UserErrorException
            from azureml._common.exceptions import AzureMLException
            _log_and_print("entering uri mode for {}".format(name))
            if data_configuration.data_location.uri.path is None:
                raise AzureMLException("run config for {} is missing uri path.".format(name))
            if self._is_download(data_configuration):
                from azureml.dataprep.rslex import Copier, PyLocationInfo, PyIfDestinationExists
                from azureml.dataprep.api._rslex_executor import get_rslex_executor

                if_destination_exists = PyIfDestinationExists.MERGE_WITH_OVERWRITE if\
                    data_configuration.overwrite else PyIfDestinationExists.FAIL
                _log_and_print("Downloading"
                               " {} to {} with overwrite as {}".
                               format(name, target_path, data_configuration.overwrite))
                get_rslex_executor()
                try:
                    Copier.copy_uri(PyLocationInfo('Local', target_path, {}),
                                    data_configuration.data_location.uri.path, if_destination_exists, "")
                except Exception as e:
                    if "InvalidUriScheme" in e.args[0] or "StreamError(NotFound)" in e.args[0]:
                        raise UserErrorException(e.args[0])
                    else:
                        raise AzureMLException(e.args[0])
                action = "Downloaded"

            elif self._is_mount(data_configuration):
                from azureml.dataprep.fuse.dprepfuse import rslex_uri_volume_mount, MountOptions

                read_write = data_configuration.options.get("ReadWrite", None) if data_configuration.options else None
                mount_options = MountOptions(read_only=read_write != "True")
                _log_and_print("Mounting"
                               " {} to {} with read_only as {}".format(name, target_path, read_write != "True"))
                try:
                    self._mount_contexts[name] = rslex_uri_volume_mount(uri=data_configuration.data_location.uri.path,
                                                                        mount_point=target_path, options=mount_options)
                except Exception as e:
                    if "InvalidUriScheme" in e.args[0] or "StreamError(NotFound)" in e.args[0]:
                        raise UserErrorException(e.args[0])
                    else:
                        raise AzureMLException(e.args[0])
                action = "Mounted"

            if data_configuration.data_location.uri.is_file:
                uri_path_parts = data_configuration.data_location.uri.path.split('/')
                if len(uri_path_parts) > 0:
                    self.__class__._update_env_var_for_single_file(
                        data_configuration.environment_variable_name,
                        "/{}".format(uri_path_parts[len(uri_path_parts) - 1]))
                    _log_and_print("updated env var for {} as a single file, ".format(name))

            _log_and_print("{} {} to {} as {}.".format(
                action, name, target_path, 'single file'
                if data_configuration.data_location.uri.is_file else 'folder'))
        elif data_configuration.data_location.dataset:
            if data_configuration.data_location.dataset.id:
                dataset = _Dataset._get_by_id(self._workspace, data_configuration.data_location.dataset.id)
            else:
                dataset = _Dataset._get_by_name(self._workspace, data_configuration.data_location.dataset.name,
                                                data_configuration.data_location.dataset.version)
            _log_and_print("Processing dataset {}".format(dataset))

            if not isinstance(dataset, FileDataset):
                from azureml.exceptions import UserErrorException

                mechanism = data_configuration.mechanism
                raise UserErrorException(
                    "Unable to {} dataset because the input {} is not a "
                    "FileDataset but instead ".format(mechanism, name) +
                    "a {}. Please make sure you pass a FileDataset.".format(type(dataset).__name__)
                )

            # only file dataset can be downloaded or mount.
            # The second part of the or statement below is to keep backwards compatibility until the execution
            # service change has been deployed to all regions.

            if self._is_download(data_configuration):
                overwrite = data_configuration.overwrite
                self.__class__._download_dataset(name, dataset, target_path, overwrite)
                action = "Downloaded"
            elif self._is_mount(data_configuration):
                self._mount_readonly(name, dataset, target_path)
                action = "Mounting"
            force_folder = data_configuration.options.get("ForceFolder", None) if data_configuration.options else None
            if force_folder != "True":
                is_single = self.__class__._try_update_env_var_for_single_file(
                    data_configuration.environment_variable_name, dataset)
            else:
                is_single = False
            _log_and_print("{} {} to {} as {}.".format(
                action, name, target_path, 'single file' if is_single else 'folder'))
        else:
            from azureml.exceptions import UserErrorException
            raise UserErrorException(
                "Unable to handle {}. because it not a valid Uri input or a valid Dataset input.".format(name)
            )

    def _mount_readonly(self, name, dataset, target_path):
        from azureml.data._dataprep_helper import dataprep_fuse
        from azureml.data.constants import _SKIP_VALIDATE_DATASETS
        from azureml.exceptions import UserErrorException

        free_space_required = self.__class__._get_required_free_space()

        _safe_mkdirs(target_path)

        _log_trace("Target path hashed path element {} mounted for readonly.".format(
            DatasetContextManager._get_hashed_path(target_path))
        )

        mount_options = dataprep_fuse().MountOptions(free_space_required=free_space_required)
        skip_validate_datasets = os.environ.get(_SKIP_VALIDATE_DATASETS, "").split(",")
        skip_validate = dataset.name in skip_validate_datasets

        try:
            context_manager = dataset.mount(mount_point=target_path,
                                            mount_options=mount_options,
                                            skip_validate=skip_validate)
            self._mount_contexts[name] = context_manager
        except UserErrorException as e:
            if self._ignore_already_mounted_error and os.path.ismount(target_path):
                _log_and_print("Failed to mount dataset {} to {} path"
                               " but mount is already running for this path."
                               " Conrinue execution.".format(name, target_path))
            else:
                raise e

    @staticmethod
    def _to_input_config(config):
        from azureml.core.runconfig import Data, DataLocation, Dataset, Uri
        data_location_json = config.get("DataLocation", None)
        dataset_json = data_location_json.get("Dataset", None) if data_location_json else None
        dataset_id = dataset_json.get("Id") if dataset_json else None
        dataset_name = dataset_json.get("Name") if dataset_json else None
        dataset_version = dataset_json.get("Version") if dataset_json else None
        dataset = Dataset(dataset_id=dataset_id, dataset_name=dataset_name, dataset_version=dataset_version)
        uri_json = data_location_json.get("Uri", None) if data_location_json else None
        path = uri_json.get("Path") if uri_json else None
        is_file = uri_json.get("IsFile") if uri_json else None
        uri = Uri(path=path, is_file=is_file) if data_location_json else None
        data_location = DataLocation(dataset=dataset, uri=uri)
        create_output_directories = config.get("CreateOutputDirectories", False)
        mechanism = config.get("Mechanism", None).lower()
        environment_variable_name = config.get("EnvironmentVariableName", None)
        path_on_compute = config.get("PathOnCompute", None)
        overwrite = config.get("Overwrite", False)
        options = config.get("Options", None)
        return Data(data_location=data_location,
                    create_output_directories=create_output_directories,
                    mechanism=mechanism,
                    environment_variable_name=environment_variable_name,
                    path_on_compute=path_on_compute,
                    overwrite=overwrite,
                    options=options)

    def _mount_write(self, name, config):
        from azureml.exceptions import UserErrorException
        from azureml._common.exceptions import AzureMLException
        from azureml.dataprep.fuse.dprepfuse import MountOptions

        destination = self._get_datastore_and_path(config)
        src_path = self.__class__._get_path_on_compute(config)
        additional_options = config["AdditionalOptions"]
        context_mount_options = additional_options.get("MountOptions", {})
        refined_destination = destination

        _log_and_print("Mounting {} to {}".format(name, src_path))
        is_single_file = self.__class__._is_single_file_output(config)
        if is_single_file:
            from azureml.dataprep.fuse.dprepfuse import rslex_uri_volume_mount

            output_uri = self._construct_datastore_uri(refined_destination[0], refined_destination[1])

            # Specify optional arguments explicitly, in case user manually change the dictionary from client and
            # overwrite these parameters
            mount_options = MountOptions(
                data_dir=None, max_size=None, free_space_required=None, default_permission=0o777,
                read_only=False, create_destination=True,
                **context_mount_options)

            try:
                self._mount_contexts[name] = rslex_uri_volume_mount(
                    uri=output_uri,
                    mount_point=src_path,
                    options=mount_options)
            except Exception as e:
                if "InvalidUriScheme" in e.args[0] or "StreamError(NotFound)" in e.args[0]:
                    raise UserErrorException(e.args[0])
                else:
                    raise AzureMLException(e.args[0])
        else:
            import uuid
            from azureml.data._dataprep_helper import dataprep_fuse
            _log_and_print("Output is not a single file")
            invocation_id = str(uuid.uuid4())

            # Specify optional arguments explicitly, in case user manually change the dictionary from client and
            # overwrite these parameters
            mount_options = dataprep_fuse().MountOptions(
                data_dir=None, max_size=None, free_space_required=None, default_permission=0o777,
                **context_mount_options
            )
            context = dataprep_fuse().mount(
                dataflow=None, files_column=None, mount_point=src_path, invocation_id=invocation_id, foreground=False,
                options=mount_options, destination=refined_destination
            )
            self._mount_contexts[name] = context

        _log_and_print("Mounted {} to {} as {}".format(name, src_path, 'single file' if is_single_file else 'folder'))
        _log_trace("Path on compute with hashed path element {} mounted for write.".format(
            DatasetContextManager._get_hashed_path(src_path)))
        self._register_output(name, refined_destination, config)

    def _construct_datastore_uri(self, datastore, relative_path):
        return "azureml://subscriptions/{}/resourcegroups/{}/workspaces/{}/datastores/{}/paths/{}".format(
            self._workspace.subscription_id,
            self._workspace.resource_group,
            self._workspace.name,
            datastore.name,
            relative_path.lstrip("/")
        )

    def _upload(self, name, config):
        from azureml.data._dataprep_helper import dataprep

        def get_upload_options():
            additional_options = config["AdditionalOptions"]
            upload_options = additional_options.get("UploadOptions", {})
            glob_options = upload_options.get("SourceGlobs", {}) or {}

            return \
                upload_options.get("Overwrite"),\
                glob_options.get("GlobPatterns"),\
                self.__class__._is_single_file_output(config)

        def upload(src_path, destination, glob_patterns, overwrite):
            engine_api = dataprep().api.engineapi.api.get_engine_api()
            dest_si = dataprep().api._datastore_helper._to_stream_info_value(destination[0], destination[1])
            glob_patterns = glob_patterns or None
            engine_api.upload_directory(
                dataprep().api.engineapi.typedefinitions.UploadDirectoryMessageArguments(
                    base_path=src_path, destination=dest_si, folder_path=src_path, glob_patterns=glob_patterns,
                    overwrite=overwrite
                )
            )

        destination = self._get_datastore_and_path(config)
        src_path = self.__class__._get_path_on_compute(config)
        overwrite, globs, is_single_file = get_upload_options()
        last_seg_path = self.__class__._get_file_name(destination[1])

        # single file output handling
        upload_destination = destination
        registered_destination = destination
        if is_single_file:
            # pass parent folder to upload function
            upload_destination = (destination[0], os.path.dirname(destination[1]))
            globs = [last_seg_path]
        try:
            # src_path will be parent folder on local compute
            # refined_destination pointing to folder on remote for both single file and folder cases
            upload(src_path, upload_destination, globs, overwrite)
        except Exception as e:
            from azureml.data.dataset_error_handling import _construct_message_and_check_exception_type, \
                _dataprep_error_handler
            message, is_dprep_exception = _construct_message_and_check_exception_type(e, None, None)
            _dataprep_error_handler(e, message, is_dprep_exception)

        self._register_output(name, registered_destination, config)

    def _register_output(self, run_name, dest, config):
        from azureml.core import Dataset

        def save_lineage(dataset, mode):
            from azureml._restclient.models import OutputDatasetLineage, DatasetIdentifier, DatasetOutputType, \
                DatasetOutputDetails, DatasetOutputMechanism
            from azureml.core import Run
            from azureml.data.constants import MOUNT_MODE

            id = dataset.id
            registered_id = dataset._registration and dataset._registration.registered_id
            version = dataset.version
            dataset_id = DatasetIdentifier(id, registered_id, version)
            output_details = DatasetOutputDetails(
                run_name,
                DatasetOutputMechanism.mount if mode.lower() == MOUNT_MODE else DatasetOutputMechanism.upload
            )
            output_lineage = OutputDatasetLineage(dataset_id, DatasetOutputType.run_output, output_details)

            try:
                run = Run.get_context()
                run._update_output_dataset_lineage([output_lineage])
            except Exception:
                module_logger.error("Failed to update output dataset lineage")

        additional_options = config["AdditionalOptions"]
        registration_options = additional_options.get("RegistrationOptions") or {}
        name = registration_options.get("Name")
        description = registration_options.get("Description")
        tags = registration_options.get("Tags")
        properties = registration_options.get("Properties")
        dataset_registration = registration_options.get("DatasetRegistrationOptions") or {}
        dataflow = dataset_registration.get("AdditionalTransformation")

        dataset = Dataset.File.from_files(dest, False)

        from copy import deepcopy
        dataset._properties = deepcopy(properties) if properties else {}
        if dataflow:
            import azureml.dataprep as dprep
            from azureml.data import TabularDataset, FileDataset
            from azureml.data._dataprep_helper import is_tabular

            transformations = dprep.Dataflow.from_json(dataflow)
            combined = dprep.Dataflow(
                transformations._engine_api,
                dataset._dataflow._get_steps() + transformations._get_steps()
            )
            dataset = TabularDataset._create(combined) if is_tabular(transformations)\
                else FileDataset._create(combined)
            _log_and_print("Outputting a tabular dataset: '{}'.".format(is_tabular(transformations)))

            has_partition_format = False
            for step in dataset._dataflow._get_steps():
                has_partition_format |= step.step_type == 'Microsoft.DPrep.AddColumnsFromPartitionFormatBlock'
            _log_and_print("Additional Transformation has partition format: '{}'.".format(has_partition_format))

        if name:
            dataset = dataset._register(self._workspace, name, description, tags, True)
        else:
            dataset._ensure_saved_internal(self._workspace)

        save_lineage(dataset, config["Mechanism"])

    def _get_datastore_and_path(self, config):
        from azureml.core import Datastore

        output_location = config["OutputLocation"]
        data_path = output_location["DataPath"]
        datastore = Datastore(self._workspace, data_path["DatastoreName"])

        return datastore, data_path["RelativePath"]

    @staticmethod
    def _is_single_file_output(config):
        # IsSingleFile mount options from 1p customers for single file output
        # default to false
        context_mount_options = config.get("AdditionalOptions", {}).get("MountOptions")
        is_single_file = "False"
        if context_mount_options is not None:
            is_single_file = context_mount_options.get("IsSingleFile", "False")

        return is_single_file == "True"

    @staticmethod
    def _get_file_name(relative_path):
        uri_path_parts = relative_path.split('/')
        if len(uri_path_parts) > 0:
            return uri_path_parts[len(uri_path_parts) - 1]

        return ""

    @staticmethod
    def _get_path_on_compute(config):
        additional_options = config["AdditionalOptions"]
        return additional_options["PathOnCompute"]

    @staticmethod
    def _get_datastores_of_dataset(in_ds):
        """Get data stores from file dataset."""
        steps = in_ds._dataflow._get_steps()
        if steps[0].step_type == "Microsoft.DPrep.GetDatastoreFilesBlock":
            return steps[0].arguments["datastores"]
        return None

    @staticmethod
    def _is_download(data_configuration):
        from azureml.data.constants import DOWNLOAD_MODE
        return data_configuration.mechanism.lower() == DOWNLOAD_MODE

    @staticmethod
    def _is_mount(data_configuration):
        from azureml.data.constants import MOUNT_MODE
        return data_configuration.mechanism.lower() == MOUNT_MODE

    @staticmethod
    def _update_env_var_for_single_file(env_name, path):
        os.environ[env_name] = os.environ[env_name].rstrip('/\\')
        os.environ[env_name] += path

        # the line below is here to keep backwards compatibility with data reference usage
        os.environ['AZUREML_DATAREFERENCE_{}'.format(env_name)] = os.environ[env_name]
        # the line below is to make sure run.input_datasets return the correct path
        os.environ[env_name.upper()] = os.environ[env_name]

    @staticmethod
    def _try_update_env_var_for_single_file(env_name, dataset):
        if not DatasetContextManager._is_single_file_no_transform(dataset):
            return False
        DatasetContextManager._update_env_var_for_single_file(env_name, dataset.to_path()[0])
        return True

    @staticmethod
    def _update_env_var_if_datareference_exists(dataset_name, datareference_path):
        os.environ[dataset_name] = datareference_path
        # the line below is here to keep backwards compatibility with data reference usage
        os.environ["AZUREML_DATAREFERENCE_{}".format(dataset_name.lower())] = datareference_path
        # the line below is to make sure run.input_datasets return the correct path
        os.environ[dataset_name.upper()] = datareference_path

    @staticmethod
    def _is_single_file_no_transform(dataset):
        steps = dataset._dataflow._get_steps()

        # if there is more than one step, we are going to naively assume that the resulting number of files is
        # nondeterministic
        if len(steps) > 1:
            return False

        first_step = steps[0]
        argument = first_step.arguments
        try:
            argument = argument.to_pod()
        except AttributeError:
            pass

        from azureml.data._dataset import _get_path_from_step
        original_path = _get_path_from_step(first_step.step_type, argument)
        if not original_path:
            return False

        if http_pattern.match(original_path):
            url = urlparse(original_path)
            original_path = url.path

        temp_column = "Temp Portable Path"
        from azureml.data._dataprep_helper import dataprep
        dataflow = dataset._dataflow.take(1).add_column(
            dataprep().api.functions.get_portable_path(dataprep().api.expressions.col("Path")), temp_column, "Path")
        path = dataflow._to_pyrecords()[0][temp_column]

        return path.strip("/").endswith(original_path.replace("\\", "/").strip("/"))

    @staticmethod
    def _get_required_free_space():
        # AZ_BATCH_RESERVED_DISK_SPACE_BYTES is set in BatchAI which is the minimum required disk space
        # before the node will become unusable. Adding 100MB on top of that to be safe
        free_space_required = _free_space_required
        bai_reserved_disk_space = os.environ.get("AZ_BATCH_RESERVED_DISK_SPACE_BYTES")
        if bai_reserved_disk_space:
            free_space_required = int(bai_reserved_disk_space) + _bai_disk_buffer
        return free_space_required

    @staticmethod
    def _download_dataset(name, dataset, target_path, overwrite):
        _log_and_print("Downloading {} to {}. Overwrite is set to {}".format(name, target_path, overwrite))
        dataset.download(target_path=target_path, overwrite=overwrite)

    @staticmethod
    def _log_session_info():
        from pkg_resources import get_distribution
        try:
            core_version = get_distribution('azureml-core').version
        except Exception:
            # this should never fail as the code path is not hit for CLI usage, but just to be safe
            from azureml.core import VERSION as core_version
        try:
            dataprep_version = get_distribution('azureml-dataprep').version
        except Exception:
            try:
                from azureml.dataprep import __version__ as dataprep_version
            except Exception:
                # it is possible to have no azureml-dataprep installed
                dataprep_version = ''
        try:
            from azureml._base_sdk_common import _ClientSessionId as session_id
        except Exception:
            session_id = None
        run_id = os.environ.get('AZUREML_RUN_ID')
        _log_and_print("SDK version: azureml-core=={} azureml-dataprep=={}. Session id: {}. Run id: {}.".format(
            core_version,
            dataprep_version,
            session_id if session_id else '(telemetry disabled)',
            run_id
        ))

    @staticmethod
    def _get_hashed_path(path):
        import hashlib

        path_elems = os.path.normpath(path).split(os.path.sep)
        hashed_path_elems = list(map(lambda p: hashlib.md5(bytes(p, encoding='utf-8')).hexdigest(), path_elems))
        return os.path.join(*hashed_path_elems)


class DatastoreContextManager(_CommonContextManager):
    """Manage the context for datastore upload and download actions. This class is not intended to be used directly."""

    def __init__(self, config):
        """Class DatastoreContextManager constructor.

        :param config: The configuration passed to the context manager.
        :type config: dict
        """
        module_logger.debug("Initialize DatastoreContextManager.")
        super(self.__class__, self).__init__(config)

    def __enter__(self):
        """Download files for datastore.

        :return:
        """
        module_logger.debug("Enter __enter__ function of datastore cmgr")
        from azureml.core import Datastore, Dataset
        for key, value in self._config.items():
            df_config, _ = self._to_data_reference_config(value)
            if self._is_upload(df_config):
                if df_config.path_on_compute:
                    dir_to_create = os.path.normpath(os.path.dirname(df_config.path_on_compute))
                    if dir_to_create:
                        _safe_mkdirs(dir_to_create)
            else:
                target_path = df_config.data_store_name
                if df_config.path_on_compute:
                    target_path = os.path.join(df_config.data_store_name, df_config.path_on_compute)
                    # The target_path is always set using the data store name with no way
                    # for the user to overwrite this behavior. The user might attempt to use ../ in
                    # the path on compute as a solution but this throws an exception
                    # because the path is not normalized.
                    # Normalizing the path to allow the user to use up-level references.
                    target_path = os.path.normpath(target_path)
                if self._is_download(df_config):
                    self._validate_config(df_config, key)
                    ds = Datastore(workspace=self._workspace, name=df_config.data_store_name)
                    if self._is_datastore_adlsgen1(ds):
                        _log_and_print("AzureDataLake Gen1 used as Datastore for download")
                        if df_config.path_on_data_store is None:
                            df_config.path_on_data_store = ""
                        Dataset.File.from_files((ds, df_config.path_on_data_store)).download(
                            os.path.join(target_path, df_config.path_on_data_store),
                            overwrite=df_config.overwrite)
                    else:
                        count = ds.download(
                            target_path=target_path,
                            prefix=df_config.path_on_data_store,
                            overwrite=df_config.overwrite)
                        if count == 0:
                            import warnings
                            warnings.warn("Downloaded 0 files from datastore {} with path {}.".format(
                                ds.name, df_config.path_on_data_store
                            ))
                else:
                    _safe_mkdirs(target_path)

        module_logger.debug("Exit __enter__ function of datastore cmgr")

    def __exit__(self, *exc_details):
        """Upload files for datastore.

        :param exc_details:
        :return:
        """
        from azureml.core.datastore import Datastore
        from azureml.data._dataprep_helper import dataprep

        module_logger.debug("Enter __exit__ function of datastore cmgr")
        for key, value in self._config.items():
            df_config, force_read = self._to_data_reference_config(value)
            if self._is_upload(df_config):
                self._validate_config(df_config, key)
                ds = Datastore(workspace=self._workspace, name=df_config.data_store_name)
                if os.path.isdir(df_config.path_on_compute):
                    if self._is_datastore_adlsgen1(ds):
                        module_logger.debug("AzureDataLake Gen1 used as Datastore for upload dir.")
                        dataprep().api.engineapi.api.get_engine_api().upload_directory(
                            dataprep().api.engineapi.typedefinitions.UploadDirectoryMessageArguments(
                                base_path=df_config.path_on_compute,
                                folder_path=df_config.path_on_compute,
                                destination=dataprep().api._datastore_helper._to_stream_info_value(
                                    ds,
                                    df_config.path_on_data_store),
                                force_read=force_read,
                                overwrite=df_config.overwrite,
                                concurrent_task_count=1))
                    else:
                        ds.upload(
                            src_dir=df_config.path_on_compute,
                            target_path=df_config.path_on_data_store,
                            overwrite=df_config.overwrite)
                elif os.path.isfile(df_config.path_on_compute):
                    if self._is_datastore_adlsgen1(ds):
                        module_logger.debug("AzureDataLake Gen1 used as Datastore for upload file.")
                        dataprep().api.engineapi.api.get_engine_api().upload_file(
                            dataprep().api.engineapi.typedefinitions.UploadFileMessageArguments(
                                base_path=os.path.dirname(df_config.path_on_compute),
                                local_path=df_config.path_on_compute,
                                destination=dataprep().api._datastore_helper._to_stream_info_value(
                                    ds,
                                    df_config.path_on_data_store),
                                force_read=force_read,
                                overwrite=df_config.overwrite))
                    else:
                        ds.upload_files(
                            files=[df_config.path_on_compute],
                            target_path=df_config.path_on_data_store,
                            overwrite=df_config.overwrite)
        module_logger.debug("Exit __exit__ function of datastore cmgr")

    def _validate_config(self, data_reference, key):
        from azureml.exceptions import UserErrorException
        if not data_reference.data_store_name:
            raise UserErrorException("DataReference {} misses the datastore name".format(key))
        if self._is_upload(data_reference) and not data_reference.path_on_compute:
            raise UserErrorException("DataReference {} misses the relative path on the compute".format(key))

    @staticmethod
    def _to_data_reference_config(config):
        from azureml.core.runconfig import DataReferenceConfiguration
        from azureml.data.constants import MOUNT_MODE
        return DataReferenceConfiguration(
            datastore_name=config.get("DataStoreName", None),
            mode=config.get("Mode", MOUNT_MODE).lower(),
            path_on_datastore=config.get("PathOnDataStore", None),
            path_on_compute=config.get("PathOnCompute", None),
            overwrite=config.get("Overwrite", False)), config.get("ForceRead", False)

    @staticmethod
    def _is_download(data_reference):
        from azureml.data.constants import DOWNLOAD_MODE
        return data_reference.mode.lower() == DOWNLOAD_MODE

    @staticmethod
    def _is_upload(data_reference):
        from azureml.data.constants import UPLOAD_MODE
        return data_reference.mode.lower() == UPLOAD_MODE

    @staticmethod
    def _is_datastore_adlsgen1(data_store):
        # https://docs.microsoft.com/en-us/python/api/azureml-core/azureml.data.azure_data_lake_datastore.abstractadlsdatastore?view=azure-ml-py
        return data_store.datastore_type.lower() == "azuredatalake"
