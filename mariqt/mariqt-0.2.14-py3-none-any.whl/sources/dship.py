import os
import io
import urllib
import zipfile
import requests
import datetime

import mariqt.geo as miqtg
import mariqt.variables as miqtv
import mariqt.provenance as miqtp
import mariqt.directories as miqtd
import mariqt.sources.dship_settings as miqtsds

def getMaxDepthForEvents(dship_events,req_actions):
	""" Adds the maximum depth of all actions as another field into the event's dict."""
	devop_maxdepth = {}
	for event in dship_events:
		for req in req_actions:
			found_a = False
			for a in dship_events[event]['actions']:
				if a['action'] == req:
					if req == "max depth/on ground":
						dep = a['dep']
					else:
						dep = 0
					devop_maxdepth[event.replace("/","-")] = {'utc':a['utc'],'lat':a['lat'],'lon':a['lon'],'dep':dep,'typ':"DSHIP action: "+a['action']}
					found_a = True
					break
			if found_a:
				break
	return devop_maxdepth


def addEndToDSHIPEventsByLastActionBeforeNextEvent(dship_events):
	""" Adds the last action of an event as another field to the event's dict."""
	for event in dship_events:
		next_event = 0
		for a in dship_events[event]['actions']:
			next_event = max(next_event,a['utc'])
		for te in dship_events:
			if dship_events[te]['start'] <= dship_events[event]['start']:
				continue
			next_event = min(next_event,dship_events[te]['start'])
		dship_events[event]['end'] = next_event

def addEndToDSHIPEventsByLastAction(dship_events):
	""" Adds the last action of an event as another field to the event's dict."""
	for event in dship_events:
		maxt = 0
		for a in dship_events[event]['actions']:
			maxt = max(maxt,a['utc'])
		dship_events[event]['end'] = maxt

def removeEventsByOtherCruises(dship_events,cruise):
	""" Removes all events from list that are not from the given cruise"""
	rem = []
	for event in dship_events:
		if cruise not in event:
			rem.append(event)
	for r in rem:
		del dship_events[r]

def renameEvents(dship_events,add_gear=True):
	""" Replaces the slash in the event name by a dash and can append the gear (event['code']) as a suffix to the event name"""
	add_events = {}
	for event in dship_events:
		new_event = event.replace("/","-")
		if add_gear:
			if dship_events[event]['code'] not in new_event:
				new_event += "_" + dship_events[event]['code']
		if new_event != event:
			add_events[new_event] = event
	for new in add_events:
		dship_events[new] = dship_events[add_events[new]]
		del dship_events[add_events[new]]

def unzipDSHIPExport(path_to_navigation_zip:str,path:miqtd.Dir,prov:miqtp.Provenance = False):
	""" Unzips a dship export zip file and distributes the files to the proper folder."""

	if path.sensor() == "":
		return False
	with zipfile.ZipFile(path_to_navigation_zip, 'r') as zip_ref:
		zip_ref.extractall(path.tosensor())

	path.createTypeFolder(['protocol','external','raw'])
	sens_path = path.tosensor()
	files = os.listdir(sens_path)

	for file in files:
		if not os.path.isfile(sens_path+file):
			continue
		src = sens_path+file
		if ".sys" in file:
			dst = sens_path+"/protocol/"+file
			if prov != False:
				prov.addPreviousProvenance(src)
		elif ".xml" in file:
			dst = sens_path+"/external/"+file
		elif ".dat" in file:
			dst = sens_path+"/raw/"+file
		else:
			continue
		if os.path.exists(dst):
			os.remove(src)
		else:
			os.rename(src,dst)


def findDSHIPSourceFile(path:miqtd.Dir):
	""" Searches for a file in the sensor part of the path that has the string '.dat' in it"""
	src_file_dir = path.tosensor()+"raw/"
	src_files = os.listdir(src_file_dir)
	for src in src_files:
		if ".dat" in src:
			return src_file_dir + src
	return False


def parseDSHIPDeviceOperationsOrEventsFile(path:str,delim="\t",date_fmt="%Y/%m/%d %H:%M:%S"):
	""" Tries to read a DSHIP file from disk. Can differentiate between deviceoperations and events files"""
	if not os.path.exists(path):
		print("Error reading DSHIP event file. No such file:",path)
		return []
	with io.open(path, "r", encoding="ISO 8859-1") as file:
		header = file.readline().split(delim)
		if len(header) == 18 and header[0] == "Station - Device Operation":
			return parseDSHIPEventsFile(path,delim,date_fmt)
		elif len(header) == 45 and header[1] == "Station - Device Operation":
			return parseDSHIPDeviceOperationsFile(path,delim,date_fmt)
		else:
			print("Error parsing DSHIP file. Unknown file format in ",path)


def parseDSHIPEventsFile(path:str,delim="\t",date_fmt="%Y/%m/%d %H:%M:%S"):
	""" Parse a DSHIP export file for events"""
	if not os.path.exists(path):
		print("Error reading DSHIP event file. No such file:",path)
		return []
	with io.open(path, "r", encoding="ISO 8859-1") as file:
		header = file.readline().split(delim)
		if len(header) != 18 or header[0] != "Station - Device Operation":
			print("Error reading DSHIP event file. Not an event file:",path)
			return []
		events = {}
		for line in file:
			line = line.split(delim)
			device_operation = line[0]
			utc = datetime.datetime.strptime(line[1]+"+0000",date_fmt+"%z")
			if device_operation not in events:
				events[device_operation] = {"code":line[3],"actions":[],"start":utc.timestamp()}
			lat = miqtg.getDecDegCoordinate(line[14])
			lon = miqtg.getDecDegCoordinate(line[15])
			events[device_operation]['actions'].append({"utc":utc.timestamp(),"action":line[6],"lat":lat,"lon":lon,"dep":float(line[13])})
			events[device_operation]['start'] = min(events[device_operation]['start'],utc.timestamp())
		return events


def parseDSHIPDeviceOperationsFile(path:str,delim="\t",date_fmt="%Y/%m/%d %H:%M:%S"):
	""" Parse a DSHIP export file for device operations"""
	if not os.path.exists(path):
		print("Error reading DSHIP device operation file. No such file:",path)
		return []
	with io.open(path, "r", encoding="ISO 8859-1") as file:
		header = file.readline().split(delim)
		if len(header) != 45 or header[1] != "Station - Device Operation":
			print("Error reading DSHIP device operation file. Not a device operation file:",path)
			return []
		events = {}

		actions = {"start":[6,8],"end":[12,14],"station start":[18,19],"profile start":[23,24],"max depth/on ground":[28,29],"station end":[33,34],"profile end":[38,39]}
		for line in file:
			line = line.split(delim)
			device_operation = line[1]
			code = line[5]

			for a in actions:
				add_a = a
				if a == "start" and line[actions[a][0]+1] in actions:
					continue
				else:
					add_a = line[actions[a][0]+1]
				if a == "end" and line[actions[a][0]+1] in actions:
					continue
				else:
					add_a = line[actions[a][0]+1]
				if line[actions[a][0]] == "" or line[actions[a][1]] == "" or line[actions[a][1]+1] == "" or line[actions[a][1]+2] == "":
					continue
				utc = datetime.datetime.strptime(line[actions[a][0]]+"+0000",date_fmt+"%z")
				lat = miqtg.getDecDegCoordinate(line[actions[a][1]+0])
				lon = miqtg.getDecDegCoordinate(line[actions[a][1]+1])
				dep = float(line[actions[a][1]+2])

				if device_operation not in events:
					events[device_operation] = {"code":code,"actions":[],"start":utc.timestamp()}
				events[device_operation]['actions'].append({"utc":utc.timestamp(),"action":add_a,"lat":lat,"lon":lon,"dep":dep})
				events[device_operation]['start'] = min(events[device_operation]['start'],utc.timestamp())

		return events


def exportNavigationFromDSHIPForOneStation(dship_url:str,export_name:str,start_unix,end_unix,steps,user_name,user_mail,pos_header_name:str,beacon_id=""):
	""" A function to call for each event to perform the HTTP request to the DSHIP database. Start and end times need to be UTC string in the format: %Y-%m-%d %H:%M:%S%z"""

	# The time interval and steps as requested by the DSHIP "API"
	#start_unix = datetime.datetime.strptime(start, '%Y-%m-%d %H:%M:%S%z').timestamp()
	#end_unix = datetime.datetime.strptime(end, '%Y-%m-%d %H:%M:%S%z').timestamp()
	steps_milli = steps * 1000


	if beacon_id in miqtv.pos_header[pos_header_name]:
		fields = miqtv.pos_header[pos_header_name][beacon_id]
	else:
		fields = miqtv.pos_header[pos_header_name]

	if 'dep' in fields:
		data = miqtsds.request.replace("__ORDER__",miqtsds.order_3d).replace("__LATFIELD__",fields['lat']).replace("__LONFIELD__",fields['lon']).replace("__DEPFIELD__",fields['dep']).replace("__USERNAME__",user_name).replace("__EXPORTNAME__",export_name).replace("__USERMAIL__",urllib.parse.quote(user_mail)).replace("__STARTTIME__",str(start_unix)).replace("__ENDTIME__",str(end_unix)).replace("__TIMESTEPS__",str(steps_milli))
	else:
		data = miqtsds.request.replace("__ORDER__",miqtsds.order_2d).replace("__LATFIELD__",fields['lat']).replace("__LONFIELD__",fields['lon']).replace("__USERNAME__",user_name).replace("__EXPORTNAME__",export_name).replace("__USERMAIL__",urllib.parse.quote(user_mail)).replace("__STARTTIME__",str(start_unix)).replace("__ENDTIME__",str(end_unix)).replace("__TIMESTEPS__",str(steps_milli))


	r = requests.post(dship_url, data=data, headers=miqtsds.headers)
	if r.status_code != 200:
		print(r.text)
	return r.status_code == 200


def exportNavigationDataFromDSHIP(events,user_name,user_mail,data_frequency = 5,dship_url="",vessel="SO"):
	""" Calls the DSHIP API to extract information

	This function takes a list of events in the form:
		[{'name':<station_name>,
		'start':<station start time (timestamp)>,
		'end':<station end time (timestamp)>},
		...[more stations]]
	and executes calls to the DSHIP API to fetch data for those events (aka stations).
	If the event list contains beacon ids ('beacon_id':<usbl beacon id - optional>) in the range >= 0
	it will request USBL data, otherwise it will fetch the ship's navigation data.
	Requires a user name and user email under which the data will be made available on the DSHIP server.
	You can set the data frequency (in seconds) at which USBL data points are delivered and the
	usbl_beacon_id for which data shall be exported. This is a general parameter for all
	request but can be overwritten by specifying a beacon_id in the events list.
	"""

	total_success = True

	if dship_url == "":
		dship_url = miqtsds.urls[vessel]
	elif dship_url in miqtsds.urls:
		dship_url = miqtsds.urls[dship_url]

	for event in events:

		if 'beacon_id' in event:
			beacon_id = event['beacon_id']
		else:
			beacon_id = ""

		success = exportNavigationFromDSHIPForOneStation(dship_url,event['name'],int(event['start']),int(event['end']),data_frequency,user_name,user_mail,event['nav_equipment'],beacon_id)
		total_success &= success

		if not success:
			print("Something went wrong fetching data for",event['name'],"Sorry.")
			print(event)
			break

	print("Done. Please check your emails for job completion notifications.")
	return total_success
