from __future__ import print_function
import argparse

from dateutil.tz import tzutc, tzlocal

from .__version__ import __version__
from . import ISO_FORMAT, gpstime, GPSTimeParseAction
from . import LEAPDATA


PARSER = argparse.ArgumentParser(
    description="""GPS time conversion

Print local, UTC, and GPS time for the specified time string.
""",
    epilog="""See the python datetime module for time formating options:
https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior
""",
    formatter_class=argparse.RawDescriptionHelpFormatter)
PARSER.add_argument(
    '-v', '--version', action='version', version=__version__,
    help="print version number and exit")
zg = PARSER.add_mutually_exclusive_group()
zg.add_argument(
    '-l', '--local', action='store_const', dest='tz', const='local',
    help="print only local time")
zg.add_argument(
    '-u', '--utc', action='store_const', dest='tz', const='utc',
    help="print only UTC time")
zg.add_argument(
    '-g', '--gps', action='store_const', dest='tz', const='gps',
    help="print only GPS time")
fg = PARSER.add_mutually_exclusive_group()
fg.add_argument(
    '-i', '--iso', action='store_const', dest='format', const=ISO_FORMAT,
    help="use ISO time format")
fg.add_argument(
    '-f', '--format',
    help="specify time format (see below), or printf numeric format for GPS times")
PARSER.add_argument(
    'time', metavar='TIME', action=GPSTimeParseAction, nargs=argparse.REMAINDER,
    default='now',
    help="time string in any format (including GPS), or current time if not specified")


def tzname(tz):
    return gpstime.now(tz).tzname()


def main():
    LEAPDATA.update_local()

    args = PARSER.parse_args()

    if args.tz == 'gps' and args.format == ISO_FORMAT:
        PARSER.error("argument -g/--gps: not allowed with argument -i/--iso")

    if not args.format:
        if args.tz == 'gps':
            args.format = '%.6f'
        else:
            args.format = '%Y-%m-%d %H:%M:%S.%f %Z'

    gt = args.time

    if not args.tz:
        ltz = tzlocal()
        utz = tzutc()
        print('{}: {}'.format(tzname(ltz), gt.astimezone(ltz).strftime(args.format)))
        print('{}: {}'.format('UTC', gt.astimezone(utz).strftime(args.format)))
        print('{}: {:.6f}'.format('GPS', gt.gps()))
    elif args.tz == 'gps':
        print(args.format % gt.gps())
    else:
        if args.tz == 'local':
            tz = tzlocal()
            if args.format == ISO_FORMAT:
                args.format = args.format[:-1]
        elif args.tz == 'utc':
            tz = tzutc()
        print('{}'.format(gt.astimezone(tz).strftime(args.format)))

##################################################

if __name__ == '__main__':
    main()
