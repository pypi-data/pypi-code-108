"""
This script creates the tables in the database that the Admins are responsible for.
"""
import os
import re

from pymedquery.config import config
from pymedquery.pg_crud_handler import CRUD
from pymedquery.config.logger_object import Logger


def topological_sort(dictionary):
    """Sort a dictionary topologically with O(n^2) (super fast up to 2^20 object)

    Parameters
    ----------
    dictionary : dict[string, [string]]
        A dictionary containing names and their dependencies

    Returns
        A topologically sorted list
    -------


    """
    order = []

    for _ in range(len(dictionary)):
        for table_name, table_dependencies in dictionary.items():
            if len(table_dependencies) == 0:
                order.append(table_name)
                del dictionary[table_name]
                for key2, value2 in dictionary.items():
                    if table_name in value2:
                        dictionary[key2].remove(table_name)

                break

    assert (
        len(dictionary) == 0
    ), f"Some dependencies are dependent on each other. Some of the following could not be processed: {dictionary}"

    return order


def create_tables(log):
    """Create all sql tables and run the sql-scripts in crud

    Parameters
    ----------
    log : skeng.config.logger_object.Logger
        A logger object for logging
    """

    crud = CRUD(
        user=os.environ.get('MQUSER'),
        password=os.environ.get('MQPWD'),
        database=os.environ.get('DATABASE'),
    )

    for root, _, files in os.walk(config.SQL_PATH):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            with open(file_path) as f:
                if os.path.splitext(file_name)[-1] != ".sql":
                    log.error(f"The file {file_path} is not a .sql file..")
                    continue

                sql_command = f.read()
                try:
                    name = re.search(
                        r"CREATE TABLE IF NOT EXISTS ([^ ]*)", sql_command
                    ).group(1)
                except Exception as e:
                    log.error(
                        f"Could not find table name for file {file_path} with error: {e}"
                    )
                    continue

                config.create_sql_command_dict[name] = file_path

                if name not in config.create_dependencies:
                    config.create_dependencies[name] = []

                foreign_keys = re.findall(
                    r"REFERENCES ([^ ]*)", sql_command
                )

                for foreign_key in foreign_keys:
                    config.create_dependencies[name].append(foreign_key)

    order = topological_sort(config.create_dependencies)

    for table_name in order:
        crud.create(config.create_sql_command_dict[table_name])
        crud.commit()

    log.success(f"\n{len(config.create_sql_command_dict)} tables created successfully in {config.DATABASE_TMP}")


if __name__ == "__main__":
    logger_object = Logger(__name__)
    create_tables(logger_object)
