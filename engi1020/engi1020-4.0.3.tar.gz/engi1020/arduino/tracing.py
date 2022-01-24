def plain(*values, action=False):
    """Trace values with plain black and white."""

    for v in values:
        print(v, end=" ")

    print()


def pretty(*values, action=False):
    """Trace values with pretty colours and xxd-style hexdump."""

    import hexdump
    from colorama import Fore, Style

    for v in values:
        if action:
            print(f"{Fore.YELLOW}{v}", end=" ")
        elif type(v) == str:
            print(f"{Fore.MAGENTA}{v}", end=" ")
        elif type(v) == int:
            print(f"{Fore.GREEN}{v}", end=" ")
        elif type(v) == bytes:
            print(Fore.CYAN)
            hexdump.hexdump(v)
        else:
            print(f"{Fore.BLUE}{v}", end=" ")

    print(Style.RESET_ALL)


def sparse(*values, action=False):
    """Trace actions only."""

    if not action:
        return

    plain(*values)


def null(*args, **kwargs):
    pass


def set_default(name):
    global default

    if name is None:
        default = null

    elif name.lower() == "plain":
        default = plain

    elif name.lower() == "pretty":
        default = pretty

    elif name.lower() == "sparse":
        default = sparse

    else:
        raise ValueError(
            f"Invalid tracer '{name}': expected plain, pretty or sparse")


# Default tracer
default = null
