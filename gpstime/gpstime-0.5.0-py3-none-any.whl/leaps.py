from __future__ import print_function
import os
import sys
import time
import calendar
import warnings


LEAPFILE_NIST = '/usr/share/zoneinfo/leapseconds'
LEAPFILE_IETF = '/usr/share/zoneinfo/leap-seconds.list'
LEAPFILE_IETF_USER = os.path.expanduser('~/.cache/gpstime/leap-seconds.list')
LEAPFILE_IETF_URL = 'https://www.ietf.org/timezones/data/leap-seconds.list'


def ntp2unix(ts):
    """Convert NTP timestamp to UTC UNIX timestamp

    1900-01-01T00:00:00Z -> 1970-01-01T00:00:00Z

    """
    return int(ts) - 2208988800


def load_NIST(path):
    data = []
    expires = 0
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line[:8] == '#expires':
                expires = int(line.split()[1])
            elif line[0] == '#':
                continue
            else:
                year, mon, day, ts, correction = line.split()[1:6]
                st = time.strptime(
                    '{} {} {} {}'.format(year, mon, day, ts),
                    '%Y %b %d %H:%M:%S',
                )
                # FIXME: do something with correction
                data.append(calendar.timegm(st))
    return data, expires


def load_IETF(path):
    data = []
    expires = 0
    first = True
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            elif line[:2] == '#@':
                expires = ntp2unix(line.split()[1])
            elif line[0] == '#':
                continue
            else:
                # ignore the first entry since that doesn't
                # actually correspond to a leap second
                if first:
                    first = False
                    continue
                leap, offset = line.split()[:2]
                # FIXME: do something with offset
                data.append(ntp2unix(leap))
    return data, expires


def fetch_ietf_leapfile(path):
    """Download IETF leap second data to path and return data.

    Downloaded file not be written to path if it fails to parse.

    """
    import requests
    dd = os.path.dirname(path)
    if dd != '' and not os.path.exists(dd):
        os.makedirs(dd)
    r = requests.get(LEAPFILE_IETF_URL)
    r.raise_for_status()
    tmp = path+'.tmp'
    with open(tmp, 'wb') as f:
        for c in r.iter_content():
            f.write(c)
    data, expires = load_IETF(tmp)
    os.rename(tmp, path)
    return data, expires


class LeapData:
    """Leap second data.

    """
    def __init__(self):
        """Load leap second data from file.

        """
        self.data = None
        self.expires = 0
        if os.path.exists(LEAPFILE_NIST):
            self._load(load_NIST, LEAPFILE_NIST)
        if (not self.data or self.expired) and os.path.exists(LEAPFILE_IETF):
            self._load(load_IETF, LEAPFILE_IETF)
        if (not self.data or self.expired) and os.path.exists(LEAPFILE_IETF_USER):
            self._load(load_IETF, LEAPFILE_IETF_USER)
        if self.expired:
            warnings.warn("Leap second data is expired.", RuntimeWarning)

    def _load(self, func, path):
        try:
            self.data, self.expires = func(path)
        except:
            raise RuntimeError("Error loading leap file: {}".format(path))

    @property
    def expired(self):
        """True if leap second data is expired

        """
        return self.expires <= time.time()

    def __iter__(self):
        if not self.data:
            raise RuntimeError("Failed to load leap second data.")
        for leap in self.data:
            yield leap

    def update_local(self):
        """Update local leap second data file.

        Only fetches if existing data doesn't exist or is expired.

        """
        if self.data and not self.expired:
            return
        print("updating user leap second data from IETF...", file=sys.stderr)
        self._load(fetch_ietf_leapfile, LEAPFILE_IETF_USER)


LEAPDATA = LeapData()


if __name__ == '__main__':
    LEAPDATA.update_local()
    print("expires: {}".format(LEAPDATA.expires))
    for ls in LEAPDATA:
        print(ls)
