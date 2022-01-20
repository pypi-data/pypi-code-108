import os
import subprocess
import math
import re
import copy
import threading
import time

import mariqt.core as miqtc
import mariqt.directories as miqtd
import mariqt.tests as miqtt
import mariqt.variables as miqtv
import mariqt.files as miqtf
import mariqt.provenance as miqtp


def getVideoRuntime(path):
	""" Uses FFMPEG to determine the runtime of a video in seconds. Returns 0 in case their was any issue"""
	if not os.path.exists(path):
		raise Exception("file " + path + " not found!")
	command = "ffprobe -v fatal -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "+path
	result = subprocess.run(command.split(" "),stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
	try:
		return float(result.stdout)
	except:
		return 0


def getVideoStartTime(path):
	""" Uses FFMPEG to determine the start time of a video from the metadata of the video file. Returns an empty string in case there was any issue"""
	if not os.path.exists(path):
		raise Exception("file " + path + " not found!")
	command = "ffprobe -v fatal -show_entries format_tags=creation_time -of default=noprint_wrappers=1:nokey=1 "+path
	result = subprocess.run(command.split(" "),stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
	return result.stdout.decode("utf-8").strip()


def getVideoUUID(path):
	""" Uses exiftool to query an video file for a UUID in its metadata (-identifier) or for mkv uses mkvinfo and 'Segment UID'. Returns an empty string if there is no UUID encoded in the file."""
	
	if not os.path.exists(path):
		raise Exception("file " + path + " not found!")

	ext = path.split('.')[-1]
	if ext.casefold() != 'mkv':

		# for all videos except mkv (matroska)
		command = ["exiftool", "-identifier",path]
		try:
			result = subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
		except FileNotFoundError:
			print("Error: exiftool not found. Install with e.g. apt-get install exiftool")
			return "",""
		all = result.stdout.decode("utf-8").strip()
		if all != "":
			# Get last line of response
			txt = all.split("\n")[-1]
			# Omit Perl warnings
			if txt[0:14] == "perl: warning:":
				txt = ""
			# Omit other warings (e.g. Warning: [minor] Unrecognized MakerNotes)
			elif txt[0:8] == "Warning:":
				txt = ""
			# Omit other errors
			elif txt[0:5] == "Error":
				txt = ""
			else:
				txt = txt.split(":")[1].strip()
		else:
			txt = ""
		return txt, all
	
	else:
		# for mkv (matroska)
		command = ["mkvinfo",path] #.replace(" ","\\ ")

		try:
			result = subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
		except FileNotFoundError:
			print("Error: mkvinfo not found. Install with e.g. apt-get install mkvtoolnix")
			return "",""
		all = result.stdout.decode("utf-8").strip()
		segmentUID_id = "Segment UID:"
		segmentUID_id_matches = [m.start() for m in re.finditer(segmentUID_id, all)]
		if len(segmentUID_id_matches) == 0:
			return "", all
		if len(segmentUID_id_matches) != 1:
			print("Caution! Multiple segments found, first occurrence of Segment UID used for file " + path)
		segmentUID_end = all.find('\n',segmentUID_id_matches[0])
		segmentUIDstr = all[segmentUID_id_matches[0]+len(segmentUID_id):segmentUID_end].replace(" 0x","").replace(" ","")
		return segmentUIDstr, all


def getPhotoUUID(path):
	""" Uses exiftool to query an image file for a UUID in its metadata. Returns an empty string if there is no UUID encoded in the file."""
	if not os.path.exists(path):
		raise Exception("file " + path + " not found!")
	command = ["exiftool", "-imageuniqueid", path]
	try:
		result = subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
	except FileNotFoundError:
		print("Error: exiftool not found. Install with e.g. apt-get install exiftool")
		return "",""
	all = result.stdout.decode("utf-8").strip()
	if all != "":
		# Get last line of response
		txt = all.split("\n")[-1]
		# Omit Perl warnings
		if txt[0:14] == "perl: warning:":
			txt = ""
		# Omit other warings (e.g. Warning: [minor] Unrecognized MakerNotes)
		elif txt[0:8] == "Warning:":
			txt = ""
		# Omit other errors
		elif txt[0:5] == "Error":
			txt = ""
		else:
			try:
				txt = txt.split(":")[1].strip()
			except:
				pass
	else:
		txt = ""
	# check if its maybe written to -identifier instead
	if txt == "":
		return getVideoUUID(path)
	return txt,all

def imageContainsValidUUID(file:str,verbose=False):
	""" returns whether image contains valid UUID and UUID. Throws exception if file extension not in variables.photo_types or variables.video_types
		For many files per directory use the faster imagesContainsValidUUID() """
	if os.path.splitext(file)[1][1:].lower() in miqtv.photo_types:
		uuid,msg = getPhotoUUID(file)
	elif os.path.splitext(file)[1][1:].lower() in miqtv.video_types:
		uuid,msg = getVideoUUID(file)
	else:
		raise Exception("Unsupported file type to determine UUID from metadata: "+os.path.splitext(file)[1][1:])
	
	if uuid == "":
		return False, uuid

	# check for validity
	if not miqtc.is_valid_uuid(uuid):
		if verbose:
			print("Image " + file + " contains invalid UUID " + uuid)
		return False, uuid
	return True, uuid


def imagesContainValidUUID(files:list):
	""" retruns dict {'file':{'uuid':str,'valid:bool'}} """

	# find different directories
	paths = []
	for file in files:
		path = os.path.dirname(file)
		if path not in paths:
			paths.append(path)

	allFilesUUIDs = {}
	prog = miqtc.PrintKnownProgressMsg("Reading files' UUIDs in directory", len(paths),modulo=1)
	for path in paths:
		prog.progress()
		allFilesUUIDsTmp1 = getImageUUIDsForFolder(path)
		# add paths
		allFilesUUIDsTmp2 = {}
		for item in allFilesUUIDsTmp1:
			allFilesUUIDsTmp2[os.path.join(path,item)] = allFilesUUIDsTmp1[item]
		allFilesUUIDs = {**allFilesUUIDs, **allFilesUUIDsTmp2}
	prog.clear()

	# check uuids
	ret = {}
	for item in allFilesUUIDs:
		if item in files:
			valid = False
			if miqtc.is_valid_uuid(allFilesUUIDs[item]):
				valid = True
			ret[item] = {'uuid':allFilesUUIDs[item],'valid':valid}
	
	return ret


def getImagesExifFieldValuesForFolder(path:str,fieldName:str):
	""" Uses exiftool to query all images in folder path for the field value in their metadata (is much faster then doing it for each file separately). Returns a dict with filename -> UUID keys/values"""
	if fieldName[0] != "-":
		fieldName = "-" + fieldName
	command = ["exiftool", "-T", "-filename", fieldName, path]
	try:
		result = subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
	except FileNotFoundError:
		print("Error: exiftool not found. Install with e.g. apt-get install exiftool")
		return "",""
	txt = result.stdout.decode("utf-8").strip()
	ret = {}
	if txt != "":
		lines = txt.split("\n")
		for line in lines:
			tmp = line.split("\t")
			if len(tmp) < 2:
				continue
			ret[tmp[0]] = tmp[1].strip()
	return ret                  


def getImagesAllExifValues(files:list,prov:miqtp.Provenance=None):
	""" Uses exiftool to query all images in folder path for all their exif metadata (is much faster then doing it for each file separately). Returns a dict with filename -> exif keys/values"""

	# find different directories
	paths = []
	for file in files:
		path = os.path.dirname(file)
		if path not in paths:
			paths.append(path)

	allFilesExifTags = {}
	prog = miqtc.PrintKnownProgressMsg("Reading files' Exif tags in directory", len(paths),modulo=1)
	for path in paths:
		prog.progress() 
		allFilesExifTagsTmp = getImagesAllExifValuesForFolder(path,prov,filesOnly=files)
		allFilesExifTags = {**allFilesExifTags, **allFilesExifTagsTmp}
	prog.clear()

	ret = {file:allFilesExifTags[file] for file in allFilesExifTags if file in files}
	return ret


def getImagesAllExifValuesForFolder(path:str,prov:miqtp.Provenance=None,filesOnly=[]):
	""" Uses exiftool to query all images in folder path for all their exif metadata (is much faster then doing it for each file separately). Returns a dict with filename -> exif keys/values"""
	command = ["exiftool",path]
	try:
		result = subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
	except FileNotFoundError:
		print("Error: exiftool not found. Install with e.g. apt-get install exiftool")
		return "",""
	all = result.stdout.decode("utf-8").strip()
	
	ret = {}
	# split per file
	perFile = all.split("========") # TODO works for windows as well?
	for fileExif in perFile:
		fileExif = fileExif.strip()
		if fileExif == "":
			continue
		fileName = ""
		exif = {}
		i = 0
		for line in fileExif.split("\n"):
			i += 1
			if i == 1: # filename should be first line
				fileName = os.path.join(path,line.strip())
				if filesOnly != [] and not fileName in filesOnly:
					break
				else:
					ret[fileName] = exif
					continue
			separtorIndex = line.find(":")
			if separtorIndex == -1:
				msg = "Can't parse exif tag: \'" + line + "\' in file: " + fileName
				if prov != None:
					prov.log(msg)
				else:
					print(msg)
			elif line[0:separtorIndex].strip() != 'Directory':
				exif[line[0:separtorIndex].strip()] = line[separtorIndex+1::].strip()

	return ret


def getImageUUIDsForFolder(path:str):
	""" Uses exiftool to query all images in folder path for the UUID in their metadata (is much faster then doing it for each file separately). 
	Returns a dict with filename -> UUID keys/values. """
	ret = {}

	# photos
	retTmp = getImagesExifFieldValuesForFolder(path,"imageuniqueid")
	ret = {**ret, **retTmp}

	# videos
	retTmp = getImagesExifFieldValuesForFolder(path,"identifier")
	# make sure for photos valied previous entries are not overridden by invalid ones here 
	toRemove = []
	for file in retTmp:
		if os.path.splitext(file)[1][1:].lower() in miqtv.photo_types:
			if not miqtc.is_valid_uuid(retTmp[file]) or miqtc.is_valid_uuid(ret[file]):
				toRemove.append(file)
	for item in toRemove:
		del retTmp[item]
	ret = {**ret, **retTmp}
	## mkv
	retTmp = {}
	for file in os.listdir(path):
		if file.endswith(".mkv"):
			uuid,all = getVideoUUID(os.path.join(path,file))
			retTmp[file] = uuid
	ret = {**ret, **retTmp}
	return ret


def browseForImageFiles(path:str,extensions:list = miqtv.image_types,recursive=True,skipConfigFiles=True):
	""" Recursively scans a folder for media files (specified by the given file extension you are looking for).

	The result variable contains a dictionary with the found file paths as keys and
	a triple for each of those files with the file size, runtime and file extension:
	<name>:[<size>,<runtime>,<ext>]
	"""

	ret = {}
	s = miqtc.PrintLoadingMsg("Browsing for image files")
	files = miqtf.browseForFiles(path,extensions,recursive,skipConfigFiles)
	s.stop()
	videoFiles = []
	prog = miqtc.PrintKnownProgressMsg("Reading file stats ", len(files), modulo=10)
	for file in files:
		prog.progress()
		file_ext = file.split(".")[-1].lower()
		ret[file] = [os.stat(file).st_size,-1,file_ext]
		if file_ext in miqtv.video_types:
			videoFiles.append(file)
	prog.clear()

	prog = miqtc.PrintKnownProgressMsg("Reading video stats ", len(videoFiles), modulo=2)
	#start = time.time()
	getVideosRuntime_multiThread(videoFiles,ret,8,prog)
	#end = time.time()
	#print(f"Runtime of the program is {end - start}")
	prog.clear

	return ret


def getVideosRuntime_multiThread(files:list,ret:dict,nrThreads:int,prog=None):
	""" calls getVideoRuntime() in separate threads to speed up the process """
	
	if len(files) == 0:
		return

	if prog != None:
		prog.modulo = nrThreads

	if nrThreads > len(files):
		nrThreads = len(files)

	splitlen = int(len(files)/nrThreads)
	threads=[]
	for i in range(nrThreads):
		if i == nrThreads-1:
				filesSub = copy.deepcopy(files[i*splitlen::])
		else:
			filesSub = copy.deepcopy(files[i*splitlen:(i+1)*splitlen])
		
		retSub = {k:ret[k] for k in ret if k in filesSub}
		threads.append(threading.Thread(target=__getVideosRuntime, args=(filesSub,retSub,prog)))

	for thread in threads:
		thread.start()
	
	for thread in threads:
		thread.join()


def __getVideosRuntime(files:list,ret:dict,prog=None):
	if prog != None:
		for file in files:
			prog.progress()
			ret[file][1] = getVideoRuntime(file)
	else:
		for file in files:
			ret[file][1] = getVideoRuntime(file)


def browseFolderForImages(path:str,types:list = miqtv.image_types):
	raise Exception("DEPRECATED, use browseForImageFiles instead")
	
def createImageList(path:miqtd.Dir,overwrite=False,write_path:bool=False,img_types = miqtv.image_types):
	""" Creates a text file that contains one line per image file found in path

	Can overwrite an existing file list file if told so.
	Can add the full absolute path to the text file if told so (by providing the absolute path you want as the write_path variable)
	Can filter which images (or actually all file types) to put into the file. Default is all image types.
	"""

	if not path.exists():
		return False,"Path not found"

	# Potentially create output folder
	path.createTypeFolder(["intermediate"])

	# Check whether the full path shall be written
	if write_path == True:
		write_path = path
	else:
		write_path = ""

	# Scan the directory and write all files to the output file
	dst_path = path.tosensor()+"intermediate/"+path.event()+"_"+path.sensor()+"_images.lst"
	if not os.path.exists(dst_path) or overwrite:
		try:
			lst = open(dst_path,"w")
			files = os.listdir(path.tosensor()+"raw/")
			for file in files:
				if file[0] == ".":
					continue
				fn, fe = os.path.splitext(file)
				if fe[1:].lower() in img_types:
					lst.write(write_path+file+"\n")
			lst.close()
			return True,"Created output file."
		except:
			return False,"Could not create output file."
	else:
		return True,"Output file exists."


def allImageNamesValidIn(path:miqtd.Dir,sub:str = "raw"):
	""" Validates that all image file names are valid in the given folder."""

	img_paths = browseForImageFiles(path.tosensor()+"/"+sub+"/")
	return allImageNamesValid(img_paths)

def allImageNamesValid(img_paths:dict):
	invalidImageNames = []
	prog = miqtc.PrintKnownProgressMsg("Checking files have valid name", len(img_paths), modulo=10)
	for file in img_paths:
		prog.progress()
		file_name = os.path.basename(file)
		if not miqtt.isValidImageName(file_name):
			invalidImageNames.append(file)
	prog.clear()
	if len(invalidImageNames) != 0:
		return False,"Not all files have valid image names! Rename following files before continuing:\n-" + "\n- ".join(invalidImageNames)
	return True,"All filenames valid"


def computeImageScaling(area_file:str, data_path:str, dst_file:str, img_col:str = "Image number/name", area_col:str = "Image area", area_factor_to_one_square_meter:float = 1.0):
	""" Turns an ASCII file with image->area information into an ASCII file with image->scaling information

	Path to the source file is given, path to the result file can be given or is constructed from the convention
	"""

	miqtc.assertExists(area_file)

	area_data = miqtf.tabFileData(area_file,[img_col,area_col],key_col = img_col,graceful=True)

	o = open(dst_file,"w")
	o.write("image-filename\timage-pixel-per-millimeter\n")

	for img in area_data:

		with Image.open(data_path + img) as im:
			w,h = im.size

			scaling = math.sqrt(w*h / (float(area_data[img][area_col]) * area_factor_to_one_square_meter * 1000000))
			o.write(img + "\t" + str(scaling) + "\n")

def createImageItemsDictFromImageItemsList(items:list):
	""" Creates from a list of item dicts a dict of dicts with the 'image-filename' value becoming the respective dicts name """
	itemsDict = {}
	for item in items:
		# in case of video files there are list entries for different time stamps. Possibly also for the same time stamp, those are merged here
		if isinstance(item,list):

			for subItem in item:
				if 'image-filename' not in subItem:
					raise Exception("subitem",subItem,"does not contain a field 'image-filename'")
				tmp_itemsDict = {subItem['image-filename']:subItem}
				log = miqtc.recursivelyUpdateDicts(itemsDict, tmp_itemsDict, miqtv.ifdo_mutually_exclusive_fields)

		else:
			if 'image-filename' not in item:
				raise Exception("item",item,"does not contain a field 'image-filename'")
			tmp_itemsDict = {item['image-filename']:item}
			log = miqtc.recursivelyUpdateDicts(itemsDict, tmp_itemsDict, miqtv.ifdo_mutually_exclusive_fields)
	return itemsDict

def createImageItemsListFromImageItemsDict(items:dict):
	""" Creates from a dict of item dicts a list of dicts with the 'image-filename' value becoming an item field again """
	itemsList = []
	for item in items:
		if isinstance(items[item],list):
			itemDictList = []
			for v in items[item]:
				itemDict = copy.deepcopy(v)
				itemDict['image-filename'] = item
				itemDictList.append(itemDict)
			itemsList.append(itemDictList)
		else:
			itemDict = copy.deepcopy(items[item])
			itemDict['image-filename'] = item
			itemsList.append(itemDict)
	return itemsList

