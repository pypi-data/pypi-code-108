#!/usr/bin/python3

#     Copyright 2021. FastyBird s.r.o.
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.

# Test dependencies
import json
import os
import unittest
from typing import Dict, Optional

# Library dependencies
import MySQLdb
from fastybird_exchange.bootstrap import register_services as register_services_exchange
from fastybird_metadata.loader import load_schema_by_routing_key
from fastybird_metadata.routing import RoutingKey
from fastybird_metadata.validator import validate
from MySQLdb import OperationalError
from MySQLdb.cursors import Cursor
from kink import di
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import Session

# Library libs
from fastybird_triggers_module.bootstrap import register_services
from fastybird_triggers_module.entities.base import Base


class DbTestCase(unittest.TestCase):
    __db_name: str

    __db_engine: Engine
    __db_session: Session

    __raw_database: MySQLdb.Connection
    __cursor: Cursor

    # -----------------------------------------------------------------------------

    @staticmethod
    def validate_exchange_data(routing_key: RoutingKey, data: Dict) -> Dict:
        """Validate received exchange message against defined schema"""
        schema: str = load_schema_by_routing_key(routing_key)

        return validate(json.dumps(data), schema)

    # -----------------------------------------------------------------------------

    @classmethod
    def setUpClass(cls) -> None:
        cls.__db_name = "fb_test_{}".format(os.getpid())

        cls.__setup_database()

        # Inject database into DI
        di[Session] = cls.__db_session

        register_services_exchange()
        register_services()

        # Initialize all database models
        Base.metadata.create_all(cls.__db_engine)

        cls.__initialize_database_data()

    # -----------------------------------------------------------------------------

    @classmethod
    def tearDownClass(cls) -> None:
        cls.__tear_down_database()

    # -----------------------------------------------------------------------------

    @classmethod
    def __setup_database(cls) -> None:
        cls.__raw_database = MySQLdb.connect(host="127.0.0.1", user="root", passwd="root")

        cls.__cursor = cls.__raw_database.cursor()

        cls.__cursor.execute("DROP DATABASE IF EXISTS {}".format(cls.__db_name))
        cls.__cursor.execute("CREATE DATABASE {}".format(cls.__db_name))
        cls.__cursor.execute("USE {}".format(cls.__db_name))

        cls.__db_engine = create_engine(f"mysql+pymysql://root:root@127.0.0.1/{cls.__db_name}", echo=False)
        cls.__db_session = Session(cls.__db_engine)

    # -----------------------------------------------------------------------------

    @classmethod
    def __tear_down_database(cls) -> None:
        cls.__db_session.close()

        cls.__cursor.execute("DROP DATABASE IF EXISTS {}".format(cls.__db_name))

        cls.__cursor.close()
        cls.__raw_database.close()

    # -----------------------------------------------------------------------------

    @classmethod
    def __initialize_database_data(cls) -> None:
        query: str = """
        SET FOREIGN_KEY_CHECKS=0;
        SELECT @str := CONCAT('TRUNCATE TABLE ', table_schema, '.', table_name, ';')
            FROM information_schema.tables
            WHERE table_type = 'BASE TABLE' AND table_schema in ('{}');
        PREPARE stmt FROM @str;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
        SET FOREIGN_KEY_CHECKS=1;
        """.format(
            cls.__db_name
        )

        cls.__cursor.execute(query)

        # cls.__raw_database.commit()

        import_file = open(os.path.join(os.path.dirname(__file__), "../sql/dummy.data.sql"), "r")
        sql_file = import_file.read()
        import_file.close()

        sql_commands = sql_file.split(";")

        # Execute every command from the input file
        for command in sql_commands:
            if command == "\n":
                continue

            # This will skip and report errors
            # For example, if the tables do not yet exist, this will skip over
            # the DROP TABLE commands
            try:
                cls.__cursor.execute(command)

            except OperationalError as msg:
                print("Command skipped: {}".format(msg))

        cls.__raw_database.commit()
