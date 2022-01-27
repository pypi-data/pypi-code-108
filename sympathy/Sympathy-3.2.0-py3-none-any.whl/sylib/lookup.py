# This file is part of Sympathy for Data.
# Copyright (c) 2013, Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
import numpy as np

from sympathy.api.exceptions import SyDataError, SyConfigurationError


def create_datacolumn(lookup_matrix, lookupee_matrix, log_no,
                      require_perfect_match=True):
    """Return the indices for the matching row using NaN if no matching row
    could be found. Raises ValueError if several matches were found for the
    same row.
    """
    req_count = len(lookup_matrix)
    unique_ids = np.arange(0, req_count)
    req_log_no = log_no[:req_count]
    data_log_no = log_no[req_count:]

    datacolumn = []
    for group_id, row in zip(data_log_no, lookupee_matrix):
        unique_match = unique_ids[req_log_no == group_id]
        if unique_match.size == 0:
            datacolumn.append(np.nan)
        elif unique_match.size > 1 and require_perfect_match:
            raise SyDataError(("Row {0} could be matched to more than one "
                               "row in the lookup table.").format(row))
        else:
            datacolumn.append(unique_match[0])
    return np.array(datacolumn)


def group_by_equality(lookup_by):
    """
    Return a numpy array with the indices of the first occurences of each
    unique row in lookup_by.

    Example:
    >>> A = np.array([['spam', 'eggs'],
    ...               ['spam', 'spam'],
    ...               ['spam', 'eggs']])
    >>> group_by_equality(A)
    [0 1 0]
    """
    order = np.lexsort(lookup_by.T)
    indices = np.zeros(len(lookup_by), int)

    group_id = 0
    prev_row = lookup_by[order[0]]
    for i, row in enumerate(lookup_by[order]):
        if np.any(row != prev_row):
            group_id += 1
        indices[order[i]] = group_id
        prev_row = row

    return indices


def group_by_event(lookup_by, lookup_matrix_column_length,
                   require_perfect_match=True):
    """
    Find the latest event before each event in second part of lookup_by.

    The matrix lookup_by consits of two parts:
    lookup[:lookup_matrix_column_length] is the lookup_matrix and
    lookup[lookup_matrix_column_length:] is the lookupee_matrix.

    For each row in lookupee_matrix find the last event in lookup_matrix for
    which all columns except the first match the data in lookupee_matrix and
    which occurs before the event in the current row.

    Event order is determined using the first column. The first column can for
    example be the year, date, or time when something happend. But can in
    theory also be any other sortable data.

    Example:
    >>> a = np.array([['1997', 'eggs'],
    ...               ['1999', 'spam'],
    ...               ['2000', 'eggs'],
    ...               ['2011', 'spam']])
    >>> b = np.array([['2001', 'spam'],
    ...               ['2013', 'spam'],
    ...               ['2020', 'spam'],
    ...               ['2000', 'eggs'],
    ...               ['2013', 'eggs']])
    >>> res = group_by_event(np.vstack(a, b), len(a))
    >>> res[:4]
    [0 1 2 3]
    >>> res[4:]
    [1 3 3 0 0 2]
    """
    # Define a sort order, grouping by columns [1:] and sorting in each group
    # by column [0] (the event column):
    order = np.lexsort(lookup_by.T)

    # Result array:
    indices = np.zeros(len(lookup_by), float)

    group_id = 0
    group_row = None
    for i, row in enumerate(lookup_by[order]):
        # Increase group_id when a new event from the lookup table is found
        if order[i] < lookup_matrix_column_length:
            group_id += 1
            group_row = row
            indices[order[i]] = group_id

        # We have reached the first row of a new group, but the row is not in
        # the lookup table. This means that the row comes before any matching
        # events in the lookup table and so doesn't match anything.
        # (First column is the event column and we don't want to compare those)
        elif group_row is None or np.any(row[1:] != group_row[1:]):

            # The first row with any unique set of params should always come
            # from the lookup table
            if require_perfect_match:
                raise SyDataError(
                    ("The row {0} has no matching event in the lookup "
                     "table.").format(row))
            indices[order[i]] = np.nan

        else:
            indices[order[i]] = group_id
    return indices


def create_lookup_matrix(in_table, columns, event_col):
    """
    Extracts a 2-dimensional numpy array with the columns that should be
    used in the matching.
    """
    lookup_list = []

    # Add the event column as the first column in the matrix
    if event_col != -1:
        column = in_table.get_column_to_array(columns[event_col])
        if np.issubdtype(column.dtype, np.dtype('datetime64')):
            column = column.astype('unicode')
        lookup_list.append(column)

    # Add all other columns
    for i, column_name in enumerate(columns):
        if i != event_col:
            column = in_table.get_column_to_array(column_name)
            if np.issubdtype(column.dtype, np.dtype('datetime64')):
                column = column.astype('unicode')
            lookup_list.append(column)

    if not lookup_list:
        raise SyConfigurationError(
            "Please choose at least one column pair to be used for matching.")
    return np.column_stack(lookup_list)


def apply_index_datacolumn_and_write_to_file(
        parameters, template_file, lookupee_file, out_file):

    # Extract lookup data from parameters
    perfect_match = parameters['perfect_match'].value
    nomasks = parameters['nomasks'].value
    event_col = parameters['event_column'].value

    # Check if we will be able to do any lookups at all
    skip_lookup = False
    for column_name in parameters['lookupee_columns'].list:
        if column_name not in lookupee_file.column_names():
            if perfect_match:
                raise SyDataError(
                    "Column {} is missing in the control table "
                    "(lower port).".format(column_name))
            else:
                skip_lookup = True
    for column_name in parameters['template_columns'].list:
        if column_name not in template_file.column_names():
            if perfect_match:
                raise SyDataError(
                    "Column {} is missing in the lookup table "
                    "(upper port).".format(column_name))
            else:
                skip_lookup = True
    if not template_file.number_of_rows() and not perfect_match:
        skip_lookup = True
    if skip_lookup:
        do_empty_lookup(
            template_file, lookupee_file.number_of_rows(), out_file, nomasks)
        return

    lookup_matrix = create_lookup_matrix(
        template_file, parameters['template_columns'].list, event_col)
    lookupee_matrix = create_lookup_matrix(
        lookupee_file, parameters['lookupee_columns'].list, event_col)

    # Check that data is sane
    if lookup_matrix.shape[1] != lookupee_matrix.shape[1]:
        raise AssertionError(
            "Different array shape ({0} != {1}).".format(
                lookup_matrix.shape[1], lookupee_matrix.shape[1]))
    if lookup_matrix.shape[1] == 0:
        raise SyDataError("No matching pairs defined.")

    # Do the lookup (using different strategies depending on whether there is
    # an event column or not)
    lookup_by = np.vstack((lookup_matrix, lookupee_matrix))
    if event_col == -1:
        log_no = group_by_equality(lookup_by)
    else:
        log_no = group_by_event(
            lookup_by, lookup_matrix.shape[0],
            require_perfect_match=perfect_match)

    datacolumn = create_datacolumn(
        lookup_matrix, lookupee_matrix, log_no,
        require_perfect_match=perfect_match)

    # Check if there was any row which couldn't be matched to anything
    nan_mask = np.isnan(datacolumn)
    nan_indices = np.flatnonzero(nan_mask)
    safe_datacolumn = datacolumn
    safe_datacolumn[nan_mask] = np.zeros(len(nan_indices), dtype=int)
    safe_datacolumn = safe_datacolumn.astype(int)
    if perfect_match:
        if len(nan_indices) > 0:
            row = lookupee_matrix[nan_indices[0]]
            raise SyDataError(
                "Row {0} couldn't be matched to any row in the lookup table."
                "".format(row))

        unique_row_count = len({tuple(row) for row in lookup_matrix})
        row_count = len(lookup_matrix)
        if unique_row_count != row_count and perfect_match:
            raise SyDataError("Nonunique rows in lookup table (upper port).")

    # Write to output file
    for column_name in template_file.column_names():
        in_column = template_file.get_column_to_array(column_name)
        if in_column.size:
            out_column = in_column[safe_datacolumn]
        else:
            out_column = in_column
        if len(nan_indices):
            if nomasks:
                out_column[nan_indices] = empty_column(
                    len(nan_indices), dtype=out_column.dtype, nomasks=nomasks)
            else:
                out_column = np.ma.MaskedArray(
                    out_column, mask=nan_mask, dtype=out_column.dtype)
        out_file.set_column_from_array(column_name, out_column)


def empty_column(length, dtype, nomasks=False):
    if nomasks:
        if dtype.kind in ['S', 'U']:
            dtype = dtype.kind + '1'
        else:
            dtype = dtype
        return np.zeros(length, dtype=dtype)
    else:
        return np.ma.masked_all(length, dtype=dtype)


def do_empty_lookup(template_file, row_count, out_file, nomasks):
    for column_name in template_file.column_names():
        out_column = empty_column(
            row_count, template_file.column_type(column_name), nomasks)
        out_file.set_column_from_array(column_name, out_column)
