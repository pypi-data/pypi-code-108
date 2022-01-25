# Copyright (c) 2014-2022 National Technology and Engineering
# Solutions of Sandia, LLC. Under the terms of Contract DE-NA0003525
# with National Technology and Engineering Solutions of Sandia, LLC,
# the U.S. Government retains certain rights in this software.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import logging
import os
import sys

logger = logging.getLogger(__name__)
logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

# We produce logging error messages so the exceptions are used to
# just stop program execution.
if sys.version_info[1] < 7:
    sys.tracebacklimit = None
else:
    sys.tracebacklimit = 0

# Dictionary of data filenames and their corresponding paths for loading
DATA_FILENAMES = {}

def build_data_dict():
    """
        Generate the DATA_FILENAMES dictonary which consists of
        data filenames and their corresponding paths for use within Tracktable.
    """

    file_dir = os.path.dirname(__file__)
    sub_dirs =  [f.path for f in os.scandir(file_dir) if f.is_dir() and "egg" not in f.name and "__pycache__" not in f.name]
    for directory in sub_dirs:
        for root, dir, files in os.walk(directory):
            for file in files:
                if not file.endswith(".py") and not file.endswith(".pyc"):
                    data_file_path = os.path.join(root, file)
                    normalized_path = os.path.normpath(data_file_path)
                    DATA_FILENAMES[file] = normalized_path

def retrieve(filename=None, file_ext=None, print_filenames=False, print_extensions=False):
    """Retrieve files to load/use within Tracktable.

    Keyword Arguments:
        filename (str): File to retrieve from the DATA_FILENAMES dictonary. (Default: None)
        file_ext (str): File extension to match against the DATA_FILENAMES dictonary. (Default: None)
        print_filenames (bool): Bool to print all filenames in the data package. (Default: False)
        print_extensions (bool): Bool to print all extensions in the data package. (Default: False)

    Returns:
        dictionary if no filename or file extension is specified, string containing a file's path if a filename is specified
        or list of strings if a file extension is specified.

    Raises:
        KeyError: no matching file or file extension
    """

    if filename and file_ext:
        logger.info("`filename` and `file_ext` flags are both set, only returning file matching `filename` and ignoring `file_ext`.")

    if len(DATA_FILENAMES) == 0:
        build_data_dict()

    if print_filenames:
        print("Avaliable Data Files")
        print("-"*20)

        for key in sorted(DATA_FILENAMES.keys()):
            print(key)

        return

    if print_extensions:
        print("Avaliable Data File Extensions")
        print("-"*30)

        ext_set = set()
        for key in DATA_FILENAMES.keys():
            ext_set.add(key.split('.')[1])

        for ext in ext_set:
            print(ext)

        return

    if filename:
        try:
            return DATA_FILENAMES[filename]
        except KeyError:
            logger.error("Unknown filename `{}`. Double check the provided filename or call `loader()` again with the `print_filenames` flag set to see all avaliable data files.".format(filename))
            raise KeyError("See log message above.")
    elif file_ext:
        matching_files = []
        for key, val in DATA_FILENAMES.items():
            if key.endswith(file_ext):
                matching_files.append(val)

        if not matching_files:
            logger.error("Unknown file_ext `{}`. Double check the provided filename or call `loader()` again with the `print_extensions` flag set to see all avaliable data file extensions.".format(file_ext))
            raise LookupError("See log message above.")
        else:
            return matching_files
    else:
        return DATA_FILENAMES
