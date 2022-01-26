"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from typing import Type
from pathlib import Path

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


def implements_protocol(proto: Type):
    """
    Creates a decorator for classes that checks that the decorated class implements the runtime protocol `proto`.

        from https://stackoverflow.com/a/62923698/13989012
    """
    def _deco(cls_def):
        try:
            assert issubclass(cls_def, proto)
        except AssertionError as e:
            e.args = (f"{cls_def} does not implement protocol {proto}",)
            raise
        return cls_def
    return _deco


# region[Main_Exec]

if __name__ == '__main__':
    pass

# endregion[Main_Exec]
