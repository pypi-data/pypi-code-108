# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains functions for labeled datasets that are still under development.

Labeled datasets are a type of TabularDataset that are created from data labeling projects.
For more information about data labeling projects, please refer to
[Create a data labeling project and export
labels](https://docs.microsoft.com/azure/machine-learning/how-to-create-labeling-projects).

Unlike a regular TabularDataset, a labeled dataset has the ability to be mounted and downloaded.
You can also convert a labeled dataset to a pandas DataFrame using the `to_pandas_dataframe` method or to a
torchvision dataset using the `to_torchvision()` method.

"""

from enum import Enum

from azureml._base_sdk_common._docstring_wrapper import experimental
from azureml.core.dataset import Dataset
from azureml._restclient.models.dataset_request_dto import DatasetRequestDto
from azureml._restclient.models.data_path_dto import DataPathDto
from azureml._restclient.models.general_section import GeneralSection
from azureml._restclient.models.data_source_properties import DataSourceProperties
from azureml._restclient.models.json_lines_section import JsonLinesSection
from azureml._restclient.models.purpose_section import PurposeSection

from azureml.data import TabularDataset, FileDataset
from azureml.data.constants import _PUBLIC_API, _DATASET_PROP_LABEL, _DATASET_PROP_IMAGE, _IMAGE_URL_COLUMN_NAME, \
    _LABEL_COLUMN_NAME, _IMAGE_URL_COLUMN
from azureml.data.dataset_error_handling import _try_execute, _validate_has_data
from azureml.data.dataset_factory import _validate_and_normalize_path
from azureml.data._dataprep_helper import get_dataflow_for_execution
from azureml.data._dataset_rest_helper import _saved_dataset_dto_to_dataset, _restclient, _custom_headers
from azureml.data._loggerfactory import track, _LoggerFactory
from azureml.exceptions import UserErrorException

_logger = None


def _get_logger():
    global _logger
    if _logger is None:
        _logger = _LoggerFactory.get_logger(__name__)
    return _logger


class FileHandlingOption(Enum):
    """Defines options for how to handle file streams in a dataset when converting to a pandas dataframe."""

    DOWNLOAD = 0
    MOUNT = 1
    NONE = 2


class LabeledDatasetTask(Enum):
    """Defines labeling task types for use with labeled datasets."""

    IMAGE_CLASSIFICATION = 'ImageClassification'
    IMAGE_INSTANCE_SEGMENTATION = 'InstanceSegmentation'
    IMAGE_MULTI_LABEL_CLASSIFICATION = 'ImageMultiLabelClassification'
    OBJECT_DETECTION = 'ObjectDetection'


class _LabeledDatasetFactory:
    """Contains methods to create tabular dataset with label trait for Azure Machine Learning."""

    @staticmethod
    @track(_get_logger, custom_dimensions={'app_name': 'TabularDataset'}, activity_type=_PUBLIC_API)
    def from_json_lines(path, task, validate=True):
        """Create a TabularDataset with label trait for the specified labeling task from a JSON Lines file.

        :param path: The path to the source files.
        :type path: (azureml.core.Datastore, str) or List[(azureml.core.Datastore, str)]
        :param task: The labeling task type. Value must be one of LabeledDatasetTask.IMAGE_CLASSIFICATION,
            LabeledDatasetTask.IMAGE_INSTANCE_SEGMENTATION, LabeledDatasetTask.IMAGE_MULTI_LABEL_CLASSIFICATION,
            or LabeledDatasetTask.OBJECT_DETECTION.
        :type task: azureml.contrib.dataset.LabeledDatasetTask
        :param validate: Boolean to validate if data can be loaded from the returned dataset. Defaults to True.
            Validation requires that the data source is accessible from the current compute.
        :type validate: bool
        :return: Returns a :class:`azureml.data.TabularDataset` object.
        :rtype: azureml.data.TabularDataset
        """
        path = _validate_and_normalize_path(path)
        if len(path) > 1:
            raise UserErrorException('Json lines files must be from a single path.')
        data_path = path[0]
        if isinstance(data_path, str):
            raise UserErrorException('Json lines files must be from a Datastore.')
        store = data_path._datastore
        workspace = store.workspace
        request_dto = DatasetRequestDto(
            data_path=DataPathDto(store.name, data_path.path_on_datastore),
            general=GeneralSection(source_properties_override=DataSourceProperties(data_source_type='JSONLines')),
            json_lines=JsonLinesSection(),
            purpose=PurposeSection(task))
        dto = _restclient(workspace).dataset.ensure_saved_from_request(
            workspace.subscription_id,
            workspace.resource_group,
            workspace.name,
            request=request_dto,
            custom_headers=_custom_headers)
        dataset = _saved_dataset_dto_to_dataset(workspace, dto)
        dataflow = dataset._dataflow
        if validate:
            _validate_has_data(dataflow, 'Cannot load any data from the specified \
            path. ' + 'Make sure the path is accessible and contains data.')
        return dataset


Dataset._Labeled = _LabeledDatasetFactory
Dataset.Labeled = _LabeledDatasetFactory


@property
@track(_get_logger, custom_dimensions={'app_name': 'TabularDataset'}, activity_type=_PUBLIC_API)
def _label(self):
    """Return the label column name and type.

    :return: A dictionary containing the name of the column consisting of the labels, and the label type.
    :rtype: dict[str]
    """
    import warnings

    warnings.warn("azureml-contrib-dataset package will be deprecated soon,"
                  " please use the TabularDataset in azureml-core", DeprecationWarning)
    return self._properties.get(_DATASET_PROP_LABEL, None)


@property
@track(_get_logger, custom_dimensions={'app_name': 'TabularDataset'}, activity_type=_PUBLIC_API)
def _image(self):
    """Return the image location column name and image details column name.

    :return: A dictionary containing the name of the column consisting of the image urls, and
        the name of the column consisting of the image details.
    :rtype: dict[str]
    """
    import warnings

    warnings.warn("azureml-contrib-dataset package will be deprecated soon,"
                  " please use the TabularDataset in azureml-core", DeprecationWarning)
    return self._properties.get(_DATASET_PROP_IMAGE, None)


@track(_get_logger, custom_dimensions={'app_name': 'TabularDataset'}, activity_type=_PUBLIC_API)
def _download(self, target_path=None, overwrite=False, **kwargs):
    """Download file streams defined by the dataset as local files.

    :param target_path: The local directory to download the files to. If None, the data will be downloaded
        into a temporary directory.
    :type target_path: str
    :param overwrite: Indicates whether to overwrite existing files. The default is False. Existing files will
        be overwritten if overwrite is set to True; otherwise an exception will be raised.
    :type overwrite: bool
    :return: Returns an array of file paths for each file downloaded.
    :rtype: numpy.ndarray
    """
    import warnings

    warnings.warn("azureml-contrib-dataset package will be deprecated soon,"
                  " please use the TabularDataset in azureml-core", DeprecationWarning)
    path_column = kwargs.get("stream_column", None)

    if path_column is None:
        if self.image is None:
            raise UserErrorException('Cannot download files unless dataset has an appropriate trait set. '
                                     'Currently supported traits for download: image')

        path_column = self.image[_IMAGE_URL_COLUMN_NAME]

    dataflow = get_dataflow_for_execution(self._dataflow, 'download', 'TabularDataset')
    if not path_column == 'Path':
        dataflow = dataflow.drop_columns('Path').rename_columns({path_column: 'Path'})

    file_ds = FileDataset._create(dataflow, self._properties, telemetry_info=self._telemetry_info)
    try:
        return file_ds.download(target_path, overwrite)
    except UserErrorException:
        raise
    except Exception:
        raise UserErrorException('Cannot download dataset. Please make sure path_column contains file streams.')


@track(_get_logger, custom_dimensions={'app_name': 'TabularDataset'}, activity_type=_PUBLIC_API)
def _mount(self, mount_point=None, **kwargs):
    """Create a context manager for mounting file streams defined by the dataset as local files.

    .. remarks::

        A context manager will be returned to manage the lifecycle of the mount. To mount, you will need to
        enter the context manager and to unmount, exit from the context manager.

        Mount is only supported on Unix or Unix-like operating systems with the native package libfuse installed.
        If you are running inside a docker container, the docker container must be started with the `--privileged`
        flag or started with `--cap-add SYS_ADMIN --device /dev/fuse`.

        .. code-block:: python

            datastore = Datastore.get(workspace, 'workspaceblobstore')
            dataset = Dataset.Tabular.from_delimited_files((datastore, 'weather/2018/*.csv'))

            with dataset.mount() as mount_context:
                # list top level mounted files and folders in the dataset
                os.listdir(mount_context.mount_point)

            # You can also use the start and stop methods
            mount_context = dataset.mount()
            mount_context.start()  # this will mount the file streams
            mount_context.stop()  # this will unmount the file streams

    :param mount_point: The local directory to mount the files to. If None, the data will be mounted into a
        temporary directory, which you can find by calling the `MountContext.mount_point` instance method.
    :type mount_point: str
    :return: Returns a context manager for managing the lifecycle of the mount.
    :rtype: azureml.dataprep.fuse.daemon.MountContext
    """
    import warnings

    warnings.warn("azureml-contrib-dataset package will be deprecated soon,"
                  " please use the TabularDataset in azureml-core", DeprecationWarning)
    path_column = kwargs.get("stream_column", None)

    if path_column is None:
        if self.image is None:
            raise UserErrorException('Cannot mount files unless dataset has an appropriate trait set. '
                                     'Currently supported traits for mount: image')
        path_column = self.image[_IMAGE_URL_COLUMN_NAME]

    dataflow = get_dataflow_for_execution(self._dataflow, 'mount', 'TabularDataset')
    if not path_column == 'Path':
        dataflow = dataflow.drop_columns('Path').rename_columns({path_column: 'Path'})

    file_ds = FileDataset._create(dataflow, self._properties, telemetry_info=self._telemetry_info)
    try:
        return file_ds.mount(mount_point)
    except UserErrorException:
        raise
    except Exception as e:
        raise UserErrorException('Cannot mount dataset. ' + str(e))


@track(_get_logger, custom_dimensions={'app_name': 'TabularDataset'}, activity_type=_PUBLIC_API)
def _keep_columns(self, columns, validate=False):
    """Keep the specified columns and drop all others from the dataset.

    If a timeseries, label, or image column is dropped, the corresponding capabilities will be dropped
    for the returned dataset as well.

    :param columns: The name or a list of names for the columns to keep.
    :type columns: str or builtin.list[str]
    :param validate: Indicates whether to validate if data can be loaded from the returned dataset.
        The default is False. Validation requires that the data source is accessible from current compute.
    :type validate: bool
    :return: Returns a new TabularDataset object with only the specified columns kept.
    :rtype: azureml.data.TabularDataset
    """
    import warnings

    warnings.warn("azureml-contrib-dataset package will be deprecated soon,"
                  " please use the TabularDataset in azureml-core", DeprecationWarning)
    dataflow = self._dataflow.keep_columns(columns, validate_column_exists=False)

    if validate:
        _validate_has_data(dataflow,
                           ('Cannot load any data from the dataset with only columns {} \
                           kept. ' + 'Make sure the specified columns exist in the current dataset.')
                           .format(columns if isinstance(columns, list) else [columns]))

    dataset = TabularDataset._create(dataflow, self._properties, telemetry_info=self._telemetry_info)

    ts_cols = self.timestamp_columns
    label_column = self.label[_LABEL_COLUMN_NAME] if self.label is not None else None
    image_column = self.image[_IMAGE_URL_COLUMN_NAME] if self.image is not None else None
    trait_dropped = None

    if isinstance(columns, str):
        columns = [columns]

    if ts_cols[0] is not None:
        if ts_cols[0] not in columns:
            dataset = dataset.with_timestamp_columns(None)
            trait_dropped = 'fine_grain_timestamp, coarse_grain_timestamp'
        elif ts_cols[1] is not None and ts_cols[1] not in columns:
            dataset = dataset.with_timestamp_columns(ts_cols[0])
            trait_dropped = 'coarse_grain_timestamp'
    if label_column is not None and label_column not in columns:
        trait_dropped = 'label'
        del dataset._properties[_DATASET_PROP_LABEL]
    if image_column is not None and image_column not in columns:
        trait_dropped = 'image'
        del dataset._properties[_DATASET_PROP_IMAGE]

    if trait_dropped is not None:
        _get_logger().info('Dropping trait ({0}) on dataset (id={1}) during keep_columns.'
                           .format(trait_dropped, self.id))

    return dataset


@track(_get_logger, custom_dimensions={'app_name': 'TabularDataset'}, activity_type=_PUBLIC_API)
def _drop_columns(self, columns):
    """Drop the specified columns from the dataset.

    If a timeseries, label, or image column is dropped, the corresponding capabilities will be dropped
    for the returned dataset as well.

    :param columns: The name or a list of names for the columns to drop.
    :type columns: str or builtin.list[str]
    :return: Returns a new TabularDataset object with the specified columns dropped.
    :rtype: azureml.data.TabularDataset
    """
    import warnings

    warnings.warn("azureml-contrib-dataset package will be deprecated soon,"
                  " please use the TabularDataset in azureml-core", DeprecationWarning)
    dataset = TabularDataset._create(
        self._dataflow.drop_columns(columns), self._properties, telemetry_info=self._telemetry_info)

    ts_cols = self.timestamp_columns
    label_column = self.label[_LABEL_COLUMN_NAME] if self.label is not None else None
    image_column = self.image[_IMAGE_URL_COLUMN_NAME] if self.image is not None else None
    trait_dropped = None

    if isinstance(columns, str):
        columns = [columns]

    if ts_cols[0] is not None:
        if ts_cols[0] in columns:
            dataset = dataset.with_timestamp_columns(None)
            trait_dropped = 'fine_grain_timestamp, coarse_grain_timestamp'
        elif ts_cols[1] is not None and ts_cols[1] in columns:
            dataset = dataset.with_timestamp_columns(ts_cols[0])
            trait_dropped = 'coarse_grain_timestamp'
    if label_column is not None and label_column in columns:
        trait_dropped = 'label'
        del dataset._properties[_DATASET_PROP_LABEL]
    if image_column is not None and image_column in columns:
        trait_dropped = 'image'
        del dataset._properties[_DATASET_PROP_IMAGE]

    if trait_dropped is not None:
        _get_logger().info('Dropping trait ({0}) on dataset (id={1}) during drop_columns.'
                           .format(trait_dropped, self.id))

    return dataset


@track(_get_logger, custom_dimensions={'app_name': 'TabularDataset'}, activity_type=_PUBLIC_API)
def _to_torchvision(self):
    """Convert a labeled dataset to a Torchvision dataset depending on the label trait.

    :return: Returns a custom Torchvision dataset depending on the type of the label trait.
    :rtype: typing.Union[azureml.contrib.dataset._torchvision_helper._TorchvisionObjectDetectionDataset,
            azureml.contrib.dataset._torchvision_helper._TorchvisionImageClassificationDataset]
    """
    import warnings

    warnings.warn("azureml-contrib-dataset package will be deprecated soon,"
                  " please use the TabularDataset in azureml-core", DeprecationWarning)
    if self.label is None or self.label['type'] is None:
        raise UserErrorException('Cannot perform torchvision conversion on dataset without labeled columns defined')

    label_type = self.label['type']
    image_column = self.image[_IMAGE_URL_COLUMN_NAME]

    if label_type != 'ObjectDetection' and label_type != 'Classification' and label_type != 'MultiLabelClassification':
        raise UserErrorException('Cannot perform torchvision conversion as the label trait type {} is unsupported.'
                                 .format(label_type))
    try:
        from azureml.contrib.dataset._torchvision_helper import _TorchvisionObjectDetectionDataset, \
            _TorchvisionImageClassificationDataset
    except Exception:
        raise UserErrorException('Error importing Torch. '
                                 'Please make sure it is installed and try again.')
    import torchvision.transforms as transforms
    import uuid
    invocation_id = str(uuid.uuid4())
    if label_type == 'ObjectDetection':
        # Convert the image to a tensor
        transform = transforms.Compose([transforms.ToTensor()])
        dataflow = get_dataflow_for_execution(self._dataflow, 'to_torchvision', 'TabularDataset',
                                              invocation_id=invocation_id,
                                              label_type='ObjectDetection')
        return _TorchvisionObjectDetectionDataset(dataflow, image_column, transform)
    if label_type == 'Classification' or label_type == 'MultiLabelClassification':
        # Convert the image to a tensor and normalize the color channels to [-1,1]
        transform = transforms.Compose(
            [transforms.ToTensor(),
                transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])
        dataflow = get_dataflow_for_execution(self._dataflow, 'to_torchvision', 'TabularDataset',
                                              invocation_id=invocation_id,
                                              label_type='Classification')
        return _TorchvisionImageClassificationDataset(dataflow, image_column, transform)


@experimental
@track(_get_logger, custom_dimensions={'app_name': 'TabularDataset'}, activity_type=_PUBLIC_API)
def _file_metadata(self, col):
    """Get file metadata expression by specifying the metadata column name.

    Supported file metadata columns are Size, LastModifiedTime, CreationTime, Extension and CanSeek

    :param col: Name of column
    :type col: str
    :return: Returns an expression that retrieves the value in the specified column.
    :rtype: azureml.dataprep.api.expression.RecordFieldExpression
    """
    import warnings

    warnings.warn("azureml-contrib-dataset package will be deprecated soon,"
                  " please use the TabularDataset in azureml-core", DeprecationWarning)
    from azureml.dataprep.api.functions import get_stream_properties
    dataflow = self._dataflow
    image_url_column = (self._properties[_DATASET_PROP_IMAGE].get(_IMAGE_URL_COLUMN_NAME)
                        if self._properties.get(_DATASET_PROP_IMAGE) else None)
    if not image_url_column:
        image_url_column = (self._properties[_DATASET_PROP_IMAGE].get(_IMAGE_URL_COLUMN)
                            if self._properties.get(_DATASET_PROP_IMAGE) else None)
    if image_url_column:
        return get_stream_properties(dataflow[image_url_column])[col]


@experimental
@track(_get_logger, custom_dimensions={'app_name': 'TabularDataset'}, activity_type=_PUBLIC_API)
def _filter(self, expression):
    """
    Filter the data, leaving only the records that match the specified expression.

    .. remarks::

        Expressions are started by indexing the Dataset with the name of a column. They support a variety of
            functions and operators and can be combined using logical operators. The resulting expression will be
            lazily evaluated for each record when a data pull occurs and not where it is defined.

        .. code-block:: python

            dataset['label'].contains('dog')
            dataset['image_details']['format'] == 'jpg'
            dataset.file_metadata('Size') > 10000

    :param expression: The expression to evaluate.
    :type expression: any
    :return: The modified dataset (unregistered).
    :rtype: azureml.data.TabularDataset
    """
    import warnings

    warnings.warn("azureml-contrib-dataset package will be deprecated soon,"
                  " please use the TabularDataset in azureml-core", DeprecationWarning)
    dataflow = self._dataflow
    dataflow = dataflow.filter(expression)
    return TabularDataset._create(dataflow, self._properties, telemetry_info=self._telemetry_info)


def _set_pandas_dataframe_index(df: 'pandas.DataFrame', timestamp_column: str):
    return df.set_index(timestamp_column, drop=False) \
        if timestamp_column is not None and df.empty is False else df


@track(_get_logger, custom_dimensions={'app_name': 'TabularDataset'}, activity_type=_PUBLIC_API)
def _labeled_ds_to_pandas_dataframe(self,
                                    file_handling_option=FileHandlingOption.NONE,
                                    target_path=None,
                                    overwrite_download=False):
    """Load all records from the dataset into a pandas DataFrame.

    :param file_handling_option: This argument only applies to TabularDatasets with the label trait, otherwise
        it is ignored. The valid options are FileHandlingOption.NONE, FileHandlingOption.DOWNLOAD (download the
        files locally), or FileHandlingOption.MOUNT (mount the files to a local path). Default is NONE.
    :type file_handling_option: azureml.contrib.dataset.FileHandlingOption
    :param target_path: This argument only applies to TabularDatasets with the label trait. The `target_path` is
        where the image files will be downloaded or mounted to. If `file_handling_option` is set to DOWNLOAD or
        MOUNT with no `target_path` provided, a temporary directory will be used.
    :type target_path: str
    :param overwrite_download: This argument only applies if file_handling_option is DOWNLOAD to indicate whether
        to overwrite existing files. The default is False. Existing files will be overwritten if overwrite_download
        is set to True; otherwise an exception will be raised.
    :type overwrite_download: bool
    :return: Returns a pandas DataFrame.
    :rtype: pandas.DataFrame
    """
    import warnings

    warnings.warn("azureml-contrib-dataset package will be deprecated soon,"
                  " please use the TabularDataset in azureml-core", DeprecationWarning)
    fine_grain_timestamp = self.timestamp_columns[0]
    if self.image is None:
        dflow = get_dataflow_for_execution(self._dataflow, 'to_pandas_dataframe', 'TabularDataset')
        df = _try_execute(dflow.to_pandas_dataframe,
                          'to_pandas_dataframe',
                          None if self.id is None else {'id': self.id, 'name': self.name, 'version': self.version})
        return _set_pandas_dataframe_index(df=df, timestamp_column=fine_grain_timestamp)

    if file_handling_option == FileHandlingOption.NONE:
        dflow = get_dataflow_for_execution(self._dataflow, 'to_pandas_dataframe', 'TabularDataset')
        df = _try_execute(dflow.to_pandas_dataframe,
                          'to_pandas_dataframe',
                          None if self.id is None else {'id': self.id, 'name': self.name, 'version': self.version},
                          extended_types=True)
        return _set_pandas_dataframe_index(df=df, timestamp_column=fine_grain_timestamp)

    path_column = self.image[_IMAGE_URL_COLUMN_NAME]

    if file_handling_option == FileHandlingOption.DOWNLOAD:
        import azureml.dataprep as dprep
        import pandas

        try:
            np_paths = self.download(target_path, overwrite_download)
        except UserErrorException as e:
            if "Set overwrite=True" in e.args[0]:
                raise UserErrorException(e.args[0].replace("Set overwrite=True", "Set overwrite_download=True"))
            raise
        dflow = dprep.read_pandas_dataframe(df=pandas.DataFrame(np_paths), in_memory=True) \
                     .append_columns([self._dataflow]) \
                     .drop_columns([path_column]) \
                     .rename_columns({'0': path_column})
        new_dflow = get_dataflow_for_execution(dflow,
                                               'to_pandas_dataframe',
                                               'TabularDataset',
                                               file_handling_option='Download')
        df = _try_execute(new_dflow.to_pandas_dataframe,
                          'to_pandas_dataframe',
                          None if self.id is None else {'id': self.id, 'name': self.name, 'version': self.version},
                          extended_types=True)
        return _set_pandas_dataframe_index(df=df, timestamp_column=fine_grain_timestamp)

    if file_handling_option == FileHandlingOption.MOUNT:
        import azureml.dataprep as dprep
        import pandas
        from azureml.dataprep.api.expressions import ValueExpression
        from azureml.dataprep.api.functions import get_portable_path

        mount_context = self.mount(target_path)
        mount_point = mount_context.mount_point
        mount_context.start()
        dflow = get_dataflow_for_execution(self._dataflow,
                                           'to_pandas_dataframe',
                                           'TabularDataset',
                                           file_handling_option='Mount')
        dflow = dflow.add_column(new_column_name='mounted_path',
                                 prior_column=path_column,
                                 expression=ValueExpression(mount_point) + get_portable_path(dflow[path_column])) \
                     .drop_columns([path_column]) \
                     .rename_columns({'mounted_path': path_column})
        df = _try_execute(dflow.to_pandas_dataframe,
                          'to_pandas_dataframe',
                          None if self.id is None else {'id': self.id, 'name': self.name, 'version': self.version},
                          extended_types=True)
        return _set_pandas_dataframe_index(df=df, timestamp_column=fine_grain_timestamp)

    raise UserErrorException('Unrecognized file_handling_option: ' + file_handling_option)


TabularDataset.label = _label
TabularDataset.image = _image
TabularDataset.download = _download
TabularDataset.mount = _mount
TabularDataset.keep_columns = _keep_columns
TabularDataset.drop_columns = _drop_columns
TabularDataset.to_torchvision = _to_torchvision
TabularDataset._to_torchvision = _to_torchvision
TabularDataset.to_pandas_dataframe = _labeled_ds_to_pandas_dataframe
TabularDataset.filter = _filter
TabularDataset.file_metadata = _file_metadata
