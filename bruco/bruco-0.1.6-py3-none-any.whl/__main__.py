from __future__ import print_function

helpstring = """
Brute force coherence (Gabriele Vajente, 2019-03-13)

Example:
python -m bruco --ifo=H1 --channel=CAL-DELTAL_EXTERNAL_DQ 
           --calib=share/lho_cal_deltal_calibration.txt 
           --gpsb=1111224016 --length=600 --outfs=4096 --naver=100 
           --dir=./bruco_1111224016 --top=100 --webtop=20 --xlim=1:2048 
           --ylim=1e-21:1e-14 --excluded=share/lho_excluded_channels_O3.txt"""

# CHANGELOG:
#
# 2015-01-29 - added linear detrending in PSD and coherence to improve low frequency bins
# 2015-02-16 - split coherence computation into PSDs and CSDs to remove redundant 
#              computation of main channel PSD (still room to improve here)
#            - removed upsampling of channels with lower sampling rate (now coherences are
#              always computed with the minimum possible number of samples)
# 2015-02-18 - further splitting of coherence into primitive FFTs
# 2015-02-19 - allow selection of plot output format (PDF or PNG)
# 2015-02-24 - corrected typo in options lenght -> length
#            - implemented parallel processing
# 2015-06-11 - using gw_data_find to locate the GWF files
# 2015-06-16 - added calibration transfer function option
#            - added expanduser to all paths to allow use of ~
# 2015-08-19 - now bruco removes the temporary files that contains the list of channels
#            - timing information file is saved into the output directory
# 2015-01-01 - x3 faster plotting based on Michele Valentini's code
# 2016-09-19 - fixed bug in output table
# 2016-10-18 - added command line options for excluded channels file and temporary folder, 
#              updated default values   
# 2016-10-26 - added portability to Virgo environment
#            - removed old timing code
# 2016-10-28 - reverted to non packaged structure for simplicty
# 2016-11-11 - using direct frame file access to read data, instead of LAL cache (a couple 
#              of minutes faster)
# 2017-01-04 - using resample function if sampling frequency ratio is not integer
# 2017-01-05 - explicitly removing main channel from aux channel list
# 2017-01-23 - if the decimation ratio is greater than 10, decimate in mutiple steps to
#              avoid numerical instabilities
# 2017-03-08 - Virgo sampling rate is not always a power of 2, and this caused a crash
#              for some auxiliary channels with sampling rate lower than the desired
#              output. Implemented an upsamping of the aux channel to solve the issue
# 2017-04-04 - mask frequencies above Nyquist
# 2017-04-06 - fixed bug: first plot of each process was not saved
# 2017-05-25 - added option to load main channel from txt file
# ......
# ......
# 2018-12-06 - merged with Virgo version, lot of logging added for Virgo people
 
import numpy
import os
import matplotlib
matplotlib.use("Agg")
from optparse import OptionParser
from pylab import *
import time
import fnmatch
import scipy.stats
import sys
import multiprocessing
import itertools
import warnings
warnings.filterwarnings("ignore")
import traceback
import pickle
import gc #for dropping caches

#from plotly.subplots import make_subplots
#import plotly.express as px
#import plotly.graph_objects as go

from scipy.signal import resample_poly

from bruco import __version__
from bruco.functions import *
from bruco.html import markup
from bruco.multirate import *
from bruco.bns_range import bns_range
 

# some newer versions of matplotlib throw an error when labels have a '_'. So here I replace them with a blank
def enc(x):
    return x.replace('_', ' ')

##### Parallelized data access and coherence computation #################################
def parallelized_coherence(args):
    # parse input arguments
    gpsb, gpse,ntop,outfs,npoints,s,opt,ch1_ffts,f1,psd1,channels,id,chidx = args
    print("Called parallelized_coherence(), process %d" % id)

    # dictionary to store timing information
    dt = {'data': 0, 'decim': 0, 'fft': 0, 'plot': 0, 'tot': 0}
    dt['tot'] = -time.time()

    # init tables
    cohtab = zeros((int(npoints/2+1), ntop))
    idxtab = zeros((int(npoints/2+1), ntop), dtype=int)

    # initialize figure and plot
    dt['plot'] = dt['plot'] - time.time()
    if opt.plotformat != 'none':
        fig, ax = subplots(2, 1, sharex=True, figsize=(10,10))
        firstplot = True

    # initialize empty list for the erroneous channels
    errchannels = []
    dt['plot'] = dt['plot'] + time.time()

    # analyze every channel in the list
    
    for channel2,i in zip(channels,arange(len(channels))):
        try: 
            print("  Process %d: channel %d of %d: %s" % (id, i+1, len(channels), channel2))

            # read auxiliary channel
            try:
                dt['data'] = dt['data'] - time.time()
                ch2, fs2 = getRawData(channel2, gpsb, gpse-gpsb)
                dt['data'] = dt['data'] + time.time()
            except:
                print("  Process %d: some error occurred in channel %s: %s" % \
                                                            (id, channel2, sys.exc_info()))
                raise

            # check if the channel is flat, and skip it if so
            if ch2.min() == ch2.max():
                print("  Process %d: %s is flat, skipping" % (id, channel2))
                continue

            # maximum frequency which is meaningful
            maxfreq = 1e6
            
            if opt.vlogerrchannels:
                print("  The AUX.channel's",channel2,"shape",ch2.shape, "and sampling freq", fs2, "before resampling")

            # resample to outfs if needed
            dt['decim'] = dt['decim'] - time.time()
            if fs2 > outfs:
                if opt.vlogerrchannels:
                    print("  Resampling. fs2: %s > outfs: %s" % (str(fs2), str(outfs)))
                    print(">>The old check:", int(numpy.round(fs2) / outfs),"==", numpy.round(fs2) / outfs)
                    print(">>The new check:", fs2 % outfs, "==", 0)

                # check if the ratio is an integer
                if fs2 % outfs == 0:
                    if opt.vlogerrchannels:
                        print("  Resampling. Integer ratio of %s / %s" % (numpy.round(fs2), outfs))

                    # here I'm using a custom decimate function, defined in functions.py
                    ch2 = resample_poly(ch2, up=1, down=int(numpy.round(fs2) / outfs))
                    fs2 = outfs
                else:
                    # use a resample function that allows non integer ratios
                    if opt.vlogerrchannels:
                        print("  Resampling. Non-integer ratio of %s / %s" % (numpy.round(fs2), outfs))

                    print(">>Warning! High memory requirements! The resample() function will be used for the thread %s, channel %s, for the non-integer ratio of %s / %s" % (id, channel2, fs2, outfs))
                    ch2 = resample(ch2, outfs, numpy.round(fs2))
                    fs2 = outfs
            else:
                if opt.vlogerrchannels:
                    print("  Resampling. fs2: %s <= outfs: %s" % (str(fs2), str(outfs)))

                # check if the number of FFT points is an integer, otherwise upsample
                if int(numpy.round(fs2)/outfs*npoints) != numpy.round(fs2)/outfs*npoints:
                    maxfreq = int(fs2/2)
                    ch2 = resample(ch2, outfs, numpy.round(fs2))
                    fs2 = outfs
            dt['decim'] = dt['decim'] + time.time()

            if opt.vlogerrchannels:
                print("  The AUX.channel's",channel2,"shape",ch2.shape, "and sampling freq", fs2, "after resampling")
            
            ###### compute coherence
            dt['fft'] = dt['fft'] - time.time()
            # compute all the FFTs of the aux channel (those FFTs are returned already 
            # normalized so that the MATLAB-like scaled PSD is just sum |FFT|^2
            ch2_ffts = computeFFTs(ch2, int(npoints*fs2/outfs), int(npoints*fs2/outfs/2), fs2)
            # average to get PSDs and CSDs, create frequency vector
            psd2 = mean(abs(ch2_ffts)**2,1)
            f = linspace(0, int(fs2/2), int(npoints*fs2/outfs/2+1))
            csd12 = mean(conjugate(ch2_ffts)*ch1_ffts[0:int(npoints*fs2/outfs/2+1),:],1)
            # we use the full sampling PSD of the main channel, using only the bins 
            # corresponding to channel2 sampling
            c = abs(csd12)**2/(psd2 * psd1[0:len(psd2)])
            # mask frequencies above Nyquist
            c[f>=maxfreq] = 0
            dt['fft'] = dt['fft'] + time.time()

            # save coherence in summary table. Basically, cohtab has a row for each frequency 
            # bin and a number of columns which is determined by the option --top. For each 
            # frequency bin, the new coherence value is added only if it's larger than the 
            # minimum already present. Then idxtab contains again a row for each frequency
            # bin: but in this case each entry is an unique index that determines the channel 
            # that gave that coherence.
            # So for example cohtab[100,0] gives the highest coherence for the 100th frequency 
            # bin; idxtab[100,0] contains an integer id that corresponds to the channel. This 
            # id is saved in channels.txt
            for cx,j in zip(c,arange(len(c), dtype=int)):
                top = cohtab[j, :]
                idx = idxtab[j, :]
                if cx > min(top):
                    ttop = concatenate((top, [cx]))
                    iidx = concatenate((idx, [chidx + i]))
                    ii = ttop.argsort()
                    ii = ii[1:]
                    cohtab[j, :] = ttop[ii]
                    idxtab[j, :] = iidx[ii]
        
            # create the output plot, if desired, and with the desired format
            dt['plot'] = dt['plot'] - time.time()
            if opt.plotformat != "none" and opt.plotformat != 'html':
                mask = ones(shape(f))
                mask[c<s] = nan

                if opt.range:
                    bns0 = bns_range(f1, psd_plot[0:len(f1)] * float(opt.range))
                    psd_sub = psd_plot.copy()
                    psd_sub[0:len(psd2)] = psd_sub[0:len(psd2)] * sqrt(1 - c)
                    bns1 = bns_range(f1, psd_sub * float(opt.range))

                # faster plotting, create all the figure and axis stuff once for all
                if firstplot:
                    pltitle = ax[0].set_title('Coherence %s vs %s - GPS %d' % \
                                        (enc(opt.channel), enc(channel2), gpsb), fontsize='smaller')
                    line1, line2 = ax[0].loglog(f, c, f, ones(shape(f))*s, 
                                                            'r--', linewidth=1)
                    if xmin != -1:
                        ax[0].axis(xmin=xmin,xmax=xmax)
                    else:
                        ax[0].axis(xmax=outfs/2)
                    ax[0].axis(ymin=s/2, ymax=1)
                    ax[0].grid(True)
                    ax[0].set_ylabel('Coherence')
                    line3, = ax[1].loglog(f1, psd_plot[0:len(f1)])
                    line4, = ax[1].loglog(f, psd_plot[0:len(psd2)] * sqrt(c) * mask, 'r')

                    if opt.range:
                        plttitle2 = ax[1].set_title('Range: original %.2f Mpc - subtracted %.2f Mpc' % \
                                                  (bns0, bns1), fontsize='smaller')
                        line5, = ax[1].loglog(f1, psd_sub) 
                    if xmin != -1:
                        ax[1].axis(xmin=xmin, xmax=xmax)
                    else:
                        ax[1].axis(xmax=outfs/2)
                    if ymin != -1:
                        ax[1].axis(ymin=ymin, ymax=ymax)
                    ax[1].set_xlabel('Frequency [Hz]')
                    ax[1].set_ylabel('Spectrum')
                    if opt.range:
                        ax[1].legend(('Target channel', 'Noise projection', 'Coherence subtraction'))
                    else:
                        ax[1].legend(('Target channel', 'Noise projection'))

                    ax[1].grid(True)
                    firstplot = False
                else:
                    # if not the first plot, just update the traces and title
                    pltitle.set_text('Coherence %s vs %s - GPS %d' % \
                                                        (enc(opt.channel), enc(channel2), gpsb))
                    line1.set_data(f, c)
                    line4.set_data(f, psd_plot[0:len(psd2)] * sqrt(c) * mask)
                    if opt.range:
                        line5.set_data(f1, psd_sub)
                        plttitle2.set_text('Range: original %.2f Mpc - subtracted %.2f Mpc' % \
                                                  (bns0, bns1))
                fig.savefig(os.path.expanduser(opt.dir) + '/%s.%s' % \
                        (channel2.split(':')[1], opt.plotformat), format=opt.plotformat)
            elif opt.plotformat == 'html':
                # use plotly
                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.02)
                fig.add_trace(go.Scatter(x=f, y=c, mode="lines", name='Coherence',
                                             line_color='blue',
                                             legendgroup='Coherence', hovertemplate='freq: %{x:.2f}<br>coher: %{y:.4f}'), row=1, col=1)
                mask = ones(shape(f))
                mask[c<s] = nan
                fig.add_trace(go.Scatter(x=f, y=psd_plot[0:len(psd2)] * sqrt(c) * mask, mode="lines",
                                                  line_color='blue', name='Noise projection',
                                                  legendgroup='Noise projection',
                                                  hovertemplate='freq: %{x:.2f} Hz<br>ASD: %{y:.4f}'), row=2, col=1)
                fig.add_trace(go.Scatter(x=f, y=psd_plot[0:len(psd2)] * sqrt(1-c) * mask, mode="lines",
                                                  line_color='red', name='Coherence subtraction',
                                                  legendgroup='Coherence subtraction',
                                                  hovertemplate='freq: %{x:.2f} Hz<br>ASD: %{y:.4f}'), row=2, col=1)
                fig.add_trace(go.Scatter(x=f, y=ones(shape(f))*s, mode="lines", name='Threshold', line_color='red',
                                                       legendgroup='Threshold', line={'dash':'dot'},
                                                  hovertemplate='freq: %{x:.2f} Hz<br>coher: %{y:.4f}'), row=1, col=1)
                fig.add_trace(go.Scatter(x=f, y=psd_plot[0:len(f1)], mode="lines", name='Target signal',
                                                       legendgroup='Target signal', line_color='black',
                                                  hovertemplate='freq: %{x:.2f} Hz<br>ASD: %{y:.4f}'), row=2, col=1)
                fig.update_xaxes(type="log")
                fig.update_yaxes(type="log", exponentformat='power')
                fig.update_layout(title='Coherence %s vs %s - GPS %d' % (enc(opt.channel), enc(channel2), gpsb))
                fig.update_layout(legend_tracegroupgap=5, template='plotly')
                fig.update_xaxes(title_text='Frequency [Hz]', row=2, col=1)
                fig.update_yaxes(title_text='Coherence', row=1, col=1)
                fig.update_yaxes(title_text='Spectrum', row=2, col=1)
                fig.update_layout(hoverlabel=dict(bgcolor="white", font_size=10))

                if xmin != -1:
                    fig.update_xaxes(range=[log10(xmin),log10(xmax)])
                else:
                    fig.update_xaxes(range=[-1,log10(outfs/2)])
                fig.update_yaxes(range=[log10(s/2),0], row=1, col=1)
                if ymin != -1:
                    fig.update_yaxes(range=[log10(ymin),log10(ymax)], row=2, col=1)

                fig.write_html(os.path.expanduser(opt.dir) + '/%s.%s' % \
                            (channel2.split(':')[1], opt.plotformat), include_plotlyjs='cdn')
 
            dt['plot'] = dt['plot'] + time.time()
            del ch2, c, f

        except KeyboardInterrupt:
            print(">>SIGINT received.")
            raise
        except:
            print(">>ERROR! Process %s, Channel %s." % (id, channel2))
            print(sys.exc_info())
            if opt.vlogerrchannels:
                errchannels.append(str(channel2)+"\n"+traceback.format_exc())
                #errchannels.append(str(channel2)+"\n"+str(sys.exc_info()))
                print(traceback.format_exc())
                #print sys.exc_info()
            else:
                errchannels.append(str(channel2))
            #It should be clear that it also catches C-c
            #TODO make separate exception for the siginterrupt from keyboard.
            continue
        if opt.dropcaches:
            gc.collect()

    del fig
    print("  Process %s concluded" % id)
    dt['tot'] = dt['tot'] + time.time()
    return cohtab, idxtab, id, dt, errchannels 
    
if __name__ == '__main__':
    # this file contains the list of channels to exclude (default)
    exc = 'share/bruco_excluded_channels.txt'
    # where to save temporary gwf cache (default)
    scratchdir = '~/tmp'

    # this variable will contain the calibration transfer function, need to
    # declare it here to share them with the parallel processes
    calibration = []
    psd_plot = []

    ##### Define and get command line options ################################################
    parser = OptionParser(usage=helpstring, version="bruco %s" % __version__)
    parser.add_option("-c", "--channel", dest="channel",
                      default='OAF-CAL_DARM_DQ',
                      help="name of the target channel", metavar="Channel")
    parser.add_option("-F", "--file", dest="file",
                      default='',
                      help="specify an ASCII file containing the data to be " +\
                           "used as the main channel. Any channel specified " +\
                           "with the --channel option will be ignored. " +\
                           "The sampling frequency will be determined from the " +\
                           "number of samples read from the text file and " + \
                           "the specified time duration", metavar="File")
    parser.add_option("-i", "--ifo", dest="ifo",
                      default="",
                      help="interferometer prefix [H1, L1, V1] (no default, must specify)", metavar="IFO")
    parser.add_option("-g", "--gpsb", dest="gpsb",
                      default='1090221600',
                      help="start GPS time (-1 means now)", metavar="GpsTime")
    parser.add_option("-l", "--length", dest="dt",
                      default='600',
                      help="amount of data to use (in seconds)", metavar="Duration")
    parser.add_option("-o", "--outfs", dest="outfs",
                      default='8192',
                      help="sampling frequency of the output results " + \
                           "(coherence will be computed up to outfs/2 " +\
                           "if possible)", metavar="OutFs")
    parser.add_option("-n", "--naver", dest="nav",
                      default='300',
                      help="number of averages", metavar="NumAver")
    parser.add_option("-d", "--dir", dest="dir",
                      default='bruco_1090221600',
                      help="output directory", metavar="DestDir")
    parser.add_option("-t", "--top", dest="ntop",
                      default='100',
                      help="number of top coherences saved (for each frequency) " +\
                           "in the datafiles idxtab.txt cohtab.txt", metavar="NumTop")
    parser.add_option("-w", "--webtop", dest="wtop",
                      default='20',
                      help="num. of top coherences written to the web page, for each frequency bin", metavar="NumTop")
    parser.add_option("-m", "--minfs", dest="minfs",
                      default='32',
                      help="minimum sampling frequency of aux channels, skip those with lower sampling rate", metavar="MinFS")
    parser.add_option("-p", "--plot", dest="plotformat",
                      default='png',
                      help="plot format (png, pdf or none)", metavar="PlotFormat")
    parser.add_option("-N", "--nproc", dest="ncpu",
                      default='-1',
                      help="number of processes to lauch (if not specified, use all cores)", metavar="NumProc")
    parser.add_option("-C", "--calib", dest="calib",
                      default='',
                      help="name of a text file containing the calibration "+\
                           "transfer function to be applied to the target "+\
                           "channel spectrum, in a two column format  " +\
                           "(frequency, absolute value)", metavar="Calibration")
    parser.add_option("-X", "--xlim", dest="xlim",
                      default='',
                      help="frequency axis limit, in the format fmin:fmax", metavar="XLim")
    parser.add_option("-Y", "--ylim", dest="ylim",
                      default='',
                      help="PSD y axis limits, in the format ymin:ymax", metavar="YLim")
    parser.add_option("-e", "--excluded", dest="excluded",
                      default='',
                      help="list of channels excluded from the coherence computation", 
                                                                        metavar="Excluded")
    parser.add_option("-T", "--tmp", dest="scratchdir",
                      default=scratchdir,
                      help="temporary file directory", metavar="Tmp")
    parser.add_option("-A", "--auxchannels", dest="auxchs",
                      default='',
                      help=" only channels whose name contains ""String"" will be used for coherence computation", metavar="Aux")
    parser.add_option("--vlogerrchannels", dest="vlogerrchannels", action='store_true',
                      default=False,
                      help="if present the parallelized_coherence() logs channels' names that failed to a <DIR>/errchannels.log with additional information (trace calls, etc.)", 
                                                                        metavar="VLogErrChannels")
    parser.add_option("--errchannelslogfile", dest="errchannelslogfile",
                      default="errchannels.log",
                      help="the filename for the errornous channels that fail during the parallelized_coherence() execution, default to errchannels.log", 
                                                                        metavar="ErrChannelsLogFile")
    parser.add_option("--source", dest="source",
                      default="raw",
                      help="the source of the ffl file (raw, /virgoData/ffl/raw.ffl, trend, ...) supplied to the GetChannel function.", metavar="Source")
    
    parser.add_option("--cohcut", dest="cohcut", default=0.5, help="the critical value of the coherence to choose for the cohshort.txt (only the most significant auxiliry channels with coherence >= cohcut. Default value = 0.5", metavar="CohCut") 
    
    parser.add_option("--dropcaches", dest="dropcaches", action='store_true',
                      default=False,
                      help="if present the parallelized_coherence() will gc.collect() after each loop (to help with the cache memory managment)",
                      metavar="DropCaches")
    
    parser.add_option("--cohshortfile", dest="cohshortfile",
                      default="cohshort.txt",
                      help="the short coherence (>= cohcut) table filename. default: cohshort.txt",
                                                                        metavar="CohShortFile")
    
    parser.add_option("--cohshort", dest="cohshort", action='store_true',
                      default=False,
                      help="if present, bruco will store a highest coherence channels (>=cohcut) in cohshort.txt.",
                      metavar="CohShort")
    
    parser.add_option("--range", dest="range", 
                      default=None,
                      help="if present, BruCo will compute the BNS range for the original and subracted spectra. User must pass the scaling factor to convert the signal to strain",
                      metavar="Range")

    (opt,args) = parser.parse_args()
    
    if opt.plotformat == 'html':
        try:
            from plotly.subplots import make_subplots
            import plotly.express as px
            import plotly.graph_objects as go
        except:
            try:
                import plotly
                print("WARNING: Your plotly version (" + plotly.__version__ + ") is too old, you need version 5.2.1 or later.")
            except:
                print("WARNING: You need the plotly library version 5.2.1 or later.")
            print("         Interactive plots disabled, saving plots in PNG format.")
            opt.plotformat = 'png'  

    gpsb = int(opt.gpsb)
    gpse = gpsb + int(opt.dt)
    dt = int(opt.dt)
    outfs = int(opt.outfs)
    nav = int(opt.nav)
    ntop = int(opt.ntop)
    wtop = int(opt.wtop)
    minfs = int(opt.minfs)
    aux = str(opt.auxchs,)
    
    
    # see if the user specified custom plot limits
    if opt.xlim != '':
        xmin, xmax = map(lambda x:float(x), opt.xlim.split(':'))
    else:
        xmin, xmax = -1, -1
    
    if opt.ylim != '':
        ymin, ymax = map(lambda x:float(x), opt.ylim.split(':'))
    else:
        ymin, ymax = -1, -1
    
    # parse list of excluded channels. If not specified use default
    if opt.excluded != '':
        exc = opt.excluded
        
    ###### Prepare folders and stuff for the processing loops ################################
    
    print("**********************************************************************")
    print("**** BruCo version 2018-12-06 - parallelized multicore processing ****")
    print("**********************************************************************")
    
    # determine which IFO the user wants and import the right functions
    if opt.ifo == '':
        print(helpstring)
        exit()
    elif opt.ifo == 'H1' or opt.ifo == 'L1':
        from bruco.ligodata import *
        from gwpy.time import tconvert
    elif opt.ifo == 'V1':
        from bruco.virgodata import *
    else:
        print("Unknown IFO %s" % opt.ifo)
        exit()
    
    print()
    print("Analyzing data from gps %d to %d.\n" % (gpsb, gpse))
    print()
    
    ###### Extract the list of channels and remove undesired ones ############################
    channels, sample_rate = get_channel_list(opt, gpsb)
    
    
    # keep only channels with high enough sampling rate
    idx = numpy.where(sample_rate >= minfs)[0]
    channels = channels[idx]
    sample_rate = sample_rate[idx]
    
    # load exclusion list from file
    f = open(exc, 'r')
    L = f.readlines()
    excluded = []
    for c in L:
        c = c.split()
        if len(c):
            excluded.append(c[0])
    f.close()
    
    # delete excluded channels, allowing for unix-shell-like wildcards
    idx = ones(shape(channels), dtype='bool')
    for c,i in zip(channels, arange(len(channels))):
        if c == opt.ifo + ':' + opt.channel:
            # remove the main channel
            idx[i] = False
        for e in excluded:
            if fnmatch.fnmatch(c, opt.ifo + ':' + e):
                idx[i] = False
                            
    # delete all channels whose name does not contain the AUX substring         
    idxaux = zeros(shape(channels), dtype='bool')
    if aux != '':
        print("aux = %s \n" % (aux))
        string = aux.split(",")
        for ss in string:
            print("substring = %s \n" % (ss))
            for c,i in zip(channels, arange(len(channels))):
                if c.find(ss) > -1:
                    print("found channel = %s \n" % (channels[i]))
                    idxaux[i] = True                                
        
        idx = numpy.logical_and(idx, idxaux)
    
    channels = channels[idx]
    
    # make list unique, removing repeated channels, if any
    channels = unique(channels)
   
    # save reduced channel list on textfile, creating the output directory if needed
    try:
        os.stat(os.path.expanduser(opt.dir))
    except:
        os.mkdir(os.path.expanduser(opt.dir))
    
    
    f = open(os.path.expanduser(opt.dir) + '/channels.txt', 'w')
    for c in channels:
        f.write("%s\n" % (c))
    f.close()
    nch = len(channels)
    
    print("Found %d channels\n\n" % nch)
    
    ###### Main processing starts here #######################################################
    
    print(">>>>> Processing all channels....")
    
    # get data for the main target channel
    if opt.file == '':
        print("Reading main channel %s from frame" % opt.channel)
        try:
            ch1, fs1 = getRawData(opt.ifo + ':' + opt.channel, gpsb, gpse-gpsb, source=opt.source)
        except:
            print("Could not find data in raw files, using GwPy")
            from gwpy.timeseries import TimeSeries
            x = TimeSeries.fetch(opt.ifo + ':' + opt.channel, gpsb, gpse)
            fs1 = int(1.0/x.dt.value)
            ch1 = x.value
    else:
        print("Reading main channel from file %s" % opt.file)
        if opt.file[-4:] == '.txt':
            ch1 = numpy.loadtxt(opt.file)
            fs1 = len(ch1)/(gpse-gpsb)
        elif opt.file[-4:] == ".gwf":
            from gwpy.timeseries import TimeSeries
            x = TimeSeries.read(opt.file, opt.ifo + ':' + opt.channel, start=gpsb, end=gpse)
            ch1 = x.value
            fs1 = int(x.sample_rate.value)
        elif opt.file[-7:] == '.pickle':
            import pickle
            x = pickle.load(open(opt.file, 'rb'))
            ch1 = x[opt.channel]
            fs1 = len(ch1)/(gpse-gpsb)
        else:
            print('File format not recognized for ' + opt.file)
            exit()
        print("Read %d samples > sampling rate is %d" % (len(ch1), fs1))

    # default outfs to main channel sampling frequency
    if outfs == -1:
        outfs = fs1
    # check if the main channel is flat
    if ch1.min() == ch1.max():
        print("Error: main channel is flat!") 
        exit()
    
    # resample main channel to output frequency if needed
    if fs1 > outfs:
        # check if the ratio is an integer
        if fs1 % outfs == 0:
            # here I'm using a custom decimate function, defined in functions.py
            ch1 = resample_poly(ch1, up=1, down=int(numpy.round(fs1) / outfs))
            fs1 = outfs
        else:
            # use a resample function that allows non integer ratios
            ch1 = resample(ch1, outfs, numpy.round(fs1))
            fs1 = outfs
    
    # check if the main channel is flat
    if ch1.min() == ch1.max():
        print("Error: main channel is flat!")
        exit()
                
    # determine the number of points per FFT
    npoints = pow(2,int(log((gpse - gpsb) * outfs / nav) / log(2)))
    print("Number of points = %d\n" % npoints)
    fres = float(outfs) / float(npoints)
    print("Frequency resolution of FFT = %f Hz\n" % fres)
    
    # compute the main channels FFTs and PSD. Here I save the single segments FFTS,
    # to reuse them later on in the CSD computation. In this way, the main channel FFTs are
    # computed only once, instead of every iteration. This function returns the FFTs already
    # scaled is such a way that PSD = sum |FFT|^2, with MATLAB-like normalization.
    ch1_ffts = computeFFTs(ch1, npoints*fs1/outfs, int((npoints*fs1/outfs)/2), fs1)
    psd1 = mean(abs(ch1_ffts)**2,1)
    f1 = linspace(0, fs1/2, int(npoints*fs1/outfs/2+1))
    
    ### Read the calibration transfer function, if specified
    if opt.calib != '':
        # load from file
        cdata = numpy.loadtxt(opt.calib)
        # interpolate to the right frequency bins
        calibration = numpy.interp(f1, cdata[:,0], cdata[:,1])
    else:
        # no calibration specified, use unity
        calibration = numpy.ones(shape(f1))
    
    psd_plot = numpy.sqrt(psd1) * calibration
    
    # compute the coherence confidence level based on the number of averages used in the PSD
    s = scipy.stats.f.ppf(0.95, 2, 2*nav)
    s = s/(nav - 1 + s)
    
    ##### Start parallel multiprocessing computations ########################################
    
    # split the list of channels in as many sublist as there are CPUs
    if opt.ncpu == "-1":
        ncpu = multiprocessing.cpu_count()
    else:
        ncpu = int(opt.ncpu)
    
    # try the most even possible distribution of channels among the processes
    nchannels = len(channels)
    n = int(nchannels / ncpu)
    N1 = int( (nchannels / float(ncpu) - n) * ncpu)
    ch2 = []
    chidx = []
    for i in range(N1):
        ch2.append(channels[i*(n+1):(i+1)*(n+1)])
        chidx.append(i*(n+1))
    for i in range(ncpu-N1):
        ch2.append(channels[N1*(n+1)+i*n:N1*(n+1)+(i+1)*n])
        chidx.append(N1*(n+1)+i*n)
    
    # start a multiprocessing pool
    print(">>>>> Starting %d parallel processes..." % ncpu)
    if ncpu > 1:
        pool = multiprocessing.Pool(ncpu)
    
    
    # Build the list of arguments
    args = []
    for c,i in zip(ch2,range(len(ch2))):
        args.append([gpsb, gpse, ntop, outfs, npoints, s, 
                        opt, ch1_ffts, f1, psd1, c, i, chidx[i]])
    
    # Start all the processes
    if ncpu > 1:
        results = pool.map(parallelized_coherence, args)
    else:
        results = [parallelized_coherence(args[0])]
    
    
    print(">>>>> Parallel processes finished...")
    
    
    
    ###### put all results together ##########################################################
    
    # first step, concatenate the tables
    x = list(zip(*results))
    cohtab = np.concatenate(x[0], axis=1)
    idxtab = np.concatenate(x[1], axis=1)
    
    # save timing info
    timing = x[3]
    with open(os.path.expanduser(opt.dir) + '/timing.pickle', 'wb') as timingfile:
        pickle.dump(timing, timingfile)
    
    errchannellist = np.concatenate(x[4],axis=0)
    
    
    # then sort in order of descending coherence for each bin
    for j in arange(shape(cohtab)[0]):
        ccoh = cohtab[j,:]
        iidx = idxtab[j,:]
        ii = ccoh.argsort()
        cohtab[j, :] = cohtab[j,ii]
        idxtab[j, :] = idxtab[j, ii]
    # Finally, keep only the top values, which are the last columns
    cohtab = cohtab[:,-ntop:]
    idxtab = idxtab[:,-ntop:]
    
    ###### Here we save the results to some files in the output directory ####################
    
    # save the coherence tables to files
    numpy.savetxt(os.path.expanduser(opt.dir) + '/cohtab.txt', cohtab)
    numpy.savetxt(os.path.expanduser(opt.dir) + '/idxtab.txt', idxtab)
    # save mainchannel fft to file # irene 03/06/2017
    numpy.savetxt(os.path.expanduser(opt.dir) + '/ch1fft.txt',numpy.sqrt(mean(abs(ch1_ffts)**2,1)))
    numpy.savetxt(os.path.expanduser(opt.dir) + '/freq.txt',f1)
    
    numpy.savetxt(os.path.expanduser(opt.dir)+'/'+str(opt.errchannelslogfile),errchannellist,fmt='%s')
    
    ###### And we generate the HTML report #########################################
    
    print(">>>>> Generating report....")
    
    # get list of files, since they corresponds to the list of plots that have been created
    command = 'ls %s/*.%s' % (os.path.expanduser(opt.dir), opt.plotformat)
    p = os.popen(command)
    L = p.readlines()
    files = [l.split('/')[-1].rstrip().split('.')[0] for l in L]
 
    # open web page
    page = markup.page( )
    page.init( title="Brute force Coherences",
               footer="(2018)  <a href=mailto:vajente@caltech.edu>vajente@caltech.edu</a>" )
    
    
    # first section, top channels per frequency bin
    nf,nt = shape(cohtab)
    freq = linspace(0,outfs/2,nf)
    
    if opt.ifo == 'H1' or opt.ifo == 'L1':
        d = tconvert(gpsb)
        page.h1('Top %d coherences of %s with auxiliary channels' % (wtop, opt.channel))
        page.h2('GPS %d + %d s [%04d/%02d/%02d %02d:%02d:%02d UTC]' % (gpsb, dt, d.year, d.month, d.day, d.hour, d.minute, d.second))
    elif opt.ifo == 'V1':
        page.h1('%s, top %d coherences at all frequencies' % (opt.channel, wtop))
        d=gpsUTC(gpsb)
        page.h2('GPS %d + %d s, UTC %d:%d:%d  %d/%d/%d + %d s' % (gpsb, dt, d.hour, d.minute, d.second, d.year, d.month, d.day, dt))
        page.h4('Excluded channels: %s' % (excluded))
        if aux != '':
            page.h4('Coherence computed only for channels containing strings: %s' % (aux))
        #Full call for the reference.
        bruco_call_full = ""                                                             
        for arg in sys.argv:                                                             
            bruco_call_full = bruco_call_full + " " + arg
        page.h4("Bruco's call: %s" % bruco_call_full)
    
    page.table(border=1, style='font-size:12px')
    page.tr()
    page.td(bgcolor="#5dadf1")
    page.h3('Frequency [Hz]')
    page.td.close()
    page.td(colspan=ntop, bgcolor="#5dadf1")
    page.h3('Top channels')
    page.td.close()
    page.tr.close()
    
    if opt.cohshort:
        cohshortfile=open(os.path.expanduser(opt.dir)+'/'+str(opt.cohshortfile), 'w')
        cohtab_maxelements = np.argmax(cohtab,axis=1) 
        aux_string=''
        if aux != '':
            aux_string=aux
        else:
            aux_string="All"
        print("Highest coherence channels (%s, Coh>=%3.2f)\n" % (aux ,opt.cohcut), file=cohshortfile)
        print("freq     coh   channel", file=cohshortfile)
        print("-------- ----- ------------------", file=cohshortfile)
        for i in np.arange(0,cohtab.shape[0]):
            if cohtab[i,cohtab_maxelements[i]] >= opt.cohcut:
                print("%8.3f %4.3f %s" % (freq[i], cohtab[i,cohtab_maxelements[i]], (channels[int(idxtab[i,cohtab_maxelements[i]])]).split(':')[1]), file=cohshortfile)
        cohshortfile.close()
    
    
    # here we create a huge table that contains, for each frequency bin, the list of most 
    # coherent channels, in descending order. The cell background color is coded from white 
    # (no coherence) to red (coherence 1)
    for i in range(nf):
        page.tr()
        page.td(bgcolor="#5dadf1")
        page.add("%.2f" % freq[i])
        page.td.close()
        for j in range(wtop):
            # write the channel only if the coherence in above the significance level
            if cohtab[i,-(j+1)] > s:
                page.td(bgcolor=cohe_color(cohtab[i,-(j+1)]))
                ch = (channels[int(idxtab[i,-(j+1)])]).split(':')[1]
                if opt.plotformat != "none":
                    page.add("<a target=_blank href=%s.%s>%s</a><br>(%.2f)"
                             % (ch, opt.plotformat, newline_name(ch), cohtab[i,-(j+1)]))
                else:
                    page.add("%s<br>(%.2f)" \
                             % (newline_name(ch), cohtab[i,-(j+1)]))
            else:
                page.td(bgcolor=cohe_color(0))
    
            page.td.close()
        page.tr.close()
    
    page.table.close()
    
    # second section, links to all coherence plots
    if len(files)>0:
        page.h1('Coherence with all channels ')
        page.h2('GPS %d (%s) + %d s' % (gpsb, gps2str(gpsb), dt))
    
        N = len(files)
        m = 6     # number of channels per row
        M = int(N / m + 1)
    
        page.table(border=1)
        for i in range(M):
            page.tr()
            for j in range(m):
                if i*m+j < N:
                    page.td()
                    page.add('<a target=_blank href=%s.%s>%s</a>' % \
                                                        (files[i*m+j], opt.plotformat, files[i*m+j]))
                    page.td.close()
                else:
                    page.td()
                    page.td.close()
    
            page.tr.close()
    
        page.table.close()
        page.br()
    
    page.h2('Excluded channels:')
    page.code('  '.join(excluded))
    if aux != '':
        page.add('Coherence computed only for channels containing strings: %s' % (aux))
    # Command call for reference
    page.h2('BruCo call string')
    page.code(' '.join(sys.argv))
    page.p()
    
    # That's the end, save the HTML page
    fileid = open(os.path.expanduser(opt.dir)  + '/index.html', 'w')
    print(page, file=fileid)
    fileid.close()
