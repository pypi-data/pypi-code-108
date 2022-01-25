# SPDX-License-Identifier: Apache-2.0
# Copyright © 2021 Wrangle Ltdimport typing

import itertools
import typing
import attr

from wrgl import repository
from wrgl.commit import Table
from wrgl.diff import DiffResult, TableProfileDiff
from wrgl.coldiff import ColDiff


class RowIterator(object):
    """Iterates over rows with specified offsets of a table.

    Each row is returned as a list of strings.

    :var list[str] columns: column names
    :var list[str] primary_key: primary key
    """
    _repo: "repository.Repository"
    _tbl_sum: str
    _offsets: typing.List[int]
    _off: int
    _fetch_size: int

    columns: typing.List[str]
    primary_key: typing.List[str]

    def __init__(
            self,
            repo: "repository.Repository",
            tbl_sum: str,
            columns: typing.List[str],
            primary_key: typing.List[str],
            fetch_size: int = 100
    ) -> None:
        """
        :param Repository repo: the repo handle
        :param str tbl_sum: checksum of the table the rows belong to
        :param list[str] columns: column names
        :param list[str] primary_key: primary key
        :param int fetch_size: number of rows to fetch for each batch
        """
        self._repo = repo
        self._tbl_sum = tbl_sum
        self._offsets = []
        self._fetch_size = fetch_size
        self.columns = columns
        self.primary_key = primary_key

    def add_offset(self, offset: int) -> None:
        """Add a single row offset

        :param int offset: row offset
        """
        self._offsets.append(offset)

    def __len__(self):
        return len(self._offsets)

    def __iter__(self):
        self._off = 0
        self._batch = (i for i in [])
        return self

    def __next__(self) -> typing.List[str]:
        try:
            return next(self._batch)
        except StopIteration:
            if self._off >= len(self):
                raise StopIteration()
            self._batch = self._repo.get_table_rows(
                self._tbl_sum,
                self._offsets[self._off:self._off + self._fetch_size]
            )
            self._off += self._fetch_size
            return next(self._batch)


class ModifiedRowIterator(object):
    """Iterates over row pairs with specifies offsets from a pair of tables

    Each row is returned as a list of tuple of two values: `(newer_value, older_value)`.
    If either cell is missing (because the column is missing in one of the tables) then
    one of the values is None.

    :var list[str] columns: column names
    :var list[str] primary_key: primary key
    """
    _repo: "repository.Repository"
    _tbl_sum1: str
    _tbl_sum2: str
    _cd: ColDiff
    _fetch_size: int
    _offsets: typing.List[typing.Tuple[int, int]]
    _off: int

    columns: typing.List[str]
    primary_key: typing.List[str]

    def __init__(
            self,
            repo: "repository.Repository",
            tbl_sum1: str,
            tbl_sum2: str,
            cd: ColDiff,
            columns: typing.List[str],
            primary_key: typing.List[str],
            fetch_size: int = 100
    ) -> None:
        """
        :param Repository repo: the repo handle
        :param str tbl_sum1: checksum of the newer table
        :param str tbl_sum2: checksum of the older table
        :param ColDiff cd: column differences
        :param list[str] columns: column names
        :param list[str] primary_key: primary key
        :param int fetch_size: number of rows to fetch for each batch
        """
        self._repo = repo
        self._tbl_sum1 = tbl_sum1
        self._tbl_sum2 = tbl_sum2
        self._cd = cd
        self._fetch_size = fetch_size
        self._offsets = []
        self._off = 0
        self.columns = columns
        self.primary_key = primary_key

    def add_offset(self, offset1: int, offset2: int) -> None:
        """Add a single row offset

        :param int offset1: row offset for the newer table
        :param int offset2: row offset for the older table
        """
        self._offsets.append((offset1, offset2))

    def __len__(self):
        return len(self._offsets)

    def __iter__(self):
        self._off = 0
        self._batch = (i for i in [])
        return self

    def __next__(self) -> typing.List[str]:
        try:
            row1, row2 = next(self._batch)
        except StopIteration:
            if self._off >= len(self):
                raise StopIteration()
            offsets = self._offsets[self._off:self._off + self._fetch_size]
            self._batch = itertools.zip_longest(
                self._repo.get_table_rows(
                    self._tbl_sum1, [i for i, _ in offsets]
                ),
                self._repo.get_table_rows(
                    self._tbl_sum2, [i for _, i in offsets]
                )
            )
            self._off += self._fetch_size
            row1, row2 = next(self._batch)
        return self._cd.combine_rows(0, row1, row2)


@attr.s(auto_attribs=True)
class ColumnChanges(object):
    """Represents changes in column names.

    :var list[str] new_values: new columns
    :var list[str] old_values: old columns
    :var set[str] unchanged: columns that are present in both versions
    :var set[str] added: columns that appear in newer version but not in older version
    :var set[str] removed: columns that appear in older version but not in newer version
    """
    new_values: typing.List[str]
    old_values: typing.List[str]
    unchanged: typing.Set[str]
    added: typing.Set[str]
    removed: typing.Set[str]

    @classmethod
    def from_new_old_columns(cls, new_cols: typing.List[str], old_cols: typing.List[str]) -> "ColumnChanges":
        """Creates a new instance by comparing two column lists

        :param list[str] new_cols: newer columns
        :param list[str] old_cols: older columns

        :rtype: ColumnChanges
        """
        new_values = new_cols
        old_values = old_cols
        old_set = set(old_cols)
        new_set = set(new_cols)
        unchanged = old_set & new_set
        added = new_set - old_set
        removed = old_set - new_set
        return cls(new_values, old_values, unchanged, added, removed)


class DiffReader(object):
    """Interprets the changes between two commits.

    :var ColumnChanges column_changes: column changes
    :var ColumnChanges pk_changes: primary key changes
    :var RowIterator added_rows: iterator for added rows
    :var RowIterator removed_rows: iterator for removed rows
    :var ModifiedRowIterator modified_rows: iterator for modified rows
    :var TableProfileDiff data_profile: changes in data profile
    """

    column_changes: ColumnChanges
    pk_changes: ColumnChanges
    added_rows: RowIterator or None = None
    removed_rows: RowIterator or None = None
    modified_rows: ModifiedRowIterator or None = None
    data_profile: TableProfileDiff or None = None

    def __init__(self, repo: "repository.Repository", com_sum1: str, com_sum2: str, fetch_size: int = 100) -> None:
        """
        :param Repository repo: the repo handle
        :param str com_sum1: checksum of the first (newer) commit
        :param str com_sum2: checksum of the second (older) commit
        """
        dr = repo.diff(com_sum1, com_sum2)
        self.data_profile = dr.data_profile
        old_tbl = Table(columns=dr.old_columns, pk=dr.old_pk)
        new_tbl = Table(columns=dr.columns, pk=dr.pk)
        cd = ColDiff(old_tbl, new_tbl)
        self.column_changes = ColumnChanges.from_new_old_columns(
            dr.columns, dr.old_columns
        )
        self.pk_changes = ColumnChanges.from_new_old_columns(
            new_tbl.primary_key, old_tbl.primary_key
        )
        if dr.row_diff is not None and old_tbl.primary_key == new_tbl.primary_key:
            self.added_rows = RowIterator(
                repo=repo,
                tbl_sum=dr.table_sum,
                columns=new_tbl.columns,
                primary_key=new_tbl.primary_key,
                fetch_size=fetch_size
            )
            self.removed_rows = RowIterator(
                repo=repo,
                tbl_sum=dr.old_table_sum,
                columns=old_tbl.columns,
                primary_key=old_tbl.primary_key,
                fetch_size=fetch_size
            )
            self.modified_rows = ModifiedRowIterator(
                repo=repo,
                tbl_sum1=dr.table_sum,
                tbl_sum2=dr.old_table_sum,
                cd=cd,
                columns=[
                    col.name for col in cd.columns
                ],
                primary_key=new_tbl.primary_key,
                fetch_size=fetch_size
            )
            for rd in dr.row_diff:
                if rd.off1 is None:
                    self.removed_rows.add_offset(rd.off2)
                elif rd.off2 is None:
                    self.added_rows.add_offset(rd.off1)
                else:
                    self.modified_rows.add_offset(rd.off1, rd.off2)
