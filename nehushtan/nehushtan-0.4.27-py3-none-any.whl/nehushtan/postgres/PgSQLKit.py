from typing import Optional, List

import psycopg2
from psycopg2 import extensions

from nehushtan.postgres.PgSQLKitConfig import PgSQLKitConfig
from nehushtan.postgres.PgSQLResultSet import PgSQLResultSet


class PgSQLKit:
    """
    Since 0.4.22
    """

    def __init__(self, config: PgSQLKitConfig):
        self.__connection = psycopg2.connect(config.dsn())
        self.set_auto_commit(config.autocommit())

    def get_raw_connection(self):
        """
        use `with` this result to handle a transcation in autocommit mode.
        """
        return self.__connection

    def get_dsn_of_connection(self) -> str:
        """
        Read-only string containing the connection string used by the connection.
        If a password was specified in the connection string it will be obscured.
        """
        return self.__connection.dsn

    def get_cursor(self, scrollable: bool = None, withhold: bool = None):
        cursor = self.__connection.cursor()
        if scrollable is not None:
            cursor.scrollable = scrollable
        if withhold is not None:
            cursor.withhold = withhold
        return cursor

    def close_connection(self):
        """
        Close the connection now (rather than whenever del is executed).
            The connection will be unusable from this point forward;
                an InterfaceError will be raised if any operation is attempted with the connection.
            The same applies to all cursor objects trying to use the connection.
            Note that closing a connection without committing the changes first
                will cause any pending change to be discarded as if a ROLLBACK was performed
                    (unless a different isolation level has been selected: see set_isolation_level()).

        Changed in version 2.2:
            previously an explicit ROLLBACK was issued by Psycopg on close().
            The command could have been sent to the backend at an inappropriate time,
            so Psycopg currently relies on the backend to implicitly discard uncommitted changes.
            Some middleware are known to behave incorrectly though when the connection is closed during a transaction
                (when status is STATUS_IN_TRANSACTION),
                e.g. PgBouncer reports an unclean server and discards the connection.
            To avoid this problem you can ensure to terminate the transaction with a commit()/rollback() before closing.
        """
        if self.__connection:
            self.__connection.close()

    def is_closed(self) -> bool:
        """
        Read-only integer attribute: 0 if the connection is open, nonzero if it is closed or broken.
        """
        return True if self.__connection.closed != 0 else False

    def __del__(self):
        self.close_connection()

    def execute(self, sql: str, variables=None):
        cursor = self.get_cursor()
        """
        cursor.execute(query, vars=None)
        
        Execute a database operation (query or command).
        Parameters may be provided as sequence or mapping and will be bound to variables in the operation. 
            Variables are specified either with positional (%s) or named (%(name)s) placeholders. 
            See Passing parameters to SQL queries.
        The method returns None. 
            If a query was executed, the returned values can be retrieved using fetch*() methods.
        """
        if variables:
            cursor.execute(sql, variables)
        else:
            cursor.execute(sql)
        return PgSQLResultSet(cursor)

    def mogrify(self, sql: str, variables=None) -> bytes:
        cursor = self.get_cursor()
        """
        mogrify(operation[, parameters])

        Return a query string after arguments binding. 
            The string returned is exactly the one 
                that would be sent to the database running the execute() method or similar.
        The returned string is always a bytes string.
        """
        if variables:
            return cursor.mogrify(sql, variables)
        else:
            return cursor.mogrify(sql)

    def call_function(self, fucntion_name: str, parameters: None):
        cursor = self.get_cursor()
        """
        callproc(procname[, parameters])

        Call a stored database procedure with the given name. 
            The sequence of parameters must contain one entry for each argument that the procedure expects. 
            Overloaded procedures are supported. 
            Named parameters can be used by supplying the parameters as a dictionary.
        This function is, at present, not DBAPI-compliant. 
            The return value is supposed to consist of the sequence of parameters 
                with modified output and input or output parameters. 
            In future versions, the DBAPI-compliant return value may be implemented, 
                but for now the function returns None.
        The procedure may provide a result set as output. 
            This is then made available through the standard fetch*() methods.

        Changed in version 2.7: added support for named arguments.
        Note 
            callproc() can only be used with PostgreSQL functions, 
                not with the procedures introduced in PostgreSQL 11, 
                which require the CALL statement to run. 
            Please use a normal execute() to run them.
        """
        if parameters:
            cursor.callproc(fucntion_name, parameters)
        else:
            cursor.callproc(fucntion_name)
        return PgSQLResultSet(cursor)

    def cancel(self):
        """
        Cancel the current database operation.
        The method interrupts the processing of the current operation.
            If no query is being executed, it does nothing.
            You can call this function from a different thread than the one currently executing a database operation,
            for instance if you want to cancel a long running query if a button is pushed in the UI.
            Interrupting query execution will cause the cancelled method to raise a QueryCanceledError.
            Note that the termination of the query is not guaranteed to succeed: see the documentation for PQcancel().
        New in version 2.3.
        """
        self.__connection.cancel()

    def reset(self):
        """
        Reset the connection to the default.
        The method rolls back an eventual pending transaction
            and executes the PostgreSQL RESET and SET SESSION AUTHORIZATION to revert the session to the default values.
        A two-phase commit transaction prepared using tpc_prepare() will remain in the database available for recover.
        New in version 2.0.12.
        """
        self.__connection.reset()

    def commit(self):
        """
        Commit any pending transaction to the database.
        By default, Psycopg opens a transaction before executing the first command:
            if commit() is not called, the effect of any data manipulation will be lost.
        The connection can be also set in “autocommit” mode:
            no transaction is automatically open, commands have immediate effect.
            See [Transactions control](https://www.psycopg.org/docs/usage.html#transactions-control) for details.
        Changed in version 2.5:
            if the connection is used in a with statement,
                the method is automatically called if no exception is raised in the with block.
        """
        self.__connection.commit()

    def rollback(self):
        """
        Roll back to the start of any pending transaction.
            Closing a connection without committing the changes first will cause an implicit rollback to be performed.
        Changed in version 2.5:
            if the connection is used in a with statement,
            the method is automatically called if an exception is raised in the with block.
        """
        return self.__connection.rollback()

    def __xid(self, format_id, gtrid, bqual):
        """
        Returns a Xid instance to be passed to the tpc_*() methods of this connection.
            The argument types and constraints are explained in Two-Phase Commit protocol support.
        The values passed to the method will be available on the returned object as the members format_id, gtrid, bqual.
        The object also allows accessing to these members and unpacking as a 3-items tuple.
        """
        return self.__connection.xid(format_id, gtrid, bqual)

    def __tpc_begin(self, xid):
        """
        Begins a TPC transaction with the given transaction ID xid.
        This method should be called outside of a transaction
            (i.e. nothing may have executed since the last commit() or rollback()
                and connection.status is STATUS_READY).
        Furthermore, it is an error to call commit() or rollback() within the TPC transaction:
            in this case a ProgrammingError is raised.
        The xid may be either an object returned by the xid() method or a plain string:
            the latter allows to create a transaction using the provided string as PostgreSQL transaction id.
            See also tpc_recover().
        """
        return self.__connection.tpc_begin(xid)

    def __tpc_prepare(self):
        """
        Performs the first phase of a transaction started with tpc_begin().
            A ProgrammingError is raised if this method is used outside of a TPC transaction.
        After calling tpc_prepare(), no statements can be executed until tpc_commit() or tpc_rollback() will be called.
        The reset() method can be used to restore the status of the connection to STATUS_READY:
            the transaction will remain prepared in the database
                and will be possible to finish it with tpc_commit(xid) and tpc_rollback(xid).
        See also the PREPARE TRANSACTION PostgreSQL command.
        """
        return self.__connection.tpc_prepare()

    def __tpc_commit(self, xid=None):
        """
        When called with no arguments, tpc_commit() commits a TPC transaction previously prepared with tpc_prepare().
        If tpc_commit() is called prior to tpc_prepare(), a single phase commit is performed.
        A transaction manager may choose to do this
            if only a single resource is participating in the global transaction.
        When called with a transaction ID xid, the database commits the given transaction.
        If an invalid transaction ID is provided, a ProgrammingError will be raised.
        This form should be called outside of a transaction, and is intended for use in recovery.
        On return, the TPC transaction is ended.
        See also the COMMIT PREPARED PostgreSQL command.
        """
        if xid:
            return self.__connection.tpc_commit(xid)
        else:
            return self.__connection.tpc_commit()

    def __tpc_rollback(self, xid=None):
        """
        When called with no arguments, tpc_rollback() rolls back a TPC transaction.
        It may be called before or after tpc_prepare().
        When called with a transaction ID xid, it rolls back the given transaction.
        If an invalid transaction ID is provided, a ProgrammingError is raised.
        This form should be called outside of a transaction, and is intended for use in recovery.
        On return, the TPC transaction is ended.
        See also the ROLLBACK PREPARED PostgreSQL command.
        """
        if xid:
            return self.__connection.tpc_rollback(xid)
        else:
            return self.__connection.tpc_rollback()

    def __tpc_recover(self):
        """
        Returns a list of Xid representing pending transactions, suitable for use with tpc_commit() or tpc_rollback().
        If a transaction was not initiated by Psycopg, the returned Xids will have attributes
            format_id and bqual set to None
            and the gtrid set to the PostgreSQL transaction ID:
                such Xids are still usable for recovery.
        Psycopg uses the same algorithm of the PostgreSQL JDBC driver to encode a XA triple in a string,
            so transactions initiated by a program using such driver should be unpacked correctly.
        Xids returned by tpc_recover() also have extra attributes prepared,
            owner, database populated with the values read from the server.
        See also the pg_prepared_xacts system view.
        """
        return self.__connection.tpc_recover()

    def set_session(self, isolation_level=None, readonly=None, deferrable=None, autocommit=None):
        """
        Set one or more parameters for the next transactions or statements in the current session.
        The function must be invoked with no transaction in progress.

        Parameters:
        * isolation_level
            set the isolation level for the next transactions/statements.
            The value can be one of the literal values
                READ UNCOMMITTED,
                READ COMMITTED,
                REPEATABLE READ,
                SERIALIZABLE
                or the equivalent constant defined in the extensions module.
        * readonly
            if True, set the connection to read only;
            read/write if False.
        * deferrable
            if True, set the connection to deferrable;
            non deferrable if False.
            Only available from PostgreSQL 9.1.
        * autocommit
            switch the connection to autocommit mode:
                not a PostgreSQL session setting but an alias for setting the autocommit attribute.
        """
        modification = {}
        if isolation_level:
            modification['isolation_level'] = isolation_level
        if readonly:
            modification['readonly'] = readonly
        if deferrable:
            modification['deferrable'] = deferrable
        if autocommit:
            modification['autocommit'] = autocommit
        self.set_session(**modification)

    def is_auto_commit(self) -> bool:
        return self.__connection.autocommit

    def set_auto_commit(self, auto_commit: bool):
        self.__connection.autocommit = auto_commit

    def get_isolation_level(self) -> Optional[int]:
        """
        use psycopg2.extensions.ISOLATION_LEVEL_*
        """
        return self.__connection.isolation_level

    def set_isolation_level(self, isolation_level: Optional[int]):
        self.__connection.isolation_level = isolation_level

    def is_readonly(self) -> Optional[bool]:
        return self.__connection.readonly

    def set_readonly(self, readonly: Optional[bool]):
        self.__connection.readonly = readonly

    def is_deferrable(self) -> Optional[bool]:
        return self.__connection.deferrable

    def set_deferrable(self, deferrable: Optional[bool]):
        self.__connection.deferrable = deferrable

    def get_encoding(self):
        """
        Read the client encoding for the current session.
        The default is the encoding defined by the database.
        It should be one of the characters set supported by PostgreSQL
        """
        return self.__connection.encoding

    def set_client_encoding(self, enc):
        """
        set the client encoding for the current session.
        The default is the encoding defined by the database.
        It should be one of the characters set supported by PostgreSQL
        """
        return self.__connection.set_client_encoding(enc)

    def get_notices(self) -> List[str]:
        """
        A list containing all the database messages sent to the client during the session.
        """
        return self.__connection.notices

    def get_notifies(self) -> list:
        """
        List of Notify objects containing asynchronous notifications received by the session.
        For other details see Asynchronous notifications.
        """
        return self.__connection.notifies

    def get_conection_info(self):
        """
        A ConnectionInfo object exposing information about the native libpq connection.
        """
        return self.__connection.info

    def get_status(self):
        """
        A read-only integer representing the status of the connection.
            Symbolic constants for the values are defined in the module psycopg2.extensions:
                see Connection status constants for the available values.
        The status is undefined for closed connections.
        """
        return self.__connection.status

    def __lobject(self, oid=0, mode=0, new_oid=0, new_file=None, lobject_factory=extensions.lobject):
        return self.__connection.lobject(oid, mode, new_oid, new_file, lobject_factory)

    def get_transaction_status(self):
        """
        Also available as info.transaction_status.
        Return the current session transaction status as an integer.
            Symbolic constants for the values are defined in the module psycopg2.extensions:
                see Transaction status constants for the available values.
        See also libpq docs for PQtransactionStatus() for details.
        """
        return self.__connection.get_transaction_status()

    def get_protocol_version(self):
        """
        Also available as info.protocol_version.
        A read-only integer representing frontend/backend protocol being used.
            Currently Psycopg supports only protocol 3,
                which allows connection to PostgreSQL server from version 7.4.
            Psycopg versions previous than 2.3 support both protocols 2 and 3.
        See also libpq docs for PQprotocolVersion() for details.
        New in version 2.0.12.
        """
        return self.__connection.protocol_version

    def get_server_version(self):
        """
        Also available as info.server_version.
        A read-only integer representing the backend version.
        The number is formed by converting the major, minor, and revision numbers
            into two-decimal-digit numbers and appending them together.
        For example, version 8.1.5 will be returned as 80105.
        See also libpq docs for PQserverVersion() for details.
        New in version 2.0.12.
        """
        return self.__connection.server_version

    def get_backend_pid(self):
        """
        Also available as info.backend_pid.
        Returns the process ID (PID) of the backend server process you connected to.
            Note that if you use a connection pool service such as PgBouncer this value will not be updated
                if your connection is switched to a different backend.
        Note that the PID belongs to a process executing on the database server host, not the local host!
        See also libpq docs for PQbackendPID() for details.
        New in version 2.0.8.
        """
        return self.__connection.get_backend_pid()

    def get_parameter_status(self, parameter):
        """
        Also available as info.parameter_status().
        Look up a current parameter setting of the server.
        Potential values for parameter are:
            server_version, server_encoding, client_encoding, is_superuser, session_authorization,
            DateStyle, TimeZone, integer_datetimes, and standard_conforming_strings.
        If server did not report requested parameter, return None.
        See also libpq docs for PQparameterStatus() for details.
        New in version 2.0.12.
        """
        return self.__connection.get_parameter_status(parameter)

    def get_dsn_parameters(self):
        """
        Also available as info.dsn_parameters.
        Get the effective dsn parameters for the connection as a dictionary.
        The password parameter is removed from the result.
        Requires libpq >= 9.3.
        See also libpq docs for PQconninfo() for details.
        New in version 2.7.
        """
        return self.__connection.get_dsn_parameters()
