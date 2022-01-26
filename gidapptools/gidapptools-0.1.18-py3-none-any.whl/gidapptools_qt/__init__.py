from importlib.util import find_spec

if find_spec("PySide6") is None:
    raise ImportError("Module can only be used if PySide6 is installed as a dependency.")
