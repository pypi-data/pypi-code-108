# Copyright 2011-2020 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

import io
import os.path
import re
import subprocess
import sys

from testtools import TestCase
from testtools.matchers import MatchesRegex

from lpbuildd.check_implicit_pointer_functions import (
    filter_log,
    implicit_pattern,
    pointer_pattern,
    )


class TestPointerCheckRegexes(TestCase):

    def test_catches_pointer_from_integer_without_column_number(self):
        # Regex should match compiler errors that don't include the
        # column number.
        line = (
            b"/build/buildd/gtk+3.0-3.0.0/./gtk/ubuntumenuproxymodule.c:94: "
            b"warning: assignment makes pointer from integer without a cast")
        self.assertIsNot(None, pointer_pattern.match(line))

    def test_catches_pointer_from_integer_with_column_number(self):
        # Regex should match compiler errors that do include the
        # column number.
        line = (
            b"/build/buildd/gtk+3.0-3.0.0/./gtk/ubuntumenuproxymodule.c:94:7: "
            b"warning: assignment makes pointer from integer without a cast")
        self.assertIsNot(None, pointer_pattern.match(line))

    def test_catches_implicit_function_without_column_number(self):
        # Regex should match compiler errors that don't include the
        # column number.
        line = (
            b"/build/buildd/gtk+3.0-3.0.0/./gtk/ubuntumenuproxymodule.c:94: "
            b"warning: implicit declaration of function 'foo'")
        self.assertIsNot(None, implicit_pattern.match(line))

    def test_catches_implicit_function_with_column_number(self):
        # Regex should match compiler errors that do include the
        # column number.
        line = (
            b"/build/buildd/gtk+3.0-3.0.0/./gtk/ubuntumenuproxymodule.c:94:7: "
            b"warning: implicit declaration of function 'foo'")
        self.assertIsNot(None, implicit_pattern.match(line))


class TestFilterLog(TestCase):

    def test_out_of_line_no_errors(self):
        in_file = io.BytesIO(b"Innocuous build log\nwith no errors\n")
        out_file = io.BytesIO()
        self.assertEqual(0, filter_log(in_file, out_file))
        self.assertEqual(b"", out_file.getvalue())

    def test_out_of_line_errors(self):
        in_file = io.BytesIO(
            b"Build log with errors\n"
            b"/build/buildd/gtk+3.0-3.0.0/./gtk/ubuntumenuproxymodule.c:94: "
            b"warning: implicit declaration of function 'foo'\n"
            b"/build/buildd/gtk+3.0-3.0.0/./gtk/ubuntumenuproxymodule.c:94: "
            b"warning: assignment makes pointer from integer without a cast\n"
            b"More build log\n")
        out_file = io.BytesIO()
        self.assertEqual(1, filter_log(in_file, out_file))
        self.assertEqual(
            b"Function `foo' implicitly converted to pointer at "
            b"/build/buildd/gtk+3.0-3.0.0/./gtk/ubuntumenuproxymodule.c:94\n",
            out_file.getvalue())

    def test_in_line_no_errors(self):
        in_file = io.BytesIO(b"Innocuous build log\nwith no errors\n")
        out_file = io.BytesIO()
        self.assertEqual(0, filter_log(in_file, out_file, in_line=True))
        self.assertEqual(
            b"Innocuous build log\nwith no errors\n", out_file.getvalue())

    def test_in_line_errors(self):
        in_file = io.BytesIO(
            b"Build log with errors\n"
            b"/build/gtk/ubuntumenuproxymodule.c:94: "
            b"warning: implicit declaration of function 'foo'\n"
            b"/build/gtk/ubuntumenuproxymodule.c:94: "
            b"warning: assignment makes pointer from integer without a cast\n"
            b"More build log\n")
        out_file = io.BytesIO()
        self.assertEqual(1, filter_log(in_file, out_file, in_line=True))
        self.assertThat(out_file.getvalue(), MatchesRegex(
            br"^" +
            re.escape(
                b"Build log with errors\n"
                b"/build/gtk/ubuntumenuproxymodule.c:94: "
                b"warning: implicit declaration of function 'foo'\n"
                b"/build/gtk/ubuntumenuproxymodule.c:94: "
                b"warning: assignment makes pointer from integer without a "
                b"cast\n"
                b"Function `foo' implicitly converted to pointer at "
                b"/build/gtk/ubuntumenuproxymodule.c:94\n"
                b"More build log\n"
                b"Function `foo' implicitly converted to pointer at "
                b"/build/gtk/ubuntumenuproxymodule.c:94\n\n\n\n") +
            br"Our automated build log filter.*",
            flags=re.M | re.S))


class TestCheckImplicitPointerFunctionsScript(TestCase):

    def setUp(self):
        super(TestCheckImplicitPointerFunctionsScript, self).setUp()
        top = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.script = os.path.join(
            top, "bin", "check-implicit-pointer-functions")

    def test_out_of_line_no_errors(self):
        in_bytes = b"Innocuous build log\nwith no errors\n\x80\x81\x82\n"
        process = subprocess.Popen(
            [sys.executable, self.script],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        out_bytes, _ = process.communicate(in_bytes)
        self.assertEqual(0, process.poll())
        self.assertEqual(b"", out_bytes)

    def test_out_of_line_errors(self):
        in_bytes = (
            b"Build log with errors\n"
            b"/build/buildd/gtk+3.0-3.0.0/./gtk/ubuntumenuproxymodule.c:94: "
            b"warning: implicit declaration of function 'foo'\n"
            b"/build/buildd/gtk+3.0-3.0.0/./gtk/ubuntumenuproxymodule.c:94: "
            b"warning: assignment makes pointer from integer without a cast\n"
            b"\x80\x81\x82\n")
        process = subprocess.Popen(
            [sys.executable, self.script],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        out_bytes, _ = process.communicate(in_bytes)
        self.assertEqual(2, process.poll())
        self.assertEqual(
            b"Function `foo' implicitly converted to pointer at "
            b"/build/buildd/gtk+3.0-3.0.0/./gtk/ubuntumenuproxymodule.c:94\n",
            out_bytes)

    def test_in_line_no_errors(self):
        in_bytes = (b"Innocuous build log\nwith no errors\n\x80\x81\x82\n")
        process = subprocess.Popen(
            [sys.executable, self.script, "--inline"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        out_bytes, _ = process.communicate(in_bytes)
        self.assertEqual(0, process.poll())
        self.assertEqual(
            b"Innocuous build log\nwith no errors\n\x80\x81\x82\n", out_bytes)

    def test_in_line_errors(self):
        in_bytes = (
            b"Build log with errors\n"
            b"/build/gtk/ubuntumenuproxymodule.c:94: "
            b"warning: implicit declaration of function 'foo'\n"
            b"/build/gtk/ubuntumenuproxymodule.c:94: "
            b"warning: assignment makes pointer from integer without a cast\n"
            b"\x80\x81\x82\n")
        process = subprocess.Popen(
            [sys.executable, self.script, "--inline"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        out_bytes, _ = process.communicate(in_bytes)
        self.assertEqual(2, process.poll())
        self.assertThat(out_bytes, MatchesRegex(
            br"^" +
            re.escape(
                b"Build log with errors\n"
                b"/build/gtk/ubuntumenuproxymodule.c:94: "
                b"warning: implicit declaration of function 'foo'\n"
                b"/build/gtk/ubuntumenuproxymodule.c:94: "
                b"warning: assignment makes pointer from integer without a "
                b"cast\n"
                b"Function `foo' implicitly converted to pointer at "
                b"/build/gtk/ubuntumenuproxymodule.c:94\n"
                b"\x80\x81\x82\n"
                b"Function `foo' implicitly converted to pointer at "
                b"/build/gtk/ubuntumenuproxymodule.c:94\n\n\n\n") +
            br"Our automated build log filter.*",
            flags=re.M | re.S))
