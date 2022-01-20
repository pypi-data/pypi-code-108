# Brute force coherence (Gabriele Vajente, 2016-10-18)
# LIGO-centric functions

import os
import subprocess
import numpy

try:
    from urllib.parse import urlparse
except ImportError:  # python < 3
    from urlparse import urlparse

import gwdatafind

try:
    import framel
    use_framel = True
except:
    from gwpy.timeseries import TimeSeries
    use_framel = False

# global variables for LIGO data I/O
files = []

# wrapper around the LIGO function to find where data is, returns a list of files
def find_data_path(observatory, gpsb, gpse):
    obs = observatory[0]
    urls = gwdatafind.find_urls(
        obs,
        "{}1_R".format(obs),
        int(gpsb),
        int(gpse),
        urltype='file',
    )
    return [str(urlparse(x).path) for x in urls]

# get the list of channels
def get_channel_list(opt, gpsb):
    
    files0 = find_data_path(opt.ifo, gpsb, gpsb+1)
    if not files0:
        ermsg = 'No frame files found of type {:s}1_R for ' \
                'time {:d}'.format(opt.ifo[0], int(gpsb))
        raise AttributeError(ermsg)
    os.system('/usr/bin/FrChannels ' + files0[0] + ' > bruco.channels')
    f = open('bruco.channels')
    lines = f.readlines()
    channels = []
    sample_rate = []
    for l in lines:
        ll = l.split()
        if ll[0][1] != '0':
            # remove all L0/H0 channels
            channels.append(ll[0])
            sample_rate.append(int(ll[1]))
    channels = numpy.array(channels)
    sample_rate = numpy.array(sample_rate)
    # remove temporary channel list
    os.system('rm bruco.channels')
    
    return channels, sample_rate
    
if use_framel:
    def getRawData(channel, gps, dt):
        """Read data from RAW file (using pylal):
        ch  = channel name
        gps = gps time
        dt  = duration
        """
    
        global files
    
        # get the list of frame files
        obs = channel[0:2]
        if len(files) == 0:
            files = find_data_path(obs, gps, gps+dt)
        # read data from all files
        data = numpy.array([]) 
        for f in files:
            # get the frame file start GPS and duration from the name 
            gps0 = int(f.split('-')[-2])
            gps1 = gps0 + int(f.split('-')[-1].split('.')[-2])
            # find the right time segment to load from this file
            gps0 = max(gps0, gps)
            gps1 = min(gps1, gps + dt)
            # read data and append
            x = framel.frgetvect(f, channel, gps0, gps1-gps0)
            data = numpy.concatenate([data, x[0]])
        return data, int(1/x[3][0])
else:
    def getRawData(channel, gps, dt, source=None):
        """Read data from RAW file (using gwpy):
        ch  = channel name
        gps = gps time
        dt  = duration
        """

        global files

        # get the list of frame files
        obs = channel[0:2]
        if source:
            files_ = open(source, 'r').readlines()
            files_ = [f[:-1] for f in files_]
            print('Reading %s from' % channel)
            print(files_)
            data = TimeSeries.read(files_, channel, start=gps, end=gps+dt)
        else:
            if len(files) == 0:
                files = find_data_path(obs, gps, gps+dt)
            data = TimeSeries.read(files, channel, start=gps, end=gps+dt, format='gwf.framecpp', type='adc')

        return data.value, int(data.sample_rate.to('Hz').value)
