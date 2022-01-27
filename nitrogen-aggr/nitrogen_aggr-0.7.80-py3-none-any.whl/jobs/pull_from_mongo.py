from pyspark.sql import SparkSession
from jobs.etl_job_base import EtlJobBase
from dependencies.exception import exception_handler
from py4j.protocol import Py4JJavaError
from constants.constants_configs import Config as Constant_Config
from pyspark.sql.utils import IllegalArgumentException
import urllib.parse
# Requires:
# pyspark --packages org.mongodb.spark:mongo-spark-connector_2.11:2.4.1
# example mongo-match-string: "{$match : {'SourceFileInfo.ISA_Date' : {$lt: '200900', $gt:'200800'}, 'Client_Name' : /thp.*/i}}"

class PullFromMongo(EtlJobBase):

    def get_custom_spark_conf(self):
        port=self.config[Constant_Config.STEP_CONFIG]['port'] if 'port' in self.config[Constant_Config.STEP_CONFIG] else "27017"
        mongo_uri = f"mongodb://{urllib.parse.quote(self.config[Constant_Config.STEP_CONFIG]['username'])}:{urllib.parse.quote(self.config[Constant_Config.STEP_CONFIG]['password'])}@{self.config[Constant_Config.STEP_CONFIG]['host']}:{port}/{self.config[Constant_Config.STEP_CONFIG]['db']}.{self.config[Constant_Config.STEP_CONFIG]['collection']}"
        print("mongo_uri is {}".format(mongo_uri))
        configs = {
            "spark.mongodb.input.uri": mongo_uri
        }

        return configs

    @exception_handler
    def extract_data(self):
        """
        Loads data from specified MongoDB collection according to Mongo Match String
        For more information on how to create the pipeline match string, see:q
        https://docs.mongodb.com/spark-connector/master/python/aggregation/
        https://docs.mongodb.com/manual/core/aggregation-pipeline/
        https://docs.mongodb.com/manual/reference/operator/aggregation/match/#pipe._S_match
        https://docs.mongodb.com/manual/tutorial/query-documents/#read-operations-query-argument
        """


        # Read Mongodb
        try:
            df = (
                self.spark.read.format("mongo")
                .option("samplePoolSize", 100000)
                .option("sampleSize", 100000)
                .option("pipeline", self.config[Constant_Config.STEP_CONFIG]["mongo_match_string"])
                .load(inferSchema=False)
            )
            '''
            TODO: Enhance pull_from_mongo to not infer Schema but to use the schema provided by us. 
            For reference: This can be done by
            df = (
                spark.read.format("mongo")
                    .option("samplePoolSize", 1000000)
                    .option("pipeline", self.config[Constant_Config.STEP_CONFIG]["mongo_match_string"])
                    .load(schema=new_schmea, inferSchema=False) 
            )
            new_schema can be stored using below 
                # This can be do
                    # temp_rdd = self.spark.parallelize(df.schema)
                    # temp_rdd.coalesce(1).saveAsPickleFile("s3a://path/to/destination_schema.pickle")
                    #
                    # df.printSchema()
            '''
            #df.printSchema()

        except Py4JJavaError as e:
            self.log.error(
                "Error connecting to mongo; check credentials and connection"
            )
            self.log.error(e.java_exception.toString())
            raise
        except IllegalArgumentException:
            self.log.error(
                "Invalid Mongo DB Match string; try verifying in Mongo Shell"
            )
            self.log.error(
                self.config[Constant_Config.STEP_CONFIG]["mongo_match_string"]
            )
            raise

        try:
            assert not df.rdd.isEmpty()
        except AssertionError:
            self.log.error("Query returned 0 records; check query:")
            self.log.error(
                self.config[Constant_Config.STEP_CONFIG]["mongo_match_string"]
            )
            raise

        return df

    def transform_data(self, df):
        return df

    @exception_handler
    def load_data(self, df):

        df.write.json(
            f"{self.config[Constant_Config.STEP_CONFIG]['output_location']}",
            mode="append"
            # compression="gzip"
        )
        return

    def get_custom_argparse_configs(self, parser):
        parser.add_argument(
            "--mongo-match-string",
            type=str,
            action="store",
            required=True,
            help="""Mongodb match string to filter data from db; e.g.: "{$match : {'SourceFileInfo.ISA_Date' : {$lt: '200900', $gt:'200800'}}}" """,
        )
        parser.add_argument(
            "--output-location",
            type=str,
            action="store",
            required=True,
            help="Where do you want the data to be written to in s3? Doc Type & Job ID will be added to the path. Do not end in /",
        )

        return parser

    @exception_handler
    def add_custom_config_fields(self, config, args):
        config[Constant_Config.STEP_CONFIG] = {
            "mongo_match_string": args["mongo_match_string"],
            "output_location" : args["output_location"]
        }


        return config


if __name__ == "__main__":
    run_pulL_from_mongo = PullFromMongo()
    run_pulL_from_mongo.main()
