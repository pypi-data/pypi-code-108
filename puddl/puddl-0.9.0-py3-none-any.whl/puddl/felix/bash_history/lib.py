import re
from typing import TextIO


class ParseError(Exception):
    pass


RE_TIMESTAMP = re.compile(r'^#(\d{5}\d+)', re.MULTILINE | re.DOTALL)


def iter_bash_history(fd: TextIO):
    """
    :param fd: file descriptor of a bash history file with HISTTIMEFORMAT='%F__%H-%M-%S '
    :return: (timestamp as int, command_line) tuples
    """
    data = fd.read()
    flat_ts2cmd = RE_TIMESTAMP.split(data)
    # e.g. ["ignore this command", "1585254366", "\nfoo\n", "1585254441", "\nbar\n"]
    # skip to the first timestamp
    while not flat_ts2cmd[0].isnumeric():
        flat_ts2cmd.pop(0)
    # e.g. ["1585254366", "\nfoo\n", "1585254441", "\nbar\n"]
    for ts, command_line in zip(flat_ts2cmd[:-1:2], flat_ts2cmd[1::2]):
        # i.e. zip(["1585254366", "1585254441"], ["\nfoo\n", "\nbar\n"])
        yield int(ts), command_line.strip()
