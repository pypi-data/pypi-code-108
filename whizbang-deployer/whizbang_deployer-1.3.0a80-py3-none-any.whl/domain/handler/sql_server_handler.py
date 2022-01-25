from abc import abstractmethod

from whizbang.config.app_config import AppConfig
from whizbang.data.pyodbc.pyodbc_context_args import SqlServerContextArgs
from whizbang.domain.handler.handler_base import IHandler, HandlerBase
from whizbang.domain.manager.az.az_sql_database_manager import IAzSqlDatabaseManager
from whizbang.domain.manager.az.az_sql_server_firewall_manager import IAzSqlServerFirewallManager
from whizbang.domain.manager.pyodbc.sql_script_manager import ISqlScriptManager
from whizbang.domain.models.firewall_rule import FirewallRule
from whizbang.domain.models.sql.sql_database_resource import SqlServerDatabaseResource
from whizbang.domain.models.sql.sql_server_resource import SqlServerResource
from whizbang.domain.models.sql_script_execution import SqlExecution, DatabaseExecution
from whizbang.domain.shared_types.sql_connection_client_type import SqlConnectionClientType
from whizbang.util.json_helpers import import_local_json
from whizbang.util.path_defaults import get_solution_directory
from whizbang.util.sql_helpers import replace_sql

import logging

_log = logging.getLogger(__name__) 


class ISqlServerHandler(IHandler):
    """"""

    @abstractmethod
    def execute_sql_scripts(self, solution_name, server, username, password, replacements: dict):
        """"""

    @abstractmethod
    def save_firewall_rules(self, sql_server_resource: SqlServerResource, firewall_list: 'list[FirewallRule]'):
        """"""

    @abstractmethod
    def remove_firewall_rules(self, sql_server_resource: SqlServerResource, firewall_name_list: 'list[str]'):
        """"""
    @abstractmethod
    def get_connection_string(
            self, server: str, database_name: str, username: str, password: str,
            auth_type: str, client_type: str) -> str:
        """"""


class SqlServerHandler(HandlerBase, ISqlServerHandler):
    def __init__(
            self,
            app_config: AppConfig,
            sql_script_manager: ISqlScriptManager,
            sql_server_firewall_manager: IAzSqlServerFirewallManager,
            sql_database_manager: IAzSqlDatabaseManager
    ):
        HandlerBase.__init__(self, app_config=app_config)
        self.__sql_database_manager = sql_database_manager
        self.__sql_script_manager = sql_script_manager
        self.__firewall_manager = sql_server_firewall_manager

    def get_connection_string(
            self, server: str, database_name: str, username: str, password: str,
            auth_type: str = 'SqlPassword', client_type: str = SqlConnectionClientType.ado_net
    ) -> str:
        db = SqlServerDatabaseResource(server=server, resource_name=database_name, location=None, resource_group_name=None)
        return self.__sql_database_manager.get_connection_string(
            database=db, client_type=client_type, username=username,
            password=password, auth_type=auth_type
        )

    def save_firewall_rules(self, sql_server_resource: SqlServerResource, firewall_list: 'list[FirewallRule]'):
        for firewall in firewall_list:
            self.__firewall_manager.save(sql_server=sql_server_resource, firewall_rule=firewall)

    def remove_firewall_rules(self, sql_server_resource: SqlServerResource, firewall_list: 'list[str]'):
        for firewall in firewall_list:
            self.__firewall_manager.remove(sql_server=sql_server_resource, firewall_rule_name=firewall)

    def execute_sql_scripts(self, solution_name, server, username, password, replacements: dict):

        # read and create an execution object
        solution_directory = get_solution_directory(self._app_config, solution_name)
        sql_directory = f'{solution_directory}/sql'
        # sql_execution_path = find_file('sql_execution.json', sql_directory)
        sql_execution_path = f'{sql_directory}/sql_execution.json'

        jlist = import_local_json(sql_execution_path)
        database_execution_list: 'list[DatabaseExecution]' = list(map(lambda x: DatabaseExecution(**x), jlist))
        sql_execution = SqlExecution(database_execution_objects=database_execution_list)

        # iterate over execution object for each database
        for execution in sql_execution.database_execution_objects:

            # create a database context arg
            database_args = SqlServerContextArgs(
                server=server,
                database=execution.database,
                username=username,
                password=password
            )

            # iterate over each script for each database
            for script in execution.scripts:
                # import script
                _log.info(f'Now executing {script}')
                if script.endswith('.sql') is False:
                    script += '.sql'

                # todo: make into single helper method
                script_path = f'{sql_directory}/{script}'
                script_file = open(script_path)
                script = script_file.read()
                script_file.close()

                # perform find/replace
                replaced_script = replace_sql(
                    sql_statement=script,
                    replacements=replacements
                )

                # call manager . execute
                self.__sql_script_manager.execute_script(database_args, replaced_script)
