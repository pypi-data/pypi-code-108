from typing import List

try:
    from pip._internal.operations import freeze
except ImportError:  # pip < 10.0
    from pip.operations import freeze

def get_pip_freeze() -> List[str]:
    """Return the freeze list from pip directly as a list"""
    return list(freeze.freeze())
