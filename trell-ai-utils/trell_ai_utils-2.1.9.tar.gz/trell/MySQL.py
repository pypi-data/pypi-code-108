import os
import sqlalchemy
import pandas as pd
import mysql.connector

from trell import aws
from trell.utils import logger
from trell.exceptions import MysqlConnectionError, MysqlDataFetchError, MysqlGenericError


class MySQL:

    """MySQL database utility functions"""

    def __init__(self, db_string):
        """
        initialisation method for MySQL Connector
        :param string db_string: mysql database connection string
        """

        try:
            self.connection = sqlalchemy.create_engine(db_string)
        except Exception as err:
            raise MysqlConnectionError(err)

    def get_data(self, query):
        """
        Fetch data from mysql as a dataframe.
        :param string query: query for fetching data from table
        :return pd.DataFrame data
        """

        try:
            data = pd.read_sql(query + " ;", self.connection)
            logger.debug("data fetched successfully")
            return data
        except Exception as err:
            raise MysqlDataFetchError(err)
        finally:
            self.connection.dispose()

    def execute_query(self, query):
        """
        Execute a query in the mysql table
        :param string query: query for execution in the table
        :return :
        """

        try:
            self.connection.execute(query)
            logger.debug("query executed successfully")
        except Exception as err:
            raise MysqlGenericError(err)
        finally:
            self.connection.dispose()

    def dump_data(self, data, table_name, mode="append"):
        """
        Execute a query in the mysql table
        :param pd.DataFrame data: dataframe to be appended or replaced
        :param string table_name: name of the the target table
        :param string mode: it can be either replace or append
        :return None
        """

        try:
            connection = self.connection
            data.to_sql(name=table_name, con=connection,
                        if_exists=mode, index=False)
            logger.debug("data dumped successfully")
        except Exception as err:
            raise MysqlGenericError(err)
        finally:
            connection.dispose()

    @staticmethod
    def get_prod_data_from_local(query):
        """
        Fetch data from production mysql from local machine via SSH tunnelling (or local port forwarding).
        :param string query: query for execution in the table
        :return :
        """

        try:
            connection = mysql.connector.connect(user=aws.cred['DATA_USER'],
                                                 password=aws.cred['DATA_PWD'],
                                                 host="127.0.0.1",
                                                 port=aws.cred['PORT_1'],
                                                 database="trellDb")

            #connection = sqlalchemy.create_engine(aws.cred['LOCAL_PROD_DB_CONNECTION_STRING'])
        except Exception as err:
            raise MysqlConnectionError(err)

        try:
            df = pd.read_sql(query + " ;", connection)
            logger.debug("data fetched successfully")
            return df
        except Exception as err:
            raise MysqlDataFetchError(err)
        finally:
            connection.close()       # for mysql.connector
            # connection.dispose()   # for sqlalchemy

    @staticmethod
    def get_prod_data(query):
        """
        Fetch data from production mysql as a dataframe.
        :param string query: query for fetching data from table
        :return pd.DataFrame data
        """

        try:
            try:
                connection = sqlalchemy.create_engine(
                    aws.cred['PROD_DB_READ_CONNECTION_STRING'])
                logger.debug("Connected to prod mysql via aws secret manager")
            except:
                connection = sqlalchemy.create_engine(
                    os.environ["PROD_DB_READ_CONNECTION_STRING"])
                logger.debug(
                    "Connected to prod mysql via environment variables")
        except Exception as err:
            raise MysqlConnectionError(err)

        try:
            return pd.read_sql(query + " ;", connection)
            logger.debug("data fetched successfully")
        except Exception as err:
            raise MysqlDataFetchError(err)
        finally:
            connection.dispose()

    @staticmethod
    def execute_query_in_prod(query):
        """
        Execute a query in the production mysql table
        :param string query: query for execution in the table
        :return:
        """

        try:
            try:
                connection = sqlalchemy.create_engine(
                    aws.cred['PROD_DB_WRITE_CONNECTION_STRING'])
                logger.debug("Connected to prod mysql via aws secret manager")
            except:
                connection = sqlalchemy.create_engine(
                    os.environ["PROD_DB_WRITE_CONNECTION_STRING"])
                logger.debug(
                    "Connected to prod mysql via environment variables")
        except Exception as err:
            raise MysqlConnectionError(err)

        try:
            connection.execute(query)
            logger.debug("data executed successfully")
        except Exception as err:
            raise MysqlGenericError(err)
        finally:
            connection.dispose()

    @staticmethod
    def dump_into_prod(data, table_name, mode="append"):
        """
        Push data into production mysql table
        :param pd.DataFrame data: dataframe to be appended or replaced
        :param string table_name: name of the the target table
        :param string mode: it can be either replace or append
        :return:
        """

        try:
            try:
                connection = sqlalchemy.create_engine(
                    aws.cred['PROD_DB_WRITE_CONNECTION_STRING'])
                logger.debug("Connected to prod mysql via aws secret manager")
            except:
                connection = sqlalchemy.create_engine(
                    os.environ["PROD_DB_WRITE_CONNECTION_STRING"])
                logger.debug(
                    "Connected to prod mysql via environment variables")
        except Exception as err:
            raise MysqlConnectionError(err)

        try:
            data.to_sql(name=table_name, con=connection,
                        if_exists=mode, index=False)
            logger.debug("data dumped successfully")
        except Exception as err:
            raise MysqlGenericError(err)
        finally:
            connection.dispose()
