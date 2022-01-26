import os
import re

from dateutil.tz import tzutc, tzlocal
from qtpy.QtGui import QColor, QBrush


# default NDS server
NDSSERVER = 'nds.ligo.caltech.edu:31200'

NDSSERVER_ALIAS_MAP = {
    None: NDSSERVER,
    '': NDSSERVER,
    'cit': NDSSERVER,
    'lho': 'nds.ligo-wa.caltech.edu:31200',
    'llo': 'nds.ligo-la.caltech.edu:31200',
}


# date/time formatting for GPS conversion
if os.getenv('DATETIME_TZ') == 'LOCAL':
    DATETIME_TZ = tzlocal()
else:
    DATETIME_TZ = tzutc()
# FIXME: why does '%c' without explicit TZ give very wrong values??
#DATETIME_FMT = '%c'
DATETIME_FMT = '%a %b %d %Y %H:%M:%S %Z'
DATETIME_FMT_OFFLINE = '%Y/%m/%d %H:%M:%S %Z'


# default plot time window
DEFAULT_TIME_WINDOW_ONLINE = (-2, 0)
DEFAULT_TIME_WINDOW_OFFLINE = (-10, 10)


# percentage of full span to add as additional padding when fetching
# new data
DATA_SPAN_PADDING = 0.5


# default trend transition thresholds
TREND_TRANS_THRESHOLD = {
    'raw/sec': 120,
    'sec/min': 3600,
}


# max requestable seconds for the various trend data
# FIXME: this should probably really be based on bytes, but the "raw"
# trends have various sample rates that are not known ahead of time.
TREND_MAX_SECONDS = {
    'raw': 3600,
    'sec': 3600*24*20,
    'min': 3600*24*365*12,
}


# number of lookback bytes available per channel
# 2**22:             4194304
# one week of 16 Hz: 4838400
# 60s of 16k Hz:     7864320
# 2**23:             8388608
DATA_LOOKBACK_LIMIT_BYTES = 2**22


CHANNEL_REGEXP = '^([a-zA-Z0-9-]+:)?[a-zA-Z0-9-_.]+$'
CHANNEL_RE = re.compile(CHANNEL_REGEXP)


# minimum GPS time supported
# 2010-01-01 00:00 UTC
GPS_MIN = 946339215


# tuples of major tick spacing and minor tick division
TICK_SPACINGS = [
    (31536000, 4),

    (31536000/5, 1),
    (56*86400, 8),
    (28*86400, 4),
    (21*86400, 3),
    (14*86400, 2),
    (7*86400, 7),
    (2*86400, 2),
    (86400, 4),

    (12*3600, 4),
    (6*3600, 6),
    (3*3600, 3),
    (2*3600, 4),
    (3600, 6),

    (30*60, 3),
    (15*60, 3),
    (10*60, 2),
    (5*60, 5),
    (2*60, 4),
    (60, 6),

    (30, 3),
    (15, 3),
    (10, 2),
    (5, 5),
    (2, 2),
    (1, 4),

    (0.500000000, 2),
    (0.250000000, 5),
    (0.125000000, 5),
    (0.100000000, 4),
    (0.050000000, 2),
    (0.025000000, 5),
    (0.012500000, 5),
    (0.010000000, 4),
    (0.005000000, 2),
    (0.002500000, 5),
    (0.001250000, 5),
    (0.001000000, 4),
    (0.000500000, 2),
    (0.000250000, 5),
    (0.000125000, 5),
    (0.000100000, 4),
    (0.000050000, 2),
    (0.000025000, 5),
    (0.000012500, 5),
    (0.000010000, 4),
    (0.000005000, 2),
    (0.000002500, 5),
    (0.000001250, 5),
    (0.000001000, 4),
    (0.000000500, 2),
    (0.000000250, 5),
    (0.000000125, 5),
    (0.000000100, 4),
    (0.000000050, 2),
    (0.000000025, 5),
    (0.000000010, 4),
    (0.000000005, 2),
]


# date/time format string to time axis labels
TICK_DATE_FMT = '%b %d %Y\n%H:%M:%S %Z'


# fill color for labels
LABEL_FILL = (0, 0, 0, 200)


COLOR_MODE = {
    'light': {
        'fg': QColor('black'),
        'bg': QBrush(QColor('white')),
    },
    'dark': {
        'fg': QColor('white'),
        'bg': QBrush(QColor('black')),
    },
}
