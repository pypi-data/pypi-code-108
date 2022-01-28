from flowty.interop import ffi, libFlowty, checked
from flowty._version import __version__
import logging


def LibVersion():
    major = ffi.new("int *")
    minor = ffi.new("int *")
    patch = ffi.new("int *")
    tweak = ffi.new("int *")
    try:
        checked(libFlowty.FLWT_Version(major, minor, patch, tweak))
        return f"{major[0]}.{minor[0]}.{patch[0]}.{tweak[0]}"
    except Exception:
        return "Core library not loaded"


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.info(
    f"""
Flowty Network Optimization Solver

Python Interface: {__version__}
Core Library    : {LibVersion()}
"""
)
