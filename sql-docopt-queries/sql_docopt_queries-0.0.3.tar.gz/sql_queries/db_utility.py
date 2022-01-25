import sqlite3
import pathlib
import pandas as pd
import copy
import os
import datetime
import tabulate

DATE_FORMAT = '%Y-%m-%d'
CONSOLE_OUT = True

fipy_fp = pathlib.Path(__file__).absolute().parent
os.makedirs(fipy_fp.joinpath('db'), exist_ok=True)

# TODO store all input validation informaiton in db, such as available options for various inputs
# TODO similarly store all process flows in db, such as which items must proceed another for feature to function


class DB:
    """    Object for interacting with the finance database object
    args:


    Attributes:
    filename:   name of the database file including filepath - hardcoded
    filepath:   file location of the db file, based on parent file of src
    conn:       database connection object
    cursor:     database cursor object
    schema:     dictionary of lists, keys are tables, values are columns

    """

    def __init__(self, filename='ct_data.db', structure=None):
        """ create database object and populate schema data"""
        # connect to db when initialized and establish cursor for later use

        self.filename = filename
        self.filepath = fipy_fp.joinpath("db")
        # check if file exists, if not create structure
        # note that calling connect will create the file, therefore connection is instead made inside logic
        if not os.path.isfile(self.filepath):
            self.conn = sqlite3.connect(self.filepath.joinpath(self.filename))
            self.create_structure(structure)

        self.conn = sqlite3.connect(self.filepath.joinpath(self.filename))

        # must enforce foreign keys when connection is formed
        self.conn.cursor().execute('PRAGMA foreign_keys = 1')

        # access and store schema
        self.schema = dict()
        self.schema = self._get_accounts()

    def create_structure(self, structure):
        """ create db file from passed structure """
        for table in structure:
            self.conn.cursor().execute(table)

    def _refresh_conn(self):
        self.conn.close()
        self.conn = sqlite3.connect(self.filepath.joinpath(self.filename))
        self.conn.cursor().execute('PRAGMA foreign_keys = 1')

    def _get_accounts(self):
        tables = self.conn.cursor().execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        self.conn.cursor().close()
        schema = dict()
        # remove sqlite sequence table
        for tup in tables:
            if "sqlite_sequence" in tup:
                tables.remove(tup)
        # access and populate columns for each table name from db
        for table in tables:
            columns = list(map(lambda x: x[0], self.conn.cursor().execute("SELECT * FROM " + table[0]).description))
            schema[table[0]] = columns

        self.conn.cursor().close()
        return schema

    def get_view(self, query, data=None):
        """ get tabulated text view of data per passed query """

        # accommodate passing only string queries and table in the future?
        header = self.get_header(query=query)

        if not data:
            data = pd.read_sql(query.build_select(), self.conn)

        tabulated = tabulate.tabulate(data, headers=header)
        return tabulated

    def get_header(self, query):
        """ gets proper header for data if tabulated given columns as string

        args:
            db:             db object from finance_db
            table:          string table name to query
            columns:        select columns as list of strings toi be filtered in query
        """

        header = []
        columns = query.s_cols
        if not columns or '*' in columns:
            header = self.schema[query.table]
        else:
            for column in columns:
                if column in self.schema[query.table]:
                    header.append(column)

        return header


    def _queryize_columns(self, columns_list):
        """create string compatible with injection in sql query from list of strings"""
        col_str = ""
        if columns_list:
            if len(columns_list) != 0:
                for column in columns_list:
                    if col_str == "":
                        col_str = col_str + column
                    else:
                        col_str = col_str + "," + column
        else:
            col_str = "*"

        return col_str

    def drop_duplicates(self, table, method, condition=None, new_data=None, id_col=None, filter_columns=None):
        """ Drop sql table entries based on first or last duplicate entered

        Args:
            <table>             string table name to delete duplicates
            <condition>         MIN or MAX, decides if maximum or minimum id in selected entries is not deleted
            <id_col>            which columns to use as unique id, default to first column in table schema
                                to this columns
            <filter_columns>    columns to determine if entry is unique or duplicate, if None all columns but first are
                                used as first is typically id column
        """
        if method in ['inside', 'outside']:
            # if no id_col passed, default is first column in table schema
            if not id_col:
                id_col = self.schema[table][0]

            # if not filter columns are passed than all are used except for the first [0] which is id, as all id are
            # unique and would delete nothing
            # copy.deepcopy(db.schema[query.table])
            if not filter_columns:
                new_columns = copy.deepcopy(self.schema[table])
                new_columns.pop(0)
                # columns_str = self._queryize_columns(new_columns)
                columns_str = self._queryize_columns(new_columns)
                filter_columns = copy.deepcopy(self.schema[table]).pop(0)
            else:
                columns_str = self._queryize_columns(filter_columns)

            if method == 'inside':
                if condition:
                    query = "DELETE FROM " + table + " WHERE " + id_col + " NOT IN (SELECT " + condition + \
                            "(" + id_col + ") FROM " + table + " GROUP BY " + columns_str + ")"
                    print(query)
                    self.conn.execute(query)
                    self.conn.commit()
                else:
                    print('Must provide condition when using inside method')

            elif method == 'outside':
                if not new_data.empty:
                    # select all existing table data using passed columns or default all
                    query = pd.read_sql_query("SELECT " + columns_str + " FROM " + table, self.conn)
                    existing_data = pd.DataFrame(query, columns=filter_columns)

                    # transactions table must be formatted as date to compare to new transactions data
                    if 'date' in existing_data.columns.tolist():
                        # convert to datetime
                        existing_data['date'] = pd.to_datetime(existing_data['date'])
                    if 'date' in new_data.columns.tolist():
                        new_data['date'] = pd.to_datetime(new_data['date'])

                    # merge data into single df
                    new_data = new_data.merge(existing_data, indicator=True, how='outer')
                    # merged dataframes will have _merge column indicating with dataframe contains each row
                    # drop rows where _merge column is 'both' eliminating overlap in files
                    new_data.drop(index=new_data[new_data['_merge'] == 'both'].index, inplace=True)
                    new_data.drop(index=new_data[new_data['_merge'] == 'right_only'].index, inplace=True)
                    # _merge column no longer needed
                    new_data.drop(columns=['_merge'], inplace=True)

                    # dump cleaned transactions to sql
                    new_data.to_sql(name=table, index=False, con=self.conn, if_exists='append')
                else:
                    print('Must provide new data to compare')

        else:
            print("Method must be either 'inside' or 'outside")

    # def update_tables(self,):
    #     """ create default tables used in finance app using default schema set internally
    #     Args:
    #     name:   name of table to create(transactions, accounts, categories)
    #
    #     """
    #
    #     for table_command in FINANCE_TABLES:
    #         # print(table_command)
    #         self.conn.cursor().execute(table_command)
    #     for table_command in DISPLAY_TABLES:
    #         # print(table_command)
    #         self.conn.cursor().execute(table_command)
    #
    #     return

    def exists(self, table):
        """ Check if table exists"""
        if table in self.schema.keys():
            return True
        else:
            return False


class Query:
    """ Store query parameters and create queries

        args:
            table:          str of table to perform query operations within
            s_cols:         list of column names as str to be queried
            in_vals:        list of values to be inserted
            up_vals:        list of values to be updated
            w_cols:         list of columns as string to construct query where clauses
            w_conds:        list of operators as strings to use in constructing query where clauses
            w_vals:         list of values to construct where clauses e.g. 'WHERE w_col[1] w_cond[1] w_val[1]'
            o_col:          string column name to be used in order clause
            o_cond:         string denoting order condition, can be 'ASC' or 'DESC', e.g. 'ORDER BY o_col o_cond'
            limit:          string number denoting limit clause, e.g. 'LIMIT limit'
            build_str:      bool indicating if all str properties should be built @ init or later if false
                            allows for addition/modification of query properties post init

        props:
            where_str:      query ready string containing where clauses
            select_str:     query ready string containing select columns
            order_str:      query ready string containing order clause
            limit_str:      query ready string containing limit clause
            values_str:     query ready string containing values for insert
            update_str:     query ready string containing cols/vals for updating
            table:          string table name in which queries operate
            wheres:         list of dictionaries structured [{'col': w_col, 'cond': w_cond, 'va': w_val}]
            o_col:          string column name to order query by
            o_cond:         string condition to order query by, 'ASC' or 'DESC'
            in_vals:        list of values to be inserted - must correspond in order to s_cols
            in_cols:        corresponding list of columns as strings to in_vals
            up_vals:        list of values to be updated - must correspond in order to s_cols
            up_cols:        corresponding list of columns as strings to up_vals
            limit:          string value indicating limit or return query items

        """

    def __init__(self, db, table, s_cols=None,
                 in_vals=None, in_cols=None,
                 up_vals=None, up_cols=None,
                 w_cols=None, w_conds=None, w_vals=None, w_joins=None,
                 o_col=None, o_cond=None,
                 limit=None,
                 build_str=True):

        # self.db = FinanceDB()
        # initialize properties
        self.table = table
        self.db = db
        self.select_str = ""
        self.in_values_str = ""
        self.in_cols_str = ""
        self.update_str = ""
        self.where_str = ""
        self.order_str = ""
        self.limit_str = ""
        self.wheres = []

        self.w_joins = w_joins
        self.o_col = o_col
        self.o_cond = o_cond
        self.in_vals = in_vals
        self.in_cols = in_cols
        self.up_vals = up_vals
        self.up_cols = up_cols
        self.limit = limit

        # if no s_cols passed then use * (all in sql)
        if s_cols:
            self.s_cols = s_cols
        else:
            # default to all columns instead of *
            self.s_cols = '* '

        if in_vals:
            self.in_vals = self.replace_null(self.in_vals)
            if not in_cols:
                # default to all columns for insert if none passed and in_vals passed
                self.in_cols = db.schema[self.table]

        if up_vals and not up_cols:
            # default to all columns for update if none passed with up_vals
            self.up_cols = db.schema[self.table]

        if w_cols:
            for i in range(0, len(w_cols)):
                where = {}
                # sql will only recognize dates enclosed in apostrophes

                # process all else normally
                where['col'] = w_cols[i]
                where['cond'] = w_conds[i]
                # convert datetime objects ot srtings
                if isinstance(w_vals[i], datetime.datetime):
                    w_vals[i] = w_vals[i].strftime(DATE_FORMAT)
                if 'date' in w_cols[i]:
                    w_vals[i] = "'" + w_vals[i] + "'"
                where['val'] = w_vals[i]
                self.wheres.append(where)

        # as long as build str is not false, all query strings will be built
        if build_str:
            self.build_str()

    def build_str(self):
        """ build all query strings given Query properties """

        # if * in s_cols, select_str is simply * as well
        if '*' not in self.s_cols:
            self.select_str = self._queryize_columns(select=True)
        else:
            self.select_str = '*'

        if self.in_vals:
            self.in_vals = self.replace_null(self.in_vals)
            if not self.in_cols:
                # default to all columns for insert if none passed and in_vals passed
                self.in_cols = self.db.schema[self.table]
            self.in_values_str = self._queryize_values()
            self.in_cols_str = self._queryize_columns(insert=True)

        if self.up_vals:
            self.update_str = self._queryize_updates(columns=self.up_cols, values=self.up_vals)

        if self.wheres:
            self.where_str = self._queryize_where()

        if self.o_col:
            self.order_str = "ORDER BY " + self.o_col + ' ' + self.o_cond + ' '

        if self.limit:
            self.limit_str = "LIMIT " + self.limit + ' '

        return

    def replace_null(self, p_list):
        """ replace NoneType objects with NULL"""
        p_list = ['NULL' if v is None else v for v in p_list]
        return p_list

    def _queryize_columns(self, select=None, insert=None):
        """create string compatible with injection in sql query from list of strings"""
        col_str = ""
        param = None
        if select:
            param = self.s_cols
        elif insert:
            param = self.in_cols

        if len(param) > 1:
            for col in param:
                if col_str == "":
                    col_str = col_str + col
                else:
                    col_str = col_str + "," + col
        else:
            col_str = param[0]

        return col_str

    def _queryize_values(self,):
        """create string compatible with injection in sql query from list of strings"""
        val_str = ""
        param = self.in_vals

        if len(param) > 1:
            for val in param:
                # replace val with param if injection option not chosen
                if not isinstance(val, str):
                    val = str(val)
                    val_str = val_str + val
                    # remove apostrophe as sql thinks its a string
                    val_str = val_str[0:(-1*(len(val))):] + val_str[(-1*(len(val)))::]
                    val_str += ","

                elif val == 'NULL':
                    val_str = val_str + val + ","
                else:
                    val_str = val_str + "'" + val + "',"
            val_str = val_str[:-1]
        else:
            val_str = param[0]

        return val_str

    def _queryize_where(self):
        """ create queryable string from where properties: WHERE col cond val (AND...) """

        where_str = "WHERE "

        # need to wrap all vals in aprotrophe or might nto work if not already for fucks sake
        # for val in self.wheres:
        #     if val['val'][0] != "'" and val['val'][-1] != "'":
        #         val['val'] = "'" + val['val'] + "'"

        if len(self.wheres) > 1:
            # w_joins counter
            j = 0
            for i in range(0, len(self.wheres)):
                # if not last where condition then add w_join to prep for next statement
                # w_join is added prior to the where clause, do not add ot first clause
                if i != 0:
                    where_str = where_str + " " + self.w_joins[j] + " "
                    j = j + 1
                else:
                    where_str = where_str + " "

                # like conditions must be wrapped in ''
                if self.wheres[i]['cond'] == 'LIKE':
                    self.wheres[i]['val'] = "'" + self.wheres[i]['val'] + "'"

                where_str = where_str + self.wheres[i]['col'] + ' ' + self.wheres[i]['cond'] + ' ' \
                            + self.wheres[i]['val']

        else:
            if self.wheres[0]['cond'] == 'LIKE':
                self.wheres[0]['val'] = "'" + self.wheres[0]['val'] + "'"
            where_str = where_str + self.wheres[0]['col'] + ' ' + self.wheres[0]['cond'] + ' ' + self.wheres[0]['val']

        return where_str

    def _queryize_updates(self, columns, values):
        """create string compatible with injection in sql query from list of strings"""
        updates_str = ""
        # if string is used as a value it must be wrapped in '
        if isinstance(values, list):

            for i in range(0, len(columns)):
                if updates_str == "":
                    updates_str = columns[i] + " = '" + str(values[i]) + "'"
                else:
                    updates_str = updates_str + ", " + columns[i] + " = '" + str(values[i]) + "'"
        else:
            if isinstance(values, str):
                if values[0] != "'" and values[len(values)] != "'":
                    values = "'" + values + "'"
            updates_str = columns[0] + " = " + values

        return updates_str

    def _query_dict(self, db, query, table):
        """ return list of dictionaries, table column names as keys and entries as items """

        entries = []
        data = db.conn.cursor().execute(query).fetchall()
        keys = db.schema[table]

        for entry in data:
            query_dict = {}
            for i in range(0, len(entry)):
                query_dict[keys[i]] = entry[i]
            entries.append(query_dict)

        return entries

    def links_entries(self, item_id, item_col, link_table):
        """ return linked items in link table given one ID and link table as list of ID's """

        links_raw = self.db.conn.cursor().execute(
            "SELECT * FROM " + link_table + "WHERE " + item_col + " = " + item_id).fetchall()

        links = []
        for link in links_raw:
            links.append(link[0])

        return links

    def build_select(self, build_op='string', console_view=CONSOLE_OUT, function=None):
        # SELECT s_cols FROM table WHERE ORDER LIMIT
        # SELECT function(s_cols) FROM table WHERE ORDER LIMIT

        # data validation for functions and select query argument requirements
        available_functions = ['AVG', 'SUM', 'MAX']
        if function:
            if function not in available_functions:
                print('Function not included, available functions must be one of ' + str(available_functions)[1:-1])
                return
            if len(self.s_cols) != 1 or '*' in self.s_cols:
                print("Function can only be used with single column")
                return

        # always space after latest addition to query - standardize
        query = 'SELECT '

        # build query
        if function:
            query = query + function + '(' + self.select_str + ') '
        elif self.s_cols:
            query = query + self.select_str

        query = query + ' FROM ' + self.table + ' '

        if self.wheres:
            query = query + self.where_str

        if self.o_col:
            query = query + self.order_str

        if self.limit:
            query = query + self.limit_str

        if console_view:
            print(query)

        if build_op == 'string':
            return query
        elif build_op == 'dict':
            data = self._query_dict(db=self.db, query=query, table=self.table)
            return data

    def build_insert(self, method='FAIL', console_view=CONSOLE_OUT):
        # INSERT OR method INTO table (columns,) VALUES (values,)
        query = 'INSERT OR ' + method + ' INTO ' + self.table + \
                ' (' + self.in_cols_str + ') ' + 'VALUES ' + '(' + self.in_values_str + ')'

        if console_view:
            print(query)
        return query

    def build_update(self, method='FAIL', console_view=CONSOLE_OUT):
        # INSERT OR method INTO table (columns,) VALUES (values,)
        query = 'UPDATE OR ' + method + ' ' + self.table + ' SET ' + self.update_str + ' '

        if self.wheres:
            query = query + self.where_str

        if console_view:
            print(query)
        return query

    def build_delete(self, console_view=CONSOLE_OUT):
        # TODO DROP TABLE
        # DELETE s_cols FROM table WHERE ORDER LIMIT

        # build query
        query = 'DELETE FROM ' + self.table + ' '

        if self.wheres:
            query = query + self.where_str

        if console_view:
            print(query)
        return query

    def add_entry(self, console_view=CONSOLE_OUT, drop_cond=None, drop_method=None, comp_columns=None, drop_id_col=None):
        self.db.conn.cursor().execute(self.build_insert())

        if drop_cond and drop_method:
            # delete duplicates and keep minimum id value (original entry)
            self.db.drop_duplicates(table=self.table, condition=drop_cond, method=drop_method,
                                    filter_columns=comp_columns,
                                    id_col=drop_id_col)
            self.db.conn.commit()

        if console_view:
            view = self.db.get_view(query=self)
            print(view)

        return

    def update_entry(self, query, console_view=CONSOLE_OUT):
        """ edit selection in query using provided up_vals and diplay change to user"""

        # copy query object but erase select columns to get all data for display
        query_all = copy.deepcopy(query)
        query_all.select_str = '*'

        # get pre-update data
        original_data = self.db.conn.cursor().execute(query_all.build_select()).fetchall()

        # update the data
        self.db.conn.cursor().execute(query.build_update())
        self.db.conn.commit()

        # get updated data
        updated_data = self.db.conn.cursor().execute(query_all.build_select()).fetchall()

        if console_view:
            # display change to user
            print('Pre-Update:')
            # print(tabulate.tabulate(original_data, headers=header))
            # show_tabulated_sql(db, query_all, data=original_data)
            view = self.db.get_view(query=self, data=original_data)
            print(view.tabulated)
            print("Post Update:")
            # print(tabulate.tabulate(updated_data, headers=header))
            # show_tabulated_sql(db, query, data=updated_data)
            view = self.db.get_view(query=self, data=updated_data)
            print(view.tabulated)