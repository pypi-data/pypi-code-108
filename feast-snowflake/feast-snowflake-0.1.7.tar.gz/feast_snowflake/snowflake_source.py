import random
import string
from typing import Callable, Dict, Iterable, Optional, Tuple
import json
from feast_snowflake.snowflake_type_map import snowflake_to_feast_value_type
from feast.data_source import DataSource
from feast.protos.feast.core.DataSource_pb2 import DataSource as DataSourceProto
from feast.repo_config import RepoConfig
from feast.value_type import ValueType
import pickle


class SnowflakeSource(DataSource):
    def __init__(
        self,
        table: Optional[str] = None,
        query: Optional[str] = None,
        event_timestamp_column: Optional[str] = "",
        created_timestamp_column: Optional[str] = "",
        field_mapping: Optional[Dict[str, str]] = None,
        date_partition_column: Optional[str] = "",
    ):
        """
        Creates a SnowflakeSource object.

        Args:
            database (optional): Snowflake database where the features are stored.
            schema (optional): Snowflake schema in which the table is located.
            table (optional): Snowflake table where the features are stored.
            event_timestamp_column (optional): Event timestamp column used for point in
                time joins of feature values.
            query (optional): The query to be executed to obtain the features.
            created_timestamp_column (optional): Timestamp column indicating when the
                row was created, used for deduplicating rows.
            field_mapping (optional): A dictionary mapping of column names in this data
                source to column names in a feature table or view.
            date_partition_column (optional): Timestamp column used for partitioning.

        """
        super().__init__(
            event_timestamp_column,
            created_timestamp_column,
            field_mapping,
            date_partition_column,
        )

        self._snowflake_options = SnowflakeOptions(
            table=table, query=query
        )

    @staticmethod
    def from_proto(data_source: DataSourceProto):
        """
        Creates a SnowflakeSource from a protobuf representation of a SnowflakeSource.

        Args:
            data_source: A protobuf representation of a SnowflakeSource

        Returns:
            A SnowflakeSource object based on the data_source protobuf.
        """

        assert data_source.HasField("custom_options")

        snowflake_options = SnowflakeOptions.from_proto(data_source.custom_options)

        return SnowflakeSource(
            field_mapping=dict(data_source.field_mapping),
            table=snowflake_options.table,
            event_timestamp_column=data_source.event_timestamp_column,
            created_timestamp_column=data_source.created_timestamp_column,
            date_partition_column=data_source.date_partition_column,
            query=snowflake_options.query,
        )

    def __eq__(self, other):
        if not isinstance(other, SnowflakeSource):
            raise TypeError(
                "Comparisons should only involve SnowflakeSource class objects."
            )

        return (
            self.snowflake_options.table == other.snowflake_options.table
            and self.snowflake_options.query == other.snowflake_options.query
            and self.event_timestamp_column == other.event_timestamp_column
            and self.created_timestamp_column == other.created_timestamp_column
            and self.field_mapping == other.field_mapping
        )

    @property
    def table(self):
        """Returns the table of this snowflake source."""
        return self._snowflake_options.table

    @property
    def query(self):
        """Returns the snowflake options of this snowflake source."""
        return self._snowflake_options.query

    @property
    def snowflake_options(self):
        """Returns the snowflake options of this snowflake source."""
        return self._snowflake_options

    @snowflake_options.setter
    def snowflake_options(self, _snowflake_options):
        """Sets the snowflake options of this snowflake source."""
        self._snowflake_options = _snowflake_options

    def to_proto(self) -> DataSourceProto:
        """
        Converts a SnowflakeSource object to its protobuf representation.

        Returns:
            A DataSourceProto object.
        """
        data_source_proto = DataSourceProto(
            type=DataSourceProto.CUSTOM_SOURCE,
            field_mapping=self.field_mapping,
            custom_options=self.snowflake_options.to_proto(),
        )

        data_source_proto.event_timestamp_column = self.event_timestamp_column
        data_source_proto.created_timestamp_column = self.created_timestamp_column
        data_source_proto.date_partition_column = self.date_partition_column

        return data_source_proto

    def validate(self, config: RepoConfig):
        # As long as the query gets successfully executed, or the table exists,
        # the data source is validated. We don't need the results though.
        self.get_table_column_names_and_types(config)

    def get_table_query_string(self) -> str:
        """Returns a string that can directly be used to reference this table in SQL."""
        if self.table:
            return f'{self.table}'
        else:
            return f"({self.query})"

    @staticmethod
    def source_datatype_to_feast_value_type() -> Callable[[str], ValueType]:
        return snowflake_to_feast_value_type

    def get_table_column_names_and_types(
        self, config: RepoConfig
    ) -> Iterable[Tuple[str, str]]:
        """
        Returns a mapping of column names to types for this snowflake source.

        Args:
            config: A RepoConfig describing the feature repo
        """

        from feast_snowflake.snowflake_offline import SnowflakeOfflineStoreConfig
        from feast_snowflake.snowflake_utils import get_snowflake_conn

        assert isinstance(config.offline_store, SnowflakeOfflineStoreConfig)

        snowflake_conn = get_snowflake_conn(config.offline_store)

        with snowflake_conn as conn:

            if self.table is not None:
                metadata = conn.cursor().execute(
                    f'DESCRIBE TABLE {self.table}'
                ).fetchall()

            else:
                table_name = "".join(
                    random.choice(string.ascii_lowercase) for _ in range(5)
                )
                conn.cursor().execute(
                    f'CREATE TEMPORARY TABLE "{config.offline_store.database}"."{config.offline_store.schema_}"."{table_name}" AS (SELECT * FROM ({self.query}) LIMIT 1)'
                )
                metadata = conn.cursor().execute(
                    f'DESCRIBE TABLE "{config.offline_store.database}"."{config.offline_store.schema_}"."{table_name}"'
                ).fetchall()

        return [(column[0], column[1].upper()) for column in metadata]


class SnowflakeOptions:
    """
    DataSource snowflake options used to source features from snowflake query.
    """

    def __init__(
        self,
        table: Optional[str],
        query: Optional[str],
    ):
        self._table = table
        self._query = query

    @property
    def query(self):
        """Returns the snowflake SQL query referenced by this source."""
        return self._query

    @query.setter
    def query(self, query):
        """Sets the snowflake SQL query referenced by this source."""
        self._query = query

    @property
    def table(self):
        """Returns the table name of this snowflake table."""
        return self._table

    @table.setter
    def table(self, table):
        """Sets the table ref of this snowflake table."""
        self._table = table

    @classmethod
    def from_proto(cls, snowflake_options_proto: DataSourceProto.CustomSourceOptions):
        """
        Creates a SnowflakeOptions from a protobuf representation of a snowflake option.

        Args:
            snowflake_options_proto: A protobuf representation of a DataSource

        Returns:
            A SnowflakeOptions object based on the snowflake_options protobuf.
        """

        snowflake_configuration = pickle.loads(snowflake_options_proto.configuration)

        snowflake_options = cls(
            table=snowflake_configuration['table'],
            query=snowflake_configuration['query'],
        )

        return snowflake_options

    def to_proto(self) -> DataSourceProto.CustomSourceOptions:
        """
        Converts an SnowflakeOptionsProto object to its protobuf representation.

        Returns:
            A SnowflakeOptionsProto protobuf.
        """
        snowflake_options_proto = DataSourceProto.CustomSourceOptions(
            configuration=pickle.dumps(
                {
                    "table": self._table,
                    "query": self._query,
                }
            )
        )
        return snowflake_options_proto
