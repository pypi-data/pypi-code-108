from __future__ import division, unicode_literals
import os
import sys
import signal
import logging
import argparse
try:
    import yaml
except ImportError:
    pass
try:
    from setproctitle import setproctitle
except ImportError:
    def setproctitle(*args):
        pass

import nds2
from gpstime import gpstime, GPSTimeException

from . import __version__, pg
from . import const
from . import template as _template
from .util import resolve_ndsserver
from ._qt import create_app
from .scope import NDScope

logging.addLevelName(5, 'DATA')
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'WARNING').upper(),
    format="%(name)s: %(message)s",
)

##################################################


def full_version():
    nds2_version = nds2.version()
    return f'''ndscope {__version__}
pygtgraph {pg.__version__}
nds2-client {nds2_version}
'''


def parse_window_str(window):
    if not window:
        return
    try:
        return float(window)
    except:
        window = window.strip('[]()').split(',')
        def z(e):
            if not e:
                return 0
            else:
                return float(e)
        window = list(map(z, window))
        return tuple([min(window), max(window)])

##################################################


PROG = 'ndscope'
USAGE = '''
ndscope [<options>]
ndscope [<options>] <channel> ...
ndscope [<options>] .yaml|.stp|.xml|.txt|-
ndscope [<options>] .hdf5|.h5
ndscope -h|--help|--usage|--version
'''
DESCRIPTION = 'Next generation NDS oscilloscope'
FULL_DESCRIPTION = '''

If no time is specified, online data will be plotted.  The -t option
may be used to specify a time in the past.  Multiple -t options
specify a time range.  Times can be expressed in GPS, Gregorian, or
relative (e.g.  "3 days ago").  Remember to use quotes around
command-line time specifications that include spaces.
Example:

  ndscope H1:GRD-ISC_LOCK_STATE_N
  ndscope -t '2 days ago' -t '1 day ago' H1:GRD-ISC_LOCK_STATE_N

The -w option allows specifying an initial window around a single -t
specification, or an initial lookback time window for online mode.
Windows can be either a single number specifying a full window width,
or a comma-separated pair specifying times relative to the specified
center time.  The ordering of numbers in the winodw does not matter,
as they will be ordered automatically.  If only one number is
specified with a comma the other is assumed to be zero.  Brackets '[]'
or parens '()' can be used around windows to circumvent CLI parsing
confusion, e.g. the following are all equivalent:
'[-10,0]', '(-10,)', ',-10', '0,-10'.
Example:

  ndscope -t 1224990999 -w 1,-10 H1:SUS-PRM_M3_MASTER_OUT_UL_DQ

Left and right mouse buttons control pan and zoom respectively, as
does center wheel.  Missing data will automatically be fetched as
needed when panning and zooming.  Second and minute trend data are
substituted automatically depending on the time scale being
requested/displayed (online minute trends not currenty supported).
Note that acquisition gaps in the data will be filled in by dashed red
lines.

By default all channels are placed into a grid (row-major ordering).
Periods and commas in the channel list (space separated) will cause
new subplots to be created, with periods starting new rows of plots.
Example:

  ndscope H1:FOO , H1:BAR H1:BAZ . H1:QUX

causes three subplots to be created, two in the top row (the second
with two channels H1:BAR and H1:BAZ), and one in the second.  The
--table option will force table layout even if no periods or commas
appear in the channel list.

Plot templates can be loaded from ndscope .yaml, StripTool .stp,
dataviewer .xml, or .txt template files (stdin assumes yaml).  An
ndscope .yaml template file can be generated to stdout with the
--gen-template option.  The "plots:" block in the configuration is a
list of subplot definitions.  Each subplot should include a "channels"
mapping of channel names to curve properties, such as "color",
"width", "scale", and "offset".  Example:

  ndscope H1:FOO H1:BAR H1:BAZ --stack --gen-template > my_template.yaml
  ndscope my_template.yaml

The "export" functionality in the scope can be used to export the plot
scene to an image file, the available data to either HDF5 or MATLAB
.mat format, or the current scope configuration to a template YAML
file.  A matplotlib plot of exported HDF5 data can be produced by
specifying the file as argument:

  ndscope foobar.hdf5

NDS server[:port] should be provided in the NDSSERVER environment
variable, or can be set with the --nds option:

  ndscope --nds=nds.ligo-la.caltech.edu L1:FOO

Please report issues: https://git.ligo.org/cds/ndscope/issues

Environment variables:
  NDSSERVER    HOST[:PORT] of desired NDS server
  DATETIME_TZ  Timezone: 'UTC' (default) or 'LOCAL'
  LOG_LEVEL    Turn on logging ('INFO', 'DEBUG', etc.)
  ANTIALIAS    Turn on anti-aliasing (possible performance hit)
'''


class TimeParseAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=False):
        try:
            gps = gpstime.parse(values).gps()
        except GPSTimeException:
            parser.error("Could not parse time string '{}'".format(values))
        if getattr(namespace, self.dest) is None:
            setattr(namespace, self.dest, [gps])
        else:
            getattr(namespace, self.dest).append(gps)


parser = argparse.ArgumentParser(
    prog=PROG,
    usage=USAGE,
    description=DESCRIPTION,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    add_help=False,
)

parser.add_argument('channels', nargs='*',
                    help=argparse.SUPPRESS)
parser.add_argument('-t', '--time', action=TimeParseAction, default=[],
                    help="time boundary (GPS or natural language), may specify one or two)")
parser.add_argument('-w', '--window', '--time-window', dest='time_window',
                    help="time window scalar or tuple, in seconds")
lgroup = parser.add_mutually_exclusive_group()
lgroup.add_argument('-g', '--grid', dest='layout', action='store_const', const='grid',
                    help="arrange channels in a grid of plots (default)")
lgroup.add_argument('-k', '--stack', dest='layout', action='store_const', const='stack',
                    help="arrange channels in a vertical stack of plots")
lgroup.add_argument('-s', '--single', dest='layout', action='store_const', const='single',
                    help="all channels in a single plot")
lgroup.add_argument('-l', '--table', dest='layout', action='store_const', const='table',
                    help="subplot table layout (period/comman in channel list starts new colum/row)")
# parser.add_argument('--colspan', action='store_true',
#                     help="expand subplots to fill empty columns (BUGGY!)")
parser.add_argument('--title', '--window-title', dest='window_title', metavar='TITLE',
                    help="application window title")
parser.add_argument('--light', dest='color_mode', action='store_const', const='light',
                    help="light color mode (black-on-white plots)")
parser.add_argument('--dark', dest='color_mode', action='store_const', const='dark',
                    help="dark color mode (white-on-black plots) [default]")
parser.add_argument('-bw', '--black-on-white', action='store_true',
                    help=argparse.SUPPRESS)
parser.add_argument('--size', nargs=2, type=int, metavar=('WIDTH', 'HEIGHT'),
                    help="specify initial window size")
parser.add_argument('--nds', metavar='HOST[:PORT]',
                    help=f"NDS server [{const.NDSSERVER}]")
parser.add_argument('--gen-template', action='store_true',
                    help="generate YAML template, dump to stdout, and exit")
parser.add_argument('--single-shot', metavar='PATH',
                    help="export initial plot/data then exit (see export options in usage)")
parser.add_argument('--version', action='version', version=full_version(),
                    help="print version and exit")
parser.add_argument('-h', '--help', action='help',
                    help=argparse.SUPPRESS)
parser.add_argument('--usage', action='store_true',
                    help="print more detailed usage information and exit")
                    #help=argparse.SUPPRESS)


def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    setproctitle(' '.join([PROG] + sys.argv[1:]))

    args = parser.parse_args()

    if args.usage:
        print(DESCRIPTION+FULL_DESCRIPTION)
        sys.exit()

    if args.black_on_white:
        print("Warning: the --black-on-white option is deprecated.  Please use --light instead.")
        args.color_mode = 'light'

    if len(args.time) == 2 and args.time_window:
        parser.error("Time-window argument incompatible with speicyfing two times.")
    elif len(args.time) > 2:
        parser.error("May only specify one or two times.")

    ##########
    # load template

    if args.channels and os.path.splitext(args.channels[0])[1] in ['.hdf5', '.h5']:
        if len(args.channels) > 1:
            parser.error("Only one argument expected when specifying HDF5 file.")
        from . import export
        export.matplot_h5(args.channels[0])
        return

    elif args.channels and (os.path.exists(args.channels[0]) or args.channels[0] == '-'):
        if len(args.channels) > 1:
            parser.error("Only one argument expected when specifying template file.")
        template, ltype = _template.load_template(args.channels[0])

    else:
        template, ltype = _template.template_from_chans(args.channels)
        if not args.channels:
            ltype = args.layout
        elif ',' in args.channels or '.' in args.channels:
            args.layout = 'table'
        elif not args.layout:
            args.layout = 'grid'

    ##########
    # command line argument overlay

    if args.layout and args.layout != ltype:
        _template.convert_layout(template, args.layout)

    if args.color_mode:
        template['color-mode'] = args.color_mode

    if args.window_title:
        template['window-title'] = args.window_title

    ##########
    # parse time specs

    try:
        window = parse_window_str(args.time_window)
    except Exception as e:
        parser.error("Could not parse time window: {}: {}".format(args.time_window, e))

    t0 = template.get('t0')
    if t0 is not None:
        try:
            t0 = gpstime.parse(t0).gps()
        except GPSTimeException:
            parser.error("Could not parse template time string '{}'".format(t0))

    if not window:
        window = template.get('time-window')

    if len(args.time) == 0:
        if t0:
            online = False
        else:
            online = True
        if window:
            if isinstance(window, float):
                window = (-window, 0)
        else:
            window = const.DEFAULT_TIME_WINDOW_ONLINE
    elif len(args.time) == 1:
        online = False
        t0 = args.time[0]
        if window:
            if isinstance(window, float):
                window = (-window/2, window/2)
        else:
            window = const.DEFAULT_TIME_WINDOW_OFFLINE
    elif len(args.time) == 2:
        online = False
        start = min(args.time)
        end = max(args.time)
        t0 = end
        window = [start-end, 0]

    template['t0'] = t0
    template['time-window'] = window

    ##########
    # launch app

    if args.gen_template:
        print(yaml.safe_dump(template, default_style=False))
        sys.exit()

    os.environ['NDSSERVER'] = resolve_ndsserver(args.nds)

    app = create_app()

    scope = NDScope()
    scope.load_template(template)
    if not scope.data.channels:
        if args.single_shot:
            parser.error("Must specify channels for single shot mode.")
        scope.select_channels()
    elif args.single_shot:
        if not t0:
            parser.error("Must specify a time for single shot mode.")
        scope.single_shot_export(args.single_shot)
    scope.show()
    if args.size:
        scope.resize(*args.size)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
