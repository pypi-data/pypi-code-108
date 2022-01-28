"""
Library for useful python functions for acquiring data via nds2,
and for taking power spectral densities and transfer functions.

To be able to acquire LIGO data, users must run:

$ kinit albert.einstein@LIGO.ORG

Craig Cahillane
Nov 3, 2019
"""

import copy
import os
import pickle
import sys
import time

import nds2
import numpy as np
import scipy.constants as scc
import scipy.signal as sig
from scipy.optimize import fsolve

"""Functions"""
# dB conversions
def dB2Mag(dBnum):
    """Takes in number in dB, returns magnitude = 10^(dB/20)"""
    return 10 ** (dBnum / 20.0)


def mag2dB(magNum):
    """Takes in number in magnitude, returns in dB = 20*log10(mag)"""
    return 20.0 * np.log10(magNum)


# Complex Algebra
def QMag2ComplexPoles(Q, f0):
    """Takes in Q and f0 (center frequency in Hz) and returns a complex pole pair"""
    f0_2 = f0 ** 2
    real = 0.5 / Q
    imag = np.sqrt(f0_2 - real ** 2)
    poles = np.array([real + 1j * imag, real - 1j * imag])
    return poles


# Plotting convenience
def good_ticks(axis):
    """Finds the plot range, and sets the y ticks to always by factors of 10 on the y scale"""
    ymin, ymax = axis.get_ylim()
    yTicks = np.array(
        [10 ** x for x in np.arange(np.ceil(np.log10(ymin)), np.ceil(np.log10(ymax)))]
    )
    return yTicks


### .pkl file save and load
def save_pickle(dataDict, savefile):
    """Saves a .pkl file from the dataDict input at savefile."""
    with open(savefile, "wb") as outfile:
        pickle.dump(dataDict, outfile)
    return


def load_pickle(savefile):
    """Load a pickle file."""
    with open(savefile, "rb") as infile:
        dataDict = pickle.load(infile)
    return dataDict


# FFT parameters
def dtt_time(averages, bandwidth, overlap, verbose=False):
    """
    Takes in number of averages, bandwidth, overlap of a FFT.
    Returns and prints the amount of data time in seconds the FFT will need.
    """
    if overlap > 1.0:  # overlap is in percent
        overlap = overlap / 100.0
    if verbose:
        print("Averages = {}".format(averages))
        print("Bandwidth = {} Hz".format(bandwidth))
        print("Overlap = {} %".format(overlap * 100.0))

    totalTime = (1 + (averages - 1) * (1 - overlap)) / bandwidth
    if verbose:
        print("\033[93m Total DTT Spectrum Time = {} seconds \033[0m".format(totalTime))
        print(
            "\033[91m Total DTT Spectrum Time = {} minutes \033[0m".format(
                totalTime / 60.0
            )
        )
    return totalTime


def dtt_averages(time, bandwidth, overlap, verbose=False):
    """Takes in time of clean data, bandwidth, overlap of a DTT template.
    Returns and prints the amount of time the DTT template will take to finish.
    Returns time in seconds, prints in minutes.
    """
    if overlap > 1.0:  # overlap is in percent
        overlap = overlap / 100.0
    if verbose:
        print("Time = {} s".format(time))
        print("Bandwidth = {} Hz".format(bandwidth))
        print("Overlap = {} %".format(overlap * 100.0))

    averages = (time * bandwidth - 1) / (1 - overlap) + 1
    if verbose:
        print("\033[93m Averages = {} \033[0m".format(averages))
    return averages


# Data acquistion/storage/manipulation
def find_channels(
    channel_glob="*",
    channel_type=None,
    data_type=None,
    min_sample_rate=0.0,
    max_sample_rate=999999995904.0,
    timespan=None,
    host_server="nds.ligo-wa.caltech.edu",
    port_number=31200,
    allow_data_on_tape="False",
    gap_handler="STATIC_HANDLER_NAN",
    verbose=True,
):
    """
    Use nds2 to find channels available in LIGO data.

    Inputs:
    channel_glob       -- A bash link glob pattern used to match channel names. Default is '*'.
    channel_type       -- str. Choose channels types to limit the search to.
                               Acceptable strings are any one of the following:
                               'UNKNOWN', 'ONLINE', 'RAW', 'RDS', 'STREND', 'MTREND', 'TEST_POINT', 'STATIC'
    data_type_mask     -- str. Choose data types to limit the search to.
                               Acceptable strings are any one of the following:
                               'UNKNOWN', 'INT16', 'INT32', 'INT64', 'FLOAT32', 'FLOAT64', 'COMPLEX32', 'UINT32'
    min_sample_rate    -- A minimum sample rate to search for.
    max_sample_rate    -- A maximum sample rate to search for.
    timespan           -- Optional time span to limit available channel search to.  This may be an nds2.epoch or a tuple of [start, stop) times.
    host_server        -- str. Valid nds2 server.  Default is `nds.ligo-wa.caltech.edu`
    port_number        -- int. Valid port from which to access the server.  Default is 31200
    allow_data_on_tape -- str. String should be `True` or `False`.  Set to `True` if need really old data, is slower.
    gap_handler        -- str.  Defines how gaps in the data should be handled by nds2.  String default is 'STATIC_HANDLER_NAN'.
                          Usual nds2 default is 'ABORT_HANDLER', which kills your request if there's any unavailable data.
                          More info at https://www.lsc-group.phys.uwm.edu/daswg/projects/nds-client/doc/manual/ch04s02.html.
    verbose            -- bool.  Automatically displays available channels.  Displays ",m-trend" on minute trend channels.   Default is True.

    Output:
    buffers = buffers native to nds2 (indexed with numbers), with no data

    Valid Host Sever:Port Number combos:
    h1nds1:8088                   # only good on LHO CDS computers
    h1nds0:8088                   # only good on LHO CDS computers
    nds.ligo-wa.caltech.edu:31200 # LHO frame cache
    nds.ligo-la.caltech.edu:31200 # LLO frame cache
    nds.ligo.caltech.edu:31200    # Caltech frame cache

    ### Examples ###
    # Get DQed Hanford DARM channel names
    find_channels('H1:LSC-DARM_*DQ')

    # Get only 'online' channels which can be streamed using stitch_real_time_data()
    find_channels('H1:CAL-DELTAL*DQ', channel_type='ONLINE')

    # Get DQed Livingston DARM channel names
    find_channels('L1:LSC-DARM_*DQ', host_server='nds.ligo-la.caltech.edu')

    # Get Hanford ITMY ISI stuff, including second and minute trend
    find_channels('H1:ISI-GND_STS_ITMY_Y_*')

    # Get Hanford ITMY ISI stuff, only the minute trends
    find_channels('H1:ISI-GND_STS_ITMY_Y_*', channel_type='MTREND')
    """

    if channel_type == None:
        channel_type_mask = 127  # accept all channels
    elif channel_type == "UNKNOWN":
        channel_type_mask = 0
    elif channel_type == "ONLINE":
        channel_type_mask = 1
    elif channel_type == "RAW":
        channel_type_mask = 2
    elif channel_type == "RDS":
        channel_type_mask = 4
    elif channel_type == "STREND":
        channel_type_mask = 8
    elif channel_type == "MTREND":
        channel_type_mask = 16
    elif channel_type == "TEST_POINT":
        channel_type_mask = 32
    elif channel_type == "STATIC":
        channel_type_mask = 64
    else:
        print(
            "\033[93m"
            + "WARNING: {channel_type} is not a valid channel type".format(
                channel_type=channel_type
            )
            + "\033[0m"
        )
        print("Continuing with no mask")
        print()

    if data_type == None:
        data_type_mask = 127  # accept all channels
    elif data_type == "UNKNOWN":
        data_type_mask = 0
    elif data_type == "INT16":
        data_type_mask = 1
    elif data_type == "INT32":
        data_type_mask = 2
    elif data_type == "INT64":
        data_type_mask = 4
    elif data_type == "FLOAT32":
        data_type_mask = 8
    elif data_type == "FLOAT64":
        data_type_mask = 16
    elif data_type == "COMPLEX32":
        data_type_mask = 32
    elif data_type == "UINT32":
        data_type_mask = 64
    else:
        print(
            "\033[93m"
            + "WARNING: {data_type} is not a valid channel type".format(
                data_type=data_type
            )
            + "\033[0m"
        )
        print("Continuing with no mask")
        print()

    params = nds2.parameters(host_server, port_number)
    params.set("ALLOW_DATA_ON_TAPE", allow_data_on_tape)
    params.set("GAP_HANDLER", gap_handler)

    buffers = nds2.find_channels(
        channel_glob=channel_glob,
        channel_type_mask=channel_type_mask,
        data_type_mask=data_type_mask,
        min_sample_rate=min_sample_rate,
        max_sample_rate=max_sample_rate,
        timespan=timespan,
        params=params,
    )

    if verbose:
        print()
        print(
            "Displaying channels that match {glob} on {hs}:{pn}".format(
                glob=channel_glob, hs=host_server, pn=port_number
            )
        )
        print()
        try:
            first_buff = buffers[0]  # to trigger the IndexError

            if len(buffers) < 1000:
                max_name_length = 0
                for buff in buffers:
                    if max_name_length < len(buff.name):
                        max_name_length = len(buff.name)
            else:
                max_name_length = 60

            max_name_length += 8  # add 8 in case there are minute or second trends
            for buff in buffers:
                name = buff.name
                fs = buff.sample_rate
                name_long = buff.NameLong()
                suffix = ""
                suffix_type = ""
                if "STREND" in name_long:
                    suffix = ",s-trend"
                    suffix_type = "STREND"
                elif "MTREND" in name_long:
                    suffix = ",m-trend"
                    suffix_type = "MTREND"
                elif "RAW" in name_long:
                    suffix_type = "RAW"
                elif "ONLINE" in name_long:
                    suffix_type = "ONLINE"
                elif "TEST_POINT" in name_long:
                    suffix_type = "TEST_POINT"

                name = "{}{}".format(name, suffix)
                print(
                    "{name:{max_name_length}}    fs = {fs:6.0f} Hz    type = {suffix_type:6}".format(
                        name=name,
                        max_name_length=max_name_length,
                        suffix_type=suffix_type,
                        fs=fs,
                    )
                )
            print()
            print(
                "Displaying channels that match {glob} on {hs}:{pn}".format(
                    glob=channel_glob, hs=host_server, pn=port_number
                )
            )
            print()

        except IndexError:
            print(
                "\033[93m"
                + "WARNING: No channels matching {glob} found".format(glob=channel_glob)
                + "\033[0m"
            )
            print()
        except RuntimeError:
            print(
                "\033[93m"
                + "RuntimeError: Failed to establish a connection[INFO: Error occurred trying to write to socket]"
                + "\033[0m"
            )
            print()
            print(
                "\033[93m" + "Did you run `kinit albert.einstein@LIGO.ORG`?" + "\033[0m"
            )
            print()
            print("\033[93m" + "Are your nds2 parameters set correctly?" + "\033[0m")
            print_nds2_params(params)
    return buffers


def check_channels_existance(
    channels,
    host_server="nds.ligo-wa.caltech.edu",
    port_number=31200,
    allow_data_on_tape="False",
    gap_handler="STATIC_HANDLER_NAN",
):
    """Uses find_channels() to determine which channels exist in a list.
    Returns nothing, outputs
    Input:
    channels = list of channels
    """
    print()
    print(f"Checking existance of channel in list on {host_server}:{port_number}")
    for chan in channels:
        buf = find_channels(
            chan,
            host_server=host_server,
            port_number=port_number,
            allow_data_on_tape=allow_data_on_tape,
            gap_handler=gap_handler,
            verbose=False,
        )
        try:
            buf[0]
            print("\033[92m" + f'"{chan}" found' "\033[0m")
        except IndexError:
            print("\033[93m" + f'"{chan}" does not exist' "\033[0m")

    return


def print_nds2_params(params):
    """Print the nds2 parameters which govern data collection."""
    for prm in params.parameter_list():
        print(f"{prm} = {params.get(prm)}")
    return


def make_array_from_buffers(buffers):
    """
    Input:
    buffers = native nds2 buffers, like from the output of find_channels().
    Outputs:
    channel_names = np.array() with the channel names as elements
    """
    channel_names = np.array([])
    for buff in buffers:
        name = buff.name
        name_long = buff.NameLong()
        suffix = ""
        if "STREND" in name_long:
            suffix = ",s-trend"
        elif "MTREND" in name_long:
            suffix = ",m-trend"

        name = "{}{}".format(name, suffix)
        channel_names = np.append(channel_names, name)
    return channel_names


def acquire_data(
    channels,
    gps_start,
    gps_stop,
    host_server="nds.ligo-wa.caltech.edu",
    port_number=31200,
    allow_data_on_tape="False",
    gap_handler="STATIC_HANDLER_NAN",
    is_minute_trend=False,
    return_nds2_buffers=False,
):
    """
    Use python nds2 client to get LIGO data.

    Inputs:
    channels            = array of strs. Valid LIGO channels from which to fetch data
    gps_start           = int. Valid GPS time at which to start acquiring data
    gps_stop            = int. Valid GPS time at which to stop acquiring data
    host_server         = str. Valid nds2 server.  Default is `nds.ligo-wa.caltech.edu`
    port_number         = int. Valid port from which to access the server.  Default is 31200
    allow_data_on_tape  = str. String should be `True` or `False`.  Set to `True` if need really old data, is slower.
    gap_handler         = str.  Defines how gaps in the data should be handled by nds2.  String default is 'STATIC_HANDLER_NAN'.
                          Usual nds2 default is 'ABORT_HANDLER', which kills your request if there's any unavailable data.
                          More info at https://www.lsc-group.phys.uwm.edu/daswg/projects/nds-client/doc/manual/ch04s02.html.
    is_minute_trend     = bool.  If true, will adjust gps_times to align with minute trend boundaries.  Default is False.
    return_nds2_buffers = bool.  If true, will return the native nds2 buffers and not the usual data dictionary.  Default is False.

    Output:
    Returns the channel buffers native to nds2.

    Valid Host Sever:Port Number combos:
    h1nds1:8088 # only good on LHO CDS computers
    h1nds0:8088
    nds.ligo-wa.caltech.edu:31200
    nds.ligo-la.caltech.edu:31200
    nds.ligo.caltech.edu:31200

    If you request minute trends of a channel by ending a channel name with ,m-trend
    this script will automatically adjust your gps_start and gps_stop times to align
    with the minute trend boundaries (basically the gpstimes must be divisible by 60)

    ### Examples ###

    # Get DARM error signal and control signal
    dataDict = acquire_data(['H1:LSC-DARM_IN1_DQ', 'H1:LSC-DARM_OUT_DQ'], 1256340013, 1256340167)

    # Get minute and second trends.  Beware of getting minute trends too close to the present, will return only nans
    dataDict = acquire_data(['H1:ISI-GND_STS_ITMY_Y_BLRMS_30M_100M.mean,m-trend',
                            'H1:ISI-GND_STS_ITMY_Y_BLRMS_30M_100M.mean,s-trend'],
                            1256340013,
                            1256340563)

    """
    # Check if ,m-trend is in any channel name
    if not is_minute_trend:
        for chan in channels:
            if ",m-trend" in chan:
                is_minute_trend = True
                break

    if is_minute_trend:
        new_gps_start = int(np.floor(gps_start / 60.0) * 60.0)
        new_gps_stop = int(np.ceil(gps_stop / 60.0) * 60.0)
        if not new_gps_start == gps_start or not new_gps_stop == gps_stop:
            print()
            print(
                "Adjusting gps_start and gps_stop times to align with minute trend boundaries:"
            )
            print("User Inputs:")
            print("gps_start = {}".format(gps_start))
            print("gps_stop  = {}".format(gps_stop))
            gps_start = int(new_gps_start)
            gps_stop = int(new_gps_stop)
            print("Adjusted GPS times:")
            print("gps_start = {}".format(gps_start))
            print("gps_stop  = {}".format(gps_stop))

    print()
    print(
        "Fetching data from {hs}:{pn} with GPS times {start} to {stop}".format(
            hs=host_server, pn=port_number, start=gps_start, stop=gps_stop
        )
    )
    print("from {channels}".format(channels=channels))
    try:
        params = nds2.parameters(host_server, port_number)
        params.set("ALLOW_DATA_ON_TAPE", allow_data_on_tape)
        params.set("GAP_HANDLER", gap_handler)
        buffers = nds2.fetch(channels, gps_start, gps_stop, params=params)
    except RuntimeError:
        print()
        print(
            "\033[93m"
            + "RuntimeError: Failed to establish a connection[INFO: Error occurred trying to write to socket]"
            + "\033[0m"
        )
        print()
        print("\033[93m" + "Did you run `kinit craig.cahillane@LIGO.ORG`?" + "\033[0m")
        print()
        print("\033[93m" + "Are your nds2 parameters set correctly?" + "\033[0m")
        print_nds2_params(params)
        print()
        print(
            "\033[93m"
            + "Checking if channels are valid with find_channels():"
            + "\033[0m"
        )
        check_channels_existance(
            channels,
            host_server=host_server,
            port_number=port_number,
            allow_data_on_tape=allow_data_on_tape,
            gap_handler=gap_handler,
        )
        return None

    try:
        first_buff = buffers[0]
        print()
        for buff in buffers:
            number_of_nans = np.sum(np.isnan(buff.data))
            if number_of_nans > 0:
                print(
                    "\033[93m"
                    + "WARNING: channel {name} returned {nan} nans".format(
                        name=buff.name, nan=number_of_nans
                    )
                    + "\033[0m"
                )

    except IndexError:
        print()
        print(
            "\033[93m"
            + "WARNING: No channel buffers returned for {channels}".format(
                channels=channels
            )
            + "\033[0m"
        )
        print()

    if return_nds2_buffers:
        return buffers

    duration = gps_stop - gps_start
    dataDict = extract_dict(buffers, duration=duration)
    return dataDict


def stitch_real_time_data(
    channels,
    duration,
    host_server="nds.ligo-wa.caltech.edu",
    port_number=31200,
    verbose=True,
):
    """
    Stitches together data broadcast from nds2 in real time.
    Useful for recording data during injections.

    Inputs:
    channels           = array of strs. Valid LIGO channels from which to fetch data.
                         All channels must be an "ONLINE" channel type.
    duration           = length of time to record data in seconds.
                         This script will take this number of seconds as it records the data in real time.
    host_server        = str. Valid nds2 server.  Default is `nds.ligo-wa.caltech.edu`
    port_number        = int. Valid port from which to access the server.  Default is 31200
    verbose            = bool.  Prints helpful statements of what's happening.  Default is True.

    Output:
    Dictionary of dicts with the channel names as keys, and the data and sampling rate fs as values.

    "real time" for some servers is slower than others.
    For nds.ligo-wa.caltech.edu the latency is ~ 2 seconds.
    If on LHO CDS computers, h1nds1:8088 is the best host_server:port_number combo.

    Valid Host Sever:Port Number combos:
    h1nds1:8088 # only good on LHO CDS computers
    h1nds0:8088
    nds.ligo-wa.caltech.edu:31200
    nds.ligo-la.caltech.edu:31200
    nds.ligo.caltech.edu:31200

    ### Example ###

    """
    dataDict = {}
    totalTime = 0
    skipSeconds = 2  # Because conn.iterate takes some time to make a true connection with the channel on h1nds1.  Needs at least two seconds.
    skipped = False
    intDuration = int(np.ceil(duration))

    if verbose:
        print("Establish connection to {}:{}".format(host_server, port_number))

    try:
        conn = nds2.connection(host_server, port_number)
    except:
        print()
        print(
            "\033[91m"
            + "Failed to establish connection to {}:{}".format(host_server, port_number)
            + "\033[0m"
        )
        print("Did you run kinit albert.einstein@LIGO.ORG ?")
        print("Are your host_server and port_number valid?")
        print()
        sys.exit(0)

    if verbose:
        print("Start gathering {} seconds of data!".format(intDuration))

    repeating_warn_dict = {}
    for chan in channels:
        repeating_warn_dict[chan] = False

    for buff in conn.iterate(channels):
        totalTime += 1

        if (totalTime <= skipSeconds) and (
            skipped is False
        ):  # skip the first two seconds
            if verbose:
                print("Skipping next {} seconds".format(skipSeconds - totalTime))
            continue
        elif skipped is False:
            skipped = True
            totalTime = 0

        for ii in range(len(channels)):
            curBuff = buff[ii]
            chan = curBuff.name
            if not len(dataDict.keys()) == len(channels):
                dataDict[chan] = {}
                dataDict[chan]["fs"] = int(curBuff.sample_rate)
                dataDict[chan]["gpsStart"] = curBuff.gps_seconds
                dataDict[chan]["data"] = curBuff.data
                if (
                    curBuff.data[0] == 0.0
                ):  # if the data is identically 0, something is wrong
                    print()
                    print(
                        "\033[91m"
                        + "Data for {} is identically zero.  Continuing data acquisition.".format(
                            chan
                        )
                        + "\033[0m"
                    )
                    print()
                    # return 'ZerosError'
            else:
                if (
                    curBuff.data[-1] == dataDict[chan]["data"][-1]
                    and not repeating_warn_dict[chan]
                ):  # if the data is repeating for some reason
                    repeating_warn_dict[chan] = True
                    print()
                    print(
                        "\033[91m"
                        + "Data for {} is repeating.  Continuing data acquisition.".format(
                            chan
                        )
                        + "\033[0m"
                    )
                    print()
                    # return 'ZerosError'

                dataDict[chan]["data"] = np.append(dataDict[chan]["data"], curBuff.data)

        sys.stdout.write("\r")
        sys.stdout.write(
            "{:d} seconds acquired / {:d} seconds total.".format(
                totalTime + 1, intDuration
            )
        )
        sys.stdout.flush()
        if totalTime >= intDuration - 1:
            break

    for chan in dataDict.keys():
        data = dataDict[chan]["data"]
        times = np.arange(len(dataDict[chan]["data"])) / float(dataDict[chan]["fs"])

        goodIndices = np.argwhere(times < duration)[:, 0]
        # goodTimes = times[goodIndices]
        goodData = data[goodIndices]

        # dataDict[chan]['times'] = goodTimes
        dataDict[chan]["data"] = goodData

    return dataDict


def extract_dict(chanData, duration):
    """
    Creates the usual data dictionary from the output of nds2.fetch(),
    The dict keys are the channel names.
    """
    dataDict = {}
    for curBuff in chanData:
        chan = curBuff.name
        dataDict[chan] = {}
        dataDict[chan]["fs"] = curBuff.sample_rate
        dataDict[chan]["gpsStart"] = curBuff.gps_seconds
        dataDict[chan]["data"] = curBuff.data
        dataDict[chan]["duration"] = duration

    for chan in dataDict.keys():
        data = dataDict[chan]["data"]
        times = np.arange(len(dataDict[chan]["data"])) / float(dataDict[chan]["fs"])

        goodIndices = np.argwhere(times < duration)[:, 0]
        goodTimes = times[goodIndices]
        goodData = data[goodIndices]

        # dataDict[chan]['times'] = goodTimes # half the cost of data storage
        dataDict[chan]["data"] = goodData

    return dataDict


def trim_dict(dataDict, duration):
    """Trims a dictionary with a long data stream down to a dictionary with a
    shorter data stream.  Good for taking fewer averages if some time is glitchy
    """
    for chan in dataDict.keys():
        data = dataDict[chan]["data"]
        times = dataDict[chan]["times"]

        goodIndices = np.argwhere(times < duration)[:, 0]
        goodTimes = times[goodIndices]
        goodData = data[goodIndices]

        dataDict[chan]["times"] = goodTimes
        dataDict[chan]["data"] = goodData

    return dataDict


def calibrate_chan(
    dataDict, chan, zeros=[], poles=[], gain=1.0, units="cts", apply_cal=True
):
    """
    Calibrates the ASD, PSD, CSD, and TF of the channel in dataDict using the zeros, poles, and gain.
    If Runs calibrate_dict().

    Inputs:
    dataDict  = data dictionary structure containing chan data
    chan      = str.    channel name we want to calibrate
    zeros     = list.   zeros associated with the calibration.  Default is []
    poles     = list.   poles associated with the calibration.  Default is []
    gain      = float.  gain associated with the calibration.  Default is 1.0
    units     = str.    units we are calibrating into.
    apply_cal = bool.   run calibrate_dict() on dataDict to immediately calibrate chan's ASD.  Default is True.

    Outputs:
    dataDict = same dataDict as before, but populated with the calibration.

    ### Example ###
    zeros = [ 30,  30,  30,  30,  30,  30]
    poles = [0.3, 0.3, 0.3, 0.3, 0.3, 0.3]
    gain  = 1.0
    calDataDict = calibrate_chan(dataDict, 'H1:CAL-DELTAL_EXTERNAL_DQ', zeros, poles, gain )
    """
    calDataDict = copy.deepcopy(dataDict)

    def cal_func(fff):
        """Intermediate calibration as function of frequency"""
        return tf_zpk(fff, zeros, poles, gain)

    calDataDict[chan]["calFunc"] = cal_func
    calDataDict[chan]["calUnits"] = units

    if apply_cal:
        calDataDict = calibrate_dict(calDataDict)  # run the calibration

    return calDataDict


def calibrate_dict(dataDict, recalculate=False):
    '''Calibrates the dataDict based on the user-provided calibrations.

    Example Usage:
    dataDict['H1:CAL-DELTAL_EXTERNAL_DQ']['calFunc'] = DARMcalFunc
    dataDict['H1:CAL-DELTAL_EXTERNAL_DQ']['calUnits'] = "m"  # not necessary but good practice
    dataDict['H1:CAL-PCALY_RX_PD_OUT_DQ']['calFunc'] = PCALcalFunc
    dataDict['H1:CAL-PCALY_RX_PD_OUT_DQ']['calUnits'] = "m"  # not necessary but good practice
    dataDict = calibrate_dict(dataDict)

    Example calFunc:
    def myChanCalFunc(fff):
        """Scale myChan ASD by a factor of 3.7 with a pole at 12.34 Hz"""
        return tf_zpk(fff, [], [12.34], 3.7)
    # Use myChan calFunc
    dataDict[myChan]['calFunc'] = myChanCalFunc

    In the dataDict data structure, each key is a channel.
    Under each channel list of values, there is a keyword that this function looks for called "calFunc".
    "calFunc" stands for calibration function, which should take in a frequency vector only and return a calibrated transfer function only.
    If "calFunc" is defined for at least one channel, a new calibrated ASD and PSD is calculated and stored under "calASD" and "calPSD" for only that channel.
    If "calFunc" is defined for at least two channels, a new calibrated CSD and TF is calculated and stored under "calCSD" and "calTF" for only those channels.

    Returns a dictionary with calibrated ASDs, PSDs, CSDs, and TFs for all channels with "calFunc" defined
    '''
    # Find channels with calibrations applied
    calChannels = np.array([])
    channels = dataDict.keys()
    for chan in channels:
        if "calFunc" in dataDict[chan].keys():
            calChannels = np.append(calChannels, chan)

    # Apply those calibrations
    # ASDs
    for chan in calChannels:
        ff_psd = dataDict[chan]["ff"]
        calFunc = dataDict[chan]["calFunc"]
        dataDict[chan]["calPSD"] = dataDict[chan]["PSD"] * np.abs(calFunc(ff_psd)) ** 2
        dataDict[chan]["calASD"] = dataDict[chan]["ASD"] * np.abs(calFunc(ff_psd))

    # CSDs
    for chan in calChannels:
        for chan2 in calChannels:
            if chan == chan2:
                continue
            if (
                chan in dataDict[chan2].keys() and not recalculate
            ):  # if we've already calculated the CSD, take it's complex conjugate and store it
                if "calCSD" in dataDict[chan2][chan].keys():
                    dataDict[chan][chan2]["ff"] = dataDict[chan2][chan]["ff"]
                    dataDict[chan][chan2]["calCSD"] = np.conj(
                        dataDict[chan2][chan]["calCSD"]
                    )
                    dataDict[chan][chan2]["calTF"] = (
                        1.0 / dataDict[chan2][chan]["calTF"]
                    )
                    continue

            if chan2 in dataDict[chan].keys():
                if "CSD" in dataDict[chan][chan2].keys():
                    ff_csd = dataDict[chan][chan2]["ff"]
                    calFunc = dataDict[chan]["calFunc"]
                    calFunc2 = dataDict[chan2]["calFunc"]
                    # C_xy = <x*|y>
                    # coherence = |C_xy|^2/(P_xx P_yy) = (C_xy C_xy^*)/(P_xx P_yy)
                    # H = C_xy/P_xx = P_yy/C_xy^* (perfect coherence = 1)
                    # |H|^2 = P_xx/P_yy
                    # |H| = A_xx/A_yy
                    dataDict[chan][chan2]["calCSD"] = (
                        dataDict[chan][chan2]["CSD"]
                        * np.conj(calFunc(ff_csd))
                        * calFunc2(ff_csd)
                    )
                    dataDict[chan][chan2]["calTF"] = (
                        dataDict[chan][chan2]["TF"] * calFunc(ff_csd) / calFunc2(ff_csd)
                    )
    return dataDict


def data_PSDs(dataDict, averages, bandwidth, overlap, averaging="mean"):
    """Take PSDs of all channels in dataDict.
    Returns them in the dataDict provided."""
    channels = dataDict.keys()
    for chan in channels:
        data = dataDict[chan]["data"]
        fs = dataDict[chan]["fs"]

        duration = dtt_time(averages, bandwidth, overlap)
        durationEffective = duration * averages / (1 + (averages - 1) * (1 - overlap))
        fftLen = durationEffective / averages
        nperseg = int(np.ceil(fftLen * fs))

        ff, Pxx = sig.welch(
            data, fs=fs, nperseg=nperseg, noverlap=overlap, average=averaging
        )
        dataDict[chan]["ff"] = ff
        dataDict[chan]["PSD"] = Pxx

        try:
            ff[1] - ff[0]
        except IndexError:
            print("IndexError, channel was likely all zeros, no sensible PSD taken")
            continue

        dataDict[chan]["df"] = ff[1] - ff[0]
        dataDict[chan]["ASD"] = np.sqrt(Pxx)

        dataDict[chan]["averages"] = averages
        dataDict[chan]["binwidth"] = bandwidth
        dataDict[chan]["overlap"] = overlap
        dataDict[chan]["duration"] = duration
        dataDict[chan]["fftLen"] = fftLen
        dataDict[chan]["nperseg"] = nperseg

    return dataDict


def data_TFs(dataDict):
    """Takes TFs and coherences of all channels in the dataDict with each other.
    Returns them in the dataDict provided."""
    channels = np.array(list(dataDict.keys()))
    if "CSD" not in dataDict[channels[0]][channels[1]]:
        print("You must run data_CSDs() first!")
        print("Exiting")
        return
    for chan in channels:
        for chan2 in channels:
            if chan == chan2:
                continue
            if chan not in dataDict[chan2].keys():
                continue

            fs = dataDict[chan]["fs"]
            fs2 = dataDict[chan2]["fs"]

            if not fs == fs2:
                if fs < fs2:
                    small_fs = fs
                    large_fs = fs2
                    ASD1 = dataDict[chan]["ASD"]
                    ASD2 = dataDict[chan2]["decimation"][small_fs]["ASD"]
                    PSD = dataDict[chan2]["decimation"][small_fs]["PSD"]
                    CSD = dataDict[chan2][chan]["CSD"]
                else:
                    small_fs = fs2
                    large_fs = fs
                    ASD1 = dataDict[chan]["decimation"][small_fs]["ASD"]
                    ASD2 = dataDict[chan2]["ASD"]
                    PSD = dataDict[chan2]["PSD"]
                    CSD = dataDict[chan2][chan]["CSD"]
            else:
                ASD1 = dataDict[chan]["ASD"]
                ASD2 = dataDict[chan2]["ASD"]
                PSD = dataDict[chan2]["PSD"]
                CSD = dataDict[chan2][chan]["CSD"]

            TF = CSD / PSD
            coh = (
                np.abs(CSD) / (ASD1 * ASD2)
            ) ** 2  # return a power coherence, but use ASDs to avoid really small numbers

            dataDict[chan][chan2]["TF"] = TF
            dataDict[chan][chan2]["coh"] = coh
    return dataDict


def data_CSDs(dataDict, averages, bandwidth, overlap, averaging="mean", makeTFs=True):
    """Takes CSDs of all channels with each other.
    If PSDs not taken, takes them automatically.
    If makeTFs=True, creates the TFs of all channels with one another.
    Returns everything in the dataDict provided."""
    channels = np.array(list(dataDict.keys()))
    # Check if PSDs exist, if not make them.
    if "PSD" not in dataDict[channels[0]].keys():
        print("Running data_PSDs!")
        dataDict = data_PSDs(
            dataDict, averages, bandwidth, overlap, averaging=averaging
        )
        print("Got PSDs!")

    for chan in channels:
        data = dataDict[chan]["data"]
        fs = dataDict[chan]["fs"]

        duration = dtt_time(averages, bandwidth, overlap)
        durationEffective = duration * averages / (1 + (averages - 1) * (1 - overlap))
        fftLen = durationEffective / averages
        # nperseg = int( np.ceil( fftLen * fs ) )

        for chan2 in channels:
            if chan == chan2:
                continue

            data2 = dataDict[chan2]["data"]
            fs2 = dataDict[chan2]["fs"]
            if not fs == fs2:
                if fs < fs2:
                    small_fs = fs
                    large_fs = fs2
                    large_data = data2
                    large_chan = chan2
                else:
                    small_fs = fs2
                    large_fs = fs
                    large_data = data
                    large_chan = chan

                decimation_ratio = int(large_fs / small_fs)
                decimated_data = sig.decimate(
                    large_data, decimation_ratio
                )  # applied antialiasing automatically

                nperseg = int(
                    np.ceil(fftLen * small_fs)
                )  # ensure samples per segment is correct now

                ff, Pxx = sig.welch(
                    decimated_data,
                    fs=small_fs,
                    nperseg=nperseg,
                    noverlap=overlap,
                    average=averaging,
                )

                large_chan_key_list = np.array(
                    list(dataDict[large_chan].keys())
                )  # don't overwrite previous ASDs
                if "decimation" not in large_chan_key_list:
                    dataDict[large_chan]["decimation"] = {}
                dataDict[large_chan]["decimation"][small_fs] = {}
                dataDict[large_chan]["decimation"][small_fs]["fs"] = small_fs
                dataDict[large_chan]["decimation"][small_fs]["ff"] = ff
                dataDict[large_chan]["decimation"][small_fs]["PSD"] = Pxx
                dataDict[large_chan]["decimation"][small_fs]["df"] = ff[1] - ff[0]
                dataDict[large_chan]["decimation"][small_fs]["ASD"] = np.sqrt(Pxx)

                if fs < fs2:
                    small_data = data
                    small_data2 = decimated_data
                else:
                    small_data = decimated_data
                    small_data2 = data2
                # print('Sampling rates of {} and {} not the same, {} != {}'.format(chan, chan2, fs, fs2))
                # print('Skipping')
                # continue
            else:
                small_data = data
                small_data2 = data2
                small_fs = fs
                nperseg = int(np.ceil(fftLen * fs))

            ff, Cxy = sig.csd(
                small_data,
                small_data2,
                fs=small_fs,
                nperseg=nperseg,
                noverlap=overlap,
                average=averaging,
            )

            dataDict[chan][chan2] = {}
            dataDict[chan][chan2]["ff"] = ff
            dataDict[chan][chan2]["CSD"] = Cxy

    if makeTFs:
        dataDict = data_TFs(dataDict)
    return dataDict


def get_PSDs(
    channels,
    gps_start,
    gps_stop,
    binwidth,
    overlap,
    averaging="mean",
    host_server="nds.ligo-wa.caltech.edu",
    port_number=31200,
    allow_data_on_tape="False",
    gap_handler="STATIC_HANDLER_NAN",
    is_minute_trend=False,
    verbose=True,
):
    """
    Use nds2 to get LIGO data, and automatically calculate some PSDs and ASDs from the data.
    Should be slightly faster than get_CSDs(), especially for large numbers of channels.

    Valid Host Sever:Port Number combos:
    h1nds1:8088 # only good on LHO CDS computers
    h1nds0:8088 # only good on LHO CDS computers
    nds.ligo-wa.caltech.edu:31200
    nds.ligo-la.caltech.edu:31200
    nds.ligo.caltech.edu:31200

    If you request minute trends of a channel by ending a channel name with ,m-trend
    this script will automatically adjust your gps_start and gps_stop times to align
    with the minute trend boundaries (basically the gpstimes must be divisible by 60)

    Inputs:
    channels           = array of strs. Valid LIGO channels from which to fetch data
    gps_start          = int. Valid GPS time at which to start acquiring data
    gps_stop           = int. Valid GPS time at which to stop acquiring data
    binwidth           = float.  Frequency bin spacing for PSDs and ASDs
    overlap            = float.  Overlap of the time series for the ASD calculations
    averaging          = str.  Either 'mean' or 'median' averaging for the ASD calculations. Default is 'mean'.
    host_server        = str. Valid nds2 server.  Default is `nds.ligo-wa.caltech.edu`
    port_number        = int. Valid port from which to access the server.  Default is 31200
    allow_data_on_tape = str. String should be `True` or `False`.  Set to `True` if need really old data, is slower.
    gap_handler        = str.  Defines how gaps in the data should be handled by nds2.  String default is 'STATIC_HANDLER_NAN'.
                         Usual nds2 default is 'ABORT_HANDLER', which kills your request if there's any unavailable data.
                         More info at https://www.lsc-group.phys.uwm.edu/daswg/projects/nds-client/doc/manual/ch04s02.html.
    is_minute_trend    = bool.  If true, will adjust gps_times to align with minute trend boundaries.  Default is False.
    verbose            = bool. Default true.  If set will print to terminal all input arguments.

    Output:
    Returns a dictionary with channel names as keys, and values which are also dictionaries containing the time-series data, sampling rate,
    and PSDs and ASDs calculated.

    ### Example ###
    import numpy as np
    from dataUtils import *
    channels = np.array(['H1:CAL-DELTAL_EXTERNAL_DQ', 'H1:PSL-ISS_SECONDLOOP_RIN_OUTER_OUT_DQ', 'H1:LSC-REFL_SERVO_ERR_OUT_DQ'])
    gps_stop_23 = 1256771546
    duration = 150
    gps_start_23 = gps_stop_23 - duration
    overlap = 0.75
    binwidth = 1.0
    dataDict_23 = get_PSDs(channels, gps_start_23, gps_stop_23, binwidth, overlap)
    """
    duration = int(gps_stop - gps_start)
    averages = int(dtt_averages(duration, binwidth, overlap))

    if allow_data_on_tape == True:
        allow_data_on_tape = "True"
    elif allow_data_on_tape == False:
        allow_data_on_tape = "False"

    if verbose:
        print("Getting PSDs:")
        print("Channels = {}".format(channels))
        print("gps_start = {}".format(gps_start))
        print("gps_stop  = {}".format(gps_stop))
        print("duration = {} s".format(duration))
        print("averages = {}".format(averages))
        print("binwidth = {} Hz".format(binwidth))
        print("overlap = {}".format(overlap))
        print("host_server = {}".format(host_server))
        print("port_number = {}".format(port_number))
        print("allow_data_on_tape = {}".format(allow_data_on_tape))
        print("gap_handler = {}".format(gap_handler))
        print("is_minute_trend = {}".format(is_minute_trend))
        print("verbose = {}".format(verbose))

    dataDict = acquire_data(
        channels,
        gps_start,
        gps_stop,
        host_server=host_server,
        port_number=port_number,
        allow_data_on_tape=allow_data_on_tape,
        gap_handler=gap_handler,
        is_minute_trend=is_minute_trend,
    )
    dataDict = data_PSDs(dataDict, averages, binwidth, overlap, averaging=averaging)
    return dataDict


def get_CSDs(
    channels,
    gps_start,
    gps_stop,
    binwidth,
    overlap,
    averaging="mean",
    host_server="nds.ligo-wa.caltech.edu",
    port_number=31200,
    allow_data_on_tape="False",
    gap_handler="STATIC_HANDLER_NAN",
    is_minute_trend=False,
    makeTFs=True,
    verbose=True,
):
    """
    Use nds2 to get LIGO data, and automatically calculate some PSDs, ASDs, CSDs and TFs from the data.

    Valid Host Sever:Port Number combos:
    h1nds1:8088 # only good on LHO CDS computers
    h1nds0:8088
    nds.ligo-wa.caltech.edu:31200
    nds.ligo-la.caltech.edu:31200
    nds.ligo.caltech.edu:31200

    If you request minute trends of a channel by ending a channel name with ,m-trend
    this script will automatically adjust your gps_start and gps_stop times to align
    with the minute trend boundaries (basically the gpstimes must be divisible by 60)

    Inputs:
    channels           = array of strs. Valid LIGO channels from which to fetch data
    gps_start          = int. Valid GPS time at which to start acquiring data
    gps_stop           = int. Valid GPS time at which to stop acquiring data
    binwidth           = float.  Frequency bin spacing for PSDs and ASDs
    overlap            = float.  Overlap of the time series for the ASD calculations
    averaging          = str.  Either 'mean' or 'median' averaging for the ASD calculations. Default is 'mean'.
    host_server        = str. Valid nds2 server.  Default is `nds.ligo-wa.caltech.edu`
    port_number        = int. Valid port from which to access the server.  Default is 31200
    allow_data_on_tape = str. String should be `True` or `False`.  Set to `True` if need really old data, is slower.
    gap_handler        = str.  Defines how gaps in the data should be handled by nds2.  String default is 'STATIC_HANDLER_NAN'.
                         Usual nds2 default is 'ABORT_HANDLER', which kills your request if there's any unavailable data.
                         More info at https://www.lsc-group.phys.uwm.edu/daswg/projects/nds-client/doc/manual/ch04s02.html.
    is_minute_trend    = bool.  If true, will adjust gps_times to align with minute trend boundaries.  Default is False.
    makeTFs            = bool.  If true, will calculate transfer functions and power coherence from all calculated CSDs.  Default is True.
    verbose            = bool. Default true.  If set will print to terminal all input arguments.

    Output:
    Returns a dictionary with channel names as keys,
    and values which are also dictionaries containing the time-series data, sampling rate,
    and PSDs, ASDs, CSDs, and TFs calculated.

    ### Example ###
    import numpy as np
    from dataUtils import *
    channels = np.array(['H1:CAL-DELTAL_EXTERNAL_DQ', 'H1:PSL-ISS_SECONDLOOP_RIN_OUTER_OUT_DQ', 'H1:LSC-REFL_SERVO_ERR_OUT_DQ'])
    gps_stop_23 = 1256771546
    duration = 150
    gps_start_23 = gps_stop_23 - duration
    overlap = 0.75
    binwidth = 1.0
    dataDict_23 = get_CSDs(channels, gps_start_23, gps_stop_23, binwidth, overlap)

    """
    duration = int(gps_stop - gps_start)
    averages = int(dtt_averages(duration, binwidth, overlap))

    if allow_data_on_tape == True:
        allow_data_on_tape = "True"
    elif allow_data_on_tape == False:
        allow_data_on_tape = "False"

    if verbose:
        print("Getting CSDs:")
        print("Channels = {}".format(channels))
        print("gps_start = {}".format(gps_start))
        print("gps_stop  = {}".format(gps_stop))
        print("duration = {} s".format(duration))
        print("averages = {}".format(averages))
        print("binwidth = {} Hz".format(binwidth))
        print("overlap = {}".format(overlap))
        print("host_server = {}".format(host_server))
        print("port_number = {}".format(port_number))
        print("allow_data_on_tape = {}".format(allow_data_on_tape))
        print("gap_handler = {}".format(gap_handler))
        print("is_minute_trend = {}".format(is_minute_trend))
        print("makeTFs = {}".format(makeTFs))
        print("verbose = {}".format(verbose))

    dataDict = acquire_data(
        channels,
        gps_start,
        gps_stop,
        host_server=host_server,
        port_number=port_number,
        allow_data_on_tape=allow_data_on_tape,
        gap_handler=gap_handler,
        is_minute_trend=is_minute_trend,
    )
    dataDict = data_CSDs(
        dataDict, averages, binwidth, overlap, averaging=averaging, makeTFs=makeTFs
    )
    return dataDict


### get_all spectral density functions
# returns every psd, csd used in calculating the average psd, csd via Welch's method
def get_all_psds(
    x,
    fs=1.0,
    window="hann",
    nperseg=None,
    noverlap=None,
    nfft=None,
    detrend="constant",
    return_onesided=True,
    scaling="density",
    axis=-1,
):
    """Abuses the function scipy.signal.spectrogram()
    to return all power spectral densities which make up a PSD estimate.
    Should be equivalent exactly to scipy.signal.spectrogram(mode='psd'),
    but we want to use this method for get_all_csds() as well.
    Included for consistency.

    Parameters
    ----------
    x : array_like
        Time series of measurement values
    fs : float, optional
        Sampling frequency of the `x` time series. Defaults to 1.0.
    window : str or tuple or array_like, optional
        Desired window to use. If `window` is a string or tuple, it is
        passed to `get_window` to generate the window values, which are
        DFT-even by default. See `get_window` for a list of windows and
        required parameters. If `window` is array_like it will be used
        directly as the window and its length must be nperseg.
        Defaults to a Tukey window with shape parameter of 0.25.
    nperseg : int, optional
        Length of each segment. Defaults to None, but if window is str or
        tuple, is set to 256, and if window is array_like, is set to the
        length of the window.
    noverlap : int, optional
        Number of points to overlap between segments. If `None`,
        ``noverlap = nperseg // 8``. Defaults to `None`.
    nfft : int, optional
        Length of the FFT used, if a zero padded FFT is desired. If
        `None`, the FFT length is `nperseg`. Defaults to `None`.
    detrend : str or function or `False`, optional
        Specifies how to detrend each segment. If `detrend` is a
        string, it is passed as the `type` argument to the `detrend`
        function. If it is a function, it takes a segment and returns a
        detrended segment. If `detrend` is `False`, no detrending is
        done. Defaults to 'constant'.
    return_onesided : bool, optional
        If `True`, return a one-sided spectrum for real data. If
        `False` return a two-sided spectrum. Defaults to `True`, but for
        complex data, a two-sided spectrum is always returned.
    scaling : { 'density', 'spectrum' }, optional
        Selects between computing the power spectral density ('density')
        where `Sxx` has units of V**2/Hz and computing the power
        spectrum ('spectrum') where `Sxx` has units of V**2, if `x`
        is measured in V and `fs` is measured in Hz. Defaults to
        'density'.
    axis : int, optional
        Axis along which the spectrogram is computed; the default is over
        the last axis (i.e. ``axis=-1``).
    mode : str, optional
        Defines what kind of return values are expected. Options are
        ['psd', 'complex', 'magnitude', 'angle', 'phase']. 'complex' is
        equivalent to the output of `stft` with no padding or boundary
        extension. 'magnitude' returns the absolute magnitude of the
        STFT. 'angle' and 'phase' return the complex angle of the STFT,
        with and without unwrapping, respectively.

    Returns
    -------
    f : ndarray
        Array of sample frequencies.
    t : ndarray
        Array of segment times.
    Sxxs : ndarray
        Power spectral densities of x. By default, the last axis of Sxx corresponds
        to the segment times.

    """
    freqs, time, Fxx = sig.spectrogram(
        x,
        fs=fs,
        window=window,
        nperseg=nperseg,
        noverlap=noverlap,
        nfft=nfft,
        detrend=detrend,
        return_onesided=return_onesided,
        scaling=scaling,
        axis=axis,
        mode="complex",
    )
    Sxxs = np.abs(2 * np.conjugate(Fxx) * Fxx)

    return freqs, time, Sxxs


def get_all_csds(
    x,
    y,
    fs=1.0,
    window="hann",
    nperseg=None,
    noverlap=None,
    nfft=None,
    detrend="constant",
    return_onesided=True,
    scaling="density",
    axis=-1,
):
    """Abuses the function scipy.signal.spectrogram()
    to return all cross spectral densities which make up a CSD estimate.

    Parameters
    ----------
    x : array_like
        Time series of measurement values
    y : array_like
        Time series of measurement values
    fs : float, optional
        Sampling frequency of the `x` time series. Defaults to 1.0.
    window : str or tuple or array_like, optional
        Desired window to use. If `window` is a string or tuple, it is
        passed to `get_window` to generate the window values, which are
        DFT-even by default. See `get_window` for a list of windows and
        required parameters. If `window` is array_like it will be used
        directly as the window and its length must be nperseg.
        Defaults to a Tukey window with shape parameter of 0.25.
    nperseg : int, optional
        Length of each segment. Defaults to None, but if window is str or
        tuple, is set to 256, and if window is array_like, is set to the
        length of the window.
    noverlap : int, optional
        Number of points to overlap between segments. If `None`,
        ``noverlap = nperseg // 8``. Defaults to `None`.
    nfft : int, optional
        Length of the FFT used, if a zero padded FFT is desired. If
        `None`, the FFT length is `nperseg`. Defaults to `None`.
    detrend : str or function or `False`, optional
        Specifies how to detrend each segment. If `detrend` is a
        string, it is passed as the `type` argument to the `detrend`
        function. If it is a function, it takes a segment and returns a
        detrended segment. If `detrend` is `False`, no detrending is
        done. Defaults to 'constant'.
    return_onesided : bool, optional
        If `True`, return a one-sided spectrum for real data. If
        `False` return a two-sided spectrum. Defaults to `True`, but for
        complex data, a two-sided spectrum is always returned.
    scaling : { 'density', 'spectrum' }, optional
        Selects between computing the power spectral density ('density')
        where `Sxx` has units of V**2/Hz and computing the power
        spectrum ('spectrum') where `Sxx` has units of V**2, if `x`
        is measured in V and `fs` is measured in Hz. Defaults to
        'density'.
    axis : int, optional
        Axis along which the spectrogram is computed; the default is over
        the last axis (i.e. ``axis=-1``).
    mode : str, optional
        Defines what kind of return values are expected. Options are
        ['psd', 'complex', 'magnitude', 'angle', 'phase']. 'complex' is
        equivalent to the output of `stft` with no padding or boundary
        extension. 'magnitude' returns the absolute magnitude of the
        STFT. 'angle' and 'phase' return the complex angle of the STFT,
        with and without unwrapping, respectively.

    Returns
    -------
    f : ndarray
        Array of sample frequencies.
    t : ndarray
        Array of segment times.
    Sxys : ndarray
        Cross spectral densities of x and y. By default, the last axis of Sxys corresponds
        to the segment times.

    """
    freqs, time, Fxx = sig.spectrogram(
        x,
        fs=fs,
        window=window,
        nperseg=nperseg,
        noverlap=noverlap,
        nfft=nfft,
        detrend=detrend,
        return_onesided=return_onesided,
        scaling=scaling,
        axis=axis,
        mode="complex",
    )
    freqs, time, Fyy = sig.spectrogram(
        y,
        fs=fs,
        window=window,
        nperseg=nperseg,
        noverlap=noverlap,
        nfft=nfft,
        detrend=detrend,
        return_onesided=return_onesided,
        scaling=scaling,
        axis=axis,
        mode="complex",
    )
    Sxys = 2 * np.conjugate(Fxx) * Fyy

    return freqs, time, Sxys


### Convenience functions for returning median-averaged psds and csds from get_all functions
def get_median_psd(Saas):
    """Calculate the median PSD from a bunch of PSDs.  No bias is applied.
    Example:
    Sxxs = get_all_psds(x)
    Sxx_med = get_median_psd(Sxxs)
    """
    Saa_med = np.median(Saas, axis=1)
    return Saa_med


def get_median_csd(Sabs):
    """Calculate the median CSD from a bunch of CSDs.  No bias is applied.
    Example:
    Sxys = get_all_csds(x, y)
    Sxy_med = get_median_csd(Sxys)
    """
    Sab_med = np.median(np.real(Sabs), axis=1) + 1j * np.median(np.imag(Sabs), axis=1)
    return Sab_med


def get_coherence(Saa_med, Sbb_med, Sab_med):
    """Calculate the coherence from given PSDs and CSDs.
    Example:
    Sxxs = get_all_psds(x)
    Syys = get_all_psds(y)
    Sxys = get_all_csds(x, y)

    Sxx_med = get_median_psd(Sxxs)
    Syy_med = get_median_psd(Syys)
    Sxy_med = get_median_csd(Sxys)

    cohs_med = get_coherence(Sxx_med, Syy_med, Sxy_med)
    """
    coherence_med = np.abs(Sab_med) ** 2 / (Saa_med * Sbb_med)
    return coherence_med


### Equivalent convenience functions for mean-averaged psds and csds.
def get_mean_psd(Saas):
    """Calculate the mean PSD from a bunch of PSDs.  No bias is applied.
    Example:
    Sxxs = get_all_psds(x)
    Sxx_mean = get_mean_psd(Sxxs)
    """
    Saa_mean = np.mean(Saas, axis=1)
    return Saa_mean


def get_mean_csd(Sabs):
    """Calculate the mean CSD from a bunch of CSDs.  No bias is applied.
    Example:
    Sxys = get_all_csds(x, y)
    Sxy_mean = get_mean_csd(Sxys)
    """
    Sab_mean = np.mean(np.real(Sabs), axis=1) + 1j * np.mean(np.imag(Sabs), axis=1)
    return Sab_mean


### Mean-to-median bias functions for cross spectral densities
# Outward-facing function is biases_from_coherences()
def median_coherence_from_power_ratio(power_ratio):
    """Given a power_ratio of uncorrelated noise over correlated noise,
    power_ratio = sigma_uncorr^2 / sigma_corr^2,
    returns the power coherence gamma^2 that would result from median-averaged PSDs and CSDs.
    """
    med_coh = (power_ratio ** 2 * np.log(1 + 1 / np.sqrt(1 + power_ratio)) ** 2) / (
        4
        * np.log(2) ** 2
        * (1 + power_ratio)
        * (2 + power_ratio - 2 * np.sqrt(1 + power_ratio))
    )
    return med_coh


def residual_median_coherence(input_array, median_coherence_desired):
    """Finds the residual between the coherence desired and the numerically attempt from fsolve().
    For use as the function input to fsolve() in bias_from_median_coherence().
    Inputs:
    input_array = array of length one, required by fsolve to find the power ratio numerically
    median_coherence_desired = median coherence estimated from the CSD signals.
    Output:
    residual = array of length one with residual from median_coherence() function
    """
    func_results = median_coherence_from_power_ratio(input_array[0])
    residual = [func_results - median_coherence_desired]
    return residual


def bias_from_median_coherence_and_power_ratio(median_coherence, power_ratio):
    """Calculates the mean-to-median bias factor from the median_coherence = gamma^2
    and the power_ratio = epsilon.
    """
    bias = np.log(2) * np.sqrt((1 + power_ratio) * median_coherence)
    return bias


def bias_from_median_coherence(median_coherence_estimated, initial_power_ratio=0.1):
    """Estimates the median/mean bias = b given some median_coherence = gamma^2.

    Numerically solves for the uncorrelated/correated power_ratio = epsilon,
    using the median_coherence.
    Uses scipy.optimize.fsolve() to find the root of residual_median_coherence().
    fsolve() seems to work for gamma^2 between (0.999 and 1e-6)

    This function requires bias_from_median_coherence_and_power_ratio(),
    residual_median_coherence(), median_coherence(), and fsolve() functions.

    Inputs:
    median_coherence_estimated  =   median coherence estimated from |<x,z>|^2/(<x,x> <z,z>)
                                    where all spectral densities are median-averaged
    initial_power_ratio         =   initial guess of the power_ratio, default is 1.0
    Output:
    bias    =   median/mean bias factor.  Divide median-averaged cross spectral density <x,z>
                by bias to recover the mean-avearged cross spectral density.
    """
    # Numerically estimate the power ratio epsilon from the median coherence
    fsolve_array = fsolve(
        residual_median_coherence,
        [initial_power_ratio],
        args=(median_coherence_estimated),
    )
    power_ratio = fsolve_array[0]

    # Find the bias factor
    bias = bias_from_median_coherence_and_power_ratio(
        median_coherence_estimated, power_ratio
    )
    return bias


def biases_from_median_coherences(median_coherences, initial_power_ratios=None):
    """Returns array of CSD mean-to-median biases from an array of median_coherences.
    Inputs:
    median_coherences =    median-averaged coherences
    initial_power_ratios =  power ratios to start estimation with.
                            If None, uses 0.1 for all.  Default is None.
    Outputs:
    biases =    array of biases calculated from the coherences

    Example:
    Sxxs = get_all_psds(x)
    Syys = get_all_psds(y)
    Sxys = get_all_csds(x, y)

    Sxx_med = get_median_psd(Sxxs)
    Syy_med = get_median_psd(Syys)
    Sxy_med = get_median_csd(Sxys)

    cohs_med = get_coherence(Sxx_med, Syy_med, Sxy_med)
    biases = biases_from_coherences(cohs_med)

    Sxy_med_bias_corrected = Sxy_med / biases
    """
    if initial_power_ratios is None:
        initial_power_ratios = 0.1 * np.ones_like(median_coherences)
    biases = np.array([])
    for coherence, initial_power_ratio in zip(median_coherences, initial_power_ratios):
        bias = bias_from_median_coherence(
            coherence, initial_power_ratio=initial_power_ratio
        )
        biases = np.append(biases, bias)
    return biases


### Modify data based on thresholds
def coherence_threshold_applier(coherenceVector, coherenceThreshold=0.9):
    """Apply a coherence threshold to a vector, returns all indicies of the vector above the threshold"""
    goodIndices = np.argwhere(coherenceVector > coherenceThreshold)[:, 0]
    return goodIndices


def bandlimit_applier(frequencyVector, bandlimit_low, bandlimit_high):
    """Cut off the low and high frequencies from a frequencyVector.  Returns the valid indices."""
    goodHighIndicies = np.argwhere(frequencyVector > bandlimit_low)[:, 0]
    goodLowIndicies = np.argwhere(frequencyVector < bandlimit_high)[:, 0]
    goodIndices = np.intersect1d(goodHighIndicies, goodLowIndicies)
    return goodIndices


# ZPK frequency responses
def zpk_freq_resp(ff, z, p, k):
    """Takes in a frequency vector, and a zpk.
    Returns the frequency response.
    Use tf_zpk instead, works for old python scipy.signal libraries."""
    ww = 2 * np.pi * ff
    z *= -2 * np.pi
    p *= -2 * np.pi
    k *= np.abs(np.prod(p) / np.prod(z))
    ww, hh = sig.freqs_zpk(z, p, k, worN=ww)
    return hh


def tf_zpk(freq, f_zeros, f_poles, gain=1.0, absval=False, input_units="n"):
    """Compute frequency response of ZPK filter

    inputUnits is the type of TF we want to implement based on foton options:
    'n' is default, and stands for normalized.  This means the gain is
    normalized by the product of the poles over the product of zeros.
    'f' is the Hz interpretation, the poles and zeros are multiplied by -1 and
    the gain is not normalized.
    's' is the rad/s interpretation, the poles and zeros are multiplied by -2*pi
    and the gain is not normalized.

    """
    f_zeros = np.array(f_zeros)
    f_poles = np.array(f_poles)

    if input_units == "n":
        z = -2 * np.pi * f_zeros
        p = -2 * np.pi * f_poles

        k = (
            np.abs(np.prod(p[p != 0]) / np.prod(z[z != 0]))
            * ((2 * np.pi) ** p[p == 0].size)
            / ((2 * np.pi) ** z[z == 0].size)
            * gain
        )
    elif input_units == "f":
        z = 2 * np.pi * f_zeros
        p = 2 * np.pi * f_poles
        k = gain
    elif input_units == "s":
        z = f_zeros
        p = f_poles
        k = gain
    else:
        # don't allow any case to go uncaught
        assert False

    w = 2 * np.pi * freq
    # tf = scipy.signal.freqs_zpk(z, p, k, worN=w)[1]
    b, a = sig.zpk2tf(z, p, k)
    tf = sig.freqs(b, a, worN=w)[1]
    if absval:
        tf = np.abs(tf)

    return tf


def get_complex_interp(x2, x1, y1, **kwargs):
    """Interpolates a complex vector y1 from x1 to x2.
    Courtesy of Evan Hall."""
    re2 = np.interp(x2, x1, np.real(y1), **kwargs)
    im2 = np.interp(x2, x1, np.imag(y1), **kwargs)
    return re2 + 1j * im2


def RMS(freq, spec):
    """Takes in frequency vector and ASD, returns the RMS from high to low freq"""
    df = np.ediff1d(freq)
    df = np.append(df, df[-1])
    return np.flipud(np.sqrt(np.cumsum(np.flipud(df * spec ** 2))))


def simple_OLG(fff, UGF):
    """Given a frequency vector and unity gain frequency, returns a simple 1/f OLG"""
    return UGF / fff


# Logbinning
def resampling_matrix_nonuniform(lorig, lresam, extrap=False):
    """
    Logbinning stolen from some astro people: https://pypi.org/project/PySTARLIGHT/

    Compute resampling matrix R_o2r, useful to convert a spectrum sampled at
    wavelengths lorig to a new grid lresamp. Here, there is no necessity to have constant gris as on :py:func:`ReSamplingMatrix`.
    Input arrays lorig and lresamp are the bin centres of the original and final lambda-grids.
    ResampMat is a Nlresamp x Nlorig matrix, which applied to a vector F_o (with Nlorig entries) returns
    a Nlresamp elements long vector F_r (the resampled spectrum):

        [[ResampMat]] [F_o] = [F_r]

    Warning! lorig and lresam MUST be on ascending order!


    Parameters
    ----------
    lorig : array_like
            Original spectrum lambda array.

    lresam : array_like
             Spectrum lambda array in which the spectrum should be sampled.

    extrap : boolean, optional
           Extrapolate values, i.e., values for lresam < lorig[0]  are set to match lorig[0] and
                                     values for lresam > lorig[-1] are set to match lorig[-1].


    Returns
    -------
    ResampMat : array_like
                Resample matrix.

    Examples
    --------
    >>> lorig = np.linspace(3400, 8900, 9000) * 1.001
    >>> lresam = np.linspace(3400, 8900, 5000)
    >>> forig = np.random.normal(size=len(lorig))**2
    >>> matrix = slut.resampling_matrix_nonuniform(lorig, lresam)
    >>> fresam = np.dot(matrix, forig)
    >>> print np.trapz(forig, lorig), np.trapz(fresam, lresam)
    """

    # Init ResampMatrix
    matrix = np.zeros((len(lresam), len(lorig)))

    # Define lambda ranges (low, upp) for original and resampled.
    lo_low = np.zeros(len(lorig))
    lo_low[1:] = (lorig[1:] + lorig[:-1]) / 2
    lo_low[0] = lorig[0] - (lorig[1] - lorig[0]) / 2

    lo_upp = np.zeros(len(lorig))
    lo_upp[:-1] = lo_low[1:]
    lo_upp[-1] = lorig[-1] + (lorig[-1] - lorig[-2]) / 2

    lr_low = np.zeros(len(lresam))
    lr_low[1:] = (lresam[1:] + lresam[:-1]) / 2
    lr_low[0] = lresam[0] - (lresam[1] - lresam[0]) / 2

    lr_upp = np.zeros(len(lresam))
    lr_upp[:-1] = lr_low[1:]
    lr_upp[-1] = lresam[-1] + (lresam[-1] - lresam[-2]) / 2

    # Iterate over resampled lresam vector
    for i_r in range(len(lresam)):

        # Find in which bins lresam bin within lorig bin
        bins_resam = np.where((lr_low[i_r] < lo_upp) & (lr_upp[i_r] > lo_low))[0]

        # On these bins, eval fraction of resamled bin is within original bin.
        for i_o in bins_resam:

            aux = 0

            d_lr = lr_upp[i_r] - lr_low[i_r]
            d_lo = lo_upp[i_o] - lo_low[i_o]
            d_ir = lo_upp[i_o] - lr_low[i_r]  # common section on the right
            d_il = lr_upp[i_r] - lo_low[i_o]  # common section on the left

            # Case 1: resampling window is smaller than or equal to the original window.
            # This is where the bug was: if an original bin is all inside the resampled bin, then
            # all flux should go into it, not then d_lr/d_lo fraction. --Natalia@IoA - 21/12/2012
            if (lr_low[i_r] > lo_low[i_o]) & (lr_upp[i_r] < lo_upp[i_o]):
                aux += 1.0

            # Case 2: resampling window is larger than the original window.
            if (lr_low[i_r] < lo_low[i_o]) & (lr_upp[i_r] > lo_upp[i_o]):
                aux += d_lo / d_lr

            # Case 3: resampling window is on the right of the original window.
            if (lr_low[i_r] > lo_low[i_o]) & (lr_upp[i_r] > lo_upp[i_o]):
                aux += d_ir / d_lr

            # Case 4: resampling window is on the left of the original window.
            if (lr_low[i_r] < lo_low[i_o]) & (lr_upp[i_r] < lo_upp[i_o]):
                aux += d_il / d_lr

            matrix[i_r, i_o] += aux

    # Fix matrix to be exactly = 1 ==> TO THINK
    # print np.sum(matrix), np.sum(lo_upp - lo_low), (lr_upp - lr_low).shape

    # Fix extremes: extrapolate if needed
    if extrap:

        bins_extrapl = np.where((lr_low < lo_low[0]))[0]
        bins_extrapr = np.where((lr_upp > lo_upp[-1]))[0]

        if (len(bins_extrapl) > 0) & (len(bins_extrapr) > 0):
            io_extrapl = np.where((lo_low >= lr_low[bins_extrapl[0]]))[0][0]
            io_extrapr = np.where((lo_upp <= lr_upp[bins_extrapr[0]]))[0][-1]

            matrix[bins_extrapl, io_extrapl] = 1.0
            matrix[bins_extrapr, io_extrapr] = 1.0

    return matrix


def logbin_ASD(log_ff, linear_ff, linear_ASD):
    """Logbins an ASD given some log spaced frequency vector.
    Inputs:
    log_ff is the final vector we want the ASD to be spaced at
    linear_ff is the original frequency vector
    linear_ASD is the ASD
    """
    matrix = resampling_matrix_nonuniform(linear_ff, log_ff)
    log_ASD = np.dot(matrix, linear_ASD)
    return log_ASD


def linear_log_ASD(log_ff, linear_ff, linear_ASD):
    """
    Creates a linear- and log-binned ASD vector from overlapping linear and log frequency vectors,
    such that the coarsest frequency vector is used.
    This avoids the problem of logbinning where the low frequency points have too
    much resolution, i.e. the FFT binwidth > log_ff[1] - log_ff[0].

    Inputs:
    linear_ff  = linear frequency vector. Will be used for low frequency points.
    log_ff     = log frequency vector.  Will be used for high frequency points.
    linear_ASD = linear ASD. Should be the same length as linear_ff, usual output of scipy.signal.welch().

    Outputs:
    fff = stitched frequency vector of linear and log points
    linlog_ASD = stitched ASD of linear and log points
    """
    df = linear_ff[1] - linear_ff[0]
    dfflog = np.diff(log_ff)
    log_index = np.argwhere(dfflog > df)[0][
        0
    ]  # first point where fflog has less resolution than the normal freq vector
    cutoff = log_ff[log_index]  # cutoff frequency
    high_fff = log_ff[log_index + 1 :]

    linear_index = np.argwhere(cutoff < linear_ff)[0][
        0
    ]  # find where the cutoff frequency is first less than the linear frequency vector
    low_fff = linear_ff[:linear_index]
    low_ASD = linear_ASD[:linear_index]

    fff = np.concatenate((low_fff, high_fff))  # make the full frequency vector

    matrix = resampling_matrix_nonuniform(linear_ff, high_fff)
    high_ASD = np.dot(matrix, linear_ASD)  # get HF part of spectrum

    linlog_ASD = np.concatenate((low_ASD, high_ASD))

    return fff, linlog_ASD
