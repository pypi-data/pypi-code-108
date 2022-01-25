from typing import Optional
from typing import Union

import pandas as pd
from pyspark.sql import DataFrame

import tecton.interactive.data_frame
from tecton import conf
from tecton._internals import errors
from tecton._internals import metadata_service
from tecton._internals.display import Displayable
from tecton._internals.sdk_decorators import sdk_public_method
from tecton.fco import Fco
from tecton.interactive import data_frame
from tecton.tecton_context import TectonContext
from tecton_proto.args.new_transformation_pb2 import TransformationMode
from tecton_proto.data.new_transformation_pb2 import NewTransformation as TransformationProto
from tecton_proto.metadataservice.metadata_service_pb2 import GetTransformationRequest
from tecton_proto.metadataservice.metadata_service_pb2 import GetTransformationSummaryRequest
from tecton_spark import function_serialization as func_ser
from tecton_spark.logger import get_logger
from tecton_spark.materialization_context import BaseMaterializationContext

logger = get_logger("Transformation")
TRANSFORMATION_TEMP_VIEW_PREFIX = "_tecton_transformation_run_"
CONST = Union[str, int, float, bool]


class Transformation(Fco):
    """
    Transformation Class.

    A Transformation is a Tecton Object that contains logic for creating a feature.

    To get a Transformation instance, call :py:func:`tecton.get_transformation`.
    """

    _transformation_proto: TransformationProto

    def __init__(self):
        """ Do not call this directly. Use :py:func:`tecton.get_transformation` """

    @classmethod
    def _fco_type_name_singular_snake_case(cls) -> str:
        return "transformation"

    @classmethod
    def _fco_type_name_plural_snake_case(cls) -> str:
        return "transformations"

    @property
    def _fco_metadata(self):
        return self._transformation_proto.fco_metadata

    @property
    def transformer(self):
        """
        Returns the raw transformation function encapsulated by this Transformation.
        """
        return func_ser.from_proto(self._transformation_proto.user_function, scope={})

    @classmethod
    def _from_proto(cls, transformation: TransformationProto):
        """
        Returns a Transformation instance.

        :param transformations: Transformation proto object.
        """
        obj = Transformation.__new__(cls)
        obj._transformation_proto = transformation
        return obj

    @sdk_public_method
    def run(
        self,
        *inputs: Union["pd.DataFrame", "pd.Series", "DataFrame", CONST],
        context: BaseMaterializationContext = None,
    ) -> data_frame.DataFrame:
        """Run the transformation against inputs.

        :param inputs: positional arguments to the transformation function. For PySpark and SQL transformations,
                       these are either ``pandas.DataFrame`` or ``pyspark.sql.DataFrame`` objects.
                       For on-demand transformations, these are ``pandas.Dataframe`` objects.
        :param context: (Optional) An optional materialization context object.
        """

        if self._transformation_proto.transformation_mode == TransformationMode.TRANSFORMATION_MODE_SPARK_SQL:
            return self._sql_run(*inputs, context=context)
        elif self._transformation_proto.transformation_mode == TransformationMode.TRANSFORMATION_MODE_PYSPARK:
            return self._pyspark_run(*inputs, context=context)
        elif self._transformation_proto.transformation_mode == TransformationMode.TRANSFORMATION_MODE_PANDAS:
            return self._on_demand_run(*inputs)
        raise RuntimeError(f"{self._transformation_proto.transformation_mode} does not support `run(...)`")

    def _sql_run(self, *inputs, context) -> data_frame.DataFrame:
        def create_temp_view(df, dataframe_index):
            df = tecton.interactive.data_frame.DataFrame._create(df).to_spark()
            temp_view = f"{TRANSFORMATION_TEMP_VIEW_PREFIX}{self._fco_metadata.name}_input_{dataframe_index}"
            df.createOrReplaceTempView(temp_view)
            return temp_view

        args = [create_temp_view(v, i) if not isinstance(v, CONST.__args__) else v for i, v in enumerate(inputs)]
        if context is not None:
            args.append(context)

        spark = TectonContext.get_instance()._get_spark()
        return tecton.interactive.data_frame.DataFrame._create(spark.sql(self.transformer(*args)))

    def _pyspark_run(self, *inputs, context) -> data_frame.DataFrame:
        args = [
            tecton.interactive.data_frame.DataFrame._create(v).to_spark() if not isinstance(v, CONST.__args__) else v
            for v in inputs
        ]
        if context is not None:
            args.append(context)

        return tecton.interactive.data_frame.DataFrame._create(self.transformer(*args))

    def _on_demand_run(self, *inputs) -> data_frame.DataFrame:
        for df in inputs:
            if not isinstance(df, pd.DataFrame):
                raise TypeError(f"Input must be of type pandas.DataFrame, but was {type(df)}.")

        return tecton.interactive.data_frame.DataFrame._create(self.transformer(*inputs))

    def summary(self):
        """
        Displays a human readable summary of this Transformation.
        """
        request = GetTransformationSummaryRequest()
        request.fco_locator.id.CopyFrom(self._transformation_proto.transformation_id)
        request.fco_locator.workspace = self.workspace

        response = metadata_service.instance().GetTransformationSummary(request)
        return Displayable.from_fco_summary(response.fco_summary)


@sdk_public_method
def get_transformation(name, workspace_name: Optional[str] = None) -> Transformation:
    """
    Fetch an existing :class:`Transformation` by name.

    :param name: An unique name of the registered Transformation.

    :return: A :class:`Transformation` class instance.

    :raises TectonValidationError: if a Transformation with the passed name is not found.
    """
    request = GetTransformationRequest()
    request.name = name
    request.workspace = workspace_name or conf.get_or_none("TECTON_WORKSPACE")

    response = metadata_service.instance().GetTransformation(request)
    if not response.HasField("new_transformation"):
        raise errors.FCO_NOT_FOUND(Transformation, name)
    return Transformation._from_proto(response.new_transformation)
