import logging
import traceback
import collections

import numpy as np
from qtpy import QtCore
from qtpy.QtCore import Signal, Slot

from gpstime import gpsnow

from . import const
from . import nds


logger = logging.getLogger('DATA ')


def _ctype_map(ctype):
    return {
        'online': 'raw',
        'raw': 'raw',
        'reduced': 'raw',
        's-trend': 'sec',
        'm-trend': 'min',
    }.get(ctype, 'raw')


class DataBuffer(object):
    """data storage

    The data attribute here is actually a dict of sub-data arrays all
    with the same meta-data.  For trend data the keys should be
    ['mean', 'min', 'max'], and for full they would just be ['raw'].

    """

    __slots__ = [
        '__weakref__',
        'channel', 'ctype', 'sample_rate',
        'trend', 'unit',
        'data', 'size', 'gps_start', 'tarray',
        'max_samples', 'lookback',
        'last_append_len',
    ]

    def __init__(self, buf):
        """initialize with NDS-like Buffer object"""
        self.channel, mod, self.ctype = nds.parse_channel(buf.channel)
        self.trend = _ctype_map(self.ctype)
        # HACK: fix m-trend sample rate.  The rate returned from NDS
        # is not accurate, seemingly subject to round-off error:
        # https://git.ligo.org/nds/nds2-distributed-server/issues/1
        # hopefully this should be fixed.  but in general we are
        # subject to round-off accumulation error in here as well (see
        # self.tlen())
        if self.trend == 'min':
            self.sample_rate = 1.0/60.0
        else:
            self.sample_rate = buf.channel.sample_rate
        self.unit = buf.channel.Units()
        self.data = {}
        self.data[mod] = buf.data
        self.gps_start = buf.gps_seconds + buf.gps_nanoseconds*1e-9
        self.update_tarray()
        #self.max_samples = int(const.DATA_LOOKBACK_LIMIT_BYTES / buf.channel.DataTypeSize())
        self.max_samples = int(const.TREND_MAX_SECONDS[self.trend] * self.sample_rate)
        self.lookback = 2
        self.last_append_len = 0

    def __repr__(self):
        return "<DataBuffer {} {}, {} Hz, [{}, {})>".format(
            self.channel, self.trend, self.sample_rate, self.gps_start, self.gps_end)

    def __len__(self):
        # FIXME: this is a hack way of doing this, and probably
        # doesn't perform well
        return list(self.data.values())[0].size

    def __getitem__(self, mod):
        return self.data[mod]

    def __contains__(self, mod):
        return mod in self.data

    def keys(self):
        return self.data.keys()

    def values(self):
        return self.data.values()

    def items(self):
        return self.data.items()

    @property
    def is_trend(self):
        return self.trend in ['sec', 'min']

    @property
    def step(self):
        return 1./self.sample_rate

    @property
    def tlen(self):
        """time length of buffer in seconds"""
        # FIXME: this, and consequently gps_end is subject to
        # round-off accumulation error.  Should have better way to
        # calculate time array and gps_end time.
        return len(self) * self.step

    def update_tarray(self):
        # FIXME: see self.tlen()
        self.tarray = np.arange(len(self)) * self.step + self.gps_start

    @property
    def gps_end(self):
        return self.gps_start + self.tlen

    @property
    def range(self):
        return self.gps_start, self.gps_end

    @property
    def span(self):
        return self.gps_end - self.gps_start

    def extend(self, buf):
        """extend buffer to right"""
        assert buf.channel == self.channel
        assert buf.sample_rate == self.sample_rate, "extend buffer sample rate {} does not match {}".format(buf.sample_rate, self.sample_rate)
        assert buf.gps_start <= self.gps_end, "extend buffer start {} is greater than end {}".format(buf.gps_start, self.gps_end)
        ind = np.where(buf.tarray >= self.gps_end)[0]
        for mod, data in self.data.items():
            self.data[mod] = np.append(data, buf.data[mod][ind])
        self.update_tarray()

    def extendleft(self, buf):
        """extend buffer to left"""
        assert buf.channel == self.channel
        assert buf.sample_rate == self.sample_rate, "extendleft buffer sample rate {} does not match {}".format(buf.sample_rate, self.sample_rate)
        assert buf.gps_end >= self.gps_start, "extendleft buffer end {} is less than start {}".format(buf.gps_end, self.gps_start)
        ind = np.where(buf.tarray < self.gps_start)[0]
        for mod, data in self.data.items():
            self.data[mod] = np.append(buf.data[mod][ind], data)
        self.gps_start = buf.gps_start
        self.update_tarray()

    def append(self, buf):
        """append data to the right, keeping overall time span"""
        assert buf.channel == self.channel
        assert buf.sample_rate == self.sample_rate, "append buffer sample rate {} does not match {}".format(buf.sample_rate, self.sample_rate)
        assert buf.gps_start == self.gps_end, "append buffer start {} does not equal end {}".format(buf.gps_start, self.gps_end)
        lbs = min(int(self.lookback * self.sample_rate), self.max_samples)
        for mod, data in self.data.items():
            self.data[mod] = np.append(data, buf.data[mod])[-lbs:]
        self.gps_start = max(
            self.gps_start,
            buf.gps_end - lbs*self.step,
        )
        self.update_tarray()
        self.last_append_len = min(len(buf), len(self)) + 1

    def last_append(self):
        """Return (t, y) data of last append"""
        if 'raw' in self.data.keys():
            mod = 'raw'
        else:
            mod = 'mean'
        t = self.tarray[-self.last_append_len:]
        y = self.data[mod][-self.last_append_len:]
        return (t, y)


class DataBufferDict(object):
    """

    Takes NDS-like Buffer list at initialization and organizes the
    included data into a dictionary of DataBuffer objects keyd by
    channel.  various trend channels are kept together in the same
    DataBuffer.

    """
    __slots__ = [
        '__weakref__',
        'buffers', 'gps_start', 'gps_end',
    ]

    def __init__(self, nds_buffers):
        self.buffers = {}
        # buffer lists should have unique channel,ctype,mod combos
        for buf in nds_buffers:
            db = DataBuffer(buf)
            chan = db.channel
            if chan in self.buffers:
                for m, d in db.data.items():
                    self.buffers[chan].data[m] = d
            else:
                self.buffers[chan] = db

    def __repr__(self):
        return "<DataBufferDict {}>".format(
            list(self.buffers.values()))

    def __getitem__(self, channel):
        return self.buffers[channel]

    def __contains__(self, channel):
        return channel in self.buffers

    def items(self):
        return self.buffers.items()

    def values(self):
        return self.buffers.values()

    @property
    def is_trend(self):
        return list(self.buffers.values())[0] in ['s-trend', 'm-trend']

    @property
    def range(self):
        # FIXME: pulling the span from a random channel is not good,
        # since there's no real guarantee that the channels all share
        # the same span.
        return list(self.buffers.values())[0].range

    def extendleft(self, bufs):
        for chan, buf in bufs.items():
            self.buffers[chan].extendleft(buf)

    def extend(self, bufs):
        for chan, buf in bufs.items():
            if chan in self.buffers:
                self.buffers[chan].extend(buf)
            else:
                self.buffers[chan] = buf

    def append(self, bufs):
        for chan, buf in bufs.items():
            self.buffers[chan].append(buf)

    def set_lookback(self, lookback):
        for buf in self.values():
            buf.lookback = lookback


class DataStore(QtCore.QObject):
    # signals
    #
    # channel list read
    signal_channel_list_ready = Signal()
    # channel add/remove attempt
    # payload: (channel, error or None)
    signal_channel_add = Signal('PyQt_PyObject')
    signal_channel_remove = Signal('PyQt_PyObject')
    # network data retrieval has started
    # payload: message string
    signal_data_online_start = Signal(str)
    signal_data_retrieve_start = Signal(str)
    # network data retrieval has completed
    # payload: tuple of
    #   error string
    #   active thread bool
    signal_data_online_done = Signal('PyQt_PyObject')
    signal_data_retrieve_done = Signal('PyQt_PyObject')
    # data buffer in response to data request
    # payload: tuple of
    #   trend type string
    #   trend data buffer
    signal_data = Signal('PyQt_PyObject')

    TREND_TYPES = ['raw', 'sec', 'min']

    def __init__(self):
        super().__init__()
        # use a counter to hold references to the channels, so that as
        # many channel references as needed can be added, while only
        # storing one set of channel data
        self._channels = collections.Counter()
        self.last_trend = None
        self.last_start_end = None
        self.restart_requested = False
        self.threads = {}
        self.reset()
        self.set_lookback(2)
        self.available_channels = None
        # sets up call to fetch channel list once the main loop starts
        QtCore.QTimer.singleShot(0, self.fetch_channel_list_async)
        logger.debug("data store initialized")

    def __getitem__(self, mod):
        return self.db[mod]

    def set_lookback(self, lookback):
        self.lookback = lookback
        for bd in self.db.values():
            if bd:
                bd.set_lookback(lookback)

    ##########

    def _emit_data(self, trend, online=False):
        if trend is None:
            self.signal_data.emit((None, None, online))
        elif self.db[trend]:
            self.signal_data.emit((self.db[trend], trend, online))

    ##########

    def fetch_channel_list_async(self):
        if self.available_channels:
            return
        self.remote_cmd('find_channels')

    def add_channel(self, channel):
        if self.available_channels and channel not in self.available_channels:
            error = f"Channel '{channel}' not found in channel list."
            self.signal_channel_add.emit((channel, error))
            raise ValueError(error)
        elif const.CHANNEL_RE.match(channel) is None:
            error = f"Invalid channel name: {channel}"
            self.signal_channel_add.emit((channel, error))
            raise ValueError(error)
        self._channels[channel] += 1
        assert self._channels[channel] > 0
        self.signal_channel_add.emit((channel, None))
        logger.debug('CHANNEL {} {}'.format(channel, self._channels[channel]))
        # if we already had reference to this channel emit
        if self.last_trend and self._channels[channel] > 1:
            self._emit_data(self.last_trend)
        # FIXME: need to handle other online trend types
        elif self.online:
            self.online_restart()
        # else fill in missing data
        else:
            for trend in self.TREND_TYPES:
                if not self.db[trend]:
                    continue
                self.remote_cmd(
                    'extend',
                    trend=trend,
                    channels=[channel],
                    start_end=self.db[trend].range,
                )

    def remove_channel(self, channel):
        self._channels[channel] -= 1
        assert self._channels[channel] >= 0
        self.signal_channel_remove.emit((channel, None))
        # FIXME: remove channel data from self.db
        logger.debug('CHANNEL {} {}'.format(channel, self._channels[channel]))
        if self.online:
            self.online_restart()

    @property
    def channels(self):
        """list of all channels in the store"""
        # the "+ Counter()" is a way to exclude elements with less
        # than zero referrents (even though we should never hold a
        # channel with zero referents)
        return list(self._channels + collections.Counter())

    @property
    def empty(self):
        """True if there are no channels in the store"""
        return len(self.channels) == 0

    ##########

    def reset(self):
        """reset the data store (clear all data)"""
        logger.debug("RESET")
        self.db = {k: None for k in self.TREND_TYPES}
        self._emit_data(None)

    def online_start(self, trend, lookback):
        """start online stream"""
        # no support for min trends, see below
        if trend == 'min':
            trend = 'sec'
        logger.debug('START ONLINE')
        self.last_trend = trend
        self.set_lookback(lookback)
        self.stop()
        self.reset()
        self.signal_data.connect(self._online_backfill)
        self.remote_cmd('online', trend=trend, channels=self.channels)

    def _online_backfill(self, recv):
        """backfill data on online start"""
        bufs, trend, online = recv
        if not trend:
            return
        self.signal_data.disconnect(self._online_backfill)
        start, end = self.db[trend].range
        start -= self.lookback
        self.remote_cmd('extendleft', trend=trend, channels=self.channels, start_end=(start, end))

    def online_stop(self):
        """stop online stream"""
        thread = self.threads.get('online')
        if thread:
            thread.stop()

    def online_restart(self):
        """restart online stream

        Will stop the stream if there are no channels referents.

        """
        if self.restart_requested:
            return
        if not self.empty:
            logger.debug('RESTART')
            self.restart_requested = True
            self.signal_data_online_done.connect(self._restart)
        self.online_stop()

    def _restart(self):
        logger.debug('_RESTART')
        self.signal_data_online_done.disconnect(self._restart)
        self.online_start(self.last_trend, self.lookback)
        self.restart_requested = False

    def _min_stop_request(self):
        self.signal_data_online_done.disconnect(self._min_stop_request)
        self.request(self.last_trend, self.last_start_end)

    def request(self, trend, start_end):
        """Request data

        promptly emits signal_data with all on-hand data for trend,
        then triggers remote requests to fill in what is missing.

        `trend` should be one of ['raw', 'sec', 'min'], and
        `start_end` should be a tuple of (start, end) times.

        """
        logger.debug("REQUEST: {} {}".format(trend, start_end))

        assert trend in self.TREND_TYPES
        self.last_trend = trend
        start, end = start_end
        assert end > start

        # FIXME: we really need to do something to put a check on the
        # length of the request.  It really should be based on the
        # bytes being requested, but we don't know the sample rate a
        # priori.
        span = abs(end - start)
        max_seconds = const.TREND_MAX_SECONDS[trend]
        if span > max_seconds:
            self.signal_data_retrieve_done.emit((
                f"Requested span too large: {max_seconds} seconds max for {trend} trend",
                self.active()
            ))
            return

        now = gpsnow()

        if self.online:
            if trend == 'min':
                # no support for min trends.  the iteration time is
                # too slow, until we have a way to forcibly
                # terminating threads
                self.last_start_end = start_end
                self.signal_data_online_done.connect(self._min_stop_request)
                self.online_stop()
                return
            elif trend != self.online:
                self.online_restart()
                return
            # note we continue if online and trend is not changing
            self.set_lookback(abs(now - start))

        # expand range to ints
        rstart = int(start)
        rend = int(np.ceil(end))

        if rstart > now:
            # self.signal_data_retrieve_done.emit("Requested start time in the future.")
            return

        # add padding
        pad = int((rend - rstart) * const.DATA_SPAN_PADDING)
        rstart -= pad
        rend += pad

        # FIXME: this is to prevent requesting data from the future.
        # The -10 is because the NDS servers don't cover the first few
        # seconds of online data, which should be fixed in the
        # servers.
        if not self.online:
            rend = min(rend, now - 1)

        if rend <= rstart:
            return

        # if the requested trend is empty, just get full span
        if self.db[trend] is None:
            self.remote_cmd('extend', trend=trend, channels=self.channels, start_end=(rstart, rend))
            return

        # get current start/end times, adjusting inward to make sure
        # we account for non-second aligned data due to 16Hz online
        dstart, dend = self.db[trend].range
        dstart = int(np.ceil(dstart))
        dend = int(dend)

        # if the requrest is fully for a discontiguous range then
        # clear the cache and make a request for fresh data
        if rstart >= dend or rend < dstart:
            logger.log(5, "CLEAR: {}".format(trend))
            self.db[trend] = None
            self.remote_cmd('extend', trend=trend, channels=self.channels, start_end=(rstart, rend))
            return

        # emit what data we have (in case the caller is requesting
        # a trend change), and will emit more below if it turns
        # out we need to extend the range
        #self.signal_data.emit(self.db[trend])
        self._emit_data(trend)

        if rstart < dstart:
            self.remote_cmd('extendleft', trend=trend, channels=self.channels, start_end=(rstart, dstart))

        if dend < rend:
            self.remote_cmd('extend', trend=trend, channels=self.channels, start_end=(dend, rend))

    ##########

    def _command_description(self, cmd, trend):
        if cmd == 'online':
            desc = 'online '
        else:
            desc = ''
        if trend == 'sec':
            desc += "second trend data"
        elif trend == 'min':
            desc += "minute trend data"
        elif trend == 'raw':
            desc += "raw data"
        return desc

    def remote_cmd(self, cmd, **kwargs):
        # the thread ID (tid) is used as a kind of primitive lock.
        # the ID should be unique enough to block requests from
        # similar trend/action combos.
        if cmd == 'find_channels':
            tid = 'find_channels'
            desc = "channel list"
            recv_cmd = self.remote_recv_channels
        elif cmd == 'online':
            if not kwargs.get('channels'):
                return
            trend = kwargs['trend']
            tid = 'online'
            desc = self._command_description(cmd, trend)
            recv_cmd = self.remote_recv_data
        else:
            if not kwargs.get('channels'):
                return
            trend = kwargs['trend']
            tid = f'{cmd}-{trend}'
            desc = self._command_description(cmd, trend)
            recv_cmd = self.remote_recv_data

        logger.debug(f"CMD: {cmd} {kwargs}")
        if self.active(tid):
            logger.debug("BUSY: {}".format(tid))
            return
        if self.online and cmd == 'extend':
            logger.debug("BUSY: no extend while online")
            return

        msg = f"Retrieving {desc}..."
        if cmd == 'online':
            self.signal_data_online_start.emit(msg)
        self.signal_data_retrieve_start.emit(msg)

        t = nds.NDSThread(tid, cmd, **kwargs)
        self.threads[tid] = t
        t.new_data.connect(recv_cmd)
        t.done.connect(self.remote_done)
        t.start()

    @Slot('PyQt_PyObject')
    def remote_recv_channels(self, channels):
        nchannels = len(channels)
        logger.info(f'channel list received: {nchannels} channels')
        self.available_channels = channels
        self.signal_channel_list_ready.emit()

    @Slot('PyQt_PyObject')
    def remote_recv_data(self, recv):
        logger.log(5, "")
        logger.log(5, f"RECV: {recv}")
        cmd, trend, buffers = recv
        # FIXME: should the NDS object just return this directly?
        dbd = DataBufferDict(buffers)
        dbd.set_lookback(self.lookback)
        if not self.db.get(trend):
            self.db[trend] = dbd
        elif cmd == 'online':
            self.db[trend].append(dbd)
        elif cmd == 'extendleft':
            try:
                self.db[trend].extendleft(dbd)
            except AssertionError:
                # FIXME: this is a hack to get around the fact that
                # left extension during online (which comes about
                # during zoom out, or during pan/zoom right after
                # stop) will sometimes fail if the left end falls off
                # the lookback while waiting for tid "left" to return.
                # Maybe this is the best thing to do here, but it
                # seems inelegant.  We have no guarantee when the left
                # extend will return, though, and during online
                # appends keep happening, so maybe even if we can be
                # more clever to avoid unnecessary left extend calls
                # that are likely to fail, we probably still want to
                # catch this error during online mode.
                logger.info(traceback.format_exc(0))
        elif cmd == 'extend':
            self.db[trend].extend(dbd)
        self._emit_data(trend, online=cmd=='online')

    @Slot('PyQt_PyObject')
    def remote_done(self, recv):
        logger.debug(f"DONE: {recv}")
        tid, error = recv
        if error:
            error = f"NDS error ({tid}): {error}"
            logger.warning(error)
        signal = (error, self.active())
        if tid == 'online':
            self.signal_data_online_done.emit(signal)
        self.signal_data_retrieve_done.emit(signal)

    def active(self, tid=None):
        """data retrieval activity status of store

        Returns True or False depending on if the specified thread is
        active, or if any thread is active if none specified.

        """
        if tid:
            thread = self.threads.get(tid)
            if not thread:
                return False
            return not thread.isFinished()
        for thread in self.threads.values():
            if not thread.isFinished():
                return True
        return False

    @property
    def online(self):
        """online status of store

        If online active returns the trend of online retrieval,
        otherwise returns False.

        """
        thread = self.threads.get('online')
        if not thread:
            return False
        if thread.isFinished():
            return False
        return thread.kwargs['trend']

    def stop(self):
        logger.debug("STOP")
        # stop data retrieval threads but not the find_channels
        for name, thread in self.threads.items():
            if name == 'find_channels':
                continue
            thread.stop()
            # FIXME: thread terminate is causing problems on SL7
            # thread.terminate()
