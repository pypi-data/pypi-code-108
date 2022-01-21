import numpy as np
from . import transform

class circle:
	"""This class defines an object of type circle. 
	Attributes: 
		center: (0,0) by default.
		radius: 1 by default.
		"""
	
	def __init__(self, radius=1, center=(0,0),pts=100,text_tag='Circle'):
		self.text_tag = text_tag
		self.r = radius
		self.xc , self.yc = center
		self.perimeter = 2*np.pi*self.r
		self.area = np.pi*self.r**2
		self.theta = np.linspace(0,2*np.pi,pts)
		self.x = self.r*np.cos(self.theta) + self.xc
		self.y = self.r*np.sin(self.theta) + self.yc
		
		return
		
		
	def plot(self,ax_f,linewidth=2,text_tag=None):
		if text_tag is None:
			ax_f.plot(self.x,self.y,linewidth=2,label=self.text_tag)
		else:
			ax_f.plot(self.x,self.y,linewidth=2,label=text_tag)
			


class ellipse:
	"""This class defines an object of type ellipse.
	Attributes: 
		center: (0,0) by default.
		(major_axis,minor_axis): (1,2) by default. 
		"""
	
	def __init__(self, maj_mi_tuple = (1,2), center=(0,0),pts=100,text_tag='Ellipse'):
		
		self.text_tag = text_tag
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
		
		
	def rotate(self,theta):
		x_rot, y_rot = transform.rotate(self.x-self.xc,self.y-self.yc,theta)
		self.x = x_rot + self.xc
		self.y = y_rot + self.yc
		
	def rotate_about_center(self,theta):
		x_rot, y_rot = transform.rotate(self.x,self.y,theta)
		self.xc, self.yc = transform.rotate(self.xc,self.yc,theta)
		self.x = x_rot
		self.y = y_rot
		
	def plot(self,ax_f,linewidth=2,text_tag=None):
		if text_tag is None:
			ax_f.plot(self.x,self.y,linewidth=2,label=self.text_tag)
		else:
			ax_f.plot(self.x,self.y,linewidth=2,label=text_tag)
			

		
		



