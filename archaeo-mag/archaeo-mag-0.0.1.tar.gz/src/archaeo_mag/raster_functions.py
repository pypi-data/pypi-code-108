# Copyright (c) 2022 Jeremy G. Menzer.
# Distributed under the terms of the MIT License.
#
# This code is part of the Archaeo-mag project https://github.com/jgmenzer/archaeo-mag.
#
"""
Raster Functions.
"""

import numpy as np
from scipy import ndimage as ip

def make_grid(xmin, xmax, ymin, ymax, xspacing, yspacing, rounding):
    # note - this should be at cell centers
	# makes a grid of evenly spaced data in numpy 1D arrays
    x = np.arange((xmin+(xspacing/2.)), (xmax+(xspacing/2.)), xspacing)
    y = np.arange((ymin+(yspacing/2.)), (ymax+(yspacing/2.)), yspacing)
    gx, gy = np.round(np.meshgrid(x,y),rounding)
    gx = gx.ravel()
    gy = gy.ravel()
    return gx, gy


def idw(xz, yz, zz, x, y, p, xs, ys):
	# perform an inverse distance weighted interpolation
	# xz is original x values, yz is original y values, zz is original z values
	# all are in numpy 1d arrays. x and y are the new data locations in numpy 1d
	# arrays. p is power of interpolation, xs, and ys are the search window dimensions
	# returns a numpy 1d array of the new interpolated z values

    zfinal = []
    for ix, iy in zip(x, y): 

        ellipse = np.where(((((xz-ix)**2)/(xs**2)) + (((yz-iy)**2)/ys**2)) <=1 )
        ellipse_dists = ((((xz[ellipse]-ix)**2)/(xs**2)) + (((yz[ellipse]-iy)**2)/ys**2))
    
        weights = (1./ellipse_dists)**2
        w_sum = np.sum(weights)
        weights = weights/w_sum
        z_ellipse = zz[ellipse]*weights
        zfinal.append(np.sum(z_ellipse))

    zfinal = np.asarray(zfinal)        
    return zfinal

def utm_to_local(utmx, utmy, utmxyA, utmxyB, localxyA, localxyB):
    # transformation of utm to local data using a line AB
	# utmx and utmy inputs are numpy 1d arrays of original data
	# utmxyA and utmxyB are a,y coords of the two reference points in UTM
    # localxyA and localxyB are the coords of the two reference points in local coords
	
    #transform equations/scaling
    utmscale = np.sqrt(((utmxyB[0]-utmxyA[0])**2)+((utmxyB[1]-utmxyA[1])**2))
    localscale = np.sqrt(((localxyB[0]-localxyA[0])**2)+((localxyB[1]-localxyA[1])**2))
    # rotation note - np should give result in radians
    utmtheta = np.arccos((utmxyB[0]-utmxyA[0])/utmscale)
    localtheta = np.arccos((localxyB[0]-localxyA[0])/localscale)
    theta = utmtheta-localtheta
    # translation
    tmp = np.sqrt((utmxyA[0]**2)+(utmxyA[1]**2))
    transtheta = np.arctan(utmxyA[1]/utmxyA[0])
    transtheta = transtheta-theta
    tx = localxyA[0]-tmp*np.cos(transtheta)    
    ty = localxyA[1]-tmp*np.sin(transtheta)
    tmp1 = np.cos(theta)
    tmp2 = np.sin(theta)
    localx = tx+(utmx*tmp1)+(utmy*tmp2)
    localy = ty-(utmx*tmp2)+(utmy*tmp1)
    
    return localx, localy

def save_surfer(fname, data, shape, area):
#set header variables, note all variables are to x horizontal and y vertical to fit with surfer terminology
#also z values are set to a max of 5 decimal places to save on space in ascii format
#this was chosen because this is just slightly above most field equipment's level of precision


#required inputs are a file name (fname) and the data (data) to be exported 
#also need data shape and area which should already be created from fatiando
    ncols = int(shape[1])
    nrows = int(shape[0])
    xmin = area[2]
    xmax = area[3]
    ymin = area[0]
    ymax = area[1]
    datamin = round(np.amin(data), 5)
    datamax = round(np.amax(data), 5)
    header = ('DSAA'+'\n'+' '+str(ncols)+' '+str(nrows)+'\n'+' '+str(xmin)+' '+str(xmax)
              +'\n'+' '+str(ymin)+' '+str(ymax)+'\n'+' '+str(datamin)+' '+str(datamax))
#make 2d array
    tmp = np.array(data).reshape(ncols,nrows)
    np.savetxt('%s.grd' % (fname),tmp, fmt='%.5f', delimiter=' ', header=(header), comments = '')

def cut_grid(x,y,z,area, resolution):
	# x,y,z are numpy 1d arrays, areas is bounding coords, resolution is x,y
    # area must be evenly divisible by resolution due to floating point rounding
    # eg if res is 0.2 must use n.6 not n.5
    xmin, xmax, ymin, ymax = area
    if len(x)!= len(y):
        raise ValueError('x and y must be the same length dummy')
    tmp = np.where((x>=xmin) & (x<=xmax) & (y>=ymin) & (y<=ymax))
    newx = x[tmp]
    newy = y[tmp]
    newz = z[tmp]
    xshape = round((xmax-xmin)/resolution[0]) # note was int()
    yshape = round((ymax-ymin)/resolution[1]) # note was int()
    newshape = [xshape,yshape]
    
    return newx, newy, newz, newshape

# 2d array functions

def mpf(data,lp,hp):
    # data is a 2d numpy array in the shape of your survey
    # eg what you would input to imshow
    #lp = low pass window size
    #hp = high pass window size
    #NOTE- this is currently a vertical only filter
    tmpl=ip.uniform_filter(data, size=(lp,1))
    tmph=ip.uniform_filter(tmpl, size=(1,hp))
    tmp=tmpl-tmph
    mpf=data-tmp
    return mpf