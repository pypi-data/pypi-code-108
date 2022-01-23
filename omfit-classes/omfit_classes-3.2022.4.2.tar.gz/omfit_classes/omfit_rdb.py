try:
    # framework is running
    from .startup_choice import *
except ImportError as _excp:
    # class is imported by itself
    if (
        'attempted relative import with no known parent package' in str(_excp)
        or 'No module named \'omfit_classes\'' in str(_excp)
        or "No module named '__main__.startup_choice'" in str(_excp)
    ):
        from startup_choice import *
    else:
        raise

from omfit_classes.utils_fusion import is_device, tokamak

import numpy as np

try:
    import pyodbc
except Exception as excp:
    warnings.warn('No RDB support: ' + repr(excp))

__all__ = ['OMFITrdb', 'available_efits_from_rdb', 'translate_RDBserver', 'set_rdb_password', 'get_rdb_password']

_RDBserverDict = {
    # dictionary to translate mnemonic names to RDB servers stored in MainSettings['SERVER']
    'd3drdb': 'd3drdb',
    'atlas.gat.com': 'd3drdb',
    'DIIID': 'd3drdb',
    'DIII-D': 'd3drdb',
    'D3D': 'd3drdb',
    'gat': 'd3drdb',
    'd3dpub': 'huez',
    'huez.gat.com': 'huez',
    'CMOD': 'alcdb2',
    'C-Mod': 'alcdb2',
    'EAST': 'east_database',
    'east': 'east_database',
    'nstx': 'nstxrdb',
}


def printq(*args):
    """Shortcut so that the topic for the file can be set consistently and easily"""
    printd(*args, topic='omfit_rdb')


def translate_RDBserver(server, servers=_RDBserverDict):
    """This function maps mnemonic names to real RDB servers"""
    server = tokamak(server)
    if server.split(':')[0] not in list(OMFIT['MainSettings']['SERVER'].keys()):
        score_table = []
        for item in list(servers.keys()):
            m = difflib.SequenceMatcher(None, item.lower(), server.lower())
            score_table.append([m.ratio(), item, servers[item]])

        # return best match
        scores = list(map(eval, np.array(score_table)[:, 0]))
        if max(scores) > 0.80:
            server = score_table[np.array(scores).argmax()][2]
        else:
            raise OMFITexception(
                "Server '"
                + server
                + "' was not recognized.\nYou need to add '"
                + server
                + "' to the list of servers in OMFIT['MainSettings']['SERVER']"
            )

    return server


def _get_rdb_credential(server):
    """
    Provides the name of the encrypted credentials file
    :param server: string
        SQL database server. Each server can have its own file.
    :return: string
        Credential name
    """
    return 'rdb_{}:0'.format(translate_RDBserver(server))


def _read_rdb_password_from_file(server=None, filename=None):
    """
    Attempts to read a typical login file and get the username and password
    :param server: string
        Sets the default filenames to search
    :param filename: string
        Override the filename to search
    :return: (string, string)
        Username and password if successful or ('', '') if unsuccessful
    """
    username = ''
    password = ''
    files = {
        'huez': ['.pgdb', '.pgpass'],
        'pppl_postgres': ['.pgdb', '.pgpass'],
        'd3drdb': ['D3DRDB.sybase_login', 'd3drdb.sybase_login'],
        'd3dsqlsrvr': ['D3DRDB.sybase_login', 'd3drdb.sybase_login'],
        'd3sqlsrvr': ['D3SQLSRVR.sybase_login', 'd3sqlsrvr.sybase_login'],
        'east_database': ['east_database.sybase_login'],
        'energy': ['ENERGY.sybase_login'],
        'nstxrdb': ['nstxlogs.sybase_login'],
    }.get(translate_RDBserver(server), [''])
    files = [filename] if filename is not None else files

    def parse_login1(ff):
        return map(lambda x: x.strip(), ff.read().split(':')[-2:])

    def parse_login2(ff):
        return map(lambda x: x.strip(), ff.readlines()[-2:])

    parsers = [parse_login1, parse_login2]
    printq('Searching for {} login info in files {}'.format(server, files))
    for login_file in files:
        login_file = os.environ['HOME'] + os.sep + login_file
        if os.path.exists(login_file):
            for i, parser in enumerate(parsers):
                try:
                    printq('  Attempt {}: read {} login from {}'.format(i, server, login_file))
                    with open(login_file, 'r') as _f:
                        username, password = parser(_f)
                    printq('  Success: username {} from file on attempt {}.'.format(username, i))
                    break
                except Exception:
                    etype, value, tb = sys.exc_info()
                    exc_info = traceback.format_exception(etype, value, tb)
                    printq('  Fail attempt {} at reading {}; {} attempts left'.format(i, login_file, len(parsers) - 1 - i), exc_info)
        else:
            printq("  File {} doesn't exist; can't get login for {} from it.".format(login_file, server))
    return username, password


def get_public_rdb_login(server):
    """
    Returns the public or guest username and password for server
    :param server: string
    :return: (string, string)
    """
    default_user_pass = ('guest', 'guest_pwd')  # Applies to d3drdb, d3dsqlsrvr, d3sqlsrvr, east_database, energy
    return {'huez': ('d3dpub', 'd3dpub'), 'pppl_postgres': ('nstxpub', 'nstxpub')}.get(translate_RDBserver(server), default_user_pass)


def set_rdb_password(server, username=None, password=None, guest=False):
    """
    Sets up an encrypted password for OMFIT to use with SQL databases on a specific server
    :param server: string
        The server this credential applies to
    :param username: string
        Username on server. If a password is specified, this defaults to os.environ['USER'].
        If neither username nor password is specified, OMFIT will try to read both from a login file.
    :param password: string
        The password to be encrypted. Set to '' to erase the exting password for username@server, if there is one.
        If None, OMFIT will attempt to read it from a default login file, like .pgpass. This may or may not be the right
        password for server.
    :param guest: bool
        Use guest login and save it. Each server has its own, with the default being guest // guest_pwd .
    """
    cred = _get_rdb_credential(server)
    if password == '':
        printq('Reset credentials because password was ""')
        return reset_credential(credential=cred)
    elif guest:
        username, password = get_public_rdb_login(server)
    elif password is None:
        username, password = _read_rdb_password_from_file(server)
    elif username is None:
        username = os.environ['USER']

    if username is None or password is None:
        raise ValueError(
            'Failed to figure out a username and password combination to use for server {}. '
            'Try again with guest=True to load public/guest login.'
        )
    userpass = '{} {}'.format(username, password)
    encrypt_credential(credential=cred, password='', otp=userpass)
    printi('Encrypted credentials for {}@{}'.format(username, (translate_RDBserver(server))))
    return


def get_rdb_password(server, username=None, password=None, guest=False, guest_fallback_allowed=True):
    """
    Returns the RDB username and password for server
    :param server: string
        Servers can have different passwords, so you have to tell us which one you're after
    :param username: string
        Defaults to os.environ['USER']
    :param password: string [optional]
        Override decrypted credential and just return this input instead
    :param guest: bool
        Return guest login for server. Each server has its own, with the default being guest // guest_pwd .
    :param guest_fallback_allowed: bool
        Allowed to return guest credentials if look up fails. Otherwise, raise ValueError
    :return: (string, string)
        The username and password for server
    """
    if guest:
        return get_public_rdb_login(server)
    if username is None or password is None:
        userpass = decrypt_credential(_get_rdb_credential(server))[1].split(' ')
        username, password = userpass[0], ' '.join(userpass[1:])
        if not len(password):
            try:
                set_rdb_password(server)
            except Exception:
                pass
            else:
                userpass = decrypt_credential(_get_rdb_credential(server))[1].split(' ')
                username, password = userpass[0], ' '.join(userpass[1:])
    if not len(password):
        if guest_fallback_allowed:
            printq(f'Password lookup failed for {server}. Using guest/public credentials...')
            return get_public_rdb_login(server)
        raise ValueError(
            '''Use set_rdb_password('{server:}') to encrypt your password for {server:} (translates to {t_server:}).
            If your password for {server:} is in .pgpass in your home directory, it will be read from there.
            Otherwise, you must provide it to set_rdb_password().
            Your password for huez would be in .pgpass or .pgdb
            Your password for d3drdb would be in D3DRDB.sybase_login or d3drdb.sybase_login
            Your password for d3dsqlsrvr would be in D3SQLSRVR.sybase_login or d3sqlsrvr.sybase_login
            '''.format(
                server=server, t_server=translate_RDBserver(server)
            )
        )
    else:
        return username, password


class OMFITrdb(SortedDict):
    """
    Class used to connect to relational databases
    """

    def __init__(self, query=None, db='d3drdb', server='d3drdb', by_column=False):
        """
        :param query: string
            SQL SELECT query

        :param db: string
            database to connect to

        :param server: string
            SQL server to connect to (e.g. `d3drdb` as listed under OMFIT['MainSettings']['SERVER'])

        :param by_column: bool
            False: return results by rows (can be slow for large number of records)
                Result of .select() is a SortedDict with keys numbered 0, 1, ... and each holding another SortedDict,
                within which keys correspond to columns
            True: return results by columns
                Result of .select() is a SortedDict with keys corresponding to columns,
                each holding an array with length set by the number of rows selected.
        """
        SortedDict.__init__(self)
        self.dynaLoad = True

        self.query = query
        self.db = db
        self.server = server

        self.cnxn = None
        self.cursor = None

        self.by_column = by_column

    @property
    def postgresql(self):
        return self.db == 'd3d' or self.server == 'huez' or self.server == 'pppl_postgres'

    def _connect(self):
        """Connects to the database"""
        connection = self._setup_connection()
        try:
            if self.postgresql:
                import psycopg2

                try:
                    self.cnxn = psycopg2.connect(**connection)
                except psycopg2.OperationalError:
                    connection = self._setup_connection(force_tunnel=True)
                    self.cnxn = psycopg2.connect(**connection)
            else:
                self.cnxn = pyodbc.connect(**connection)
            self.cursor = self.cnxn.cursor()
        except Exception as _excp1:
            if "Login failed for user " in repr(_excp1) and self.server == 'd3drdb':
                raise ValueError(
                    """
Connection to the D3DRDB relational database requires the file D3DRDB.sybase_login to be present in the $HOME directory of the user on the workstation where OMFIT is running.
You should be able to copy this file from the $HOME folder on the GA iris cluster.
If this file is not available to you contact the GA computer group: iris-support@fusion.gat.com
"""
                )
            connection2 = {}
            try:
                if self.postgresql:
                    connection2 = connection
                    raise
                dsn = 'OMFIT_tmp'
                self._buildUserConfig(connection, dsn)
                connection2['DSN'] = dsn
                connection2['UID'] = connection['UID']
                connection2['PWD'] = connection['PWD']
                self.cnxn = pyodbc.connect(**connection2)
                self.cursor = self.cnxn.cursor()
            except Exception as _excp2:
                printe('\nFailed connection details: ' + repr(_excp1))
                printe(connection)
                printe('\nFailed connection details: ' + repr(_excp2))
                printe(connection2)
                printe('\n')
                raise

    @staticmethod
    def _buildUserConfig(connection, dsn):
        """
        Sets up OMFIT-related controls in the .odbc.ini file in the user's home directory
        :param connection: dict
            Contains connection information. Typically formed by self._setup_connection()
        :param dsn: string
            This is a tag or header name for the relevant section of the .odbc.ini file
        """
        filename = os.environ['HOME'] + os.sep + '.odbc.ini'

        # Create if it did not exist and give OMFIT full control over it
        header = '#--below this line OMFIT is in control of this file--\n'
        if not os.path.exists(filename):
            with open(filename, 'w') as f:
                f.write(header)

        # Retain what is above the header line
        with open(filename, 'r') as _f:
            top = _f.read().split(header)[0]

        # Text to add to .odbc.ini
        txt = []
        c = ''
        if '[' + dsn + ']' in top:
            c = '# '
        txt.append('')
        txt.append(c + '[' + dsn + ']')
        for item in connection:
            txt.append(c + item + ' = ' + str(connection[item]))
        txt.append('')

        # Write updated .odbc.ini
        with open(filename, 'w') as f:
            f.write(top + header + '\n'.join(txt))
        return

    def select(self, query=None, by_column=None):
        """
        Pass a query to the database, presumably with a SELECT statement in it

        :param query: string
            A string such as "SELECT * from profile_runs where shot=126006";
            if None then use the query used to instantiate the object
        :param by_column: bool [optional]
            If True or False, override the self.by_column set at instantiation
        :return: SortedDict
            by_column = False:
                Keys are numbered 0, 1, 2, ...
                The value behind each key is a SortedDict
                The keys of the child SortedDict are the columns selected
            by_column = True:
                Keys are column names
                Values are arrays with length set by the number of rows selected
        """
        if query is None and self.query is None:
            return SortedDict()
        if self.cnxn is None or self.cursor is None:
            self._connect()
            if not self.postgresql:
                self.cursor.execute("use " + self.db)

        if query is None:
            query = self.query
        if by_column is None:
            by_column = self.by_column
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        if self.postgresql:
            colnames = [desc[0] for desc in self.cursor.description]
        else:
            colnames = None

        res = SortedDict()
        # Not by column can be very computationally expensive if there are many records
        if not by_column:
            for r, row in enumerate(rows):
                res[r] = SortedDict()
                for c, col in enumerate(row):
                    if not self.postgresql:
                        name = row.cursor_description[c][0]
                    else:
                        name = colnames[c]
                    res[r][name] = row[c]

        # Faster, by column organization
        else:
            for r, row in enumerate(rows):
                names = []
                for c, col in enumerate(row):
                    if not self.postgresql:
                        name = row.cursor_description[c][0]
                    else:
                        name = colnames[c]
                    if name in names:
                        continue
                    names.append(name)
                    if r == 0:
                        res[name] = []
                    res[name].append(row[c])
            for name in list(res.keys()):
                res[name] = np.array(res[name])

        return res

    def custom_procedure(self, procedure, commit=True, **arguments):
        """
        Pass an arbitrary custom procedure to the sql database

        :param procedure: string
            A string that represents the custom procedure to be called
        :param commit (bool): If set to False it will not commit the data to the coderunrdb. This should be done when running a
            jenkins test, otherwise it may attempt to write data to the same shot/runid twice and throw an error.
        :return: Dict
            Output list of pyodbc rows returned by the custom query
        """
        arguments = ', '.join(
            [
                "@%s='%s'" % (arg, arguments[arg]) if isinstance(arguments[arg], str) else "@%s=%s" % (arg, arguments[arg])
                for arg in arguments
            ]
        )
        command = "exec %s " % (procedure) + arguments
        if self.cnxn is None or self.cursor is None:
            self._connect()
            self.cursor.execute("use " + self.db)
        self.cursor.execute(command)
        rows = self.cursor.fetchall()
        if commit:
            self.cnxn.commit()
        return rows

    def alter_add(self, table, column_name, column_type, commit=True, verbose=True):
        """
        Alter table in SQL database by adding a column

        :param table: string
            table name

        :param column_name: string
            column name

        :param column_type: string
            column type, has to be an SQL DataType, e.g. BOOLEAN, FLOAT etc..

        :param commit: bool
            commit alter command to SQL

        :param verbose: bool
            print SQL command being used
        """
        if self.postgresql:
            raise NotImplementedError('File issue on Github if this is needed')

        if self.cnxn is None or self.cursor is None:
            self._connect()
            self.cursor.execute("use " + self.db)

        sql_cmd = "ALTER TABLE %s ADD %s %s" % (table, str(column_name), str(column_type))

        if verbose:
            printi(sql_cmd)

        self.cursor.execute(sql_cmd)
        if commit:
            self.commit()
        return sql_cmd

    def alter_drop(self, table, column_name, commit=True, verbose=True):
        """
        Alter table in SQL database by dropping a column

        :param table: string
            table name

        :param column_name: string
            column name

        :param commit: bool
            commit alter command to SQL

        :param verbose: bool
            print SQL command being used

        :return: string
            SQL command
        """
        if self.postgresql:
            raise NotImplementedError('File issue on Github if this is needed')

        if self.cnxn is None or self.cursor is None:
            self._connect()
            self.cursor.execute("use " + self.db)

        sql_cmd = "ALTER TABLE %s DROP COLUMN %s" % (table, str(column_name))

        if verbose:
            printi(sql_cmd)

        self.cursor.execute(sql_cmd)
        if commit:
            self.commit()
        return sql_cmd

    def delete(self, table, where, commit=True, verbose=True):
        """
        Delete row(s) in SQL database

        :param table: string
            table where to update

        :param where: string or dict
            Which record or records should be deleted
            NOTE that all records that satisfy this condition will be deleted!
            A dict will be converted into a string of the form "key1=value1 and key2=value2 ..."

        :param commit: bool
            commit delete to SQL

        :param verbose: bool
            print SQL command being used
        """
        if self.cnxn is None or self.cursor is None:
            self._connect()
            self.cursor.execute("use " + self.db)

        if isinstance(where, dict):
            where = ' and '.join([str(x[0]) + '=' + repr(x[1]) for x in zip(list(where.keys()), list(where.values()))])
        sql_cmd = "DELETE FROM %s WHERE %s" % (table, where)

        if verbose:
            printi(sql_cmd)

        self.cursor.execute(sql_cmd)
        if commit:
            self.commit()
        return sql_cmd

    def commit(self):
        """
        Commit commands in SQL database
        """

        printq('committing')
        self.cnxn.commit()

    def update(self, table, data, where, commit=True, overwrite=1, verbose=True):
        """
        Update row(s) in SQL database

        :param table: string
            Table to update.

        :param data: dict
            Keys are columns to update and values are values to put into those columns.

        :param where: dict or string
            Which record or records should be updated.
            NOTE that all records that satisfy this condition will be updated!
            If it's a dictionary, the columns/data condition will be concatenated with " AND ", so that
                {'my_column': 5.2, 'another_col': 7} becomes "my_column=5.2 AND another_col=7".
            A string will be used directly.

        :param commit: bool
            Commit update to SQL. Set to false for testing without editing the database.

        :param overwrite: bool or int
            0/False: If any of the keys in data already have entries in the table, do not update anything
            1/True: Update everything. Don't even check.
            2: If any of the keys in dat already have entries in the table, don't update those,
               but DO write missing entries.

        :param verbose: bool
            Print SQL command being used.

        :return: string
            The SQL command that would be used.
            If the update is aborted due to overwrite avoidance, the SQL command will be prefixed by "ABORT:"
        """
        if self.cnxn is None or self.cursor is None:
            self._connect()
            if not self.postgresql:
                self.cursor.execute("use " + self.db)

        def mk_kv_list(a):
            """
            Turns a dictionary of columns and values into a list of strings of the form 'k=v'
            to be later concatenated by ", " or " AND "
            :param a: dict-like
            :return: list of strings
            """
            return [str(x[0]) + '=' + x[1] for x in zip(list(a.keys()), tolist(self._sqlRepr(list(a.values()))))]

        if isinstance(where, dict):
            where = ' AND '.join(mk_kv_list(where))
        if len(where):
            where = ' WHERE ' + where
        columns_values = ', '.join(mk_kv_list(data))

        sql_cmd = "UPDATE %s SET %s%s" % (table, columns_values, where)
        if verbose:
            printi(sql_cmd)

        if overwrite not in [1, True, 1.0]:
            # Need to check for pre-existing data
            columns = ', '.join(list(data.keys()))
            query = 'SELECT {columns:} FROM {table:}{where:}'.format(**locals())
            results = self.select(query=query, by_column=False)
            results_with_content = []
            for result in results.values():
                cleaned_result = {k: v for k, v in result.items() if v is not None}
                if len(cleaned_result):
                    results_with_content += [cleaned_result]
            if len(results_with_content) and overwrite == 0:
                printw('Requested update aborted to avoid overwriting some data.')
                return 'ABORT:' + sql_cmd
            elif len(results_with_content) and overwrite > 1:
                skipped_columns = []
                for cleaned_result in results_with_content:
                    for key in cleaned_result:
                        data.pop(key, None)
                        skipped_columns += [key]
                if len(data) == 0:
                    printw('To avoid overwriting, all data were removed from the update list & there is nothing to do.')
                    return 'ABORT:' + sql_cmd
                else:
                    columns_values = ', '.join(mk_kv_list(data))
                    sql_cmd = "UPDATE %s SET %s%s" % (table, columns_values, where)
                    printq('New update list: {}'.format(columns_values))
                    printq('Data removed: {}'.format(list(set(skipped_columns))))
                    if verbose:
                        print('Update command after avoiding overwriting anything:')
                        printi(sql_cmd)

        self.cursor.execute(sql_cmd)
        if commit:
            self.commit()
        return sql_cmd

    def insert(self, table, data, duplicate_key_update=False, commit=True, verbose=True):
        """
        Insert row in SQL database

        :param table: string
            table where data will be inserted

        :param data: dict, list, or tuple
            dict: keys are column names
            list or tuple:
            dictionary (columns & values) or list/tuple of values

        :param duplicate_key_update: bool
            append ' ON DUPLICATE KEY UPDATE' to INSERT command

        :param commit: bool
            commit insert to SQL

        :param verbose: bool
            print SQL command being used

        :return: The SQL command that was used or would be used
        """
        if self.cnxn is None or self.cursor is None:
            self._connect()
            if not self.postgresql:
                self.cursor.execute("use " + self.db)

        if isinstance(data, (list, tuple)):
            values = (','.join(["%s"] * len(data))) % tuple(self._sqlRepr(data))
            sql_cmd = "INSERT INTO %s VALUES (%s)" % (table, values)
        else:
            columns = (','.join(["%s"] * len(data))) % tuple(data.keys())
            values = (','.join(["%s"] * len(data))) % tuple(self._sqlRepr(list(data.values())))
            sql_cmd = "INSERT INTO %s (%s) VALUES (%s)" % (table, columns, values)

        if duplicate_key_update:
            sql_cmd += ' ON DUPLICATE KEY UPDATE'

        if verbose:
            printi(sql_cmd)

        self.cursor.execute(sql_cmd)
        if commit:
            self.commit()
        return sql_cmd

    def copy_row(self, table, **kw):
        r"""
        Copy one row of a table to a new row of a table

        :param table: string
            table in the database for which to copy a row
        :param \**kw: The keywords passed must be the primary keys of the table.
               The values of the keywords must be two-element containers: (copy_from, copy_to)
        :return: string
            SQL command
        """
        if not self.postgresql:
            raise NotImplemented('File issue on GitHub if needed')
        if self.cnxn is None or self.cursor is None:
            self._connect()
            if not self.postgresql:
                self.cursor.execute("use " + self.db)

        primary = self.primary_keys(table)
        for k in kw:
            if k not in primary:
                raise ValueError('%s is not a primary key; only primary keys allowed for copying a row' % k)
        where = []
        where2 = []
        for k, v in list(kw.items()):
            where.append('%s=%s' % (k, self._sqlRepr(v[0])))
            where2.append('%s=%s' % (k, self._sqlRepr(v[1])))
        query = 'SELECT * from %s where %s' % (table, ' and '.join(where))
        copy_from = self.select(query)[0]
        if 'userid' in copy_from:
            copy_from['userid'] = self.username
        for k, v in list(kw.items()):
            copy_from[k] = v[1]
        insert_row = 'INSERT INTO {0}({1}) VALUES ({2});'.format(
            table, ','.join(list(copy_from.keys())), ','.join(['%s'] * len(list(copy_from.values())))
        )
        self.cursor.execute(insert_row, list(copy_from.values()))
        self.commit()
        return insert_row

    def primary_keys(self, table):
        """
        Return the keys that are the primary keys of the table

        :param table: string
            table for which to evaluate the primary keys
        :return: list of strings
        """
        if not self.postgresql:
            raise NotImplemented('File issue on GitHub if needed')
        if self.cnxn is None or self.cursor is None:
            self._connect()
            if not self.postgresql:
                self.cursor.execute("use " + self.db)

        self.cursor.execute("SELECT indexdef from pg_indexes where tablename = '%s'" % table)
        return list(map(lambda x: str(x).strip(), self.cursor.fetchall()[0][0].split('(')[1].split(')')[0].split(',')))

    def _sqlRepr(self, data):
        """
        Forms the SQL representation of data
        :param data: dict
        :return: string
        """
        if self.postgresql:
            # Adapted from Osborne tools setup_run_table._value_to_dbstring:
            # CONVERT PYTHON VALUE TO EXPRESSION FOR ENTRY INTO DB TABLE
            sl = []
            for v in np.atleast_1d(data):
                if isinstance(v, str):
                    s = "'" + v + "'"
                elif v is None:
                    s = 'NULL'
                elif np.iterable(v):
                    s = '{'
                    for x in v:
                        if isinstance(x, str):
                            s = s[:] + '"' + x + '",'
                        else:
                            s = s[:] + str(x) + ','
                    if len(v):
                        s = s[:-1] + '}'
                    else:
                        s = s[:] + '}'
                    s = "'" + s + "'"
                else:
                    s = str(v)
                sl.append(s)
            if len(sl) == 1:
                return sl[0]
            return sl
        else:
            data_out = []
            for k, d in enumerate(np.atleast_1d(data)):
                if d is None or (is_numeric(d) and np.isnan(d)):
                    data_out.append('NULL')
                else:
                    data_out.append(repr(d))
            return data_out

    def __getstate__(self):
        return {
            'query': self.query,
            'db': self.db,
            'server': self.server,
            'cnxn': None,
            'cursor': None,
            'dynaLoad': self.dynaLoad,
            'by_column': self.by_column,
        }

    def __setstate__(self, new_state):
        """
        :param new_state: dict or tuple containing dict in [0]
        """
        if isinstance(new_state, tuple):
            new_state = new_state[0]
        for k in list(new_state.keys()):
            setattr(self, k, new_state[k])
        if 'by_column' not in new_state:
            self.by_column = False
        return

    @dynaLoad
    def load(self):
        """
        Connect to the database and retrieve its content
        """
        if self.query is not None:
            self.clear()
            res = self.select()
            SortedDict.update(self, res)

    def _setup_connection(self, force_tunnel=False):
        # Get server/tunnel from OMFIT['MainSettings']['SERVER'] list
        server0 = translate_RDBserver(self.server, _RDBserverDict)
        MS_server0 = OMFIT['MainSettings']['SERVER'][server0]
        server = MS_server0['RDB_server']
        tunnel = MS_server0.get('tunnel', '')

        # Try directly connecting to the RDB server
        if server not in OMFITaux['RDBserverReachable']:
            OMFITaux['RDBserverReachable'][server] = test_connection(None, *parse_server(server)[2:], timeout=1, ntries=1)

        rdb_server = list(parse_server(server))
        username, password = get_rdb_password(server0)
        if username != rdb_server[0]:
            printw(
                "username from get_rdb_password({}) ({}) != username indicated by MainSettings ({})".format(
                    server0, username, rdb_server[0]
                )
            )
        self.username = username

        # If direct connection fails, use tunneling
        if not OMFITaux['RDBserverReachable'][server] or force_tunnel:
            # Handle server tunneling (this function does already buffering)
            rdb_server[2:] = list(map(str, setup_ssh_tunnel(server, tunnel, True)))[1:]

        connection = {}
        if not self.postgresql:
            connection['UID'] = username
            connection['PWD'] = password
            connection['SERVER'] = rdb_server[2]
            connection['PORT'] = rdb_server[3]
            if 'instance' in MS_server0:
                del connection['PORT']
                connection['SERVER'] = rf"{connection['SERVER']}\{MS_server0['instance']}"
            driver = 'tdsodbc'
            if 'driver' in MS_server0:
                connection['DRIVER'] = driver = evalExpr(MS_server0['driver'])
            if isinstance(driver, str) and driver and os.sep not in driver and driver not in pyodbc.drivers():
                connection['DRIVER'] = find_library(driver)
            if not isinstance(connection['DRIVER'], str) or not connection['DRIVER']:
                raise OMFITexception(
                    'The library to drive your `' + str(driver) + '` SQL connection is not setup properly.\n' + repr(connection)
                )
            if 'tdsodbc' in driver:
                connection['TDS_Version'] = '8.0'
            for k in MS_server0:
                if k not in list(connection.keys()) + ['driver', 'server', 'tunnel', 'RDB_server', 'instance']:
                    connection[k] = MS_server0[k]
        else:
            connection['user'] = username
            connection['password'] = password
            connection['host'] = rdb_server[2]
            connection['port'] = rdb_server[3]
            connection['database'] = self.db
        printq('')
        printq(server)
        for k in list(connection.keys()):
            printq(k + '\t\t:\t ' + str(connection[k]))

        return connection

    def get_databases(self):
        '''
        Return a list of databases on the server
        '''
        return sorted(list(self.select('select name from sys.databases', by_column=True)['name']))

    def get_tables(self):
        '''
        Return a list of tables on the given database
        '''
        return sorted(list(self.select('select table_name from information_schema.tables', by_column=True)['table_name']))

    def get_columns(self, table):
        '''
        Return a list of columns in the given table
        '''
        if table not in self.get_tables():
            raise RuntimeError(f'Table {table} not in {self.get_tables()}')
        return sorted(
            list(
                self.select(f"select column_name from information_schema.columns where table_name='{table}'", by_column=True)['column_name']
            )
        )

    def get_db_structure(self):
        '''
        Return a nested list of tables and columns of those tables within the current database
        '''
        result = {}
        for table in self.get_tables():
            result[table] = []
            for column in self.get_columns(table):
                result[table].append(column)
        return result


def available_efits_from_rdb(scratch, device, shot, default_snap_list=None, format='{tree}', **kw):
    """
    :param scratch: dict
        dictionary where the information is cached (to avoid querying SQL database multiple times)

    :param device: string
        device for which to query list of available EFITs

    :param shot: int
        shot for which to query list of available EFITs

    :param default_snap_list: dict
        dictionary to which list of available efits will be passed

    :param format: string
        format in which to write list of available efits (tree, by, com, drun, runid) are possible options

    :param **kw: quietly accepts and ignores other keywords for compatibility with other similar functions

    :return: (dict, str)
        dictionary with list of available options formatted as {text:format}
        information about the discovered EFITs
    """
    efit_sql = f'EFIT_SQL_{device}_{shot}'
    if default_snap_list is None:
        default_snap_list = {'': ''}
    snap_list = copy.deepcopy(default_snap_list)
    help = ''
    scratch.setdefault('searched_in', [])
    scratch['searched_in'] += ['rdb']
    if is_device(device, ['DIII-D', 'NSTX', 'NSTXU']):
        try:
            query = "SELECT * FROM plasmas WHERE shot=" + str(shot) + " AND code_name='EFIT' AND deleted!=1 ORDER BY tree"
            try:
                if scratch[efit_sql].query != query:
                    scratch[efit_sql] = OMFITrdb(query, 'code_rundb', server=device)
            except Exception:
                scratch[efit_sql] = OMFITrdb(query, 'code_rundb', server=device)
            runids = scratch[efit_sql].across("['*']['shot']")
            try:
                runids = scratch[efit_sql].across("['*']['run_id']")
            except Exception:
                pass
            for tree, by, com, drun, tag, runid in zip(
                *(
                    scratch[efit_sql].across("['*']['tree']"),
                    scratch[efit_sql].across("['*']['run_by']"),
                    scratch[efit_sql].across("['*']['run_comment']"),
                    scratch[efit_sql].across("['*']['date_run']"),
                    scratch[efit_sql].across("['*']['runtag']"),
                    runids,
                )
            ):
                if tree == 'EFIT':
                    item = by + ' ' + tag
                    tree = int(runid)
                elif by in ['autoload', 'mdsadmin']:
                    item = f'{tree} {tag}'
                else:
                    item = f'{tree} by {tag}'

                help += '[' + item + '] : "' + com.strip() + '"\n'
                if drun is not None:
                    snap_list['[' + item + '] ' + drun.strftime(' (%d %b %Y @ %H:%M)')] = format.format(
                        tree=tree, runid=runid, by=by, com=com, drun=drun, tag=tag
                    )

                else:
                    snap_list['[' + item + '] ' + ' (???)'] = format.format(tree=tree, runid=runid, by=by, com=com, drun=drun, tag=tag)
                scratch['available_efits_from_rdb_success'] = True

        except Exception as _excp:
            scratch['available_efits_from_rdb_success'] = False
            raise
            printe('Could not retrieve list of available EFIT runs: ' + repr(_excp))
            snap_list = {'EFIT01': 'EFIT01', 'EFIT02': 'EFIT02'}
            help = 'Enter EFIT tree by hand\n\nCould not retrieve list of available EFIT runs:\n' + repr(_excp)
    else:
        scratch['available_efits_from_rdb_success'] = False
    help = help.strip()
    return snap_list, help
