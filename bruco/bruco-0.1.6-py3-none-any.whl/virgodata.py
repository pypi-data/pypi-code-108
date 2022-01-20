# Brute force coherence (Gabriele Vajente, 2016-10-26)
# Virgo-centric functions (Bas Swinkels, Irene Fiori)

import sys
import numpy as np
from virgotools import getChannel, FrameFile, gps2utc

# function to convert gps to UTC, taken from virgotools
def gpsUTC(gpsb):
    return gps2utc(gpsb)
  
# return the list of channels    
def get_channel_list(opt, gpsb):
    channels = []
    sample_rate = []
    channelMain = 'V1:' + opt.channel
    with FrameFile('raw') as ffl:
        with ffl.get_frame(gpsb) as frame:
            for adc in frame.iter_adc():
                fr = int(adc.contents.sampleRate)
                channel = str(adc.contents.name)
                channels.append(channel)	    
                sample_rate.append(fr)
      
    channels, sample_rate = (list(t) for t in zip(*sorted(zip(channels, sample_rate))))
    nchold = len(channels)  # number of channels before the exclusions
    #print "Found %d channels before the exclusions\n\n" % nchold
    return np.array(channels), np.array(sample_rate)

# Function to get data from raw files
def getRawData(ch, gps, dt, source="raw"):
    """Read data from RAW file:
    ch  = channel name
    gps = gps time
    dt  = duration
    """
    with getChannel(source, ch, gps, dt) as x:
        frac, whole = np.modf(x.fsample)
        if frac > 0. :
            print(">>WARNING The sampling frequency (whole:%s frac:%s Hz) is not an integer." % (whole, frac))
        #For some channels the frequency doesn't have an integer frequency, this is believed to be a bug and therefor the rounding is introduced.
        return x.data, int(np.round(x.fsample))
