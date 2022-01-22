import cmd
import shlex
import sys

from . import serial

class GroveShell(cmd.Cmd):
    intro = 'ENGI 1020 Grove shell\n'
    prompt = '> '

    def __init__(self):
        super().__init__()

        self.link = serial.Link.get()

        if self.link.signature:
            self.intro += f'Device {self.link.signature} ({self.link.board})\n'

        self.prompt = f'{self.link.board} v{self.link.version}> '

    def precmd(self, line):
        """Precondition a command line, parsing arguments into Python values.

        Returns: None, 'EOF' or (command, args) tuple.
        """

        cmdline = shlex.split(line)
        if len(cmdline) == 0:
            return None

        cmd = cmdline[0]
        if cmd == 'EOF':
            return 'EOF'

        try:
            args = [parse_arg(a) for a in cmdline[1:]]
            return (cmd, args)
        except Exception as e:
            sys.stderr.write(f"{e}\n")
            return None

    def onecmd(self, line):
        """Execute a single command."""

        if line is None:
            return

        if line == 'EOF' or line == 'exit':
            return True

        try:
            cmd, args = line
            serialized = [serialize(a) for a in args]
            msg = f"Executing {cmd} {' '.join([str(a) for a in args])}"

            print(self.link.command(msg, cmd, valid_response, *serialized))
        except Exception as e:
            sys.stderr.write(f"{e}\n")
            return None


def parse_arg(a):
    """Parse a single command-line argument."""

    try:
        return eval(a)
    except Exception as e:
        return a


def serialize(value):
    """Turn a value passed at the command line into serial bytes."""

    if isinstance(value, bool) or isinstance(value, int):
        return bytes([value])

    if isinstance(value, bytes):
        return value

    if isinstance(value, str):
        # Encode strings with length first
        encoded = value.encode('utf-8')
        b = bytearray([len(encoded)])
        b.extend(encoded)

        return bytes(b)


    raise ValueError(f"{value} has unknown type {type(value)}")


def valid_response(r):
    """Is a response from the Arduino device valid?"""

    return (r is not None)
