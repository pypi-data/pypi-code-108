import os.path
__dir__ = os.path.split(os.path.abspath(os.path.realpath(__file__)))[0]
data_location = os.path.join(__dir__, "verilog")
src = "https://github.com/openrisc/or1k_marocchino.git"

# Module version
version_str = "0.0.post188"
version_tuple = (0, 0, 188)
try:
    from packaging.version import Version as V
    pversion = V("0.0.post188")
except ImportError:
    pass

# Data version info
data_version_str = "0.0.post64"
data_version_tuple = (0, 0, 64)
try:
    from packaging.version import Version as V
    pdata_version = V("0.0.post64")
except ImportError:
    pass
data_git_hash = "79ce290612a0d410023998f258a1755abbea56bc"
data_git_describe = "v0.0-64-g79ce290"
data_git_msg = """\
commit 79ce290612a0d410023998f258a1755abbea56bc
Author: Andrey Bacherov <bandvig@mail.ru>
Date:   Tue Nov 23 23:18:24 2021 +0300

    restore travis killed by previous merge

"""

# Tool version info
tool_version_str = "0.0.post124"
tool_version_tuple = (0, 0, 124)
try:
    from packaging.version import Version as V
    ptool_version = V("0.0.post124")
except ImportError:
    pass


def data_file(f):
    """Get absolute path for file inside pythondata_cpu_marocchino."""
    fn = os.path.join(data_location, f)
    fn = os.path.abspath(fn)
    if not os.path.exists(fn):
        raise IOError("File {f} doesn't exist in pythondata_cpu_marocchino".format(f))
    return fn
