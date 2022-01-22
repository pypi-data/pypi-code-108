import sqlite3


class Database:
    def __init__(self, name:str=":memory:"):
        """
        Database object for a sqlite database
        :param name: The filename (path included) of the database file
        """
        self.db = sqlite3.connect(name)  # Database connection
        self.cs = self.db.cursor()  # Database cursor

        # ez access
        self.do = self.cs.execute
        self.domany = self.cs.executemany

    @staticmethod
    def _save(func):
        """
        A decorator to save / commit the changes after performing actions
        :return: The things the original function returns
        """
        def decorator(self, *args):
            result = func(self, *args)
            self.db.commit()
            return result
        return decorator

    @_save
    def create_table(self, name:str, columns:dict):
        """
        Create a table in the database
        :param name: name of the table
        :param columns: keys: names of columns; values: properties of the columns (NON NULL, AUTO_INCREMENT, TEXT, INT, etc.)
        :return: the table object (same as calling get_table(name))
        """
        l = []
        for key in columns:
            l.append(f"{key} {columns[key]}")
        self.do(f"CREATE TABLE {name} ({', '.join(l)})")
        return self.get_table(name)

    @_save
    def append_data(self, table:str, *values):
        """
        Insert a row of data to the table
        :param table: name of the table
        :param values: values you want to add. values should be given in ascending order. NO NEED for putting the values into a list / tuple first
        :return: None
        """
        self.do(f"INSERT INTO {table} VALUES {values}")

    @_save
    def append_many_data(self, table:str, *values:list):
        """
        Insert multiple columns of data to the table
        :param table: name of the table
        :param values: values you want to add. each row of values should be in a separate list
        :return: None
        """
        self.domany(f"INSERT INTO {table} VALUES ({', '.join(['?'] * len(values[0]))})", values)

    @_save
    def update_data(self, table:str, column:str, new_value, filter:str=None):
        """
        Update a single box in the table
        :param table: name of the table
        :param column: the column you're going to update on
        :param new_value: the new value to update
        :param filter: filters to locate the column you want to update on
        :return: None
        """
        f = " WHERE {}".format(filter) if filter else ""
        self.do(f"UPDATE {table} SET {column}={new_value}" + f)

    @_save
    def delete_data(self, table:str, filter:str=None):
        """
        Delete a row of data
        :param table: name of the table
        :param filter: filters for locating the row(s)
        :return: None
        """
        f = " WHERE {}".format(filter) if filter else ""
        self.do(f"DELETE FROM {table}" + f)

    def get_data(self, table:str, number:int=1, columns:tuple=(), filter:str=None):
        """
        Find data
        :param table: name of the table
        :param number: 0: All rows are fetched; 1: Only one row is fetched, so no list outside each row of data; other numbers: fetching the number of rows accordingly
        :param columns: the columns you want to fetch
        :param filter: filters to find the row(s)
        :return: the data you wanted to fetch
        """
        if columns == ():
            c = "*"
        elif isinstance(columns, str):
            c = columns
        else:
            c = ", ".join(columns)

        f = " WHERE {}".format(filter) if filter else ""
        self.do(f"SELECT {c} FROM {table}" + f)

        if number == 1:
            return self.cs.fetchone()
        elif number <= 0:
            return self.cs.fetchall()
        return self.cs.fetchmany(number)

    def get_table(self, name):
        """
        Give you a table object to more quickly work with a table
        :param name: name of the table
        :return: the table object
        """
        return Table(self, name)


class Table:
    def __init__(self, db, name):
        self.db = db
        self.name = name

    def append_many(self, *values:list):                                 return self.db.append_many_data(self.name, *values)
    def append(self, *values):                                           return self.db.append_data(self.name, *values)
    def update(self, column:str, new_value, filter:str=None):            return self.db.update_data(self.name, column, new_value, filter)
    def delete(self, filter:str=None):                                   return self.db.delete_data(self.name, filter)
    def get(self, number:int=1, columns:tuple=(), filter:str=None):      return self.db.get_data(self.name, number, columns, filter)