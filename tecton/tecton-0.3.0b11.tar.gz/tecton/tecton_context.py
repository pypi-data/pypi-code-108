from typing import Any
from typing import Dict
from typing import Optional
from typing import Union

import pandas
import pendulum
import pyspark

import tecton.interactive.data_frame
import tecton_spark
from tecton._internals import errors
from tecton._internals import utils
from tecton._internals.sdk_decorators import sdk_public_method
from tecton._internals.spark_utils import get_or_create_spark_session
from tecton_spark import logger as logger_lib
from tecton_spark.feature_definition_wrapper import FeatureDefinitionWrapper as FeatureDefinition


logger = logger_lib.get_logger("TectonContext")


class TectonContext:
    """
    Execute Spark SQL queries; access various utils.
    """

    _current_context_instance = None
    _config: Dict[str, Any] = {}

    def __init__(self, spark):
        self._spark = spark

    @classmethod
    def _set_config(cls, custom_spark_options=None):
        """
        Sets the configs for TectonContext instance.
        To take effect it must be called before any calls to TectonContext.get_instance().

        :param custom_spark_options: If spark session gets created by TectonContext, custom spark options/
        """
        cls._config = {"custom_spark_options": custom_spark_options}

    @classmethod
    @sdk_public_method
    def get_instance(cls) -> "TectonContext":
        """
        Get the singleton instance of TectonContext.
        """
        # If the instance doesn't exist, creates a new TectonContext from
        # an existing Spark context. Alternatively, creates a new Spark context on the fly.
        if cls._current_context_instance is not None:
            return cls._current_context_instance
        else:
            return cls._generate_and_set_new_instance()

    @classmethod
    def _generate_and_set_new_instance(cls) -> "TectonContext":
        logger.debug(f"Generating new Spark session")
        spark = get_or_create_spark_session(
            cls._config.get("custom_spark_options"),
        )
        cls._current_context_instance = cls(spark)
        return cls._current_context_instance

    def _list_tables(self):
        """
        Lists the registered tables.

        :return: An array of tables.
        """
        tables = []
        spark_databases = self._spark.catalog.listDatabases()

        for db in spark_databases:
            spark_tables = self._spark.catalog.listTables(db.name)
            for t in spark_tables:
                if db.name == "default":
                    tables.append(t.name)
                else:
                    tables.append("{database}.{table}".format(database=db.name, table=t.name))
        return tables

    # A user-facing validation method
    @classmethod
    def validate_spine_type(cls, spine: Union[pyspark.sql.dataframe.DataFrame, pandas.DataFrame, None]):
        if not isinstance(spine, (pyspark.sql.dataframe.DataFrame, pandas.DataFrame, type(None))):
            raise errors.INVALID_SPINE_TYPE(type(spine))

    # Validates and returns a spark df constructed from the spine.
    # This is an internal method and supports more types than what we support in the user-facing
    # methods, see validate_spine_type
    def _get_spine_df(
        self,
        spine: Union[str, dict, pyspark.sql.dataframe.DataFrame, list, pandas.DataFrame, pyspark.RDD, None],
    ):
        df = None

        # sql
        if isinstance(spine, str):
            df = self._spark.sql(spine)
        # entity dict
        elif isinstance(spine, dict):
            # TODO(there is probably a much more efficient way to have spark join against temporary single row tables)
            df = self._spark.createDataFrame(pandas.DataFrame([spine]))
        elif isinstance(spine, tecton.interactive.data_frame.DataFrame):
            df = spine.to_spark()
        elif isinstance(spine, pyspark.sql.dataframe.DataFrame):
            df = spine
        elif isinstance(spine, (pandas.DataFrame, list, pyspark.RDD)):
            df = self._spark.createDataFrame(spine)
        elif spine is None:
            pass
        else:
            raise errors.INVALID_SPINE_TYPE(type(spine))
        return df

    @sdk_public_method
    def execute(
        self,
        spine: Union[str, dict, pyspark.sql.dataframe.DataFrame, list, pandas.DataFrame, pyspark.RDD, None],
        feature_set_config: Optional["tecton_spark.feature_set_config.FeatureSetConfig"] = None,
        timestamp_key: Optional[str] = None,
        include_feature_view_timestamp_columns: bool = False,
        use_materialized_data: bool = True,
    ):
        """
        Runs a SQL query against Tecton's registered data sources.

        :param spine: Instance of [str, dict, pyspark.sql.dataframe.DataFrame, pandas.DataFrame, list, pyspark.RDD, NoneType].
            `str` = SQL;
            `dict` = Creates a fake table of just one row with the keys as columns;
            `pyspark.sql.dataframe.DataFrame` = instance of spark DataFrame;
            `pandas.DataFrame`, `list`, and `pyspark.RDD` are passed directly to :func:`~pyspark.sql.SQLContext.createDataFrame`
            `NoneType` = No spine, which means extracting all features from the given feature_set_config.
        :param feature_set_config: (Optional) Instance of :class:`~tecton.FeatureSetConfig`.
        :param timestamp_key: (Optional) Name of the time column in the returning Dataframe. The column must be of type Spark timestamp.
            If spine is provided, needs to match time key in it.
            If spine is not provided, we default to one of the underlying feature definition's time column name.
        :param include_feature_view_timestamp_columns: (Optional) Include timestamp columns for every individual FeatureView/FeatureTable.
        :param use_materialized_data: (Optional) Use materialized data if materialization is enabled.
        :return: A Tecton DataFrame.
        """

        df = self._get_spine_df(spine)
        utils.validate_spine_dataframe(df, timestamp_key)

        from tecton._internals import data_frame_helper

        if feature_set_config is not None:
            if spine is not None:
                df = data_frame_helper.get_features_for_spine(
                    self._spark,
                    df,
                    feature_set_config,
                    timestamp_key=timestamp_key,
                    from_source=not use_materialized_data,
                    include_feature_view_timestamp_columns=include_feature_view_timestamp_columns,
                )
            else:
                df = data_frame_helper.get_features_for_preview(
                    self._spark,
                    feature_set_config,
                    spine_time_key=timestamp_key,
                    use_materialized_data=use_materialized_data,
                    include_feature_view_timestamp_columns=include_feature_view_timestamp_columns,
                )
            # Equivalent to df.explain(extended=True) but returns string instead of printing it
            query_execution_plan = df._jdf.queryExecution().toString()
            logger.log(logger_lib.TRACE, f"Query execution plan for FeatureSetConfig:\n{query_execution_plan}")

        df = utils.filter_internal_columns(df)
        return tecton.interactive.data_frame.DataFrame._create(df)

    def _register_temp_views_for_feature_view(
        self,
        fd: FeatureDefinition,
        register_stream=False,
        raw_data_time_limits: Optional[pendulum.Period] = None,
    ):
        for ds in fd.data_sources:
            self._register_temp_view_for_data_source(
                ds, register_stream=register_stream, raw_data_time_limits=raw_data_time_limits
            )

    def _register_temp_view_for_data_source(
        self,
        data_source_proto,
        register_stream=False,
        raw_data_time_limits: Optional[pendulum.Period] = None,
    ):
        from tecton_spark.data_source_helper import register_temp_view_for_data_source

        name = data_source_proto.fco_metadata.name

        register_temp_view_for_data_source(
            self._spark,
            data_source_proto,
            register_stream=register_stream,
            raw_data_time_limits=raw_data_time_limits,
            name=name,
        )

    def _get_spark(self):
        return self._spark
