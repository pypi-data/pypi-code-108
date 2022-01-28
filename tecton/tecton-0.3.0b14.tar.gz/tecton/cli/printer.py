import os
import platform
import re
import string

from yaspin import yaspin
from yaspin.spinners import Spinners

"""
A drop-in wrapper around `print` and `yaspin` that's primarily used to filter rich output
(i.e. emojis) from CLI output.

By default, rich output is disabled in non-Mac environments or if TECTON_RICH_OUTPUT != "1".
"""


def safe_string(s: str) -> str:
    if not _rich_output():
        return _filter_nonprintable(_filter_colors(_convert_emoji(s)))
    return s


def safe_print(*objects, **kwargs):
    # Mirrors Python3 print API (https://docs.python.org/3/library/functions.html#print)
    filtered_objects = []
    for o in objects:
        if isinstance(o, str):
            o = safe_string(o)
        filtered_objects.append(o)
    print(*filtered_objects, **kwargs)


def safe_yaspin(spinner, text):
    if not _rich_output():
        return yaspin(Spinners.simpleDots, text=text)
    return yaspin(spinner, text)


def _rich_output() -> bool:
    return platform.system() != "Windows" and (os.environ.get("TECTON_RICH_OUTPUT", "1") == "1")


def _filter_colors(s) -> str:
    # https://stackoverflow.com/questions/30425105/filter-special-chars-such-as-color-codes-from-shell-output
    return re.sub(r"\x1b(\[.*?[@-~]|\].*?(\x07|\x1b\\))", "", s)


def _filter_nonprintable(s) -> str:
    printable = set(string.printable)
    return "".join(filter(lambda x: x in printable, s))


def _convert_emoji(s) -> str:
    emoji_replacements = {"⛔": "[FAIL]", "✅": "[OK]", "💡": "[Tip]", "🎉": "[OK]", "⚠️": "[WARNING]", "↓": "-", "↑": "-"}
    for k, v in emoji_replacements.items():
        s = s.replace(k, v)
    return s
