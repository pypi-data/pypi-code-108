import os
import datetime
import math
import ast

import mariqt.core as miqtc
import mariqt.geo as miqtg


def fileSearch(path:str,search):
	""" Return the absolute paths to all files and folders in the folder path that contain one of the search strings in their name"""
	ret = []
	if not os.path.exists(path):
		return ret
	if not isinstance(search,list):
		search = [search]
	files = os.listdir(path)
	for file in files:
		for s in search:
			if s in file.lower():
				ret.append(path+file)
				break
	return ret


def recursiveFolderSearch(path:str,search):
	""" Returns the absolute paths of folders only that contain one of the search strings in their name"""
	ret = []
	if not os.path.exists(path):
		return ret
	if not isinstance(search,list):
		search = [search]
	files = os.listdir(path)
	for file in files:
		if not os.path.isdir(path+file):
			continue
		for s in search:
			if s in file.lower():
				ret.append(path+file)
				break
		ret += recursiveFolderSearch(path + file +"/",search)
	return ret


def recursiveFileSearch(path,search):
	""" Tries to find files containing the string <search> in their names

	Recursively descending to subfolders to do the search. Returns a list of the absolute file paths to all files found.
	TODO Does not return folders. Is that correct?
	"""

	ret = []
	if not os.path.exists(path):
		return ret
	if not isinstance(search,list):
		search = [search]
	files = os.listdir(path)
	for file in files:
		if os.path.isdir(path+file):
			ret += recursiveFileSearch(path+file+"/",search)
		else:
			for s in search:
				if s in file.lower():
					ret.append(path+file)
					break
	return ret


def browseForFiles(path:str,extensions:list = [],recursive=True,skipConfigFiles=True):
	""" Returns list of files (with path) found in path and its subfolders if recursive True. If extensions is not empty only files machting those are returned"""

	ret = []
	if not os.path.exists(path):
		raise Exception(path, "does not exist")
	if path[-1] != "/":
		path += "/"
	files = os.listdir(path)
	for file in files:

		if skipConfigFiles and file[0] == ".":
			continue

		# Recurse into subfolders
		if recursive and os.path.isdir(path+file):
			ret.extend(browseForFiles(path+file+"/",extensions,recursive,skipConfigFiles))

		elif os.path.isfile(path+file):
			if len(extensions) > 0:
				file_ext = os.path.splitext(file)[1].replace(".","").lower()
				if file_ext in extensions:
					ret.append(path+file)
			else:
				ret.append(path+file)

	return ret


def recursiveFileStat(path,ext = False):
	""" Count the number and size of all files in a folder and its subfolders

	Returns tow numbers: the total number of files and the cumulated size of all files in bytes
	"""

	num = 0
	size = 0
	if not os.path.exists(path):
		return num,size
	files = os.listdir(path)
	for file in files:
		if os.path.isdir(path+file):
			tmp_num,tmp_size = recursiveFileStat(path+file+"/")
			num += tmp_num
			size += tmp_size
		else:
			if ext == False or os.path.splitext(file)[1].lower() in ext:
				num += 1
				size += os.stat(path+file).st_size
	return num,size


def tabFileColumnIndex(col_name,cols):
	""" Takes an array (a data header row) of column names and returns the index of one given column that is searched for. Returns -1 if said column name does not exist."""
	if len(col_name) == 0:
		raise Exception("Empty column name!")
	
	search_prefix = False
	search_suffix = False
	if col_name[-1] == "*":
		search_prefix = True
		col_name = col_name[0:len(col_name)-2]
	elif col_name[0] == "*":
		search_suffix = True
		col_name = col_name[1:]

	for k in range(len(cols)):
		if search_prefix and cols[k][0:len(col_name)] == col_name:
			return k
		elif search_suffix and cols[k][-len(col_name):] == col_name:
			return k
		elif cols[k] == col_name:
			return k
	return -1


def tabFileColumnNames(file_path,col_separator="\t"):
	""" Returns all the column names in the table file at file_path"""

	if not os.path.exists(file_path):
		raise ValueError("Could not find file "+file_path)

	with open(file_path,"r",errors="ignore",encoding="utf-8") as file:
		for line in file:
			if line[0] == "#":
				continue
			line = line.strip()
			while line[-1] == col_separator:
				line = line[0:len(line)-1]
			return line.split(col_separator)


def tabFileColumnIndices(col_names,cols,optional=[]):
	""" Receives a list of header field names and a list of required column names and returns the column indices of those colums.

	The column names given in the optional parameter also have to be part of the required_names!
	"""

	col_indcs = {}
	for name in col_names:
		col_indcs[name] = -1

	for name in col_names:
		if type(col_names) == list:
			col_name = name
		else:
			col_name = col_names[name]
		col_indcs[name] = tabFileColumnIndex(col_name,cols)
		if col_indcs[name] < 0:
			if name not in optional:
				raise ValueError("Could not find column \"" + col_name + "\" in header" + str(cols))
			else:
				del col_indcs[name]
	return col_indcs


def tabFileMaxColumnIndexRequested(col_idcs):
	""" Inspects a set od column indices (including multiple column requests: col1;;;col2) and returns the largest number"""

	max_col_idx = -1
	for idx in col_indcs:
		if type(col_indcs[idx]) == int:
			max_col_idx = max(col_indcs[idx],max_col_idx)
		else:
			multi = col_indcs[idx].split(";;;")
			for m in multi:
				max_col_idx = max(int(m),max_col_idx)
	return max_col_idx


def tabFileColumnValues(line,col_indcs:dict,col_separator="\t",convert=False):
	""" Receives a line of a file, a set of column indices to extract values for and an optional column separator

	Returns a dict with the column names as keys and the data values from the row as values
	"""

	# Validate row content and get unix timestamp
	ar = line.strip().split(col_separator)

	ret = {}
	for col in col_indcs:

		if type(col_indcs[col]) == int:
			if col_indcs[col] >= len(ar):
				raise Exception("Index out of bounds",col_indcs,col,ar)
			ret[col] = ar[col_indcs[col]]
			if convert:
				try:
					ret[col] = float(ret[col])
				except:
					pass
				try:
					ret[col] = ast.literal_eval(ret[col].strip())
				except:
					continue
		else:
			multi = col_indcs[col].split(";;;")
			val = ""
			for m in multi:
				idx = int(m)
				if idx >= len(ar):
					raise Exception("Index out of bounds")
				val += ar[idx]+" "
			ret[col] = val.strip()
			if convert:
				try:
					ret[col] = float(ret[col])
				except:
					pass
				try:
					ret[col] = ast.literal_eval(ret[col].strip())
				except:
					continue

	return ret


def tabFileColumnIndicesFromFile(file,required_names,col_separator="\t",optional=[]):
	""" Extracts column indices for requested column names from a file.

	Can handle either an open file object or a path to a file as the first argument
	Read from the file until a row is found that is not a comment.
	The column names given in the optional parameter also have to be part of the required_names!
	"""

	if isinstance(file, str):
		file = open(file,"r",errors="ignore",encoding="utf-8")

	# Skip initial comments
	for line in file:
		if line[0] != "#" and line != "":
			break

	try:
		line
	except NameError:
		raise Exception("Empty file")

	header = line.strip().split(col_separator)
	col_indcs = tabFileColumnIndices(required_names,header,optional)
	max_col_idx = max(list(col_indcs.values()))
	return max_col_idx,col_indcs


def tabFileData(path,required_names,col_separator="\t",key_col="",graceful=False,optional=[],convert=False):
	""" Read all data values from a file for a given set of column names.

	Returns dictionaries with column names as keys and extracted data from the file as values.
	If key_col is not provided or not found in column headers the dictionaries are returned as a list.
	Otherwise the are returned as a dictionary itself with the key_col value being the respecive dictionary's key. 
	The column names given in the optional parameter also have to be part of the required_names!
	"""

	file = open(path,"r",errors="ignore",encoding="utf-8")
	max_col_idx,col_indcs = tabFileColumnIndicesFromFile(file,required_names,col_separator,optional)
	if key_col != "" and col_indcs[key_col] >= 0:
		data = {}
		for line in file:
			# Skip comments within file
			if line[0] == "#":
				continue
			try:
				vals = tabFileColumnValues(line,col_indcs,col_separator,convert)
				key = vals[key_col]
				del vals[key_col]
				# if key already in data (multiple occurrences of same key_col value, e.g. for video multiple occurrences of same file name) make vals to list (if not so yet) and add new vals
				if key in data:
					if not isinstance(data[key],list):
						data[key] = [data[key]]
					data[key].append(vals)
				else:
					data[key] = vals
			except Exception as e:
				if graceful:
					continue
				raise e
	else:
		data = []
		for line in file:
			# Skip comments within file
			if line[0] == "#":
				continue
			try:
				data.append(tabFileColumnValues(line,col_indcs,col_separator,convert))
			except Exception as e:
				if graceful:
					continue
				else:
					file.close()
					raise e
	file.close()
	return data


def positionFromTabFileLine(line:str,col_indcs:dict,date_format:str,add_utc:bool=False,col_separator="\t",const_values:dict={}):
	""" Processes a single data row from a file and convert it into a Position"""

	# Fetch the values from the the columns
	ret = tabFileColumnValues(line,col_indcs,col_separator)

	# Try to create a UTC(!) datetime object.
	timestamp = tryCreateUTCdateTimeMillisec(ret['utc'],date_format,add_utc)

	# Get position data and validate it along the way
	not_allowed = ['.',' ','']

	if "lat" in col_indcs:
		lat = ret["lat"].strip()
	elif "lat" in const_values:
		lat = const_values["lat"]
	else:
		raise Exception("Lat value not found for line")
	try:
		lat = float(lat)
	except Exception as ex:
		raise Exception("Latitude: ", str(ex))

	if "lon" in col_indcs:
		lon = ret["lon"].strip()
	elif "lon" in const_values:
		lon = const_values["lon"]
	else:
		raise Exception("Lon value not found for line")
	try:
		lon = float(lon)
	except Exception as ex:
		raise Exception("Longitude: ", str(ex))

	if lat in not_allowed or lon in not_allowed:
		raise Exception("Lat/Lon have illegal value: "+lat+"/"+lon)

	if "dep" in col_indcs or "dep" in const_values:
		if "dep" in col_indcs:
			dep = ret["dep"].strip()
		elif "dep" in const_values:
			dep = const_values["dep"]
	# parse altitude as negative depth
	elif "alt" in col_indcs or "alt" in const_values:
		if "alt" in col_indcs:
			dep = str(float(ret["alt"].strip()) * -1)
		elif "alt" in const_values:
			dep = str(float(const_values["alt"]) * -1)
	else:
		dep = 0
	if dep in not_allowed:
			return Exception("Depth value has illegal value: "+dep)
	try:
		dep = float(dep)
	except Exception as ex:
		raise Exception("Depth/Altitude: ", str(ex))

	if "hgt" in col_indcs or "hgt" in const_values:
		if "hgt" in col_indcs:
			hgt = ret["hgt"].strip()
		elif "hgt" in const_values:
			hgt = const_values["hgt"]
		if hgt in not_allowed:
			return Exception("Height value has illegal value: "+hgt)
	else:
		hgt = -1
	try:
		hgt = float(hgt)
	except Exception as ex:
		raise Exception("Height: ", str(ex))

	if "uncert" in col_indcs or "uncert" in const_values:
		if "uncert" in col_indcs:
			uncert = ret["uncert"].strip()
		elif "uncert" in const_values:
			uncert = const_values["uncert"]
		if uncert in not_allowed:
			return Exception("Coordinate uncertainty value has illegal value: "+uncert)
	else:
		uncert = -1
	try:
		uncert = float(uncert)
	except Exception as ex:
		raise Exception("Coordinate Uncertainty: ", str(ex))

	# Return Position object
	return miqtg.Position(timestamp,lat,lon,dep,hgt,uncert)


def attitudeFromTabFileLine(line:str,col_indcs:dict,date_format:str,add_utc:bool=False,col_separator="\t",const_values:dict={},anglesInRad=False):
	""" Processes a single data row from a file and convert it into an Attitude"""

	# Fetch the values from the the columns
	ret = tabFileColumnValues(line,col_indcs,col_separator)

	# Try to create a UTC(!) datetime object.
	timestamp = tryCreateUTCdateTimeMillisec(ret['utc'],date_format,add_utc)

	# Get position data and validate it along the way
	not_allowed = ['.',' ','']

	yaw,pitch,roll = 0,0,0
	found = False

	if "yaw" in col_indcs:
		yaw = ret["yaw"].strip()
		found = True
	elif "yaw" in const_values:
		yaw = const_values["yaw"]
		found = True

	if "pitch" in col_indcs:
		pitch = ret["pitch"].strip()
		found = True
	elif "pitch" in const_values:
		pitch = const_values["pitch"]
		found = True

	if "roll" in col_indcs:
		roll = ret["roll"].strip()
		found = True
	elif "roll" in const_values:
		roll = const_values["roll"]
		found = True

	if found == False:
		raise Exception("Could find none of yaw,pitch,roll in line " + line)

	if yaw in not_allowed or pitch in not_allowed or roll in not_allowed:
		raise Exception("yaw,pitch or roll have illegal value: "+yaw+","+pitch+","+roll)

	if anglesInRad:
		yaw = math.degrees(float(yaw))
		pitch = math.degrees(float(pitch))
		roll = math.degrees(float(roll))

	# Return Attitude object
	return miqtg.Attitude(timestamp,float(yaw),float(pitch),float(roll))


def tryCreateUTCdateTimeMillisec(time_str:str,date_format:str,add_utc=True):
	""" tries to parse a datetime string and returns its unix time representation in millisecs. Throws exception if format does not match datetime string """
	if add_utc:
		time_str += "+0000"
		date_format += "%z"
	try:
		timestamp = int(datetime.datetime.strptime(time_str, date_format).timestamp() * 1000)
	except Exception as e:
		raise Exception("Could not create datetime from",time_str,"with format",date_format)
	return timestamp