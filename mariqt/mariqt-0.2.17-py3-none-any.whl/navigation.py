import os
import math
import copy
import json
import datetime
import statistics

import mariqt.geo as miqtg
import mariqt.variables as miqtv
import mariqt.files as miqtf


def getMinMaxLatLon(positions:miqtg.Positions,outlier_percent:int = 0):
	""" Returns the minimum and maximum latitude and longitude values of the given positions.

	Returns 0,0,0,0 if the positions are empty"""

	time_points = list(positions.keys())

	lats = []
	lons = []

	for utc in time_points:
		lats.append(positions[utc].lat)
		lons.append(positions[utc].lon)

	lats.sort()
	lons.sort()

	pos = round(len(lats) * outlier_percent / 100)

	return lats[pos],lats[len(lats)-pos-1],lons[pos],lons[len(lats)-pos-1]



def readAllPositionsFromFilePath(src_file_path:str,col_names:dict,date_format:str,col_separator="\t",optional=['hgt'],const_values:dict={}):
	""" Load all navigation data from file.

	Does so based on the file path, the name of the pos_header to extract (see variables.py)
	and the date_format string."""

	navigation_file = open(src_file_path,"r",errors="ignore")
	max_col_idx,col_indcs = miqtf.tabFileColumnIndicesFromFile(navigation_file,col_names,optional=optional,col_separator=col_separator)
	nav_data, msg = readAllPositionsFromFile(navigation_file,col_indcs,date_format,col_separator=col_separator,const_values=const_values)
	navigation_file.close()
	return nav_data, msg


def readAllPositionsFromFile(navigation_file,col_indcs:dict,date_format:str,col_separator="\t",const_values:dict={}):
	""" Read all positions and store by timestamp"""
	nav_data = miqtg.Positions({})
	msg = ""
	lineNr = 0
	for line in navigation_file:
		if line.strip() != "":
			try:
				position = miqtf.positionFromTabFileLine(line,col_indcs,date_format,add_utc=True,col_separator=col_separator,const_values=const_values)
				nav_data.setPos(position)
			except Exception as ex:
				msg += "line " + str(lineNr) + ": " + str(ex.args) + "\n"
		lineNr += 1
	return nav_data, msg


def readAllAttitudesFromFilePath(src_file_path:str,col_names:dict,date_format:str,col_separator="\t",const_values:dict={},anglesInRad=False):
	""" Load all attitude data from file.

	Does so based on the file path, the name of the pos_header to extract (see variables.py)
	and the date_format string."""

	navigation_file = open(src_file_path,"r",errors="ignore")
	max_col_idx,col_indcs = miqtf.tabFileColumnIndicesFromFile(navigation_file,col_names,col_separator=col_separator)
	att_data, msg = readAllAttitudesFromFile(navigation_file,col_indcs,date_format,col_separator=col_separator,const_values=const_values,anglesInRad=anglesInRad)
	navigation_file.close()
	return att_data, msg


def readAllAttitudesFromFile(navigation_file,col_indcs:dict,date_format:str,col_separator="\t",const_values:dict={},anglesInRad=False):
	""" Read all Attiudes and store by timestamp"""
	attitude_data = miqtg.Attitudes({})
	msg = ""
	lineNr = 0
	for line in navigation_file:
		if line.strip() != "":
			try:
				attitude = miqtf.attitudeFromTabFileLine(line,col_indcs,date_format,add_utc=True,col_separator=col_separator,const_values=const_values,anglesInRad=anglesInRad)
				attitude_data.setAtt(attitude)
			except Exception as ex:
				msg += "line " + str(lineNr) + ": " + str(ex.args) + "\n"
		lineNr += 1
	return attitude_data, msg


def runAutomatedCuration(nav_data,params:dict):
	""" Runs all steps required for an automated curation of the navigation data."""

	if nav_data.len() < 50:
		return False, "ERROR: Very few positions (" + str(nav_data.len()) + "). Skipping.", {}

	log = []
	nav_data_curated = copy.deepcopy(nav_data)

	# Remove duplicate position values
	num_duplicates = removeDuplicatePositions(nav_data_curated)
	log.append("Removed "+str(num_duplicates)+" duplicate positions")

	# Remove temporal outliers
	num_time_outliers = removeTemporalOutliers(nav_data_curated)
	log.append("Removed "+str(num_time_outliers)+" positions as time outliers")

	# Remove positions that are outliers by travel speed
	time_removals = removeSpeedOutliers(nav_data_curated,params["max_lateral_speed_m-per-s"],params["max_vertical_speed_m-per-s"],params["max_time_gap_s"])
	log.append("Removed "+str(time_removals)+" positions due to excess vehicle speed")

	# Remove positions that have few close neighbors (potential outliers)
	num_outliers = removeSpatialOutliers(nav_data_curated,params["outlier_check_min_neighbors"],params["max_allowed_outlier_lateral_dist_m"],params["max_allowed_outlier_vertical_dist_m"],params["outlier_check_time_window_size_s"])
	log.append("Removed "+str(num_outliers)+" spatial outliers")

	# Smooth remaining positions
	uncertainty = smoothPositionsSlidingGaussian(nav_data_curated,params["smoothing_gauss_half_width_s"])
	log.append(str(nav_data_curated.len())+" positions smoothed")


	# Spline data gaps to create result file with values at 1s interval
	added_spline_values,spline_uncertainty = splineToOneSecondInterval(nav_data_curated,uncertainty)
	log.append("Added "+str(added_spline_values)+" interpolated positions to the position list")

	# Check how much new data has been added
	if added_spline_values > nav_data.len()*10 and params['processing_type'] == "transect":

		return False, "Too many interpolations in relation to original data (+"+str(round(added_spline_values/(len(nav_data_curated.positions))*100))+"%). Skipping.)", {}

	return nav_data_curated, log, spline_uncertainty


def removeDuplicatePositions(positions:miqtg.Positions):
	""" Remove duplicates values where the lat, lon, dep values for consecutive time points are identical."""
	time_points = list(positions.keys())
	time_points.sort()

	pre_lat = -1
	pre_lon = -1
	pre_dep = -1
	num_duplicates = 0

	for utc in time_points:
		if positions[utc].lat == pre_lat and positions[utc].lon == pre_lon and positions[utc].dep == pre_dep:
			positions.remUTC(utc)
			num_duplicates += 1
			continue

		pre_lat = positions[utc].lat
		pre_lon = positions[utc].lon
		pre_dep = positions[utc].dep

	return num_duplicates


def removeTemporalOutliers(positions:miqtg.Positions, minimum_data_values_per_hour:int=10):
	""" Remove temporal outliers"""
	time_points = list(positions.keys())
	time_points.sort()

	# Construct a histogram of all days occurring in the data set
	time_hist = {}
	for utc in time_points:
		hour = datetime.datetime.fromtimestamp(utc / 1000,tz=datetime.timezone.utc).strftime("%Y%m%d%H")
		if hour not in time_hist:
			time_hist[hour] = 1
		else:
			time_hist[hour] += 1

	num_time_outliers = 0
	for utc in time_points:
		hour = datetime.datetime.fromtimestamp(utc / 1000,tz=datetime.timezone.utc).strftime("%Y%m%d%H")
		if time_hist[hour] < minimum_data_values_per_hour:
			positions.remUTC(utc)
			num_time_outliers += 1
	return num_time_outliers


def removeSpeedOutliers(positions:miqtg.Positions,max_lateral_speed:float=2.0,max_vertical_speed:float=3.0,max_time_gap:int=300):
	""" Removes position outliers by checking for values exceeding a given lateral and vertical speed threshold Speeds given im [m/s], time gap given in [s]"""
	time_points = list(positions.keys())
	time_points.sort()

	pre_utc = -1
	pre_lat = -1
	pre_lon = -1
	pre_dep = -1
	time_removals = 0

	for utc in time_points:

		lat = positions[utc].lat
		lon = positions[utc].lon
		dep = positions[utc].dep

		time_dist = max(1,(utc - pre_utc) / 1000)

		# If data gap of more than max_time_gap seconds occurs, see this as a new starting point
		if time_dist > max_time_gap:
			pre_utc = utc
			pre_lat = lat
			pre_lon = lon
			pre_dep = dep
			continue

		spat_dist = miqtg.distanceLatLon(pre_lat,pre_lon,lat,lon)
		vert_dist = abs(pre_dep - dep)

		lateral_speed = spat_dist / time_dist
		vertical_speed = vert_dist / time_dist

		if lateral_speed > max_lateral_speed or vertical_speed > max_vertical_speed: # m/s
			positions.remUTC(utc)
			time_removals += 1
			continue

		pre_utc = utc
		pre_lat = lat
		pre_lon = lon
		pre_dep = dep

	return time_removals


def removeSpatialOutliers(positions:miqtg.Positions,
							min_neighbors:int=5,
							max_allowed_lateral_distance:int=10,
							max_allowed_vertical_distance:int=10,
							time_window_size:int=60):
	""" Removes positions that have few close neighbors (potential outliers). Distances in meters, time_window_size in seconds """

	time_points = list(positions.keys())
	time_points.sort()

	tmp_positions = {}
	num_outliers = 0

	j = 0
	for utc in time_points:

		lat = positions[utc].lat
		lon = positions[utc].lon
		dep = positions[utc].dep

		num_close = 0

		for i in range(-time_window_size,time_window_size):
			if i == 0:
				continue
			start_index = j
			timePointsInWindow, start_index = getPositionsInTimeRange(time_points,utc + (i * 1000 -1), utc + (i+1) * 1000, start_index)
			for time_point in timePointsInWindow:

				t_lat = positions[time_point].lat
				t_lon = positions[time_point].lon
				t_dep = positions[time_point].dep

				lateral_dist = miqtg.distanceLatLon(t_lat,t_lon,lat,lon) / abs(i)
				vertical_dist = abs((dep-t_dep) / i)

				# Is this neighbor less than both the requested distances away?
				if lateral_dist < max_allowed_lateral_distance and vertical_dist < max_allowed_vertical_distance:
					num_close += 1

		if num_close > min_neighbors:
			tmp_positions[utc] = miqtg.Position(utc,lat,lon,dep)
		else:
			num_outliers += 1

		j += 1
	positions.positions = copy.deepcopy(tmp_positions)
	return num_outliers

def getPositionsInTimeRange(time_points:list,t_min:int,t_max:int,t_startIndex:int):
	""" returns list of position within time range. Start search at t_start. Postions Must be ordered by time """
	time_points_InRange = []

	# forward
	last_index = t_startIndex
	for i in range(t_startIndex,len(time_points)):
		if time_points[i] > t_min and time_points[i] < t_max:
			time_points_InRange.append(time_points[i])
			last_index = i
		if time_points[i] >= t_max:
			break
	# backward
	for i in range(t_startIndex -1,-1,-1):
		if time_points[i] > t_min and  time_points[i] < t_max:
			time_points_InRange.append(time_points[i])
			last_index = i
		if time_points[i] <= t_min:
			break
	if len(time_points_InRange) > 1:
		time_points_InRange.sort()

	return time_points_InRange, last_index

def smoothPositionsSlidingGaussian(positions:miqtg.Positions,gauss_half_width:int=60):
	""" Smoothes position data with a sliding Gaussian window.

	Takes raw position data and applies a sliding window smoothing using a Gaussian
	to adjust the impact of data values to a specific time point by their temporal
	distance from said time point. You can adjust the size of the gaussian by the
	gauss_half_width paramater in seconds. The whole gaussian window is of size 2*gauss_half_width+1
	"""

	time_points = list(positions.keys())
	time_points.sort()

	# Compute a gaussian curve to smooth the posi points that contribute to one new position
	gauss = {}
	for i in range(-gauss_half_width,gauss_half_width):
		gauss[i] = math.exp(-i*i/(2/6*gauss_half_width*gauss_half_width))

	smoothed_pos_tmp = {}
	uncertainty = {}

	pre_lat = -1
	pre_lon = -1
	pre_dep = -1
	pre_hgt = -1

	j = 0
	for utc in time_points:

		g_sum = 0
		new_lat = 0.0
		new_lon = 0.0
		new_dep = 0.0
		new_hgt = 0.0

		# Get current lat / lon
		lat = positions[utc].lat
		lon = positions[utc].lon
		dep = positions[utc].dep
		hgt = positions[utc].hgt

		# Find posi values within the maximum time offset and accumulate their values
		timePointsInWindowSections = [] 
		for i in range(-gauss_half_width, gauss_half_width):
			start_index = j
			timePointsInWindow, start_index = getPositionsInTimeRange(time_points,utc + (i * 1000 -1), utc + (i+1) * 1000, start_index)
			timePointsInWindowSections.append(timePointsInWindow)
			for time_point in timePointsInWindow:
				new_lat += positions[time_point].lat * gauss[i]
				new_lon += positions[time_point].lon * gauss[i]
				new_dep += positions[time_point].dep * gauss[i]
				new_hgt += positions[time_point].hgt * gauss[i]
				g_sum += gauss[i]

		# Normalise the new coordinates by the total gaussian weight of the contributing positions
		new_lat /= g_sum
		new_lon /= g_sum
		new_dep /= g_sum
		new_hgt /= g_sum

		# Compute the variance of the new points towards all the contributing points
		var = 0.0
		k = 0
		for i in range(-gauss_half_width, gauss_half_width):
			for time_point in timePointsInWindowSections[k]:
				dist = miqtg.distanceLatLon(new_lat,new_lon,positions[time_point].lat,positions[time_point].lon)
				dist += (positions[time_point].dep - new_dep) * (positions[time_point].dep - new_dep)
				var += math.sqrt(dist) * gauss[i]
			k += 1

		var /= g_sum

		# Store new positions
		smoothed_pos_tmp[utc] = miqtg.Position(utc,new_lat,new_lon,new_dep,new_hgt)
		uncertainty[utc] = var

		j += 1

	positions.positions = copy.deepcopy(smoothed_pos_tmp)
	return uncertainty


def splineToOneSecondInterval(positions:miqtg.Positions,uncertainty:dict = {}):
	""" Fills gaps bigger one sec in the position list with 1 Hz interpolated samples"""

	time_points = list(positions.keys())
	time_points.sort()

	pre_utc = -1
	pre_lat = -1
	pre_lon = -1
	pre_dep = -1
	pre_hgt = -1

	splined_positions = {}
	ret_uncertainty = {}
	added_points = 0

	for utc in time_points:

		lat = positions[utc].lat
		lon = positions[utc].lon
		dep = positions[utc].dep
		hgt = positions[utc].hgt

		# Interpolate between previous and current value
		if pre_utc > 0 and pre_utc+1000 < utc:
			for tmp_utc in range(pre_utc+1000,utc,1000):
				alpha = 1.0 * (tmp_utc - pre_utc) / (utc - pre_utc)
				new_lat = positions[pre_utc].lat * (1-alpha) + positions[utc].lat * alpha
				new_lon = positions[pre_utc].lon * (1-alpha) + positions[utc].lon * alpha
				new_dep = positions[pre_utc].dep * (1-alpha) + positions[utc].dep * alpha
				new_hgt = positions[pre_utc].hgt * (1-alpha) + positions[utc].hgt * alpha

				if pre_utc in uncertainty and utc in uncertainty:
					ret_uncertainty[tmp_utc] = uncertainty[pre_utc] * (1-alpha) + uncertainty[utc] * alpha
				else:
					ret_uncertainty[tmp_utc] = miqtg.distanceLatLon(new_lat,new_lon,positions[pre_utc].lat,positions[pre_utc].lon) * (1-alpha) + miqtg.distanceLatLon(new_lat,new_lon,positions[utc].lat,positions[utc].lon) * alpha

				splined_positions[tmp_utc] = miqtg.Position(tmp_utc,new_lat,new_lon,new_dep,new_hgt)

				added_points += 1

		# Add current value to position list
		splined_positions[utc] = miqtg.Position(utc,lat,lon,dep,hgt)

		pre_utc = utc
		pre_lat = lat
		pre_lon = lon
		pre_dep = dep
		pre_hgt = hgt

	positions.positions = copy.deepcopy(splined_positions)
	return added_points, ret_uncertainty


def selectSamplingPosition(positions:miqtg.Positions):
	""" Selects the sampling location from a position profile as the the maximum depth time point"""

	time_points = list(positions.keys())

	max_dep = 0
	for utc in time_points:
		if positions[utc].dep > max_dep:
			max_lat = positions[utc].lat
			max_lon = positions[utc].lon
			max_dep = positions[utc].dep
			max_hgt = positions[utc].hgt
			max_utc = utc

	return miqtg.Position(max_utc,max_lat,max_lon,max_dep,max_hgt)


def selectTransectMiddlePoint(positions:miqtg.Positions):
	""" Selects the position of the median time point of a series"""
	time_points = list(positions.keys())

	time_med = statistics.median(time_points)

	min_diff = 10000000000
	for utc in time_points:
		if abs(time_med - utc) < min_diff:
			avg_utc = utc
			avg_lat = positions[utc].lat
			avg_lon = positions[utc].lon
			avg_dep = positions[utc].dep
			avg_hgt = positions[utc].hgt
			min_diff = abs(time_med  - utc)
	return miqtg.Position(avg_utc, avg_lat, avg_lon, avg_dep, avg_hgt)


def checkPositionContent(positions:miqtg.Positions):
	""" Check whether all nav data of one col are equal or empty.

	Returns seven booleans: lat_identical,lon_identical,dep_identical,hgt_identical,dep_not_zero,hgt_not_zero,uncert_not_zero."""

	lat_identical = True
	lon_identical = True
	dep_identical = True
	hgt_identical = True
	dep_not_zero = False
	hgt_not_zero = False
	uncert_not_zero = False
	for i,utc in enumerate(positions.positions):
		if i > 0:
			if prev_lat != positions.positions[utc].lat:
				lat_identical = False
			if prev_lon != positions.positions[utc].lon:
				lon_identical = False
			if prev_dep != positions.positions[utc].dep:
				dep_identical = False
			if prev_hgt != positions.positions[utc].hgt:
				hgt_identical = False
		if positions.positions[utc].dep != 0:
			dep_not_zero = True
		if positions.positions[utc].hgt != -1:
			hgt_not_zero = True
		if positions.positions[utc].uncert > 0:
			uncert_not_zero = True
		prev_lat = positions.positions[utc].lat
		prev_lon = positions.positions[utc].lon
		prev_dep = positions.positions[utc].dep
		prev_hgt = positions.positions[utc].hgt
	return lat_identical,lon_identical,dep_identical,hgt_identical,dep_not_zero,hgt_not_zero,uncert_not_zero


def checkPositionProductsExists(path:str,name:str,output_types:list):
	""" Check whether all the products exist as files in the given path"""

	for ot in output_types:
		dst_file_name = name
		if ot == "kml":
			dst_file_name += ".kml"
		elif ot == "geojson":
			dst_file_name += ".geojson"
		else:
			dst_file_name += "_"+ot+".txt"
		if not os.path.exists(path + dst_file_name):
			return False
	return True


def writeMultiplePositionTypes(positions:miqtg.Positions,path:str,name:str,output_types:list,overwrite:bool=False,with_depth:bool=True,with_height:bool=True):
	""" Can produce several position output formats at once."""

	for ot in output_types:
		dst_file_name = name
		if ot == "kml":
			dst_file_name += ".kml"
		elif ot == "geojson":
			dst_file_name += ".geojson"
		else:
			dst_file_name += "_"+ot+".txt"
		dst_file_path = path + dst_file_name
		writePositions(positions,dst_file_path,ot,with_depth = with_depth,with_height = with_height)


def writePositions(positions:miqtg.Positions,dst_path:str,output_type:str,overwrite:bool=False,with_depth:bool=True,with_height:bool=True):
	""" Write positions any kind of file, specified by the output_type"""

	if os.path.exists(dst_path) and overwrite == False:
		print("Not overwriting positions at",dst_path)
		return

	# Open smoothed output file
	o = open(dst_path,"w",errors="ignore",encoding='utf-8')
	if not o:
		raise Exception("ERROR: Could not open " + dst_path + " for writing.");

	if output_type == "track":
		writePositionsToTrack(o,positions,with_depth)

	elif output_type == "gx_track":
		writePositionsToGxTrack(o,positions,with_depth)

	elif output_type == "kml":
		name = dst_path[dst_path.rfind('/')+1:].replace(".kml","")
		writePositionsToKML(o,positions,name,with_depth)

	elif output_type == "geojson":
		name = dst_path[dst_path.rfind('/')+1:].replace(".geojson","")
		writePositionsToGeoJSON(o,positions,name,with_depth)

	else:
		# You can use this function to write any kind of tab file header specified in definitions.py
		writePositionsToTabFile(o,positions,output_type,with_depth,with_height)


def writePositionsToTrack(o,positions:miqtg.Positions,with_depth:bool = False):
	""" Type 'track' has no header, it just dumps the positions consecutively without time information"""
	for utc in positions.positions:
		if with_depth:
			o.write(str(round(positions[utc].lon,7))+","+str(round(positions[utc].lat,7))+","+str(-round(positions[utc].dep,1))+" ")
		else:
			o.write(str(round(positions[utc].lon,7))+","+str(round(positions[utc].lat,7))+" ")


def writePositionsToGxTrack(o,positions:miqtg.Positions,with_depth:bool = False):
	""" Type 'gx_track' has no header, it just dumps the time points consecutively followed by the positions"""
	position_str = ""
	for utc in positions.positions:
		o.write("<when>"+datetime.datetime.fromtimestamp(utc,tz=datetime.timezone.utc).strftime(miqtv.date_formats['gx_track'])+"</when>\n")
		position_str += "<gx:coord>" + str(round(positions[utc].lon,7)) + " " + str(round(positions[utc].lat,7))
		if with_depth:
			position_str += " " + str(-round(positions[utc].dep,1))
		position_str += "</gx:coord>\n"
	o.write(position_str)


def writePositionsToKML(o,positions:miqtg.Positions,name,with_depth:bool = False):
	""" Type 'kml' adds an XML header to a gx_track data representation, including a name"""
	o.write('<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2"><Folder><Placemark><name>'+name+'</name><gx:Track>')
	writePositionsToGxTrack(o,positions,with_depth)
	o.write('</gx:Track></Placemark></Folder></kml>')


def writePositionsToGeoJSON(o,positions:miqtg.Positions,name,with_depth:bool = False):
	""" Type 'geojson' turns the positions into a json representation. It is recommened to use this format!"""
	coordinates = []
	if with_depth:
		for utc in positions.positions:
			coordinates.append([positions.positions[utc].lon,positions.positions[utc].lat,positions.positions[utc].dep])
	else:
		for utc in positions.positions:
			coordinates.append([positions.positions[utc].lon,positions.positions[utc].lat])
	if len(coordinates) == 1:
		type = "Point"
	else:
		type = "MultiPoint"
	gj = {"type": "FeatureCollection",
			"name": name,
			"crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:OGC:1.3:CRS84" } },
			"features": [
				{ "type": "Feature",
				"properties": { "id": 0 },
				"geometry": { "type": type, "coordinates": coordinates } }]}
	json.dump(gj, o, ensure_ascii=False, indent=4)


def writePositionsToTabFile(o,positions:miqtg.Positions,header_format:str,with_depth:bool = False,with_height:bool = False):
	""" Write a tab separated ascii file of the positions. You can specify which column headers shall be used for the various output types defined in definitions.py"""

	# Construct output file header
	if header_format not in miqtv.pos_header:
		raise ValueError("Output type "+ header_format + " not implemented")
	new_header = ""
	for col in miqtv.pos_header[header_format]:
		if col == "dep" and not with_depth:
			continue
		elif col == "hgt" and not with_height:
			continue
		new_header += miqtv.pos_header[header_format][col] + "\t"
	o.write(new_header.strip() + "\n")

	date_format = miqtv.date_formats['pangaea']
	if header_format in miqtv.date_formats:
		date_format = miqtv.date_formats[header_format]

	for utc in positions.positions:
		line = datetime.datetime.fromtimestamp(utc / 1000,tz=datetime.timezone.utc).strftime(date_format)+"\t"+str(round(positions[utc].lat,7))+"\t"+str(round(positions[utc].lon,7))
		if with_depth:
			line += "\t"+str(round(positions[utc].dep,1))
		if with_height:
			line += "\t"+str(round(positions[utc].hgt,1))
		line += "\n"
		o.write(line)
