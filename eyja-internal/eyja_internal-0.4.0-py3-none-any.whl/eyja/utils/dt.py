import pytz
from datetime import datetime


utc = pytz.utc


def now():
    return utc.localize(datetime.utcnow())