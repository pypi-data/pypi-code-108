""" This class implements the MareHub AGVI directory structure convention. this convention specifies that data should be structured like so: /base/project/[Gear/]event/sensor/data_type/ E.g.: /mnt/nfs/cruises/SO268/SO268-1_021-1_OFOS-02/SONNE_CAM-01_OFOS-Still/raw/"""
import os
from enum import Enum

import mariqt.core as miqtc

def findBaseForDir(base_paths:list,dir:str,create:bool = False,gear:str = ""):
	""" Checks whether the required dir exists in any of the base_paths"""

	if gear != "":
		with_gear = True
		gear += "/"
	else:
		with_gear = False

	path = False
	for base in base_paths:
		path = Dir(base,gear+dir,with_gear=with_gear)
		if path.exists():
			break
	if path == False and create == True:
		# Find the one base folder that is closest to the searched dir
		closest = -1
		closest_path = False
		for base in base_paths:
			path = Dir(base,gear+dir,with_gear=with_gear)
			for e in dp:
				if os.path.exists(path.to(e)):
					if e > closest:
						closest = e
						closest_path = path
		path = closest_path
	return path


def findSensorInEvents(base_paths:dict,sensor:str,gear:str = ""):
	""" Returns the absolute paths to all sensor directories that contain search in their name"""

	ret = []

	for bp in base_paths:
		if not os.path.exists(bp):
			continue
		if gear == "":
			events = os.listdir(bp)
			for event in events:
				if event[0] == ".":
					continue
				sensors = os.listdir(bp+"/"+event)
				for sens in sensors:
					if sens[0] == ".":
						continue
					if sensor in sens:
						ret.append(event)
						break
		else:
			gears = os.listdir(bp)
			for gear in gears:
				events = os.listdir(bp+"/"+gear)
				for event in events:
					if event[0] == ".":
						continue
					sensors = os.listdir(bp+"/"+gear+"/"+event)
					for sens in sensors:
						if sens[0] == ".":
							continue
						if sensor in sens:
							ret.append(event)
							break

	return ret


class Dir:

	class dt(Enum):
		""" The terminal data folders allowed at the end of directory path"""
		external = 0
		raw = 1
		intermediate = 2
		processed = 3
		products = 4
		protocol = 5
	class dp(Enum):
		""" The five folders that make up the valid directory paths according to the convention (GEAR is optional)"""
		PROJECT = 0
		GEAR = 1
		EVENT = 2
		SENSOR = 3
		TYPE = 4


	def __init__(self,base_dir:str,dir:str,create:bool = False,with_gear:bool = False):
		""" Requires a base_dir and the subsequent part dir of the directory path. If base_dir = "" dir is split in base_dir and dir automatically assuming dir points to TYPE folder. Will create a missing directory path if asked to do so.
		(e.g. base_dir = "/mnt/nfs/cruises/", dir = "SO268/SO268-1_021-1_OFOS-02/SONNE_CAM-01_OFOS-Still/raw"). 
		"""

		# if base_dir empty it is reconstructed assuming that dir points to TYPE folder
		if base_dir == "":
			lengthDir = len(self.dp)
			if not with_gear:
				lengthDir -= 1
			dir = miqtc.assertSlash(dir.replace("//","/"))
			tmp = dir.split("/")[0:-1] # last one is empty as dir ends with "/"
			base_dir = "/".join(tmp[:-1*lengthDir]) + "/"
			dir = "/".join(tmp[-1*lengthDir:]) + "/"
			

		if not isinstance(dir, str):
			raise Exception("No directroy provided")

		if not isinstance(base_dir, str):
			raise Exception("No base directroy provided")

		base_dir = miqtc.assertSlash(base_dir.replace("//","/"))
		if(base_dir[-1] != "/"):
			base_dir += "/"
		dir = miqtc.assertSlash(dir.replace("//","/"))
		if dir[0] == "/":
			dir = dir[1:]

		self.base_dir = base_dir
		self.with_gear = with_gear
		self.dirs = {self.dp.PROJECT:"",self.dp.GEAR:"",self.dp.EVENT:"",self.dp.SENSOR:"",self.dp.TYPE:""}
		self.keys = {self.dp.PROJECT:False,self.dp.GEAR:False,self.dp.EVENT:False,self.dp.SENSOR:False,self.dp.TYPE:False}

		base_len = len(base_dir.split("/"))
		tmp = dir.split("/")
		idx = 0
		for d in self.dirs:

			# Do not try to add more parts of the directory path than available
			if idx >= len(tmp) or tmp[idx] == "":
				break

			# Skip gear folder if not used
			if d == self.dp.GEAR and not self.with_gear:
				continue

			# For the final (type) part of the directory path, check whether the given value is valid
			if d == self.dp.TYPE:
				valid = False
				for dtt in self.dt:
					if dtt.name == tmp[idx]:
						valid = True
						break
				if not valid:
					raise ValueError(tmp[idx] + " is not a valid data type")
			self.dirs[d] = tmp[idx]
			self.keys[d] = base_len + idx
			idx += 1

		if create:
			self.create()


	def dump(self,):
		""" Dumps the directory path to the console, mainly for debugging. Use str() instead to get a proper directory string"""
		print("Basedir:",self.base_dir,"Dirs:",self.dirs)


	def str(self):
		""" Turns the Dir object information into a directory string. Returns everything of the directory path that is known."""
		ret = self.base_dir
		for d in self.dirs:
			if d == self.dp.GEAR and not self.with_gear:
				continue
			if self.dirs[d] == "":
				break
			ret += self.dirs[d] + "/"
			if ret[-1] != "/":
				ret += "/"
		return ret


	def validDataDir(self):
		""" Validates whether directory information is available until the data_type"""
		for d in self.dirs:
			if d == self.dp.GEAR and not self.with_gear:
				continue
			if self.dirs[d] == "":
				print("Invalid Dir",self.str(),"no " + str(d) + " information")
				return False
		return True


	def exists(self):
		""" Checks whether the directory of this object exists"""
		return os.path.exists(self.str())


	def create(self):
		""" Creates the directory of this object if it does not exist"""
		if not self.exists():
			os.makedirs(self.str(),0o755)


	def replace(self,dir:dp,new_val:str,keep_rest:bool = False):
		""" Can replace one (!) part of the object's directory (given by the keyword in dir) and replaces it with the value in new_val. Useful to change e.g. from one sensor to another or from one event to another. This only returns a string! In case you want to have another Dir object, use replaceCreateDir() instead."""
		tmp_dir = ""
		for d in self.dirs:

			if d == dir or d.name == dir:

				if d == self.dp.TYPE:
					valid = False
					for dtt in self.dt:
						if dtt.name == new_val:
							valid = True
							break
					if not valid:
						raise ValueError(new_val + " is not a valid data type")

				tmp_dir += new_val + "/"
				if keep_rest == False:
					break
			else:
				if d == self.dp.GEAR and not self.with_gear:
					continue
				tmp_dir += self.dirs[d] + "/"
		return self.base_dir + tmp_dir


	def replaceCreateDir(self,dir:dp,new_val:str,keep_rest:bool = False):
		""" Can replace one (!) part of the object's directory (given by the keyword in dir) and replaces it with the value in new_val. Useful to change e.g. from one sensor to another or from one event to another. This returns a new Dir object! In case you only want to have a string, use replace() instead."""
		ret = self.replace(dir,new_val,keep_rest)
		return Dir(self.base_dir,ret.replace(self.base_dir,""),with_gear = self.with_gear)





	def createTypeFolder(self,subs = [e.name for e in dt]):
		""" Creates all the type folders"""
		if self.sensor() == "":
			return False
		for sub in subs:
			if not os.path.exists(self.tosensor()+sub):
				os.mkdir(self.tosensor()+sub,0o775)



	""" Getter for the base, type, sensor, event, gear"""
	def base(self):
		return self.base_dir
	def type(self):
		return self.dirs[self.dp.TYPE]
	def sensor(self):
		return self.dirs[self.dp.SENSOR]
	def event(self):
		return self.dirs[self.dp.EVENT]
	def gear(self):
		return self.dirs[self.dp.GEAR]
	def project(self):
		return self.dirs[self.dp.PROJECT]

	def toproject(self):
		return self.replace(self.dp.PROJECT,self.project(),keep_rest=False)
	def togear(self):
		return self.replace(self.dp.GEAR,self.gear(),keep_rest=False)
	def toevent(self):
		return self.replace(self.dp.EVENT,self.event(),keep_rest=False)
	def tosensor(self):
		return self.replace(self.dp.SENSOR,self.sensor(),keep_rest=False)
	def totype(self):
		return self.replace(self.dp.TYPE,self.type(),keep_rest=False)
	def to(self,d:dp):
		if d == self.dp.PROJECT:
			return self.toproject()
		elif d == self.dp.GEAR:
			return self.togear()
		elif d == self.dp.EVENT:
			return self.toevent()
		elif d == self.dp.SENSOR:
			return self.tosensor()
		elif d == self.dp.TYPE:
			return self.totype()
		elif d in self.dt:
			return self.replace(self.dp.TYPE,d.name)
		else:
			raise ValueError('Unknown directory part.')
