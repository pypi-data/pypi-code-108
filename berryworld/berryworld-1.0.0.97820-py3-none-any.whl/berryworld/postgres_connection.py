import re
import pandas as pd
import psycopg2


class Postgresql:

    def __init__(self, server_creds, elastic_pool=False):
        """ Initialize the class
        -----------------------------
        server_creds = {
                        "server_name": "",
                        "db_name": "",
                        "user_name": "",
                        "password": ""
                        }

        con_ = SQLConnection(server_creds)
        -----------------------------
        :param server_creds: Dictionary containing the info to connect to the Postgres Server
        """

        if elastic_pool:
            sslmode = None
        else:
            sslmode = 'require'

        self.sslmode = sslmode
        self.conn_str = None
        self.conn = None
        self.cur = None
        self.server = server_creds['server_name']
        self.db = server_creds['db_name']
        self.user = server_creds['user_name']
        self.pw = server_creds['password']

    def connect(self):
        """ Open the connection to Postgresql """
        """
        If sslmode is required connect direct to the server with ssl certificate, else connect to Postgres Elasticpool
        without specifying sslmode as the certificate is defined within the kubernetes env with server_tls_sslmode 
        """
        if self.sslmode:
            self.conn_str = "dbname='%s' user='%s' host='%s' password='%s' port='5432' sslmode='%s' " % (
                self.db, self.user, self.server, self.pw, self.sslmode)

        else:
            self.conn_str = "dbname='%s' user='%s' host='%s' password='%s' port='5432' " % (
                self.db, self.user, self.server, self.pw)

        self.conn = psycopg2.connect(self.conn_str)
        self.cur = self.conn.cursor()

    def close(self):
        """ Close the connection to Postgresql """
        self.cur.close()
        self.conn.close()

    @staticmethod
    def _chunker(seq, size):
        """ Split the data set in chunks to be sent to SQL
        :param seq: Sequence of records to be split
        :param size: Size of any of the chunks to split the data
        :return: The DataFrame divided in chunks
        """
        return (seq[pos:pos + size] for pos in range(0, len(seq), size))

    @staticmethod
    def convert_decimal_str(string):
        """ Method to parse the Decimal type in python
        :param string: String variable to parse
        """
        string = re.sub("'\)(?!(,[ ]+\())(?=([^$]))", "", string)
        return re.sub("Decimal\('", "", string)

    def query(self, sql_query):
        """ Read data from Postgres SQL according to the sql_query
        -----------------------------
        query_str = "SELECT * FROM %s" & table
        con_.query(query_str)
        -----------------------------
        :param sql_query: Query to be sent to SQL
        :return: DataFrame gathering the requested data
        """

        try:
            self.connect()
            self.cur.execute(sql_query)
            rows = self.cur.fetchall()
            col_names = [desc[0] for desc in self.cur.description]
            result = pd.DataFrame(rows, columns=col_names)
            return result
        except Exception as e:
            raise Exception(e)
        finally:
            self.close()

    def run_statement(self, statement):
        """ Execute SQL statement
        -----------------------------
        query_str = "DELETE FROM %s WHERE Id > 100" & table
        con_.run_statement(query_str)
        -----------------------------
        :param statement: Statement as string to be run in Postgres SQL
        :return: Print the number of rows affected
        """
        try:
            self.connect()
            self.cur.execute(statement)
            self.conn.commit()
            count = self.cur.rowcount
            print(count, "Rows affected")
        except Exception as e:
            raise Exception(e)
        finally:
            self.close()

    def insert(self, data, schema, table, truncate=False, output=None, print_sql=False, chunk=1000):
        """ Insert data in a table in SQL truncating the table if needed
        -----------------------------
        df = pd.DataFrame({'col1': ['a', 'b'], 'col2': [1, 2]})
        con_.insert(df, table_schema, table_name)
        -----------------------------
        :param data: DataFrame containing the data to upload
        :param schema: Schema of the table in which the data will be uploaded
        :param table: Table in which the data will be uploaded
        :param truncate: Indicate whether the table has to be truncated before the data is sent or not
        :param output: Outputs the columns indicated in this list
        :param chunk: Indicate how many rows will be uploaded at once
        :param print_sql: boolean to indicate that you want the sql_statement to be printed on the console
        :return: A DataFrame with the output columns requested if output is not None, else None
        """
        if output is None:
            output = []
        if data is None:
            # no data to upload
            return ValueError("The data provided is invalid!")

        try:
            self.connect()

            # Truncate table if needed
            if truncate:
                self.cur.execute("TRUNCATE TABLE %s.%s" % (schema, table))

            # Convert category columns to string
            cat_cols = data.columns[(data.dtypes == 'category').values].to_list()
            data[cat_cols] = data[cat_cols].astype(str)
            # Deal with bull values and apostrophes (')
            data = data.replace("'NULL'", "NULL")
            data = data.replace("'", "~~", regex=True)
            data = data.fillna("null")
            # Insert data into the table destination
            records = [tuple(x) for x in data.values]
            insert_ = """INSERT INTO %s.%s """ % (schema, table)
            insert_ += str(tuple(data.columns.values)).replace("\'", "") + """ VALUES """
            results = pd.DataFrame()
            for batch in self._chunker(records, chunk):
                rows = str(batch).strip('[]').replace("~~", "''")
                rows = rows.replace("'NULL'", "NULL").replace("'null'", 'null')
                insert_rows = insert_ + rows
                insert_rows = self.convert_decimal_str(insert_rows)
                insert_rows = re.sub(r"\';", "'')", insert_rows)
                if len(output) > 0:
                    insert_rows += " RETURNING " + ','.join(output)

                if print_sql:
                    print(insert_rows)
                self.cur.execute(insert_rows)
                if len(output) > 0:
                    results = results.append(pd.DataFrame.from_records(self.cur.fetchall(), columns=output))
                self.conn.commit()

            if len(output) > 0:
                return results
        except Exception as e:
            raise Exception(e)
        finally:
            self.close()
