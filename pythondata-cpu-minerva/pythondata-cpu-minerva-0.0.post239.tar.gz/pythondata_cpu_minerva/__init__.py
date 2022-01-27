import os.path
__dir__ = os.path.split(os.path.abspath(os.path.realpath(__file__)))[0]
data_location = os.path.join(__dir__, "sources")
src = "https://github.com/lambdaconcept/minerva"

# Module version
version_str = "0.0.post239"
version_tuple = (0, 0, 239)
try:
    from packaging.version import Version as V
    pversion = V("0.0.post239")
except ImportError:
    pass

# Data version info
data_version_str = "0.0.post115"
data_version_tuple = (0, 0, 115)
try:
    from packaging.version import Version as V
    pdata_version = V("0.0.post115")
except ImportError:
    pass
data_git_hash = "d4a55f23855f43c9a13fa2f7c0f7c1a62242826b"
data_git_describe = "v0.0-115-gd4a55f2"
data_git_msg = """\
commit d4a55f23855f43c9a13fa2f7c0f7c1a62242826b
Author: Tobias Müller <Tobias_Mueller@twam.info>
Date:   Sun Jan 16 11:39:10 2022 +0100

    Fix nmigen include in cli.py

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
    """Get absolute path for file inside pythondata_cpu_minerva."""
    fn = os.path.join(data_location, f)
    fn = os.path.abspath(fn)
    if not os.path.exists(fn):
        raise IOError("File {f} doesn't exist in pythondata_cpu_minerva".format(f))
    return fn
