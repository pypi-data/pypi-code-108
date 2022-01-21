# Copyright (c) 2022 Jeremy G. Menzer.
# Distributed under the terms of the MIT License.
#
# This code is part of the Archaeo-mag project https://github.com/jgmenzer/archaeo-mag.
#
"""
Depth Estimation Functions.
"""

import numpy as np

def half_max_all_dir(x, y, z, sampling):
"""
	note this returns data that still needs the sensor height subtracted
	computes the HW in 360 degrees of the maximum z value in a data window
	x, y, z are 1d numpy arrays of data
	sampling is the line interpolation spacing, or number of values to interp
	between the current data resolution.
"""
    
    lines = make_all_direction_profiles(x, y, z)
    iterator =  np.arange(0,180,1)
    hm_data = []
    for i in iterator:
        samples = find_samples_pdist((lines[0][i],lines[1][i]), (lines[2][i],lines[3][i]), sampling)
        profile = extract_profile(x, y, z, (lines[0][i],lines[1][i]), (lines[2][i],lines[3][i]), samples)
        tmplocs = np.where(~np.isnan(profile[3]))
        newz = profile[3][tmplocs]
        tmpdist = profile[2][tmplocs]
        length = len(tmpdist)
        newdist = np.arange(0,length,(1./sampling))
        hm_tmp = calc_half_max(newdist, newz)
        hm_data.append(hm_tmp)
        
    hm_data = np.asarray(hm_data)

    fwhm = hm_data[:,0]
    hm_n2 = hm_data[:,1]
    hm = hm_data[:,2]
    
    return fwhm, hm_n2, hm	

def make_all_direction_profiles(x, y, z):
	# makes 180 lines (360 deg) around the max z value
    xmin = np.min(x)
    xmax = np.max(x)
    ymin = np.min(y)
    ymax = np.max(y)
    zmax = np.max(z)
    zmaxi = np.where(z==zmax)
    if len(zmaxi) > 1:
        zmaxi = zmaxi[0]
    xp = x[zmaxi]
    xp = xp[0]
    yp = y[zmaxi]
    yp = yp[0]
    
    topdist = ymax-yp
    rightdist = xmax-xp
    bottomdist = yp-ymin
    leftdist = xp-xmin
    
    length = np.sqrt((((xmax-xmin)**2)+(ymax-ymin)**2))
    deg = np.arange(0,180,1)
    
    northy = []
    northx = []
    southy = []
    southx = []
    
    for d in deg:
        
        northy.append(yp+(length * np.sin(np.deg2rad(d))))
        northx.append(xp+(length * np.cos(np.deg2rad(d))))
        southy.append(yp-(length * np.sin(np.deg2rad(d))))
        southx.append(xp-(length * np.cos(np.deg2rad(d))))
    
    return northx, northy, southx, southy


def find_samples_pdist(point1, point2, sampling):
    # points are in x, y, samping is # per unit
    dist = np.sqrt(((point2[0]-point1[0])**2)+((point2[1]-point1[1])**2))
    samples = np.round((dist*sampling),0)
    samples = samples.astype(int)
    
    return samples

def calc_half_max(profile_dist, profile_data):
	# note this returns data that still needs the sensor height subtracted
    hm_locs = find_half_max_locs2(profile_data)
    if np.isnan(hm_locs[0][0])== True or np.isnan(hm_locs[0][1])==True:
        fwhm=np.nan
        hm=np.nan
        hm_n2=np.nan
    else:
        fwhm = np.abs(profile_dist[hm_locs[1][0]]-profile_dist[hm_locs[1][1]])
        hm = fwhm/2.
        hm_n2 = hm*1.3
    
    return fwhm, hm_n2, hm

def find_half_max_locs2(data):
    max_data = np.max(data)
    half_max_data = max_data/2.
    max_index = np.where(data == max_data)
    max_index = int(max_index[0])
    
    #tmp = find_points_along_slope(data[:max_index], half_max_data)
    
    L_nearest, L_index = find_points_left_slope(data[:max_index], half_max_data)
    R_nearest, R_index = find_points_right_slope(data[max_index:], half_max_data)
    
    R_index +=max_index

    indexes = (L_index, R_index)
    nearest = (L_nearest, R_nearest)
        
    return nearest, indexes

def find_points_left_slope(data, point):
    tmp = np.where(data <= point)
    tmp=np.squeeze(tmp, axis=(0))
    if len(tmp) > 0: # note work with 1
        tmp = np.max(tmp)
        nearest = data[tmp]
        index = tmp
    else:
        #tmp = np.min(data)
        nearest = np.nan
        index = np.nan
    return nearest, index

def find_points_right_slope(data, point):
    tmp = np.where(data <= point)
    tmp=np.squeeze(tmp, axis=(0))
    if len(tmp) > 0:
        tmp = np.min(tmp)
        nearest = data[tmp]
        index = tmp
    else:
        nearest = np.nan
        index = np.nan
    return nearest, index

def multi_height_profile(profile_1, profile_2, h_1, h_2):
	# calculates the multi-height depth estimate
	# h_1 and h_2 are the survey heights (lower and higher)
	# profile 1 and 2 are numpy 1d arrays of profile (could also be a grid)
	#returns estimates with SI = 3, 2.5, 2, 1
    max_1 = np.max(profile_1)
    max_1_index = np.where(profile_1 == max_1)
    max_2 = profile_2[max_1_index] # use exact location above lower profile max point
    
    #calculate the distance estimations for all 3 structural indexes
    depth_est_n3 = (h_2 - h_1 * (max_1/max_2)**(1./3.))/((max_1/max_2)**(1./3.)-1.)
    depth_est_n25 = (h_2 - h_1 * (max_1/max_2)**(1./2.5))/((max_1/max_2)**(1./2.5)-1.)
    depth_est_n2 = (h_2 - h_1 * (max_1/max_2)**(1./2.))/((max_1/max_2)**(1./2.)-1.)
    depth_est_n1 = (h_2 - h_1 * (max_1/max_2)**(1./1.))/((max_1/max_2)**(1./1.)-1.)
    ####NOTE these return the depth below surface
    
    return depth_est_n3, depth_est_n25, depth_est_n2, depth_est_n1