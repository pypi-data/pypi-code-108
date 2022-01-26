# Copyright 2020 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

"""Test BuildManager directly.

Most tests are done on subclasses instead.
"""

import io
import re

from fixtures import (
    FakeLogger,
    TempDir,
    )
import six
from testtools import TestCase
from testtools.deferredruntest import AsynchronousDeferredRunTest
from twisted.internet import defer
from twisted.python import log

from lpbuildd.builder import (
    Builder,
    BuildManager,
    )
from lpbuildd.tests.fakebuilder import FakeConfig


class TestBuildManager(TestCase):

    run_tests_with = AsynchronousDeferredRunTest.make_factory(timeout=5)

    def setUp(self):
        super(TestBuildManager, self).setUp()
        observer = log.PythonLoggingObserver()
        observer.start()
        self.addCleanup(observer.stop)

    @defer.inlineCallbacks
    def test_runSubProcess(self):
        logger = self.useFixture(FakeLogger())
        config = FakeConfig()
        config.set("builder", "filecache", self.useFixture(TempDir()).path)
        builder = Builder(config)
        builder._log = io.BytesIO()
        manager = BuildManager(builder, "123")
        d = defer.Deferred()
        manager.iterate = d.callback
        manager.runSubProcess("echo", ["echo", "hello world"])
        code = yield d
        self.assertEqual(0, code)
        self.assertEqual(
            b"RUN: echo 'hello world'\n"
            b"hello world\n",
            builder._log.getvalue())
        self.assertEqual(
            "Build log: RUN: echo 'hello world'\n"
            "Build log: hello world\n",
            logger.output)

    @defer.inlineCallbacks
    def test_runSubProcess_bytes(self):
        logger = self.useFixture(FakeLogger())
        config = FakeConfig()
        config.set("builder", "filecache", self.useFixture(TempDir()).path)
        builder = Builder(config)
        builder._log = io.BytesIO()
        manager = BuildManager(builder, "123")
        d = defer.Deferred()
        manager.iterate = d.callback
        manager.runSubProcess("echo", ["echo", u"\N{SNOWMAN}".encode("UTF-8")])
        code = yield d
        self.assertEqual(0, code)
        self.assertEqual(
            u"RUN: echo '\N{SNOWMAN}'\n"
            u"\N{SNOWMAN}\n".encode("UTF-8"),
            builder._log.getvalue())
        logged_snowman = '\N{SNOWMAN}' if six.PY3 else '\\u2603'
        self.assertEqual(
            ["Build log: RUN: echo '%s'" % logged_snowman,
             "Build log: %s" % logged_snowman],
            [re.sub(r".*? \[-\] (.*)", r"\1", line)
             for line in logger.output.splitlines()])
