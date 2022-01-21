from typing import Final, final
import logging
import string
import sys
import re
import os
import psycopg2

from .exceptions_ import (
    SlashBadColumnNameError, SlashTypeError,
    SlashBadAction, SlashPatternMismatch
)
from ..types_ import QueryQueue, BasicTypes


class Connection:
    def __init__(self, dbname, user, password, host, port, *, logger=False):
        self._dbname = dbname
        self._user = user
        self._password = password
        self._host = host
        self._port = port

        self.__connection = psycopg2.connect(
            dbname=self._dbname,
            user=self._user,
            password=self._password,
            host=self._host,
            port=self._port
        )
        self.cursor = self.__connection.cursor()

        self.__query_queue = QueryQueue(self)

        self.__logger = logger

    @property
    def queue(self):
        return self.__query_queue

    def execute(self, request, message=""):
        try:
            self.cursor.execute(request)
            self.__connection.commit()
        except Exception as e:
            if self.__logger is not False:
                if os.environ.get("redirect_error") != "True":
                    print(e)
                self.__logger.info(
                    "Unsuccessful commit: \n\t<< {} >>\n\t{}\n\n{}".format(request, message, e)
                )
        else:
            if self.__logger is not False:
                self.__logger.info("Successful commit: {}".format(message))

    def close(self):
        self.__connection.close()
        if self.__logger is not False:
            self.__logger.info("Session closed")

    def fetchall(self):
        return self.cursor.fetchall()

    def create(self, table, operation_obj=None):
        Create(table, BasicTypes.TYPES_LIST, self, operation_obj)


class Create():
    def __init__(self, table, types_list, conn: Connection, operation_obj):
        self.connection = conn
        self.table = table
        if self.__validate(types_list):
            self.__create(table, operation_obj)

    def __validate(self, types_list):
        CheckDatas.check_str(self.table.name)

        for column in self.table.columns:
            if column.type not in types_list:
                raise SlashTypeError(f"{type(column.type)} is not available type for data base")

            CheckDatas.check_str(column.name)

        return True

    def __create(self, table, operation_obj):
        if operation_obj:
            table.op = operation_obj(self.connection, table)

        request = "CREATE TABLE IF NOT EXISTS {} (rowID SERIAL PRIMARY KEY, {})".format(
            table.name,
            ", ".join([f"{col.name} {col.sql_type}" for col in table.columns])
        )
        self.connection.execute(
            CheckDatas.check_sql(request, "create"),
            "create operation"
        )


@final
class SQLConditions:
    EQ = "="
    AND = "AND"
    NE = "!="
    OR = "OR"
    NOT = "NOT"
    GT = ">"
    LT = "<"
    GE = ">="
    LE = "<="

    @staticmethod
    def where(*condition):
        output_condition = " WHERE " + " ".join(list(map(str, condition)))

        main_templates = re.findall(r"[a-zA-Z_0-9]* = [a-zA-Z_0-9]*", output_condition)
        new_condition = []
        for template in main_templates:
            item = template.split()[-1]
            try:
                int(template.split()[-1])
                item = str(item)
            except:
                item = f"'{item}'"
            template = template.split()
            template[-1] = item
            template = " ".join(template)
            
            new_condition.append(template)
        
        new_condition =  " AND ".join(new_condition)
        new_condition = " WHERE " + new_condition

        print(CheckDatas.check_str(new_condition))
        return new_condition

    @staticmethod
    def order_by(column, *, desc=""):
        return " ORDER BY {} {}".format(
            CheckDatas.check_str(column),
            CheckDatas.check_str(desc)
        )

    @staticmethod
    def group_by(): ...


class CheckDatas:
    SQL_TEMPLATES: Final = {
        "insert": r"INSERT INTO [a-zA-Z0-9_]* [)()a-zA-Z,\s_]* VALUES [a-zA-Z)(0-9,\s'@._]*",
        "create": r"CREATE TABLE IF NOT EXISTS [a-zA-Z0-9_]* [)()a-zA-Z0-9',\s_]*",
        "update": r"UPDATE [a-zA-Z0-9_]* SET [a-zA-Z0-9\s<>!=',_]*",
        "delete": r"DELETE FROM [a-zA-Z0-9_]* [a-zA-Z0-9\s<>!=_.]*",
        "select": r"SELECT [a-zA-Z0-9(),\s'<>!=*._]*"
    }
    def __init__(self): ...

    @staticmethod
    def check_str(str_: str):
        datas = string.punctuation.replace("@", "").replace(".", "").replace("_", "").replace("-", "")
        datas = datas.replace("=", "").replace(">", "").replace("<", "").replace("'", "")
        for char_ in str_:
            if char_ in datas:
                raise SlashBadColumnNameError(
                    f"Error:\n\nBad name for column of data base\nName: {str_}\nSymbol: {char_}"
                )
        return str_

    @staticmethod
    def check_sql(sql_request: str, action: str):
        sql_template = CheckDatas.SQL_TEMPLATES.get(action)

        if sql_template is not None:
            template = re.findall(sql_template, sql_request)
            if sql_request in template:
                return sql_request
            else:
                raise SlashPatternMismatch(
                    "\n\nPattern mismatch:\n\t{}\n\nFinded pattern: {}\n\t".format(
                        sql_request, template
                    )
                )
        else:
            raise SlashBadAction("Action is wrong")


class Logger(logging.Logger):
    def __init__(self, name: str, file: str, *, redirect_error: bool=False, level=logging.INFO) -> None:
        super().__init__(name, level=level)

        self.__redirect_error = redirect_error
        os.environ.setdefault("redirect_error", str(redirect_error))

        handler = logging.FileHandler(self.__path(file), encoding="utf-8")
        formatter = logging.Formatter("[%(asctime)s]:[%(process)d-%(levelname)s]:[%(name)s]:[%(message)s]")

        handler.setFormatter(formatter)
        self.addHandler(handler)

        with open(os.environ.get("logs"), "a") as file_:
            file_.write("\n")

    def __path(self, file: str):
        path_ = os.path.dirname(os.path.abspath(file)) + "\\logs"

        if not os.path.exists(path_):
            os.mkdir(path_)
        path_ += "\\data.log"

        os.environ.setdefault("logs", path_)
        if self.__redirect_error:
            sys.stderr = open(os.environ.get("logs"), "a")

        return path_
