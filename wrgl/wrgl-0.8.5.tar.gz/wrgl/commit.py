# SPDX-License-Identifier: Apache-2.0
# Copyright © 2021 Wrangle Ltd

import datetime
import typing

import attr

from wrgl.isoformat import fromisoformat
from wrgl.serialize import field_transformer


@attr.s(auto_attribs=True, field_transformer=field_transformer(globals()))
class CommitResult(object):
    """Payload of a successful commit

    :ivar str sum: 16-bit checksum of commit presented as hex string
    :ivar str table: 16-bit checksum of underlying table presented as hex string
    """
    sum: str
    table: str


@attr.s(auto_attribs=True, field_transformer=field_transformer(globals()))
class Table(object):
    """A table represents the underlying CSV of a :class:`Commit`

    :ivar str sum: 16-bit checksum of table presented as hex string
    :ivar list[str] columns: list of column names
    :ivar list[int] pk: indices of primary key columns
    :ivar int rows_count: number of rows
    """
    sum: str
    columns: typing.List[str]
    pk: typing.List[int]
    rows_count: int

    @property
    def primary_key(self) -> typing.List[str]:
        """Returns primary-key columns of the first commit

        :rtype: list[str]
        """
        if self.pk is None:
            return []
        return [self.columns[idx] for idx in self.pk]


@attr.s(auto_attribs=True, field_transformer=field_transformer(globals()))
class Commit(object):
    """A commit represents an immutable snapshot of a CSV

    :ivar str sum: 16-bit checksum of commit presented as hex string
    :ivar str author_name: name of commit author
    :ivar str author_email: email of commit author
    :ivar str message: commit message
    :ivar Table table: the underlying table
    :ivar datetime.datetime time: commit time
    :ivar list[str] parents: checksums of parent commits
    :ivar dict[str, Commit] parent_commits: mapping between parent checksums and commits.
        Only present if the commit was returned by :func:`Repository.get_commit_tree`
    """
    sum: str
    author_name: str
    author_email: str
    message: str
    table: Table
    time: datetime.datetime = attr.ib(
        converter=attr.converters.optional(fromisoformat)
    )
    parents: typing.List[str]
    parent_commits: "typing.Dict[str, Commit]"


@attr.s(auto_attribs=True, field_transformer=field_transformer(globals()))
class CommitTree(object):
    """Payload returned by :func:`Repository.get_commit_tree`

    :ivar str sum: 16-bit checksum of root commit presented as hex string
    :ivar Commit root: the root commit
    """
    sum: str
    root: Commit
