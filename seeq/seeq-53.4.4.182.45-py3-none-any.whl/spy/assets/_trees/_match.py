import fnmatch
import re

import numpy as np
import pandas as pd

from seeq.spy import _common
from seeq.spy._errors import *
from seeq.spy.assets._trees import _path


def is_column_value_query(s):
    if not isinstance(s, str):
        return False
    if re.search(r'{{.*}.*}', s):
        return True
    return False


def fill_column_values(row, query: str = None, query_column=None):
    """
    Fills a column values query with actual column values from a row in a dataframe. Returns the output string
    """
    if pd.isnull(query):
        if query_column not in row:
            return np.nan
        query = row[query_column]
        if pd.isnull(query):
            return np.nan

    def _fill_column_value(col_val_query_match: re.Match):
        col_val_query = col_val_query_match[1]
        col, extract_pattern = re.fullmatch(r'{(.*?)}(.*)', col_val_query).groups(default='')
        if not _common.present(row, col):
            raise SPyValueError('Not a match')
        value = str(row[col])
        if extract_pattern == '':
            return value

        # Match against a glob pattern first, then try regex
        for pattern in (glob_with_capture_groups_to_regex(extract_pattern), extract_pattern):
            try:
                extraction = re.fullmatch(pattern, value)
                if extraction:
                    if len(extraction.groups()) != 0:
                        return extraction[1]
                    else:
                        return extraction[0]
            except re.error:
                # There may be a compilation error if the input wasn't intended to be interpreted as regex
                continue
        raise SPyValueError('Not a match')

    try:
        return re.sub(r'{({.*?}.*?)}', _fill_column_value, query)
    except SPyValueError:
        return np.nan


def glob_with_capture_groups_to_regex(glob):
    """
    Converts a glob to a regex, but does not escape parentheses, so that the glob can be written with capture groups
    """
    return re.sub(r'\\([()])', r'\1', fnmatch.translate(glob))


def is_node_match(pattern, node):
    """
    General pattern matcher for tree methods that match on tree items. Input options for pattern:

    None
        Matches the root

    np.nan
        Matches nothing. This is used when the user inserts via a 'Parent' column in the children
        dataframe that is only specified for some children.

    int
        Matches all items of the specified depth.

    GUID
        Matches items that have ID or Referenced ID equal to pattern

    Path/Name match
        If just a name is given, matching will be attempted when interpreting the string as
        1) a case-insensitive exact query
        2) a globbing pattern
        3) a regex pattern
        If path markers '>>' are included, the pieces of the path will be split and matched like above
        to find items whose paths end with the path query given.

    list
        Iterates over all elements and calls this same function. If any match is found, return True

    pd.Series
        Checks if this is a DataFrame row containing 'ID' or 'Name' in its index. If so, tries to match
        on ID and then Path/Name. If not, then treated like an iterable in the same way as a list

    pd.DataFrame
        Checks if any of the rows are a match
    """
    if pattern is None:
        return node['Depth'] == 1
    if pd.api.types.is_scalar(pattern) and pd.isnull(pattern):
        # This case handles when the user only gives the 'Parent' column for some children, or gives a parent
        #  string that uses column values that aren't valid for some rows.
        return False
    if isinstance(pattern, pd.DataFrame):
        return pattern.apply(is_node_match, axis=1, node=node).any()
    if isinstance(pattern, list):
        if len(pattern) == 0:
            return False
        else:
            # Pass on to next isinstance() check
            pattern = pd.Series(pattern)
    if isinstance(pattern, pd.Series):
        # First interpret the Series as a dataframe row being matched up against the tree dataframe row
        if _common.present(pattern, 'ID'):
            return pattern['ID'] == _common.get(node, 'ID') or pattern['ID'] == _common.get(node, 'Referenced ID')
        if _common.present(pattern, 'Name'):
            if _common.present(pattern, 'Path') and _path.determine_path(pattern).casefold() != node['Path'].casefold():
                return False
            return pattern['Name'].casefold() == node['Name'].casefold()
        if len(pattern.index.intersection(node.index)) != 0:
            return False

        # Now interpret the Series as a collection of patterns to check against
        return pattern.apply(is_node_match, node=node).any()
    if isinstance(pattern, str):
        if _common.is_guid(pattern):
            if isinstance(node['ID'], str) and pattern.upper() == node['ID'].upper():
                return True
            if isinstance(node['Referenced ID'], str) and pattern.upper() == node['Referenced ID'].upper():
                return True
        else:
            regex_list = node_match_string_to_regex_list(pattern)
            return is_node_match_via_regex_list(regex_list, node)
    if isinstance(pattern, int):
        return node['Depth'] == pattern
    return False


def node_match_string_to_regex_list(pattern):
    """
    :param pattern: String name match (case-insensitive equality, globbing, regex, column values)
                    or string path match (full or partial; case-insensitive equality, globbing, or regex)
    :return: A list of regular expressions that match the last n names in the full path of a node.
    """
    patterns = _common.path_string_to_list(pattern)
    return [exact_or_glob_or_regex(p) for p in patterns]


def exact_or_glob_or_regex(pat):
    try:
        re.compile(pat)
        return re.compile('(?i)' + '(' + ')|('.join([re.escape(pat), fnmatch.translate(pat), pat]) + ')')
    except re.error:
        return re.compile('(?i)' + '(' + ')|('.join([re.escape(pat), fnmatch.translate(pat)]) + ')')


def is_node_match_via_regex_list(pattern_list, node):
    path_list = _common.path_string_to_list(_path.get_full_path(node))
    offset = len(path_list) - len(pattern_list)
    if offset < 0:
        return False
    for i in range(len(pattern_list)):
        if not pattern_list[i].fullmatch(path_list[offset + i]):
            return False
    return True
