# -*- coding: utf-8 -*-
from typing_extensions import Literal

LANG = Literal["ru", "en", "ua", "lt", "lv", "pl", "ro"]
DAYS = Literal[
    3, 4, 5, 6, 7, 8, 9, 10, "3", "4", "5", "6", "7", "8", "9", "10"
]
STEP3_DAYS = Literal[DAYS, 1, 2, "1", "2"]
