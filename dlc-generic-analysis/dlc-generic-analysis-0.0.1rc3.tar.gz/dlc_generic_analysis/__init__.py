import os

try:
    cuda_bin = os.path.join(os.environ.get("CUDA_PATH_V11_2"), "bin")
    os.add_dll_directory(cuda_bin)
except TypeError as e:
    pass
try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"
from logging import info
import matplotlib as mpl

try:
    import PyQt5
    from . import gui_objects, gui_utils
    from .trimmer import Trimmer
    from .dlc_generic_analysis import MainWidget
    from .viewer import ViewerWidget

    mpl.use("QtAgg")
except (ModuleNotFoundError, ImportError) as e:
    info("dlc-generic-analysis GUI not loaded")
    mpl.use("agg")
from . import geometries, math_utils, utils, video_tools, filter
from .dlc import dlc_analyze
from .analysis import Analysis
