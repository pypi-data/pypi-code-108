from typing import Dict, Optional

from pyspark.sql import DataFrame
from pyspark.sql.functions import countDistinct
from pyspark.sql.types import (
    ArrayType,
    BooleanType,
    DateType,
    NumericType,
    StringType,
    TimestampType,
)

from aporia.core.context import get_context
from aporia.core.errors import AporiaError, handle_error
from aporia.core.types.field import FieldType

DATA_SAMPLE_SIZE = 10000
UNIQUE_RATIO = 0.25
UNIQUE_VALUES_THRESHOLD = 50


def infer_schema_from_pyspark_dataframe(data: DataFrame) -> Optional[Dict[str, str]]:
    """Infers model version schema from a PySpark DataFrame.

    Field names and types are inferred from column names and types.

    Args:
        data: PySpark DataFrame

    Returns:
        A schema describing the data, as required by the create_model_version function.

    Notes:
        * The field types are inferred using the following logic, based on the data schema:
            * Boolean data type -> boolean field
            * Datetime data type -> datetime field
            * Array data type with numeric elements -> vector field
            * Numeric data type:
                * At most 50 unique values, at most 25% of the values are unique -> categorical field
                * Otherwise -> numeric field
            * String data type:
                * At least 50 unique values, at least 25% of the values are unique -> text field
                * Otherwise -> string field
        * If data contains a column with a type that doesn't match any of the rules
          described above, an error will be raised.
        * If data is a large dataset (> 10000 rows), a sample of the data will be used to infer the schema.

    See Also:
        * <https://spark.apache.org/docs/latest/sql-ref-datatypes.html#data-types>
    """
    context = get_context()
    schema = {}
    # To avoid long computations, use a sample of the data
    data_sample = data.sample(fraction=min(DATA_SAMPLE_SIZE / data.count(), 1.0))
    total_count = data_sample.count()
    try:
        for column in data.schema:
            unique_count = 0
            # Numeric and String columns might be categorical/text fields, fetch the
            # number of unique values to apply our heuristic later
            if isinstance(column.dataType, (NumericType, StringType)):
                unique_count = (
                    data_sample.select(column.name).agg(countDistinct(column.name)).collect()[0][0]
                )

            if isinstance(column.dataType, BooleanType):
                field_type = FieldType.BOOLEAN
            elif isinstance(column.dataType, (TimestampType, DateType)):
                field_type = FieldType.DATETIME
            elif isinstance(column.dataType, ArrayType) and isinstance(
                column.dataType.elementType, NumericType
            ):
                field_type = FieldType.VECTOR
            elif isinstance(column.dataType, NumericType):
                # See the heuristic described in the function notes
                if (
                    total_count > 0
                    and unique_count < UNIQUE_VALUES_THRESHOLD
                    and unique_count < total_count * UNIQUE_RATIO
                ):
                    field_type = FieldType.CATEGORICAL
                else:
                    field_type = FieldType.NUMERIC
            elif isinstance(column.dataType, StringType):
                # See the heuristic described in the function notes
                if (
                    total_count > 0
                    and unique_count > UNIQUE_VALUES_THRESHOLD
                    and unique_count > total_count * UNIQUE_RATIO
                ):
                    field_type = FieldType.TEXT
                else:
                    field_type = FieldType.STRING
            else:
                raise AporiaError(
                    "the type {} of column {} is not supported".format(column.dataType, column.name)
                )

            schema[column.name] = field_type.value

        return schema

    except Exception as err:
        handle_error(
            message_format="Inferring schema from PySpark dataframe failed, {}",
            verbose=context.config.verbose,
            throw_errors=context.config.throw_errors,
            debug=context.config.debug,
            original_exception=err,
        )

    return None
