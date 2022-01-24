import os
import mariqt.core
import mariqt.navigation

known_ofop_files = ["_posi.txt","_prot.txt","_obser.txt","_ROV.txt","_image_#1.bmp"]

def applyDataStructure(path):

	assertExists(path)
	path = validateDir(path)

	files = os.listdir(path)

	external = ["waypoint",".jpeg",".map",".jgw","button"]
	products = [".bmp"]

	create = ["raw","external","intermediate","processed","data_products"]
	for c in create:
		if not os.path.exists(path+c):
			os.mkdir(path+c,0o775)

	for file in files:
		file_lower = file.lower()
		if file.startswith("."):
			continue
		if file in create:
			continue
		target = "raw"
		for s in products:
			if s in file_lower:
				target = "data_products"
				break
		for s in external:
			if s in file_lower:
				target = "external"

		os.rename(path+file, path+"/"+target+"/"+file)


def findOFOPDataFiles(path):
	""" Find OFOP annotation files in a folder"""

	if not os.path.exists(path):
		return {}

	ofops = {}
	files = os.listdir(path)
	for file in files:
		if file.startswith('.'):
			continue
		for tmp in known_ofop_files:
			if tmp in file:
				ofop_name = file.replace(tmp,"")
				if ofop_name not in ofops:
					ofops[ofop_name] = []
				ofops[ofop_name].append(file)

	return ofops

def validOFOPDataFiles(ofop_name, ofop_file_list, base_path, position_only = False):

	unknown = []
	empty = []

	required_ofop = ["_posi.txt","_prot.txt","_obser.txt"]
	if position_only:
		required_ofop = ["_posi.txt"]

	for file in ofop_file_list:

		file_size = os.stat(base_path+file).st_size
		type = file.replace(ofop_name,"")

		if type not in known_ofop_files:
			unknown.append(file)
		else:
			if file_size == 0:
				empty.append(file)
			elif type in required_ofop:
				required_ofop.remove(type)

	if len(required_ofop) > 0:
		return False, "Required files are missing: " + ",".join(required_ofop)
	elif len(empty) > 0:
		return True, "Files are empty: " + ",".join(empty)
	return True, "Further files: " + ",".join(unknown)

def findValidPosiColumns(file_path):

	file = open(file_path,"r",errors="ignore")
	first = True

	columns = {}
	for line in file:
		if first:
			header_cols = line.split("\t")
			idx = 0
			for col in header_cols:
				columns[idx] = {'name':col,'index':idx,'min':False,'max':False}
				idx += 1
			first = False
		else:
			cols = line.split("\t")
			for idx in range(0,min(len(header_cols),len(cols))):
				if cols[idx] != "":
					try:
						val = float(cols[idx])
						if columns[idx]['min'] == False:
							columns[idx]['min'] = val
							columns[idx]['max'] = val
						else:
							columns[idx]['min'] = min(columns[idx]['min'],val)
							columns[idx]['max'] = max(columns[idx]['max'],val)
					except ValueError:
						continue

	ret_cols = []
	for idx in columns:
		if columns[idx]['min'] != False and columns[idx]['min'] != columns[idx]['max']:
			ret_cols.append(columns[idx]['name'])
	return ret_cols

	#max_col_idx,cis = acmw_hlp.getColumnIndicesFromFile(file,cols)

	#date_fmt = "%m/%d/%Y %H:%M:%S"
	#cis['utc'] = str(cis['date'])+";;;"+str(cis['time'])

	#Date	Time	PC_UTC	PC_Time	SHIP_Lon	SHIP_Lat	SHIP_SOG	SHIP_COG	SHIP_Hdg	Water_Depth	REF_Lon	REF_Lat	SHIP_Roll	SHIP_Pitch	SHIP_Heave	SUB1_Lon	SUB1_Lat	SUB1_Depth	SUB1_USBL_Depth	SUB1_Altitude	SUB1_COG	SUB1_Hdg	SUB1_Roll	SUB1_Pitch	SUB1_Camera_Pan	SUB1_Battery	SUB1_Magnetic_field_strength	SUB2_Lon	SUB2_Lat	SUB2_Depth	SUB2_USBL_Depth	SUB2_Altitude	SUB3_Lon	SUB3_Lat	SUB3_USBL_Depth	SUB4_Lon	SUB4_Lat	SUB4_USBL_Depth



def getOFOPAnnotations(file_path,type="obser",multi_row_replacements=[{'pre':'*','cur':'delete','rep':''}]):
	""" Loads all annotations from either an obser or prot file

	Type can be "obser" or "prot"
	Multi-row replacements handle subsequent annotations belonging to the same object:
	they are defined by mrr['pre'] = first label, mrr['cur'] = second label, mrr['rep'] = replacement of first label.
	The second annotation will be ignored and thus its label not returned!
	"""

	file = open(file_path,"r",errors="ignore",encoding="utf-8")

	if type == "prot":
		# Skip protocol header rows
		for line in file:
			if line[0:20] == "--------------------":
				break
		cols = {'date':'#Date','time':'Time','obs':'Image-Video Path'}
	elif type == 'obser':
		cols = {'date':'#Date','time':'Time','id':'ID_Number','name':'ID_Name'}
	else:
		die("Unknown OFOP annotation type: " + type)
	#print(file.readline())


	max_col_idx,cis = gmrcc.helper.getColumnIndicesFromFile(file,cols)

	date_fmt = "%m/%d/%Y %H:%M:%S"
	cis['utc'] = str(cis['date'])+";;;"+str(cis['time'])
	annotations = []
	prev_label = ""
	prev_timestamp = -1
	prev_double_row = False
	c = 0
	for line in file:

		try:
			row,timestamp = gmrcc.navprocessing.extractColumnsFromLine(line,cis,date_fmt)

			if type == "prot":
				tmp = row['obs'].split("]")
				label = tmp[1].strip()
				id = tmp[0][1:].strip()
			else:
				id = row['id']
				label = row['name'].replace(id,"").strip()
				id = id.replace("]","").replace("[","").strip()

			# Handles double-click annotations and deletes
			double_row = False
			for mrr in multi_row_replacements:
				if (mrr['pre'] == "*" or mrr['pre'] == prev_label) and (mrr['cur'] == "*" or mrr['cur'] == label):
					prev_label = mrr['rep']
					double_row = True

			if not prev_label == "" and not prev_timestamp < 0 and not prev_double_row:
				annotations.append([prev_timestamp,prev_label,prev_id])

			prev_label = label
			prev_timestamp = timestamp
			prev_double_row = double_row
			prev_id = id

		except Exception as e:
			#print(line,e)
			continue

	return annotations
