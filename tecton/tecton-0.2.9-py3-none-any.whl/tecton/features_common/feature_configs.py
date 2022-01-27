from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import attr
import pendulum
import pytimeparse
from google.protobuf.duration_pb2 import Duration

from tecton._internals import errors
from tecton.aggregation_functions import AggregationFunction
from tecton_proto.args import feature_view_pb2

AVAILABILITY_SPOT = "spot"
AVAILABILITY_ON_DEMAND = "on_demand"
AVAILABILITY_SPOT_FALLBACK = "spot_with_fallback"
DATABRICKS_SUPPORTED_AVAILABILITY = [AVAILABILITY_SPOT, AVAILABILITY_ON_DEMAND, AVAILABILITY_SPOT_FALLBACK]
EMR_SUPPORTED_AVAILABILITY = [AVAILABILITY_SPOT, AVAILABILITY_ON_DEMAND]
BACKFILL_CONFIG_MODE_PROTO_PREFIX = "BACKFILL_CONFIG_MODE_"
BACKFILL_CONFIG_MODE_MULTIPLE = "multiple_batch_schedule_intervals_per_job"
BACKFILL_CONFIG_MODE_SINGLE = "single_batch_schedule_interval_per_job"


@attr.s(auto_attribs=True)
class FeatureAggregation(object):
    """
    This class describes a single aggregation that is applied in a batch or stream window aggregate feature view.

    :param column: Column name of the feature we are aggregating.
    :type column: str
    :param function: One of the built-in aggregation functions.
    :type function: Union[str, AggregationFunction]
    :param time_windows: Duration to aggregate over in pytimeparse_ format. Examples: ``"30days"``, ``["8hours", "30days", "365days"]``.
    :type time_windows: Union[str, List[str]]

    `function` can be one of predefined numeric aggregation functions, namely ``"count"``, ``"sum"``, ``"mean"``, ``"min"``, ``"max"``. For
    these numeric aggregations, you can pass the name of it as a string. Nulls are handled like Spark SQL `Function(column)`, e.g. SUM/MEAN/MIN/MAX of all nulls is null and COUNT of all nulls is 0.

    In addition to numeric aggregations, :class:`FeatureAggregation` supports "last-n" aggregations that
    will compute the last N distinct values for the column by timestamp. Right now only string column types are supported as inputs
    to this aggregation, i.e., the resulting feature value will be a list of strings. Nulls are not included in the aggregated list.

    You can use it via the ``last_distinct()`` helper function like this:

    .. code-block:: python

        from tecton.aggregation_functions import last_distinct
        my_fv = BatchWindowAggregateFeatureView(
        ...
        aggregations=[FeatureAggregation(
            column='my_column',
            function=last_distinct(15),
            time_windows=['7days'])],
        ...
        )

    .. _pytimeparse: https://pypi.org/project/pytimeparse/
    """

    column: str
    """"""
    function: Union[str, AggregationFunction]
    """One of the built-in aggregation functions (`'count'`, `'sum'`, `'mean'`, `'min'`, `'max'`)."""
    time_windows: Union[str, List[str]]
    """
       Examples: `"30days"`, `["8hours", "30days", "365days"]`.

       .. _pytimeparse: https://pypi.org/project/pytimeparse/
       """

    def _to_proto(self):
        proto = feature_view_pb2.FeatureAggregation()
        proto.column = self.column

        if isinstance(self.function, str):
            proto.function = self.function
        elif isinstance(self.function, AggregationFunction):
            proto.function = self.function.name
            for k, v in self.function.params.items():
                assert isinstance(v, int)
                proto.function_params[k].CopyFrom(feature_view_pb2.ParamValue(int64_value=v))
        else:
            raise TypeError(f"Invalid function type: {type(self.function)}")

        windows = self.time_windows if isinstance(self.time_windows, list) else [self.time_windows]
        for w in windows:
            duration = Duration()
            duration.FromTimedelta(pendulum.duration(seconds=pytimeparse.parse(w)))
            proto.time_window_durations.append(duration)
            proto.time_windows.append(w)
        return proto


@attr.s(auto_attribs=True)
class ExistingClusterConfig:
    """Use an existing Databricks cluster.

    :param existing_cluster_id: ID of the existing cluster.
    """

    existing_cluster_id: str

    def _to_proto(self) -> feature_view_pb2.ExistingClusterConfig:
        proto = feature_view_pb2.ExistingClusterConfig()
        proto.existing_cluster_id = self.existing_cluster_id

        return proto

    def _to_cluster_proto(self) -> feature_view_pb2.ClusterConfig:
        return feature_view_pb2.ClusterConfig(existing_cluster=self._to_proto())


@attr.s(auto_attribs=True)
class EMRClusterConfig:
    """Configuration used to specify materialization cluster options.

    This class describes the attributes of the new clusters which are created in EMR during
    materialization jobs. You can configure options of these clusters, like cluster size and extra pip dependencies.

    :param instance_type: Instance type for the cluster. Must be a valid type as listed in https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-supported-instance-types.html.
        If not specified, a value determined by the Tecton backend is used.
    :param instance_availability: Instance availability for the cluster : "spot" or "on_demand".
        If not specified, default is spot.
    :param number_of_workers: Number of instances for the materialization job. If not specified, a value determined by the Tecton backend is used
    :param first_on_demand: The first `first_on_demand` nodes of the cluster will use on_demand instances. The rest will use the type specified by instance_availability.
        If first_on_demand >= 1, the master node will use on_demand instance type. `first_on_demand` is recommended to be set >= 1 for cluster configs for critical streaming features.
    :param root_volume_size_in_gb: Size of the root volume in GB per instance for the materialization job.
        If not specified, a value determined by the Tecton backend is used.
    :param extra_pip_dependencies: Extra pip dependencies to be installed on the cluster.
    :param spark_config: Map of Spark configuration options and their respective values that will be passed to the
        FeatureView materialization Spark cluster. Currently, we support only the following options: ``spark.driver.memory``, ``spark.driver.memoryOverhead``, ``spark.executor.memory``, ``spark.executor.memoryOverhead``

    Note on ``extra_pip_dependencies``: This is a list of pip package names that will be installed during
    materialization. These libraries will only be available to use inside Spark UDFs. For example, if you set
    ``extra_pip_dependencies=["tensorflow"]``, you can use it in your transformation as shown below.

    An example of EMRClusterConfig.

    .. code-block:: python

        from tecton import batch_feature_view, Input, EMRClusterConfig

        @batch_feature_view(
            inputs={'credit_scores': Input(credit_scores_batch)},
            # Can be an argument instance to a batch feature view decorator
            batch_cluster_config = EMRClusterConfig(
                instance_type = 'm5.2xlarge',
                number_of_workers=4,
                extra_pip_dependencies=["tensorflow==2.2.0"],
            ),
            # Other named arguments to batch feature view
            ...
        )

        # Use the tensorflow package in the UDF since tensorflow will be installed
        # on the EMR Spark cluster. The import has to be within the UDF body. Putting it at the
        # top of the file or inside transformation function won't work.

        @transformation(mode='pyspark')
        def test_transformation(transformation_input):
            from pyspark.sql import functions as F
            from pyspark.sql.types import IntegerType

            def my_tensorflow(x):
                import tensorflow as tf
                return int(tf.math.log1p(float(x)).numpy())

            my_tensorflow_udf = F.udf(my_tensorflow, IntegerType())

            return transformation_input.select(
                'entity_id',
                'timestamp',
                my_tensorflow_udf('clicks').alias('log1p_clicks')
            )
    """

    instance_type: Optional[str] = None
    instance_availability: Optional[str] = None
    number_of_workers: Optional[int] = None
    first_on_demand: Optional[int] = None
    root_volume_size_in_gb: Optional[int] = None
    extra_pip_dependencies: Optional[List[str]] = None
    spark_config: Optional[Dict[str, str]] = None

    def _to_proto(self) -> feature_view_pb2.NewEMRClusterConfig:
        proto = feature_view_pb2.NewEMRClusterConfig()
        if self.instance_type:
            proto.instance_type = self.instance_type
        if self.instance_availability:
            if self.instance_availability not in EMR_SUPPORTED_AVAILABILITY:
                raise ValueError(
                    f"Instance availability {self.instance_availability} is not supported. Choose {AVAILABILITY_SPOT} or {AVAILABILITY_ON_DEMAND}"
                )
            proto.instance_availability = self.instance_availability
        if self.number_of_workers:
            proto.number_of_workers = self.number_of_workers
        if self.first_on_demand:
            proto.first_on_demand = self.first_on_demand
        if self.root_volume_size_in_gb:
            proto.root_volume_size_in_gb = self.root_volume_size_in_gb
        if self.extra_pip_dependencies:
            proto.extra_pip_dependencies.extend(self.extra_pip_dependencies)
        if self.spark_config:
            spark_config = SparkConfigWrapper(self.spark_config)._to_proto()
            proto.spark_config.CopyFrom(spark_config)

        return proto

    def _to_cluster_proto(self) -> feature_view_pb2.ClusterConfig:
        return feature_view_pb2.ClusterConfig(new_emr=self._to_proto())


@attr.s(auto_attribs=True)
class DatabricksClusterConfig:
    """Configuration used to specify materialization cluster options.

    This class describes the attributes of the new clusters which are created in Databricks during
    materialization jobs. You can configure options of these clusters, like cluster size and extra pip dependencies.

    :param instance_type: Instance type for the cluster. Must be a valid type as listed in https://databricks.com/product/aws-pricing/instance-types.
        If not specified, a value determined by the Tecton backend is used.
    :param instance_availability: Instance availability for the cluster : "spot", "on_demand", or "spot_with_fallback".
        If not specified, default is spot.
    :param first_on_demand: The first `first_on_demand` nodes of the cluster will use on_demand instances. The rest will use the type specified by instance_availability.
        If first_on_demand >= 1, the driver node use on_demand instance type.
    :param number_of_workers: Number of instances for the materialization job. If not specified, a value determined by the Tecton backend is used
    :param root_volume_size_in_gb: Size of the root volume in GB per instance for the materialization job.
        If not specified, a value determined by the Tecton backend is used.
    :param extra_pip_dependencies: Extra pip dependencies to be installed on the cluster. Can be PyPI packages or S3 wheels/eggs.
    :param spark_config: Map of Spark configuration options and their respective values that will be passed to the
        FeatureView materialization Spark cluster. Currently, we support only the following options: ``spark.driver.memory``, ``spark.driver.memoryOverhead``, ``spark.executor.memory``, ``spark.executor.memoryOverhead``

    Note on ``extra_pip_dependencies``: This is a list of pip package names that will be installed during
    materialization. These libraries will only be available to use inside Spark UDFs. For example, if you set
    ``extra_pip_dependencies=["tensorflow"]``, you can use it in your transformation as shown below.

    An example of DatabricksClusterConfig.

    .. code-block:: python

        from tecton import batch_feature_view, Input, DatabricksClusterConfig

        @batch_feature_view(
            inputs={'credit_scores': Input(credit_scores_batch)},
            # Can be an argument instance to a batch feature view decorator
            batch_cluster_config = DatabricksClusterConfig(
                instance_type = 'm5.2xlarge',
                spark_config = {"spark.executor.memory" : "12g"}
                extra_pip_dependencies=["tensorflow"],
            ),
            # Other named arguments to batch feature view
            ...
        )

        # Use the tensorflow package in the UDF since tensorflow will be installed
        # on the Databricks Spark cluster. The import has to be within the UDF body. Putting it at the
        # top of the file or inside transformation function won't work.

        @transformation(mode='pyspark')
        def test_transformation(transformation_input):
            from pyspark.sql import functions as F
            from pyspark.sql.types import IntegerType

            def my_tensorflow(x):
                import tensorflow as tf
                return int(tf.math.log1p(float(x)).numpy())

            my_tensorflow_udf = F.udf(my_tensorflow, IntegerType())

            return transformation_input.select(
                'entity_id',
                'timestamp',
                my_tensorflow_udf('clicks').alias('log1p_clicks')
            )
    """

    instance_type: Optional[str] = None
    instance_availability: Optional[str] = None
    number_of_workers: Optional[int] = None
    first_on_demand: Optional[int] = None
    root_volume_size_in_gb: Optional[int] = None
    extra_pip_dependencies: Optional[List[str]] = None
    spark_config: Optional[Dict[str, str]] = None

    def _to_proto(self) -> feature_view_pb2.NewDatabricksClusterConfig:
        proto = feature_view_pb2.NewDatabricksClusterConfig()
        if self.instance_type:
            proto.instance_type = self.instance_type
        if self.instance_availability:
            if self.instance_availability not in DATABRICKS_SUPPORTED_AVAILABILITY:
                raise ValueError(
                    f"Instance availability {self.instance_availability} is not supported. Choose {AVAILABILITY_SPOT}, {AVAILABILITY_ON_DEMAND} or {AVAILABILITY_SPOT_FALLBACK}"
                )
            proto.instance_availability = self.instance_availability
        if self.number_of_workers:
            proto.number_of_workers = self.number_of_workers
        if self.root_volume_size_in_gb:
            proto.root_volume_size_in_gb = self.root_volume_size_in_gb
        if self.first_on_demand:
            proto.first_on_demand = self.first_on_demand
        if self.extra_pip_dependencies:
            # Pretty easy to do e.g. extra_pip_dependencies="tensorflow" by mistake and end up with
            # [t, e, n, s, o, r, f, l, o, w] as a list of dependencies passed to the Spark job.
            #
            # Since this is annoying to debug, we check for that here.
            if isinstance(self.extra_pip_dependencies, str):
                raise ValueError("extra_pip_dependencies must be a list")
            proto.extra_pip_dependencies.extend(self.extra_pip_dependencies)
        if self.spark_config:
            spark_config = SparkConfigWrapper(self.spark_config)._to_proto()
            proto.spark_config.CopyFrom(spark_config)

        return proto

    def _to_cluster_proto(self) -> feature_view_pb2.ClusterConfig:
        return feature_view_pb2.ClusterConfig(new_databricks=self._to_proto())


@attr.s(auto_attribs=True)
class SparkConfigWrapper:
    spark_config_map: Dict[str, str]

    SUPPORTED_OPTS = {
        "spark.driver.memory": "spark_driver_memory",
        "spark.executor.memory": "spark_executor_memory",
        "spark.driver.memoryOverhead": "spark_driver_memory_overhead",
        "spark.executor.memoryOverhead": "spark_executor_memory_overhead",
    }

    def _to_proto(self):
        proto = feature_view_pb2.SparkConfig()
        for opt, val in self.spark_config_map.items():
            if opt not in self.SUPPORTED_OPTS:
                raise ValueError(f"Spark config option {opt} is not supported.")
            setattr(proto, self.SUPPORTED_OPTS[opt], val)

        return proto


@attr.s(auto_attribs=True)
class ParquetConfig:
    """(Config Class) ParquetConfig Class.

    This class describes the attributes of Parquet-based offline feature store storage for the feature definition.
    """

    def _to_proto(self):
        store_config = feature_view_pb2.OfflineFeatureStoreConfig()
        store_config.parquet.SetInParent()
        return store_config


@attr.s(auto_attribs=True)
class DeltaConfig:
    """(Config Class) DeltaConfig Class.

    This class describes the attributes of DeltaLake-based offline feature store storage for the feature definition.
    """

    time_partition_size: Optional[str] = "24h"
    """The size of a time partition in the DeltaLake table, specified as a time string. Defaults to "24h"."""

    def _to_proto(self):
        store_config = feature_view_pb2.OfflineFeatureStoreConfig()
        store_config.delta.time_partition_size.FromTimedelta(
            pendulum.duration(seconds=pytimeparse.parse(self.time_partition_size))
        )
        return store_config


@attr.s(auto_attribs=True)
class DynamoConfig:
    """(Config Class) DynamoConfig Class.

    This class describes the attributes of DynamoDB based online feature store for the feature definition.
    Currently there are no attributes for this class.
    Users can specify online_store = DynamoConfig()
    """

    def _to_proto(self):
        store_config = feature_view_pb2.OnlineStoreConfig()
        store_config.dynamo.enabled = True
        store_config.dynamo.SetInParent()
        return store_config


@attr.s(auto_attribs=True)
class RedisConfig:
    """(Config Class) RedisConfig Class.

    This class describes the attributes of Redis based online feature store for the feature definition.
    Currently there are no attributes for this class.
    Users can specify online_store = RedisConfig()
    Note : Your Tecton deployment needs to be connected to Redis before you can use this configuration option.
    Please contact Tecton support for details.
    """

    def _to_proto(self):
        store_config = feature_view_pb2.OnlineStoreConfig()
        store_config.redis.enabled = True
        store_config.redis.SetInParent()
        return store_config


@attr.s(auto_attribs=True)
class MonitoringConfig:
    """Configuration used to specify monitoring options.

    This class describes the FeatureView materialization freshness and alerting configurations. Requires
    materialization to be enabled. Freshness monitoring requires online materialization to be enabled.
    See `Monitoring Materialization`_ for more details.

    :param monitor_freshness: Defines the enabled/disabled state of monitoring when feature data is materialized to the online feature store.
    :type monitor_freshness: bool
    :param expected_feature_freshness: Threshold used to determine if recently materialized feature data is stale.
        Data is stale if ``now - anchor_time(most_recent_feature_value) > expected_feature_freshness``.
        Value must be at least 2 times the feature tile length.
        If not specified, a value determined by the Tecton backend is used
    :type expected_feature_freshness: str, optional
    :param alert_email: Email that alerts for this FeatureView will be sent to.
    :type alert_email: str, optional

    An example declaration of a MonitorConfig

        .. code-block:: python

            from tecton import batch_feature_view, Input, MonitoringConfig
            # For all named arguments to the batch feature view, see docs for details and types.
            @batch_feature_view(
                inputs={'credit_scores': Input(credit_scores_batch)},
                # Can be an argument instance to a batch feature view decorator
                monitoring = MonitoringConfig(
                    monitor_freshness=True,
                    expected_feature_freshness="1w",
                    alert_email="jules@tecton.ai"
                ),
                # Other named arguments
                ...
            )

            # Your batch feature view function
            def credit_batch_feature_view(credit_scores):
              ...

    .. _Monitoring Materialization: https://docs.tecton.ai/v2/overviews/monitoring_materialization.html
    """

    monitor_freshness: bool
    expected_feature_freshness: Optional[str] = None
    alert_email: Optional[str] = None

    def _to_proto(self) -> feature_view_pb2.MonitoringConfig:
        proto = feature_view_pb2.MonitoringConfig()

        if self.expected_feature_freshness:
            proto.expected_feature_freshness.FromTimedelta(
                pendulum.duration(seconds=pytimeparse.parse(self.expected_feature_freshness))
            )

        proto.alert_email = self.alert_email or ""
        proto.monitor_freshness = self.monitor_freshness
        return proto


@attr.s(auto_attribs=True)
class BackfillConfig:
    """Configuration used to specify backfill options.

    This class configures the backfill behavior of a Batch Feature View. Requires
    materialization to be enabled.

    :param mode: Determines whether Tecton batches backfill jobs:
        [``single_batch_schedule_interval_per_job``, ``multiple_batch_schedule_intervals_per_job``]
    """

    mode: str

    def _to_proto(self) -> feature_view_pb2.BackfillConfig:
        proto = feature_view_pb2.BackfillConfig()
        try:
            proto.mode = feature_view_pb2.BackfillConfigMode.Value(
                BACKFILL_CONFIG_MODE_PROTO_PREFIX + self.mode.upper()
            )
        except ValueError:
            # TODO: add BACKFILL_CONFIG_MODE_SINGLE when supported
            raise errors.InvalidBackfillConfigMode(self.mode, [BACKFILL_CONFIG_MODE_MULTIPLE])
        return proto
