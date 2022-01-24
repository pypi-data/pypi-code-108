import os
import traceback
from logging import getLogger

import cffi

logger = getLogger(__name__)

def build(libtraceable_dir):
    try:
        logger.debug('attempting to build libtraceable ffi')
        ffi = cffi.FFI()
        include_path = os.path.join(libtraceable_dir, 'blocking.h')
        logger.debug(
            "Generating libtraceable at include path: %s", include_path)
        static_lib_path = os.path.join(libtraceable_dir, "libtraceable_full.a")
        ffi.set_source("traceableai.filter._blocking",
                       # Since we are calling a fully built library directly no custom source
                       # is necessary. We need to include the .h files, though, because behind
                       # the scenes cffi generates a .c file which contains a Python-friendly
                       # wrapper around each of the functions.

                       # We need to use the absolute path for blocking.h to avoid path differences
                       # when _blocking is referenced from __pycache__ directory
                       '#include "{}"'.format(include_path),
                       # The important thing is to include the pre-built lib in the list of
                       # libraries we are linking against:

                       # static lib uses "extra_objects" keyword
                       extra_objects=[static_lib_path],
                       # needed when using the static lib
                       libraries=["stdc++"],
                       )

        preprocessed_header_path = os.path.join(os.path.dirname(__file__), "blocking.h.preprocessed")
        with open(preprocessed_header_path) as preprocessed_header_file:
            ffi.cdef(preprocessed_header_file.read())

        src_dir = os.path.join(os.path.dirname(__file__), '..', '..')
        logger.debug(src_dir)
        ffi.compile(verbose=True, tmpdir=src_dir)
        logger.debug('successfully built libtraceable ffi')
        return True
    except Exception:  # pylint: disable=broad-except
        logger.error('failed to build libtraceable ffi, %s', traceback.format_exc())
    return False
