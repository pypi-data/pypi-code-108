import numpy as np



def rotate(x,y,theta):
	'''Rotates the coordinates (x,y) in anit-clockwise direction by an angle theta.
	theta is in the units of degrees.'''
	
	theta_rad = np.radians(theta)
	x_rot  = x*np.cos(-theta_rad) + y*np.sin(-theta_rad)
	y_rot  = -x*np.sin(-theta_rad) + y*np.cos(-theta_rad)
	
	
	return x_rot, y_rot
