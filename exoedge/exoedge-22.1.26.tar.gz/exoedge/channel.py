# -*- coding: utf-8 -*-
# pylint: disable=C0103,R0902,W1202
"""
Module to generate data from arbitrary source modules as defined in config_io.
"""
import sys
import time
import json
import threading
import inspect
from exoedge import get_thread_by_name
from exoedge import logger
from exoedge.namespaces import ChannelNamespace
from exoedge.sources import ExoEdgeSource
from murano_client.client import WatchQueue, StoppableThread

LOG = logger.getLogger(__name__)


class Channel(ChannelNamespace, object):
    """
    A Channel creates Signal data for ExoSense.

    This class provides methods to get new data from a source specified in
    config_io.
    """
    def __init__(self, **kwargs):
        """
            Channel initialized and started by
            config_io.ConfigIO.add_channel()
        """
        LOG.debug("Channel kwargs: {}".format(kwargs))
        if kwargs.get('__no_derived__'):
            kwargs['__ns_no_defaults__'] = True
            kwargs.pop('__no_derived__')
        ChannelNamespace.__init__(self, **kwargs)

        # DERIVED
        if not kwargs.get('__ns_no_defaults__'):
            self.downsampler = DownSampler(self.protocol_config.down_sample) # pylint: disable=E1101
            self.ROCH = ReportOnChangeHandler(
                self.protocol_config.report_on_change,  # pylint: disable=E1101
                tolerance=self.protocol_config.report_on_change_tolerance) # pylint: disable=E1101
        elif '__ns_no_defaults__' in kwargs:
            kwargs.pop('__ns_no_defaults__')
        self.last_value = None
        self.last_report_time = 0
        self.last_sample = 0
        self.q_out = WatchQueue()
        self.q_error_out = WatchQueue()
        self.callback_timer = None
        self.source = None
        LOG.info("Channel YAML:\n{}".format(self.to_yaml()))

    def is_sample_time(self, blocking=False):
        """ Sleep for the sample rate

        # FEATURE_IMPLEMENTATION: sample_rate
        """
        sr = self.protocol_config.sample_rate / 1000.0 # pylint: disable=E1101
        if blocking:
            time.sleep(sr)
        diff = time.time() - self.last_sample
        is_sample_time = diff >= sr
        return is_sample_time

    def is_report_time(self):
        """
            Determine whether or not it is time to send queued channel data.
        """
        now = time.time()
        should_report_by = self.last_report_time + self.protocol_config.report_rate / 1000.0 # pylint: disable=E1101
        if now >= should_report_by: # pylint: disable=E1101
            return True
        return False

    def set_report_stats(self, last_value, last_report_time):
        """
            Update channel stats last_value and last_report_time.
        """
        LOG.debug(
            "stats ({}): {}, {}"
            .format(self.name, last_value, last_report_time) # pylint: disable=E1101
        )
        self.last_value = last_value
        self.last_report_time = last_report_time

    def put_sample(self, sample, timestamp=None):
        """ Place data in queue.

        In the future, this method will be switchable and optionally send
        data to gmq or SQL database, e.g. send_data_to_gmq(data)

        Parameters:
        sample:           Datapoint to be placed in queue.
        """
        LOG.info(
            "putting sample({}): {}"
            .format(self.name, sample) # pylint: disable=E1101
        )
        sample_obj = Sample(
            sample,
            gain=self.protocol_config.multiplier, # pylint: disable=E1101
            offset=self.protocol_config.offset, # pylint: disable=E1101
            timestamp=timestamp)
        self.q_out.put(sample_obj)
        self.last_sample = sample_obj.timestamp

    def put_channel_error(self, error):
        """
            Helper method for sending data on the __error channel.
        """
        LOG.info(
            "putting error: {}"
            .format(error)
        )
        self.q_error_out.put(str(error))
        self.last_sample = time.time()


class DataOutChannel(Channel):
    """
        Class for processing command and control from ExoSense
        via the data_out resource.

        The differences between a DataOutChannel and a Channel are:

         - it is never sample time
         - it is always report time
         - the `execute()` function is only implemented

        on a DataOutChannel.
    """
    resource = 'data_out'
    def __init__(self, **kwargs):
        LOG.critical("DataOutChannel kwargs: {}".format(kwargs))
        Channel.__init__(self, **kwargs)

    def execute(self, data_out_value):
        LOG.critical(
            "Channel {} executing data_out with payload: {} - source {}"
            .format(self.name, data_out_value, self.source)
        )

        if self.source:
            self.source.put_data_out(self, data_out_value)
        else:
            LOG.critical(
                "Cannot execute data_out on channel source: {}"
                .format(self.source)
            )

class Sample(tuple):
    """ Class to attach a timestamp to new data that is generated """
    def __new__(cls, data, **kwargs):
        """ Subclasses tuple. (timestamp, data) """
        timestamp = kwargs.get('timestamp') or time.time()
        offset = kwargs.get('offset')
        gain = kwargs.get('gain')
        if not isinstance(data, bool):
            try:
                data = data * gain + offset
            except TypeError:
                data = data
            # Attempt to JSON serialize the data point. If not
            # serializable, force into string.
            try:
                LOG.debug("data (json): {}".format(json.dumps(data)))
            except TypeError:
                data = str(data)
        else:
            # support bool-type data
            data = data
        new = tuple.__new__(Sample, (timestamp, data))
        setattr(new, 'timestamp' , timestamp)
        setattr(new, 'data' , data)
        LOG.debug("created new sample: {}".format(new))
        return new

    def age(self):
        """ Return age of data point in seconds """
        return time.time() - self.timestamp


class DownSampler(object):
    """
        Class to deal with down sampling Channel data

        Methods:
            max:            Maximum value in list
            min:            Minimum value in list
            sum:            Sum of values in list
            avg:            Average of values in list
            act:            Last value in list ("actual value")

        Time:
            Regardless of the downsample method
            chosen, the timestamp that will be reported
            to Murano will be the timestamp of the latest
            sample in the list provided to the
            `down_sample(data_list)` method.

            This is done because users can specify their
            own timestamps for each sample via the
            `channel.put_sample(<sample>, timestamp=<user_defined>)`
            method.

    """
    method_mapper = {
        'max': max,
        'min': min,
        'sum': sum,
        'avg': lambda ls: float(sum(ls))/len(ls),
        'act': lambda ls: ls    # No change
    }

    def __init__(self, method):
        """
        Initialized by Channel.__init__()
        """
        # TODO: remove this method check once THEMVE-2944 is fixed.
        if method == 'actual':
            method = 'ACT'
        self.method = method.lower()
        self._fn = self.method_mapper.get(self.method)
        if self._fn is None:
            LOG.critical("Couldn't map method: {}, using default: ACT".format(method))
            self._fn = self.method_mapper.get('act')

    def __repr__(self):
        return '<{}: {}>'.format(self.method, self._fn)

    def down_sample(self, channel_dq):
        """ Down sample data in the list provided.

            Assume data is list of tuples.
             - e.g. [(ts, val), (ts, val), ...]
        """
        # Create iterable copy of channel.q_out.queue contents
        data_list = list(channel_dq)

        # Clear the current queue to avoid re-processing or discarding new entries
        channel_dq.clear()
        LOG.debug(
            'Performing downsample {} on {}'
            .format(self.method, data_list)
        )

        ds_dq = []
        if self.method == 'act':
            ds_dq.extend(self._fn(data_list))
        else:
            ds_dq.append(Sample(
                self._fn([d[1] for d in data_list]),
                timestamp=data_list[-1][0]
            ))

        return ds_dq


class ReportOnChangeHandler(object):
    def __init__(self, roc, tolerance=None):
        self.roc = roc
        self.tolerance = tolerance

    def __repr__(self):
        return '<{}: {}>'.format(self.roc, self.tolerance)

    def filter_data(self, latest_samples, last):
        filtered_samples = []
        latest_ts = 0
        if self.roc and last is not None:
            # Check each sample for a changed[-enough] value
            for new_sample in latest_samples:
                if self.tolerance:
                    LOG.info(
                        "Validating whether {} <= {} <= {}..."
                        .format(
                            last - self.tolerance,
                            new_sample.data,
                            last + self.tolerance)
                    )
                    if (last - self.tolerance) <= new_sample.data <= (last + self.tolerance):
                        LOG.info("Within range; not reporting.")
                    else:
                        LOG.info("Tolerance breached; adding to report list.")
                        filtered_samples.append(new_sample)
                        last = new_sample.data
                elif last != new_sample.data:
                    LOG.info("Changed value; adding to report list.")
                    filtered_samples.append(new_sample)
                    last = new_sample.data
                latest_ts = new_sample.timestamp

        # No change(s)?
        if not filtered_samples:
            return [Sample(None, timestamp=latest_ts)]

        return filtered_samples

