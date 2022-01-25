# pylint: skip-file
import sys

import pyspark


print(sys.argv)

uuid = sys.argv[1]
out_path = sys.argv[2]

sqlContext = pyspark.sql.SparkSession.builder.config(
    "spark.sql.parquet.datetimeRebaseModeInWrite",
    "LEGACY",
).getOrCreate()

df = sqlContext.createDataFrame(
    [
        (1, "foo"),  # create your data here, be consistent in the types.
        (2, "bar"),
        (2, "bar"),
    ],
    ["id", "label"],  # add your column names here
)

df.write.parquet(out_path)

print(f"Finished:{uuid}")
