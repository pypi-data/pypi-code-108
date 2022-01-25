"""colourful output courtesy of lolcat
Parts of the original code were omitted.
"""

# "THE BEER-WARE LICENSE" (Revision 43~maze)
#
# <maze@pyth0n.org> wrote these files. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return.

import io
import math
import os
import random
import re
import sys


# Reset terminal colors at exit
def reset():
    sys.stdout.write("\x1b[0m")
    sys.stdout.flush()


def detect_mode(term_hint="xterm-256color"):
    """
    Poor-mans color mode detection.
    """
    if "ANSICON" in os.environ:
        return 16
    elif os.environ.get("ConEmuANSI", "OFF") == "ON":
        return 256
    elif (
        os.environ.get("COLORTERM", "") == "truecolor"
        or os.environ.get("COLORTERM", "") == "24bit"
    ):
        return "truecolor"
    else:
        term = os.environ.get("TERM", term_hint)
        if term.endswith("-256color") or term in ("xterm", "screen"):
            return 256
        elif term.endswith("-color") or term in ("rxvt",):
            return 16
        else:
            return 256  # optimistic default


# default options
default_options = {
    "spread": 2.0,
    "freq": 0.1,
    "seed": 22.0,
    "animate": False,
    "duration": 12,
    "speed": 20.0,
    "force": False,
    "mode": None,
    "os": 0.0,
}

default_options["os"] = (
    random.randint(0, 256) if default_options["seed"] == 0 else default_options["seed"]
)
default_options["mode"] = default_options["mode"] or detect_mode()

STRIP_ANSI = re.compile(r"\x1b\[(\d+)(;\d+)?(;\d+)?[m|K]")
COLOR_ANSI = (
    (0x00, 0x00, 0x00),
    (0xCD, 0x00, 0x00),
    (0x00, 0xCD, 0x00),
    (0xCD, 0xCD, 0x00),
    (0x00, 0x00, 0xEE),
    (0xCD, 0x00, 0xCD),
    (0x00, 0xCD, 0xCD),
    (0xE5, 0xE5, 0xE5),
    (0x7F, 0x7F, 0x7F),
    (0xFF, 0x00, 0x00),
    (0x00, 0xFF, 0x00),
    (0xFF, 0xFF, 0x00),
    (0x5C, 0x5C, 0xFF),
    (0xFF, 0x00, 0xFF),
    (0x00, 0xFF, 0xFF),
    (0xFF, 0xFF, 0xFF),
)


class LolCat(object):
    def __init__(self, mode=default_options["mode"], output=sys.stdout, spread=None):
        self.mode = mode
        self.output = output
        self.spread = spread

    def _distance(self, rgb1, rgb2):
        return sum(map(lambda c: (c[0] - c[1]) ** 2, zip(rgb1, rgb2)))

    def ansi(self, rgb):
        r, g, b = rgb

        if self.mode == "truecolor":
            return "38;2;" + ";".join(str(x) for x in rgb)
        elif self.mode in (8, 16):
            colors = COLOR_ANSI[: self.mode]
            matches = [
                (self._distance(c, map(int, rgb)), i) for i, c in enumerate(colors)
            ]
            matches.sort()
            color = matches[0][1]

            return "3%d" % (color,)
        else:
            gray_possible = True
            sep = 2.5

            while gray_possible:
                if r < sep or g < sep or b < sep:
                    gray = r < sep and g < sep and b < sep
                    gray_possible = False

                sep += 42.5

            if gray:
                color = 232 + int(float(sum(rgb) / 33.0))
            else:
                color = sum(
                    [16]
                    + [
                        int(6 * float(val) / 256) * mod
                        for val, mod in zip(rgb, [36, 6, 1])
                    ]
                )

            return "38;5;%d" % (color,)

    def wrap(self, *codes):
        return "\x1b[%sm" % ("".join(codes),)

    def rainbow(self, freq, i):
        r = int(math.sin(freq * i) * 127 + 128)
        g = int(math.sin(freq * i + 2 * math.pi / 3) * 127 + 128)
        b = int(math.sin(freq * i + 4 * math.pi / 3) * 127 + 128)
        return [r, g, b]

    def println(self, s, options=default_options.copy()):
        s = s.rstrip()
        if options["force"] or self.output.isatty():
            s = STRIP_ANSI.sub("", s)
        self.println_plain(s, options=options)

        self.output.write("\n")
        self.output.flush()

    def println_plain(self, s, off=0, options=default_options.copy()):
        if self.spread:
            options["spread"] = self.spread
        for i, c in enumerate(s):
            rgb = self.rainbow(
                options["freq"], options["os"] + (off - i) / options["spread"]
            )
            self.output.write("".join([self.wrap(self.ansi(rgb)), c]))

    def get_str(self, s, off=0, options=default_options.copy()):

        with io.StringIO() as f:
            self.output = f
            self.println_plain(s, off=off, options=options)
            return f.getvalue() + "\x1b[0m"


if __name__ == "__main__":  # pragma: no cover

    options = default_options.copy()

    lc = LolCat(mode=options["mode"])

    lc.println(
        "This is LolCat. █████████████████████████████████████████████████████████████████████████████████████████",
        options=options,
    )
    options["os"] += 2  # type: ignore
    lc.println(
        "This is LolCat. █████████████████████████████████████████████████████████████████████████████████████████",
        options=options,
    )
    options["os"] += 2  # type: ignore
    lc.println(
        "This is LolCat. █████████████████████████████████████████████████████████████████████████████████████████",
        options=options,
    )
    options["os"] += 2  # type: ignore
    lc.println(
        "This is LolCat. █████████████████████████████████████████████████████████████████████████████████████████",
        options=options,
    )

    lc.println(
        "With default options. ███████████████████████████████████████████████████████████████████████████████████"
    )
    print(
        lc.get_str(
            "Generated string. ███████████████████████████████████████████████████████████████████████████████████████"
        )
    )
