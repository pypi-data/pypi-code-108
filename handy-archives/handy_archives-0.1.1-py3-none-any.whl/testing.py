#!/usr/bin/env python3
#
#  testing.py
"""
Pytest helpers.

.. extras-require:: testing
	:pyproject:
"""
#
#  Copyright © 2021 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#  DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#  OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
#  OR OTHER DEALINGS IN THE SOFTWARE.
#

# stdlib
import os
from typing import Union

# 3rd party
import pytest  # nodep
from coincidence import AdvancedFileRegressionFixture  # nodep

# this package
from handy_archives import TarFile, ZipFile

__all__ = ["ArchiveFileRegressionFixture", "archive_regression"]


class ArchiveFileRegressionFixture(AdvancedFileRegressionFixture):
	"""
	Class for performing regression checks on files in ``tar`` and ``zip`` archives.
	"""

	def check_archive(self, archive: Union[TarFile, ZipFile], filename: str, **kwargs):
		r"""
		Checks a text file in ``archive`` against a previously recorded version, or generates a new file.

		:param archive: The ``tar`` archive.
		:param filename: The name of the file in the archive to check.
		:param \*\*kwargs: Additional keyword arguments passed to
			:meth:`pytest_regressions.file_regression.FileRegressionFixture.check`.
		"""

		__tracebackhide__ = True

		kwargs.setdefault("extension", os.path.splitext(filename)[-1] or None)
		self.check(archive.read_text(filename), **kwargs)

	def check_archive_binary(self, archive: Union[TarFile, ZipFile], filename: str, **kwargs):
		r"""
		Checks a binary file in ``archive`` against a previously recorded version, or generates a new file.

		:param archive:
		:param filename: The name of the file in the archive to check.
		:param \*\*kwargs: Additional keyword arguments passed to
			:meth:`pytest_regressions.file_regression.FileRegressionFixture.check`.
		"""

		__tracebackhide__ = True

		kwargs.setdefault("extension", os.path.splitext(filename)[-1] or None)
		self.check_bytes(archive.read_bytes(filename), **kwargs)


@pytest.fixture()
def archive_regression(datadir, original_datadir, request) -> AdvancedFileRegressionFixture:
	"""
	Pytest fixture for performing regression tests on files in ``tar`` and ``zip`` archives.
	"""

	return ArchiveFileRegressionFixture(datadir, original_datadir, request)
