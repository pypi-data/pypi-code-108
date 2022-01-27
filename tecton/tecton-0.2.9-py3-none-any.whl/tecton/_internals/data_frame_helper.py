from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import attr
import pandas
import pendulum
from pyspark.sql import DataFrame
from pyspark.sql import functions
from pyspark.sql import SparkSession
from pyspark.sql.functions import isnull
from pyspark.sql.functions import to_timestamp
from pyspark.sql.functions import when
from pyspark.sql.utils import AnalysisException

import tecton
from tecton._internals import errors
from tecton._internals.utils import is_bfc_mode_single
from tecton.tecton_context import TectonContext
from tecton_proto.data.feature_view_pb2 import AggregateFeature
from tecton_spark.feature_definition_wrapper import FeatureDefinitionWrapper as FeatureDefinition
from tecton_spark.logger import get_logger
from tecton_spark.materialization_params import MaterializationParams
from tecton_spark.time_utils import add_seconds_to_timestamp
from tecton_spark.time_utils import convert_epoch_to_datetime

TEMPORAL_JOIN_COLUMN = "__tecton_temporal_join_column"
TEMPORARY_COLUMN_NAME = "__temp_time_key"

logger = get_logger("Internal")


@attr.s(auto_attribs=True)
class _FeatureSetQueryBuilder(object):
    spark: SparkSession
    spine_df: Optional[DataFrame]
    # Dataframe against which we're joining this FeatureView.
    # It can be None *only* when we're doing an outer join or
    # for FeatureSetConfigs containing OnDemandFeatureViews.
    parent_df: Optional[DataFrame]
    fd: FeatureDefinition
    override_join_keys: Dict[str, str]
    namespace: str
    features: List[AggregateFeature]
    spine_time_key: Optional[str]
    use_materialized_data: bool
    include_feature_view_timestamp_columns: bool
    join_type: str
    wildcard_key_not_in_spine: bool = False
    all_spine_join_keys: List[str] = []
    spine_time_limits: Optional[pendulum.Period] = None

    def build(self) -> DataFrame:
        """Build the dataframe by joining the given tfeature definition to the parent DF using the provided configs."""
        self._validate()
        # If the outer join is specified, we should extract whole data from the feature definition by providing None spine
        fv_spine_df = None
        if self.fd.is_on_demand:
            fv_spine_df = self._construct_spine_for_on_demand_feature_view()
            time_key = self.spine_time_key
        elif self.join_type != "outer":
            fv_spine_df = self._construct_spine_for_materialized_feature_view()
            # this is None because we're using a modified fv_spine_df that matches the FV time key
            time_key = None
        else:
            # this is None because we're using no spine
            time_key = None
        logger.info(f"{self.fd.name}: Building Tile DataFrame [2/3]")
        feature_df = _get_feature_dataframe_with_limits(
            fd=self.fd,
            spine=fv_spine_df,
            spine_time_key=time_key,
            spine_time_limits=self.spine_time_limits,
            wildcard_key_not_in_spine=self.wildcard_key_not_in_spine,
            use_materialized_data=self.use_materialized_data,
            namespace=self.namespace,
        ).to_spark()

        if self.fd.is_on_demand:
            # This DF will contain the features computed by this iteration as well as any features
            # from previous iterations passed in via the spine.
            # columns are already renamed in pipeline_helper.dataframe_with_input
            return feature_df

        parent_df, feature_df = self._add_temporal_join_columns(self.parent_df, feature_df)
        feature_df = self._rename_fv_cols_to_fs_names(feature_df)
        logger.info(f"{self.fd.name}: Generating Join [3/3]")
        join_df = self._join(parent_df, feature_df)
        return join_df

    def _validate(self):
        """Validates that _FeatureSetQueryBuilder was constructed with a good state before proceeding."""
        # If this feature definition is temporal, then we should also have a spine time key. Throw an error otherwise.
        if self.fd.is_on_demand:
            return
        if not self.spine_time_key:
            raise errors.FV_TIME_KEY_MISSING(self.fd.name)
        if self.spine_df and self.spine_time_key not in self.spine_df.columns:
            raise errors.MISSING_SPINE_COLUMN("timestamp_key", self.spine_time_key, self.spine_df.columns)

        # Assert correct join_type and parent_df
        if self.join_type not in ("left", "outer"):
            raise errors.INTERNAL_ERROR(f"_FeatureSetQueryBuilder called with join_type={self.join_type}")
        if self.join_type == "left" and self.parent_df is None:
            raise errors.INTERNAL_ERROR("_FeatureSetQueryBuilder called with empty spine on left join")

        self.use_materialized_data = _validate_and_return_use_materialized_data(self.fd, self.use_materialized_data)

    def _construct_spine_for_materialized_feature_view(self):
        """Return the spine for the provided BFV/SFV."""
        spine_columns = [c.name for c in self.spine_df.schema]
        override_join_keys = {k: v for (k, v) in self.override_join_keys.items() if k in spine_columns}
        # Rename columns to match the FeatureView using the join config and temporal columns names.
        column_projection = {self.spine_time_key: self.fd.timestamp_key, **override_join_keys}
        df = self.spine_df.select(*column_projection.keys()).distinct()
        for k, v in column_projection.items():
            df = df.withColumnRenamed(k, v)
        return df

    def _construct_spine_for_on_demand_feature_view(self):
        """Return the spine for the provided OnDemandFeatureView.
        If the ODFV has any dependent FeatureViews, they would be computed first into the parent_df.
        """
        return self.parent_df

    def _add_temporal_join_columns(self, spine_df, feature_df):
        """Add temporal join columns to both spine_df & feature_df and return them."""
        # Process the spine
        if spine_df is not None:
            if self.fd.is_temporal_aggregate:
                materialization_params = MaterializationParams.from_feature_definition(self.fd)
                if self.join_type == "left":
                    # Returns a column of the most recently scheduled anchor for the given FV before the time given by time_key
                    # TODO: Account for processing delay.
                    feature_endtime = materialization_params.most_recent_anchor(to_timestamp(self.spine_time_key))
                else:
                    # During the outer join temporal column values represent the end range, so we only need to round down spine_time_key to the closest anchor time
                    feature_endtime = convert_epoch_to_datetime(
                        materialization_params.align_timestamp_left(to_timestamp(self.spine_time_key))
                    )

                # Create a temporary column for the temporal join condition on both sides that we will drop later.
                spine_df = spine_df.withColumn(TEMPORAL_JOIN_COLUMN, feature_endtime)
            else:
                # For temporal features just use the spine's original timestamp, since feature_df has the same timestamps
                spine_time_val = to_timestamp(self.spine_time_key)
                spine_df = spine_df.withColumn(TEMPORAL_JOIN_COLUMN, spine_time_val)
        if feature_df is None:
            return spine_df, None

        # Process FeatureView DataFrame
        timestamp_val = to_timestamp(self.fd.timestamp_key)
        feature_df = feature_df.withColumn(TEMPORAL_JOIN_COLUMN, timestamp_val)
        if self.include_feature_view_timestamp_columns:
            if self.fd.is_temporal_aggregate:
                materialization_params = MaterializationParams.from_feature_definition(self.fd)
                # When displaying to users, represent tile with its end time rather than the tile anchor time.
                slide_interval = materialization_params.get_tile_interval().in_seconds()
                adjusted_timestamp = add_seconds_to_timestamp(to_timestamp(self.fd.timestamp_key), slide_interval)
                feature_df = feature_df.withColumn(self.fd.timestamp_key, adjusted_timestamp.cast("timestamp"))

            feature_df = feature_df.withColumnRenamed(self.fd.timestamp_key, f"{self.fd.name}.{self.fd.timestamp_key}")
        else:
            feature_df = feature_df.drop(self.fd.timestamp_key)

        # Drop duplicates from FV Dataframe - they could be introduced by identical anchor times after dropping the time keys
        return spine_df, feature_df.drop_duplicates()

    def _rename_fv_cols_to_fs_names(self, feature_df):
        """Rename FV columns to FS key space & by prefixing with namespaces if requested."""
        # Rename features if we have a namespace.
        if self.namespace:
            for feature in self.features:
                feature_df = feature_df.withColumnRenamed(feature, f"{self.namespace}.{feature}")
        # Rename FV column names to spine column names to match spine_df
        for spine_column_name, fv_column_name in self.override_join_keys.items():
            feature_df = feature_df.withColumnRenamed(fv_column_name, spine_column_name)
        return feature_df

    def _join(self, parent_df, feature_df) -> DataFrame:
        """Properly join spine_df & feature_df, handling cases such as temporal aggregate vs temporal."""
        # If FV does not have wildcard join_key or if spine contains all the join_keys, simply join
        # feature_df to parent_df on shared set of FV join_keys and timestamp column.
        if not self.wildcard_key_not_in_spine or self.fd.wildcard_join_key is None:
            # Joining columns include all intersecting join keys + time key for temporal features
            # Note, that non-intersecting join keys get cartesian-joined automatically, which is very expensive.
            join_cols = [TEMPORAL_JOIN_COLUMN]
            if parent_df is not None:
                left_join_cols = set(parent_df.columns)
                right_join_cols = self.override_join_keys.keys()
                if left_join_cols - right_join_cols and right_join_cols - left_join_cols:
                    # Cartesian join can only happen during preview - otherwise spine should contain all necessary columns
                    assert self.join_type == "outer"
                    logger.warn(
                        "This FeatureService hits an edge case for which Tecton's preview() method is not optimized, which "
                        "may make this method run slower than usual. To make things faster, try running preview() on individual feature definitions."
                    )
                join_cols += list(left_join_cols & right_join_cols)

            # Do the join if parent_df exists
            df = feature_df if parent_df is None else parent_df.join(feature_df, on=join_cols, how=self.join_type)
        else:
            df = self._join_wildcard_FV_to_wildcard_spine(parent_df, feature_df)

        if self.join_type == "outer":
            df = self._join_for_preview(df)

        return df.drop(TEMPORAL_JOIN_COLUMN)

    def _join_wildcard_FV_to_wildcard_spine(self, parent_df, feature_df) -> DataFrame:
        # Cache `parent_df` as it is used used multiple times below
        parent_df.cache()

        spine_wildcard_key = [
            spine_key for spine_key, fv_key in self.override_join_keys.items() if fv_key == self.fd.wildcard_join_key
        ][0]
        fv_bound_join_keys = list(self.override_join_keys.keys())
        fv_bound_join_keys.remove(spine_wildcard_key)

        # Timestamp key does not necessarily have to be in `spine_join_keys` that will later be used for outer joining.
        # But it is for conveninece to avoid having duplicate timestamp columns after joining.
        spine_join_keys = self.all_spine_join_keys + [TEMPORAL_JOIN_COLUMN]
        if self.spine_time_key:
            spine_join_keys.append(self.spine_time_key)
        s, _ = self._add_temporal_join_columns(self.spine_df, None)
        parent_df_without_features = s.select(spine_join_keys).drop_duplicates()

        # Add all non-self.spine_time_keyildcard join_keys from the other feature definitions in the FeatureService
        # to the `feature_df` so that we can later outer join it with `parent_df`.
        df = feature_df.join(parent_df_without_features, fv_bound_join_keys + [TEMPORAL_JOIN_COLUMN], "inner")

        spine_columns = [column.name for column in parent_df.schema]
        # If parent spine already contains wildcard keys, include it in the outer joining columns.
        if spine_wildcard_key in spine_columns:
            spine_join_keys.append(spine_wildcard_key)

        # Set of fully bound join_keys from the spine can result into different sets of wildcard join_key
        # ranges from different feature definitions.
        # We do outer join to aggregate all the seen values of wildcard join_key column.
        return df.join(parent_df, spine_join_keys, "outer")

    def _join_for_preview(self, feature_df):
        # The outer join means we don't provide spine_df. Therefore we need to somehow generate the time key.
        # Here, we use the time key from the temporal join column. Therefore it's important that the first
        # feature definition in the FeatureSet is temporal aggregate with smallest tile interval, so that the resulting
        # time key has the highest granularity. See _sort_key method for how the feature definitions are sorted.
        if self.spine_time_key not in feature_df.columns:
            df = feature_df.withColumn(self.spine_time_key, functions.col(TEMPORAL_JOIN_COLUMN))
        else:
            # Here we need to basically do an outer join of the original time key and the temporal join column
            # We achieve this by creating a new column with CASE expression (=spine_time_key if not null, otherwise temporal join column)
            df = (
                feature_df.withColumn(
                    TEMPORARY_COLUMN_NAME,
                    when(isnull(self.spine_time_key), functions.col(TEMPORAL_JOIN_COLUMN)).otherwise(
                        feature_df[self.spine_time_key]
                    ),
                )
                .drop(self.spine_time_key)
                .withColumnRenamed(TEMPORARY_COLUMN_NAME, self.spine_time_key)
            )
        # Stable-sort columns in order of (join_keys, timestamp, feature_columns)
        # Note: Some columns may contain dot (.) in name. We can't select them without wrapping them in "`".
        return df.select(*[f"`{col}`" for col in sorted(df.columns, key=self._sort_column_key)])

    def _sort_column_key(self, col: str):
        """Join keys < time key < feature columns"""
        if col in self.fd.join_keys:
            return -1
        if col == self.spine_time_key:
            return 0
        return 1


def _get_time_limits_of_dataframe(df: DataFrame, time_key: str) -> Optional[pendulum.Period]:
    """The returned range is inclusive at the beginning & exclusive at the end: [start, end)."""
    # Fetch lower and upper time bound of the spine so that we can demand the individual feature definitions
    # to limit the amount of data they fetch from the raw data sources.
    # Returns None if df is empty.
    collected_df = df.select(
        functions.min(df[time_key]).alias("time_start"), functions.max(df[time_key]).alias("time_end")
    ).collect()
    time_start = collected_df[0]["time_start"]
    time_end = collected_df[0]["time_end"]
    if time_start is None or time_end is None:
        return None

    # Need to add 1 microsecond to the end time, since the range is exclusive at the end, and we need
    # to make sure to include the very last feature value (in terms of the event timestamp).
    return pendulum.instance(time_end).add(microseconds=1) - pendulum.instance(time_start)


def _sort_key_for_spine(fd_and_config):
    # Fully bound BFV/BWAFV will be processed first.
    # BFV/BWAFV with wildcard join_key will be processed next.
    # ODFVs will be processed last since they may have BFV/BWAFV inputs.
    fv = fd_and_config.feature_definition
    if fv.is_on_demand:
        return 3
    elif fv.wildcard_join_key is None:
        return 1
    return 2


def _sort_key_for_features(fs_config: "tecton.interactive.feature_set_config.FeatureSetConfig"):  # type: ignore
    features = fs_config.features

    def sort_key(column):
        # all non-features will have -1 sort key, meaning they'll be stably ordered at the beginning of the dataframe
        # all features will come after the rest of the columns in the order of `features` coming from the FSC definition
        return features.index(column) if column in features else -1

    return sort_key


def get_features_for_spine(
    spark,
    spine_df: DataFrame,
    feature_set_config,
    timestamp_key: Optional[str],
    from_source: bool = False,
    include_feature_view_timestamp_columns: bool = False,
) -> DataFrame:
    """Get features dataframe given the spine and feature set.

    :param spark: Spark session instance.
    :param spine_df: Spine Dataframe.
    :param feature_set_config: FeatureSetConfig instance.
    :param timestamp_key: Name of the time column in spine_df.
    :param from_source: (Optional) Whether feature values should be recomputed from the original data source.
            If False, we will read the values from the materialized store.
    :param include_feature_view_timestamp_columns: (Optional) Include timestamp columns for every individual feature definition.
    :return: A Spark Dataframe containing feature values for each row in spine_df.
    """
    wildcard_key_not_in_spine = False
    all_spine_join_keys = set()
    # Do some early validation.
    spine_columns = [c.name for c in spine_df.schema]
    for fd_and_config in feature_set_config._get_feature_definitions_and_join_configs():
        if from_source and is_bfc_mode_single(fd_and_config.feature_definition):
            raise errors.FV_BFC_SINGLE_FROM_SOURCE

        # Validate that join key overrides are actually present in the spine SQL's columns.
        # This also ensures the union of join keys across FeatureViews is present in the spine.
        for spine_key, fv_key in fd_and_config.join_keys:
            if spine_key not in spine_columns:
                if fv_key == fd_and_config.feature_definition.wildcard_join_key:
                    wildcard_key_not_in_spine = True
                    wildcard_join_key = fd_and_config.feature_definition.wildcard_join_key
                else:
                    raise errors.FS_SPINE_JOIN_KEY_OVERRIDE_INVALID(spine_key, fv_key, spine_columns)
            else:
                all_spine_join_keys.add(spine_key)

    df = spine_df

    if timestamp_key is not None and timestamp_key not in spine_columns:
        raise errors.FS_SPINE_TIMESTAMP_KEY_INVALID(timestamp_key, spine_columns)

    spine_time_limits = _get_time_limits_of_dataframe(spine_df, timestamp_key) if timestamp_key is not None else None

    total = len(feature_set_config._get_feature_definitions_and_join_configs())
    num = 0
    for fd_and_config in sorted(
        feature_set_config._get_feature_definitions_and_join_configs(), key=_sort_key_for_spine
    ):
        definition = fd_and_config.feature_definition
        parent_df = df
        num += 1
        logger.info(f"{definition.name}: (FV {num}/{total}) Start Build [1/3]")
        df = _FeatureSetQueryBuilder(
            spark=spark,
            spine_df=spine_df,
            all_spine_join_keys=list(all_spine_join_keys),
            wildcard_key_not_in_spine=wildcard_key_not_in_spine,
            parent_df=parent_df,
            fd=definition,
            override_join_keys=dict(fd_and_config.join_keys),
            namespace=fd_and_config.namespace,
            features=fd_and_config.features,
            spine_time_key=timestamp_key,
            use_materialized_data=not from_source,
            include_feature_view_timestamp_columns=include_feature_view_timestamp_columns,
            join_type="left",
            spine_time_limits=spine_time_limits,
        ).build()

    # Seems reasonable that wildcard queries can return 0-k rows per original row in spine.
    if wildcard_key_not_in_spine:
        df = df.filter(functions.col(wildcard_join_key).isNotNull())

    df = df.select([f"`{column}`" for column in sorted(df.columns, key=_sort_key_for_features(feature_set_config))])
    return df


def _sort_key(fd_and_config):
    # The sort order is as follows:
    # 1. Temporal Aggregate features come before Temporal features.
    # 2. Among temporal aggregate features, shorter tile intervals come before longer tile intervals.
    # 3. No order between multiple temporal features.
    # This is an important invariant for _FeatureSetQueryBuilder._join to work (see comments there).
    fd = fd_and_config.feature_definition
    if fd.is_temporal_aggregate:
        return fd.get_tile_interval
    else:
        return pendulum.Duration.max


def _filter_df_for_preview(feature_set_config, df):
    all_join_keys = list(
        {
            spine_join_key
            for fd_and_config in feature_set_config._get_feature_definitions_and_join_configs()
            for spine_join_key, _ in fd_and_config.join_keys
        }
    )
    # Drop duplicates from preview, since it looks pretty bad if we
    # show same join keys with different timestamps in preview
    df = df.drop_duplicates(all_join_keys)
    return df


def _get_feature_dataframe_with_limits(
    fd: FeatureDefinition,
    spine: Union[DataFrame, pandas.DataFrame, None],
    spine_time_key: Optional[str],
    spine_time_limits: Optional[pendulum.Period],
    use_materialized_data: bool,
    wildcard_key_not_in_spine: bool = False,
    validate_time_key=True,
    namespace: Optional[str] = None,
) -> "tecton.interactive.data_frame.DataFrame":
    """
    Returns a Tecton DataFrame that contains the output Feature Transformation of the FeatureView.

    :param spine: (Optional) The spine to join against, either as SQL string or a dataframe.
        If present, the returned data frame will contain rollups for all (join key, temporal key)
        combinations that are required to compute a full frame from the spine.
    :param spine_time_key: (Optional) Name of the time column in spine.
        If unspecified, will default to the name of the timestamp key of the feature definition.
    :param spine_time_limits: (Optional) Spine Time Bounds, precomputed by the caller.
    :param wildcard_key_not_in_spine: Whether or not the wildcard join_key is present in the spine.
        Defaults to False if spine is not specified or if the feature definition has no wildcard join_key.
    :return: A Tecton DataFrame.
    """
    from tecton._internals.feature_views import aggregations
    from tecton._internals import utils
    import tecton

    tc = TectonContext.get_instance()

    spine_df = tc._get_spine_df(spine)

    if validate_time_key:
        if fd.is_on_demand:
            fv_time_key = None
            assert isinstance(spine_df, DataFrame), "Spine must be a DataFrame for OnDemandFeatureView"
        elif fd.is_temporal_aggregate:
            assert fd.trailing_time_window_aggregation
            fv_time_key = fd.trailing_time_window_aggregation.time_key
        else:
            fv_time_key = fd.timestamp_key

        # Validate using either the spine_time_key or fv_time_key
        if spine_time_key is not None:
            utils.validate_spine_dataframe(spine_df, spine_time_key)
            if fv_time_key is not None:
                spine_df = spine_df.withColumnRenamed(spine_time_key, fv_time_key)
        elif fv_time_key is not None:
            utils.validate_spine_dataframe(spine_df, fv_time_key)

    # spine_time_limits refers to the range of feature timestamps.
    # Converting to the corresponding raw data time range.
    raw_data_time_limits = None
    if fd.is_temporal_aggregate or fd.is_temporal:
        raw_data_time_limits = aggregations._get_time_limits(
            fd=fd, spine_df=spine_df, spine_time_limits=spine_time_limits
        )

    use_materialized_data = _validate_and_return_use_materialized_data(fd, use_materialized_data)

    try:
        if fd.is_temporal_aggregate:
            spark_df = aggregations.construct_full_tafv_df(
                tc._spark,
                time_aggregation=fd.trailing_time_window_aggregation,
                join_keys=fd.join_keys,
                feature_store_format_version=fd.get_feature_store_format_version,
                tile_interval=fd.get_tile_interval,
                fd=fd,
                spine_join_keys=fd.join_keys,
                wildcard_join_keys=fd.wildcard_join_key,
                spine_df=spine_df,
                use_materialized_data=use_materialized_data,
                raw_data_time_limits=raw_data_time_limits,
                wildcard_key_not_in_spine=wildcard_key_not_in_spine,
            )
        elif fd.is_on_demand:
            from tecton.interactive.feature_view import OnDemandFeatureView

            spark_df = OnDemandFeatureView(fd.fv)._on_demand_transform_dataframe(
                spine=spine_df,
                use_materialized_data=use_materialized_data,
                namespace=namespace,
            )
        elif fd.is_temporal:
            spark_df = aggregations.construct_full_tfv_or_ft_df(
                tc._spark,
                fd,
                spine_df=spine_df,
                use_materialized_data=use_materialized_data,
                raw_data_time_limits=raw_data_time_limits,
                wildcard_key_not_in_spine=wildcard_key_not_in_spine,
            )
        elif fd.is_feature_table:
            spark_df = aggregations.construct_full_tfv_or_ft_df(
                tc._spark,
                fd,
                spine_df=spine_df,
                use_materialized_data=True,
                raw_data_time_limits=raw_data_time_limits,
                wildcard_key_not_in_spine=wildcard_key_not_in_spine,
            )
        else:
            raise ValueError(f"Invalid feature type for FeatureView {fd.name}")
        return tecton.interactive.data_frame.DataFrame._create(spark_df)
    except AnalysisException as e:
        if "Unable to infer schema for Parquet" in e.desc or "doesn't exist" in e.desc:
            if fd.is_feature_table:
                return tecton.interactive.data_frame.DataFrame._create(
                    tc._spark.createDataFrame([], fd.view_schema.to_spark())
                )
            else:
                raise errors.FV_NO_MATERIALIZED_DATA(fd.name)
        raise


def get_features_for_preview(
    spark,
    feature_set_config: "tecton.interactive.feature_set_config.FeatureSetConfig",
    spine_time_key: Optional[str] = None,
    use_materialized_data: bool = True,
    include_feature_view_timestamp_columns: bool = False,
) -> DataFrame:
    """Get a synthetic features dataframe of all features for the given feature_set used for preview.

    :param spark: Spark session instance
    :param feature_set_config: FeatureSetConfig instance
    :param spine_time_key: (Optional) Name of the time column in the returning Dataframe.
        We default to one of the underlying feature definition's time column name.
    :param use_materialized_data: (Optional) Use materialized data if materialization is enabled
    :param include_feature_view_timestamp_columns: (Optional) Include timestamp columns for every individual feature definition.
    :return: A Spark Dataframe containing synthetic feature values from the given feature_set_config.
    """
    df = None
    for fd_and_config in sorted(feature_set_config._get_feature_definitions_and_join_configs(), key=_sort_key):
        # Use the first WAFV's time key as the time column name in the resulting DF
        if spine_time_key is None:
            spine_time_key = fd_and_config.feature_definition.timestamp_key
        df = _FeatureSetQueryBuilder(
            spark=spark,
            spine_df=None,
            parent_df=df,
            fd=fd_and_config.feature_definition,
            override_join_keys=dict(fd_and_config.join_keys),
            namespace=fd_and_config.namespace,
            features=fd_and_config.features,
            spine_time_key=spine_time_key,
            use_materialized_data=use_materialized_data,
            include_feature_view_timestamp_columns=include_feature_view_timestamp_columns,
            join_type="outer",
        ).build()
    return _filter_df_for_preview(feature_set_config, df)


def _validate_and_return_use_materialized_data(fd, use_materialized_data):
    if fd.is_on_demand:
        return False

    if use_materialized_data and not (fd.writes_to_offline_store and fd.materialization_enabled):
        raise errors.FD_GET_FEATURES_MATERIALIZATION_DISABLED(fd.name)

    return use_materialized_data
