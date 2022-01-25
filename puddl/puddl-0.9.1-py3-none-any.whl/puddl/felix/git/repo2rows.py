#!/usr/bin/env python
import csv
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
from pydantic import BaseModel

from puddl.felix.git import CommitParseError, log, EmptyLogError, GitLogError

here = Path(__file__).parent


class Record(BaseModel):
    repo_path: str
    hash: str
    dt: datetime
    file_path: str


class Commit:
    def __init__(self, txt: str):
        self._raw = txt
        self.lines = self._raw.strip().split('\n')
        self.header = self.lines[0]
        try:
            h, d, e, s = self.header.split(' ', 3)
        except ValueError:
            raise CommitParseError(f'could not parse header from "{self._raw}"')
        self.hash = h
        self.dt = datetime.fromisoformat(d)
        self.email = e
        self.subject = s
        self.paths = self.lines[1:]

    def __str__(self):
        return f'{self.header} ({len(self.paths)})'


class Repo:
    def __init__(self, path: Path, author=None, since_commit=None):
        self.path = path
        self.author = author
        self.since_commit = since_commit
        self._log = self.get_log()
        if self._log == '':
            raise EmptyLogError(f'{self} is empty for author={self.author}')

    def __str__(self):
        return f'{self.path}'

    def get_log(self):
        cmd = ['git', 'log', '--reverse', "--pretty=format:%H %aI %cE %s", "--stat", "--name-only"]
        if self.author is not None:
            cmd.extend(["--author", self.author])
        if self.since_commit is not None:
            cmd.append(self.since_commit)
        try:
            return subprocess.check_output(cmd, cwd=self.path, encoding='utf-8', stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            raise GitLogError(f'{self}: {e.stderr}')

    def commits(self) -> [Commit]:
        # records are separated by empty lines
        _records = self._log.strip().split('\n\n')
        for rec in _records:
            if rec is None:
                continue
            yield Commit(rec)

    def __iter__(self):
        try:
            commits = self.commits()
            for commit in commits:
                try:
                    for file_path in commit.paths:
                        yield Record(
                            repo_path=str(self.path),
                            hash=commit.hash,
                            dt=commit.dt,
                            file_path=file_path,
                        )
                except CommitParseError as e:
                    log.warning(f'{self}: {e}')
        except EmptyLogError as e:
            log.warning(e)

    def as_df(self):
        return pd.DataFrame(record.dict() for record in self)

    def as_csv(self, fd):
        fieldnames = list(Record.schema()["properties"].keys())
        writer = csv.DictWriter(fd, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for record in self:
            writer.writerow(record.dict())


if __name__ == '__main__':
    Repo(Path('.')).as_csv(sys.stdout)
