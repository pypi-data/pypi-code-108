from tecton._internals.sdk_decorators import sdk_public_method
from tecton_spark import conf
from tecton_spark import logger as logger_lib
from tecton_spark.snowflake.snowflake_utils import supress_snowflake_logs

logger = logger_lib.get_logger("SnowflakeContext")


class SnowflakeContext:
    """
    Get access to Snowflake session.
    """

    _current_context_instance = None
    _session = None

    def __init__(self):
        from snowflake.snowpark import Session

        supress_snowflake_logs()

        # We need a default warehouse/database/schema to create things for the spine.
        # TODO(TEC-6997): This should be configurable.
        snowflake_warehouse = "LOAD_WH"
        snowflake_database = "TECTON_DEV_SNOWFLAKE"
        snowflake_schema = conf.get_or_none("TECTON_WORKSPACE").replace("-", "_")

        # Warehouse, database, schema is needed to store temporary table.
        # TODO(TEC-6895): Currently we hard coded the account part here, need to allow clients to change it.
        connection_parameters = {
            "user": conf.get_or_raise("SNOWFLAKE_USER"),
            "password": conf.get_or_raise("SNOWFLAKE_PASSWORD"),
            "account": "tectonpartner",
            "warehouse": snowflake_warehouse,
            "database": snowflake_database,
            "schema": snowflake_schema,
        }
        self._session = Session.builder.configs(connection_parameters).create()

    def get_session(self):
        return self._session

    @classmethod
    @sdk_public_method
    def get_instance(cls) -> "SnowflakeContext":
        """
        Get the singleton instance of SnowflakeContext.
        """
        # If the instance doesn't exist, creates a new SnowflakeContext from
        # an existing Spark context. Alternatively, creates a new Spark context on the fly.
        if cls._current_context_instance is not None:
            return cls._current_context_instance
        else:
            return cls._generate_and_set_new_instance()

    @classmethod
    def _generate_and_set_new_instance(cls) -> "SnowflakeContext":
        logger.debug(f"Generating new Snowflake session")
        cls._current_context_instance = cls()
        return cls._current_context_instance
