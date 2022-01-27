# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved
import _io
import io
import os
import unittest
import sys
import pytest

from tcell_agent.instrumentation.lfi import instrument_file_open
from tcell_agent.instrumentation.manager import InstrumentationManager
from tcell_agent.utils.compat import PY2
from tcell_agent.tests.support.builders import ConfigurationBuilder

pathlib = pytest.importorskip('pathlib')

test_file = os.path.dirname(os.path.realpath(__file__)) + '/passwd'


@pytest.mark.usefixtures('disable_block')
class LFIInstrumentationTests(unittest.TestCase):
    def setUp(self):
        ConfigurationBuilder().set_config()
        instrument_file_open()

    def tearDown(self):
        InstrumentationManager.reset()

    def test_builtin_open_function_is_instrumented(self):
        assert InstrumentationManager.is_instrumented(open) is True

    def test_os_open_function_is_instrumented(self):
        assert InstrumentationManager.is_instrumented(os.open) is True

    def test_io_open_function_is_instrumented(self):
        assert InstrumentationManager.is_instrumented(io.open) is True

    def test__io_open_function_is_instrumented(self):
        assert InstrumentationManager.is_instrumented(_io.open) is True

    def test_builtin_open_function_is_blocking_once(self):
        with open(test_file) as f:
            f.read()
        assert self.block.call_count == 1

    def test_os_open_function_is_blocking_once(self):
        fd = os.open(test_file, os.O_RDONLY)
        os.read(fd, 100)
        assert self.block.call_count == 1

    def test_io_open_function_is_blocking_once(self):
        with io.open(test_file) as f:
            f.read()
        assert self.block.call_count == 1

    def test__io_open_function_is_blocking_once(self):
        with _io.open(test_file) as f:
            f.read()
        assert self.block.call_count == 1


@pytest.mark.skipif(not PY2, reason="Requires Python 2")
@pytest.mark.usefixtures('disable_block')
class Py2LFIInstrumentationTests(unittest.TestCase):
    def setUp(self):
        ConfigurationBuilder().set_config()
        instrument_file_open()

    def tearDown(self):
        InstrumentationManager.reset()

    def test_builtin_file_function_is_instrumented(self):
        assert InstrumentationManager.is_instrumented(file) is True  # noqa  # pylint: disable=undefined-variable

    def test_builtin_file_function_is_blocking_once(self):
        with file(test_file) as f:  # noqa  # pylint: disable=undefined-variable
            f.read()
        assert self.block.call_count == 1

    def test_builtin_file_function_has_correct_wrapper(self):
        assert file.__tcell_instrumentation__new_method__.__name__ == 'py2_file_wrapper'  # noqa  # pylint: disable=undefined-variable

    def test_builtin_open_function_has_correct_wrapper(self):
        assert open.__tcell_instrumentation__new_method__.__name__ == 'py2_open_wrapper'

    def test_os_open_function_has_correct_wrapper(self):
        assert os.open.__tcell_instrumentation__new_method__.__name__ == 'py2_os_open_wrapper'

    def test_io_open_function_has_correct_wrapper(self):
        assert io.open.__tcell_instrumentation__new_method__.__name__ == 'py2_io_open_wrapper'

    def test__io_open_function_has_correct_wrapper(self):
        assert _io.open.__tcell_instrumentation__new_method__.__name__ == 'py2_io_open_wrapper'


@pytest.mark.skipif(PY2, reason="Requires Python 3")
@pytest.mark.usefixtures('disable_block')
class Py3LFIInstrumentationTests(unittest.TestCase):
    def setUp(self):
        if sys.version_info < (3, 10):
            self.call_count = 2
        else:
            self.call_count = 1

        ConfigurationBuilder().set_config()
        instrument_file_open()

    def tearDown(self):
        InstrumentationManager.reset()

    def test_pathlib_open_function_is_blocking_twice(self):
        # since `pathlib.Path.open` is using both `io.open` and `os.open` we
        # will receive two events. In 3.10.0a7+ builds, it only uses `os.open`
        with pathlib.Path(test_file).open('r') as f:
            f.read()
        assert self.block.call_count == self.call_count

    def test_builtin_open_function_has_correct_wrapper(self):
        assert open.__tcell_instrumentation__new_method__.__name__ == 'py3_open_wrapper'

    def test_os_open_function_has_correct_wrapper(self):
        assert os.open.__tcell_instrumentation__new_method__.__name__ == 'py3_os_open_wrapper'

    def test_io_open_function_has_correct_wrapper(self):
        assert io.open.__tcell_instrumentation__new_method__.__name__ == 'py3_io_open_wrapper'

    def test__io_open_function_has_correct_wrapper(self):
        assert _io.open.__tcell_instrumentation__new_method__.__name__ == 'py3_io_open_wrapper'

    def test_pathlib_normalaccessor_open_method_has_correct_wrapper(self):
        assert pathlib._NormalAccessor.open.__tcell_instrumentation__new_method__.__name__ == 'py3_pathlib_normalaccessor_open_wrapper'  # noqa
