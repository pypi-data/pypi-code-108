import numpy as np

from . import transform

class rectangle:
	"""This class defines an object of type rectangle. 
	Attributes: 
		center: (0,0) by default
		radius
		fill_type"""
	
	def __init__(self, ab_tuple = (1,1), center=(0,0),pts=100,text_tag='Rectangle'):
		print(ab_tuple)
		self.xc, self.yc = center
		
		self.text_tag = text_tag
		self.a, self.b = ab_tuple
		
		pts_by_2 = int(pts/2)
		
		pts_a = int(pts_by_2*self.a/(self.a+self.b))
		pts_b = pts_by_2 - pts_a
		print(pts_b)
		
		self.perimeter = 2*(self.a+self.b)
		self.area = self.a * self.b
		
		#self.x = np.linspace(-self.a/2,self.a/2,pts_a) 
		#self.y = -self.b/2*np.ones(pts_a) + self.yc
		
		
		'''Top arm'''
		x_t = np.linspace(-self.a/2,self.a/2,pts_a) 
		y_t = self.b/2*np.ones(pts_a)
		
		'''Right arm'''
		x_r = self.a/2*np.ones(pts_b)
		y_r = np.linspace(self.b/2,-self.b/2,pts_b) 
		
		
		'''Bottom arm'''
		x_b = np.linspace(self.a/2,-self.a/2,pts_a) 
		y_b = -self.b/2*np.ones(pts_a)
		
		
		'''Left arm'''
		x_l = -self.a/2*np.ones(pts_b)
		y_l = np.linspace(-self.b/2,self.b/2,pts_b)+0.01 
		print('sdfsdf')
		
		
		self.x = np.concatenate((x_t,x_r,x_b,x_l)) + self.xc
		self.y = np.concatenate((y_t,y_r,y_b,y_l)) + self.yc
		
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
			
		
