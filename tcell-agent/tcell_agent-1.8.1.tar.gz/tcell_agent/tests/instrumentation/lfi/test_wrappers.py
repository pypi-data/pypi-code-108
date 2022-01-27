# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved
import io
import os
import sys
import unittest
from functools import partial

import pytest

from tcell_agent.instrumentation.lfi import wrappers
from tcell_agent.instrumentation.manager import InstrumentationManager
from tcell_agent.utils.compat import PY2

pathlib = pytest.importorskip('pathlib')

test_file = os.path.dirname(os.path.realpath(__file__)) + '/passwd'


@pytest.mark.skipif(not PY2, reason="Requires Python 2")
@pytest.mark.usefixtures('disable_block')
class Py2BuiltinFileWrapperTests(unittest.TestCase):
    def setUp(self):
        self._wrapper = partial(wrappers.py2_file_wrapper, file)  # noqa  # pylint: disable=undefined-variable

    def test_open_file_is_not_blocked(self):
        with self._wrapper(test_file) as f:
            assert f.read() is not None

    def test_open_file_is_blocked(self):
        self.block.return_value = True
        with pytest.raises(IOError):
            with self._wrapper(test_file) as f:
                f.read()

    def test_block_function_is_called_with_correct_args_using_args(self):
        with self._wrapper(test_file) as f:
            f.read()
        self.block.assert_called_once_with(
            file_path=test_file, mode='Read', opener_class='__builtin__.file'
        )

    def test_block_function_is_called_with_correct_args_using_kwargs(self):
        with self._wrapper(name=test_file, mode='r') as f:
            f.read()
        self.block.assert_called_once_with(
            file_path=test_file, mode='Read', opener_class='__builtin__.file'
        )


@pytest.mark.skipif(not PY2, reason="Requires Python 2")
@pytest.mark.usefixtures('disable_block')
class Py2BuiltinOpenWrapperTests(unittest.TestCase):
    def setUp(self):
        self._wrapper = partial(wrappers.py2_open_wrapper, open)

    def test_open_file_is_not_blocked(self):
        with self._wrapper(test_file) as f:
            assert f.read() is not None

    def test_open_file_is_blocked(self):
        self.block.return_value = True
        with pytest.raises(IOError):
            with self._wrapper(test_file) as f:
                f.read()

    def test_block_function_is_called_with_correct_args_using_args(self):
        with self._wrapper(test_file) as f:
            f.read()
        self.block.assert_called_once_with(
            file_path=test_file, mode='Read', opener_class='__builtin__.open'
        )

    def test_block_function_is_called_with_correct_args_using_kwargs(self):
        with self._wrapper(name=test_file, mode='r') as f:
            f.read()
        self.block.assert_called_once_with(
            file_path=test_file, mode='Read', opener_class='__builtin__.open'
        )


@pytest.mark.skipif(not PY2, reason="Requires Python 2")
@pytest.mark.usefixtures('disable_block')
class Py2OsOpenWrapperTests(unittest.TestCase):
    def setUp(self):
        self._wrapper = partial(wrappers.py2_os_open_wrapper, os.open)

    def test_open_file_is_not_blocked(self):
        fd = self._wrapper(test_file, os.O_RDONLY)
        assert os.read(fd, 100) is not None

    def test_open_file_is_blocked(self):
        self.block.return_value = True
        with pytest.raises(IOError):
            fd = self._wrapper(test_file, os.O_RDONLY)
            os.read(fd, 100)

    def test_block_function_is_called_with_correct_args_using_args(self):
        fd = self._wrapper(test_file, os.O_RDONLY)
        os.read(fd, 100)
        self.block.assert_called_once_with(
            file_path=test_file, mode='Read', opener_class='posix.open'
        )


@pytest.mark.skipif(not PY2, reason="Requires Python 2")
@pytest.mark.usefixtures('disable_block')
class Py2IOOpenWrapperTests(unittest.TestCase):
    def setUp(self):
        self._wrapper = partial(wrappers.py2_io_open_wrapper, io.open)

    def test_open_file_is_not_blocked(self):
        with self._wrapper(test_file) as f:
            assert f.read() is not None

    def test_open_file_is_blocked(self):
        self.block.return_value = True
        with pytest.raises(IOError):
            with self._wrapper(test_file) as f:
                f.read()

    def test_block_function_is_called_with_correct_args_using_args(self):
        with self._wrapper(test_file) as f:
            f.read()
        self.block.assert_called_once_with(
            file_path=test_file, mode='Read', opener_class='_io.open'
        )

    def test_block_function_is_called_with_correct_args_using_kwargs(self):
        with self._wrapper(file=test_file, mode='r') as f:
            f.read()
        self.block.assert_called_once_with(
            file_path=test_file, mode='Read', opener_class='_io.open'
        )


@pytest.mark.skipif(PY2, reason="Requires Python 3")
@pytest.mark.usefixtures('disable_block')
class Py3BuiltinOpenWrapperTests(unittest.TestCase):
    def setUp(self):
        self._wrapper = partial(wrappers.py3_open_wrapper, open)

    def test_open_file_is_not_blocked(self):
        with self._wrapper(test_file) as f:
            assert f.read() is not None

    def test_open_file_is_blocked(self):
        self.block.return_value = True
        with pytest.raises(IOError):
            with self._wrapper(test_file) as f:
                f.read()

    def test_block_function_is_called_with_correct_args_using_args(self):
        with self._wrapper(test_file) as f:
            f.read()
        self.block.assert_called_once_with(file_path=test_file, mode='Read', opener_class='io.open')

    def test_block_function_is_called_with_correct_args_using_kwargs(self):
        with self._wrapper(file=test_file, mode='r') as f:
            f.read()
        self.block.assert_called_once_with(file_path=test_file, mode='Read', opener_class='io.open')


@pytest.mark.skipif(sys.version_info < (3, 6), reason="Requires Python 3.6 or higher")
@pytest.mark.usefixtures('disable_block')
class Py3BuiltinOpenPathlibWrapperTests(unittest.TestCase):
    def setUp(self):
        self._wrapper = partial(wrappers.py3_open_wrapper, open)

    def test_open_file_is_not_blocked(self):
        with self._wrapper(pathlib.Path(test_file)) as f:
            assert f.read() is not None

    def test_open_file_is_blocked(self):
        self.block.return_value = True
        with pytest.raises(IOError):
            with self._wrapper(pathlib.Path(test_file)) as f:
                f.read()

    def test_block_function_is_called_with_correct_args_using_args(self):
        with self._wrapper(pathlib.Path(test_file)) as f:
            f.read()
        self.block.assert_called_once_with(file_path=test_file, mode='Read', opener_class='io.open')

    def test_block_function_is_called_with_correct_args_using_kwargs(self):
        with self._wrapper(file=pathlib.Path(test_file)) as f:
            f.read()
        self.block.assert_called_once_with(file_path=test_file, mode='Read', opener_class='io.open')


@pytest.mark.skipif(PY2, reason="Requires Python 3")
@pytest.mark.usefixtures('disable_block')
class Py3OsOpenWrapperTests(unittest.TestCase):
    def setUp(self):
        self._wrapper = partial(wrappers.py3_os_open_wrapper, os.open)

    def test_open_file_is_not_blocked(self):
        fd = self._wrapper(test_file, os.O_RDONLY)
        assert os.read(fd, 100) is not None

    def test_open_file_is_blocked(self):
        self.block.return_value = True
        with pytest.raises(IOError):
            fd = self._wrapper(test_file, os.O_RDONLY)
            os.read(fd, 100)

    def test_block_function_is_called_with_correct_args_using_args(self):
        fd = self._wrapper(test_file, os.O_RDONLY)
        os.read(fd, 100)
        self.block.assert_called_once_with(
            file_path=test_file, mode='Read', opener_class='posix.open'
        )


@pytest.mark.skipif(PY2, reason="Requires Python 3")
@pytest.mark.usefixtures('disable_block')
@pytest.mark.parametrize(
    'file_path', [
        test_file,
        pytest.param(
            pathlib.Path(test_file),
            marks=pytest.mark.skipif(
                sys.version_info < (3, 6), reason="Requires Python 3.6 or higher"
            )
        )
    ]
)
class Py3PathlibNativeAccessorOpenWrapperTests(object):
    def setup_method(self):
        self._wrapper = partial(
            wrappers.py3_pathlib_normalaccessor_open_wrapper, os.open, pathlib._NormalAccessor()
        )

    def test_open_file_is_not_blocked(self, file_path):
        fd = self._wrapper(file_path, os.O_RDONLY)
        assert os.read(fd, 100) is not None

    def test_open_file_is_blocked(self, file_path):
        self.block.return_value = True
        with pytest.raises(IOError):
            fd = self._wrapper(file_path, os.O_RDONLY)
            os.read(fd, 100)

    def test_block_function_is_called_with_correct_args(self, file_path):
        """ make sure os.open can handle the different arg signatures """
        fd = self._wrapper(file_path, 524288, 438)
        os.read(fd, 100)
        self.block.assert_called_once_with(
            file_path=test_file, mode='Read', opener_class='posix.open'
        )


@pytest.mark.skipif(PY2, reason="Requires Python 3")
@pytest.mark.usefixtures('disable_block')
class Py3IOOpenWrapperTests(unittest.TestCase):
    def setUp(self):
        self._wrapper = partial(wrappers.py3_io_open_wrapper, io.open)

    def test_open_file_is_not_blocked(self):
        with self._wrapper(test_file) as f:
            assert f.read() is not None

    def test_open_file_is_blocked(self):
        self.block.return_value = True
        with pytest.raises(IOError):
            with self._wrapper(test_file) as f:
                f.read()

    def test_block_function_is_called_with_correct_args_using_args(self):
        with self._wrapper(test_file) as f:
            f.read()
        self.block.assert_called_once_with(file_path=test_file, mode='Read', opener_class='io.open')

    def test_block_function_is_called_with_correct_args_using_kwargs(self):
        with self._wrapper(file=test_file, mode='r') as f:
            f.read()
        self.block.assert_called_once_with(file_path=test_file, mode='Read', opener_class='io.open')


@pytest.mark.skipif(PY2, reason="Requires Python 3")
@pytest.mark.usefixtures('disable_block')
class Py3PathlibIOOpenWrapperTests(unittest.TestCase):
    def setUp(self):
        if sys.version_info < (3, 10):
            self.call_count = 2
            self._opener = 'posix.open'
        else:
            self.call_count = 1
            self._opener = 'io.open'


    # since we don't have an explicit wrapper for `pathlib.Path.open` we must
    # patch the `io.open` and `pathlib._NormalAccessor.open` methods which are
    # used by `pathlib.Path.open` under the hood
    def test_pathlib_open_file_is_not_blocked(self):
        with InstrumentationManager() as manager:
            manager.instrument(io, "open", wrappers.py3_io_open_wrapper)
            manager.instrument(
                pathlib._NormalAccessor, "open", wrappers.py3_pathlib_normalaccessor_open_wrapper
            )
            file_path = pathlib.Path(test_file)
            with file_path.open() as f:
                assert f.read() is not None
        assert self.block.call_count == self.call_count

    def test_pathlib_open_file_is_blocked(self):
        self.block.return_value = True
        with InstrumentationManager() as manager:
            manager.instrument(io, "open", wrappers.py3_io_open_wrapper)
            manager.instrument(
                pathlib._NormalAccessor, "open", wrappers.py3_pathlib_normalaccessor_open_wrapper
            )
            with pytest.raises(IOError):
                with pathlib.Path(test_file).open() as f:
                    f.read()
        assert self.block.call_count == 1

    def test_block_function_is_called_with_correct_args(self):
        with InstrumentationManager() as manager:
            manager.instrument(io, "open", wrappers.py3_io_open_wrapper)
            manager.instrument(
                pathlib._NormalAccessor, "open", wrappers.py3_pathlib_normalaccessor_open_wrapper
            )
            with pathlib.Path(test_file).open() as f:
                f.read()
        self.block.assert_called_with(file_path=test_file, mode='Read', opener_class=self._opener)
        assert self.block.call_count == self.call_count
