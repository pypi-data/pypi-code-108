from .core import CheckDatas, Connection, SQLConditions
from ..types_ import DataSet, QueryQueue, Table

from .exceptions_ import SlashRulesError


class Insert():
    def __init__(self, conn: Connection, table: Table, names: tuple, values: tuple, rules="*"):
        self.__responce = self.__validate(table, names, values, rules)
        self.__table = table
        conn.execute(
            CheckDatas.check_sql(self.__responce, "insert"),
            "insert operation"
        )

    def __validate(self, table, names, values, rules):
        names = [names] if (type(names) != list) and (type(names) != tuple) else names
        values = [values] if (type(values) != list) and (type(values) != tuple) else values

        CheckDatas.check_str(table.name)

        for name in names:
            CheckDatas.check_str(name)

        for value in values:
            if value.type_name == "type_text":
                CheckDatas.check_str(value.value)

            valid_responce = value._is_valid_datas(rules)
            if not valid_responce[0]:
                raise SlashRulesError(f"\n\n\nRule: {valid_responce[1]}")

        names = ", ".join(names)

        sql_responce = f"""INSERT INTO {table.name} ({names}) VALUES ("""

        for index, val in enumerate(values):
            if val.type_name == "type_int":
                sql_responce += str(val.value)
                if (index + 1) != len(values):
                    sql_responce += ", "
            elif val.type_name == "type_text":
                sql_responce += ("'" + val.value + "'")
                if (index + 1) != len(values):
                    sql_responce += ","
            elif val.type_name == "type_bool":
                sql_responce += str(val.value)
                if (index + 1) != len(values):
                    sql_responce += ", "
            elif val.type_name == "type_date":
                sql_responce += ("'" + str(val.value) + "'")
                if (index + 1) != len(values):
                    sql_responce += ", "
            elif val.type_name == "type_hidden":
                sql_responce += ("'" + str(val.value) + "'")
                if (index + 1) != len(values):
                    sql_responce += ", "                
        sql_responce += ")"

        return sql_responce

    @property
    def responce(self):
        return self.__responce

    @property
    def table(self):
        return self.__table


class Delete():
    def __init__(self, conn: Connection, table: Table, condition: SQLConditions):
        self.__responce = self.__validate(table, condition)
        conn.execute(
            CheckDatas.check_sql(self.__responce, "delete"),
            "delete operation"
        )

    def __validate(self, table, condition):
        CheckDatas.check_str(table.name)
        sql_responce = f"DELETE FROM {table.name}{condition}"

        return sql_responce

    @property
    def responce(self):
        return self.__responce


class Select():
    def __init__(self, conn: Connection, table: Table, names: tuple, condition: SQLConditions):
        self.__conn = conn
        self.__responce = self.__validate(table, names, condition)
        self.__table__name = table.name
        self.__names = names

    def __validate(self, table, names, condition):
        names = [names] if (type(names) != list) and (type(names) != tuple) else names

        CheckDatas.check_str(table.name)

        return "SELECT {} FROM {}{}".format(
            ", ".join([n for n in names]),
            table.name, condition
        )

    def get(self):
        self.__conn.execute(
            CheckDatas.check_sql(self.__responce, "select"),
            "select operation"
        )

        return DataSet(
            self.__table__name, self.__names, self.__conn.fetchall()
        )

    @property
    def responce(self):
        return self.__responce


class Update():
    def __init__(self, conn: Connection, table: Table, names: tuple, values: tuple, condition, rules="*"):
        self.__responce = self.__validate(
            table, names, values, condition, rules
        )
        conn.execute(
            CheckDatas.check_sql(self.__responce, "update"),
            "update operation"
        )

    def __validate(self, table, names, values, condition, rules):
        names = [names] if (type(names) != list) and (type(names) != tuple) else names
        values = [values] if (type(values) != list) and (type(values) != tuple) else values

        CheckDatas.check_str(table.name)
        sql_responce = "UPDATE {} SET ".format(table.name)

        for index, value in enumerate(values):
            valid_responce = value._is_valid_datas(rules)
            if not valid_responce[0]:
                raise SlashRulesError(f"\n\n\nRule: {valid_responce[1]}")

            if value.type_name == "type_text":
                sql_responce += " = ".join((names[index], f"'{value.value}'"))
            elif value.type_name == "type_int":
                sql_responce += " = ".join((names[index], f"{value.value}"))
            elif value.type_name == "type_bool":
                sql_responce += " = ".join((names[index], f"{value.value}"))
            elif value.type_name == "type_date":
                sql_responce += " = ".join((names[index], f"'{value.value}'"))

            sql_responce += ", " if index != (len(values) - 1) else ""

        sql_responce += condition

        return sql_responce

    @property
    def responce(self):
        return self.__responce


class Operations():
    def __init__(self, connection, table_link=None):
        self.__connection = connection
        self.query_handler: QueryQueue = connection.queue
        self.__table = table_link

    def insert(self, table, names, values, *, rules="*"):
        if self.__table:
            table = self.__table

        if table.__dict__.get("_is_unated") is not None:
            table._is_unated

            data: dict = dict(zip(names, values))

            for one_table in table.tables:
                columns_list = []
                for column in one_table.columns:
                    columns_list.append(column.name)

                insert_query = Insert(
                    self.__connection, one_table, columns_list, [data[i] for i in columns_list], rules
                )
                self.query_handler.add_query(insert_query)
        else:
            if rules == "*":
                insert_query = Insert(self.__connection, table, names, values)
                self.query_handler.add_query(insert_query)
            else:
                insert_query = Insert(
                    self.__connection, table, names, values, rules
                )
                self.query_handler.add_query(insert_query)

    def select(self, table, names, condition=" "):
        if self.__table:
            table = self.__table

        if table.__dict__.get("_is_unated") is not None:
            table._is_unated

            data: list = []
            for one_table in table.tables:
                columns_list = []
                non_existence_column = None
                for column in one_table.columns:
                    columns_list.append(column.name)

                for column in table.columns:
                    if column.name not in columns_list:
                        non_existence_column = column.name

#                print(non_existence_column)
#                print(columns_list)
                select_query = Select(self.__connection, one_table, columns_list, condition if non_existence_column not in condition else " ")
                self.query_handler.add_query(select_query)
                data.append(select_query.get().get_data())

            new_data = []
            for i, data_item in enumerate(data):
                if i == len(data) - 1:
                    break
                for n, item in enumerate(data_item):
                    temp_data = item + data[i+1][n]
                    temp_data = sorted(set(temp_data), key=lambda d: temp_data.index(d))
                    new_data.append(tuple(temp_data))
            new_data = tuple(new_data)

            return DataSet(table.name, table.columns, new_data)
        else:
            select_query = Select(self.__connection, table, names, condition)
            self.query_handler.add_query(select_query)
            return select_query.get()

    def delete(self, table, condition=" "):
        if self.__table:
            table = self.__table

        if table.__dict__.get("_is_unated") is not None:
            table._is_unated

            for table_item in table.tables:
                Delete(self.__connection, table_item, condition)
        else:
            return Delete(self.__connection, table, condition)

    def update(self, table, column_names, values, condition=" "):
        if self.__table:
            table = self.__table

        if table.__dict__.get("_is_unated") is not None:
            table._is_unated


            for table_item in table.tables:
                Update(self.__connection, table_item, column_names, values, condition)
        else:
            Update(self.__connection, table, column_names, values, condition)
