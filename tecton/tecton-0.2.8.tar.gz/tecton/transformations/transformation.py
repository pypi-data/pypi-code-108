import functools
from dataclasses import dataclass
from dataclasses import field
from inspect import signature
from typing import Callable
from typing import Dict
from typing import Optional
from typing import Union

from google.protobuf.empty_pb2 import Empty
from pandas import DataFrame as PandasDataFrame
from pyspark.sql import DataFrame
from typeguard import typechecked

from tecton import materialization_context
from tecton._internals import errors
from tecton._internals.fco import Fco
from tecton.basic_info import prepare_basic_info
from tecton.cli.common import get_fco_source_info
from tecton.transformations.const import Constant
from tecton_proto.args.new_transformation_pb2 import NewTransformationArgs as TransformationArgs
from tecton_proto.args.new_transformation_pb2 import TransformationMode
from tecton_proto.args.pipeline_pb2 import Input
from tecton_proto.args.pipeline_pb2 import MaterializationContextNode
from tecton_proto.args.pipeline_pb2 import PipelineNode
from tecton_proto.args.repo_metadata_pb2 import SourceInfo
from tecton_proto.common.id_pb2 import Id
from tecton_spark import function_serialization as func_ser
from tecton_spark.id_helper import IdHelper
from tecton_spark.materialization_context import UnboundMaterializationContext

SPARK_SQL_MODE = "spark_sql"
SNOWFLAKE_SQL_MODE = "snowflake_sql"
PYSPARK_MODE = "pyspark"
PANDAS_MODE = "pandas"

_GLOBAL_TRANSFORMATIONS_LIST = []


@dataclass
class Transformation(Fco):
    """
    (Tecton Object) Transformation class.
    """

    name: str
    mode: str
    user_function: Callable[..., Union[str, DataFrame]]
    description: str
    owner: str
    family: str
    tags: Dict[str, str]
    _source_info: SourceInfo = field(init=False, repr=False)
    _args: TransformationArgs = field(init=False, repr=False)
    _ARGUMENT_TYPE = Union[PipelineNode, Constant, UnboundMaterializationContext]

    def _docstring(self):
        return None

    @property
    def transformer(self):
        return func_ser.from_proto(self._args.user_function)

    def _is_builtin(self):
        return False

    def __post_init__(self):
        self._source_info = get_fco_source_info()

        self._args = TransformationArgs()
        self._args.transformation_id.CopyFrom(IdHelper.from_string(IdHelper.generate_string_id()))
        self._args.info.CopyFrom(
            prepare_basic_info(
                name=self.name, description=self.description, owner=self.owner, family=self.family, tags=self.tags
            )
        )
        if self.mode == SPARK_SQL_MODE:
            transform_mode = TransformationMode.TRANSFORMATION_MODE_SPARK_SQL
            return_type = str
        elif self.mode == SNOWFLAKE_SQL_MODE:
            transform_mode = TransformationMode.TRANSFORMATION_MODE_SNOWFLAKE_SQL
            return_type = str
        elif self.mode == PYSPARK_MODE:
            transform_mode = TransformationMode.TRANSFORMATION_MODE_PYSPARK
            return_type = DataFrame
        elif self.mode == PANDAS_MODE:
            transform_mode = TransformationMode.TRANSFORMATION_MODE_PANDAS
            return_type = PandasDataFrame
        else:
            raise errors.InvalidTransformationMode(self.name, self.mode, [SPARK_SQL_MODE, PYSPARK_MODE])
        if self._docstring() is not None:
            self._args.docstring = self._docstring()
        self._args.transformation_mode = transform_mode
        self._args.user_function.CopyFrom(func_ser.to_proto(self.user_function, return_type))
        self._args.is_builtin = self._is_builtin()
        if not self._is_builtin():
            Fco._register(self)
        _GLOBAL_TRANSFORMATIONS_LIST.append(self)

    def _args_proto(self) -> TransformationArgs:
        return self._args

    def __call__(self, *args, **kwargs) -> PipelineNode:
        wrapper = PipelineNode()
        node = wrapper.transformation_node
        node.transformation_id.CopyFrom(self._args.transformation_id)

        try:
            bound_user_function = signature(self.user_function).bind(*args, **kwargs)
        except TypeError as e:
            raise TypeError(f"while binding inputs to function {self.name}, TypeError: {e}")

        materialization_context_count = 0

        for i, arg in enumerate(args):
            input_ = Input()
            input_.arg_index = i
            input_.node.CopyFrom(self._value_to_node(arg))
            node.inputs.append(input_)
            if isinstance(arg, UnboundMaterializationContext):
                materialization_context_count += 1
        for name, arg in kwargs.items():
            input_ = Input()
            input_.arg_name = name
            input_.node.CopyFrom(self._value_to_node(arg))
            node.inputs.append(input_)
            if isinstance(arg, UnboundMaterializationContext):
                materialization_context_count += 1

        for param in signature(self.user_function).parameters.values():
            if isinstance(param.default, UnboundMaterializationContext):
                if param.name in bound_user_function.arguments:
                    # the user passed in context explicitly, so no need to double register
                    continue
                input_ = Input()
                input_.arg_name = param.name
                input_.node.CopyFrom(self._value_to_node(param.default))
                node.inputs.append(input_)
                if isinstance(param.default, UnboundMaterializationContext):
                    materialization_context_count += 1
            elif param.default is materialization_context:
                raise Exception(
                    "It seems you passed in tecton.materialization_context. Did you mean tecton.materialization_context()?"
                )

        if materialization_context_count > 1:
            raise Exception(f"Only 1 materialization_context can be passed into transformation {self.name}")

        return wrapper

    def _value_to_node(self, arg: _ARGUMENT_TYPE) -> PipelineNode:
        if isinstance(arg, PipelineNode):
            return arg
        elif isinstance(arg, Constant):
            wrapper = PipelineNode()
            node = wrapper.constant_node
            if arg.value is None:
                node.null_const.CopyFrom(Empty())
            elif arg.value_type == str:
                node.string_const = arg.value
            elif arg.value_type == int:
                node.int_const = repr(arg.value)
            elif arg.value_type == float:
                node.float_const = repr(arg.value)
            elif arg.value_type == bool:
                node.bool_const = arg.value
            return wrapper
        elif isinstance(arg, UnboundMaterializationContext):
            wrapper = PipelineNode()
            wrapper.materialization_context_node.CopyFrom(MaterializationContextNode())
            assert wrapper.HasField("materialization_context_node")
            return wrapper
        else:
            raise errors.InvalidTransformInvocation(self.name, arg)

    def _id(self) -> Id:
        return self._args.transformation_id

    def __hash__(self):
        return hash(self.name)


@typechecked
def transformation(
    mode: str,
    name_override: Optional[str] = None,
    description: str = "",
    owner: str = "",
    family: str = "",
    tags: Dict[str, str] = None,
):
    """
    Declares a Transformation that wraps a user function. Transformations are assembled in a pipeline function of a Feature View.

    :param mode: The mode for this transformation should be one of "spark_sql", "pyspark" or "pandas".
    :param name_override: (Optional) Unique, human friendly name override that identifies the Transformation.
    :param description: (Optional) description.
    :param owner: Owner name (typically the email of the primary maintainer).
    :param family: (Optional) Family of this transformation, used to group Tecton Objects.
    :param tags: (Optional) Tags associated with this Tecton Object (key-value pairs of arbitrary metadata).
    :return: A wrapped transformation

    Examples of Spark SQL, PySpark, and Pandas transformation declarations:

        .. code-block:: python

            from tecton import transformation
            import pyspark.sql.DataFrame
            import pandas as pd

            # Create a Spark SQL transformation.
            @transformation(mode="spark_sql",
                            description="Create new column by splitting the string in an existing column")
            def str_split(input_data, column_to_split, new_column_name, delimiter):
                return f'''
                    SELECT
                        *,
                        split({column_to_split}, {delimiter}) AS {new_column_name}
                    FROM {input_data}'''

            # Create a PySpark transformation.
            @transformation(mode="pyspark",
                            description="Add a new column 'user_has_good_credit' if score is > 670")
            def user_has_good_credit_transformation(credit_scores: pyspark.sql.DataFrame) -> pyspark.sql.DataFrame:
                from pyspark.sql import functions as F

                (df = credit_scores.withColumn("user_has_good_credit",
                    F.when(credit_scores["credit_score"] > 670, 1).otherwise(0))
                return df.select("user_id", df["date"].alias("timestamp"), "user_has_good_credit") )

            # Create a Pandas transformation.
            @transformation(mode="pandas",
                            description="Add a new Pandas column if the request amount is > 10000")
            def is_transformation_high(request: pandas.DataFrame) -> pandas.DataFrame:
                import pandas

                df = pd.DataFrame()
                df['amount_is_high'] = (request['amount'] >= 10000).astype('int64')
                return df
    """

    def decorator(user_function):
        transform_name = name_override or user_function.__name__
        transform = Transformation(transform_name, mode, user_function, description, owner, family, tags)
        functools.update_wrapper(wrapper=transform, wrapped=user_function)

        return transform

    return decorator
