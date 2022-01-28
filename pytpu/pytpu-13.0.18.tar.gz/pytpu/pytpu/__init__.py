import importlib.util
import sys

spec = importlib.util.spec_from_file_location("libtpu", "/usr/lib/pytpu.so")
assert spec
libtpu = importlib.util.module_from_spec(spec)
sys.modules['pytpu.pytpu'] = libtpu


# pylint: disable=E0603
__all__ = [
    'ProcessingMode',
    'TPUDevice',
    'TPUInference',
    'TPUInferenceException',
    'TPUProgram',
    'TPUProgramException',
    'TPUProgramInfo',
]
