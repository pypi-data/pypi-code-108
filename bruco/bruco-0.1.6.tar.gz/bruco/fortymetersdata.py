# Brute force coherence (Gabriele Vajente, 2017-11-17)
# 40m-centric functions

import os
#from pylal import frutils, Fr
import subprocess
from pylab import *
import numpy
import nds2

# global variables for LIGO data I/O
files = []

# get the list of channels
def get_channel_list(opt, gpsb):
    
    conn = nds2.connection('nds40.ligo.caltech.edu')
    ch = conn.find_channels('C1:*DQ')
    channels = [c.name for c in ch]
    sample_rate = [c.sample_rate for c in ch]
   
    return array(channels), array(sample_rate)
    
def getRawData(channel, gps, dt):
    """Read data from RAW file:
    ch  = channel name
    gps = gps time
    dt  = duration
    """

    conn = nds2.connection('nds40.ligo.caltech.edu')
    buf = conn.fetch(gps, gps+dt, [channel])
    return buf[0].data, int(buf[0].length/dt)

