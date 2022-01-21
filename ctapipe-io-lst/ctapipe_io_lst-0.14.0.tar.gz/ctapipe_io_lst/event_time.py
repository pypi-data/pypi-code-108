from collections import deque, defaultdict
import numpy as np

import astropy.version
from astropy.table import Table
from astropy.time import Time, TimeUnixTai, TimeFromEpoch

from ctapipe.core import TelescopeComponent
from ctapipe.core.traits import TelescopeParameter, Path

from traitlets import Enum, Int as _Int, Bool


if astropy.version.major == 4 and astropy.version.minor <= 2 and astropy.version.bugfix <= 0:
    # clear the cache to not depend on import orders
    TimeFromEpoch.__dict__['_epoch']._cache.clear()
    # fix for astropy #11245, epoch was wrong by 8 seconds
    TimeUnixTai.epoch_val = '1970-01-01 00:00:00.0'
    TimeUnixTai.epoch_scale = 'tai'


CENTRAL_MODULE = 132


# fix for https://github.com/ipython/traitlets/issues/637
class Int(_Int):
    def validate(self, obj, value):
        if value is None and self.allow_none is True:
            return value

        return super().validate(obj, value)


def calc_dragon_time(pps_counter, tenMHz_counter, reference_time, reference_counter):
    '''
    Calculate a unix tai timestamp (in ns) from dragon counter values
    and reference time / counter value for a given module index.
    '''
    reference_time = reference_time.astype(np.uint64)
    reference_counter = reference_counter.astype(np.uint64)

    counter = combine_counters(pps_counter, tenMHz_counter)

    if counter > reference_counter:
        delta = counter - reference_counter
        timestamp = reference_time + delta
    else:
        delta = reference_counter - counter
        timestamp = reference_time - delta

    return timestamp


S_TO_NS = np.uint64(1e9)
TEN_MHZ_TO_NS = np.uint64(100)


def combine_counters(pps_counter, tenMHz_counter):
    '''
    Combines the values of pps counter and tenMHz_counter
    and returns the sum in ns.
    '''
    return (
        S_TO_NS * pps_counter.astype(np.uint64)
        + TEN_MHZ_TO_NS * tenMHz_counter.astype(np.uint64)
    )


def read_run_summary(path):
    '''
    Read a run summary file into an astropy table

    Reads run summaries as created by `lstchain_create_run_summary` and
    creates an index on `run_id` so `table.loc[run_id]` returns the correct
    row for a given run id.

    Parameters
    ----------
    path: str or Path
        Path to the night summary file

    Returns
    -------
    table: Table
        astropy table of the run summary file.
    '''
    table = Table.read(str(path))
    table.add_index(['run_id'])
    return table


def time_from_unix_tai_ns(unix_tai_ns):
    '''
    Create an astropy Time instance from a unix time tai timestamp in ns.
    By using both arguments to time, the result will be a higher precision
    timestamp.
    '''
    full_seconds = unix_tai_ns // S_TO_NS
    fractional_seconds = (unix_tai_ns % S_TO_NS) * 1e-9
    return Time(full_seconds, fractional_seconds, format='unix_tai')


def module_id_to_index(expected_module_ids, module_id):
    return np.where(expected_module_ids == module_id)[0][0]


def uint64_diff(a, b):
    '''Calculate the diff of two uint64 numbers without risking underflow'''
    if a > b:
        return (a - b).astype(np.int64)
    else:
        return  -(b - a).astype(np.int64)


class EventTimeCalculator(TelescopeComponent):
    '''
    Class to calculate event times from low-level counter information.

    Also keeps track of "UCTS jumps", where UCTS info goes missing for
    a certain event and all following info has to be shifted.


    There are several sources of timing information in LST raw data.

    Each dragon module has two high precision counters, which however only
    give a relative time.
    Same is true for the TIB.

    The only precise absolute timestamp is the UCTS timestamp.
    However, at least during the commissioning, UCTS was/is not reliable
    enough to only use the UCTS timestamp.

    Instead, we calculate an absolute timestamp by using one valid pair
    of dragon counter / ucts timestamp and then use the relative time elapsed
    from this reference using the dragon counter.

    For runs where no such UCTS reference exists, for example because UCTS
    was completely unavailable, we use the start of run timestamp from the
    camera configuration.
    This will however result in imprecises timestamps off by several seconds.
    These might be good enough for interpolating pointing information but
    are only precise for relative time changes, i.e. not suitable for pulsar
    analysis or matching events with MAGIC.

    Extracting the reference will only work reliably for the first subrun
    for ucts.
    Using svc.date is only possible for the first subrun and will raise an erorr
    if the event id of the first event seen by the time calculator is not 1.
    '''
    timestamp = TelescopeParameter(
        trait=Enum(['ucts', 'dragon']), default_value='dragon',
        help=(
            'Source of the timestamp. UCTS is simplest and most precise,'
            ' unfortunately it is not yet reliable, instead the time is calculated'
            ' by default using the relative dragon board counters with a reference'
            ' pair of counter / time. See the `dragon_reference_time` and'
            ' `dragon_reference_counter` traitlets'
        )
    ).tag(config=True)

    dragon_reference_time = TelescopeParameter(
        Int(allow_none=True),
        default_value=None,
        help='Reference timestamp for the dragon time calculation in ns'
    ).tag(config=True)

    dragon_reference_counter = TelescopeParameter(
        Int(allow_none=True),
        help='Dragon board counter value of a valid ucts/dragon counter combination',
        default_value=None,
    ).tag(config=True)

    dragon_module_id = TelescopeParameter(
        Int(allow_none=True),
        default_value=None,
        help='Module id used to calculate dragon time.',
    ).tag(config=True)

    run_summary_path = TelescopeParameter(
        Path(exists=True, directory_ok=False, allow_none=True),
        default_value=None,
        help=(
            'Path to the run summary for the correct night.'
            ' If given, dragon reference counters are read from this file.'
            ' Explicitly given values override values read from the file.'
        )
    ).tag(config=True)

    extract_reference = Bool(
        default_value=True,
        help=(
            'If true, extract the reference values from the first event.'
            'This will only work for the first file of a run, due to the '
            'UCTS jumps when UCTS is available or because svc.date gives only '
            'the start of the run, not the start of each file (subrun) '
        )
    ).tag(config=True)


    def __init__(self, subarray, run_id, expected_modules_id, config=None, parent=None, **kwargs):
        '''Initialize EventTimeCalculator'''
        super().__init__(subarray=subarray, config=config, parent=parent, **kwargs)

        self.previous_ucts_timestamps = defaultdict(deque)
        self.previous_ucts_trigger_types = defaultdict(deque)

        # we cannot __setitem__ telescope lookup values, so we store them
        # in non-trait private values
        self._has_dragon_reference = {}
        self._dragon_reference_time = {}
        self._dragon_reference_counter = {}
        self._dragon_module_index = {}

        self.detected_jumps = defaultdict(list)

        for tel_id in self.subarray.tel:
            if self.run_summary_path.tel[tel_id] is not None:
                run_summary = read_run_summary(self.run_summary_path.tel[tel_id])
                row = run_summary.loc[run_id]
                self._has_dragon_reference[tel_id] = True
                self._dragon_reference_time[tel_id] = np.uint64(row['dragon_reference_time'])
                self._dragon_reference_counter[tel_id] = np.uint64(row['dragon_reference_counter'])
                self._dragon_module_index[tel_id] = row['dragon_reference_module_index']

                if row['dragon_reference_source'] == 'run_start':
                    self.log.warning(
                        'Dragon reference source is run_start, '
                        'times will be imprecise by several seconds'
                    )

            else:
                self._has_dragon_reference[tel_id] = (
                    self.dragon_reference_time.tel[tel_id] is not None
                    and self.dragon_reference_counter.tel[tel_id] is not None
                    and self.dragon_module_id.tel[tel_id] is not None
                )

            if not self._has_dragon_reference[tel_id] and not self.extract_reference:
                raise ValueError('No dragon reference values given and extract_reference=False')

            # set values from traitlets, overrides values from files if both given
            if self.dragon_reference_counter.tel[tel_id] is not None:
                self._dragon_reference_counter[tel_id] = np.uint64(self.dragon_reference_counter.tel[tel_id])

            if self.dragon_reference_time.tel[tel_id] is not None:
                self._dragon_reference_time[tel_id] = np.uint64(self.dragon_reference_time.tel[tel_id])

            if self.dragon_module_id.tel[tel_id] is not None:
                module_id = self.dragon_module_id.tel[tel_id]
                module_index = module_id_to_index(expected_modules_id, module_id)
                self._dragon_module_index[tel_id] = module_index

    def __call__(self, tel_id, event):
        lst = event.lst.tel[tel_id]
        ucts_available = bool(lst.evt.extdevices_presence & 2)
        ucts_timestamp = lst.evt.ucts_timestamp

        # first event and values not passed
        if self.extract_reference and not self._has_dragon_reference[tel_id]:
            # use first working module if none is specified
            if tel_id not in self._dragon_module_index:
                self._dragon_module_index[tel_id] = np.where(
                    lst.evt.module_status != 0
                )[0][0]

            module_index = self._dragon_module_index[tel_id]

            self._dragon_reference_counter[tel_id] = combine_counters(
                lst.evt.pps_counter[module_index],
                lst.evt.tenMHz_counter[module_index]
            )
            if not ucts_available:
                source = 'svc.date'
                if event.index.event_id != 1:
                    raise ValueError(
                        'Can only use run start timestamp'
                        ' as reference for the first subrun'
                    )
                self.log.warning(
                    f'Cannot calculate a precise timestamp for obs_id={event.index.obs_id}'
                    f', tel_id={tel_id}. UCTS unavailable.'
                )
                # convert runstart from UTC to tai
                run_start = Time(lst.svc.date, format='unix')
                self._dragon_reference_time[tel_id] = np.uint64(S_TO_NS * run_start.unix_tai)
            else:
                source = 'ucts'
                self._dragon_reference_time[tel_id] = ucts_timestamp
                if event.index.event_id != 1:
                    self.log.warning(
                        'Calculating time reference values not from first event.'
                        ' This might result in wrong timestamps due to UCTS jumps'
                    )

            self.log.critical(
                f'Using event {event.index.event_id} as time reference for dragon.'
                f' timestamp: {self._dragon_reference_time[tel_id]} from {source}'
                f' counter: {self._dragon_reference_counter[tel_id]}'
            )

            self._has_dragon_reference[tel_id] = True

        # Dragon timestamp based on the reference timestamp
        module_index = self._dragon_module_index[tel_id]
        dragon_timestamp = calc_dragon_time(
            pps_counter=lst.evt.pps_counter[module_index],
            tenMHz_counter=lst.evt.tenMHz_counter[module_index],
            reference_time=self._dragon_reference_time[tel_id],
            reference_counter=self._dragon_reference_counter[tel_id],
        )

        # if ucts is not available, there is nothing more we have to do
        # and dragon time is our only option
        if not ucts_available:
            return time_from_unix_tai_ns(dragon_timestamp)

        # Due to a DAQ bug, sometimes there are 'jumps' in the
        # UCTS info in the raw files. After one such jump,
        # all the UCTS info attached to an event actually
        # corresponds to the next event. This one-event
        # shift stays like that until there is another jump
        # (then it becomes a 2-event shift and so on). We will
        # keep track of those jumps, by storing the UCTS info
        # of the previously read events in the list
        # previous_ucts_time_unix. The list has one element
        # for each of the jumps, so if there has been just
        # one jump we have the UCTS info of the previous
        # event only (which truly corresponds to the
        # current event). If there have been n jumps, we keep
        # the past n events. The info to be used for
        # the current event is always the first element of
        # the array, previous_ucts_time_unix[0], whereas the
        # current event's (wrong) ucts info is placed last in
        # the array. Each time the first array element is
        # used, it is removed and the rest move up in the
        # list. We have another similar array for the trigger
        # types, previous_ucts_trigger_type
        ucts_trigger_type = lst.evt.ucts_trigger_type

        if len(self.previous_ucts_timestamps[tel_id]) > 0:
            # put the current values last in the queue, for later use:
            self.previous_ucts_timestamps[tel_id].append(ucts_timestamp)
            self.previous_ucts_trigger_types[tel_id].append(ucts_trigger_type)

            # get the correct time for the current event from the queue
            ucts_timestamp = self.previous_ucts_timestamps[tel_id].popleft()
            ucts_trigger_type = self.previous_ucts_trigger_types[tel_id].popleft()

            lst.evt.ucts_trigger_type = ucts_trigger_type
            lst.evt.ucts_timestamp = ucts_timestamp

        # Now check consistency of UCTS and Dragon times. If
        # UCTS time is ahead of Dragon time by more than
        # 1 us, most likely the UCTS info has been
        # lost for this event (i.e. there has been another
        # 'jump' of those described above), and the one we have
        # actually corresponds to the next event. So we put it
        # back first in the list, to assign it to the next
        # event. We also move the other elements down in the
        # list,  which will now be one element longer.
        # We leave the current event with the same time,
        # which will be approximately correct (depending on
        # event rate), and set its ucts_trigger_type to -1,
        # which will tell us a jump happened and hence this
        # event does not have proper UCTS info.
        delta = uint64_diff(ucts_timestamp, dragon_timestamp)
        if delta < -1e3:
            self.log.warning(
                f'Found dragon time much ahead of ucts time in event {event.index.event_id}'
                f', dragon time: {dragon_timestamp:d}'
                f', ucts time: {ucts_timestamp:d}'
                f', delta: {delta / 1000:.0f} µs'
            )

        if delta > 1e3:
            self.log.warning(
                f'Found UCTS jump in event {event.index.event_id}'
                f', dragon time: {dragon_timestamp:d}'
                f', ucts time: {ucts_timestamp:d}'
                f', delta: {delta / 1000:.0f} µs'
            )
            self.previous_ucts_timestamps[tel_id].appendleft(ucts_timestamp)
            self.previous_ucts_trigger_types[tel_id].appendleft(ucts_trigger_type)
            self.detected_jumps[tel_id].append((event.count, event.index.event_id, delta))
            lst.evt.ucts_jump = True

            # fall back to dragon time / tib trigger
            lst.evt.ucts_timestamp = dragon_timestamp
            ucts_timestamp = dragon_timestamp

            tib_available = lst.evt.extdevices_presence & 1
            if tib_available:
                lst.evt.ucts_trigger_type = lst.evt.tib_masked_trigger
            else:
                self.log.warning(
                    'Detected ucts jump but not tib trigger info available'
                    ', event will have no trigger information'
                )
                lst.evt.ucts_trigger_type = 0

        # Select the timestamps to be used for pointing interpolation
        if self.timestamp.tel[tel_id] == "dragon":
            return time_from_unix_tai_ns(dragon_timestamp)

        return time_from_unix_tai_ns(ucts_timestamp)
