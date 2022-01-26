import os
import time
import logging
import numpy as np

import nds2
from gpstime import gpsnow

from qtpy import QtCore
from qtpy.QtCore import Signal


logger = logging.getLogger('NDS  ')


##########

# ctypes: 'online', 's-trend', 'm-trend'
# mods: 'raw', 'min', 'max', 'mean'

CHANNEL_TYPE_MASK = nds2.channel.CHANNEL_TYPE_ONLINE | nds2.channel.CHANNEL_TYPE_RAW | nds2.channel.CHANNEL_TYPE_RDS | nds2.channel.CHANNEL_TYPE_TEST_POINT

TREND_CTYPES = [
    nds2.channel.CHANNEL_TYPE_STREND,
    nds2.channel.CHANNEL_TYPE_MTREND,
]

##########


def _parse_channel(channel):
    ct = channel.split(',')
    name = ct[0]
    if len(ct) > 1:
        if ct[1] == 's-trend':
            ctype = nds2.channel.CHANNEL_TYPE_STREND
            sample_rate = 1
        elif ct[1] == 'm-trend':
            ctype = nds2.channel.CHANNEL_TYPE_MTREND
            sample_rate = 1/60
    elif 'MON' in name:
        ctype = nds2.channel.CHANNEL_TYPE_RAW
        sample_rate = 16
    else:
        ctype = nds2.channel.CHANNEL_TYPE_RAW
        sample_rate = 2**14
    return name, ctype, sample_rate


class FakeChannel:
    def __init__(self, name, ctype, sample_rate):
        self.name = name
        self.channel_type = ctype
        self.sample_rate = sample_rate

    def Units(self):
        return ''

    def DataTypeSize(self):
        return 8


class FakeBuffer:
    def __init__(self, name, ctype, sample_rate, seconds, nanoseconds, data):
        self.channel = FakeChannel(name, ctype, sample_rate)
        assert isinstance(seconds, int)
        assert isinstance(nanoseconds, int)
        self.gps_seconds = seconds
        self.gps_nanoseconds = nanoseconds
        self.data = data

    def __repr__(self):
        return '<{} {} {}.{} {}>'.format(
            self.__class__.__name__,
            self.channel.name,
            self.gps_seconds, self.gps_nanoseconds,
            len(self.data),
        )


class FakeChannelSource:
    def __init__(self, channel):
        self.channel = channel
        self.amp = np.random.normal(10, 5, 1)
        self.freq = 2*np.pi * np.random.normal(1, 1/2, 1)
        self.phase = 2*np.pi * np.random.random()
        self.offset = np.random.normal(0, 20, 1)

    def sampler(self, t):
        # signal
        data = self.amp*np.sin(t * self.freq + self.phase)
        # add offset
        data += self.offset
        # add noise
        # data += np.random.normal(0, 1, len(t))
        data += np.random.exponential(3, len(t))
        # add glitches
        #data += 20 * np.random.power(0.1, len(t)) * np.random.choice([-1,1])
        # add a gap
        if np.random.randint(0, 100) == 0:
            data *= np.nan
        return data

    def gen_buf(self, ctype, sample_rate, start, stride):
        seconds = int(start)
        nanoseconds = int((start % 1) * 1e9)
        nsamples = int(sample_rate*stride)
        t = np.arange(nsamples)/sample_rate + seconds + nanoseconds*1e-9
        data = self.sampler(t)
        data = np.where(t < gpsnow(), data, np.nan)
        return FakeBuffer(
            self.channel,
            ctype,
            sample_rate,
            seconds,
            nanoseconds,
            data,
        )


class FakeSource:
    def __init__(self):
        self.sources = {}

    def gen_bufs(self, channels, start, stride):
        bufs = []
        for chan in channels:
            name, ctype, sample_rate = _parse_channel(chan)
            if name not in self.sources:
                self.sources[name] = FakeChannelSource(name)
            bufs.append(self.sources[name].gen_buf(
                ctype,
                sample_rate,
                start,
                stride,
            ))
        return bufs


FAKE_SOURCE = FakeSource()


def fake_fetch(channels=None, gps_start=None, gps_stop=None, **kwargs):
    global FAKE_SOURCE
    stride = gps_stop - gps_start
    return FAKE_SOURCE.gen_bufs(channels, gps_start, stride)


def fake_iterate(channels=None, stride=None, **kwargs):
    global FAKE_SOURCE
    if stride == -1:
        stride = 1./16
    start = np.floor(gpsnow()) - stride
    while True:
        yield FAKE_SOURCE.gen_bufs(channels, start, stride)
        start += stride
        while gpsnow() <= start+stride:
            time.sleep(0.01)


##########


def get_parameters():
    params = nds2.parameters()
    params.set('GAP_HANDLER', 'STATIC_HANDLER_NAN')
    return params


class Channel:
    """Simple channel metadata class

    Extracts just the info we care about, with a method to update from
    other instances of the same name.

    """
    def __init__(self, nds_channel):
        """initialize with an nds channel object"""
        self.name = nds_channel.name
        self.online = False
        self.testpoint = False
        self.sample_rate = nds_channel.sample_rate
        if self.sample_rate >= 1:
            self.sample_rate = int(self.sample_rate)
        self.update(nds_channel)

    def update(self, nds_channel):
        """update metadata

        from another channel instance of the same name

        """
        assert nds_channel.name == self.name
        self.online |= nds_channel.channel_type == nds2.channel.CHANNEL_TYPE_ONLINE
        self.online |= nds_channel.channel_type == nds2.channel.CHANNEL_TYPE_TEST_POINT
        self.testpoint |= nds_channel.channel_type == nds2.channel.CHANNEL_TYPE_TEST_POINT


def find_channels(channel_glob=None):
    if not channel_glob:
        channel_glob = os.getenv('CHANNEL_GLOB', '*')
    kwargs = {
        'channel_glob': channel_glob,
        'channel_type_mask': CHANNEL_TYPE_MASK,
    }
    if os.getenv('NDSSERVER', '').lower() == 'fake':
        return {}
    else:
        func = nds2.find_channels
    logger.debug("find_channels(**{})".format(kwargs))
    # pre-process channel list into a dictionary of Channel objects
    # useful for building the channel select dialog
    channels = {}
    for channel in func(**kwargs):
        try:
            channels[channel.name].update(channel)
        except KeyError:
            channels[channel.name] = Channel(channel)
    return channels


def iterate(channels, start_end, stride):
    kwargs = {
        'channels': channels,
        'stride': stride,
        'params': get_parameters(),
    }
    if start_end:
        kwargs['gps_start'] = start_end[0]
        kwargs['gps_stop'] = start_end[1]
    if os.getenv('NDSSERVER', '').lower() == 'fake':
        func = fake_iterate
    else:
        func = nds2.iterate
    logger.debug("iterate(**{})".format(kwargs))
    for bufs in func(**kwargs):
        yield bufs


def fetch(channels, start_end):
    kwargs = {
        'channels': channels,
        'gps_start': start_end[0],
        'gps_stop': start_end[1],
        'params': get_parameters(),
    }
    if os.getenv('NDSSERVER', '').lower() == 'fake':
        func = fake_fetch
    else:
        func = nds2.fetch
    logger.debug("fetch(**{})".format(kwargs))
    return func(**kwargs)


def parse_channel(channel):
    ctype = nds2.channel.channel_type_to_string(channel.channel_type)
    if ctype in ['s-trend', 'm-trend']:
        # HACK: FIXME: work around a bug in nds2-client around 0.16.3:
        # https://git.ligo.org/nds/nds2-client/issues/85. this should
        # not be necessary (to split on ',') and should be removed
        # once the client is fixed.
        namemod = channel.name.split(',')[0]
        name, mod = namemod.split('.')
    else:
        name = channel.name
        mod = 'raw'
    return name, mod, ctype


def _channels_for_trend(channels, trend):
    if trend == 'raw':
        return channels
    else:
        # use first letter of trend type ('s' or 'm')
        t = trend[0]
        chans = []
        for chan in channels:
            for m in ['mean', 'min', 'max']:
                chans.append('{}.{},{}-trend'.format(chan, m, t))
        return chans


def _start_end_quant(start_end, trend):
    if not start_end:
        return
    start = int(start_end[0])
    end = int(np.ceil(start_end[1]))
    if trend == 'min':
        start -= (start % 60)
        end += 60 - (end % 60)
    assert start < end, "invalid times: {} >= {}".format(start, end)
    return (start, end)

##################################################


class NDSThread(QtCore.QThread):
    new_data = Signal('PyQt_PyObject')
    done = Signal('PyQt_PyObject')

    def __init__(self, tid, cmd, **kwargs):
        super(NDSThread, self).__init__()
        self.tid = tid
        self.cmd = cmd
        if self.cmd == 'find_channels':
            self.method = 'find_channels'
        elif self.cmd == 'online':
            self.method = 'iterate'
        else:
            self.method = 'fetch'
        self.kwargs = kwargs
        self._run_lock = QtCore.QMutex()
        self._running = True

    @property
    def running(self):
        try:
            self._run_lock.lock()
        # FIXME: python3
        #else:
            return self._running
        finally:
            self._run_lock.unlock()

    def run(self):
        error = None

        if self.method == 'fetch':
            trend = self.kwargs['trend']
            channels = _channels_for_trend(self.kwargs['channels'], trend)
            start_end = _start_end_quant(self.kwargs['start_end'], trend)
            try:
                bufs = fetch(channels, start_end)
                if self.running:
                    self.new_data.emit((self.cmd, trend, bufs))
            except RuntimeError as e:
                error = str(e).split('\n')[0]
            # HACK: FIXME: catch TypeError here because of a bug in
            # the client that started around 0.16.3, that is actually
            # exposing a bug in the NDS1 server:
            # https://git.ligo.org/cds/ndscope/issues/109.  Quick
            # successive fetches cause the server to start returning
            # garbage, that shows up as a TypeError in the client
            except TypeError as e:
                error = str(e).split('\n')[0]

        elif self.method == 'iterate':
            trend = self.kwargs['trend']
            channels = _channels_for_trend(self.kwargs['channels'], trend)
            start_end = _start_end_quant(self.kwargs.get('start_end'), trend)
            stride = {
                'raw': nds2.connection.FAST_STRIDE,
                'sec': 1,
                'min': 60,
            }[trend]
            try:
                for bufs in iterate(channels, start_end, stride):
                    if self.running:
                        self.new_data.emit((self.cmd, trend, bufs))
                    else:
                        break
            except RuntimeError as e:
                error = str(e).split('\n')[0]

        elif self.method == 'find_channels':
            try:
                channel_list = find_channels()
                if self.running:
                    self.new_data.emit(channel_list)
            except RuntimeError as e:
                error = str(e).split('\n')[0]

        self.done.emit((self.tid, error))

    def stop(self):
        # disconnect any data connections
        try:
            self.new_data.disconnect()
        except TypeError:
            # diconnect throws a TypeError if there are no connections
            pass
        self._run_lock.lock()
        self._running = False
        self._run_lock.unlock()
