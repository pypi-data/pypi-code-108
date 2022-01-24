from typing import Optional, List

from psycopg2 import ProgrammingError


class PgSQLResultSet:
    """
    Since 0.4.22
    @see https://www.psycopg.org/docs/cursor.html#cursor
    """

    def __init__(self, cursor):
        self.__cursor = cursor

    def __del__(self):
        self.close()

    def get_raw_cursor(self):
        return self.__cursor

    def get_description(self):
        return self.__cursor.description

    def close(self):
        if self.__cursor:
            self.__cursor.close()

    def is_closed(self) -> bool:
        return self.__cursor.closed

    def is_scrollable(self) -> bool:
        return self.__cursor.scrollable

    def is_withhold(self) -> bool:
        return self.__cursor.withhold

    def fetch_one_row(self) -> Optional[tuple]:
        """
        Fetch the next row of a query result set,
            returning a single tuple, or None when no more data is available.
        A ProgrammingError is raised
            if the previous call to execute*() did not produce any result set or no call was issued yet.
        """
        return self.__cursor.fetchone()

    def fetch_next_batch_of_rows(self, size: int = None) -> List[tuple]:
        """
        Fetch the next set of rows of a query result,
            returning a list of tuples.
            An empty list is returned when no more rows are available.
        The number of rows to fetch per call is specified by the parameter.
            If it is not given, the cursor’s arraysize determines the number of rows to be fetched.
            The method should try to fetch as many rows as indicated by the size parameter.
            If this is not possible due to the specified number of rows not being available,
                fewer rows may be returned.
        A ProgrammingError is raised
            if the previous call to execute*() did not produce any result set or no call was issued yet.
        Note
            there are performance considerations involved with the size parameter.
            For optimal performance, it is usually best to use the arraysize attribute.
            If the size parameter is used,
                then it is best for it to retain the same value from one fetchmany() call to the next.
        """
        if size:
            return self.__cursor.fetchmany(size)
        else:
            return self.__cursor.fetchmany()

    def fetch_all_remaining_rows(self) -> List[tuple]:
        """
        Fetch all (remaining) rows of a query result, returning them as a list of tuples.
            An empty list is returned if there is no more record to fetch.
        A ProgrammingError is raised
            if the previous call to execute*() did not produce any result set or no call was issued yet.
        """
        return self.__cursor.fetchall()

    def scroll_next_n_rows(self, n: int):
        """
        Scroll the cursor in the result set to a new position according to mode.
        value is taken as offset to the current position in the result set.

        If the scroll operation would leave the result set,
            an IndexError from ProgrammingError is raised and the cursor position is not changed.

        The method can be used both for client-side cursors and server-side cursors.
            Server-side cursors can usually scroll backwards only if declared scrollable.
            Moving out-of-bound in a server-side cursor doesn’t result in an exception,
                if the backend doesn’t raise any
                (Postgres doesn’t tell us in a reliable way if we went out of bound).
        """
        try:
            self.__cursor.scroll(n, 'relative')
        except ProgrammingError as pe:
            raise IndexError from pe

    def scroll_to_target_row(self, index: int):
        """
        Scroll the cursor in the result set to a new position according to mode.
        value states an absolute target position.

        If the scroll operation would leave the result set,
            an IndexError from ProgrammingError is raised and the cursor position is not changed.

        The method can be used both for client-side cursors and server-side cursors.
            Server-side cursors can usually scroll backwards only if declared scrollable.
            Moving out-of-bound in a server-side cursor doesn’t result in an exception,
                if the backend doesn’t raise any
                (Postgres doesn’t tell us in a reliable way if we went out of bound).
        """
        try:
            self.__cursor.scroll(index, 'absolute')
        except ProgrammingError as pe:
            raise IndexError from pe

    def get_array_size_of_cursor(self) -> int:
        """
        read: This attribute specifies the number of rows to fetch at a time with fetchmany().
        It defaults to 1 meaning to fetch a single row at a time.
        """
        return self.__cursor.arraysize

    def set_array_size_of_cursor(self, x: int):
        """
        write: This attribute specifies the number of rows to fetch at a time with fetchmany().
        It defaults to 1 meaning to fetch a single row at a time.
        """
        self.__cursor.arraysize = x

    def get_iter_size_of_cursor(self) -> int:
        """
        Read: attribute specifying the number of rows to fetch from the backend
            at each network roundtrip during iteration on a named cursor.
        The default is 2000.
        """
        return self.__cursor.itersize

    def set_iter_size_of_cursor(self, x: int):
        """
        Write: attribute specifying the number of rows to fetch from the backend
            at each network roundtrip during iteration on a named cursor.
        The default is 2000.
        """
        self.__cursor.itersize = x

    def get_row_count(self) -> int:
        """
        This read-only attribute specifies the number of rows
            that the last execute*() produced (for DQL statements like SELECT)
            or affected (for DML statements like UPDATE or INSERT).
        The attribute is -1 in case no execute*() has been performed on the cursor
            or the row count of the last operation if it can’t be determined by the interface.
        Note
            The DB API 2.0 interface reserves to redefine the latter case to have the object return None
                instead of -1 in future versions of the specification.
        """
        return self.__cursor.rowcount

    def get_row_number(self) -> Optional[int]:
        """
        This read-only attribute provides the current 0-based index of the cursor in the result set
            or None if the index cannot be determined.
        The index can be seen as index of the cursor in a sequence (the result set).
            The next fetch operation will fetch the row indexed by rownumber in that sequence.
        """
        return self.__cursor.rownumber

    def get_last_inserted_row_id(self) -> Optional[int]:
        """
        This read-only attribute provides the OID of the last row inserted by the cursor.
            If the table wasn’t created with OID support or the last operation is not a single record insert,
                the attribute is set to None.
        Note PostgreSQL currently advices to not create OIDs on the tables
            and the default for CREATE TABLE is to not support them.
            The INSERT ... RETURNING syntax available from PostgreSQL 8.3 allows more flexibility.
        """
        return self.__cursor.lastrowid

    def get_query(self) -> Optional[bytes]:
        """
        Read-only attribute containing the body of the last query sent to the backend (including bound arguments)
            as bytes string.
            None if no query has been executed yet.
        """
        return self.__cursor.query

    def get_status_message(self):
        """
        Read-only attribute containing the message returned by the last command
        """
        return self.__cursor.statusmessage

    def __cast(self, oid, s):
        """
        Convert a value from the PostgreSQL string representation to a Python object.
        Use the most specific of the typecasters registered by register_type().
        """
        return self.__cursor.cast(oid, s)

    def get_tzinfo_factory(self):
        """
        The time zone factory used to handle data types such as TIMESTAMP WITH TIME ZONE.
            It should be a tzinfo object.
            Default is datetime.timezone.
        Changed in cursor version 2.9: previosly the default factory was psycopg2.tz.FixedOffsetTimezone.
        """
        return self.__cursor.tzinfo_factory

    # the following copy-series methods are not implemented now
    # copy_from(file, table, sep='\t', null='\\N', size=8192, columns=None)¶
    # copy_to(file, table, sep='\t', null='\\N', columns=None)¶
    # copy_expert(sql, file, size=8192)¶
