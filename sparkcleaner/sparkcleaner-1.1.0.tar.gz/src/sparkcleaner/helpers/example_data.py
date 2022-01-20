from typing import Any, List
from pyspark.sql import DataFrame as SparkDataFrame
from pyspark.sql import SparkSession

# Create Spark session with max cores to run local tests
spark = SparkSession.builder \
                .master("local[*]") \
                .appName("dfcleaner") \
                .getOrCreate()


def load_example_data() -> SparkDataFrame:
    """Load an example dataset for testing purposes."""
    data: List[Any] = [
            (1, '000000000F251', ' Banana salsa ', 61, True, 20220110),
            (2, None, 'Apple', 56, True, 20201215),
            (3, '000000000253', 'Avocado ', None, False, 19991215),
            (4, '000000000254', ' Pomegrenade party', 0, False, 20210923),
            (5, '000000000255', 'Watermelon-juice', 57, True, 20201113)
            ]
    col_names = ['ID', 'MATERIAL', 'MATERIAL_DESCRIPTION', 'QUANTITY',
                 'ACTIVE', 'MODIFIED_DATE']
    example_df: SparkDataFrame = spark.createDataFrame(data, col_names)
    return example_df
