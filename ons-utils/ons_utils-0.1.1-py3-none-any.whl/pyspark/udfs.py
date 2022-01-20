"""A selection of Spark UDFs."""
import numpy as np
from pyspark.sql.types import FloatType, ArrayType
from pyspark.sql.functions import udf


@udf(ArrayType(FloatType()))
def diff(a):
    """Convert numpy.diff to UDF - difference between values in a list."""
    return np.diff(a).tolist()
