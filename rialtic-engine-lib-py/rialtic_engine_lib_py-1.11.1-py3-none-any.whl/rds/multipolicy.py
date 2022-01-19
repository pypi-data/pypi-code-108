import os
import csv

from enginelib.errors import Error
from enginelib.rds.client import db_client, db_name


def _local_get_initial_subset_of_rows(procedure_code: str, max_rows: int = 0) -> list:
    """ Reads a csv file which has the name given in the environment variable
    MASTER_TABLE_FILENAME, and returns the records in which column {cpt_procedurecode}
    has the value given in the `procedure_code` parameter.

    The csv should contain the column names (header) in the first row, and the data should
    start already in the second row. All columns in the file will be considered, so make
    sure they have valid names in the header.

    Args:
        procedure_code - the value to be used to filter the rows in the master table.

    Returns:
        A list of rows, each row being a dictionary containing a column_name: value
            pair for each column in the master table. The values are all strings.

            The zero-based index of each row will be added for debugging purposes
            in each dictionary at key `row_number`. The header (which would have
            its `row_number` equal to 0) is not returned in the list. The first
            data row has its `row_number` equal to 1 and so on.
    """

    with open(os.environ['MASTER_TABLE_FILENAME']) as f:
        rows = csv.reader(f)
        header = next(rows)

        table = list()
        for j, row in enumerate(rows):
            entry = {header[i]: field for i, field in enumerate(row) if header[i]}
            if entry['cpt_procedurecode'] == procedure_code:
                entry['row_number'] = j + 1
                table.append(entry)

        return table[:max_rows] if max_rows else table


def _remote_get_initial_subset_of_rows(procedure_code: str = '', max_rows: int = 0, all_to_str: bool = True) -> list:
    """For MPEs, this function does the initial filtering of rows from table `multipolicy`
    (the MASTER table), returning every row for which the given procedure code appears
    in column {cpt_procedurecode}.

    Set the environment variable `MASTER_TABLE_NAME` to change the default table name
    for the master table.

    Args:
        procedure_code - the value to be used to filter the rows in the master table.
        max_rows - the maximum number of rows to be returned from the DB.
        all_to_str - whether we should convert all values in the rows that are
            returned to str. (To mimic what happens when we read from a local CSV.)

    Returns:
        A list of rows, each row being a dictionary containing a column_name: value
            pair for each column in the master table.
    """

    clause = f'''WHERE "cpt_procedurecode" = '{procedure_code}' ''' if procedure_code else ''
    limit = f'LIMIT {max_rows}' if max_rows > 0 else ''

    # If there is a version of the master table on platform that is meant to test your engine,
    #     then, please, set the environment variable below (in your code) to the correct table
    #     name that should be used.
    table_name = os.getenv('MASTER_TABLE_NAME', 'multipolicy')

    # noinspection SqlResolve
    query = f'''
    SELECT * 
        FROM {db_name}.{table_name}
        {clause}
        {limit};
    '''

    ref_data, err = db_client.GetReferenceData("multi_policy_prefilter", query)
    if err:
        raise Error(f'Not able to access multipolicy reference data set: {err}')
    else:
        ref_data = ref_data or list()
        if all_to_str:
            return [
                {key: str(value) for key, value in row.items()}
                for row in ref_data
            ]

        return ref_data


def rows_for_cpt(procedure_code: str, max_rows: int = 0, all_to_str: bool = True) -> list:
    """Selects the rows in the master table that have the given procedure code
    in column {cpt_procedurecode}.

    Args:
        procedure_code - the value to be used to filter the rows in the master table.
        max_rows - the maximum number of rows to be returned from the DB.
        all_to_str - whether we should convert all values in the rows that are
            returned to str. (To mimic what happens when we read from a local CSV.)

    Returns:
        A list of rows, each row being a dictionary containing a column_name: value
            pair for each column in the master table.

    Notes:
        If running with a local copy of the master table, please set environment
        variables:

            MASTER_TABLE_ENV = 'local'
            MASTER_TABLE_FILENAME = <filename of the csv, local master table>

        To run with a master table on platform that is a "fake" master table, please
        set the environment variable MASTER_TABLE_NAME to the right table name. If
        this variable is not set, the name of the table used on platform will be
        `multipolicy`.
    """
    if os.getenv('MASTER_TABLE_ENV') == 'local':
        return _local_get_initial_subset_of_rows(procedure_code, max_rows)
    return _remote_get_initial_subset_of_rows(procedure_code, max_rows, all_to_str)
