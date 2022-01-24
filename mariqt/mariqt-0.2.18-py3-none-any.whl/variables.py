""" A dictionary holding various header field names to store 4.5D navigation information in the form of: t (utc time), x (longitude), y (latitude), z (depth: below sea level), a (altitude: above seafloor)"""
from enum import Enum
import os

version = '0.2.6'

apis = {
		'osis_underway':'https://dm-apps-node0.geomar.de/osis-underway/api/v1/'
		}

pos_header = {
		# Field/column name definition for internally handling this kind of t,y,x,z,h position data
		"mariqt":{
			'utc':'utc',	# YYYY-MM-DD HH:ii:ss.sssss+0000 (UTC!!!) -> t-axis
			'lat':'lat',	# Decimal degrees, WGS84 / EPSG4362 -> y-axis
			'lon':'lon',	# Decimal degrees, WGS84 / EPSG4326 -> x-axis
			'dep':'dep',	# Depth of the signal, sample, platform, ... *in the water* -> z-axis, positive when submerged, negative when in air
			'hgt':'hgt',	# Height above the seafloor -> relative measure!
		},

		# Definition of field/column names according to the iFDO specification:
		# https://gitlab.hzdr.de/datahub/marehub/ag-videosimages/metadata-profiles-fdos/-/blob/master/MareHub_AGVI_iFDO.md
		"ifdo":{'utc':'image-datetime','lat':'image-latitude','lon':'image-longitude','dep':'image-depth','hgt':'image-meters-above-ground'},

		# Definition of field/column names according to the "Acquisition, Curation and Management Workflow"
		# for marine image data https://www.nature.com/articles/sdata2018181
		"acmw":{'utc':'SUB_datetime','lat':'SUB_latitude','lon':'SUB_longitude','dep':'SUB_depth','hgt':'SUB_distance'},

		# Definition of field/colum names as they occur in a DSHIP export file

		# for RV Sonne posidonia beacons
		"SO_NAV-2_USBL_Posidonia":{1:{'utc':'date time','lat':'USBL.PTSAG.1.Latitude','lon':'USBL.PTSAG.1.Longitude','dep':'USBL.PTSAG.1.Depth'},
									2:{'utc':'date time','lat':'USBL.PTSAG.2.Latitude','lon':'USBL.PTSAG.2.Longitude','dep':'USBL.PTSAG.2.Depth'},
									4:{'utc':'date time','lat':'USBL.PTSAG.4.Latitude','lon':'USBL.PTSAG.4.Longitude','dep':'USBL.PTSAG.4.Depth'},
									5:{'utc':'date time','lat':'USBL.PTSAG.5.Latitude','lon':'USBL.PTSAG.5.Longitude','dep':'USBL.PTSAG.5.Depth'}
		},

		# for RV Sonne itself (GPS)
		"SO_NAV-1_GPS_Saab":{'utc':'date time','lat':'SYS.STR.PosLat','lon':'SYS.STR.PosLon'},


		# for RV Maria S Merian sonardyne beacons
		"MSM_NAV-2_USBL_Sonardyne":{2104:{'utc':'date time','lat':'Ranger2.PSONLLD.2104.position_latitude','lon':'Ranger2.PSONLLD.2104.position_longitude','dep':'Ranger2.PSONLLD.2104.depth'},
									2105:{'utc':'date time','lat':'Ranger2.PSONLLD.2105.position_latitude','lon':'Ranger2.PSONLLD.2105.position_longitude','dep':'Ranger2.PSONLLD.2105.depth'}
		},

		# for RV Maria S Metian itself (GPS)
		"MSM_NAV-1_GPS_Debeg4100":{'utc':'date time','lat':'SYS.STR.PosLat','lon':'SYS.STR.PosLon'},

		# Definition of field/column names according to the DSM Workbench
		"workbench": {},

		# Definition of field/column names required for assigning EXIF infos to a JPG file
		"exif":{'utc':'CreateDate','lat':'GPSLatitude','lon':'GPSLongitude','dep':'GPSAltitude','hgt':'GPSDestDistance'},

		# Definition of field/column names according to the AWI O2A GeoCSV standard
		# https://confluence.digitalearth-hgf.de/display/DM/O2A+GeoCSV+Format
		# Warning: GeoCSVs need an additional WKT column: geometry [point] with values like: POINT(latitude longitude)
		# Warning: depth and altitude are guessed as i could not find it in the documentation
		"o2a":{'utc':'datetime','lat':'latitude [deg]','lon':'longitude [deg]','dep':'depth [m]','hgt':'altitude [m]'},

		# Definition of field/column names according to the OFOP software
		# Warning: OFOP requires two separate columns for date and time
		# Warning: Depth can also be in column SUB1_USBL_Depth
		# ---- USBL depth kommt vom USBL System, nur depth von einem (online/logging) Drucksensor, manchmal gibt es nur USBL.
		# Warning: It does not have to be SUB1 it can also be SUB2, SUB3, ...
		"ofop":{'utc':'Date\tTime','lat':'SUB1_Lat','lon':'SUB1_Lon','dep':'SUB1_Depth','hgt':'SUB1_Altitude'},

		# Definition of field/column names according to the world data center PANGAEA
		"pangaea":{
				'utc':'DATE/TIME',								# (1599)
				'lat':'LATITUDE',								# (1600)
				'lon':'LONGITUDE',								# (1601)
				'dep':'DEPTH, water [m]',						# (1619)
				'hgt':'Height above sea floor/altitude [m]'		# (27313)
				},

		# Definition of field/column names according to the annotation software BIIGLE
		"biigle":{'utc':'taken_at','lat':'lat','lon':'lng','dep':'gps_altitude','hgt':'distance_to_ground'}

}

att_header = {
	"mariqt":{
			'yaw':'yaw',		# in degrees
			'pitch':'pitch',	# in degrees
			'roll':'roll',		# in degrees
		},
}

navigation_equipment = {
	'SO':{'satellite':'SO_NAV-1_GPS_Saab','underwater':'SO_NAV-2_USBL_Posidonia'},
	'MSM':{'satellite':'','underwater':''}
}

date_formats = {"pangaea":"%Y-%m-%dT%H:%M:%S",
				"mariqt":"%Y-%m-%d %H:%M:%S.%f",
				"mariqt_files":"%Y%m%d_%H%M%S",
				"mariqt_short":"%Y-%m-%d %H:%M:%S",
				"gx_track":"%Y-%m-%dT%H:%M:%SZ",
				"dship":"%Y/%m/%d %H:%M:%S",
				"underway":"%Y-%m-%dT%H:%M:%S.%fZ"}

col_header = {	'pangaea':{'annotation_label':'Annotation label'},
				'mariqt':{	'uuid':'image-uuid',
							'img':'image-filename',
							'utc':'image-datetime',
							'lat':'image-latitude',
							'lon':'image-longitude',
							'dep':'image-depth',
							'hgt':'image-meters-above-ground',
							'alt':'image-altitude',
							'hash':'image-hash-sha256',
							'acqui':'image-acquisition-settings',
							'uncert':'image-coordinate-uncertainty-meters',
							'yaw':'image-camera-yaw-degrees',
							'pitch':'image-camera-pitch-degrees',
							'roll':'image-camera-roll-degrees',
							'pose':'image-camera-pose'
							},
				'exif':{	'img':'SourceFile',
							'uuid':'imageuniqueid'}
}

photo_types = ['jpg','png','bmp','raw','jpeg','tif']
video_types = ['mp4','mov','avi','mts','mkv','wmv']
image_types = photo_types + video_types

equipment_types = ['CAM','HYA','ENV','NAV','SAM','PFM']

colors = ['#94B242','#24589B','#DCB734','#E7753B','#A0BAAC','#CAD9A0','#82C9EB','#E9DCA6','#ED9A72','#D0DDD6','#EFF5E4','#E6F5FB','#F7F1DC','#F9DED2','#E8EEEB']
color_names = {'entity':'#94B242','process':'#24589B','infrastructure':'#DCB734','missing':'#ED9A72','error':'#E7753B','green':'#94B242','light_green':'#EFF5E4','blue':'#24589B','light_blue':'#E6F5FB','yellow':'#DCB734','light_yellow':'#F7F1DC','red':'#E7753B','light_red':'#F9DED2','grey':'#A0BAAC','light_grey':'#E8EEEB','mid_green':'#CAD9A0','mid_blue':'#82C9EB','mid_yellow':'#E9DCA6','mid_red':'#ED9A72','mid_grey':'#D0DDD6','dark_grey':'#6D7F77',}

class dataTypes(Enum): # default is string
	float = 0
	dict = 1
	text = 2 # just for gui elements to show bigger text field

image_set_header_key = 'image-set-header'
image_set_items_key =  'image-set-items'

req_person_fields = ['name','email','orcid']

ifdo_mutually_exclusive_fields = [['image-depth','image-altitude']]

ifdo_header_core_fields = {
	'image-set-name':{'comment':'A unique name for the image set, should include <project>, <event>, <sensor> and purpose','alt-fields':[]},
	'image-set-uuid':{'comment':'A UUID (version 4 - random) for the entire image set','alt-fields':['']},
	'image-set-handle':{'comment':'A Handle (using the UUID?) to point to the landing page of the data set','alt-fields':['']},
}

ifdo_item_core_fields = {
	'image-datetime':{'comment':'UTC: YYYY-MM-DD HH:MM:SS.SSSSS','alt-fields':[]},
	'image-latitude':{'comment':'Decimal degrees: D.DDDDDDD','alt-fields':[],'dataType':dataTypes.float},
	'image-longitude':{'comment':'Decimal degrees: D.DDDDDDD','alt-fields':[],'dataType':dataTypes.float},
	'image-depth':{'comment':'Use if camera below water, then it has positive values','alt-fields':['image-altitude'],'dataType':dataTypes.float},
	'image-altitude':{'comment':'Use if camera above water, then it has positive values. You may also use image-depth with negative values instead','alt-fields':['image-depth'],'dataType':dataTypes.float},
	'image-coordinate-reference-system':{'comment':'The coordinate reference system, e.g. EPSG:4326','alt-fields':[]},
	'image-coordinate-uncertainty-meters':{'comment':'Average/static uncertainty of coordinates in this dataset, given in meters','alt-fields':[],'dataType':dataTypes.float},
	'image-project':{'comment':'The lower-level / specific expedition or cruise or experiment or ...','alt-fields':[]},
	'image-context':{'comment':'The high-level "umbrella" project','alt-fields':[]},
	'image-event':{'comment':'One event of a project or expedition or cruise or experiment or ...','alt-fields':[]},
	'image-platform':{'comment':'Platform URN or Equipment Git ID or Handle URL','alt-fields':[]},
	'image-sensor':{'comment':'Sensor URN or Equipment Git ID or Handle URL','alt-fields':[]},
	'image-uuid':{'comment':'UUID (version 4 - random) for the image file (still or moving)','alt-fields':[]},
	'image-hash-sha256':{'comment':'An SHA256 hash to represent the whole file (including UUID in metadata!) to verify integrity on disk','alt-fields':[]},
	'image-pi':{'comment':'{orcid:..., name: ....} of principal investigator','alt-fields':[]},
	'image-creators':{'comment':'A list containing objects for all creators containing: {orcid:..., name:...}','alt-fields':[]},
	'image-license':{'comment':'License to use the data (should be FAIR, e.g. CC-BY or CC-0)','alt-fields':[]},
	'image-copyright':{'comment':'Copyright sentence / contact person or office','alt-fields':[],'dataType':dataTypes.text},
	'image-abstract':{'comment':'500 - 2000 characters describing what, when, where, why and how the data was collected. Includes general information on the event (aka station, experiment), e.g. overlap between images/frames, parameters on platform movement, aims, purpose of image capture etc.','alt-fields':[''],'dataType':dataTypes.text},
	'image-filename':{'comment':'A filename string to identify the image data on disk (no absolute path!)','alt-fields':[]},
}

ifdo_content_fields = {
	'image-entropy':{'comment':'1D time series constructed of single entropy values for each image / frame \n<image filename 1>:<entropy 1>\n<image filename 2>: <entropy 2>\n...'},
	'image-particle-count':{'comment':'1D time series constructed of single particle/object count values for each image / frame \n<image filename 1>: <particle count 1>\n<image filename 2>: <particle count 2>\n...'},
	'image-average-color':{'comment':'Set of n 1D time series constructed of the average colour for each image / frame and the n channels of an image (e.g. 3 for RGB)\n<image filename 1>:\n\t<channel 0>: <value>\n\t<channel 1>: <value>\n<image filename 2>:\n\t<channel 0>: <value>\n...'},
	'image-mpeg7-colorlayout':{'comment':'An nD feature vector per image / frame of varying dimensionality according to the chosen descriptor settings.'},
	'image-mpeg7-colorstatistic':{'comment':'An nD feature vector per image / frame of varying dimensionality according to the chosen descriptor settings.'},
	'image-mpeg7-colorstructure':{'comment':'An nD feature vector per image / frame of varying dimensionality according to the chosen descriptor settings.'},
	'image-mpeg7-dominantcolor':{'comment':'An nD feature vector per image / frame of varying dimensionality according to the chosen descriptor settings.'},
	'image-mpeg7-edgehistogram':{'comment':'An nD feature vector per image / frame of varying dimensionality according to the chosen descriptor settings.'},
	'image-mpeg7-homogeneoustexture':{'comment':'An nD feature vector per image / frame of varying dimensionality according to the chosen descriptor settings.'},
	'image-mpeg7-scalablecolor':{'comment':'An nD feature vector per image / frame of varying dimensionality according to the chosen descriptor settings.'},
	'image-annotations':{'comment':'This field is mighty powerful! It takes a list of objects of 3-4 fields ([{coordinates: [[p1.x,p1.y,p2.x,p2.y,...],...], frames: [f1,...], labels: [{label: <LID>, annotator: <ORCID/UUID>,confidence: <float>},...]}). The number of given coordinates specifies which kind of shape the annotation takes (the ROI in the image, the selected pixels). If there are no coordinates, then the annotation is for the entire image. Two coordinates specify a single pixel / point: [p.x,p.y]. Three coordinates need to be given for a circle: [p.x,p.y,r]. A longer list of points is given for a polyline: [p1.x,p1.y,p2.x,p2.y,...,pn.x,pn.y]. In case the first and last position are the same, then a polygon is specified. The coordinates field is a list of lists in case an annotation geometry changes over time over several video frames. In case an annotation is for one frame (or an image) only, it may also be a single list. The optional "frames" field of the annotation specifies the start and end frame between which an annotation exists. The list of labels specifies the ids or names of objects and annotators and their confidence. It might be a good choice to add a image-annotation-labels and image-annotation-creators field in the iFDO header to provide more information on the values represented here. Confidence in one user\'s annotations can be given as a float between 0 and 1 here or in the image-set-annotators header field.','dataType':dataTypes.dict},
	'image-annotation-labels':{'comment':'[{id:<LID>,name:String,info:<description>,type:},...]'},
	'image-annotation-label-types':{'comment':'List of up to four allowed values (operation, geology, biology, garbage) to characterize annotation labels in this image set at the highest abstraction level'},
	'image-annotation-creators':{'comment':'[{id:<ORCUD/UUID>,name:String,type:String (crowd-sourced, non-expert, expert, AI)},...]'},
	'image-annotation-geometry-types':{'comment':'List of up to four allowed values (whole-image, single-pixel, polygon, bounding-box) to characterize annotation geometries in this image set at the highest abstraction level'},
}

ifdo_capture_fields = {
	'image-acquisition':{'comment':'photo: still images, video: moving images, slide: microscopy / slide scans','valid':['photo','video','slide']},
	'image-quality':{'comment':'raw: straight from the sensor, processed: QA/QCd, product: image data ready for interpretation','valid':['raw', 'processed', 'product']},
	'image-deployment':{'comment':'mapping: planned path execution along 2-3 spatial axes, stationary: fixed spatial position, survey: planned path execution along free path, exploration: unplanned path execution, experiment: observation of manipulated environment, sampling: ex-situ imaging of samples taken by other method','valid':['mapping', 'stationary', 'survey', 'exploration', 'experiment', 'sampling']},
	'image-navigation':{'comment':'satellite: GPS/Galileo etc., beacon: USBL etc., transponder: LBL etc., reconstructed: position estimated from other measures like cable length and course over ground','valid':['satellite', 'beacon', 'transponder', 'reconstructed']},
	'image-scale-reference':{'comment':'3D camera: the imaging system provides scale directly, calibrated camera: image data and additional external data like object distance provide scale together, laser marker: scale information is embedded in the visual data, optical flow: scale is computed from the relative movement of the images and the camera navigation data','valid':['3D camera', 'calibrated camera', 'laser marker', 'optical flow']},
	'image-illumination':{'comment':'sunlight: the scene is only illuminated by the sun, artificial light: the scene is only illuminated by artificial light, mixed light: both sunlight and artificial light illuminate the scene','valid':['sunlight', 'artificial light', 'mixed light']},
	'image-resolution':{'comment':'average size of one pixel of an image','valid':['km', 'hm', 'dam', 'm', 'cm', 'mm', 'µm']},
	'image-marine-zone':{'comment':'seafloor: images taken in/on/right above the seafloor, water column: images taken in the free water without the seafloor or the sea surface in sight, sea surface: images taken right below the sea surface, atmosphere: images taken outside of the water, laboratory: images taken ex-situ','valid':['seafloor', 'water column', 'sea surface', 'atmosphere', 'laboratory']},
	'image-spectral-resolution':{'comment':'grayscale: single channel imagery, rgb: three channel imagery, multi-spectral: 4-10 channel imagery, hyper-spectral: 10+ channel imagery','valid':['grayscale', 'rgb', 'multi-spectral', 'hyper-spectral']},
	'image-capture-mode':{'comment':'whether the time points of image capture were systematic, human-triggered or both','valid':['timer','manual','mixed']},
	
	'image-area-square-meter':{'comment':'The footprint of the entire image in square meters','dataType':dataTypes.float},
	'image-pixel-per-millimeter':{'comment':'Resolution of the imagery in pixels / square millimeter which is numerically identical to megapixel / square meter','dataType':dataTypes.float},
	'image-meters-above-ground':{'comment':'Distance of the camera to the seafloor in meters','dataType':dataTypes.float},
	'image-acquisition-settings':{'comment':'All the information that is recorded by the camera in the EXIF, IPTC etc. As a dict. Includes ISO, aperture, etc.','dataType':dataTypes.dict},
	'image-camera-yaw-degrees':{'comment':'Camera view yaw angle.     Rotation of camera coordinates (x,y,z = top, right, line of sight) with respect to NED coordinates (x,y,z = north,east,down) in accordance with the yaw,pitch,roll rotation order convention:\n1. yaw around z,\n2. pitch around rotated y,\n3. roll around rotated x\nRotation directions according to \'right-hand rule\'. I.e. for yaw,pitch,roll = 0,0,0 camera is facing downward with top side towards north','dataType':dataTypes.float},
	'image-camera-pitch-degrees':{'comment':'Camera view pitch angle. Rotation of camera coordinates (x,y,z = top, right, line of sight) with respect to NED coordinates (x,y,z = north,east,down) in accordance with the yaw,pitch,roll rotation order convention:\n1. yaw around z,\n2. pitch around rotated y,\n3. roll around rotated x\nRotation directions according to \'right-hand rule\'. I.e. for yaw,pitch,roll = 0,0,0 camera is facing downward with top side towards north','dataType':dataTypes.float},
	'image-camera-roll-degrees':{'comment':'Camera view roll angle.   Rotation of camera coordinates (x,y,z = top, right, line of sight) with respect to NED coordinates (x,y,z = north,east,down) in accordance with the yaw,pitch,roll rotation order convention:\n1. yaw around z,\n2. pitch around rotated y,\n3. roll around rotated x\nRotation directions according to \'right-hand rule\'. I.e. for yaw,pitch,roll = 0,0,0 camera is facing downward with top side towards north','dataType':dataTypes.float},
	'image-overlap-fraction':{'comment':'The average overlap of two consecutive images i and j as the area images in both of the images (A_i * A_j) divided by the total area images by the two images (A_i + A_j - A_i * A_j): f = A_i * A_j / (A_i + A_j - A_i * A_j) -> 0 if no overlap. 1 if complete overlap','dataType':dataTypes.float},

	'image-camera-pose':{'comment':'{pose-utm-zone: int, pose-utm-epsg: int, pose-utm-east-north-up-meters: [double,double,double], pose-absolute-orientation-utm-matrix: 3x3 row-major float rotation matrix that transforms a direction in camera coordinates (x,y,z = right, down, line of sight) into a direction in UTM coordinates (x,y,z = easting,northing,up)}','dataType':dataTypes.dict},
	'image-camera-housing-viewport':{'comment':'{viewport-type: string (e.g.: flatport, domeport, other), viewport-optical-density: float (unit-less, 1.0=vacuum),   viewport-thickness-millimeter: float, viewport-extra-description: text}','dataType':dataTypes.dict},
	'image-flatport-parameters':{'comment':'{flatport-lens-port-distance-millimeter: float, flatport-interface-normal-direction: [float, float, float] (unit-less (0,0,1) is "aligned"), flatport-extra-description: text}','dataType':dataTypes.dict},
	'image-domeport-parameters':{'comment':'{domeport-outer-radius-millimeter: float, domeport-decentering-offset-xyz-millimeter: [float,float,float],domeport-extra-description: text}','dataType':dataTypes.dict},
	'image-camera-calibration-model':{'comment':'{calibration-model-type: string (e.g.: rectilinear air, rectilinear water, fisheye air, fisheye water, other), calibration-model-extra-description: text (explain model, or if lens parameters are in mm rather than in pixel), calibration-focal-length-xy-pixel: [float, float], calibration-principal-point-xy-pixel: [float,float] (top left pixel center is 0,0, x right, y down), calibration-distortion-coefficients: [float,float,float, float, float, float, float,float] (rectilinear: k1, k2, p1, p2, k3, k4, k5, k6, fisheye: k1, k2, k3, k4),calibration-approximate-field-of-view-water-xy-degree: [float, float] (proxy for pixel to meter conversion, and as backup)}','dataType':dataTypes.dict},
	'image-photometric-calibration':{'comment':'{photometric-sequence-white-balancing: text, photometric-exposure-factor-RGB-float: [float, float, float] (RGB factors applied to this image, product of ISO, exposure time, relative white balance), photometric-sequence-illumination-type: String (e.g. "constant artificial", "globally adapted artificial", "individually varying light sources", "sunlight", "mixed"), photometric-sequence-illumination-description: text,   photometric-illumination-factor-RGB-float: [float, float, float] (RGB factors applied to artificial lights for this image), photometric-water-properties-description: text }','dataType':dataTypes.dict},
	'image-objective':{'comment':'A general translation of the aims and objectives of the study, as they pertain to biology and method scope. This should define the primary and secondary data to be measured and to what precision.','dataType':dataTypes.text},
	'image-target-environment':{'comment':'A description, delineation, and definition of the habitat or environment of study, including boundaries of such','dataType':dataTypes.text},
	'image-target-timescale':{'comment':'A description, delineation, and definition of the period, interval or temporal environment of the study.','dataType':dataTypes.text},
	'image-spatial-contraints':{'comment':'A description / definition of the spatial extent of the study area (inside which the photographs were captured), including boundaries and reasons for constraints (e.g. scientific, practical)','dataType':dataTypes.text},
	'image-temporal-constraints':{'comment':'A description / definition of the temporal extent, including boundaries and reasons for constraints (e.g. scientific, practical)','dataType':dataTypes.text},
	'image-fauna-attraction':{'comment':'','valid':['none','baited','light']},
	'image-time-synchronisation':{'comment':'Synchronisation procedure and determined time offsets between camera recording values and UTC','dataType':dataTypes.text},
	'image-item-identification-scheme':{'comment':'How the images file names are constructed. Should be like this `<project>_<event>_<sensor>_<date>_<time>.<ext>`','dataType':dataTypes.text},
	'image-curation-protocol':{'comment':'A description of the image and metadata curation steps and results','dataType':dataTypes.text},
}

ifdo_coreFields = {**ifdo_header_core_fields, **ifdo_item_core_fields}
ifdo_fields =  {**ifdo_coreFields, **ifdo_content_fields, **ifdo_capture_fields}



# icons for iFDO creation wizard notebook to retrieve them centrally from pip package
myPath = os.path.dirname(__file__)
icon_check = open(myPath + "/for_notebooks/icons/checkbox-circle-line_green.png", "rb").read()
icon_checkDisabled = open(myPath + "/for_notebooks/icons/checkbox-circle-line_gray.png", "rb").read()
icon_error = open(myPath + "/for_notebooks/icons/error-warning-line_red.png", "rb").read()
icon_errorDisabled = open(myPath + "/for_notebooks/icons/error-warning-line_gray.png", "rb").read()
icon_warning = open(myPath + "/for_notebooks/icons/error-warning-line_orange.png", "rb").read()