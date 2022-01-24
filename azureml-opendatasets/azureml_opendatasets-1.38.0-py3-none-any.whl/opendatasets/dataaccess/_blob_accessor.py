# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import json
import pkgutil
import re
import shutil
import tempfile
import warnings
from enum import Enum
from typing import List, Optional, Tuple, TypeVar

import azureml.dataprep as dprep
import pandas as pd
from azureml._restclient.models.dataset_registry_dto import DatasetRegistryDto
from azureml.data import FileDataset, TabularDataset
from azureml.data._dataset import _DatasetTelemetryInfo
from azureml.dataprep.api.readers import _handle_type_inference_and_path
from dateutil.relativedelta import relativedelta
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

DatasetRegistryInfo = TypeVar('DatasetRegistryInfo', str, DatasetRegistryDto)


class DateTimePartitionName(Enum):
    YEAR = 'partition_year'
    MONTH = 'partition_month'
    DAY = 'partition_day'


class DefaultArgKey(Enum):
    STARTDATE = 'start_date'
    ENDDATE = 'end_date'
    LIMIT = 'limit'

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


class BlobAccessor(object):
    def __init__(
            self,
            registry_info: DatasetRegistryInfo,
            mandatory_columns: Optional[List[str]] = None):
        """
        Initialize Blob Accessor
        :param registry_info: registry id or DatasetRegistryDto for open datasets
        :type registry_info: DatasetRegistryInfo
        :param mandatory_columns: mandatory columns need to be included, defaults to None
        :type mandatory_columns: Optional[List[str]], optional
        """
        self._registry_info = registry_info
        self._partition_pattern = self._clean_partiton_pattern(
            self._registry_dto.partition_pattern)
        self._blob_account_name = self._registry_dto.blob_location.account_name
        self._blob_container_name, self._blob_relative_path = self._get_blob_info()
        self._file_extension = self._registry_dto.blob_location.data_format.lower()
        self._time_column_name = next((f.column_name for f in self._registry_dto.filters
                                       if f.column_type == "DateTime"), None) if self._registry_dto.filters else None
        self._mandatory_columns = ([self._time_column_name] if self._time_column_name else [
        ]) + (mandatory_columns if mandatory_columns else [])

    @property
    def id(self) -> str:
        """RegistryId"""
        return self._registry_dto.id

    @property
    def mandatory_columns(self) -> List[str]:
        """Get the mandatory columns"""
        return self._mandatory_columns

    @property
    def time_column_name(self) -> str:
        """Get the time column name."""
        return self._time_column_name

    @property
    def _registry_dto(self) -> DatasetRegistryDto:
        if isinstance(self._registry_info, str):
            self._registry_info = self._get_dataset_registry_dto(
                self._registry_info)
        return self._registry_info

    def get_url(self, partition_pattern: str = None) -> str:
        """
        Get the blob url
        :param partition_pattern: partition partterns to construct the url.
            Will use the pattern from registry info if not supplied, defaults to None
        :type partition_pattern: str, optional
        :return: blob url
        :rtype: str
        """
        partition_pattern = partition_pattern if partition_pattern else self._partition_pattern
        partitions = self._get_partitions(partition_pattern)
        glob_pattern = ""
        if self._blob_relative_path and self._blob_relative_path.endswith("/"):
            if partition_pattern:
                for partition in partitions:
                    partition_pattern = partition_pattern.replace(
                        "{%s}" % partition, "*")
                glob_pattern = partition_pattern + \
                    "/*." + self._file_extension
            else:
                glob_pattern = "*." + self._file_extension
        return 'https://%s.blob.core.windows.net/%s/%s%s' % (
            self._blob_account_name,
            self._blob_container_name,
            self._blob_relative_path,
            glob_pattern)

    def get_urls(self, **kwargs) -> List[str]:
        """
        Get the blob url based on args and partition pattern to reduce look up cost
        :return: List of blob urls
        :rtype: List[str]
        """
        partitions = self._get_partitions()
        start_date = self._get_arg(DefaultArgKey.STARTDATE.value, **kwargs)
        end_date = self._get_arg(DefaultArgKey.ENDDATE.value, **kwargs)
        if DateTimePartitionName.YEAR.value in partitions and start_date and end_date:
            # type\: datetime
            start_date = kwargs[DefaultArgKey.STARTDATE.value]
            end_date = kwargs[DefaultArgKey.ENDDATE.value]  # type\: datetime
            urls = []
            while start_date <= end_date:
                year = start_date.year
                partition_pattern = self._partition_pattern.replace(
                    "{%s}" % DateTimePartitionName.YEAR.value, str(year))
                urls.append(self.get_url(partition_pattern))
                start_date = start_date.replace(start_date.year + 1)
            return urls
        else:
            return [self.get_url()]

    def get_data_wasbs_path(self) -> str:
        wasbs_path = 'wasbs://%s@%s.blob.core.windows.net/%s' % (
            self._blob_container_name,
            self._blob_account_name,
            self._blob_relative_path)
        return wasbs_path

    def get_file_dataset(
            self,
            **kwargs) -> FileDataset:
        properties = {"opendatasets:%s" % key: value for key,
                      value in kwargs.items()} if kwargs else {}
        properties["opendatasets"] = self.id
        ds = FileDataset._create(self.get_file_dataflow(
            **kwargs), properties=properties)
        ds._telemetry_info = _DatasetTelemetryInfo(
            entry_point='PythonSDK:OpenDataset')
        return ds

    def get_file_dataflow(self, **kwargs) -> dprep.Dataflow:
        self._check_dataprep()
        dflow = dprep.Dataflow.get_files(self.get_urls(**kwargs))
        dflow = self._filter_file_dataflow(dflow, **kwargs)
        #  skip for now and wait for DataPrep Official release to studio
        #  skip blob uri replacement for other account storage
        if self._blob_account_name == "azureopendatastorage":
            dflow = self._convert_frontdoor_dataflow(dflow)
        return dflow

    def get_tabular_dataset(
            self,
            cols: Optional[List[str]] = None,
            **kwargs) -> TabularDataset:
        dflow = self.get_tabular_dataflow(cols, **kwargs)
        properties = {"OpenDatasets:%s" % key: value for key,
                      value in kwargs.items()} if kwargs else {}
        properties["opendatasets"] = self.id
        ds = TabularDataset._create(dflow, properties=properties)\
            .with_timestamp_columns(fine_grain_timestamp=self._time_column_name)
        ds._telemetry_info = _DatasetTelemetryInfo(
            entry_point='PythonSDK:OpenDataset')
        return ds

    def get_tabular_dataflow(
            self,
            cols: Optional[List[str]] = None,
            **kwargs: dict) -> dprep.Dataflow:
        cols = self._get_cols(cols)
        dflow = self.get_file_dataflow(**kwargs)
        if self._file_extension == "parquet":
            dflow = dflow.read_parquet_file()
        elif self._file_extension == "csv":
            inference_arguments = dprep.InferenceArguments(day_first=True)
            dflow = dflow.parse_delimited(
                separator=",",
                headers_mode=dprep.PromoteHeadersMode.CONSTANTGROUPED,
                encoding=dprep.FileEncoding.UTF8,
                quoting=False,
                skip_rows=0,
                skip_mode=dprep.SkipMode.NONE,
                comment=None)
            dflow = _handle_type_inference_and_path(
                dflow, inference_arguments, True, True)
        elif self._file_extension == "json":
            dflow = dflow.read_json("", dprep.FileEncoding.UTF8)
        else:
            raise Exception("Not support file format(%s).",
                            self._file_extension)
        start_date = self._get_arg(DefaultArgKey.STARTDATE.value, **kwargs)
        end_date = self._get_arg(DefaultArgKey.ENDDATE.value, **kwargs)
        if self._time_column_name:
            if start_date:
                dflow = dflow.filter(
                    dflow[self._time_column_name] >= start_date)
            if end_date:
                dflow = dflow.filter(dflow[self._time_column_name] <= end_date)
        partitions = self._get_partitions()
        for key, value in kwargs.items():
            if not DefaultArgKey.has_value(key) \
                    and (key not in partitions) and value:
                if isinstance(value, list):
                    filters = dflow[key] == value[0]
                    for value_index in range(1, len(value)):
                        filters = filters | value[value_index]
                    dflow = dflow.filter(filters)
                else:
                    dflow = dflow.filter(dflow[key] == value)
        if cols:
            dflow = dflow.keep_columns(cols)
        else:
            dflow = dflow.drop_columns("Path")
        return dflow

    def get_pandas_dataframe(
            self,
            cols: Optional[List[str]] = None,
            **kwargs) -> pd.DataFrame:
        cols = self._get_cols(cols)
        pandas_dfs = []
        tmp_dir = tempfile.mkdtemp()
        download_files = self.get_file_dataset(
            **kwargs).download(target_path=tmp_dir)
        for path in download_files:
            print("[Info] read from %s" % path)
            df = self._read_parquet(path, cols)
            df = self._filter_pandas_dataframe(df, **kwargs)
            if df is not None and df.shape[0] > 0:
                pandas_dfs.append(df)
        if len(pandas_dfs) == 0:
            return None
        df = pd.concat(pandas_dfs)  # type: pd.DataFrame
        try:
            shutil.rmtree(tmp_dir)
        except Exception:
            print(
                "[Warning] Error while deleting temp directory: {0}".format(tmp_dir))
        return df

    def _read_parquet(self, path: str, cols: Optional[List[str]] = None) -> pd.DataFrame:
        ex = None
        for i in range(0, 2):
            try:
                df = pd.read_parquet(path, columns=cols)
                return df
            except Exception as e:
                ex = e
                continue
        raise ex

    def _filter_pandas_dataframe(
            self,
            df: pd.DataFrame,
            **kwargs):
        if df is None or df.shape[0] == 0:
            return None
        start_date = self._get_arg(DefaultArgKey.STARTDATE.value, **kwargs)
        end_date = self._get_arg(DefaultArgKey.ENDDATE.value, **kwargs)
        if self._time_column_name:
            if start_date:
                df = df[df[self._time_column_name] >= start_date]
            if end_date:
                df = df[df[self._time_column_name] <= end_date]
        partitions = self._get_partitions()
        for key, value in kwargs.items():
            if (key in df.columns) \
                    and not DefaultArgKey.has_value(key) \
                    and (key not in partitions) and value:
                if isinstance(value, list):
                    df = df[df[key] in value]
                else:
                    df = df[df[key] == value]
        return df

    def get_spark_dataframe(
            self,
            cols: Optional[List[str]] = None,
            **kwargs):
        cols = self._get_cols(cols)
        targets_dataframe = self.get_file_dataflow(
            **kwargs).to_pandas_dataframe()
        if targets_dataframe.empty:
            return None
        target_paths = targets_dataframe.Path
        wasab_format = "wasbs://%s@%s.blob.core.windows.net/%s"
        paths = [wasab_format % (self._blob_container_name, self._blob_account_name,
                                 self._get_relative_path(path)) for path in target_paths]
        spark = SparkSession.builder.getOrCreate()
        df = spark.read \
            .option("basePath", self.get_data_wasbs_path()) \
            .parquet(*paths)
        if cols:
            df = df.select(cols)
        start_date = self._get_arg(DefaultArgKey.STARTDATE.value, **kwargs)
        end_date = self._get_arg(DefaultArgKey.ENDDATE.value, **kwargs)
        if self._time_column_name is not None and start_date:
            df = df.where(col(self._time_column_name) >= start_date)
            if end_date:
                df = df.where(col(self._time_column_name) <= end_date)
        partitions = self._get_partitions()
        for key, value in kwargs.items():
            if (key in df.columns)\
                    and not DefaultArgKey.has_value(key) \
                    and (key not in partitions) and value:
                if isinstance(value, list):
                    df = df.where(col[key] in value)
                else:
                    df = df.where(col[key] == value)
        return df

    def _filter_file_dataflow(
            self,
            dflow: dprep.Dataflow,
            **kwargs) -> dprep.Dataflow:
        # extract partitions
        if not self._partition_pattern:
            return dflow

        dflow = dflow._add_columns_from_partition_format(
            'Path', self._partition_pattern, False)

        # get all partitions
        partitions = self._get_partitions()

        # build datetime filter if necessary
        start_date = self._get_arg(DefaultArgKey.STARTDATE.value, **kwargs)
        if start_date:
            # type : datetime
            start_date = kwargs[DefaultArgKey.STARTDATE.value]
            start_date = start_date.replace(
                hour=0, minute=0, second=0, microsecond=0)
            if DateTimePartitionName.YEAR.value in partitions:
                datetime_columns = []
                for item in DateTimePartitionName:
                    if item.value in partitions:
                        datetime_columns.append(dflow[item.value])
                    else:
                        if item == DateTimePartitionName.MONTH:
                            start_date = start_date.replace(month=1)
                            datetime_columns.append('1')
                        start_date = start_date.replace(day=1)
                        datetime_columns.append('1')
                        break
                dflow = dflow.add_column(dprep.create_datetime(
                    *datetime_columns), 'PathDate', 'Path')
                end_date = self._get_arg(DefaultArgKey.ENDDATE.value, **kwargs)
                if end_date:
                    limit = self._get_arg(DefaultArgKey.LIMIT.value, **kwargs)
                    if limit and limit > 0:
                        end_date = min(end_date, start_date + self._get_time_step(limit))
                    dflow = dflow.filter((dflow['PathDate'] >= start_date) & (dflow['PathDate'] <= end_date))
                else:
                    dflow = dflow.filter(dflow['PathDate'] >= start_date)
                dflow = dflow.drop_columns('PathDate')

        # build other string filter if necessary
        for partition in partitions:
            if partition in kwargs:
                possibles = kwargs[partition]
                if isinstance(possibles, list) \
                        and all(isinstance(s, str) for s in possibles) \
                        and len(possibles) > 0:
                    filters = dflow[partition] == possibles[0]
                    for possible_index in range(1, len(possibles)):
                        filters = filters | possibles[possible_index]
                    dflow = dflow.filter(filters)
                elif isinstance(possibles, str):
                    dflow = dflow.filter(dflow[partition] == possibles)
        dflow = dflow.drop_columns(partitions)
        return dflow

    def _get_time_step(self, limit: int) -> relativedelta:
        partitions = self._get_partitions()
        if DateTimePartitionName.DAY.value in partitions:
            return relativedelta(days=limit)
        if DateTimePartitionName.MONTH.value in partitions:
            return relativedelta(month=limit)
        if DateTimePartitionName.YEAR.value in partitions:
            return relativedelta(year=limit)

    def _convert_frontdoor_dataflow(
            self,
            dflow: dprep.Dataflow) -> dprep.Dataflow:
        dflow = dflow.add_column(
            expression=dprep.get_stream_name(dflow['Path']),
            new_column_name='FilePath',
            prior_column='Path'
        )

        dflow = dflow.str_replace(
            columns="FilePath",
            value_to_find="blob.core.windows",
            replace_with="azurefd")

        dflow = dflow.add_column(
            expression=dprep.create_http_stream_info(dflow['FilePath']),
            new_column_name="HttpStream",
            prior_column="FilePath")

        dflow = dflow.drop_columns('Path')
        dflow = dflow.rename_columns({'HttpStream': 'Path'})
        dflow = dflow.drop_columns('FilePath')

        return dflow

    def _get_blob_info(self) -> Tuple[str]:
        path = self._registry_dto.blob_location.path
        slash_index = path.find('/')
        if slash_index >= 0:
            blob_container_name = path[:slash_index]
            blob_relative_path = path[(slash_index + 1):]
            if blob_relative_path\
                    and not blob_relative_path.endswith('/')\
                    and not blob_relative_path.endswith('.csv')\
                    and not blob_relative_path.endswith('.json')\
                    and not blob_relative_path.endswith('.tsv')\
                    and not blob_relative_path.endswith('.parquet'):
                blob_relative_path = blob_relative_path + '/'
            return blob_container_name, blob_relative_path

    def _clean_partiton_pattern(self, partition_pattern: str) -> str:
        if partition_pattern:
            return partition_pattern\
                .replace("{yyyy}", "{%s}" % DateTimePartitionName.YEAR.value)\
                .replace("{%M}", "{%s}" % DateTimePartitionName.MONTH.value)\
                .replace("{%d}", "{%s}" % DateTimePartitionName.DAY.value)\
                .lstrip("/")\
                .strip("/")
        else:
            return None

    def _get_partitions(self, partition_pattern: str = None) -> List[str]:
        if partition_pattern:
            return re.findall(r'\{([a-zA-Z0-9_-].*?)\}', partition_pattern)
        if self._partition_pattern:
            return re.findall(r'\{([a-zA-Z0-9_-].*?)\}', self._partition_pattern)
        return []

    def _get_base_url(self) -> str:
        return 'https://%s.blob.core.windows.net/%s/' % (
            self._blob_account_name,
            self._blob_container_name)

    def _get_frontdoor_base_url(self) -> str:
        return 'https://%s.azurefd.net/%s/' % (
            self._blob_account_name,
            self._blob_container_name)

    def _get_relative_path(self, url: str) -> str:
        if "blob.core.windows.net" in url:
            return url.replace(self._get_base_url(), "")
        else:
            return url.replace(self._get_frontdoor_base_url(), "")

    def _get_arg(self, arg_name: str, **kwargs):
        if arg_name in kwargs:
            return kwargs[arg_name]
        return None

    def _get_cols(self, cols: Optional[List[str]] = None) -> List[str]:
        if cols and len(cols) > 0:
            return list(set(cols + self._mandatory_columns))
        return None

    @staticmethod
    def _get_dataset_registry_dto(registry_id: str) -> DatasetRegistryDto:
        local_path = '../data/list_EN-US.json'
        json_str = pkgutil.get_data(__name__, local_path).decode()
        json_data = next(x for x in json.loads(
            json_str) if x["Id"] == registry_id)
        # try:
        #     blob_url = \
        #         'https://azureopendatasets.azureedge.net/apiresource/OpenDatasetsList/list_EN-US.json'
        #     response = requests.get(blob_url)
        #     response.raise_for_status()
        #     response_json = response.json()
        #     json_data = next(
        #         x for x in response_json if x["Id"] == registry_id)
        # except requests.RequestException as ex:
        #     print('[Warning] Caught request exception: %s' % (ex))
        #     print('[Warning] Hit exception when getting storage info'
        #           'from REST API, falling back to default location...')
        # except (ValueError, StopIteration):
        #     print('[Warning] Hit value error when getting storage info'
        #           'from REST API, falling back to default location...')
        data = DatasetRegistryDto.from_dict(
            json_data)  # type: DatasetRegistryDto
        return data

    @staticmethod
    def _check_dataprep():
        from pkg_resources import get_distribution
        try:
            dataset_runtime = get_distribution(
                "azureml-dataset-runtime")
            if dataset_runtime:
                return
            warnings.warn(
                "Please install azureml-dataset-runtime" + "using pip install azureml-dataset-runtime", Warning)
        except Exception:
            # it is possible to have no azureml-dataprep installed
            warnings.warn(
                "Please install azureml-dataset-runtime" + "using pip install azureml-dataset-runtime", Warning)


class BlobAccessorDescriptor(object):
    """Descriptor for Blob Accessor for Lazy load
    """

    def __init__(
            self,
            registry_info: DatasetRegistryInfo,
            mandatory_columns: Optional[List[str]] = None,
            cls=BlobAccessor):
        """
        Descriptor for BlobAccesor for purpose of Lazy load

        :param registry_info: registry id or DatasetRegistryDto for open datasets
        :type registry_info: DatasetRegistryInfo
        :param mandatory_columns: mandatory columns need to be included, defaults to None
        :type mandatory_columns: Optional[List[str]], optional
        """
        self._registry_info = registry_info
        self._mandatory_columns = mandatory_columns
        self._cache = None
        self._cls = cls

    def __get__(self, obj, klass=None) -> BlobAccessor:
        """
        Lazy load and cache for BlobAccessor
        :return: [description]
        :rtype: BlobAccesor
        """
        if not self._cache:
            if klass is None:
                klass = type(obj)
            self._cache = self._cls(
                self._registry_info, self._mandatory_columns)
        return self._cache
