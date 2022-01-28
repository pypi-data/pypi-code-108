"""
    This is a template for a vault demo job. The vault demo job reads from a vault
    and get new configurations and secrets .
"""

from dependencies.exception import exception_handler
from dependencies.spark import start_spark
from dependencies import config, logging
from os import environ
from dependencies.vault import Vault
from random import random
from operator import add


class VaultDemoBase:

    def __init__(self):
        self.spark = self.config = self.log = self.vault = None
        self.unittest_sampling_enabled = True

    def set_spark_session(self, spark_session=None):
        # set spark session
        # temprorary solution for configuring boto3
        if not spark_session:
            self.spark = start_spark(
                app_name='vault_demo_base_job')
        else:
            self.spark = spark_session

    def set_config(self, input_config=None):
        '''
        set configuration
        :param input_config:
        :return:
        '''
        if not input_config:
            self.config = config.get_config()
        else:
            self.config = input_config

    def set_log(self):
        # create logger handler
        if not self.spark:
            raise Exception("Spark session must be set first")

        self.log = logging.Log4j(self.spark)

    @exception_handler
    def set_vault(self, vault_config=False):
        if not vault_config:  # for unittest None may be passed.
            self.vault = Vault(_self_config=self.config, _log_handler=self.log)
        else:
            self.vault = vault_config

    @exception_handler
    def main(self):
        """Main ETL script definition.
        :return: None
        """
        # start Spark application and get Spark session, logger and config
        self.set_spark_session()
        self.set_log()
        self.set_config()
        self.set_vault()

        # set boto3 os.environmen using the aws credentials set for Spark.
        print("self.spark.conf")
        print(self.spark.conf)
        # environ['AWS_ACCESS_KEY_ID'] = self.spark.conf.get("spark.hadoop.fs.s3a.access.key")
        # environ['AWS_SECRET_ACCESS_KEY'] = self.spark.conf.get("spark.hadoop.fs.s3a.secret.key")

        # log that main ETL job is starting
        self.log.info('vault demo is up-and-running')
        # execute ETL pipeline
        partitions = 2
        n = 100000 * partitions

        def f(_):
            x = random() * 2 - 1
            y = random() * 2 - 1
            return 1 if x ** 2 + y ** 2 <= 1 else 0

        count = self.spark.sparkContext.parallelize(range(1, n + 1), partitions).map(f).reduce(add)
        self.log.info("Pi is roughly %f" % (4.0 * count / n))
        config_from_vault = self.vault.config
        self.log.info(config_from_vault)

        # log the success and terminate Spark application
        self.log.info('vault demo is finished')
        self.spark.stop()

        return None


# entry point for PySpark ETL application
if __name__ == '__main__':
    vault_demo_base = VaultDemoBase()
    vault_demo_base.main()
