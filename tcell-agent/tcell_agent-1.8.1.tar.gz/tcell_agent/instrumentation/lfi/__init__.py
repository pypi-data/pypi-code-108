# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved
try:
    import __builtin__ as builtins
except ImportError:
    import builtins
import _io
import io
import os

from tcell_agent.instrumentation.decorators import catches_generic_exception
from tcell_agent.instrumentation.lfi import wrappers
from tcell_agent.instrumentation.manager import InstrumentationManager
from tcell_agent.utils import compat
from tcell_agent.config.configuration import get_config
from tcell_agent.tcell_logger import get_module_logger


try:
    import pathlib
except ImportError:
    pass


@catches_generic_exception(__name__, "Could not instrument for lfi")
def instrument_file_open():
    if 'local-file-inclusion' in get_config().disabled_instrumentation or compat.PY2:
        logger = get_module_logger(__name__)
        if logger is not None:
            logger.info("Skipping instrumentation for Local File Inclusion feature")
        return
    else:
        InstrumentationManager.instrument(builtins, "open", wrappers.py3_open_wrapper)
        InstrumentationManager.instrument(os, "open", wrappers.py3_os_open_wrapper)
        InstrumentationManager.instrument(io, "open", wrappers.py3_io_open_wrapper)
        InstrumentationManager.instrument(_io, "open", wrappers.py3_io_open_wrapper)
        # we must patch `pathlib._NormalAccessor.open` explicitly since it has
        # an old reference to `os.open`, otherwise we might get inconsistent
        # behaviour depending on when `pathlib` is imported
        InstrumentationManager.instrument(
            pathlib._NormalAccessor, "open", wrappers.py3_pathlib_normalaccessor_open_wrapper
        )
