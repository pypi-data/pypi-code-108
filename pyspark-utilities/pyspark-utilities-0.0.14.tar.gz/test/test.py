from pysparkutilities.spark_initializer import spark_initializer
from pysparkutilities import ds_initializer

import sys

if __name__ == '__main__':

    print('sys arguments {}'.format(sys.argv))

    # Input args preparation
    args = {}
    for _ in sys.argv[1:]:
        if "=" in _:
            p = _.split('=')
            args[p[0].replace("--", "", 1)] = p[1]

    # Spark initializer + create dataset
    spark = spark_initializer("PySpark-Utilities-Test", args)

    test = [("Finance",10),
            ("Marketing",20),
            ("Sales",30),
            ("IT",40)
            ]

    testColumns = ["dept_name", "dept_id"]
    testDf = spark.createDataFrame(data=test, schema=testColumns)
    testDf.printSchema()
    testDf.show(truncate=False)

    # Write the dataset
    ds_initializer.save_dataset(df=testDf)

    # Load the dataset
    data = ds_initializer.load_dataset(sc=spark, read_all=True)

    # Show dataset
    data.show(truncate=False)
