import sys

PLATFORM_WINDOWS = "windows"
PLATFORM_LINUX = "linux"
PLATFORM_BSD = "bsd"
PLATFORM_DARWIN = "darwin"
PLATFORM_UNKNOWN = "unknown"


def get_platform_name() -> str:
    if sys.platform.startswith("win"):
        return PLATFORM_WINDOWS
    elif sys.platform.startswith("darwin"):
        return PLATFORM_DARWIN
    elif sys.platform.startswith("linux"):
        return PLATFORM_LINUX
    elif sys.platform.startswith(("dragonfly", "freebsd", "netbsd", "openbsd", "bsd")):
        return PLATFORM_BSD
    else:
        return PLATFORM_UNKNOWN


__platform__ = get_platform_name()


def is_linux() -> bool:
    return __platform__ == PLATFORM_LINUX


def is_bsd() -> bool:
    return __platform__ == PLATFORM_BSD


def is_darwin() -> bool:
    return __platform__ == PLATFORM_DARWIN


def is_windows() -> bool:
    return __platform__ == PLATFORM_WINDOWS


if is_windows():
    list_delimiter = ";"
else:
    list_delimiter = ":"
