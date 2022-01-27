

""""""  # start delvewheel patch
def _delvewheel_init_patch_0_0_18():
    import os
    import sys
    libs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'FastWARC.libs'))
    if sys.version_info[:2] >= (3, 8):
        if os.path.exists(os.path.join(sys.base_prefix, 'conda-meta')):
            # backup the state of the environment variable CONDA_DLL_SEARCH_MODIFICATION_ENABLE
            conda_dll_search_modification_enable = os.environ.get('CONDA_DLL_SEARCH_MODIFICATION_ENABLE')
            os.environ['CONDA_DLL_SEARCH_MODIFICATION_ENABLE'] = '1'

        os.add_dll_directory(libs_dir)

        if os.path.exists(os.path.join(sys.base_prefix, 'conda-meta')):
            # restore the state of the environment variable CONDA_DLL_SEARCH_MODIFICATION_ENABLE
            if conda_dll_search_modification_enable is None:
                os.environ.pop('CONDA_DLL_SEARCH_MODIFICATION_ENABLE', None)
            else:
                os.environ['CONDA_DLL_SEARCH_MODIFICATION_ENABLE'] = conda_dll_search_modification_enable
    else:
        from ctypes import WinDLL
        with open(os.path.join(libs_dir, '.load-order-FastWARC-0.10.3')) as file:
            load_order = file.read().split()
        for lib in load_order:
            WinDLL(os.path.join(libs_dir, lib))


_delvewheel_init_patch_0_0_18()
del _delvewheel_init_patch_0_0_18
# end delvewheel patch

# Copyright 2021 Janek Bevendorff
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from .stream_io import FileStream, GZipStream, LZ4Stream
from .stream_io import FastWARCError, StreamError
from .warc import ArchiveIterator, WarcRecord, WarcRecordType
