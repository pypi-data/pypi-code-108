__all__ = [
    "DataConnection",
    "S3Connection",
    "ConnectionAsset",
    "S3Location",
    "FSLocation",
    "AssetLocation",
    "CP4DAssetLocation",
    "WMLSAssetLocation",
    "WSDAssetLocation",
    "CloudAssetLocation",
    "DeploymentOutputAssetLocation",
    "NFSConnection",
    "NFSLocation",
    'ConnectionAssetLocation',
    "DatabaseLocation",
    "ContainerLocation"
]

#  (C) Copyright IBM Corp. 2021.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import io
import os
import uuid
import copy
from copy import deepcopy
from typing import Union, Tuple, List, TYPE_CHECKING, Optional
from warnings import warn

from ibm_boto3 import resource
from ibm_botocore.client import ClientError
from pandas import DataFrame
import ibm_watson_machine_learning._wrappers.requests as requests

from ibm_watson_machine_learning.utils.autoai.enums import PredictionType, DataConnectionTypes
from ibm_watson_machine_learning.utils.autoai.errors import (
    MissingAutoPipelinesParameters, UseWMLClient, MissingCOSStudioConnection, MissingProjectLib,
    HoldoutSplitNotSupported, InvalidCOSCredentials, MissingLocalAsset, InvalidIdType, NotWSDEnvironment,
    NotExistingCOSResource, InvalidDataAsset, CannotReadSavedRemoteDataBeforeFit, NoAutomatedHoldoutSplit
)

import numpy as np
from ibm_watson_machine_learning.utils.autoai.utils import all_logging_disabled, try_import_autoai_libs, \
    try_import_autoai_ts_libs
from ibm_watson_machine_learning.utils.autoai.watson_studio import get_project
from ibm_watson_machine_learning.wml_client_error import MissingValue, ApiRequestFailure
from .base_connection import BaseConnection
from .base_data_connection import BaseDataConnection
from .base_location import BaseLocation
from ..flight.service import FlightService
from ..flight.utils import get_data_asset_attachment, try_import_pyarrow
from ..flight.errors import DataSourceTypeNotRecognized
from typing import Callable, Any

if TYPE_CHECKING:
    from ibm_watson_machine_learning.workspace import WorkSpace


class DataConnection(BaseDataConnection):
    """
    Data Storage Connection class needed for WML training metadata (input data).

    Parameters
    ----------
    connection: Union[S3Connection], optional
        connection parameters of specific type

    location: Union[S3Location, FSLocation, AssetLocation],
        required location parameters of specific type

    data_join_node_name: Union[str, List[str]], optional
        Names for node(s). If no value provided, data file name will be used as node name. If str will be passed,
        it will became node name. If multiple names will be passed, several nodes will have the same data connection
        (used for excel files with multiple sheets).

    data_asset_id: str, optional,
        Data asset ID if DataConnection should be pointing out to Data Asset.
    """

    def __init__(self,
                 location: Union['S3Location',
                                 'FSLocation',
                                 'AssetLocation',
                                 'CP4DAssetLocation',
                                 'WMLSAssetLocation',
                                 'WSDAssetLocation',
                                 'CloudAssetLocation',
                                 'NFSLocation',
                                 'DeploymentOutputAssetLocation',
                                 'ConnectionAssetLocation',
                                 'DatabaseLocation',
                                 'ContainerLocation'] = None,
                 connection: Optional[Union['S3Connection', 'NFSConnection', 'ConnectionAsset']] = None,
                 data_join_node_name: Union[str, List[str]] = None,
                 data_asset_id: str = None,
                 connection_asset_id: str = None,
                 **kwargs):
        if data_asset_id is None and location is None:
            raise MissingValue('location or data_asset_id', reason="Provide 'location' or 'data_asset_id'.")

        elif data_asset_id is not None and location is not None:
            raise ValueError("'data_asset_id' and 'location' cannot be specified together.")

        elif data_asset_id is not None:
            location = AssetLocation(asset_id=data_asset_id)

            if kwargs.get('model_location') is not None:
                location._model_location = kwargs['model_location']

            if kwargs.get('training_status') is not None:
                location._training_status = kwargs['training_status']

        elif connection_asset_id is not None and isinstance(location, (S3Location, DatabaseLocation)):
            connection = ConnectionAsset(connection_id=connection_asset_id)

        super().__init__()

        self.connection = connection
        self.location = location

        # TODO: remove S3 implementation
        if isinstance(connection, S3Connection):
            self.type = DataConnectionTypes.S3

        elif isinstance(location, NFSLocation):
            self.type = DataConnectionTypes.CA
            if self.connection is not None:
                self.location.id = self.connection.asset_id

        elif isinstance(connection, ConnectionAsset):
            self.type = DataConnectionTypes.CA
            # note: We expect a `file_name` keyword for CA pointing to COS.
            if isinstance(self.location, S3Location):
                self.location.file_name = self.location.path
                del self.location.path
            # --- end note

        elif isinstance(location, FSLocation):
            self.type = DataConnectionTypes.FS

        elif isinstance(location, ContainerLocation):
            self.type = DataConnectionTypes.CN

        elif isinstance(location, (AssetLocation, CP4DAssetLocation, WMLSAssetLocation, CloudAssetLocation,
                                   WSDAssetLocation, DeploymentOutputAssetLocation)):
            self.type = DataConnectionTypes.DS

        self.auto_pipeline_params = {}  # note: needed parameters for recreation of autoai holdout split
        self._wml_client = None
        self.__wml_client = None  # only for getter/setter for AssetLocation href
        self._run_id = None
        self._obm = False
        self._obm_cos_path = None
        self._test_data = False
        self._user_holdout_exists = False

        # note: make data connection id as a location path for OBM + KB
        if data_join_node_name is None:
            # TODO: remove S3 implementation
            if self.type == DataConnectionTypes.S3 or (
                    self.type == DataConnectionTypes.CA and hasattr(location, 'file_name')):
                self.id = location.get_location()

            else:
                self.id = None

        else:
            self.id = data_join_node_name
        # --- end note

    # note: client as property and setter for dynamic href creation for AssetLocation
    @property
    def _wml_client(self):
        return self.__wml_client

    @_wml_client.setter
    def _wml_client(self, var):
        self.__wml_client = var
        if isinstance(self.location, (AssetLocation, WSDAssetLocation)):
            self.location.wml_client = self.__wml_client

    # --- end note

    @classmethod
    def from_studio(cls, path: str) -> List['DataConnection']:
        """
        Create DataConnections from the credentials stored (connected) in Watson Studio. Only for COS.

        Parameters
        ----------
        path: str, required
            Path in COS bucket to the training dataset.

        Returns
        -------
        List with DataConnection objects.

        Example
        -------
        >>> data_connections = DataConnection.from_studio(path='iris_dataset.csv')
        """
        try:
            from project_lib import Project

        except ModuleNotFoundError:
            raise MissingProjectLib("Missing project_lib package.")

        else:
            data_connections = []
            for name, value in globals().items():
                if isinstance(value, Project):
                    connections = value.get_connections()

                    if connections:
                        for connection in connections:
                            asset_id = connection['asset_id']
                            connection_details = value.get_connection(asset_id)

                            if ('url' in connection_details and 'access_key' in connection_details and
                                    'secret_key' in connection_details and 'bucket' in connection_details):
                                data_connections.append(
                                    cls(connection=ConnectionAsset(id=connection_details['id']),
                                        location=ConnectionAssetLocation(bucket=connection_details['bucket'],
                                                                         file_name=path))
                                )

            if data_connections:
                return data_connections

            else:
                raise MissingCOSStudioConnection(
                    "There is no any COS Studio connection. "
                    "Please create a COS connection from the UI and insert "
                    "the cell with project API connection (Insert project token)")

    def _subdivide_connection(self):
        if type(self.id) is str or not self.id:
            return [self]
        else:
            def cpy(new_id):
                child = copy.copy(self)
                child.id = new_id
                return child

            return [cpy(id) for id in self.id]

    def _to_dict(self) -> dict:
        """
        Convert DataConnection object to dictionary representation.

        Returns
        -------
        Dictionary
        """

        if self.id and type(self.id) is list:
            raise InvalidIdType(list)

        _dict = {"type": self.type}

        # note: for OBM (id of DataConnection if an OBM node name)
        if self.id is not None:
            _dict['id'] = self.id
        # --- end note

        if self.connection is not None:
            _dict['connection'] = deepcopy(self.connection.to_dict())
        else:
            _dict['connection'] = {}

        try:
            _dict['location'] = deepcopy(self.location.to_dict())

        except AttributeError:
            _dict['location'] = {}

        return _dict

    def __repr__(self):
        return str(self._to_dict())

    def __str__(self):
        return str(self._to_dict())

    @classmethod
    def _from_dict(cls, _dict: dict) -> 'DataConnection':
        """
        Create a DataConnection object from dictionary

        Parameters
        ----------
        _dict: dict, required
            A dictionary data structure with information about data connection reference.

        Returns
        -------
        DataConnection
        """
        # TODO: remove S3 implementation
        if _dict['type'] == DataConnectionTypes.S3:
            warn(message="S3 DataConnection is deprecated! Please use data_asset_id instead.")

            data_connection: 'DataConnection' = cls(
                connection=S3Connection(
                    access_key_id=_dict['connection']['access_key_id'],
                    secret_access_key=_dict['connection']['secret_access_key'],
                    endpoint_url=_dict['connection']['endpoint_url']
                ),
                location=S3Location(
                    bucket=_dict['location']['bucket'],
                    path=_dict['location']['path']
                )
            )
        elif _dict['type'] == DataConnectionTypes.FS:
            data_connection: 'DataConnection' = cls(
                location=FSLocation._set_path(path=_dict['location']['path'])
            )
        elif _dict['type'] == DataConnectionTypes.CA:
            if _dict['location'].get('file_name') is not None and _dict['location'].get('bucket'):
                data_connection: 'DataConnection' = cls(
                    connection_asset_id=_dict['connection']['id'],
                    location=S3Location(
                        bucket=_dict['location']['bucket'],
                        path=_dict['location']['file_name']
                    )
                )

            elif _dict['location'].get('path') is not None and _dict['location'].get('bucket'):
                data_connection: 'DataConnection' = cls(
                    connection_asset_id=_dict['connection']['id'],
                    location=S3Location(
                        bucket=_dict['location']['bucket'],
                        path=_dict['location']['path']
                    )
                )

            elif _dict['location'].get('schema_name') and _dict['location'].get('table_name'):
                data_connection: 'DataConnection' = cls(
                    connection_asset_id=_dict['connection']['id'],
                    location=DatabaseLocation(schema_name=_dict['location']['schema_name'],
                                              table_name=_dict['location']['table_name'])
                )

            else:
                data_connection: 'DataConnection' = cls(
                    connection=NFSConnection(asset_id=_dict['connection']['asset_id']),
                    location=NFSLocation(path=_dict['location']['path'])
                )
        elif _dict['type'] == DataConnectionTypes.CN:
            data_connection: 'DataConnection' = cls(
                location=ContainerLocation(path=_dict['location']['path'])
            )

        else:
            data_connection: 'DataConnection' = cls(
                location=AssetLocation._set_path(href=_dict['location']['href'])
            )

        if _dict.get('id'):
            data_connection.id = _dict['id']

        return data_connection

    def _recreate_holdout(
            self,
            data: 'DataFrame',
            with_holdout_split: bool = True
    ) -> Union[Tuple['DataFrame', 'DataFrame'], Tuple['DataFrame', 'DataFrame', 'DataFrame', 'DataFrame']]:
        """This method tries to recreate holdout data."""

        if self.auto_pipeline_params.get('prediction_columns') is not None:
            # timeseries
            try_import_autoai_ts_libs()
            from autoai_ts_libs.utils.holdout_utils import make_holdout_split

            # Note: When lookback window is auto detected there is need to get the detected value from training details
            if self.auto_pipeline_params.get('lookback_window') == -1 or self.auto_pipeline_params.get('lookback_window') is None:
                ts_metrics = self._wml_client.training.get_details(self.auto_pipeline_params.get('run_id'))['entity']['status']['metrics']
                final_ts_state_name = "after_final_pipelines_generation"


                for metric in ts_metrics:
                    if metric['context']['intermediate_model']['process'] == final_ts_state_name:
                        self.auto_pipeline_params['lookback_window'] = metric['context']['timeseries']['lookback_window']
                        break

            # Note: imputation is not supported
            X_train, X_holdout, y_train, y_holdout, _, _, _, _ = make_holdout_split(
                dataset=data,
                target_columns=self.auto_pipeline_params.get('prediction_columns'),
                learning_type="forecasting",
                test_size=self.auto_pipeline_params.get('holdout_size'),
                lookback_window=self.auto_pipeline_params.get('lookback_window'),
                # feature_columns=None,
                timestamp_column=self.auto_pipeline_params.get('timestamp_column_name'),
                # n_jobs=None,
                # tshirt_size=None,
                return_only_holdout=False
            )

            X_train = DataFrame(X_train, columns=self.auto_pipeline_params['prediction_columns'])
            X_holdout = DataFrame(X_holdout, columns=self.auto_pipeline_params['prediction_columns'])
            y_train = DataFrame(y_train, columns=self.auto_pipeline_params['prediction_columns'])
            y_holdout = DataFrame(y_holdout, columns=self.auto_pipeline_params['prediction_columns'])

            return X_train, X_holdout, y_train, y_holdout

        else:
            try_import_autoai_libs(minimum_version='1.12.14')
            from autoai_libs.utils.holdout_utils import make_holdout_split, numpy_split_on_target_values
            from autoai_libs.utils.sampling_utils import numpy_sample_rows

            data.replace([np.inf, -np.inf], np.nan, inplace=True)
            data.drop_duplicates(inplace=True)
            data.dropna(subset=[self.auto_pipeline_params['prediction_column']], inplace=True)
            dfy = data[self.auto_pipeline_params['prediction_column']]
            data.drop(columns=[self.auto_pipeline_params['prediction_column']], inplace=True)

            y_column = [self.auto_pipeline_params['prediction_column']]
            X_columns = data.columns

            if self._test_data or not with_holdout_split:
                return data, dfy

            else:
                ############################
                #   REMOVE MISSING ROWS    #
                from autoai_libs.utils.holdout_utils import numpy_remove_missing_target_rows
                # Remove (and save) the rows of X and y for which the target variable has missing values
                data, dfy, _, _, _, _ = numpy_remove_missing_target_rows(
                    y=dfy, X=data
                )
                #   End of REMOVE MISSING ROWS    #
                ###################################

                #################
                #   SAMPLING    #
                # Get a sample of the rows if requested and applicable
                # (check for sampling is performed inside this function)
                try:
                    data, dfy, _ = numpy_sample_rows(
                        X=data,
                        y=dfy,
                        train_sample_rows_test_size=self.auto_pipeline_params['train_sample_rows_test_size'],
                        learning_type=self.auto_pipeline_params['prediction_type'],
                        return_sampled_indices=True
                    )

                # Note: we have a silent error here (the old core behaviour)
                # sampling is not performed as 'train_sample_rows_test_size' is bigger than data rows count
                # TODO: can we throw an error instead?
                except ValueError as e:
                    if 'between' in str(e):
                        pass

                    else:
                        raise e
                #   End of SAMPLING    #
                ########################

                # Perform holdout split
                X_train, X_holdout, y_train, y_holdout, _, _ = make_holdout_split(
                    x=data,
                    y=dfy,
                    learning_type=self.auto_pipeline_params['prediction_type'],
                    fairness_info=self.auto_pipeline_params.get('fairness_info', None),
                    test_size=self.auto_pipeline_params['holdout_size'],
                    return_only_holdout=False
                )

                X_train = DataFrame(X_train, columns=X_columns)
                X_holdout = DataFrame(X_holdout, columns=X_columns)
                y_train = DataFrame(y_train, columns=y_column)
                y_holdout = DataFrame(y_holdout, columns=y_column)

                return X_train, X_holdout, y_train, y_holdout

    def read(self,
             with_holdout_split: bool = False,
             csv_separator: str = ',',
             excel_sheet: Union[str, int] = 0,
             encoding: Optional[str] = 'utf-8',
             raw: Optional[bool] = False,
             **kwargs) -> Union['DataFrame', Tuple['DataFrame', 'DataFrame']]:
        """
        Download dataset stored in remote data storage.

        Parameters
        ----------
        with_holdout_split: bool, optional
            If True, data will be split to train and holdout dataset as it was by AutoAI.

        csv_separator: str, optional
            Separator / delimiter for CSV file, default is ','

        excel_sheet: Union[str, int], optional
            Excel file sheet name to use, default is 0.

        encoding: str, optional
            Encoding type of the CSV

        raw: bool, optional
            Default False. If False there will be applied simple data preprocessing (the same as in the backend).
            If True, data will be not preprocessed.

        Returns
        -------
        pandas.DataFrame contains dataset from remote data storage : Xy_train
        or
        Tuple[pandas.DataFrame, pandas.DataFrame, pandas.DataFrame, pandas.DataFrame] : X_train, X_holdout, y_train, y_holdout
        or
        Tuple[pandas.DataFrame, pandas.DataFrame] : X_test, y_test
        containing training data and holdout data from remote storage.


        Example
        -------
        Auto holdout split from backend (only train data provided)
        >>> train_data_connections = optimizer.get_data_connections()
        >>>
        >>> data = train_data_connections[0].read() # all train data
        >>> # or
        >>> X_train, X_holdout, y_train, y_holdout = train_data_connections[0].read(with_holdout_split=True) # train and holdout data

        User provided train and test data
        >>> optimizer.fit(training_data_reference=[DataConnection],
        >>>               training_results_reference=DataConnection,
        >>>               test_data_reference=DataConnection)
        >>>
        >>> test_data_connection = optimizer.get_test_data_connections()
        >>> X_test, y_test = test_data_connection.read() # only holdout data
        >>>
        >>> # and
        >>>
        >>> train_data_connections = optimizer.get_data_connections()
        >>> data = train_connections[0].read() # only train data
        """
        if with_holdout_split and self._user_holdout_exists:  # when this connection is training one
            raise NoAutomatedHoldoutSplit(reason="Experiment was run based on user defined holdout dataset.")

        # note: experiment metadata is used only in autogen notebooks
        experiment_metadata = kwargs.get('experiment_metadata')
        if experiment_metadata is not None:
            self.auto_pipeline_params['train_sample_rows_test_size'] = experiment_metadata.get(
                'train_sample_rows_test_size')
            self.auto_pipeline_params['prediction_column'] = experiment_metadata.get('prediction_column')
            self.auto_pipeline_params['prediction_columns'] = experiment_metadata.get('prediction_columns')
            self.auto_pipeline_params['holdout_size'] = experiment_metadata.get('holdout_size')
            self.auto_pipeline_params['prediction_type'] = experiment_metadata['prediction_type']
            self.auto_pipeline_params['fairness_info'] = experiment_metadata.get('fairness_info')
            self.auto_pipeline_params['lookback_window'] = experiment_metadata.get('lookback_window')
            self.auto_pipeline_params['timestamp_column_name'] = experiment_metadata.get('timestamp_column_name')

            # note: check for cloud
            if isinstance(experiment_metadata['training_result_reference'].location, (S3Location, AssetLocation)):
                run_id = experiment_metadata['training_result_reference'].location._training_status.split('/')[-2]
            # WMLS
            else:
                run_id = experiment_metadata['training_result_reference'].location.path.split('/')[-3]
            self.auto_pipeline_params['run_id'] = run_id

            if self._test_data:
                csv_separator = experiment_metadata.get('test_data_csv_separator', csv_separator)
                excel_sheet = experiment_metadata.get('test_data_excel_sheet', excel_sheet)
                encoding = experiment_metadata.get('test_data_encoding', encoding)

            else:
                csv_separator = experiment_metadata.get('csv_separator', csv_separator)
                excel_sheet = experiment_metadata.get('excel_sheet', excel_sheet)
                encoding = experiment_metadata.get('encoding', encoding)

        if self.type == DataConnectionTypes.DS or self.type == DataConnectionTypes.CA:
            if self._wml_client is None:
                try:
                    from project_lib import Project

                except ModuleNotFoundError:
                    raise NotImplementedError(f"This functionality can be run only on Watson Studio.")

        if (with_holdout_split or self._test_data) and not self.auto_pipeline_params.get('prediction_type', False):
            raise MissingAutoPipelinesParameters(
                self.auto_pipeline_params,
                reason=f"To be able to recreate an original holdout split, you need to schedule a training job or "
                       f"if you are using historical runs, just call historical_optimizer.get_data_connections()")

        # note: allow to read data at any time
        elif (('csv_separator' not in self.auto_pipeline_params and 'excel_sheet' not in self.auto_pipeline_params and
               'encoding' not in self.auto_pipeline_params)
              or csv_separator != ',' or excel_sheet != 0 or encoding != 'utf-8'):
            self.auto_pipeline_params['csv_separator'] = csv_separator
            self.auto_pipeline_params['excel_sheet'] = excel_sheet
            self.auto_pipeline_params['encoding'] = encoding
        # --- end note

        data = DataFrame()

        # TODO: Remove S3 implementation
        if self.type == DataConnectionTypes.S3:
            warn(message="S3 DataConnection is deprecated! Please use data_asset_id instead.")

            cos_client = self._init_cos_client()

            try:
                if self._obm:
                    data = self._download_obm_data_from_cos(cos_client=cos_client)

                else:
                    data = self._download_data_from_cos(cos_client=cos_client)

            except Exception as cos_access_exception:
                raise ConnectionError(
                    f"Unable to access data object in cloud object storage with credentials supplied. "
                    f"Error: {cos_access_exception}")

        elif self.type == DataConnectionTypes.DS:
            try:
                with all_logging_disabled():
                    if self._check_if_connection_asset_is_s3():
                        cos_client = self._init_cos_client()

                        if self._obm:
                            data = self._download_obm_data_from_cos(cos_client=cos_client)

                        else:
                            data = self._download_data_from_cos(cos_client=cos_client)
                    else:
                        data = self._download_training_data_from_data_asset_storage()

            except NotImplementedError as e:
                raise e

            except FileNotFoundError as e:
                raise e

            except Exception as e:
                # do not try Flight if we are on the cloud
                if self._wml_client is not None:
                    if not self._wml_client.ICP:
                        raise e

                elif os.environ.get('USER_ACCESS_TOKEN') is None:
                    raise e

                data_location = self.location.to_dict()
                data_location.update({'type': self.type})

                try_import_pyarrow()

                flight_service = FlightService(
                    wml_client=self._wml_client,
                    params=self.auto_pipeline_params,
                    data_location=data_location,
                    experiment_metadata=kwargs.get('experiment_metadata')
                )

                data = flight_service.read()

        elif self.type == DataConnectionTypes.FS:

            if self._obm:
                data = self._download_obm_data_from_file_system()
            else:
                data = self._download_training_data_from_file_system()

        elif self.type == DataConnectionTypes.CA or self.type == DataConnectionTypes.CN:
            try:
                with all_logging_disabled():
                    if self._check_if_connection_asset_is_s3():
                        cos_client = self._init_cos_client()

                        try:
                            if self._obm:
                                data = self._download_obm_data_from_cos(cos_client=cos_client)

                            else:
                                data = self._download_data_from_cos(cos_client=cos_client)

                        except Exception as cos_access_exception:
                            raise ConnectionError(
                                f"Unable to access data object in cloud object storage with credentials supplied. "
                                f"Error: {cos_access_exception}")

                    else:
                        data = self._download_data_from_nfs_connection()

            except Exception as e:
                # do not try Flight is we are on the cloud
                if self._wml_client is not None:
                    if not self._wml_client.ICP:
                        raise e

                elif os.environ.get('USER_ACCESS_TOKEN') is None:
                    raise e

                try_import_pyarrow()

                flight_service = FlightService(
                    wml_client=self._wml_client,
                    params=self.auto_pipeline_params,
                    data_location={'location': self.location.to_dict(),
                                   'type': self.type,
                                   "connection": self.connection.to_dict()},
                    experiment_metadata=kwargs.get('experiment_metadata')
                )

                data = flight_service.read()

        if isinstance(data, DataFrame) and 'Unnamed: 0' in data.columns.tolist():
            data.drop(['Unnamed: 0'], axis=1, inplace=True)

        if raw or (self.auto_pipeline_params.get('prediction_column') is None
                   and self.auto_pipeline_params.get('prediction_columns') is None):
            return data

        else:
            if with_holdout_split:  # when this connection is training one
                X_train, X_holdout, y_train, y_holdout = self._recreate_holdout(data=data)
                return X_train, X_holdout, y_train, y_holdout

            else:  # when this data connection is a test / holdout one
                if self.auto_pipeline_params.get('prediction_columns') is not None:
                    # timeseries dataset does not have prediction columns. Whole data set is returned:
                    test_X = data
                else:
                    test_X, test_y = self._recreate_holdout(data=data, with_holdout_split=False)
                    test_X[self.auto_pipeline_params.get('prediction_column', 'prediction_column')] = test_y
                return test_X  # return one dataframe

    def write(self, data: Union[str, 'DataFrame'], remote_name: str = None, **kwargs) -> None:
        """
        Upload file to a remote data storage.

        Parameters
        ----------
        data: str, required
            Local path to the dataset or pandas.DataFrame with data.

        remote_name: str, required
            Name that dataset should be stored with in remote data storage.
        """
        # TODO: Remove S3 implementation
        if self.type == DataConnectionTypes.S3:
            warn(message="S3 DataConnection is deprecated! Please use data_asset_id instead.")
            if remote_name is None:
                raise MissingValue('remote_name')

            cos_resource_client = self._init_cos_client()
            if isinstance(data, str):
                with open(data, "rb") as file_data:
                    cos_resource_client.Object(self.location.bucket, remote_name).upload_fileobj(
                        Fileobj=file_data)

            elif isinstance(data, DataFrame):
                # note: we are saving csv in memory as a file and stream it to the COS
                buffer = io.StringIO()
                data.to_csv(buffer, index=False)
                buffer.seek(0)

                with buffer as f:
                    cos_resource_client.Object(self.location.bucket, remote_name).upload_fileobj(
                        Fileobj=io.BytesIO(bytes(f.read().encode())))

            else:
                raise TypeError("data should be either of type \"str\" or \"pandas.DataFrame\"")

        elif self.type == DataConnectionTypes.CA or self.type == DataConnectionTypes.CN:
            if self._check_if_connection_asset_is_s3():
                cos_resource_client = self._init_cos_client()
                if isinstance(data, str):
                    with open(data, "rb") as file_data:
                        cos_resource_client.Object(self.location.bucket, remote_name).upload_fileobj(
                            Fileobj=file_data)

                elif isinstance(data, DataFrame):
                    # note: we are saving csv in memory as a file and stream it to the COS
                    buffer = io.StringIO()
                    data.to_csv(buffer, index=False)
                    buffer.seek(0)

                    with buffer as f:
                        cos_resource_client.Object(self.location.bucket, remote_name).upload_fileobj(
                            Fileobj=io.BytesIO(bytes(f.read().encode())))

                else:
                    raise TypeError("data should be either of type \"str\" or \"pandas.DataFrame\"")

            else:
                try_import_pyarrow()

                flight_service = FlightService(
                    wml_client=self._wml_client,
                    params=self.auto_pipeline_params,
                    data_location={'location': self.location.to_dict(),
                                   'type': self.type,
                                   "connection": self.connection.to_dict()},
                    experiment_metadata=kwargs.get('experiment_metadata')
                )

                if isinstance(data, str):
                    raise TypeError(f"'data' should be of pandas.DataFrame type if "
                                    f"you want to store it with connection asset.")

                elif isinstance(data, DataFrame):
                    flight_service.write_data(data)

        elif self.type == DataConnectionTypes.DS:
            raise UseWMLClient('DataConnection.write()',
                               reason="If you want to upload any data to CP4D instance, "
                                      "firstly please get the WML client by calling "
                                      "\"client = WMLInstance().get_client()\" "
                                      "then call the method: \"client.data_assets.create()\"")

    def _init_cos_client(self) -> 'resource':
        """Initiate COS client for further usage."""
        from ibm_botocore.client import Config
        if hasattr(self.connection, 'auth_endpoint') and hasattr(self.connection, 'api_key'):
            cos_client = resource(
                service_name='s3',
                ibm_api_key_id=self.connection.api_key,
                ibm_auth_endpoint=self.connection.auth_endpoint,
                config=Config(signature_version="oauth"),
                endpoint_url=self.connection.endpoint_url
            )

        else:
            cos_client = resource(
                service_name='s3',
                endpoint_url=self.connection.endpoint_url,
                aws_access_key_id=self.connection.access_key_id,
                aws_secret_access_key=self.connection.secret_access_key
            )
        return cos_client

    def _validate_cos_resource(self):
        cos_client = self._init_cos_client()
        try:
            files = cos_client.Bucket(self.location.bucket).objects.all()
            next(x for x in files if x.key == self.location.path)
        except Exception as e:
            raise NotExistingCOSResource(self.location.bucket, self.location.path)


# TODO: Remove S3 Implementation for connection
class S3Connection(BaseConnection):
    """
    Connection class to COS data storage in S3 format.

    Parameters
    ----------
    endpoint_url: str, required
        S3 data storage url (COS)

    access_key_id: str, optional
        access_key_id of the S3 connection (COS)

    secret_access_key: str, optional
        secret_access_key of the S3 connection (COS)

    api_key: str, optional
        API key of the S3 connection (COS)

    service_name: str, optional
        Service name of the S3 connection (COS)

    auth_endpoint: str, optional
        Authentication endpoint url of the S3 connection (COS)
    """

    def __init__(self, endpoint_url: str, access_key_id: str = None, secret_access_key: str = None,
                 api_key: str = None, service_name: str = None, auth_endpoint: str = None, _internal_use=False) -> None:
        if not _internal_use:
            warn(message="S3 DataConnection is deprecated! Please use data_asset_id instead.")

        if (access_key_id is None or secret_access_key is None) and (api_key is None or auth_endpoint is None):
            raise InvalidCOSCredentials(reason='You need to specify (access_key_id and secret_access_key) or'
                                               '(api_key and auth_endpoint)')

        if secret_access_key is not None:
            self.secret_access_key = secret_access_key

        if api_key is not None:
            self.api_key = api_key

        if service_name is not None:
            self.service_name = service_name

        if auth_endpoint is not None:
            self.auth_endpoint = auth_endpoint

        if access_key_id is not None:
            self.access_key_id = access_key_id

        if endpoint_url is not None:
            self.endpoint_url = endpoint_url


class S3Location(BaseLocation):
    """
    Connection class to COS data storage in S3 format.

    Parameters
    ----------
    bucket: str, required
        COS bucket name

    path: str, required
        COS data path in the bucket.

    model_location: str, optional
        Path to the pipeline model in the COS.

    training_status: str, optional
        Path t the training status json in COS.
    """

    def __init__(self, bucket: str, path: str, **kwargs) -> None:
        self.bucket = bucket
        self.path = path

        if kwargs.get('model_location') is not None:
            self._model_location = kwargs['model_location']

        if kwargs.get('training_status') is not None:
            self._training_status = kwargs['training_status']

    def _get_file_size(self, cos_resource_client: 'resource') -> 'int':
        try:
            size = cos_resource_client.Object(self.bucket, self.path).content_length
        except ClientError:
            size = 0
        return size

    def get_location(self) -> str:
        if hasattr(self, "file_name"):
            return self.file_name
        else:
            return self.path


class ContainerLocation(BaseLocation):
    """
    Connection class to default COS in user Project/Space.
    """

    def __init__(self, path: Optional[str] = None, **kwargs) -> None:
        if path is None:
            self.path = "default_autoai_out"

        else:
            self.path = path

        self.bucket = None

        if kwargs.get('model_location') is not None:
            self._model_location = kwargs['model_location']

        if kwargs.get('training_status') is not None:
            self._training_status = kwargs['training_status']

    def to_dict(self) -> dict:
        _dict = super().to_dict()

        if 'bucket' in _dict and _dict['bucket'] is None:
            del _dict['bucket']

        return _dict

    @classmethod
    def _set_path(cls, path: str) -> 'ContainerLocation':
        location = cls()
        location.path = path
        return location

    def _get_file_size(self):
        pass


class FSLocation(BaseLocation):
    """
    Connection class to File Storage in CP4D.
    """

    def __init__(self, path: Optional[str] = None) -> None:
        if path is None:
            self.path = "/{option}/{id}" + f"/assets/auto_ml/auto_ml.{uuid.uuid4()}/wml_data"

        else:
            self.path = path

    @classmethod
    def _set_path(cls, path: str) -> 'FSLocation':
        location = cls()
        location.path = path
        return location

    def _save_file_as_data_asset(self, workspace: 'WorkSpace') -> 'str':

        asset_name = self.path.split('/')[-1]
        if self.path:
            data_asset_details = workspace.wml_client.data_assets.create(asset_name, self.path)
            return workspace.wml_client.data_assets.get_uid(data_asset_details)
        else:
            raise MissingValue('path', reason="Incorrect initialization of class FSLocation")

    def _get_file_size(self, workspace: 'WorkSpace') -> 'int':
        # note if path is not file then returned size is 0
        try:
            # note: try to get file size from remote server
            url = workspace.wml_client.service_instance._href_definitions.get_wsd_model_attachment_href() \
                  + f"/{self.path.split('/assets/')[-1]}"
            path_info_response = requests.head(url, headers=workspace.wml_client._get_headers(),
                                               params=workspace.wml_client._params())
            if path_info_response.status_code != 200:
                raise ApiRequestFailure(u"Failure during getting path details", path_info_response)
            path_info = path_info_response.headers
            if 'X-Asset-Files-Type' in path_info and path_info['X-Asset-Files-Type'] == 'file':
                size = path_info['X-Asset-Files-Size']
            else:
                size = 0
            # -- end note
        except (ApiRequestFailure, AttributeError):
            # note try get size of file from local fs
            size = os.stat(path=self.path).st_size if os.path.isfile(path=self.path) else 0
            # -- end note
        return size


class AssetLocation(BaseLocation):

    def __init__(self, asset_id: str) -> None:
        self._wsd = self._is_wsd()
        self.href = None
        self._initial_asset_id = asset_id
        self.__wml_client = None

        if self._wsd:
            self._asset_name = None
            self._asset_id = None
            self._local_asset_path = None
        else:
            self.id = asset_id

    def _get_bucket(self, client) -> str:
        """Try to get bucket from data asset."""
        connection_id = self._get_connection_id(client)
        conn_details = client.connections.get_details(connection_id)
        bucket = conn_details.get('entity', {}).get('properties', {}).get('bucket')

        if bucket is None:
            asset_details = client.data_assets.get_details(self.id)
            connection_path = asset_details['entity'].get('folder_asset', {}).get('connection_path')
            if connection_path is None:
                attachment_content = self._get_attachment_details(client)
                connection_path = attachment_content.get('connection_path')

            bucket = connection_path.split('/')[1]

        return bucket

    def _get_attachment_details(self, client) -> dict:
        asset_details = client.data_assets.get_details(self.id)

        if 'attachment_id' in asset_details['metadata']:
            attachment_id = asset_details['metadata']['attachment_id']

        else:
            attachment_id = asset_details['attachments'][0]['id']

        attachment_url = client.service_instance._href_definitions.get_data_asset_href(self.id)
        attachment_url = f"{attachment_url}/attachments/{attachment_id}"

        if client.ICP:
            attachment = requests.get(attachment_url, headers=client._get_headers(),
                                      params=client._params())

        else:
            attachment = requests.get(attachment_url, headers=client._get_headers(),
                                      params=client._params())

        if attachment.status_code != 200:
            raise ApiRequestFailure(u"Failure during getting attachment details", attachment)

        return attachment.json()

    def _get_connection_id(self, client) -> str:
        attachment_content = self._get_attachment_details(client)

        return attachment_content.get('connection_id')

    @classmethod
    def _is_wsd(cls):
        if os.environ.get('USER_ACCESS_TOKEN'):
            return False

        try:
            from project_lib import Project
            try:
                with all_logging_disabled():
                    access = Project.access()
                return True
            except RuntimeError:
                pass
        except ModuleNotFoundError:
            pass

        return False

    @classmethod
    def _set_path(cls, href: str) -> 'AssetLocation':
        items = href.split('/')
        _id = items[-1].split('?')[0]
        location = cls(_id)
        location.href = href
        return location

    def _get_file_size(self, workspace: 'WorkSpace', *args) -> 'int':
        if self._wsd:
            return self._wsd_get_file_size()
        else:
            asset_info_response = requests.get(
                workspace.wml_client.service_instance._href_definitions.get_data_asset_href(self.id),
                params=workspace.wml_client._params(),
                headers=workspace.wml_client._get_headers())
            if asset_info_response.status_code != 200:
                raise ApiRequestFailure(u"Failure during getting asset details", asset_info_response)
            return asset_info_response.json()['metadata'].get('size')

    def _wsd_setup_local_asset_details(self) -> None:
        if not self._wsd:
            raise NotWSDEnvironment()

        # note: set local asset file from asset_id
        project = get_project()
        project_id = project.get_metadata()["metadata"]["guid"]

        local_assets = project.get_files()

        # note: reuse local asset_id when object is reused more times
        if self._asset_id is None:
            local_asset_id = self._initial_asset_id

        else:
            local_asset_id = self._asset_id
        # --- end note

        if local_asset_id not in str(local_assets):
            raise MissingLocalAsset(local_asset_id, reason="Provided asset_id cannot be found on WS Desktop.")

        else:
            for asset in local_assets:
                if asset['asset_id'] == local_asset_id:
                    asset_name = asset['name']
                    self._asset_name = asset_name
                    self._asset_id = local_asset_id

            local_asset_path = f"{os.path.abspath('.')}/{project_id}/assets/data_asset/{asset_name}"
            self._local_asset_path = local_asset_path

    def _wsd_move_asset_to_server(self, workspace: 'WorkSpace') -> None:
        if not self._wsd:
            raise NotWSDEnvironment()

        if not self._local_asset_path or self._asset_name or self._asset_id:
            self._wsd_setup_local_asset_details()

        remote_asset_details = workspace.wml_client.data_assets.create(self._asset_name, self._local_asset_path)
        self.href = remote_asset_details['metadata']['href']

    def _wsd_get_file_size(self) -> 'int':
        if not self._wsd:
            raise NotWSDEnvironment()

        if not self._local_asset_path or self._asset_name or self._asset_id:
            self._wsd_setup_local_asset_details()
        return os.stat(path=self._local_asset_path).st_size if os.path.isfile(path=self._local_asset_path) else 0

    @classmethod
    def list_wsd_assets(cls):
        if not cls._is_wsd():
            raise NotWSDEnvironment

        project = get_project()
        return project.get_files()

    def to_dict(self) -> dict:
        """Return a json dictionary representing this model."""
        _dict = vars(self).copy()

        del _dict['_wsd']
        del _dict[f"_{self.__class__.__name__}__wml_client"]

        if self._wsd:
            del _dict['_asset_name']
            del _dict['_asset_id']
            del _dict['_local_asset_path']

        del _dict['_initial_asset_id']

        return _dict

    @property
    def wml_client(self):
        return self.__wml_client

    @wml_client.setter
    def wml_client(self, var):
        self.__wml_client = var

        if self.__wml_client:
            self.href = self.__wml_client.service_instance._href_definitions.get_base_asset_href(self._initial_asset_id)
        else:
            self.href = f'/v2/assets/{self._initial_asset_id}'

        if not self._wsd:
            if self.__wml_client:
                if self.__wml_client.default_space_id:
                    self.href = f'{self.href}?space_id={self.__wml_client.default_space_id}'
                else:
                    self.href = f'{self.href}?project_id={self.__wml_client.default_project_id}'


class ConnectionAssetLocation(BaseLocation):
    """
        Connection class to COS data storage.

        Parameters
        ----------
        bucket: str, required
            COS bucket name

        file_name: str, required
            COS data path in the bucket

        model_location: str, optional
            Path to the pipeline model in the COS.

        training_status: str, optional
            Path t the training status json in COS.
        """

    def __init__(self, bucket: str, file_name: str, **kwargs) -> None:
        self.bucket = bucket
        self.file_name = file_name
        self.path = file_name

        if kwargs.get('model_location') is not None:
            self._model_location = kwargs['model_location']

        if kwargs.get('training_status') is not None:
            self._training_status = kwargs['training_status']

    def _get_file_size(self, cos_resource_client: 'resource') -> 'int':
        try:
            size = cos_resource_client.Object(self.bucket, self.path).content_length
        except ClientError:
            size = 0
        return size

    def to_dict(self) -> dict:
        """Return a json dictionary representing this model."""
        return vars(self)


class ConnectionAsset(BaseConnection):
    """
    Connection class for Connection Asset

    Parameters
    ----------
    connection_id: str, required
        Connection asset ID
    """

    def __init__(self, connection_id: str):
        self.id = connection_id


class NFSConnection(BaseConnection):
    """
    Connection class to file storage in CP4D of NFS format.

    Parameters
    ----------
    connection_id: str, required
        Connection ID from the project on CP4D
    """

    def __init__(self, asset_id: str):
        self.asset_id = asset_id
        self.id = asset_id


class NFSLocation(BaseLocation):
    """
    Location class to file storage in CP4D of NFS format.

    Parameters
    ----------
    path: str, required
        Data path form the project on CP4D.
    """

    def __init__(self, path: str):
        self.path = path
        self.id = None

    def _get_file_size(self, workspace: 'Workspace', *args) -> 'int':
        params = workspace.wml_client._params().copy()
        params['path'] = self.path
        params['detail'] = 'true'

        href = workspace.wml_client.connections._href_definitions.get_connection_by_id_href(self.id) + '/assets'
        asset_info_response = requests.get(href,
                                           params=params, headers=workspace.wml_client._get_headers(None))
        if asset_info_response.status_code != 200:
            raise Exception(u"Failure during getting asset details", asset_info_response.json())
        return asset_info_response.json()['details']['file_size']


class CP4DAssetLocation(AssetLocation):
    """
    Connection class to data assets in CP4D.

    Parameters
    ----------
    asset_id: str, required
        Asset ID from the project on CP4D.
    """

    def __init__(self, asset_id: str) -> None:
        super().__init__(asset_id)
        warning_msg = ("Depreciation Warning: Class CP4DAssetLocation is no longer supported and will be removed."
                       "Use AssetLocation instead.")
        print(warning_msg)

    def _get_file_size(self, workspace: 'WorkSpace', *args) -> 'int':
        return super()._get_file_size(workspace)


class WMLSAssetLocation(AssetLocation):
    """
    Connection class to data assets in WML Server.

    Parameters
    ----------
    asset_id: str, required
        Asset ID of the file loaded on space in WML Server.
    """

    def __init__(self, asset_id: str) -> None:
        super().__init__(asset_id)
        warning_msg = ("Depreciation Warning: Class WMLSAssetLocation is no longer supported and will be removed."
                       "Use AssetLocation instead.")
        print(warning_msg)

    def _get_file_size(self, workspace: 'WorkSpace', *args) -> 'int':
        return super()._get_file_size(workspace)


class CloudAssetLocation(AssetLocation):
    """
    Connection class to data assets as input data references to batch deployment job on Cloud.

    Parameters
    ----------
    asset_id: str, required
        Asset ID of the file loaded on space on Cloud.
    """

    def __init__(self, asset_id: str) -> None:
        super().__init__(asset_id)
        self.href = self.href
        warning_msg = ("Depreciation Warning: Class CloudAssetLocation is no longer supported and will be removed."
                       "Use AssetLocation instead.")
        print(warning_msg)

    def _get_file_size(self, workspace: 'WorkSpace', *args) -> 'int':
        return super()._get_file_size(workspace)


class WSDAssetLocation(BaseLocation):
    """
    Connection class to data assets in WS Desktop.

    Parameters
    ----------
    asset_id: str, required
        Asset ID from the project on WS Desktop.
    """

    def __init__(self, asset_id: str) -> None:
        self.href = None
        self._asset_name = None
        self._asset_id = None
        self._local_asset_path = None
        self._initial_asset_id = asset_id
        self.__wml_client = None

        warning_msg = ("Depreciation Warning: Class WSDAssetLocation is no longer supported and will be removed."
                       "Use AssetLocation instead.")
        print(warning_msg)

    @classmethod
    def list_assets(cls):
        project = get_project()
        return project.get_files()

    def _setup_local_asset_details(self) -> None:
        # note: set local asset file from asset_id
        project = get_project()
        project_id = project.get_metadata()["metadata"]["guid"]

        local_assets = project.get_files()

        # note: reuse local asset_id when object is reused more times
        if self._asset_id is None:
            local_asset_id = self.href.split('/')[3].split('?space_id')[0]

        else:
            local_asset_id = self._asset_id
        # --- end note

        if local_asset_id not in str(local_assets):
            raise MissingLocalAsset(local_asset_id, reason="Provided asset_id cannot be found on WS Desktop.")

        else:
            for asset in local_assets:
                if asset['asset_id'] == local_asset_id:
                    asset_name = asset['name']
                    self._asset_name = asset_name
                    self._asset_id = local_asset_id

            local_asset_path = f"{os.path.abspath('.')}/{project_id}/assets/data_asset/{asset_name}"
            self._local_asset_path = local_asset_path

    def _move_asset_to_server(self, workspace: 'WorkSpace') -> None:
        if not self._local_asset_path or self._asset_name or self._asset_id:
            self._setup_local_asset_details()

        remote_asset_details = workspace.wml_client.data_assets.create(self._asset_name, self._local_asset_path)
        self.href = remote_asset_details['metadata']['href']

    @classmethod
    def _set_path(cls, href: str) -> 'WSDAssetLocation':
        location = cls('.')
        location.href = href
        return location

    @property
    def wml_client(self):
        return self.__wml_client

    @wml_client.setter
    def wml_client(self, var):
        self.__wml_client = var

        if self.__wml_client:
            self.href = self.__wml_client.service_instance._href_definitions.get_base_asset_href(self._initial_asset_id)
        else:
            self.href = f'/v2/assets/{self._initial_asset_id}'

    def to_dict(self) -> dict:
        """Return a json dictionary representing this model."""
        _dict = vars(self).copy()
        del _dict['_asset_name']
        del _dict['_asset_id']
        del _dict['_local_asset_path']
        del _dict[f"_{self.__class__.__name__}__wml_client"]
        del _dict['_initial_asset_id']

        return _dict

    def _get_file_size(self) -> 'int':
        if not self._local_asset_path or self._asset_name or self._asset_id:
            self._setup_local_asset_details()
        return os.stat(path=self._local_asset_path).st_size if os.path.isfile(path=self._local_asset_path) else 0


class DeploymentOutputAssetLocation(BaseLocation):
    """
    Connection class to data assets where output of batch deployment will be stored.

    Parameters
    ----------
    name: str, required
        name of .csv file which will be saved as data asset.
    description: str, optional
        description of the data asset
    """

    def __init__(self, name: str, description: str = "") -> None:
        self.name = name
        self.description = description


class DatabaseLocation(BaseLocation):
    """
    Location class to Database.

    Parameters
    ----------
    schema_name: str, required
        Database schema name.

    table_name: str, required
        Database table name
    """

    def __init__(self, schema_name: str, table_name: str, **kwargs) -> None:
        self.schema_name = schema_name
        self.table_name = table_name

    def _get_file_size(self) -> None:
        raise NotImplementedError()
