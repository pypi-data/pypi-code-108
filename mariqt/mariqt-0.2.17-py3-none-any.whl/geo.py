from datetime import datetime
import math
import mariqt.core as miqtc
from abc import ABC, abstractmethod
import cmath
import numpy as np
import pymap3d
import copy

class NumDataTimeStamped(ABC):
	""" Abstract class for data in form of a dict with UNIX timestamps in milliseconds as key """
	@abstractmethod
	def interpolateAtTime(self,utc:int,sorted_time_points:list = [] ,startIndex:int = 0):
		pass

	@abstractmethod
	def len(self):
		pass

class Position:
	""" A class defining a 4.5D position, encoded by a utc time (unix in milliseconds), latitude, longitude, depth, height and coordinate uncertainty. Depth, height and coordinate uncertainty are optional."""
	def __init__(self,utc:int,lat:float,lon:float,dep:float=0,hgt:float=-1,uncert:float=-1):
		self.lat = lat
		self.lon = lon
		self.utc = utc
		self.dep = dep
		self.hgt = hgt
		self.uncert = uncert

	def dateTime(self):
		return datetime.utcfromtimestamp(self.utc / 1000)

	def __str__(self) -> str:
		return "utc: " + str(self.utc) + ", lat: " + str(self.lat) + ", lon: " + str(self.lon) + ", dep: " + str(self.dep) + ", hgt: " + str(self.hgt) + ", uncert: " + str(self.uncert)


class Positions(NumDataTimeStamped):
	""" A class that holds several 4.5D Positions in the form of a dictionary with UNIX timestamps in milliseconds as keys and containing (x,y,z,d,h) tuples. Decorator pattern of a dictionary"""

	def __init__(self,positions={}):
		self.positions = positions
	def setPos(self,p:Position):
		self.positions[p.utc] = p
	def setVals(self,utc:int,lat:float,lon:float,dep:float=0,hgt:float=-1,uncert:float=-1):
		self.positions[utc] = Position(utc,lat,lon,dep,hgt,uncert)
	def remUTC(self,utc:int):
		del self.positions[utc]
	def remPos(self,p:Position):
		del self.positions[p.utc]
	def len(self):
		return len(self.positions)
	def __getitem__(self,utc:int):
		return self.positions[utc]
	def __setitem__(self,utc:int,p:Position):
		self.positions[utc] = p
	def keys(self):
		return self.positions.keys()

	def __str__(self):
		return str("\n".join([str(self.positions[e]) for e in self.positions]))

	def interpolateAtTime(self,utc:int,sorted_time_points:list = [] ,startIndex:int = 0):
		""" returns pos_interpolated, lastIndex """

		if utc in self.positions:
			return self.positions[utc], startIndex

		if sorted_time_points == []:
			sorted_time_points = list(self.positions.keys())
			sorted_time_points.sort()

		prev_nearest_index, past_nearest_index = findNearestNeighbors(sorted_time_points,utc,startIndex)
		pre_utc = sorted_time_points[prev_nearest_index]
		post_utc = sorted_time_points[past_nearest_index]

		alpha = 1.0 * (utc - pre_utc) / (post_utc - pre_utc)
		new_lat = self.positions[pre_utc].lat * (1-alpha) + self.positions[post_utc].lat * alpha
		new_lon = self.positions[pre_utc].lon * (1-alpha) + self.positions[post_utc].lon * alpha
		new_dep = self.positions[pre_utc].dep * (1-alpha) + self.positions[post_utc].dep * alpha
		new_hgt = self.positions[pre_utc].hgt * (1-alpha) + self.positions[post_utc].hgt * alpha
		new_uncert = self.positions[pre_utc].uncert * (1-alpha) + self.positions[post_utc].uncert * alpha # TODO uncert? siehe navigation.splineToOneSecondInterval()

		return Position(utc,new_lat,new_lon,new_dep,new_hgt,new_uncert), past_nearest_index

class Attitude:
	""" A class defining an attitude, encoded by a utc time (unix in milliseconds) and yaw, pitch, roll in degrees which are by default 0."""
	def __init__(self,utc:int,yaw:float=0,pitch:float=0,roll:float=0):
		self.utc = utc
		self.yaw = float(yaw)
		self.pitch = float(pitch)
		self.roll = float(roll)

	def dateTime(self):
		return datetime.utcfromtimestamp(self.utc / 1000)

	def __eq__(self, __o: object) -> bool:
		if self.utc == __o.utc and self.yaw == __o.yaw and self.pitch == __o.pitch and self.roll == __o.roll:
			return True
		return False

	def __str__(self) -> str:
		return "utc: " + str(self.utc) + ", yaw: " + str(self.yaw) + ", pitch: " + str(self.pitch) + ", roll: " + str(self.roll)

class Attitudes(NumDataTimeStamped):
	""" A class that holds several Attitudes in the form of a dictionary with UNIX timestamps in milliseconds as keys and containing (yaw,pitch,roll) tuples. Decorator pattern of a dictionary"""

	def __init__(self,attitudes={}):
		self.attitudes = attitudes
	def setAtt(self,a:Attitude):
		self.attitudes[a.utc] = a
	def setVals(self,utc:int,yaw:float=0,pitch:float=0,roll:float=0):
		self.attitudes[utc] = Attitude(utc,yaw,pitch,roll)
	def remUTC(self,utc:int):
		del self.attitudes[utc]
	def remAtt(self,a:Attitude):
		del self.attitudes[a.utc]
	def len(self):
		return len(self.attitudes)
	def __getitem__(self,utc:int):
		return self.attitudes[utc]
	def __setitem__(self,utc:int,a:Attitude):
		self.attitudes[utc] = a
	def keys(self):
		return self.attitudes.keys()

	def __str__(self):
		return str("\n".join([str(self.attitudes[e]) for e in self.attitudes]))

	def interpolateAtTime(self,utc:int,sorted_time_points:list = [] ,startIndex:int = 0):
		""" returns att_interpolated, lastIndex """

		if utc in self.attitudes:
			return self.attitudes[utc], startIndex

		if sorted_time_points == []:
			sorted_time_points = list(self.attitudes.keys())
			sorted_time_points.sort()

		prev_nearest_index, past_nearest_index = findNearestNeighbors(sorted_time_points,utc,startIndex)
		pre_utc = sorted_time_points[prev_nearest_index]
		post_utc = sorted_time_points[past_nearest_index]

		new_yaw = interpolateAngles(pre_utc,self.attitudes[pre_utc].yaw,utc,post_utc,self.attitudes[post_utc].yaw,anglesInDegrees=True)
		new_pitch = interpolateAngles(pre_utc,self.attitudes[pre_utc].pitch,utc,post_utc,self.attitudes[post_utc].pitch,anglesInDegrees=True)
		new_roll = interpolateAngles(pre_utc,self.attitudes[pre_utc].roll,utc,post_utc,self.attitudes[post_utc].roll,anglesInDegrees=True)

		return Attitude(utc,new_yaw,new_pitch,new_roll), past_nearest_index 

class AngularInterpolater():
	""" Allows for interpolation of angular values via .interpolateAt(). source_t must be list of floats. 
		Angular quantities can not be simply interpolated (e.g. middle of 175 and -175 would be zero but should be 180).
		This class handles such cases properly """

	def __init__(self,source_t:list,source_x:list,source_t_is_sorted=False,anglesInDegrees=True):
		""" Allows for interpolation of angular values via .interpolateAt(). source_t must be list of floats. 
		 	Angular quantities can not be simply interpolated (e.g. middle of 175 and -175 would be zero but should be 180).
			This class handles such cases properly """
		if len(source_t) != len(source_x):
			raise Exception("AngularInterpolater: time and data vector must be of same length!")

		self.source_dict = dict(zip(source_t, source_x))
		self.anglesInDegrees = anglesInDegrees

		if not source_t_is_sorted:
			self.source_t_sorted = copy.deepcopy(source_t)
			self.source_t_sorted.sort()
		else:
			self.source_t_sorted = source_t

		self.startIndex = 0

	def interpolateAt(self,target_t:float):

		if target_t in self.source_dict:
			return self.source_dict[target_t]

		prev_nearest_index, past_nearest_index = findNearestNeighbors(self.source_t_sorted ,target_t,self.startIndex)
		
		pre_target_t = self.source_t_sorted[prev_nearest_index]
		post_target_t = self.source_t_sorted[past_nearest_index]

		# set start for next interpolation
		self.startIndex = past_nearest_index

		return interpolateAngles(pre_target_t,self.source_dict[pre_target_t],target_t,post_target_t,self.source_dict[post_target_t],anglesInDegrees=self.anglesInDegrees)


def interpolateAngles(t_pre:float,x_pre:float,t_target:float,t_post:float,x_post:float,anglesInDegrees=True):
	""" interplates angle a t_target between to angles x_pre and x_post, with respective times t_pre and t_post"""
	if anglesInDegrees:
		x_pre = math.radians(x_pre)
		x_post = math.radians(x_post)

	alpha = 1.0 * (t_target - t_pre) / (t_post - t_pre)
	# angular quantities can not be simply interpolated (e.g. middle of 175 and -175 would be zero but should be 180), therefore angular values α are applied as arguments of unit complex numbers
	# e^jα . The resulting complex numbers can then, if necessary, be weighted by ω, added together and the phase of the result provides a valid mean/interpolation
	target_x = cmath.phase( cmath.exp(complex(0,x_pre)) * (1-alpha) + cmath.exp(complex(0,x_post))  * alpha )
	if anglesInDegrees:
		target_x = math.degrees(target_x)
	return target_x

	
# TODO move to core?
def findNearestNeighbors(values_sorted:list,value, startIndex):
	""" returns prev_nearest_index, past_nearest_index of value in values starting the search at startIndex. Throws exception if value out of range"""

	if value < values_sorted[0] or value > values_sorted[-1]:
		raise Exception("value " + str(value) + " out of range")

	if values_sorted[startIndex] < value:
		increment = 1
		limit = len(values_sorted)
		def passed(value1,value2):
			return value1 >= value2
	else:
		increment = -1
		limit = -1
		def passed(value1,value2):
			return value1 <= value2

	for i in range(startIndex,limit,increment):
		if passed(values_sorted[i],value):
			if increment == 1:
				return i-1, i
			else:
				return i, i+1
	raise Exception("something went wrong")


def distanceLatLon(lat_1,lon_1,lat_2,lon_2):
	""" Computes a distance in meters from two given decimal lat/lon values."""

	lat_1_r = math.radians(lat_1)
	lon_1_r = math.radians(lon_1)
	lat_2_r = math.radians(lat_2)
	lon_2_r = math.radians(lon_2)

	lat_offset = lat_1_r - lat_2_r
	lon_offset = lon_1_r - lon_2_r

	alpha = 2 * math.asin(math.sqrt(math.pow(math.sin(lat_offset / 2), 2) + math.cos(lat_1_r) * math.cos(lat_2_r) * math.pow(math.sin(lon_offset / 2), 2)))
	return alpha * 6371000 # Earth's radius


def distancePositions(p1:Position,p2:Position):
	""" Computes a distance in meters from two given positions"""
	return distanceLatLon(p1.lat,p1.lon,p2.lat,p2.lon)


def getDecDegCoordinate(val):
	""" Asserts that the given value is a decimal degree float value"""
	if isinstance(val, float):
		return val
	else:
		return decmin2decdeg(val)


def decdeg2decmin(val,xy = ""):
	""" Turns a float representation of a coordinate (lat/lon) into a string representation using decimal minutes"""
	if val < 0:
		dec = math.ceil(val)
		if xy == "lat":
			xy = "S"
			dec *= -1
			val *= -1
		elif xy == "lon":
			xy = "W"
			dec *= -1
			val *= -1
	else:
		dec = math.floor(val)
		if xy == "lat":
			xy = "N"
		elif xy == "lon":
			xy = "E"
	min = str(round(60*(val - dec),3))
	add = ""
	for i in range(len(min[min.find(".")+1:]),3):
		add += "0"
	return str(dec)+"°"+min+add+xy


def decmin2decdeg(str):
	""" Converts a decimal degree string ("117° 02.716' W") to a decimal degree float"""
	str = str.strip()
	try:
		return float(str)
	except:
		p1 = str.find(chr(176))# This is an ISO 8859-1 degree symbol: °
		p2 = str.find(chr(39))# This is a single tick: '
		deg = int(str[0:p1].strip())
		min = float(str[p1+1:p2].strip())
		reg = str[p2+1:].strip()

		if reg.lower() == "s" or reg.lower() == "w":
			deg *= -1
			return deg - min/60
		else:
			return deg + min/60

def Rx(angle:float):
    """ Rotation matrix around x, take angle in degrees """
    c = np.cos(np.deg2rad(angle))
    s = np.sin(np.deg2rad(angle))
    return np.array([   [1, 0, 0],
                        [0, c,-s],
                        [0, s, c]])

def Ry(angle:float):
    """ Rotation matrix around y, take angle in degrees """
    c = np.cos(np.deg2rad(angle))
    s = np.sin(np.deg2rad(angle))
    return np.array([   [c, 0, s],
                        [0, 1, 0],
                        [-s,0, c]])

def Rz(angle:float):
    """ Rotation matrix around z, take angle in degrees """
    c = np.cos(np.deg2rad(angle))
    s = np.sin(np.deg2rad(angle))
    return np.array([   [c,-s, 0],
                        [s, c, 0],
                        [0, 0, 1]])

def R_YawPitchRoll(yaw,pitch,roll):
    """ return yaw pitch roll rotation matrix """
    return np.dot(Rz(yaw),Ry(pitch)).dot(Rx(roll))

def R_XYZ(angle_x,angle_y,angle_z):
    """ return rotation matrix for consecutive rotations around fixed axis x,y,z"""
    return np.dot(Rz(angle_z),Ry(angle_y)).dot(Rx(angle_x))

def yawPitchRoll(R:np.array):
    """ retruns [yaw,pitch,roll] in degrees from yaw,pitch,roll rotation matrix """
    yaw = np.degrees(np.arctan2(R[1,0],R[0,0]))
    pitch = np.degrees(np.arctan2(-R[2,0],np.sqrt(R[2,1]**2 + R[2,2]**2)))
    roll = np.degrees(np.arctan2(R[2,1],R[2,2]))
    return [yaw,pitch,roll]

def addLeverarms2Latlon(orig_lat,orig_lon,orig_depth,offset_x,offset_y,offest_z,yaw,pitch,roll):
	""" adds and offest in vehicle coordinates to an original lat,lon,depth(downward positive) position (wgs84) and returns new lat,lon,depth position. 
		Angles in degrees, offsets in meters """

	# get offest in NED
	offest_xyz = np.array([offset_x,offset_y,offest_z])
	offset_NED = R_YawPitchRoll(yaw,pitch,roll).dot(offest_xyz)

	ell = pymap3d.Ellipsoid("wgs84")
	lat_lon_h_new =  pymap3d.ned2geodetic(offset_NED[0], offset_NED[1], offset_NED[2],orig_lat,orig_lon,-orig_depth,ell=ell)
	lat_new = lat_lon_h_new[0]
	lon_new = lat_lon_h_new[1]
	depth_new = -lat_lon_h_new[2]

	return lat_new,lon_new,depth_new
