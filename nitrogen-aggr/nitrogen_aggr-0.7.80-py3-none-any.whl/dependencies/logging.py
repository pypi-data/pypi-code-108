"""
logging
~~~~~~~
This module contains a class that wraps the log4j object instantiated
by the active SparkContext, enabling Log4j logging for PySpark using.
"""
from dependencies.post_gres import CadmiumPostGres
from constants.constants_configs import Config as Constant_Config
import traceback

class Log4j(object):
    """Wrapper class for Log4j JVM object.
    :param spark: SparkSession object.
    """

    def __init__(self, spark, config=None, ts_start=None):
        # get spark app details with which to prefix all messages
        conf = spark.sparkContext.getConf()
        app_id = conf.get('spark.app.id')
        app_name = conf.get('spark.app.name')

        log4j = spark._jvm.org.apache.log4j
        message_prefix = '<' + app_name + ' ' + app_id + '>'
        self.logger = log4j.LogManager.getLogger(message_prefix)
        self.config = config
        self.ts_start = ts_start

    def error(self, message):
        """Log an error.
        :param: Error message to write to log
        :return: None
        """
        self.logger.error(message)
        return None

    def warn(self, message):
        """Log an warning.
        :param: Error message to write to log
        :return: None
        """
        self.logger.warn(message)
        return None

    def info(self, message):
        """Log information.
        :param: Information message to write to log
        :return: None
        """
        self.logger.info(message)
        return None

    def log_into_postgresql_job_log(self, message):
        """

        :return:
        """
        self.info(message)
        if Constant_Config.PROJECT_CONFIG not in self.config or self.config[
            Constant_Config.PROJECT_CONFIG] is None or "postgres" not in self.config[Constant_Config.PROJECT_CONFIG]:
            self.warn("postgres could not be loaded")
            return

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
                columns_tuples="(job_id,ssd_job_id, workflow_name,step,ts_start, log)",
                placeholders_tuple="(%s,%s, %s,%s, %s, %s)",
                values_tuple=(
                    self.config.get(Constant_Config.JOB_ID),
                    self.config.get(Constant_Config.SSD_JOB_ID),
                    self.config.get(Constant_Config.WORKFLOW),
                    self.config.get(Constant_Config.STEP_NAME),
                    self.ts_start,
                    message
                ),
            )
        except Exception:
            self.error(
                "{} Stack Trace: {}".format(
                    "Logging into Postgres Failed.", traceback.format_exc()
                )
            )
            pass