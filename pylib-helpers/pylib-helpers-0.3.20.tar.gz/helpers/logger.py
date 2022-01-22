# StdLib
import sys
import traceback

from colorama import Fore, Style, init


class Logger:
    def __init__(self):
        init()

    def print_line(self, size: int = 20):
        self.print_debug(self._get_char_repitition("-", size))

    def print_separation_marker(self):
        self.print_line(size=5)

    def print_plus_line(self, size: int = 20):
        self.print_debug(self._get_char_repitition("+", size))

    def _get_char_repitition(self, char: str, times: int):
        string = ""
        for i in range(times):
            string += char
        return string

    def print_info(self, *args):
        sys.stdout.flush()
        print(f"{Fore.BLUE}[INFO] ", sep="", end="", flush=False)
        print(*args, file=sys.stdout, sep="\n", end="", flush=False)
        print(Style.RESET_ALL, sep="", end="\n", flush=True)

    def print_success(self, *args):
        sys.stdout.flush()
        print(f"{Fore.GREEN}[SUCCESS] ", sep="", end="", flush=False)
        print(*args, file=sys.stdout, sep="\n", end="", flush=False)
        print(Style.RESET_ALL, sep="", end="\n", flush=True)

    def print_warning(self, *args):
        sys.stdout.flush()
        print(f"{Fore.YELLOW}[WARN] ", sep="", end="", flush=False)
        print(*args, file=sys.stdout, sep="\n", end="", flush=False)
        print(Style.RESET_ALL, sep="", end="\n", flush=True)

    def print_debug(self, *args):
        sys.stdout.flush()
        print(f"{Fore.MAGENTA}[DEBUG] ", sep="", end="", flush=False)
        print(*args, file=sys.stdout, sep="\n", end="", flush=False)
        print(Style.RESET_ALL, sep="", end="\n", flush=True)

    def _print_err(self, arg):
        sys.stderr.flush()
        print(f"{Fore.RED}[ERROR] {arg}", file=sys.stderr, sep="\n", end="\n", flush=True)
        if isinstance(arg, Exception):
            err: Exception = arg
            traceback.print_exception(type(err), value=err, tb=err.__traceback__, file=sys.stderr, limit=5000)
        print(Style.RESET_ALL, file=sys.stderr, sep="", end="", flush=True)

    def print_error(self, *args):
        try:
            [self._print_err(arg) for arg in args]
        except Exception as err:
            self._print_err(err)
            self._print_err(args)
