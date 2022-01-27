import os.path
__dir__ = os.path.split(os.path.abspath(os.path.realpath(__file__)))[0]
data_location = os.path.join(__dir__, "verilog")
src = "https://github.com/openrisc/mor1kx.git"

# Module version
version_str = "5.1.post126"
version_tuple = (5, 1, 126)
try:
    from packaging.version import Version as V
    pversion = V("5.1.post126")
except ImportError:
    pass

# Data version info
data_version_str = "5.1.post2"
data_version_tuple = (5, 1, 2)
try:
    from packaging.version import Version as V
    pdata_version = V("5.1.post2")
except ImportError:
    pass
data_git_hash = "aca24812520db8e3a0347ac45b0ac18027ccf053"
data_git_describe = "v5.1-2-gaca2481"
data_git_msg = """\
commit aca24812520db8e3a0347ac45b0ac18027ccf053
Merge: 16ad5ad 698681d
Author: Stafford Horne <shorne@gmail.com>
Date:   Wed Jan 12 06:08:22 2022 +0900

    Merge pull request #144 from stffrdhrn/synth-params
    
    core: Add parameters to the synth job

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
    """Get absolute path for file inside pythondata_cpu_mor1kx."""
    fn = os.path.join(data_location, f)
    fn = os.path.abspath(fn)
    if not os.path.exists(fn):
        raise IOError("File {f} doesn't exist in pythondata_cpu_mor1kx".format(f))
    return fn
