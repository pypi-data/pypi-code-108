# Copyright (c) 2022 Jeremy G. Menzer.
# Distributed under the terms of the MIT License.
#
# This code is part of the Archaeo-mag project https://github.com/jgmenzer/archaeo-mag.
#
"""
Pre-processing Functions.
"""

import numpy as np
import scipy as sp
import pandas as pd

def clip_base(basedata, n):
    # this clips off the start and end of a file by n number
	# this is used when basedata have erroneous data at the
	# beginning and end of a survey due to the user being nearby
	# basedata is a numpy array, n is the number of data point
	# to remove
    tmp = len(basedata)-n
    tmp = basedata[n:tmp]
    return tmp

def med_despike(data, r, threshold, data_sign):
    # data is the data to be despiked, data_sign either '+' or '-'
	# data is a  numpy array
    # is if the data is positve or negative, insert data_sign=''
    # is a range factor, eg is data >/< median + range
    # threshold is the number to cut data off at, if its above/below its bad data
    if data_sign == '+':
        tmp_goodlocs = np.where(data>threshold)
        tmp_median = np.median(data.iloc[tmp_goodlocs])
        new_data = np.where(data < tmp_median-r, tmp_median, data) #for erroneous data insert the good data median
    if data_sign == '-':
        tmp_goodlocs = np.where(data<threshold)
        tmp_median = np.median(data.iloc[tmp_goodlocs]) #for erroneous data insert the good data median
        new_data = np.where(data > tmp_median+r, tmp_median, data)
    return new_data

def thres_despike(data, threshold, threshsign):
    # data is the data to be despiked, threshold is the data value cutoff, threshsign either '>' or '<'
	# data is a numpy array
    # is if you want data above or below the threshold, need to write threshsign=''
    if threshsign == '>':
        tmp_goodlocs = np.where(data>threshold)
        tmp_median = np.median(data[tmp_goodlocs])
        new_data = np.where(data < threshold, tmp_median, data) #for erroneous data insert the good data median
    if threshsign == '<':
        tmp_goodlocs = np.where(data<threshold)
        tmp_median = np.median(data[tmp_goodlocs]) #for erroneous data insert the good data median
        new_data = np.where(data > threshold, tmp_median, data)
    return new_data
	
def notch_filter(data, f_notch, fs, Q):
    # an iir notch filter, input data is data to be filtered as a numpy array
    # f_notch is the desired notch frequency in Hz,
    # fs is the data frequency in Hz and Q the quality factor/bandwith factor a 
    # higher factor decreases the bandwidth, recommend 30>
    b_notch, a_notch = sp.signal.iirnotch(f_notch, Q, fs=fs)
    filtered = sp.signal.filtfilt(b_notch, a_notch, data)
    return filtered

def pd_mad(data, window_size):
	# median absolute deviation filter in pandas dataframe format
	# data is the pandas series
    data= data
    tmp = data.rolling(window=window_size, min_periods=1, center=True).median()
    tmp2 = np.absolute(data-tmp)
    tmp_mad = tmp2.rolling(window=window_size, min_periods=1, center=True).median()
    # return the moving mad data and the moving median data 
    return tmp_mad, tmp

def pd_hampel(data, mad_data, median_data, nd):
    # data to be filtered, a pandas series
	# nd = number of deviations equivalent to standard deviations
    new_data = data.copy()
    k=1.4826
    outlier_locs = np.where(np.absolute(new_data-median_data) >= nd*k*mad_data)
    new_data.iloc[outlier_locs] = median_data.iloc[outlier_locs]
    
    return new_data