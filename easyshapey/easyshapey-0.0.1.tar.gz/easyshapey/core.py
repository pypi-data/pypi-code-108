#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 17 17:06:57 2017

@author: caganze
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import matplotlib.patches as patches
import random as rd
#from itertools import combinations
#from functools import reduce
import pandas as pd
#import statsmodels.nonparametric.kernel_density as kde
from matplotlib.path import Path

from abc import ABCMeta
from abc import abstractproperty
from decimal import Decimal
#import functools 
from matplotlib.patches import Ellipse
import math

import copy


class Shape(object):
	"""
    Main class 

    Extended description of function.

    Parameters
    ----------
    arg1 : int
        Description of arg1
    arg2 : str
        Description of arg2

    Returns
    -------
    int
        Description of return value

    """
	__metaclass__=ABCMeta
	def __init__(self, **kwargs):
		self.xrange=kwargs.get('xrange', []) #the range
		self.yrange=kwargs.get('yrange', [])
		self._color=kwargs.get('color', None)
		self.alpha=kwargs.get('alpha', 0.3)
		self.linewidth=kwargs.get('lw', 2)
		self.linestyle=kwargs.get('linestyle', '--')
		#self.angle=kwargs.get('angle', 0.0)
		self.edgecolor=kwargs.get('color', 'k')
		#self.xspt_range=kwargs.get('xspt_range', []) #x-range for all objects in that spt_range
		#self.yspt_range=kwargs.get('yspt_range', [])
		self.spt_name=kwargs.get('spt_range', ' ') #name of the spectral type range
		#self.vertices=kwargs.get('vertices', [])
		self.codes=[Path.MOVETO, Path.LINETO,Path.LINETO,Path.LINETO,Path.CLOSEPOLY]
		self._shapetype=None
		self._coeffs=None

	def __repr__(self):
		return 'shape'
		
	@abstractproperty
	def shapetype(self):
		return self._shapetype
		
	@shapetype.setter
	def shapetype(self, s_type):
		self._shapetype=s_type
		
	#make it ok to change the color 
	@abstractproperty
	def color(self):
		return self._color
		
	@color.setter
	def color(self, new_color):
		self._color=new_color
		
	@abstractproperty
	def spath(self):
		return Path(self.vertices, self.codes)
	
	def _select(self, data):
		"""
	    Summary line.

	    Extended description of function.

	    Parameters
	    ----------
	    arg1 : int
	        Description of arg1
	    arg2 : str
	        Description of arg2

	    Returns
	    -------
	    int
	        Description of return value

	    """
		if self.__repr__ =='oval':
			bools=self.ellipse.contains_points(list(map(tuple, data.T)), transform=None, radius=0.0) 
		if not self.__repr__=='oval':
			bools=self.spath.contains_points(list(map(tuple, data.T)), transform=None, radius=0.0)
			
		selected_data=np.array([data[0][bools], data[1][bools]])

		return selected_data, bools

	def select(self, data):
		"""
	    Summary line.

	    Extended description of function.

	    Parameters
	    ----------
	    arg1 : int
	        Description of arg1
	    arg2 : str
	        Description of arg2

	    Returns
	    -------
	    int
	        Description of return value

	    """
		sels=None
		if len(data)==0:
			raise ValueError('Please pass some data lol')
			
		if isinstance(data, pd.DataFrame):
			data.columns=['x', 'y']
			bools=self._select(np.array([data['x'].values, data['y'].values]))[1]
			sels=data[bools]

		#print (data)
		if (len(data) !=0) and (not isinstance(data, pd.DataFrame)):
			sels=self._select(data)[0]

			
		return sels
		


		
class BadVerticesFormatError(Exception):
	pass

class Box(Shape):
	"""
    Summary line.

    Extended description of function.

    Parameters
    ----------
    arg1 : int
        Description of arg1
    arg2 : str
        Description of arg2

    Returns
    -------
    int
        Description of return value

    """
	def __init__(self, **kwargs):
		super().__init__()
		self.shapetype=kwargs.get('shapetype', 'box')
		self.completeness=kwargs.get('completeness',0.85)
		self.contamination=np.nan
		self._data=None # a pandas object with two or more columns (should have x and y	 for directions)
		self._data_type=None #this is to inform whether the data are contaminants (do not change the box)
		self._scatter=None
		self._pol=None
		self._vertices=None
		self._angle=None
		self._coeffs=None
		self.scatter_coeff=kwargs.get('scoeff', 1.5)
		self.xshift=kwargs.get('xshift', 0.1)
	def __repr__(self):
		return 'box'

	def __len__(self):
		if self._data is None:
			return 0
		else:
			return len(self.data[0])

	
	@property 
	def center(self):
		"""
	    Summary line.

	    Extended description of function.

	    Parameters
	    ----------
	    arg1 : int
	        Description of arg1
	    arg2 : str
	        Description of arg2

	    Returns
	    -------
	    int
	        Description of return value

	    """
		vs=np.array(self.vertices)
		return (np.nanmean(vs[:,0]), np.nanmean(vs[:,1]))

	@property
	def angle(self):

		x1, y1=self.vertices[0]
		x2, y2= self.vertices[1]
		dist = math.hypot(x2 - x1, y2 - y1)
		dx=abs(x2-x1)
		if y2 > y1:
			ang=np.arccos(dx/dist)
		else:
			ang=np.arccos(dx/dist)
		return ang

	@property
	def vertices(self):
		"""
		The vertices of a box are defined by the center and half the xranges and y ranges
		They must follow a clockwise, direction (and back ) i.e (v1, v2, v3, v4, v1) with v1 
		having the smallest x value
		"""
		return self._vertices
		
	@vertices.setter
	def vertices(self, vertices):
		"""
		create vertices properties of a box
		"""
		flag1=np.isclose(np.array(vertices[0]), np.array(vertices[-1]), equal_nan=True, rtol=0.0001).all()
		#flag2= vertices[:,0].T == vertices
		
		if not flag1 :
			#should check that vertices define	a square, 
			#there is a precision example for this 
			raise BadVerticesFormatError('''Invalid vertices for a Box, vertices first element {}  must be equal to the last element {} must be equal within 10^-4'''.format(vertices[0], vertices[-1]))
		
		vs_x= np.array(vertices)[:, 0]
		vs_y=np.array(vertices)[:,1]
		argxmin=np.argmin(np.array(vertices)[:, 0])
		argxmax=np.argmax(np.array(vertices)[:, 0])
		self.xrange= [vs_x[np.argmin(vs_x)], vs_x[np.argmax(vs_x)]]
		self.yrange=[vs_y[np.argmin(vs_y)], vs_y[np.argmax(vs_y)]]
		self._vertices=vertices
		
		#v1=(self.center[0]-0.5*np.ptp(self.xrange), self.center[1]+0.5*np.ptp(self.yrange))
		#v2=(self.center[0]+0.5*np.ptp(self.xrange), self.center[1]+0.5*np.ptp(self.yrange))
		#v3=(self.center[0]+0.5*np.ptp(self.xrange), self.center[1]-0.5*np.ptp(self.yrange))
		#v4=(self.center[0]-0.5*np.ptp(self.xrange), self.center[1]-0.5*np.ptp(self.yrange))
		
	
	@property
	def area(self):
		"""
		Area is dx*dy
		"""
		return abs( np.ptp(self.xrange)*np.ptp(self.yrange))

	@property
	def data(self):
		return np.array(self._data)

	@data.setter
	def data(self, input):
		"""
		input must be a 2d-numpy array
		x is assumed to be data[0]
		y is assumed tp be data[1]
		xerr is data[2] etc.
		similar assumptions are made about yerr 
		"""
		if not self._data_type=='contam':
			#fit a line to the data
			if isinstance(input, pd.DataFrame):
				x=input.ix[:,0].astype(float).values
				y=input.ix[:,1].astype(float).values
				#if no error arrays are given, assume gaussian
				if input.shape[1] ==2:
					xerr=np.zeros(len(x)) #i don't use this anyway
					mu=np.nanmean(y)
					sigma=np.nanstd(y)
					yerr= np.random.normal(mu, sigma, len(y))
				#otherwise, retrieve the values
				else:
					xerr=input.ix[:,2].astype(float).values
					yerr=input.ix[:,3].astype(float).values

			else: 
				x=input[0]
				y=input[1]
				#if no error arrays are given, assume zero
				if input.shape[0] ==2:
					xerr=np.zeros(len(x)) #i don't use this much
					mu=np.nanmean(y)
					sigma=np.nanstd(y)
					yerr= np.random.normal(mu, sigma, len(y))
				#otherwise, retrieve the values
				else:
					xerr=input[2]
					yerr=input[3]

			x_max=np.nanmedian(x)+3.*np.nanstd(x)
			x_min=np.nanmedian(x)-3.*np.nanstd(x)

			y_max=np.nanmedian(y)+3.*np.nanstd(y)
			y_min=np.nanmedian(y)-3.*np.nanstd(y)

			dx=x_max-x_min
			dy=y_max-y_min

			if x_max> np.nanmax(x):
				x_max= np.nanmax(x)

			if x_min < np.nanmin(x):
				x_min=np.nanmin(x)

			if y_max> np.nanmax(y):
				y_max= np.nanmax(y)

			if y_min < np.nanmin(y):
				y_min=np.nanmin(y)

			#add fudge factor to xlimits
			x_max=x_max+self.xshift*dx 
			x_min=x_min-self.xshift*dx

			mask1=np.logical_and(x>x_min, x<x_max)
			mask2=np.logical_and(y>y_min, y<y_max)
			
			#use matrix algebra to determine the best fit line given uncertainties
			#Y = y.reshape(-1,1)
			#A = np.vstack((np.ones_like(x), x)).T
			#C = np.diag(yerr**2)

			#X = np.linalg.inv(A.transpose()@np.linalg.inv(C)@A) @ (A.transpose()@np.linalg.inv(C)@Y)
			#if the user asks for a reactangle then give them a reactangle
			if self.shapetype=='box':

				pol = np.poly1d(np.polyfit(x[mask2], y[mask2], 1))

			if self.shapetype =='rectangle':
				pol=np.poly1d(np.polyfit(x[mask2], np.ones_like(y[mask2])*np.nanmedian(y[mask2]), 1))
			
			coeffs = pol.coefficients
			ys=pol([x_min, x_max])


			scatter= self.scatter_coeff* np.nansum(np.sqrt((y[mask2]- pol(x[mask2]))**2)/len(x[mask2]))
			
			#print ('x_max {}  x_min {} scatter {}'.format(x_max, x_min, scatter))
			ys_above= ys+0.4*dy
			ys_below=ys-0.4*dy
			
			#print ('ys above {} ys below {}'.format(ys_above, ys_below))
			v1= (x_min, ys_above[0])
			v2=(x_max, ys_above[1])
			v4= (x_min,	 ys_below[0])
			v3=(x_max,	ys_below[1])
			
			self.vertices=[v1, v2, v3, v4, v1]
			self._data=np.array([x, y])
			self._scatter=scatter
			self._pol=pol
			self._coeffs=coeffs
		else:
			self._data=input
			
	@property
	def datatype(self):
		return self._data_type
	
	@datatype.setter
	def datatype(self, new_type):
		"""
		chnaging the lable for the type of data passed onto the box
		"""
		self._data_type=new_type
			
	@property
	def efficiency(self):
		"""
		This is really a completeness or a contamination, based on the data that's passed in
		"""
		eff=float(len(self.select(self.data)[0])) /float(len(self.data[0]))
		return eff
	@property
	def scatter(self):
		"""
		the scatter between the data and the center line
		"""
		return self._scatter
	
	@property
	def coeffs(self):
		"""
		coefficients of the line (slope and y-intercept
		"""
		return self._coeffs
		
	def contains(self, points):
		"""
		If point belongs to this path, it returns true otherwise it returns false
		points must be a list of tuples
		INPUT: list of tuples
		"""
		#_points=
		return [self.spath.contains_point(x, transform=None, radius=0.0) for x in points]
		
	def rotate(self,  ang, **kwargs):
	
		"""
		rotate a box by an angle
		angles are always measured in radians
		
		the center of rotation is defined by the mean of the vertices
		the axis of rotation is the line passing through the center,
		 parallel to the edges of the box
		"""
	
		vs=np.array(self.vertices)
	
		r=[[np.cos(ang), -np.sin(ang)],
			 [np.sin(ang), np.cos(ang)]]
	
		c=kwargs.get('center', self.center)
	
	
		i=np.identity(2)
	
		mat=np.matrix([[r[0][0], r[0][1], np.dot(i-r, c)[0]],
				[r[1][0], r[1][1], np.dot(i-r, c)[1]],
				[0., 0., 1.]])
	
		xs=vs[:, 0]
		ys=vs[:, 1]
		zs=np.array([1. for x in xs])
	
		rotated=np.array(np.dot(mat, np.array([xs, ys, zs])))
	
		#reformat
		new_vs=rotated.reshape((3, len(self.vertices)))[:2]

		#print (np.array(new_vs.T)[0])
		if kwargs.get('set_vertices', True):
			self.vertices=np.array(new_vs.T)
			return 
		else:
			return new_vs.T

	def plot(self, **kwargs):
		"""
		display a box, must pass matploltib axes as argument 
		"""
		xlim=kwargs.get('plot_xlim', [])
		ylim=kwargs.get('plot_ylim', [])
		ax1= kwargs.get('ax', plt.gca())
		size=kwargs.get('size', 0.1)
		if not kwargs.get('only_shape', True):
			 ax1.plot(self.data[0], self.data[1], 'k.', ms=size)
		
		alpha=self.alpha
		if kwargs.get('highlight', False):
			self.linewidth=3.5
			self.linestyle='-'
			self.edgecolor='#111111'
			alpha=self.alpha*3.0
			#self.color='none'
		
		#self.color=None
		#print ('selfcolor', self.color)
		patch =patches.PathPatch(self.spath, 
						facecolor=self.color, 
							alpha=alpha, 
							edgecolor=self.edgecolor, 
							linewidth=self.linewidth,
							linestyle=self.linestyle)
							
		ax1.add_patch(patch)
		label=kwargs.get('label', None)
		if label is not None: 
			ax1.text(self.center[0], self.center[1]+self._scatter, label, fontsize=15, rotation=360-self.angle*57.2958, color='#111111')
		if kwargs.get('set_limits', False):
			 ax1.set_xlim(xlim)
			 ax1.set_ylim(ylim)

			 

class RotatedBox(Box):

	def __init__(self, **kwargs):
		super().__init__()
	
		
	@Box.data.setter
	def data(self, df):
		if not self._data_type=='contam':
			#define vertices as min and max of the data
			x=np.array(df.x)
			y=np.array(df.y)
			
			x_max=np.nanmax(x)
			x_min=np.nanmin(x)
			
			y_max=np.nanmax(y)
			y_min=np.nanmin(y)
			
			v1= (x_min, y_max)
			v2=(x_max, y_max)
			v4= (x_min,	 y_min)
			v3=(x_max,	y_min)
			
			vs=[v1, v2, v3, v4, v1]
			self._data=df
			
			self.vertices=vs
			areas=[]
			all_vertices=[]
			
			for alpha in np.linspace(0., 0.5*np.pi, 1000):
				vs=self.rotate(alpha, set_vertices=False)
				all_vertices.append(vs)
				areas.append(np.ptp(vs[:,0])*np.ptp(vs[:, 1]))
	
			best= np.argmin(areas)
			self.vertices=np.array(all_vertices)[best]
			
		else:
			self._data=df
			
		return 
	
class Oval(Shape):
	""" 
	Oval with vertices define as extremes of the major and minor axes
	"""
	def __init__(self, **kwargs):

		super().__init__()
		self.shapetype='oval'
		self.completeness=kwargs.get('completeness',0.85)
		self.contamination=np.nan
		self._data=None # a pandas object with two or more columns (should have x and y	 for directions)
		self._data_type=None #this is to inform whether the data are contaminants (do not change the box)
		self._scatter=None
		self._pol=None
		self._vertices=None
		self._center=None
		self._height=None
		self._width=None
		#self.codes=None
		self._box=None 
		self._ellipse=None
	
	def __repr__(self):
		return 'oval'

	def __len__(self):
		if self._data is None:
			return 0
		else:
			return len(self.data)

	@property
	def angle(self):
		return self._angle

	@angle.setter
	def angle(self, new_angle):
		self.rotate(new_angle)

	@property
	def center(self):
		return self._center

	@property
	def height(self):
		return self._height

	@property 
	def width(self):
		return self._width

	@property
	def vertices(self):
		return self._vertices


	@property
	def box(self):
		"""
		an ellispe has an underlying box
		"""
		return self._box

	@property
	def ellipse(self):
		if self._ellipse is not None:
			self._ellipse.set_alpha(self.alpha)
			self._ellipse.set_facecolor(self.color)
		return self._ellipse

	@ellipse.setter
	def ellipse(self, new_ellipse):
		self._ellipse=new_ellipse
		self._center=new_ellipse.center
		self._angle=new_ellipse.angle
		self._box=b
		self._width=new_ellipse.width
		self._height=new_ellipse.height
	
	@property
	def data(self, df):
		return self._data

	@data.setter
	def data(self, df):
		#determines ellipse by fitting to a box
		b=Box()
		b.data=df
		vs=np.array(b.vertices)
		self._vertices=vs
		self._center=[np.mean(vs[:, 0]), np.mean(vs[:, 1])]
		self._angle=b.angle
		self._box=b
		#the distance formula
		self._height=np.sqrt((vs[1][0]-vs[2][0])**2+(vs[1][1]-vs[2][1])**2)
		self._width=np.sqrt((vs[1][0]-vs[2][0])**2+(vs[1][1]-vs[2][1])**2)
		self._ellipse=Ellipse(self._center, self._width, self._height, self._angle)
		self._data=df

	def rotate(self, angle):
		self.ellipse= self._ellipse.set_alpha(angle)

	def plot(self, **kwargs):

		ax=kwargs.get('ax', plt.gca())

		xlim=kwargs.get('plot_xlim', [])
		ylim=kwargs.get('plot_ylim', [])

		
		ax.add_patch(self.ellipse)

		
		if kwargs.get('set_limits', False):
			 ax.set_xlim(xlim)
			 ax.set_ylim(ylim)
		



	
	
	

