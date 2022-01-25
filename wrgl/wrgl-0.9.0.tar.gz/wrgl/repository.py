# SPDX-License-Identifier: Apache-2.0
# Copyright © 2021 Wrangle Ltd

from typing import Iterator, List
import tempfile
import gzip
import shutil
import typing
import requests
import csv
import io
from requests_toolbelt.multipart.encoder import MultipartEncoder

from wrgl import diffreader
from wrgl.commit import Commit, CommitResult, Table, CommitTree
from wrgl.diff import DiffResult
from wrgl.serialize import json_dumps, json_loads
from wrgl.config import Config


class Repository(object):
    """Represents the HTTP API that wraps a hosted Wrgl repository
    """

    def __init__(self, endpoint: str, id_token: str = None) -> None:
        """
        :param str endpoint: the endpoint of the HTTP API
        :param str id_token: optional, the access token for this API.
            If it is a valid token then you don't need to run :func:`Repository.authenticate`.
        """
        self.endpoint = endpoint.rstrip("/")
        self._is_hub_repo = self.endpoint.startswith("https://hub.wrgl.co/")
        self._id_token = id_token

    def authenticate(self, email: str, password: str) -> str:
        """Authenticates and returns the access token.

        If successful, access token will be saved for future usage.

        :param str email: user's email
        :param str password: user's password

        :rtype: str
        """
        if self._is_hub_repo:
            endpoint = "https://hub.wrgl.co/api/authenticate/"
        else:
            endpoint = self.endpoint + "/authenticate/"
        r = requests.post(endpoint, json={
            'email': email,
            'password': password
        })
        r.raise_for_status()
        self._id_token = r.json()['idToken']
        return self._id_token

    def _headers(self, extra_headers=dict()):
        headers = list(extra_headers.items())
        if self._id_token is not None:
            headers.append(('Authorization', 'Bearer %s' % self._id_token))
        return dict(headers)

    def _get(self, path, params=None):
        if params is not None:
            params = {k: v for k, v in params.items() if v}
        r = requests.get(
            self.endpoint+path, params=params, headers=self._headers(),
        )
        r.raise_for_status()
        return r

    def _put_json(self, path, obj):
        r = requests.put(
            self.endpoint+path,
            data=json_dumps(obj),
            headers=self._headers({
                'Content-Type': 'application/json'
            }),
        )
        r.raise_for_status()
        return r

    def _post_json(self, path, obj):
        r = requests.post(
            self.endpoint+path,
            data=json_dumps(obj),
            headers=self._headers({
                'Content-Type': 'application/json'
            }),
        )
        r.raise_for_status()
        return r

    def get_config(self) -> Config:
        """Get configurations

        :rtype: Config
        """
        r = self._get("/config/")
        return json_loads(r.content, Config)

    def put_config(self, config: Config) -> None:
        """Updates configurations

        :param Config config: the entire configurations
        """
        if not isinstance(config, Config):
            raise TypeError('config argument must be instance of %s' % Config)
        self._put_json("/config/", config)

    def get_refs(self) -> dict:
        """Get references as a mapping of reference name and commit checksum

        :rtype: dict
        """
        r = self._get("/refs/")
        obj = r.json()
        return obj["refs"]

    def get_branch(self, branch: str) -> Commit:
        """Get the head commit of a branch

        :param str branch: the name of the branch

        :rtype: Commit
        """
        r = self._get("/refs/heads/%s/" % branch)
        return json_loads(r.content, Commit)

    def commit(self, branch: str, message: str, file: typing.BinaryIO, primary_key: typing.List[str]) -> CommitResult:
        """Creates a new commit

        :param str branch: name of the branch to commit under
        :param str message: commit message
        :param typing.BinaryIO file: the CSV file to commit
        :param list[str] primary_key: list of column names that make up the primary key

        :rtype: CommitResult
        """
        with tempfile.TemporaryFile() as fp:
            with gzip.open(fp, 'w') as gzf:
                shutil.copyfileobj(file, gzf)
            fp.seek(0)
            m = MultipartEncoder(
                fields={
                    'branch': branch,
                    'message': message,
                    'primaryKey': ','.join(primary_key),
                    'file': ('data.csv.gz', fp, 'text/csv')
                }
            )
            r = requests.post(
                self.endpoint+"/commits/",
                data=m,
                headers=self._headers({'Content-Type': m.content_type}),
            )
        r.raise_for_status()
        return json_loads(r.content, CommitResult)

    def get_commit_tree(self, head: str, max_depth: int) -> CommitTree:
        """Gets commit tree

        :param str head: name of the root commit, could either be reference name or commit checksum.
        :param int max_depth: maximum depth of commit tree to fetch

        :rtype: CommitTree
        """
        r = self._get(
            "/commits/", params={'head': head, 'maxDepth': max_depth}
        )
        return json_loads(r.content, CommitTree)

    def get_commit(self, commit_sum: str) -> Commit:
        """Get commit with the given checksum

        :param str commit_sum: commit checksum

        :rtype: Commit
        """
        r = self._get("/commits/%s/" % commit_sum)
        return json_loads(r.content, Commit)

    def get_table(self, table_sum: str) -> Table:
        """Get table with the given checksum

        :param str table_sum: table checksum

        :rtype: Table
        """
        r = self._get("/tables/%s/" % table_sum)
        return json_loads(r.content, Table)

    def get_blocks(self, commit: str, start: int = None, end: int = None, with_column_names: bool = True) -> Iterator[List[str]]:
        """Fetchs blocks as concatenated rows. Each row as a list of strings.

        Calling this with default `start`, `end`, and `with_column_names` will return the entire table.

        :param str commit: either commit checksum or reference e.g. "heads/main"
        :param int start: index of the first block to fetch. Defaults to 0.
        :param int end: index of the last block to fetch. If not set, fetch til the end.
        :param bool with_column_names: prepend column names to the resulting CSV, which in effect producing a CSV with header.

        :rtype: typing.Iterator[list[str]]
        """
        r = self._get(
            "/blocks/",
            params={
                'head': commit,
                'start': start,
                'end': end,
                'columns': 'true' if with_column_names else 'false'
            }
        )
        for row in csv.reader(io.StringIO(r.text), dialect='unix'):
            yield row

    def get_table_blocks(self, table_sum: str, start: int = None, end: int = None, with_column_names: bool = True) -> Iterator[List[str]]:
        """Fetchs blocks with table checksum.

        Calling this with default `start`, `end`, and `with_column_names` will return the entire table.

        :param str table_sum: table checksum
        :param int start: index of the first block to fetch. Defaults to 0.
        :param int end: index of the last block to fetch. If not set, fetch til the end.
        :param bool with_column_names: prepend column names to the resulting CSV, which in effect producing a CSV with header.

        :rtype: typing.Iterator[list[str]]
        """
        r = self._get(
            "/tables/%s/blocks/" % table_sum,
            params={
                'start': start,
                'end': end,
                'columns': 'true' if with_column_names else 'false'
            }
        )
        for row in csv.reader(io.StringIO(r.text), dialect='unix'):
            yield row

    def get_rows(self, commit: str, offsets: List[int]) -> Iterator[List[str]]:
        """Get rows at certain offsets. Each row will be returned as a list of strings.

        This is usually used in tandem with row offsets from :class:`DiffResult` to fetch changed rows.

        :param str commit: either commit checksum or reference e.g. "heads/main"
        :param list[int] offsets: the offsets of the rows to fetch

        :rtype: typing.Iterator[list[str]]
        """
        r = self._get(
            "/rows/",
            params={
                'head': commit,
                'offsets': ','.join([str(v) for v in offsets])
            }
        )
        for row in csv.reader(io.StringIO(r.text), dialect='unix'):
            yield row

    def get_table_rows(self, table_sum: str, offsets: List[int]) -> Iterator[List[str]]:
        """Get rows at certain offsets with table checksum.

        This is usually used in tandem with row offsets from :class:`DiffResult` to fetch changed rows.

        :param str table_sum: table checksum
        :param list[int] offsets: the offsets of the rows to fetch

        :rtype: typing.Iterator[list[str]]
        """
        r = self._get(
            "/tables/%s/rows/" % table_sum,
            params={
                'offsets': ','.join([str(v) for v in offsets])
            }
        )
        for row in csv.reader(io.StringIO(r.text), dialect='unix'):
            yield row

    def diff(self, sum1: str, sum2: str) -> DiffResult:
        """Compares two commits and returns their differences.

        :param str sum1: checksum of the first commit
        :param str sum2: checksum of the second commit

        :rtype: DiffResult
        """
        r = self._get(
            "/diff/%s/%s/" % (sum1, sum2)
        )
        return json_loads(r.content, DiffResult)

    def diff_reader(self, sum1: str, sum2: str, fetch_size: int = 100) -> diffreader.DiffReader:
        """Compares two commits and interpret their differences.

        This method is higher level than :func:`Repository.diff` and should
        be preferred for 99% of use cases.

        :param str sum1: checksum of the first commit
        :param str sum2: checksum of the second commit

        :rtype: DiffReader
        """
        return diffreader.DiffReader(self, sum1, sum2, fetch_size)
