from pyspark.sql import SparkSession
from pyspark.sql import HiveContext
from pyspark import SparkConf


def spark_initializer(app_name, args, additional_config=[]):

    input_datastorage_type = ""
    output_datastorage_type = ""

    if "dataStorageType-input-dataset" in args:
        input_datastorage_type = args["dataStorageType-input-dataset"].lower()

    if "dataStorageType-output-dataset" in args:
        output_datastorage_type = args["dataStorageType-output-dataset"].lower()

    if input_datastorage_type.startswith("hive"):

        config_tuples = [
            ('spark.sql.warehouse.dir', '/warehouse/tablespace/managed/hive'),
            ('hive.metastore.uris', args["hiveMetastoreUris-input-dataset"]),
            ('spark.hadoop.dfs.client.use.datanode.hostname', True),
            ('javax.jdo.option.ConnectionUserName', args["hiveUserName-input-dataset"]),
            ('javax.jdo.option.ConnectionPassword', args["hivePassword-input-dataset"]),
            ('hive.server2.enable.doAs', True),
            ('hive.metastore.client.connect.retry.delay', 5),
            ('hive.metastore.client.socket.timeout', 1800)
        ] + additional_config

        config = SparkConf().setAll(config_tuples)

        spark = SparkSession \
            .builder \
            .appName(app_name) \
            .config(conf=config) \
            .enableHiveSupport() \
            .getOrCreate()

    elif output_datastorage_type.startswith("hive"):

        config_tuples = [
            ('spark.sql.warehouse.dir', '/warehouse/tablespace/managed/hive'),
            ('hive.metastore.uris', args["hiveMetastoreUris-output-dataset"]),
            ('spark.hadoop.dfs.client.use.datanode.hostname', True),
            ('javax.jdo.option.ConnectionUserName', args["hiveUserName-output-dataset"]),
            ('javax.jdo.option.ConnectionPassword', args["hivePassword-output-dataset"]),
            ('hive.server2.enable.doAs', True),
            ('hive.metastore.client.connect.retry.delay', 5),
            ('hive.metastore.client.socket.timeout', 1800)
        ] + additional_config

        config = SparkConf().setAll(config_tuples)

        spark = SparkSession \
            .builder \
            .appName(app_name) \
            .config(conf=config) \
            .enableHiveSupport() \
            .getOrCreate()

        # Hive session
        hive = HiveContext(spark)
    else:

        if len(additional_config) is 0:

            spark = SparkSession.builder.appName(app_name).getOrCreate()

        else:

            config = SparkConf().setAll(additional_config)

            spark = SparkSession.builder.appName(app_name).config(conf=config).getOrCreate()

    return spark
