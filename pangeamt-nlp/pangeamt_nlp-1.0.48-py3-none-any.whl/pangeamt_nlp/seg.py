from typing import Optional, Dict


class SegCase:
    UPPER = 1
    LOWER = 0
    MIXED = -1


class Seg:
    def __init__(self, src: str, tgt: Optional[str] = None):
        self._src = src
        self._src_raw = src
        self._tgt = tgt
        self._tgt_raw = tgt
        self._error = None
        self._src_entities = []
        self._tgt_entities = []
        self._white_left = ""
        self._white_right = ""
        if src.islower():
            self._src_case = SegCase.LOWER
        elif src.isupper():
            self._src_case = SegCase.UPPER
        else:
            self._src_case = SegCase.MIXED
        self._placeholder_dictionary = {}

    # Todo typing
    def get_src_entities(self):
        return self._src_entities

    # Todo typing
    def set_src_entities(self, src_entities):
        self._src_entities = src_entities

    src_entities = property(get_src_entities, set_src_entities)

    # Todo typing
    def get_tgt_entities(self):
        return self._tgt_entities

    # Todo typing
    def set_tgt_entities(self, tgt_entities):
        self._tgt_entities = tgt_entities

    tgt_entities = property(get_tgt_entities, set_tgt_entities)

    # Src
    def get_src(self) -> str:
        return self._src

    def set_src(self, src: str) -> None:
        self._src = src

    src = property(get_src, set_src)

    # Src raw
    def get_src_raw(self) -> str:
        return self._src_raw

    src_raw = property(get_src_raw)

    # Tgt
    def get_tgt(self) -> Optional[str]:
        return self._tgt

    def set_tgt(self, tgt: str) -> None:
        self._tgt = tgt

    tgt = property(get_tgt, set_tgt)

    # Tgt Raw
    def get_tgt_raw(self) -> Optional[str]:
        return self._tgt_raw

    def set_tgt_raw(self, tgt_raw) -> None:
        self.set_tgt(tgt_raw)
        self._tgt_raw = tgt_raw

    tgt_raw = property(get_tgt_raw, set_tgt_raw)

    # Error
    def get_error(self) -> Optional[str]:
        return self._error

    def set_error(self, error: str) -> None:
        self._error = error

    error = property(get_error, set_error)

    # White left
    def get_white_left(self) -> str:
        return self._white_left

    def set_white_left(self, white_left: str) -> None:
        self._white_left = white_left

    white_left = property(get_white_left, set_white_left)

    # White right
    def get_white_right(self) -> str:
        return self._white_right

    def set_white_right(self, white_right: str) -> None:
        self._white_right = white_right

    white_right = property(get_white_right, set_white_right)

    # Src casing
    def get_src_case(self) -> int:
        return self._src_case

    def set_src_case(self, case) -> None:
        self._src_case = case

    src_case = property(get_src_case, set_src_case)

    # Placeholder dictionary
    def get_placeholder_dictionary(self) -> Dict:
        return self._placeholder_dictionary

    def set_placeholder_dictionary(self, new_dict):
        self._placeholder_dictionary = new_dict

    placeholder_dictionary = property(
        get_placeholder_dictionary, set_placeholder_dictionary
    )
