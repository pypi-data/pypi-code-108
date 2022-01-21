import numpy as np
from . import transform

class circle:
	"""This class defines an object of type circle. 
	Attributes: 
		center: (0,0) by default
		radius
		fill_type"""
	
	def __init__(self, radius, center=(0,0),pts=100):
		self.r = radius
		self.xc , self.yc = center
		
		self.perimeter = 2*np.pi*self.r
		self.area = np.pi*self.r**2
		self.theta = np.linspace(0,2*np.pi,pts)
		self.x = self.r*np.cos(self.theta) + self.xc
		self.y = self.r*np.sin(self.theta) + self.yc
		return
		
		

class ellipse:
	"""This class defines an object of type ellipse"""
	
	def __init__(self, maj_mi_tuple = (1,2), center=(0,0),pts=100):
		
		self.major_axis, self.minor_axis = maj_mi_tuple
		self.xc , self.yc = center
		self.perimeter = np.pi*(self.major_axis + self.minor_axis)
		
		#self.area = np.pi*self.major_axis*self.minor_axis
		self.theta = np.linspace(0,2*np.pi,pts)
		self.x = self.major_axis*np.cos(self.theta) + self.xc
		self.y = self.minor_axis*np.sin(self.theta) + self.yc
		
	def rotate(self,theta):
		#print('rotate by theta', theta)
		x_rot, y_rot = transform.rotate(self.x-self.xc,self.y-self.yc,theta)
		
		self.x = x_rot + self.xc
		self.y = y_rot + self.yc

		
		



