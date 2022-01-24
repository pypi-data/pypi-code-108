#!/usr/bin/env python3
#
#  __init__.py
"""
Some handy archive helpers for Python.
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
import datetime
import os
import shutil
import sys
import tarfile
import zipfile
from typing import IO, Optional, Type, TypeVar, Union

# 3rd party
from domdf_python_tools.typing import PathLike

__author__: str = "Dominic Davis-Foster"
__copyright__: str = "2021 Dominic Davis-Foster"
__license__: str = "MIT License"
__version__: str = "0.1.1"
__email__: str = "dominic@davis-foster.co.uk"

__all__ = ["unpack_archive", "TarFile", "ZipFile", "is_tarfile"]

_Self = TypeVar("_Self")

if "wheel" not in shutil._UNPACK_FORMATS:  # type: ignore
	shutil.register_unpack_format(
			name="wheel",
			extensions=[".whl"],
			function=shutil._unpack_zipfile,  # type: ignore
			)


def unpack_archive(filename, extract_dir=None, format=None):  # noqa: A002  # pylint: disable=redefined-builtin
	"""
	Unpack an archive.

	:param filename: The name of the archive.

	:param extract_dir: The name of the target directory, where the archive is unpacked.
		If not provided, the current working directory is used.

	:param format: The archive format: one of ``'zip'``, ``'tar'``, ``'gztar'``, ``'bztar'``, or ``'xztar'``,
		or any other format registered through :func:`shutil.register_unpack_format`.
		If not provided, ``unpack_archive`` will use the filename extension and see if
		an unpacker was registered for that extension.

	If no unpacker is found, a :exc:`ValueError` is raised.
	"""

	if sys.version_info < (3, 7):  # pragma: no cover (py37+)

		if extract_dir is not None:
			extract_dir = os.fspath(extract_dir)

		filename = os.fspath(filename)

	shutil.unpack_archive(filename, extract_dir, format)


class TarFile(tarfile.TarFile):
	"""
	Subclass of :class:`tarfile.TarFile` with additional methods.
	"""

	closed: bool
	offset: int

	def extractfile(self, member: Union[str, tarfile.TarInfo]) -> IO[bytes]:
		"""
		Extract a member from the archive as a file object.

		:param member: A filename or a :class:`tarfile.TarInfo` object.

		If ``member`` is a regular file or a link, an :class:`io.BufferedReader` object is returned.

		Otherwise :exc:`FileNotFoundError` is raised.
		"""

		if isinstance(member, str):
			tarinfo = self._getmember(member)  # type: ignore
			if tarinfo is None:
				raise FileNotFoundError(member)
			else:
				fd = super().extractfile(member)
		else:
			fd = super().extractfile(member)

		if fd is None:
			raise FileNotFoundError(member)
		else:
			return fd

	def read_text(
			self,
			member: Union[str, tarfile.TarInfo],
			*,
			normalize_nl: bool = False,
			) -> str:
		r"""
		Returns the content of the given file as a string.

		:param member:
		:param normalize_nl: If :py:obj:`True`, line endings are normalized to ``\n`` (LF).

		:raises FileNotFoundError: If the file is not found in the archive.

		:rtype:

		.. versionadded:: 0.2.0  Added the ``normalize_nl`` option.
		"""

		return _normalize_nl(self.read_bytes(member).decode("UTF-8"), normalize_nl)

	def read_bytes(self, member: Union[str, tarfile.TarInfo]) -> bytes:
		"""
		Returns the content of the given file as bytes.

		:param member:

		:raises FileNotFoundError: If the file is not found in the archive.
		"""

		with self.extractfile(member) as fd:
			return fd.read()

	def write_file(self, filename, arcname=None, mtime: Optional[datetime.datetime] = None):
		"""
		Add the file ``filename`` to the archive under the name ``arcname``.

		:param filename:
		:param arcname: An alternative name for the file in the archive.
		:param mtime: The last modified time of the file.
			Defaults to the value obtained from :func:`os.stat`.
		:no-default mtime:
		"""

		if not os.path.isfile(filename):
			raise IsADirectoryError("'TarFile.write_file' only supports files.")

		if mtime is None:
			return self.add(filename, arcname, recursive=False)

		if arcname is None:  # pragma: no cover
			arcname = filename

		if isinstance(arcname, os.PathLike):
			arcname = os.fspath(arcname)

		self._check("awx")  # type: ignore

		# Skip if somebody tries to archive the archive...
		if self.name is not None and os.path.abspath(filename) == self.name:  # pragma: no cover
			self._dbg(2, "tarfile: Skipped %r" % filename)  # type: ignore
			return

		self._dbg(1, filename)  # type: ignore

		# Create a TarInfo object from the file.
		tarinfo = self.gettarinfo(filename, arcname)
		tarinfo.mtime = mtime.timestamp()  # type: ignore

		if tarinfo is None:  # pragma: no cover
			self._dbg(1, f"tarfile: Unsupported type {filename!r}")
			return

		# Append the tar header and data to the archive.
		with open(filename, "rb") as f:
			self.addfile(tarinfo, f)

	def __enter__(self: _Self) -> _Self:
		return super().__enter__()  # type: ignore

	@classmethod  # noqa: A003  # pylint: disable=redefined-builtin
	def open(  # noqa: D102
			cls: Type[_Self],
			name=None,
			*args,
			**kwargs,
			) -> _Self:

		if name is not None:
			name = os.fspath(name)

		return super().open(  # type: ignore
				name,
				*args,
				**kwargs,
				)


class ZipFile(zipfile.ZipFile):
	"""
	Subclass of :class:`tarfile.TarFile` with additional methods.
	"""

	def extractfile(
			self,
			member: Union[str, zipfile.ZipInfo],
			pwd: Union[str, bytes, None] = None,
			) -> IO[bytes]:
		"""
		Extract a member from the archive as a file object.

		:param member: A filename or a :class:`zipfile.ZipInfo` object.
		:param pwd: The password to decrypt files.

		:raises FileNotFoundError: If the file is not found in the archive.
		"""

		info: zipfile.ZipInfo

		# Make sure we have an info object
		if isinstance(member, zipfile.ZipInfo):
			# 'member' is already an info object
			info = member
		else:
			# Get info object for 'member'
			maybe_info = self.NameToInfo.get(member)
			if maybe_info is None:
				raise FileNotFoundError(member)
			else:
				info = maybe_info

		if isinstance(pwd, str):
			pwd = pwd.encode("UTF-8")

		return self.open(info, pwd=pwd)

	def read_text(
			self,
			member: Union[str, zipfile.ZipInfo],
			pwd: Union[str, bytes, None] = None,
			*,
			normalize_nl: bool = False
			) -> str:
		r"""
		Returns the content of the given file as a string.

		:param member:
		:param pwd: The password to decrypt files.
		:param normalize_nl: If :py:obj:`True`, line endings are normalized to ``\n`` (LF).

		:raises FileNotFoundError: If the file is not found in the archive.

		:rtype:

		.. versionadded:: 0.2.0  Added the ``normalize_nl`` option.
		"""

		return _normalize_nl(self.read_bytes(member, pwd=pwd).decode("UTF-8"), normalize_nl)

	def read_bytes(
			self,
			member: Union[str, zipfile.ZipInfo],
			pwd: Union[str, bytes, None] = None,
			) -> bytes:
		"""
		Returns the content of the given file as bytes.

		:param member:
		:param pwd: The password to decrypt files.

		:raises FileNotFoundError: If the file is not found in the archive.
		"""

		with self.extractfile(member, pwd=pwd) as fd:
			return fd.read()

	def write_file(self, filename, arcname=None, mtime: Optional[datetime.datetime] = None):
		"""
		Put the bytes from ``filename`` into the archive under the name ``arcname``.

		:param filename:
		:param arcname: An alternative name for the file in the archive.
		:param mtime: The last modified time of the file.
			Defaults to the value obtained from :func:`os.stat`.
		:no-default mtime:
		"""

		if self._writing:  # type: ignore
			raise ValueError("Can't write to ZIP archive while an open writing handle exists")

		if not os.path.isfile(filename):
			raise IsADirectoryError("'ZipFile.write_file' only supports files.")

		if mtime is None:
			return self.write(filename, arcname)

		if isinstance(arcname, os.PathLike):
			arcname = os.fspath(arcname)

		zinfo = zipfile.ZipInfo(arcname, mtime.timetuple()[:6])

		zinfo.compress_type = self.compression

		if sys.version_info >= (3, 7):  # pragma: no cover (<py37)
			zinfo._compresslevel = self.compresslevel

		with open(filename, "rb") as src, self.open(zinfo, 'w') as dest:
			shutil.copyfileobj(src, dest, 1024 * 8)

	def __enter__(self: _Self) -> _Self:
		return super().__enter__()  # type: ignore


def is_tarfile(name: Union[PathLike, IO[bytes]]):
	"""
	Return :py:obj:`True` if ``name`` points to a tar archive that :mod:`tarfile` can handle, else return :py:obj:`False`.

	:param name: A string, file, or file-like object.
	"""

	try:
		if hasattr(name, "read"):
			t = TarFile.open(fileobj=name)
		else:
			t = TarFile.open(name)
		t.close()
		return True

	except tarfile.TarError:
		return False


def _normalize_nl(text: str, enable: bool):
	if enable:
		return text.replace("\r\n", '\n').replace('\r', '\n')
	else:
		return text
