import os
import platform
import sys

from colors import colors


def run_once(function):
    def wrapper(*args, **kwargs):
        if not wrapper.has_run:
            wrapper.has_run = True
            return function(*args, **kwargs)
    wrapper.has_run = False
    return wrapper


def clear():
    lines = "\n" * 45
    if "idlelib.run" in sys.modules:
        print(lines)
        print(lines)
    else:
        if os.name == "nt":
            os.system("cls")
        elif os.name == "posix":
            os.system("clear")
        else:
            print(lines)
            print(lines)


@run_once
def init_print():
    if platform.system().lower() == 'windows':
        from ctypes import byref, c_int, windll
        stdout_handle = windll.kernel32.GetStdHandle(c_int(-11))
        mode = c_int(0)
        windll.kernel32.GetConsoleMode(c_int(stdout_handle), byref(mode))
        mode = c_int(mode.value | 4)
        windll.kernel32.SetConsoleMode(c_int(stdout_handle), mode)


orignialprint = print


def print(*args, color=None, bcolor=None, sep=" ", **kwargs):
    init_print()
    if len(args) == 1:
        string = str(args[0])
    else:
        string = sep.join(list(map(str, args)))

    if "idlelib.run" in sys.modules:
        orignialprint(string, **kwargs)
    else:
        colorIsHex, bcolorIsHex = 0, 0
        if color is not None:
            if color[0] == "#":
                color = color[1:]
                colorIsHex = 1

            code = None
            for i in range(len(colors)):
                if colors[i][colorIsHex].lower() == color.lower():
                    code = (u"\u001b[38;5;" + str(i) + u"m")

            if code is None:
                raise ValueError("Colour '" + str(color) + "' is not a valid colour in colors.py.")
        else:
            code = ""

        if bcolor is not None:
            if bcolor[0] == "#":
                bcolor = bcolor[1:]
                bcolorIsHex = 1

            bcode = None
            for i in range(len(colors)):
                if colors[i][bcolorIsHex].lower() == bcolor.lower():
                    bcode = (u"\u001b[48;5;" + str(i) + u"m")

            if bcode is None:
                raise ValueError("Background Colour '" + str(bcolor) + "' is not a valid colour in colors.py.")
        else:
            bcode = ""

        reset = u"\u001b[0m"
        orignialprint(bcode, code, string, reset, sep="", **kwargs)
