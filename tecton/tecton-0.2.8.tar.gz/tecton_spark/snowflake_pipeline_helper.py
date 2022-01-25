from dataclasses import dataclass
from textwrap import dedent
from typing import *

from pyspark.sql.types import ArrayType
from pyspark.sql.types import BooleanType
from pyspark.sql.types import DoubleType
from pyspark.sql.types import FloatType
from pyspark.sql.types import LongType
from pyspark.sql.types import StringType
from pyspark.sql.types import StructType

from tecton_proto.args.new_transformation_pb2 import NewTransformationArgs as TransformationArgs
from tecton_proto.args.new_transformation_pb2 import TransformationMode
from tecton_proto.args.pipeline_pb2 import DataSourceNode
from tecton_proto.args.pipeline_pb2 import Pipeline
from tecton_proto.args.pipeline_pb2 import PipelineNode
from tecton_proto.args.pipeline_pb2 import TransformationNode
from tecton_proto.data.new_transformation_pb2 import NewTransformation as Transformation
from tecton_proto.data.virtual_data_source_pb2 import VirtualDataSource
from tecton_spark import function_serialization
from tecton_spark.id_helper import IdHelper
from tecton_spark.pipeline_helper import constant_node_to_value
from tecton_spark.pipeline_helper import CONSTANT_TYPE
from tecton_spark.pipeline_helper import get_keyword_inputs
from tecton_spark.pipeline_helper import get_transformation_name
from tecton_spark.pipeline_helper import positional_inputs
from tecton_spark.pipeline_helper import transformation_type_checker
from tecton_spark.templates_utils import load_template

PIPELINE_TEMPLATE = None
ONDEMAND_UDF_TEMPLATE = None
TEMP_CTE_PREFIX = "_TT_CTE_"
SPINE_TABLE_NAME = "_TT_SPINE_TABLE"


def _load_template():
    # TODO: Do this at module loading time once we sort out including the templates in the public SDK build
    global PIPELINE_TEMPLATE
    if not PIPELINE_TEMPLATE:
        PIPELINE_TEMPLATE = load_template("transformation_pipeline.sql.j2")
    global ONDEMAND_UDF_TEMPLATE
    if not ONDEMAND_UDF_TEMPLATE:
        ONDEMAND_UDF_TEMPLATE = load_template("ondemand_udf.sql.j2")


def pipeline_to_sql_string(
    pipeline: Pipeline,
    data_sources: List[VirtualDataSource],
    transformations: List[Transformation],
) -> str:
    _load_template()
    return _PipelineBuilder(
        pipeline,
        data_sources,
        transformations,
    ).get_sql_string()


# Pandas Pipeline (ODFV)
# input_df (snowpark df) is the spine passed in by the user (including request context),
# and it has been augmented with dependent fv fields in of the form "_udf_internal_{input_name}.{feature_field_name}".
# The dataframe we return will be everything from the spine, with the on-demand features added
# TODO: Figure out a way to get the dependent fv fields on tecton apply, this way we can
#      register the udf on apply and avoid doing it adhoc on feature retrival.
def pipeline_to_df_with_input(
    session: "snowflake.snowpark.Session",
    # This should have data from all inputs
    input_df: "snowflake.snowpark.DataFrame",
    pipeline: Pipeline,
    transformations: List[Transformation],
    output_schema: StructType,
    name: str,
    fv_id: str,
) -> "snowflake.snowpark.DataFrame":
    _load_template()
    # TODO: Currently there's a bug in toPandas() call, types may not be casted to the correct type.
    # e.g. Long is currently being casted to object(decimal.Decimal) instead of int64.
    return _PandasPipelineBuilder(
        session=session,
        input_df=input_df,
        output_schema=output_schema,
        name=name,
        pipeline=pipeline,
        transformations=transformations,
        fv_id=fv_id,
    ).get_df()


# Used for j2 template
@dataclass
class _NodeInput:
    name: str
    sql_str: str


# This class is for Snowflake pipelines
class _PipelineBuilder:
    # The value of internal nodes in the tree
    _VALUE_TYPE = Union[str, CONSTANT_TYPE]

    def __init__(
        self,
        pipeline: Pipeline,
        data_sources: List[VirtualDataSource],
        # we only use mode and name from these
        transformations: Union[List[Transformation], List[TransformationArgs]],
    ):
        self._pipeline = pipeline
        self._id_to_ds = {IdHelper.to_string(ds.virtual_data_source_id): ds for ds in data_sources}
        self._id_to_transformation = {IdHelper.to_string(t.transformation_id): t for t in transformations}

    def get_sql_string(self) -> str:
        sql_str = self._node_to_value(self._pipeline.root)
        assert isinstance(sql_str, str)
        return sql_str

    def _node_to_value(self, pipeline_node: PipelineNode) -> _VALUE_TYPE:
        if pipeline_node.HasField("transformation_node"):
            return self._transformation_node_to_sql_str(pipeline_node.transformation_node)
        elif pipeline_node.HasField("data_source_node"):
            return self._data_source_node_to_sql_str(pipeline_node.data_source_node)
        elif pipeline_node.HasField("constant_node"):
            return constant_node_to_value(pipeline_node.constant_node)
        elif pipeline_node.HasField("materialization_context_node"):
            raise ValueError("MaterializationContext is not supported in Snowflake SQL pipelines")
        elif pipeline_node.HasField("request_data_source_node"):
            raise ValueError("RequestDataSource is not supported in Snowflake SQL pipelines")
        elif pipeline_node.HasField("feature_view_node"):
            raise ValueError("Dependent FeatureViews are not supported in Snowflake SQL pipelines")
        else:
            raise KeyError(f"Unknown PipelineNode type: {pipeline_node}")

    def _data_source_node_to_sql_str(self, data_source_node: DataSourceNode) -> str:
        """Creates a sql string from a ds and time parameters."""
        ds = self._id_to_ds[IdHelper.to_string(data_source_node.virtual_data_source_id)]
        # TODO(TEC-5906): Applies time window on the data source
        return self._get_ds_sql_str(ds)

    def _get_ds_sql_str(self, ds: VirtualDataSource) -> str:
        # TODO(TEC-5907): Supports other types of data source
        if ds.HasField("batch_data_source"):
            batch_data_source = ds.batch_data_source
            # TODO(TEC-5907): Supports other types of batch data source
            if batch_data_source.HasField("snowflake"):
                snowflake_args = batch_data_source.snowflake.snowflakeArgs
                if snowflake_args.HasField("table"):
                    # Makes sure we have all the info for the table
                    assert snowflake_args.HasField("database")
                    assert snowflake_args.HasField("schema")
                    sql_str = f"{snowflake_args.database}.{snowflake_args.schema}.{snowflake_args.table}"
                else:
                    raise ValueError(f"Snowflake SQL pipeline does not support query as a batch data source")
            else:
                raise ValueError(f"Snowflake SQL pipeline does not support batch data source: {ds.batch_data_source}")
        else:
            raise ValueError("Snowflake SQL pipeline only supports batch data source")
        return sql_str

    def _transformation_node_to_sql_str(self, transformation_node: TransformationNode) -> str:
        """Recursively translates inputs to values and then passes them to the transformation."""
        args: List[_VALUE_TYPE] = []
        kwargs = {}
        for transformation_input in transformation_node.inputs:
            node_value = self._node_to_value(transformation_input.node)
            if transformation_input.HasField("arg_index"):
                assert len(args) == transformation_input.arg_index
                args.append(node_value)
            elif transformation_input.HasField("arg_name"):
                kwargs[transformation_input.arg_name] = node_value
            else:
                raise KeyError(f"Unknown argument type for Input node: {transformation_input}")

        return self._apply_transformation_function(transformation_node, args, kwargs)

    def _apply_transformation_function(self, transformation_node, args, kwargs) -> str:
        """For the given transformation node, returns the corresponding sql string."""
        transformation = self._id_to_transformation[IdHelper.to_string(transformation_node.transformation_id)]
        user_function = function_serialization.from_proto(transformation.user_function)
        transformation_name = get_transformation_name(transformation)

        if transformation.transformation_mode == TransformationMode.TRANSFORMATION_MODE_SNOWFLAKE_SQL:
            return self._wrap_sql_function(transformation_node, user_function)(*args, **kwargs)
        else:
            raise KeyError(
                f"Invalid transformation mode: {TransformationMode.Name(transformation.transformation_mode)} for a Snowflake SQL pipeline"
            )

    def _wrap_sql_function(
        self, transformation_node: TransformationNode, user_function: Callable[..., str]
    ) -> Callable[..., str]:
        def wrapped(*args, **kwargs):
            transformationInputs = []
            wrapped_args = []
            for i, (arg, node_input) in enumerate(zip(args, positional_inputs(transformation_node))):
                input_str, is_sql = self._wrap_node_inputvalue(node_input, arg)
                cte_name = TEMP_CTE_PREFIX + str(i)
                if is_sql:
                    wrapped_args.append(cte_name)
                    transformationInputs.append(_NodeInput(name=cte_name, sql_str=input_str))
                else:
                    wrapped_args.append(input_str)
            keyword_inputs = get_keyword_inputs(transformation_node)
            wrapped_kwargs = {}
            for k, v in kwargs.items():
                node_input = keyword_inputs[k]
                input_str, is_sql = self._wrap_node_inputvalue(node_input, v)
                if is_sql:
                    cte_name = TEMP_CTE_PREFIX + k
                    wrapped_kwargs[k] = cte_name
                    transformationInputs.append(_NodeInput(name=cte_name, sql_str=input_str))
                else:
                    wrapped_kwargs[k] = input_str
            user_function_sql = dedent(user_function(*wrapped_args, **wrapped_kwargs))
            sql_str = PIPELINE_TEMPLATE.render(inputs=transformationInputs, user_function=user_function_sql)
            transformation_name = get_transformation_name(
                self._id_to_transformation[IdHelper.to_string(transformation_node.transformation_id)]
            )
            transformation_type_checker(transformation_name, sql_str, "snowflake_sql", self._possible_modes())
            return sql_str

        return wrapped

    def _wrap_node_inputvalue(self, node_input, value: _VALUE_TYPE) -> Tuple[Union[CONSTANT_TYPE], bool]:
        """Returns the node value, along with a boolean indicating whether the input is a sql str."""
        if node_input.node.HasField("constant_node"):
            assert (
                isinstance(value, str)
                or isinstance(value, int)
                or isinstance(value, float)
                or isinstance(value, bool)
                or value is None
            )
            return value, False
        elif node_input.node.HasField("data_source_node"):
            # For data source we don't want a bracket around it
            assert isinstance(value, str)
            return value, False
        else:
            # This should be a sql string already, we need to return this with a bracket wrapping it
            # The current implementation will add a round bracket () to all subquery
            assert isinstance(value, str)
            return f"({value})", True

    def _possible_modes(self):
        return ["snowflake_sql", "pipeline"]


# This class is for Pandas pipelines
class _PandasPipelineBuilder:
    def __init__(
        self,
        session: "snowflake.snowpark.Session",
        input_df: "snowflake.snowpark.DataFrame",
        name: str,
        transformations: List[Transformation],
        output_schema: StructType,
        pipeline: Pipeline,
        fv_id: str,
    ):
        self._input_df = input_df
        self._session = session
        self._pipeline = pipeline
        self._name = name
        self._fv_id = fv_id
        self._id_to_transformation = {IdHelper.to_string(t.transformation_id): t for t in transformations}
        # TODO: Need to see how do we support this in Snowflake.
        if len(output_schema.fieldNames()) != 1:
            raise ValueError("Snowflake Pandas pipeline only supports single column output On-Demand FeatureView")
        self._output_schema = output_schema

    def get_df(self) -> "snowflake.snowpark.DataFrame":
        if not self._pipeline.root.HasField("transformation_node"):
            raise ValueError("Root pipeline has to be a transformation for pandas mode")
        return self._transformation_node_to_udf(self._pipeline.root.transformation_node)

    def _transformation_node_to_udf(self, transformation_node: TransformationNode) -> "snowflake.snowpark.DataFrame":
        # Columns in snowflake dataframe have double quotes around them.
        udf_args = [c.strip('"') for c in self._input_df.columns if ("_UDF_INTERNAL" in c)]
        input_columns = []
        input_map = {}
        prefix_map = {}
        # Input for On-Demand can only be a feature view, or request data source
        for transformation_input in transformation_node.inputs:
            input_node = transformation_input.node
            if input_node.HasField("feature_view_node"):
                features = []
                feature_view_node = input_node.feature_view_node
                prefix = f"_UDF_INTERNAL_{feature_view_node.input_name}_{self._fv_id}__".upper()
                for feature in udf_args:
                    if not feature.startswith(prefix):
                        continue
                    input_columns.append(feature)
                    features.append(feature)
                input_map[feature_view_node.input_name] = features
                prefix_map[feature_view_node.input_name] = prefix
            elif input_node.HasField("request_data_source_node"):
                request_data_source_node = input_node.request_data_source_node
                field_names = [field.name for field in request_data_source_node.request_context.schema.fields]
                for input_col in field_names:
                    input_columns.append(input_col)
                input_map[request_data_source_node.input_name] = field_names
                prefix_map[request_data_source_node.input_name] = ""
                # Request context should be in the input_df already
                pass
            else:
                raise ValueError("Snowflake only supports feature view and request data source input.")

        ondemand_udf = self._generate_on_demand_udf(transformation_node, input_map, prefix_map, input_columns)

        from snowflake.snowpark.functions import array_construct, call_udf

        output_df = self._input_df.select(
            *self._input_df.columns,
            call_udf(ondemand_udf, array_construct(*input_columns)).name(self._output_schema[0].name),
        )
        return output_df

    def _generate_on_demand_udf(
        self,
        transformation_node: TransformationNode,
        input_map: Dict[str, List[str]],
        prefix_map: Dict[str, str],
        input_columns: List[str],
    ) -> str:
        """Returns the name of the registered udf"""
        transformation = self._id_to_transformation[IdHelper.to_string(transformation_node.transformation_id)]
        source = transformation.user_function.body
        # TODO(TEC-6901): This line is added to fix a bug with spark udf. We don't need this in Snowflake.
        source = source.replace("from tecton.interactive.data_frame import DataFrame", "")

        # TODO(TEC-6893): We should use Snowpark struct types in the repo directly.
        SPARK_TO_NATIVE_TYPES = {
            LongType(): "int",
            DoubleType(): "float",
            StringType(): "str",
            BooleanType(): "bool",
            ArrayType(LongType()): "list",
            ArrayType(FloatType()): "list",
            ArrayType(DoubleType()): "list",
            ArrayType(StringType()): "list",
        }

        SPARK_TO_SNOWFLAKE_TYPES = {
            LongType(): "NUMBER",
            DoubleType(): "FLOAT",
            StringType(): "STRING",
            BooleanType(): "BOOL",
            ArrayType(LongType()): "ARRAY",
            ArrayType(FloatType()): "ARRAY",
            ArrayType(DoubleType()): "ARRAY",
            ArrayType(StringType()): "ARRAY",
        }

        function_name = self._name
        sql_str = ONDEMAND_UDF_TEMPLATE.render(
            function_name=function_name,
            input_map=input_map,
            prefix_map=prefix_map,
            input_columns=input_columns,
            output_type=SPARK_TO_NATIVE_TYPES[self._output_schema[0].dataType],
            snowflake_output_type=SPARK_TO_SNOWFLAKE_TYPES[self._output_schema[0].dataType],
            output_column=self._output_schema[0].name,
            user_function=source,
        )
        # Register udf function with sql. collect() will force the sql to be executed.
        self._session.sql(sql_str).collect()

        return f"_{function_name}"
