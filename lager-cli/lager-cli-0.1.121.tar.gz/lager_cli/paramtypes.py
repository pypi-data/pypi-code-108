"""
    lager.paramtypes

    Custom click paramtypes
"""
import collections
import os
import re
import click

class MemoryAddressType(click.ParamType):
    """
        Memory address integer parameter
    """
    name = 'memory address'

    def convert(self, value, param, ctx):
        """
            Parse string reprsentation of a hex integer
        """
        value = value.strip().lower()
        if value.lower().startswith('0x'):
            try:
                return int(value, 16)
            except ValueError:
                self.fail(f"{value} is not a valid hex integer", param, ctx)

        try:
            return int(value, 10)
        except ValueError:
            self.fail(f"{value} is not a valid integer", param, ctx)

    def __repr__(self):
        return 'ADDR'

class HexParamType(click.ParamType):
    """
        Hexadecimal integer parameter
    """
    name = 'hex'

    def convert(self, value, param, ctx):
        """
            Parse string reprsentation of a hex integer
        """
        try:
            return int(value, 16)
        except ValueError:
            self.fail(f"{value} is not a valid hex integer", param, ctx)

    def __repr__(self):
        return 'HEX'

class VarAssignmentType(click.ParamType):
    """
        Openocd variable parameter
    """
    name = 'FOO=BAR'

    def convert(self, value, param, ctx):
        """
            Parse a variable assignment
        """
        parts = value.split('=')
        if len(parts) != 2:
            self.fail('Invalid assignment', param, ctx)

        return parts

    def __repr__(self):
        return 'VAR ASSIGNMENT'

class EnvVarType(click.ParamType):
    """
        Environment variable
    """
    name = 'FOO=BAR'
    regex = re.compile(r'\A[a-zA-Z_]{1,}[a-zA-Z0-9_]{0,}\Z')

    def convert(self, value, param, ctx):
        """
            Parse string representation of environment variable
        """
        parts = value.split('=', maxsplit=1)
        if len(parts) != 2:
            self.fail('Invalid assignment', param, ctx)

        name = parts[0]
        if not self.regex.match(name):
            self.fail(f'Invalid environment variable name "{name}". Names must begin with a letter or underscore, and may only contain letters, underscores, and digits', param, ctx)

        return value

    def __repr__(self):
        return 'ENV VAR'

Binfile = collections.namedtuple('Binfile', ['path', 'address'])
class BinfileType(click.ParamType):
    """
        Type to represent a command line argument for a binfile (<path>,<address>)
    """
    envvar_list_splitter = os.path.pathsep
    name = 'binfile'

    def __init__(self, *args, exists=False, **kwargs):
        self.exists = exists
        super().__init__(*args, **kwargs)

    def convert(self, value, param, ctx):
        """
            Convert binfile param string into useable components
        """
        parts = value.rsplit(',', 1)
        if len(parts) != 2:
            self.fail(f'{value}. Syntax: --binfile <filename>,<address>', param, ctx)
        filename, address = parts
        path = click.Path(exists=self.exists).convert(filename, param, ctx)
        address = HexParamType().convert(address, param, ctx)

        return Binfile(path=path, address=address)

    def __repr__(self):
        return 'BINFILE'

        # CAN_FRAME format:

        # \b
        # <can_id>#{R|data}
        #     for CAN 2.0 frames

        # \b
        # <can_id>##<flags>{data}
        #     for CAN FD frames

        # \b
        # <can_id>:
        #     can have 3 (SFF) or 8 (EFF) hex chars

        # \b
        # {data}:
        #     has 0..8 (0..64 CAN FD) ASCII hex-values (optionally separated by '.')

        # \b
        # <flags>:
        #     a single ASCII Hex value (0 .. F) which defines canfd_frame.flags

        # \b
        # CAN_FRAME Examples:



CanFrame = collections.namedtuple('CanFrame', [
    'arbitration_id',
    'is_fd',
    'is_error_frame',
    'is_remote_frame',
    'is_extended_id',
    'data',
])

CanFilter = collections.namedtuple('CanFilter', [
    'can_id',
    'can_mask',
    'extended',
])

PortForwardSpecifier = collections.namedtuple('PortForwardSpecifier', [
    'src',
    'dst',
    'proto',
])

def parse_can_data(data_str):
    parts = data_str.split('.')
    return list(b''.join([bytes.fromhex(part) for part in parts]))

def parse_can2(value):
    arbitration_id, rest = value.split('#')
    arbitration_id = int(arbitration_id, 16)
    if rest == 'R':
        is_remote_frame = True
        data = None
    else:
        is_remote_frame = False
        data = parse_can_data(rest)
    return CanFrame(
        arbitration_id=arbitration_id,
        is_fd=False,
        is_error_frame=False,
        is_remote_frame=is_remote_frame,
        is_extended_id=False,
        data=data,
    )


def parse_canfd(value):
    arbitration_id, rest = value.split('##')
    arbitration_id = int(arbitration_id, 16)
    flags = int(rest[0:1], 16)
    data = parse_can_data(rest[1:])
    return CanFrame(
        arbitration_id=arbitration_id,
        is_fd=True,
        is_error_frame=False,
        is_remote_frame=False,
        is_extended_id=False,
        data=data,
        flags=flags,
    )

class CanFrameType(click.ParamType):
    """
        Type to represent a command line argument for a CAN frame
    """
    name = 'CANFrame'

    def convert(self, value, param, ctx):
        """
            Parse out a CAN frame
        """
        if '#' in value:
            return parse_can2(value)
        if '##' in value:
            return parse_canfd(value)
        raise ValueError('Invalid CAN frame.\nSee `lager canbus send --help` for format and examples.')

    def __repr__(self):
        return 'CAN_FRAME'


class CanFilterType(click.ParamType):
    """
        Type to represent a command line argument for a CAN frame
    """
    name = 'CANFilter'

    def convert(self, value, param, ctx):
        """
            Parse out a CAN frame
        """
        try:
            can_id, can_mask = value.split(':')
            if len(can_id) not in (3, 8):
                self.fail('Filter can_id must be 3 or 8 hexadecimal digits')
            extended = len(can_id) == 8
            can_id = int(can_id, 16)
            can_mask = int(can_mask, 16)
        except ValueError:
            self.fail('Invalid filter format.\nSee lager canbus dump --help')

        return CanFilter(can_id=can_id, can_mask=can_mask, extended=extended)

    def __repr__(self):
        return 'CAN_FILTER'

class ADCChannelType(click.ParamType):
    """
        Type to represent a command line argument for a CAN frame
    """
    name = 'CHANNEL'

    SPECIAL = ('VTREF', 'VIO')
    def convert(self, value, param, ctx):
        """
            Parse out an ADC Channel
        """
        if value in self.SPECIAL:
            return value
        if '-' in value:
            start, end = value.split('-', 1)
            start = int(start, 10)
            end = int(end, 10)
            if start < 0 or start > 5:
                self.fail('Range start must be 0-5')
            if end < 0 or end > 5:
                self.fail('Range end must be 0-5')
            if end <= start:
                self.fail('Range start must be before range end')
            return {'start': start, 'end': end}
        value = int(value, 10)
        if value < 0 or value > 5:
            self.fail('Read channel must be 0-5')
        return {'channel': value}

    def __repr__(self):
        return 'ADC_CHANNEL'


class CanbusRange(click.ParamType):
    """
        Type to represent a command line argument for a CAN frame
    """
    name = 'CANRange'

    def convert(self, value, param, ctx):
        """
            Parse out a CAN interface range
        """
        output = []
        for part in value.split(','):
            rangevals = part.split('-')
            if len(rangevals) == 1:
                output.append(int(rangevals[0]))
            elif len(rangevals) == 2:
                start = int(rangevals[0], 10)
                end = int(rangevals[1], 10) + 1
                output.extend(range(start, end))
            else:
                self.fail(f'Invalid range {part}')

        return sorted(set(output))

    def __repr__(self):
        return 'CAN_RANGE'


class PortForwardType(click.ParamType):
    """
        Environment variable
    """
    name = 'PORT'
    regex = re.compile(r'\A([0-9]+)(:[0-9]+)?(/[a-z]+)?\Z')
    RESERVED = [2331, 3333, 4444, 8081, 5555, 8888]

    def convert(self, value, param, ctx):
        """
            Parse string representation of environment variable
        """
        match = self.regex.search(value)
        if not match:
            self.fail(f'Invalid port specifier "{value}".', param, ctx)

        source = int(match[1], 10)
        if source in self.RESERVED:
            self.fail(f'Port {source} is reserved for internal use on the gateway.', param, ctx)

        if match[2]:
            dest = int(match[2][1:], 10)
        else:
            dest = source

        if match[3]:
            protocol = match[3][1:]
        else:
            protocol = None

        return PortForwardSpecifier(source, dest, protocol)

    def __repr__(self):
        return 'PORT FORWARD'
