import os.path
__dir__ = os.path.split(os.path.abspath(os.path.realpath(__file__)))[0]
data_location = os.path.join(__dir__, "system_verilog")
src = "https://github.com/antmicro/cv32e40p"

# Module version
version_str = "0.0.post134"
version_tuple = (0, 0, 134)
try:
    from packaging.version import Version as V
    pversion = V("0.0.post134")
except ImportError:
    pass

# Data version info
data_version_str = "0.0.post10"
data_version_tuple = (0, 0, 10)
try:
    from packaging.version import Version as V
    pdata_version = V("0.0.post10")
except ImportError:
    pass
data_git_hash = "087cb61a182f6bc4f757d3430865482aaff61cba"
data_git_describe = "v0.0-10-g087cb61"
data_git_msg = """\
commit 087cb61a182f6bc4f757d3430865482aaff61cba
Author: Piotr Binkowski <pbinkowski@antmicro.com>
Date:   Wed May 20 14:40:57 2020 +0200

    disable sim tracer

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
    """Get absolute path for file inside pythondata_cpu_cv32e40p."""
    fn = os.path.join(data_location, f)
    fn = os.path.abspath(fn)
    if not os.path.exists(fn):
        raise IOError("File {f} doesn't exist in pythondata_cpu_cv32e40p".format(f))
    return fn
