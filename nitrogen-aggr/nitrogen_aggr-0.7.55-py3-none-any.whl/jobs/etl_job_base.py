import argparse
import traceback
from os import environ
from dependencies import logging, logger
from datetime import datetime
from dependencies.vault import Vault

from dependencies.spark import start_spark
from dependencies.exception import exception_handler
from dependencies.config import (
    load_client_step_config,
    load_framework_config,
    load_project_config,
    load_client_all_step_configs
)
from dependencies.post_gres import CadmiumPostGres
from constants.constants_configs import Config as Constant_Config

# from dependencies.unit_test_data_factory import unit_test_data_factory


"""
    This is a test / template for a etl job. The etl job reads from a text file
    and then transform it to 10 lines and write it back to a parquet file.
"""


class EtlJobBase:
    def __init__(self):
        self.spark = self.config = self.log = self.vault = None
        self.unittest_sampling_enabled = False
        self.ts_start = (
            datetime.now()
        )  # this timestamp is the start of the etl job and will be used later to log to postgresql database
        self.is_input_config_set = False
        self.spark_conf = {}
        self.spark_custom_conf = {}

    def get_custom_spark_conf(self):
        '''
            overwrite this to add custom spark configuration (e.g., mongo uri)
        :return:
        '''
        return {}

    def set_spark_session(self, spark_session=None):
        # set spark session
        # temprorary solution for configuring boto3
        if not spark_session:
            self.spark = start_spark(app_name=self.config["step_name"],
                                     spark_config={**self.spark_conf, **self.spark_custom_conf}
                                     )
        else:
            self.spark = spark_session

        self.spark.sparkContext.setLogLevel(self.config[Constant_Config.LOG_LEVEL])

    def get_base_argparse_configs(self):
        """
            This function relies on load_config function to retrieve dictionaries with
            application configuration elements.

        :return:
        """
        parser = argparse.ArgumentParser(
            description="Argument Parser for Cadmium ETL Job"
        )
        parser.add_argument(
            "--job_id", action="store", type=str, required=True, help="argo jobid"
        )
        parser.add_argument(
            "--ssd_job_id", action="store", type=str, required=False, help="argo ssd jobid"
        )
        parser.add_argument(
            "--client",
            action="store",
            type=str,
            required=True,
            help="Episource Client",
        )
        parser.add_argument(
            "--workflow",
            action="store",
            type=str,
            required=True,
            help="Cadmium Workflow (e.g., ingestion, aggregation)",
        )
        parser.add_argument(
            "--step",
            action="store",
            type=str,
            required=True,
            help="Which step in the Cadmium pipeline is this for?",
        )
        parser.add_argument(
            "--env",
            action="store",
            type=str,
            required=True,
            help="local, dev, test or prod",
        )

        parser.add_argument(
            "--log_level", action="store", type=str, required=False, default="ERROR", help="vault key"
        )
        parser.add_argument(
            "--vault_key", action="store", type=str, required=False, help="vault key",
        )

        # Temporary for boto3
        parser.add_argument(
            "--awskey", action="store", type=str, required=False, help="aws key ",
        )
        parser.add_argument(
            "--awssecret", action="store", type=str, required=False, help="aws secret ",
        )

        parser.add_argument(
            "--project_root_path", action="store", type=str, required=False, help="The cloud data parent location"
        )
        parser.add_argument(
            "--client2",
            action="store",
            type=str,
            required=False,
            help="anonymize source Client",
        )
        # if ssd_job_id is not set, then set it as job_id

        parser = self.get_custom_argparse_configs(parser)
        args = vars(parser.parse_args())

        if 'ssd_job_id' not in args or not args['ssd_job_id']:
            ssd_job_id = args['job_id']
        else:
            ssd_job_id = args['ssd_job_id']

        config = {
            Constant_Config.JOB_ID: args["job_id"],
            Constant_Config.SSD_JOB_ID: ssd_job_id,
            Constant_Config.WORKFLOW: args["workflow"],
            Constant_Config.STEP_NAME: args["step"],
            Constant_Config.CLIENT: args["client"],
            Constant_Config.ENV: args["env"],
            Constant_Config.LOG_LEVEL: args['log_level'],
            Constant_Config.AWS_KEY: args["awskey"],
            Constant_Config.AWS_SECRET: args["awssecret"],
            Constant_Config.VAULT_KEY: args["vault_key"],
            Constant_Config.PROJECT_ROOT_PATH: args["project_root_path"],
            Constant_Config.CLIENT2: args["client2"],
            Constant_Config.LOCATION_SSD: f"{args[Constant_Config.PROJECT_ROOT_PATH]}/{args[Constant_Config.CLIENT]}/ssd",
            Constant_Config.LOCATION_MASTER: f"{args[Constant_Config.PROJECT_ROOT_PATH]}/{args[Constant_Config.CLIENT]}/master",
            Constant_Config.LOCATION_AGGR: f"{args[Constant_Config.PROJECT_ROOT_PATH]}/{args[Constant_Config.CLIENT]}/aggr",
            Constant_Config.LOCATION_REFERENCE: f"{args[Constant_Config.PROJECT_ROOT_PATH]}/{args[Constant_Config.CLIENT]}/references",
            Constant_Config.LOCATION_REPORT: f"{args[Constant_Config.PROJECT_ROOT_PATH]}/{args[Constant_Config.CLIENT]}/report",
            Constant_Config.STEP_CONFIG: {},
        }
        config = self.add_custom_config_fields(config, args)
        return config

    def get_custom_argparse_configs(self, parser):
        """
        Overload this function for adding job-specfic argparse CLI params
        """
        return parser

    def set_config(self, input_config=None):
        """
        set configuration
        :param input_config:
        :return:
        """
        if not input_config:
            self.config = self.get_base_argparse_configs()

            self.set_configs_from_configs_folder()
            # for local testing

        else:
            self.config = input_config
            self.is_input_config_set = True

    def add_custom_config_fields(self, config, args):
        """
        Overload this function to add custom job-specific argparse CLI params
        :param config: dictionary of configs initialized in get_base_argparse_configs
        :param args: any other cli args needing to be passed to create additional configs
        """
        return config

    def set_log(self):
        # create logger handler
        if not self.spark:
            self.log = logger.logger()
            return

        self.log = logging.Log4j(self.spark, config=self.config, ts_start=self.ts_start)

    @exception_handler
    def get_config_for_step(self, step):
        loaded_step_config = load_client_step_config(
            self.config[Constant_Config.CLIENT], step
        )
        if self.vault:
            step_config_from_vault = self.vault.get_step_config(step)
        else:
            step_config_from_vault = {}

        # read configs from /configs/{client}/{step}
        step_config = {
            **loaded_step_config,
            **step_config_from_vault,
        }  # merge two dicts (only works on Python >3.5)
        return step_config

    @exception_handler
    def set_configs_from_configs_folder(self):
        # read configs from /configs/framework

        self.config[Constant_Config.FRAMEWORK] = load_framework_config()

        loaded_step_config = load_client_step_config(
            self.config[Constant_Config.CLIENT],
            self.config[Constant_Config.STEP_NAME]
        )

        # read configs from /configs/{client}/{step}
        self.config[Constant_Config.STEP_CONFIG] = {
            **loaded_step_config,
            **self.config[Constant_Config.STEP_CONFIG],
        }  # merge two dicts (only works on Python >3.5)

        # /configs/{client}/project.yaml
        self.config[Constant_Config.PROJECT_CONFIG] = load_project_config(
            self.config[Constant_Config.CLIENT]
        )

    # @exception_handler
    def set_configs_from_vault(self, vault_config=False):
        """
        self.vault = {
            'project': project config data,
            'step': step specific data
            'metadata': vault metadata
        }
        :param vault_config:
        :return:
        """
        try:
            if vault_config is False:  # for unittest None may be passed.
                self.log.info(self.config)
                self.log.info(self.config[Constant_Config.STEP_NAME])
                self.vault = Vault(
                    _self_config=self.config,
                    _log_handler=self.log,
                    _step=self.config[Constant_Config.STEP_NAME],
                )
            else:
                self.vault = vault_config

            if "step" in self.vault.config:
                self.config[Constant_Config.STEP_CONFIG] = {
                    **self.config[Constant_Config.STEP_CONFIG],
                    **self.vault.config["step"],
                }  # merge two dicts, replace _1 with _2 (only works on Python >3.5)

            # Overrides nitrogen-aggr/configs/default/project.yaml
            # or nitrogen-aggr/configs/{client}/project.yaml,
            # vault path is : nitrogen/flexi/{client}-> key: project
            if  "project" in self.vault.config:
                self.config[Constant_Config.PROJECT_CONFIG] = self.vault.config["project"]

            if  "metadata" in self.vault.config:
                self.config[Constant_Config.VAULT_METADATA] = self.vault.config["metadata"]

        except Exception as e:
            self.log.warn(
                f"Vault integration failed . {e}"
            )
            self.vault = {}
            self.vault['config'] ={}


    @exception_handler
    def log_into_postgresql(self):
        """

        :return:
        """
        postgres_config = self.config[Constant_Config.PROJECT_CONFIG].get("cadmium_postgres_db")
        try:
            postgres = CadmiumPostGres(
                postgres_config["hostname"],
                postgres_config["database_name"],
                postgres_config["user"],
                postgres_config["password"],
                postgres_config["port"],
                True,
            )
            postgres.insert_into_table(
                table_name="nitrogen.job_step",
                columns_tuples="(job_id,workflow_name,step,ts_start,ts_end)",
                placeholders_tuple="(%s,%s,%s, %s,%s)",
                values_tuple=(
                    self.config.get(Constant_Config.JOB_ID),
                    self.config.get(Constant_Config.WORKFLOW),
                    self.config.get(Constant_Config.STEP_NAME),
                    self.ts_start,
                    datetime.now(),
                ),
            )

        except Exception:
            self.log.error(
                "{} Stack Trace: {}".format(
                    "Logging into Postgres Failed.", traceback.format_exc()
                )
            )
            pass

    @exception_handler
    def log_into_postgresql_job_log(self, log):
        """

        :return:
        """
        self.log.info(log)
        postgres_config = self.config[Constant_Config.PROJECT_CONFIG].get("cadmium_postgres_db")
        try:
            postgres = CadmiumPostGres(
                postgres_config["hostname"],
                postgres_config["database_name"],
                postgres_config["user"],
                postgres_config["password"],
                postgres_config["port"],
                True,
            )
            postgres.insert_into_table(
                table_name="nitrogen.job_log",
                columns_tuples="(job_id,workflow_name,step,ts_start, log)",
                placeholders_tuple="(%s,%s,%s, %s, %s)",
                values_tuple=(
                    self.config.get(Constant_Config.JOB_ID),
                    self.config.get(Constant_Config.WORKFLOW),
                    self.config.get(Constant_Config.STEP_NAME),
                    self.ts_start,
                    log
                ),
            )

        except Exception:
            self.log.error(
                "{} Stack Trace: {}".format(
                    "Logging into Postgres Failed.", traceback.format_exc()
                )
            )
            pass

    @exception_handler
    def extract_data(self):
        """Load test_data from Parquet file format.
        :return: Spark DataFrame.
        """

        df = self.spark.read.csv(
            "s3a://epidatalake-test/sandbox/farshad.javadi/SPY.csv", header=True
        )
        return df

    @exception_handler
    def transform_data(self, df):
        """Transform original dataset.
        :param df: Input DataFrame.
        :return: Transformed DataFrame.
        """

        df_transformed = df.select(df["Date"], (df["Close"] - df["Open"]).alias("diff"))
        return df_transformed

    @exception_handler
    def load_data(self, df):
        """Collect test_data locally and write to CSV.
        :param df: DataFrame to print.
        :return: None
        """
        output_file_loc = "s3a://epidatalake-test/sandbox/farshad.javadi/etl_job_out"
        df.write.option("header", "true").parquet(
            output_file_loc, mode="append", compression="uncompressed"
        )
        return None

    @exception_handler
    def run_etl(self):
        """
        Run etl job
        Overload this function if need be, instead of main
        """
        data = self.extract_data()
        data_transformed = self.transform_data(data)
        self.load_data(data_transformed)

        return

    @exception_handler
    def main(self):
        """Main ETL script definition.
        :return: None
        """
        # start Spark application and get Spark session, logger and config
        self.set_config()
        self.set_log() # set python logger
        if not self.is_input_config_set and self.config[Constant_Config.ENV] != "local":
            self.set_configs_from_vault()
        else:
            print("Running local....")

        self.spark_custom_conf = self.get_custom_spark_conf()
        self.set_spark_session()
        self.set_log() # set spark logger
        #self.log.info("Overwriting configs using Vault")

        # log that main ETL job is starting
        self.log.info(f"{self.config['step_name']} ETL job is Up and Running")

        # execute ETL pipeline
        self.run_etl()

        # log the success and terminate Spark application
        self.log.info(f"{self.config['step_name']} ETL job is Finished")
        self.spark.stop()

        if self.config[Constant_Config.ENV] != "local":
            self.log_into_postgresql()
        else:
            values_tuple = (
                self.config.get(Constant_Config.JOB_ID),
                self.config.get(Constant_Config.WORKFLOW),
                self.config.get(Constant_Config.STEP_NAME),
                self.ts_start,
                datetime.now(),
            )

            self.log.info(
                "postgreslog: ENV is set as 'local'. Logging to Postresql will be skipped."
                " The values are {}".format(values_tuple)
            )

        return None


# entry point for PySpark ETL application
if __name__ == "__main__":
    etl_job_base = EtlJobBase()
    etl_job_base.main()
