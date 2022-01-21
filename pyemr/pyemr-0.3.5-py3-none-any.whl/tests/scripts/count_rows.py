# pylint: skip-file
import sys

import pyspark


def test():
    """ """
    session = pyspark.sql.SparkSession
    builder = session.builder
    conf = ["spark.sql.parquet.datetimeRebaseModeInWrite", "LEGACY"]
    sqlContext = builder.config(*conf).getOrCreate()
    uid = sys.argv[1]
    path = sys.argv[2]
    print(f"path={path}")
    df = sqlContext.read.parquet(path)
    count = df.count()
    print(f"count={count}")
    print(f"Finished:{uid}")


test()
