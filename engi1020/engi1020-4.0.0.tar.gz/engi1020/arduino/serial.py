import re
import serial

from . import tlv, tracing

BANNER = b"ENGI 1020 v"


class Link:
    """A serial link to a device that speaks the ENGI 1020 protocol."""

    # Assuming there's only one Grove kit connected to this computer, here it is.
    singleton = None

    @classmethod
    def get(cls, port=None, version=range(5)):
        if cls.singleton is None:
            if port is None:
                port = find_port()

            if port is None:
                from . import ArduinoException
                raise ArduinoException('Unable to find Arduino device')

            cls.singleton = Link(port, version)

        return cls.singleton

    def __init__(self, port, version_range, baud_rate=9600, timeout=5):
        from . import ProtocolError

        self.s = serial.Serial(
            port,
            baud_rate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=timeout,
        )

        self.trace = tracing.default
        self.trace("Reading banner and version", action=True)

        banner = self.read_tlv()
        m = re.match('ENGI 1020 v([0-9]+)(.*)', banner)
        if not m:
            raise ProtocolError(f"Invalid banner: '{banner}'")

        version, remainder = m.groups()

        self.version = int(version)
        if not self.version in version_range:
            raise ProtocolError(
                f"Unknown ENGI 1020 protocol version: {self.version}")

        if self.version >= 2:
            (self.board,) = re.match(' on (.*)', remainder).groups()
            self.signature = None
        if self.version >= 4:
            (self.board, self.signature) = (
                re.match('(.*) \((.*)\)', self.board).groups()
            )
        else:
            self.board = 'ENGI 1020'
            self.signature = None

    def command(self, descrip, command, expect, *params):
        """Execute a remote command.

        Parameters:
          descrip (str):         Human-readable description for tracing
          command (str|bytes):   Command identifier
          expect:                Expected response value, type or predicate
          params:                Byte string(s) to be sent as parameters
        """
        self.trace(descrip, action=True)

        self.write(command.encode() if type(command) == str else command)

        for param in params:
            self.write(param)

        self.trace("Reading response", action=True)
        r = self.read_tlv()

        if isinstance(expect, type(lambda x: x)):
            response_ok = expect(r)
        elif isinstance(expect, type):
            response_ok = isinstance(r, expect)
        else:
            response_ok = (r == expect)

        if not response_ok:
            from . import ProtocolError

            raise ProtocolError(
                f'Response to {command} command should be {expect}, not {r}')

        return r

    def read(self, size=1):
        self.trace("Reading", size, "B")

        b = self.s.read(size)

        if len(b) < size:
            from . import ProtocolError

            raise ProtocolError(f"Failed to read {size} B from {self.s}: {b}")

        self.trace("Read", len(b), "B:", b)

        return b

    def read_tlv(self):
        t = self.read(1)[0]
        len = self.read(1)[0]
        self.trace("Value of type", t, "/", chr(t), "has len", len)

        raw = self.read(len)

        return tlv.decode(chr(t), raw)

    def read_until(self, expected):
        self.trace(f"Reading until:", expected)

        b = self.s.read_until(expected)

        self.trace("Read", len(b), "B:", b)

        return b

    def write(self, raw_bytes):
        self.trace("Writing", len(raw_bytes), "B:", raw_bytes)
        return self.s.write(raw_bytes)

    def write_byte(self, b):
        self.write_integer(b, 1)

    def write_integer(self, n, bytes):
        self.write(n.to_bytes(bytes, byteorder="little"))


def find_port():
    """Find the serial device the Arduino device is attached to.

    With luck, this will be the only serial device. If we're not so lucky,

    If only one Arduino device is connected to the computer, leaving the default
    value of port=None will allow for auto-detection. However, the port value
    can be set explicitly to specify one of several options."""

    import serial.tools.list_ports
    import sys

    if sys.platform == "darwin":
        ports = list(serial.tools.list_ports.grep("cu.usb"))

    elif sys.platform == "win32":
        ports = list(serial.tools.list_ports.comports())

        if len(ports) != 1:
            print("Check Windows Device Manager for COM port number")

    if len(ports) == 0:
        sys.stderr.write("No Arduino device detected (none plugged in?)\n")
        return None

    if len(ports) == 1:
        return ports[0].device

    print("Multiple devices detected:")
    for i, p in enumerate(ports):
        desc = f"({p.description})" if p.description != "n/a" else ""
        print(f"[{i}]    {p.name} {desc}")

    while True:
        try:
            i = int(input("select device> "))
            return ports[int(i)].device

        except IndexError as e:
            sys.stderr.write("Invalid device number\n")

        except ValueError as e:
            print(e)
