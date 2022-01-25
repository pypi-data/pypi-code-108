# SPDX-License-Identifier: Apache-2.0
# Copyright © 2021 Wrangle Ltd

from datetime import datetime
import typing
import platform
import _csv
from unittest import TestCase
from contextlib import contextmanager
import io
import tempfile
import pathlib
import tarfile
import socket
import re
import time
import os
import subprocess
import csv

import requests

from wrgl.config import Config, Receive, User
from wrgl.diffreader import ColumnChanges
from wrgl.repository import Repository


def read_version():
    pat = re.compile(r'^version = (\d+\.\d+\.\d+)')
    with open(pathlib.Path(__file__).parent.parent / 'setup.cfg', 'r') as f:
        for line in f:
            m = pat.match(line)
            if m is not None:
                return m.group(1)
    raise ValueError('cannot read version from file setup.cfg')


def download_wrgl(version):
    ver_dir = pathlib.Path(__file__).parent / '__testcache__' / version
    OS = platform.system().lower()
    if not ver_dir.exists():
        ver_dir.mkdir(parents=True)
        url = "https://github.com/wrgl/wrgl/releases/download/v%s/wrgl-%s-amd64.tar.gz" % (
            version, OS
        )
        with requests.get(url, stream=True) as r:
            with tarfile.open(mode='r:gz', fileobj=r.raw) as tar:
                tar.extractall(ver_dir)
    return ver_dir / ('wrgl-%s-amd64' % OS) / 'bin'


def get_open_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    s.listen(1)
    port = s.getsockname()[1]
    s.close()
    return str(port)


class RepositoryTestCase(TestCase):
    maxDiff = None

    @classmethod
    def setUpClass(cls):
        cls.version = read_version()
        cls.bin_dir = download_wrgl(cls.version)

    def wrgl(self, *args):
        try:
            result = subprocess.run(
                [self.bin_dir / 'wrgl']+list(args)+["--wrgl-dir", self.repo_dir.name], check=True)
        except subprocess.CalledProcessError as e:
            print(e.stdout)
            print(e.stderr)
            raise
        return result

    @contextmanager
    def run_wrgld(self) -> typing.Iterator[str]:
        port = get_open_port()
        proc = subprocess.Popen(
            [self.bin_dir / 'wrgld', self.repo_dir.name, "-p", port], stdout=subprocess.PIPE)
        time.sleep(1)
        yield "http://localhost:%s" % port
        proc.stdout.close()
        proc.terminate()
        proc.wait()

    def setUp(self):
        super().setUp()
        self.repo_dir = tempfile.TemporaryDirectory()
        self.wrgl("init")
        self.email = "johndoe@domain.com"
        self.name = "John Doe"
        self.password = "password"
        self.wrgl(
            "config", "set", "receive.denyNonFastForwards", "true"
        )
        self.wrgl(
            "config", "set", "user.email", self.email
        )
        self.wrgl(
            "config", "set", "user.name", self.name
        )
        self.wrgl(
            "auth", "add-user", self.email, "--name", self.name, "--password", self.password
        )
        self.wrgl(
            "auth", "add-scope", self.email, "--all"
        )

    def tearDown(self) -> None:
        self.repo_dir.cleanup()
        return super().tearDown()

    @contextmanager
    def commit(self, branch: str, message: str, primary_key: typing.List[str]) -> typing.Iterator["_csv._writer"]:
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            writer = csv.writer(f)
            yield writer
        try:
            self.wrgl(
                "commit", branch, f.name, message, "-p", ",".join(primary_key)
            )
        finally:
            os.remove(f.name)

    def test_commit(self):
        with self.commit("main", "initial commit", ["a"]) as writer:
            writer.writerow(['a', 'b', 'c'])
            writer.writerow(['1', 'q', 'w'])
            writer.writerow(['2', 'a', 's'])

        with self.run_wrgld() as url:
            repo = Repository(url)
            repo.authenticate(self.email, self.password)
            cfg = repo.get_config()
            self.assertEqual(cfg, Config(
                receive=Receive(deny_non_fast_forwards=True),
                user=User(
                    name=self.name,
                    email=self.email
                )
            ))
            cfg.receive.deny_deletes = True
            repo.put_config(cfg)
            cfg = repo.get_config()
            self.assertEqual(cfg, Config(
                receive=Receive(
                    deny_non_fast_forwards=True,
                    deny_deletes=True
                ),
                user=User(
                    name=self.name,
                    email=self.email
                )
            ))

            refs = repo.get_refs()
            self.assertEqual(len(refs), 1)
            commit1 = repo.get_commit(refs['heads/main'])
            self.assertIsInstance(commit1.time, datetime)
            commit2 = repo.get_branch('main')
            print(commit2)
            self.assertEqual(commit1, commit2)

            b = io.StringIO()
            writer = csv.writer(b)
            writer.writerow(['a', 'b', 'c'])
            writer.writerow(['1', 'e', 'w'])
            writer.writerow(['2', 'c', 's'])
            cr = repo.commit(
                branch='main',
                message='second commit',
                file=io.BytesIO(b.getvalue().encode('utf8')),
                primary_key=['a']
            )
            self.assertIsNotNone(cr.sum)
            self.assertIsNotNone(cr.table)

            com_tree = repo.get_commit_tree(cr.sum, 2)
            self.assertIsNotNone(
                com_tree.root.parent_commits[commit1.sum].table
            )

            tbl = repo.get_table(cr.table)
            self.assertEqual(tbl.columns, ['a', 'b', 'c'])
            self.assertEqual(list(repo.get_blocks(cr.sum)), [
                ['a', 'b', 'c'], ['1', 'e', 'w'], ['2', 'c', 's']
            ])
            self.assertEqual(list(repo.get_table_blocks(cr.table)), [
                ['a', 'b', 'c'], ['1', 'e', 'w'], ['2', 'c', 's']
            ])
            self.assertEqual(list(repo.get_rows(cr.sum, [0])), [
                ['1', 'e', 'w']
            ])
            self.assertEqual(list(repo.get_table_rows(cr.table, [0])), [
                ['1', 'e', 'w']
            ])
            dr = repo.diff(cr.sum, commit1.sum)
            self.assertTrue(dr.primary_key == dr.old_primary_key)
            self.assertGreater(len(dr.row_diff), 0)

    def test_diff_reader(self):
        with self.commit("main", "initial commit", ["a"]) as writer:
            writer.writerow(['a', 'b', 'c', 'd'])
            writer.writerow(['1', 'q', 'w', 'e'])
            writer.writerow(['2', 'a', 's', 'd'])
            writer.writerow(['3', 'z', 'x', 'c'])

        with self.commit("main", "second commit", ["a"]) as writer:
            writer.writerow(['a', 'b', 'c', 'e'])
            writer.writerow(['1', 'q', 'u', 'r'])
            writer.writerow(['2', 'a', 's', 'f'])
            writer.writerow(['4', 'y', 'u', 'i'])

        with self.run_wrgld() as url:
            repo = Repository(url)
            token = repo.authenticate(self.email, self.password)

        with self.run_wrgld() as url:
            repo = Repository(url, token)
            com_tree = repo.get_commit_tree("heads/main", 2)
            dr = repo.diff_reader(com_tree.sum, com_tree.root.parents[0])
            self.assertEqual(dr.column_changes, ColumnChanges(
                new_values=['a', 'b', 'c', 'e'],
                old_values=['a', 'b', 'c', 'd'],
                unchanged=set(['a', 'b', 'c']),
                added=set(['e']),
                removed=set(['d'])
            ))
            self.assertEqual(dr.pk_changes, ColumnChanges(
                new_values=['a'],
                old_values=['a'],
                unchanged=set(['a']),
                added=set([]),
                removed=set([])
            ))
            self.assertEqual(len(dr.added_rows), 1)
            self.assertEqual(dr.added_rows.columns, ['a', 'b', 'c', 'e'])
            self.assertEqual(dr.added_rows.primary_key, ['a'])
            self.assertEqual(list(dr.added_rows), [
                ['4', 'y', 'u', 'i']
            ])
            self.assertEqual(len(dr.removed_rows), 1)
            self.assertEqual(dr.removed_rows.columns, ['a', 'b', 'c', 'd'])
            self.assertEqual(dr.removed_rows.primary_key, ['a'])
            self.assertEqual(list(dr.removed_rows), [
                ['3', 'z', 'x', 'c']
            ])
            self.assertEqual(len(dr.modified_rows), 2)
            self.assertEqual(
                dr.modified_rows.columns, ['a', 'b', 'c', 'd', 'e']
            )
            self.assertEqual(dr.modified_rows.primary_key, ['a'])
            self.assertEqual(list(dr.modified_rows), [
                [('1', '1'), ('q', 'q'), ('u', 'w'), (None, 'e'), ('r', None)],
                [('2', '2'), ('a', 'a'), ('s', 's'), (None, 'd'), ('f', None)]
            ])
            self.assertIsNotNone(dr.data_profile)
            self.assertEqual(dr.data_profile.old_rows_count, 3)
            self.assertEqual(dr.data_profile.new_rows_count, 3)
            self.assertEqual(len(dr.data_profile.columns), 5)

    def test_diff_reader_no_changes(self):
        with self.commit("main", "initial commit", ["a"]) as writer:
            writer.writerow(['a', 'b', 'c', 'd'])
            writer.writerow(['1', 'q', 'w', 'e'])
            writer.writerow(['2', 'a', 's', 'd'])
            writer.writerow(['3', 'z', 'x', 'c'])

        with self.commit("main", "second commit", ["a"]) as writer:
            writer.writerow(['a', 'b', 'c', 'd'])
            writer.writerow(['1', 'q', 'w', 'e'])
            writer.writerow(['2', 'a', 's', 'd'])
            writer.writerow(['3', 'z', 'x', 'c'])

        with self.run_wrgld() as url:
            repo = Repository(url)
            repo.authenticate(self.email, self.password)
            com_tree = repo.get_commit_tree("heads/main", 2)
            dr = repo.diff_reader(com_tree.sum, com_tree.root.parents[0])
            self.assertEqual(dr.column_changes, ColumnChanges(
                new_values=['a', 'b', 'c', 'd'],
                old_values=['a', 'b', 'c', 'd'],
                unchanged=set(['a', 'b', 'c', 'd']),
                added=set([]),
                removed=set([])
            ))
            self.assertEqual(dr.pk_changes, ColumnChanges(
                new_values=['a'],
                old_values=['a'],
                unchanged=set(['a']),
                added=set([]),
                removed=set([])
            ))
            self.assertIsNone(dr.added_rows)
            self.assertIsNone(dr.removed_rows)
            self.assertIsNone(dr.modified_rows)
