import inspect
import os

_currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
_FILENAME_EVEUNIVERSE_TESTDATA = "eveuniverse.json"


def test_data_filename():
    return f"{_currentdir}/{_FILENAME_EVEUNIVERSE_TESTDATA}"


def test_image_filename():
    return f"{_currentdir}/test_image.jpg"
