# import importlib.util
# import sys
from .tools import get_fps
# pylint: disable=E0611
from .pytpu import ProcessingMode  # type: ignore
from .pytpu import TPUDevice  # type: ignore
from .pytpu import TPUInference  # type: ignore
from .pytpu import TPUInferenceException  # type: ignore
from .pytpu import TPUProgram  # type: ignore
from .pytpu import TPUProgramException  # type: ignore
from .pytpu import TPUProgramInfo  # type: ignore
# pylint: enable=E0611

__all__ = [
    'get_fps',
    'ProcessingMode',
    'TPUDevice',
    'TPUInference',
    'TPUInferenceException',
    'TPUProgram',
    'TPUProgramException',
    'TPUProgramInfo',
]

# spec = importlib.util.spec_from_file_location("libtpu", "/usr/lib/libtpu.so")
# libtpu = importlib.util.module_from_spec(spec)
# sys.modules['pytpu'] = libtpu
# sys.modules["pytpu"] = sys.modules["pytpu"].append(libtpu)
