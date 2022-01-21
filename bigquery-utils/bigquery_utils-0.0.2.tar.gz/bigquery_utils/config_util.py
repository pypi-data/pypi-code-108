from datetime import datetime, timedelta, date
from typing import Union, TextIO, List, Iterator, Optional
from pathlib import Path
import logging

import pandas as pd
import yaml

from google.cloud import bigquery
from google.cloud.bigquery import SqlTypeNames, SchemaField, Client
from google.cloud.bigquery.table import TableListItem


class BqConfig:

    def __init__(self,
                 config_path: Union[Path,str]):

        self.config_path = config_path
        self.config = config_path  # setter

    @property
    def config(self) -> dict:
        return self._config

    @config.setter
    def config(self, config_path):
        """
        Deserialize yaml config file to dictionary.
        """
        with open(config_path, "r") as config_yml:
            config = yaml.safe_load(config_yml)
            self._validate_fields(config)
            self._config = config

    @property
    def table_name(self) -> str:
        _table_name = self.config["table_name"]
        if not isinstance(_table_name, str):
            e = "`table_name` must have type `string`"
            raise TypeError(e)
        return _table_name

    @property
    def dataset_name(self) -> str:
        dataset_name = self.config["dataset_name"]
        return dataset_name

    @property
    def table_id(self) -> str:
        return f"{self.dataset_name}.{self.table_name}"

    @property
    def description(self) -> str:
        _description = self.config["description"]
        if not isinstance(_description, str):
            e = "`description` must have type `string`"
            raise TypeError(e)
        return _description

    @property
    def column_mapper(self) -> dict:
        _mapper = self.config["column_mapper"]
        if _mapper is None:
            return _mapper
        if not isinstance(_mapper, dict):
            e = "`column_mapper` must be a dictionary."
            raise TypeError(e)
        return _mapper

    @property
    def type_conversions(self) -> List[dict]:
        _tc = self.config["type_conversions"]

        try:
            self._validate_type_conversions(_tc)
        except:
            raise

        return _tc

    @property
    def time_partitioning(self) -> Optional[bigquery.TimePartitioning]:
        _tp = self.config["time_partitioning"]
        if _tp:
            _type = _tp["type"]
            _field = _tp["field"]
            _expiration_ms = _tp["expiration_ms"]
            try:
                type_ = getattr(bigquery.TimePartitioningType, _type)
                _tp = bigquery.TimePartitioning(type_=type_, field=_field,
                                                expiration_ms=_expiration_ms)
            except:
                raise
        else:
            return None

        return _tp

    @property
    def schema(self) -> List[dict]:
        _schema = self.config["schema"]
        if (
                not isinstance(_schema, list) or
                not all([isinstance(f, dict) for f in _schema])
        ):
            e = "`schema` must be a list of dictionaries."
            raise TypeError(e)
        return _schema

    @property
    def bq_schema(self) -> List[SchemaField]:
        _schema = self.schema
        _bq_schema = []
        for field in _schema:
            _type = field["field_type"]
            field["field_type"] = SqlTypeNames[_type]
            _bq_schema.append(SchemaField(**field))

        return _bq_schema

    @staticmethod
    def _validate_fields(_config) -> None:
        """
        Called by self.config setter.

        Raise exception if expected top-level fields aren't present in self.config.
        """
        _fields = list(_config.keys())
        expected_fields = ["table_name",
                           "description",
                           "dataset_name",
                           "column_mapper",
                           "type_conversions",
                           "schema",
                           "time_partitioning"]

        unexpected = [f for f in _fields if f not in expected_fields]
        missing = [f for f in expected_fields if f not in _fields]

        if any([len(unexpected) > 0, len(missing) > 0]):
            e = "Invalid top-level configuration: \n"
            if len(unexpected) > 0:
                e += f"    - Unexpected fields: {unexpected}\n"
            if len(missing) > 0:
                e += f"    - Missing fields: {missing}"
            raise ValueError(e)

    @staticmethod
    def _validate_type_conversions(_type_conversions: List[dict]) -> None:

        type_lookup = {
            "int": int,
            "float": float,
            "str": str,
            "datetime": datetime
        }

        unexpected = [t["type"] for t in _type_conversions
                      if t["type"] not in type_lookup.keys()]
        if len(unexpected) > 0:
            e = f"Invalid types: {unexpected}. \n" \
                f"Type options include: {list(type_lookup.keys())}."
            raise ValueError(e)

    def __repr__(self):
        table_id = self.table_id
        type_conversions = self.type_conversions
        time_partitioning = self.time_partitioning

        r = f"BqConfig(table_id={table_id}, type_conversions={type_conversions}, time_partitioning={time_partitioning})"
        return r


class BqLoader(BqConfig):

    def __init__(self,
                 client: Client,
                 config_path: str):
        super().__init__(config_path)
        self.client = client

    @property
    def project_name(self):
        return self.client.project

    @property
    def table_id(self):
        return f"{self.project_name}.{super().table_id}"

    def apply_column_mapper(self,
                            df: pd.DataFrame) -> pd.DataFrame:
        _column_mapper = self.column_mapper
        try:
            self._validate_column_mapper(_column_mapper=_column_mapper,
                                         _data=df)
        except:
            raise
        df = df.rename(columns=_column_mapper)
        return df

    def apply_type_conversions(self,
                               df: pd.DataFrame) -> pd.DataFrame:
        """
        Currently takes types: ["datetime","str"]

        """
        _tc = self.type_conversions
        for tc in _tc:
            col_name = tc["name"]
            _type = tc["type"]
            formatter = tc.get("formatter",None)

            if _type == "datetime":
                try:
                    df[col_name] = pd.to_datetime(df[col_name],format=formatter)
                except:
                    e = f"Failed to convert `{col_name}` to `{_type}` with formatter `{formatter}`."
                    raise ValueError(e)
            elif _type == "str":
                try:
                    df[col_name] = df[col_name].astype(str)
                except:
                    e = f"Failed to convert `{col_name}` to `{_type}`."
                    raise ValueError(e)
            elif _type == "int":
                try:
                    df[col_name] = df[col_name].astype(int)
                except:
                    e = f"Failed to convert `{col_name}` to `{_type}`."
                    raise ValueError(e)


        return df

    def table_exists(self) -> bool:
        """
        Returns true if the given table name already exists in the given dataset.
        """
        _table_name = self.table_name
        _dataset_name = self.dataset_name
        _client = self.client

        tables = _client.list_tables(dataset=_dataset_name)  # type: Iterator[TableListItem]
        table_names = [t.table_id for t in tables]
        if _table_name in table_names:
            return True
        else:
            return False

    def create_table(self,
                     if_not_exists: bool = True) -> str:
        """
        If table creation completes without error, returns fully qualified table_id.
        """
        _client = self.client
        _table_id = self.table_id

        if if_not_exists:
            exists = self.table_exists()
            if exists:
                warn = f"Table `{_table_id}` already exists. Skipping table creation."
                logging.info(warn)

        _schema = self.bq_schema
        _time_partitioning = self.time_partitioning
        _description = self.description

        table = bigquery.Table(_table_id, schema=_schema)
        table.time_partitioning = _time_partitioning
        table.description = _description

        table = _client.create_table(table, exists_ok=True, )

        return table.full_table_id

    def load_df(self,
                df: pd.DataFrame,
                write_disposition: str = "WRITE_APPEND",
                from_latest_partition: bool = False):
        """
        :param write_disposition: {"WRITE_APPEND","WRITE_EMPTY","WRITE_TRUNCATE"}
        """
        _client = self.client
        _table_id = self.table_id

        valid_disp = ["WRITE_APPEND", "WRITE_EMPTY", "WRITE_TRUNCATE"]
        if write_disposition not in valid_disp:
            e = f"Invalid argument for write_disposition: `{write_disposition}`. Should be one of: {valid_disp}."
            logging.error(e, exc_info=True)
            raise ValueError(e)

        # apply column_name mappers and schema changes
        df = self.apply_column_mapper(df)
        df = self.apply_type_conversions(df)

        if from_latest_partition:
            bq_query = BqQueryJob(client=_client,
                                  config_path=self.config_path)
            date_latest = bq_query.get_latest_date_partition()



        _bq_schema = self.bq_schema

        job_config = bigquery.LoadJobConfig(schema=_bq_schema,
                                            write_disposition=write_disposition)

        job = _client.load_table_from_dataframe(df,
                                                destination=_table_id,
                                                job_config=job_config)
        job.result()

        log = f"Loaded {job.output_rows} rows. Output bytes: {job.output_bytes}"
        logging.warning(log)

    def load_csv(self,
                 csv_path: str,
                 write_disposition: str = "WRITE_APPEND",
                 encoding: str = "utf-8"):
        """
        :param write_disposition: {"WRITE_APPEND","WRITE_EMPTY","WRITE_TRUNCATE"}
        """
        df = pd.read_csv(csv_path,encoding=encoding)

        df = self.apply_column_mapper(df)
        df = self.apply_type_conversions(df)

        self.load_df(df=df,write_disposition=write_disposition)

    @staticmethod
    def _validate_column_mapper(_column_mapper: dict,
                                _data: pd.DataFrame) -> None:
        """
        Raise error if any mismatch between column mapper and given dataframe.

        Called by `self.apply_column_mapper`.
        """

        source_cols = _data.columns
        mapped_cols = [c for c in _column_mapper.values()]

        # if colnames already mapped
        if all(
                [source in mapped_cols for source in source_cols] and
                [mapped in source_cols for mapped in mapped_cols]
        ):
            return None

        else:
            expected_cols = [c for c in _column_mapper.keys()]

            missing = [c for c in expected_cols if c not in source_cols]
            unexpected = [c for c in source_cols if c not in expected_cols]
            if len(missing) > 0 or len(unexpected) > 0:
                e = "Invalid source columns:"
                if len(missing) > 0:
                    e += f"\n    - Missing expected columns: {missing}"
                if len(unexpected) > 0:
                    e += f"\n    - Unexpected columns: {unexpected}"
                raise ValueError(e)

    @staticmethod
    def _slice_df_by_date(df: pd.DataFrame,
                          dt_field: str,
                          start: datetime,
                          end: datetime = datetime.now()) -> pd.DataFrame:
        start_date = start.date()
        end_date = end.date()

        df_slice = df.loc[df[dt_field].dt.date >= start_date]
        df_slice = df_slice.loc[df_slice[dt_field].dt.date <= end_date]

        return df_slice

    def reconcile_partition(self,
                            df: pd.DataFrame,
                            latest: bool = True,
                            partition_date: Optional[datetime] = None):
        bq_query = BqQueryJob(self.client,config_path=self.config_path)

        # apply schema changes to df
        df = self.apply_column_mapper(df)
        df = self.apply_type_conversions(df)

        dt_col = self.time_partitioning.field

        if latest:
            if partition_date:
                e = "If `latest`=True, any argument given for `partition_date` is ignored."
                raise ValueError(e)
            _partition_date = bq_query.get_latest_date_partition()

        elif partition_date:
            _partition_date = partition_date.date()
        else:
            e = "Must either set `latest`=True or supply a datetime value for `partition_date`."
            raise ValueError(e)

        df_partition = df[df[dt_col].dt.date == _partition_date]
        n_cols = len(df_partition.index)

        if n_cols > 0:
            print("yah")
        else:
            # ensure no records in bigquery table

            e = f"No records found for date `{_partition_date}` in the supplied dataframe."
            raise ValueError(e)

class BqQueryJob(BqConfig):

    def __init__(self,
                 client: Client,
                 config_path: str):

        super().__init__(config_path)
        self.client = client

    @property
    def project_name(self):
        return self.client.project

    @property
    def table_id(self):
        return f"{self.project_name}.{super().table_id}"

    def get_latest_date_partition(self,
                                  start_datetime: datetime = datetime.now(),
                                  max_tries: int = 30) -> datetime:

        _tp = self.time_partitioning
        _tp_field = _tp.field
        _table_id = self.table_id
        _client = self.client

        if _tp is None:
            e = f"Table {_table_id} has no time partitioning."
            logging.error(e)
            raise ValueError(e)
        if _tp.type_ != "DAY":
            e = f"Tipe partitioning type must be `DAY`. Given column has type: `{_tp.type_}`."
            raise ValueError

        _date = start_datetime.date()
        delta = timedelta(days=1)
        tries = 0
        while tries < max_tries:
            print(_date,tries)

            query = f"""
            SELECT * 
            FROM {_table_id}
            WHERE DATE(`{_tp_field}`) = DATE('{str(_date)}')
            """
            query_job = _client.query(query)

            for r in query_job:
                if r:
                    return _date

            tries += 1
            _date -= delta

        if tries >= max_tries:
            e = f"After searching between {start_datetime.date()} and {_date}, no results found."
            raise TimeoutError(e)

    def get_records_by_date_range(self,
                                  start: datetime,
                                  end: datetime,
                                  dt_column: Optional[str] = None) -> Optional[pd.DataFrame]:
        """
        If no records for given date, returns None.

        Only works for time_partitioned tables.
        """

        table_id = self.table_id
        client = self.client

        if dt_column is None:
            try:
                dt_column = self.time_partitioning.field
            except:
                raise

        start_date = start.date()
        end_date = end.date()

        query = f"""
        SELECT * 
        FROM {table_id}
        WHERE DATE(`{dt_column}`) >= DATE("{start_date}") AND
              DATE(`{dt_column}`) <= DATE("{end_date}");    
        """

        query_job = client.query(query)
        results = query_job.result()

        df_date = results.to_dataframe()
        return df_date
