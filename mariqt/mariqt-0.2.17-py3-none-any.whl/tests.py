""" This file contains various validation functions to check whether given parameters adhere to the MareHub AG V/I conventions"""

import os
import datetime

import mariqt.variables as miqtv
import mariqt.directories as miqtd
import mariqt.core as miqtc

def isValidPerson(o:dict):
	""" Checks whether the dict contains the fields needed to identify a person"""
	req = miqtv.req_person_fields
	for r in req:
		if not r in o or o[r] == "":
			return False
		
		if r == "email" and not isValidEmail(o[r]):
			return False
		if r == "orcid" and not isValidOrcid(o[r]):
			return False
	return True


def isValidDatapath(path:str):
	""" Check whether a path leads to a proper leaf data folder (raw, processed, etc.)"""
	try:
		d = miqtd.Dir(path)
		return d.validDataDir()
	except:
		return False


def isValidEventName(event:str):
	""" Check whether an event name follows the conventions: <project>[-<project part>]_<event-id>[-<event-id-index>][_<device acronym>]"""
	tmp = event.split("_")
	if len(tmp) < 2 or len(tmp) > 3:
		return False
	tmp2 = tmp[0].split("-")
	if len(tmp2) == 2:
		try:
			int(tmp2[1])
		except:
			return False

	tmp2 = tmp[1].split("-")
	if len(tmp2) == 1:
		try:
			int(tmp2[0])
		except:
			return False
	elif len(tmp2) == 2:
		try:
			int(tmp2[0])
			int(tmp2[1])
		except:
			return False
	else:
		return False
	return True


def isValidEquipmentID(eqid:str):
	""" Check whether an equipment id follows the convention: <owner>_<type>-<type index[_<subtype>[_<name>]]>"""
	eq = eqid.split("_")
	if len(eq) < 2:
		print("too short")
		return False
	eq2 = eq[1].split("-")
	if len(eq2) != 2:
		print("second too short")
		return False
	try:
		int(eq2[1])
	except:
		print("second second no int")
		return False
	if eq2[0] not in miqtv.equipment_types:
		print(eq2[0],"not in eq types")
		return False
	return True

def isValidImageName(name:str):
	""" Check whether an image filename adheres to the convention: <event>_<sensor>_<date>_<time>.<ext>"""
	tmp = name.split("_")

	# Find the sensor part of the name
	eq_type_idx = -1
	for i in range(0,len(tmp)):
		tmp2 = tmp[i].split("-")
		if tmp2[0] in miqtv.equipment_types:
			eq_type_idx = i
			break
	if eq_type_idx < 0:
		print(name, "invalid equipment type")
		return False

	# everthing before sensor part is tested on being a valid event name
	event = tmp[0]
	for i in range(1,eq_type_idx-1):
		event += "_" + tmp[i]
	if not isValidEventName(event):
		print(event,"is not a valid event name")
		return False

	# check if from field before sensor part till timespamp is valid equipment id (e.g. GMR_CAM-12)
	eqid = tmp[eq_type_idx-1]
	for i in range(eq_type_idx,len(tmp)-2):
		eqid += "_" + tmp[i]
	if not isValidEquipmentID(eqid):
		print(eqid,"is not a valid equipment id")
		return False

	# check if file extension in miqtv.image_types
	pos = tmp[-1].rfind(".")
	ext = tmp[-1][pos+1:].lower()
	if not ext in miqtv.image_types:
		print(ext," is not a valid image type")
		return False

	try:
		miqtc.parseFileDateTimeAsUTC(name)
	except:
		print(name," cannot be parsed as date time")
		return False

	return True


def isValidiFDOField(field,value):
	""" Tries to parse value to field's dataType and throws exception if it does not succeed """

	
	if 'valid' in miqtv.ifdo_fields[field] and value not in miqtv.ifdo_fields[field]['valid']:
		raise Exception(field+": value \"" + value + "\" not in " + str(miqtv.ifdo_fields[field]['valid']))
	elif field in ['image-filename']:
		if not isValidImageName(value):
			raise Exception('Invalid item name',value)
	elif field in ['image-datetime']:
		try:
			format = miqtv.date_formats['mariqt']
			datetime.datetime.strptime(value,format)
		except:
			raise Exception('Invalid datetime value',value, "does not match format:",format)
	
	elif field in ['image-longitude']:
		try:
			value = float(value)
		except:
			raise Exception(field,'value is not a float',value)
		if value < -180 or value > 180:
			raise Exception(field,'value is out of bounds',value)
	elif field in ['image-latitude']:
		try:
			value = float(value)
		except:
			raise Exception(field,'value is not a float',value)
		if value < -90 or value > 90:
			raise Exception(field,'value is out of bounds',value)
	elif field in ['image-depth']:
		try:
			value = float(value)
		except:
			raise Exception(field,'value is not a float',value)
		if value < 0:
			raise Exception(field,'value is out of bounds',value)
	elif field in ['image-altitude']:
		try:
			value = float(value)
		except:
			raise Exception(field,'value is not a float',value)
		if value < 0:
			raise Exception(field,'value is out of bounds',value)
	elif field in ['image-abstract']:
		if len(value) < 500 or len(value) > 2000:
			raise Exception("Length of the abstract ("+ str(len(value)) +") is too long (max. 2000 chars) or too short (min 500 chars)")
	elif field in ['image-pi']:
		if not isValidPerson(value):
			raise Exception("Not a valid person description for the pi:",value)
	elif field in ['image-creators']:
		for p in value:
			if not isValidPerson(p):
				raise Exception("Not a valid person description for one of the creators: ",value)
	elif field in ['image-coordinate-uncertainty-meters']:
		try:
			value = float(value)
		except:
			raise Exception(field,'value is not a float',value)
		if value < 0:
			raise Exception(field,'value is out of bounds',value)
	elif field in ['image-set-uuid','image-uuid']:
		if not miqtc.is_valid_uuid(value):
			raise Exception(field,"invalid uuid 4:",value)
	elif field in miqtv.ifdo_fields:
		if 'dataType' in miqtv.ifdo_fields[field]:
			if miqtv.ifdo_fields[field]['dataType'] == miqtv.dataTypes.float:
				try:
					value = float(value)
				except:
					raise Exception(field,'value is not a float',value)
	else:
		print("Unknown field \"" + field + "\"")
	
	return value

def isValidiFDOItem(item:dict,header:dict):
	""" Checks if all fields in variables.ifdo_item_core_fields or one of their alternatives are validly filled either in the item itself of in the header. If not an exception is thrown. """

	for req in miqtv.ifdo_item_core_fields:

		field_found_in = None

		# add alt fields
		altFields = [alt for alt in miqtv.ifdo_item_core_fields[req]['alt-fields'] if alt != '']
		reqAndAlts = [req] + altFields
		fieldName = ""
		for field in reqAndAlts:

			fieldName = field
			# check in item
			if field in item and item[field] != "":
				field_found_in = item
				break
			# check in header
			if field in header and header[field] != "":
				field_found_in = header
				break

		# A required field nor its alternative was not found in item or header
		if field_found_in == None:
			raise Exception('Neither',req,'nor one ot the alternatives',altFields,'found in item',item)

		# A required field was found, now check its value
		else:
			field_found_in[fieldName] = isValidiFDOField(fieldName,field_found_in[fieldName])


def isValidiFDOCoreHeader(header:dict):
	""" checks if all fields are validly filled or an alternative field is found in header or all_items_have. If not an exception is thrown """
	for req in miqtv.ifdo_header_core_fields:

		field_found = False
		alt_field_found = False

		if req in header and header[req] != "":
			field_found = True
		elif len(miqtv.ifdo_header_core_fields[req]['alt-fields']) > 0:
			for alt in miqtv.ifdo_header_core_fields[req]['alt-fields']:
				if alt in header and header[alt] != "":
					alt_field_found = True

		# A required field was not found
		if not field_found:
			if not alt_field_found:
				raise Exception('Missing',req,'in header',header,'and alternative fields')
		else:
			# Validata values
			header[req] = isValidiFDOField(req,header[req])


def isValidiFDOCapture(iFDO:dict):
	""" Returns fields of variables.ifdo_capture_fields which are missing in iFDO and throws exception if a field contains an invalid value"""
	return isValidiFDO(iFDO,miqtv.ifdo_capture_fields)
def isValidiFDOContent(iFDO:dict):
	""" Returns fields of variables.ifdo_content_fields which are missing in iFDO and throws exception if a field contains an invalid value"""
	return isValidiFDO(iFDO,miqtv.ifdo_content_fields)


def isValidiFDO(iFDO:dict,ref:dict):
	""" Returns fields of ref which are missing in iFDO and throws exception if a field contains an invalid value"""
	vals_missing = []

	if 'image-set-header' not in iFDO or 'image-set-items' not in iFDO:
		raise Exception("iFOD does not contain 'image-set-header' or 'image-set-items'")

	prog = miqtc.PrintKnownProgressMsg("Checking fields", len(ref), modulo=10)
	for req in ref:
		prog.progress()
		# check if in header
		inHeader = False
		if req in iFDO['image-set-header']:
			iFDO['image-set-header'][req] = isValidiFDOField(req,iFDO['image-set-header'][req])
			inHeader = True

		# if not in header and a 'set' field, its missing
		if req[:9] == 'image-set' and not inHeader:
			vals_missing.append(req)
		# check if in items
		else:
			num = 0
			for item in iFDO['image-set-items']:
				if req not in iFDO['image-set-items'][item]:
					num += 1
				else:
					iFDO['image-set-items'][item][req] = isValidiFDOField(req,iFDO['image-set-items'][item][req])

			if num == len(iFDO['image-set-items']) and not inHeader:
				vals_missing.append(req+": neither the set's header nor any image item contain this field")
			elif num > 0 and not inHeader:
				vals_missing.append(req+": neither the set's header nor "+str(num)+" of "+str(len(iFDO['image-set-items']))+" contain this field")
	prog.clear()
	return vals_missing

	"""
	for req in ref:
		if req[:9] == 'image-set':
			# It is a header field
			if req not in iFDO['image-set-header']:
				vals_missing.append(req)
			else:
				iFDO['image-set-header'][req] = isValidiFDOField(req,iFDO['image-set-header'][req])
		else:
			# It is an item field:
			num = 0
			for item in iFDO['image-set-items']:
				if req not in iFDO['image-set-items'][item]:
					num += 1
				else:
					iFDO['image-set-items'][item][req] = isValidiFDOField(req,iFDO['image-set-items'][item][req])
				
			if num == len(iFDO['image-set-items']):
				vals_missing.append(req+": no image item contains this field")
			elif num > 0:
				vals_missing.append(req+": "+str(num)+" of "+str(len(iFDO['image-set-items']))+" do not contain this field")
	return vals_missing
	"""


def filesHaveUniqueName(files:list):
	""" checks if all files (with or without path) have unique file names. Returns True/False and list of duplicates"""
	fileNames_noPath = []
	duplicates = []
	prog = miqtc.PrintKnownProgressMsg("Checking files have unique name", len(files), modulo=10)
	for file in files:
		prog.progress()
		fileName_noPath = os.path.basename(file)
		if fileName_noPath in fileNames_noPath:
			duplicates.append(fileName_noPath)
		else:
			fileNames_noPath.append(fileName_noPath)
	
	prog.clear()
	if len(duplicates) == 0:
		return True, duplicates
	else:
		return False, duplicates


def isValidOrcid(orcid:str):
	""" returns whether  oricd is valid my using the MOD 11-2 check digit standard """
	# # e.g. "https://orcid.org/0000-0002-9079-593X"
	try:
		orcid = orcid[orcid.rindex("/")+1::]
	except ValueError:
		pass
	if len(orcid) != 19 or orcid[4] != "-" or orcid[9] != "-" or orcid[14] != "-":
		return False

	digits = []
	for char in orcid:
		if char.isdigit():
			digits.append(int(char))
		if char == "X" or char == "x":
			digits.append(10)

	if len(digits) != 16:
		return False

	# MOD 11-2 (see https://www.sis.se/api/document/preview/605987/)
	M = 11
	r = 2

	p = 0
	for digit in digits:
		s = p + digit
		p = s * r
	if s%M == 1:
		return True

	return False


def isValidEmail(mail:str):
	if mail.count("@") == 1:
		return True
	return False