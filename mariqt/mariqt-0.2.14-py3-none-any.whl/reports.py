""" This files contains various functions to create HTML reports about data"""

import math
import datetime
import mariqt.geo as miqtg
import mariqt.core as miqtc
import mariqt.variables as miqtv
import mariqt.provenance as miqtp
import mariqt.navigation as miqtn
import mariqt.sources.svgs as miqtss

cols = miqtv.color_names

def createReport(name:str,path:str,sections:dict):
	""" Creates the entire report HTML and stores it at path"""

	# Create blank HTML page
	html = '<!doctype html><html lang="en"><head><meta charset="utf-8"><title>'+name+'</title>'
	html += '<meta name="description" content="An automatically generated report"><style>'
	html += 'body {background-color:#fff; font-family: monospace;}'
	html += '.content {max-width: 960px; margin: auto; position: relative;}'
	html += '.box { border-radius: 5px; border: 1px solid; padding:10px; position: relative}'
	html += '.title { font-size: 12pt; font-weight: bold; margin-top: 30px; margin-bottom: 10px}'
	html += '.footer { text-align: center; font-size: 10pt; font-weight: normal; color: '+cols['grey']+'; margin-top: 30px; margin-bottom: 10px}'
	html += '.box_title { position: relative; left: 965px; top: 21px}'
	html += '.tab_right { text-align: right; width: 240px;}'
	html += '.tab_key { width: 240px; text-align: right; vertical-align: top; }'
	html += '.tab_val { width: 650px; font-weight: bold }'
	html += '.tab_wide { padding:0 15px; }'
	html += '</style></head><body><div class="content">'
	html += '<div class="title">'+name+'<hr style="height:1px;border-width:0;color:#000;background-color:#000"></div>'

	if 'event' in sections:
		html += createEventReportSection(sections['event'])
	if 'dship' in sections:
		html += createDSHIPEventReportSection(sections['dship'])
	if 'ifdo' in sections:
		html += createiFDOReportSection(sections['ifdo'])
	if 'positions' in sections:
		html += createPositionsReportSection(sections['positions'])
	if 'project' in sections:
		html += createProjectReportSection(sections['project'])
	if 'provenance' in sections:
		html += createProvenanceReportSection(sections['provenance'])

	# Add the closing tags for the HTML page
	dt = datetime.datetime.now(tz=datetime.timezone.utc)
	html += '<div class="footer"><hr style="height:1px;border-width:0;color:'+cols['grey']+';background-color:'+cols['grey']+'">'
	html += 'This report was generated automatically by the MareHub <i>mariqt</i> python package - powered by GEOMAR!<br> '+dt.strftime(miqtv.date_formats['mariqt_short'])+' (UTC)</div>'
	html += "</div></body></html>"

	# Write everything to disk
	with open(path,"w",encoding="utf-8") as file:
		file.write(html)


def createProjectReportSection(project:dict):
	html = '<div class="box_title" style="color:'+cols['dark_grey']+'">Project info</div>'
	html += '<div class="box" style="border-color:'+cols['grey']+';color:'+cols['dark_grey']+';background-color:'+cols['light_grey']+'"><table>'
	html += '<tr><td class="tab_key">Project number:</td><td class="tab_val">'+project['number']+'</td></tr>'
	html += '<tr><td class="tab_key">Project title:</td><td class="tab_val">'+project['title']+'</td></tr>'
	html += '<tr><td class="tab_key">Project PI:</td><td class="tab_val">'+project['pi']['name']+' ('+project['pi']['email']+') - <a href="https:orgid.orc/'+project['pi']['orcid']+'">'+project['pi']['orcid']+'</a></td></tr>'
	html += '<tr><td class="tab_key">Data PI:</td><td class="tab_val">'+project['data-pi']['name']+' ('+project['data-pi']['email']+') - <a href="https:orgid.orc/'+project['data-pi']['orcid']+'">'+project['data-pi']['orcid']+'</a></td></tr>'
	html += '<tr><td class="tab_key">Copyright:</td><td class="tab_val">'+project['copyright']+'</td></tr>'
	html += '<tr><td class="tab_key">License:</td><td class="tab_val">'+project['license']+'</td></tr>'
	html += '</table></div>'
	return html

def createEventReportSection(event:dict):
	html = '<div class="box_title" style="color:'+cols['blue']+'">Event info</div>'
	html += '<div class="box" style="border-color:'+cols['mid_blue']+';color:'+cols['blue']+';background-color:'+cols['light_blue']+'"><table>'
	html += '<tr><td class="tab_key">Event name:</td><td class="tab_val">'+event['name']+'</td></tr>'
	html += '<tr><td class="tab_key">Equipment:</td><td class="tab_val">'+event['equipment']+'</td></tr>'
	html += '<tr><td class="tab_key">Start:</td><td class="tab_val">'+event['start']+' (UTC)</td></tr>'
	html += '<tr><td class="tab_key">End:</td><td class="tab_val">'+event['end']+' (UTC)</td></tr>'
	html += '</table></div>'
	return html


def createDSHIPEventReportSection(dship:dict):
	html = '<div class="box_title" style="color:'+cols['blue']+'">DSHIP info</div>'
	html += '<div class="box" style="border-color:'+cols['mid_blue']+';color:'+cols['blue']+';background-color:'+cols['light_blue']+'"><table>'
	if 'code' in dship:
		html += '<tr><td class="tab_key">Code:</td><td class="tab_val">'+dship['code']+'</td></tr>'
	if 'start' in dship:
		dt = datetime.datetime.fromtimestamp(dship['start'],tz=datetime.timezone.utc)
		html += '<tr><td class="tab_key">Start:</td><td class="tab_val">'+dt.strftime(miqtv.date_formats['mariqt_short'])+'</td></tr>'
	if 'end' in dship:
		dt = datetime.datetime.fromtimestamp(dship['end'],tz=datetime.timezone.utc)
		html += '<tr><td class="tab_key">End:</td><td class="tab_val">'+dt.strftime(miqtv.date_formats['mariqt_short'])+'</td></tr>'
	if 'actions' in dship:
		html += '<tr><td class="tab_key">Actions:</td><td class="tab_val"><table style="border-collapse:collapse"><tr><td>UTC</td><td class="tab_wide">Action</td><td class="tab_wide">Latitude</td><td class="tab_wide">Longitude</td><td class="tab_wide">Depth</td></tr>'
		for act in dship['actions']:
			dt = datetime.datetime.fromtimestamp(act['utc'],tz=datetime.timezone.utc)
			html += '<tr><td>'+dt.strftime(miqtv.date_formats['mariqt_short'])+'</td><td class="tab_wide">'+act['action']+'</td><td class="tab_wide">'+str(round(act['lat'],7))+'</td><td class="tab_wide">'+str(round(act['lon'],7))+'</td><td class="tab_wide">'
			if 'dep' in act:
				html += str(round(act['dep'],2))+'</td></tr>'
			else:
				html += '</td></tr>'
		html += '</table></td></tr>'
	html += '</table></div>'
	return html


def createiFDOReportSection(ifdo:dict):

	html = '<div class="box_title" style="color:'+cols['green']+'">iFDO badges</div>'
	html += '<div class="box" style="border-color:'+cols['mid_green']+';color:'+cols['green']+';background-color:'+cols['light_green']+'">'

	# Which fields to turn into an SVG
	svgs = ['image-acquisition','image-spectral-resolution','image-marine-zone','image-resolution','image-navigation','image-scale-reference','image-illumination','image-deployment','image-quality','image-license']

	# Which fields to turn into a plot
	plot = ['image-depth','image-meters-above-ground','image-entropy','image-area-square-meter','image-average-color','image-particle-count']



	# Plot svg icons
	for svg in svgs:
		if svg in ifdo['image-set-header']:
			val = ifdo['image-set-header'][svg]
			if val in miqtss.ifdo_svgs[svg]:
				html += miqtss.ifdo_svgs[svg][val].replace('enable-background:new 0 0 85 85;','enable-background:new 0 0 85 85;width:87px;height:87px;background-color:#fff;border:'+cols['green']+' solid 1px;margin:2px;')
	html += '</div>'


	# Plot header values, first the core ones, then all other
	html += '<div class="box_title" style="color:'+cols['green']+'">iFDO header</div>'
	html += '<div class="box" style="border-color:'+cols['mid_green']+';color:'+cols['green']+';background-color:'+cols['light_green']+'">'
	html += '<table>'
	for hed in miqtv.ifdo_header_core_fields:
		if hed in ifdo['image-set-header']:
			#html += '<tr><td class="tab_key">'+hed.replace('image-set-','')+'</td><td class="tab_val">'+str(ifdo['image-set-header'][hed])+'</td></tr>'
			html += '<tr><td class="tab_key">'+hed.replace('image','')+'</td><td class="tab_val">'+str(ifdo['image-set-header'][hed])+'</td></tr>' # TODO remove '-set-' from header fields, Test
	for hed in ifdo['image-set-header']:
		if hed not in svgs and hed not in plot and hed not in miqtv.ifdo_header_core_fields:
			#html += '<tr><td class="tab_key">'+hed.replace('image-set-','')+'</td><td class="tab_val">'+str(ifdo['image-set-header'][hed])+'</td></tr>'
			html += '<tr><td class="tab_key">'+hed.replace('image','')+'</td><td class="tab_val">'+str(ifdo['image-set-header'][hed])+'</td></tr>' # TODO remove '-set-' from header fields, Test
	html += '</table>'
	html += '</div>'


	html += '<div class="box_title" style="color:'+cols['green']+'">iFDO item plots</div>'
	html += '<div class="box" style="border-color:'+cols['mid_green']+';color:'+cols['green']+';background-color:'+cols['light_green']+'">'

	# TODO Plot preview values: depth, height, entropy, area, image-average-color, image-particle-count
	values = {}
	img_coordinates_cur = miqtg.Positions()
	for key in plot:
		values[key] = {}
	min_utc = 100000000000000
	max_utc = 0
	for img in ifdo['image-set-items']:

		# Get UTC timestamp
		utc = int(datetime.datetime.strptime(ifdo['image-set-items'][img]['image-datetime'],miqtv.date_formats['mariqt']).timestamp())
		max_utc = max(max_utc,utc)
		min_utc = min(min_utc,utc)

		# Add item coordinate for plotting a map
		img_coordinates_cur.setVals(utc,ifdo['image-set-items'][img]['image-latitude'],ifdo['image-set-items'][img]['image-longitude'])

		for key in plot:
			if key in ifdo['image-set-items'][img]:
				if key == 'image-average-color':
					values[key][utc] = eval(ifdo['image-set-items'][img][key])
				else:
					if key == 'image-depth':
						values[key][utc] = -float(ifdo['image-set-items'][img][key])
					else:
						values[key][utc] = float(ifdo['image-set-items'][img][key])


	for key in plot:
		if len(values[key]) == 0:
			continue
		if key == 'image-average-color':
			# TODO Plot average colours
			cvs = createDataCanvas(940,100,True,key,"","",min_utc,max_utc)

			html += cvs[0]

			for utc in values[key]:
				rgb = miqtc.rgb2hex(int(values[key][utc][0]),int(values[key][utc][1]),int(values[key][utc][2]))
				x = round((utc - min_utc) / (max_utc - min_utc) * 940)
				html += '<div style="position:absolute;width:1px;height:'+str(100)+'px;left:'+str(x)+'px;top:0px;background-color:'+rgb+'"></div>'
			html += cvs[1]

		else:

			html += createDataPlot(key,values[key],min_utc,max_utc)

	# TODO Plot clustering of images based on features?

	html += '</div>'

	# Plot coordinates from iFDO items
	pos = {'title':'Image capture positions of '+ifdo['image-set-header']['image-event']+" "+ifdo['image-set-header']['image-sensor'],'positions':[{'name':'Curated image coordinates','data':img_coordinates_cur,'color':miqtv.color_names['green']}]}
	html += createPositionsReportSection(pos)

	return html


def createDataCanvas(canvas_width,canvas_height,with_decoration,title,min_y,max_y,min_x,max_x):

	html = '<div style="position:relative;margin-top:20px;width:'+str(canvas_width)+'px;height:'+str(canvas_height)+'px">'

	if title == "image-depth":
		min_y = -min_y
		max_y = -max_y

	if not title == "image-average-color":
		min_y_str = str(round(min_y,2))
		max_y_str = str(round(max_y,2))
	else:
		min_y_str = ""
		max_y_str = ""

	dec_space = 0
	if with_decoration:

		dec_space = 20

		# Add GEOMAR logo
		html += miqtss.geomar_logo.replace('top:2px;','bottom:2px;')

		min_utc = datetime.datetime.fromtimestamp(min_x).strftime(miqtv.date_formats['mariqt_short'])
		max_utc = datetime.datetime.fromtimestamp(max_x).strftime(miqtv.date_formats['mariqt_short'])

		# Add axis descriptions (min/max lat/lon)
		html += '<div style="color:#000;font-family:monospace;position:absolute;left:0px;bottom:10px;transform: rotate(-90deg);transform-origin: left top">'+min_y_str+'</div>'
		html += '<div style="color:#000;font-family:monospace;position:absolute;left:0px;top:0px;transform:rotate(-90deg);transform-origin: right top;translate:-100%">'+max_y_str+'</div>'
		html += '<div style="color:#000;font-family:monospace;position:absolute;left:'+str(dec_space+2)+'px;bottom:0px;">'+str(min_utc)+'</div>'
		html += '<div style="color:#000;font-family:monospace;position:absolute;right:2px;bottom:0px;">'+str(max_utc)+'</div>'


	# Add title
	html += '<div style="width:'+str(canvas_width-dec_space)+'px;text-align:center;position:absolute;left:'+str(dec_space)+'px;bottom:0px;">'
	html += '<div style="color:#000;margin: 0 auto;">'+title+'</div></div>'

	html += '<div style="border:solid 1px #000;background-color:#fff;position:absolute;overflow:hidden;width:'+str(canvas_width-dec_space-2)+'px;height:'+str(canvas_height-dec_space-2)+'px;left:'+str(dec_space)+'px;bottom:'+str(dec_space)+'px">'
	return html,'</div></div>'


def createDataPlot(title,values,min_x,max_x):

	plot_w = 940
	plot_h = 200

	# Compute min max values an drop the top/bottom one percent of the values to omit outliers
	vals = []
	for v in values:
		vals.append(values[v])
	vals.sort()
	pos = round(len(vals) / 1000)
	min_v = vals[pos]
	max_v = vals[len(vals)-pos-1]

	med_v = vals[round(0.5*len(vals))]

	canvas = createDataCanvas(plot_w,plot_h,True,title,min_v,max_v,min_x,max_x)
	html = canvas[0]

	for v in values:

		x = round((v - min_x) / (max_x - min_x) * plot_w)
		y = round((values[v] - min_v) / (max_v - min_v) * plot_h)
		if x >= 0 and x < plot_w and y >= 0 and y < plot_h:
			html += '<div style="position:absolute;left:'+str(x)+'px;bottom:'+str(y)+'px;width:1px;height:1px;background-color:#000"></div>'

	# Add median line
	y = round((med_v - min_v) / (max_v - min_v) * plot_h)
	html += '<div style="position:absolute;left:0px;bottom:'+str(y)+'px;width:'+str(plot_w)+'px;height:1px;background-color:'+cols['green']+'"></div>'
	html += '<div style="position:absolute;right:2px;bottom:'+str(y+5)+'px;color:'+cols['green']+'">'+str(round(med_v,2))+' (median)</div>'

	return html+canvas[1]


def plotData(positions:miqtg.Positions,canvas_width,canvas_height,min_lat,max_lat,min_lon,max_lon,icon_color:str = '#000',icon:str = ''):

	time_points = list(positions.keys())

	if icon == '':
		icon = 'width:1px;height:1px'

	ret = ""
	for utc in time_points:

		x = round((positions[utc].lon - min_lon) / (max_lon - min_lon) * canvas_width)
		y = round((positions[utc].lat - min_lat) / (max_lat - min_lat) * canvas_height)

		if x >= 0 and x < canvas_width and y >= 0 and y < canvas_height:
			ret += '<div style="position:absolute;left:'+str(x)+'px;bottom:'+str(y)+'px;'+icon+';background-color:'+icon_color+'"></div>'

	return ret

def createPositionsReportSection(positions:dict):

	# How large the entire plot shall be including decorations, excluding the legend
	plot_w = 940
	plot_h = 500

	# With positions / scalebar
	with_decoration = True

	if with_decoration:
		cvs_w = plot_w - 20
		cvs_h = plot_h - 20
	else:
		cvs_w = plot_w
		cvs_h = plot_h

	# Get min max extent of all position sets
	all_min_lat = 360
	all_min_lon = 360
	all_max_lat = -360
	all_max_lon = -360
	for pos_set in positions['positions']:
		tmp = miqtn.getMinMaxLatLon(pos_set['data'],outlier_percent = 1)
		all_min_lat = min(all_min_lat,tmp[0])
		all_max_lat = max(all_max_lat,tmp[1])
		all_min_lon = min(all_min_lon,tmp[2])
		all_max_lon = max(all_max_lon,tmp[3])

	# Compute relative extents of x and y axis
	frac_lon = cvs_w / (all_max_lon - all_min_lon) # px/°
	frac_lat = cvs_h / (all_max_lat - all_min_lat) # px/°

	frac = min(frac_lon,frac_lat) # px/°

	used_lat = frac*(all_max_lat - all_min_lat) # px
	used_lon = frac*(all_max_lon - all_min_lon) # px

	offset_deg_lat = 0.5 * (cvs_h-used_lat) / frac
	offset_deg_lon = 0.5 * (cvs_w-used_lon) / frac

	all_min_lat -= offset_deg_lat
	all_max_lat += offset_deg_lat

	all_min_lon -= offset_deg_lon
	all_max_lon += offset_deg_lon

	lat_buf = 0.02 * (all_max_lat - all_min_lat)
	lon_buf = 0.02 * (all_max_lon - all_min_lon)
	all_min_lat -= lat_buf
	all_max_lat += lat_buf
	all_min_lon -= lon_buf
	all_max_lon += lon_buf

	html = '<div class="box_title" style="color:'+cols['green']+'">Position info</div>'
	html += '<div class="box" style="border-color:'+cols['mid_green']+';color:'+cols['green']+';background-color:'+cols['light_green']+'">'

	canvas = createMapCanvas(plot_w,plot_h,with_decoration,'<strong>'+positions['title']+'</strong>',all_min_lat,all_max_lat,all_min_lon,all_max_lon)
	html += canvas[0]

	for pos_set in positions['positions']:
		col = '#000'
		if 'color' in pos_set:
			col = pos_set['color']

		icon = ''
		if 'icon' in pos_set:
			icon = pos_set['icon']

		html += plotNavigationData(pos_set['data'],cvs_w,cvs_h,all_min_lat,all_max_lat,all_min_lon,all_max_lon,col,icon)

	legend = []
	for pos_set in positions['positions']:
		col = '#000'
		if 'color' in pos_set:
			col = pos_set['color']
		legend.append('<div><div style="height:11px;width:11px;background-color:'+col+';display:inline-block"></div><div style="display:inline-block;margin-left:2px">' + pos_set['name']+'</div></div>')
	legend = createLegend(legend,plot_w)
	html += canvas[1]+legend+'</div>'
	return html


def createMapCanvas(canvas_width,canvas_height,with_decoration,title,all_min_lat,all_max_lat,all_min_lon,all_max_lon):

	html = '<div style="position:relative;width:'+str(canvas_width)+'px;height:'+str(canvas_height)+'px">'

	dec_space = 0
	if with_decoration:

		dec_space = 20

		# Add GEOMAR logo
		html += miqtss.geomar_logo

		# Add axis descriptions (min/max lat/lon)
		html += '<div style="color:#000;font-family:monospace;position:absolute;left:0px;bottom:-15px;transform: rotate(-90deg);transform-origin: left top">'+miqtg.decdeg2decmin(all_min_lat,'lat')+'</div>'
		html += '<div style="color:#000;font-family:monospace;position:absolute;left:0px;top:105px;transform:rotate(-90deg);transform-origin: left top">'+miqtg.decdeg2decmin(all_max_lat,'lat')+'</div>'
		html += '<div style="color:#000;font-family:monospace;position:absolute;left:'+str(dec_space+2)+'px;top:0px;">'+miqtg.decdeg2decmin(all_min_lon,'lon')+'</div>'
		html += '<div style="color:#000;font-family:monospace;position:absolute;right:2px;top:0px;">'+miqtg.decdeg2decmin(all_max_lon,'lon')+'</div>'

		# Add scalebar
		width_m = miqtg.distanceLatLon(all_min_lat,all_min_lon,all_max_lat,all_min_lon)
		bar_width_m = 0.5 * width_m

		# Make the bar width a nice flat number
		fac = 1
		while bar_width_m > 10:
			bar_width_m /= 10
			fac *= 10
		bar_width_m = math.floor(bar_width_m) * fac

		# Compute the bar length in pixel
		bar_width_px = round(bar_width_m / width_m * canvas_height) # m / m * px

		html += '<div style="position:absolute;left:0px;top:'+str(0.5*(canvas_height-dec_space-bar_width_px)+bar_width_px+dec_space)+'px;width:'+str(bar_width_px)+'px;height:15px;background-color:#000;color:#fff;text-align:center;vertical-align:middle;font-size:10px;transform:rotate(-90deg);transform-origin:left top;">'
		html += miqtc.humanReadable(bar_width_m)+'m</div>'

	# Add title
	html += '<div style="width:'+str(canvas_width-dec_space)+'px;text-align:center;position:absolute;left:'+str(dec_space)+'px">'
	html += '<div style="color:#000;margin: 0 auto;">'+title+'</div></div>'

	html += '<div style="border:solid 1px #000;background-color:#fff;position:absolute;overflow:hidden;width:'+str(canvas_width-dec_space-2)+'px;height:'+str(canvas_height-dec_space-2)+'px;left:'+str(dec_space)+'px;top:'+str(dec_space)+'px">'
	return html,'</div></div>'


def createLegend(legend,width:int):

	# The legend box
	html = '<div style="position:relative;color:#000;background-color:'+cols['light_grey']+';width:'+str(width-20)+'px;left:20px;font-family:monospace">'

	# Add legend items
	for line in legend:
		html += '<div style="margin-left:2px">'+line+'</div>'
	html += '<div style="font-style:italic;color:'+cols['dark_grey']+';margin-left:2px;">This map was generated automatically by the MareHub mariqt python package at '+datetime.datetime.now(tz=datetime.timezone.utc).strftime(miqtv.date_formats['mariqt_short'])+'</div>'

	# Add MareHub icon
	html += miqtss.marehub_logo
	html += '</div>'

	return html

def plotNavigationData(positions:miqtg.Positions,canvas_width,canvas_height,min_lat,max_lat,min_lon,max_lon,icon_color:str = '#000',icon:str = ''):

	time_points = list(positions.keys())

	if icon == '':
		icon = 'width:1px;height:1px'

	ret = ""
	for utc in time_points:

		x = round((positions[utc].lon - min_lon) / (max_lon - min_lon) * canvas_width)
		y = round((positions[utc].lat - min_lat) / (max_lat - min_lat) * canvas_height)

		if x >= 0 and x < canvas_width and y >= 0 and y < canvas_height:
			ret += '<div style="position:absolute;left:'+str(x)+'px;bottom:'+str(y)+'px;'+icon+';background-color:'+icon_color+'"></div>'

	return ret


def createProvenanceReportSection(provenance:miqtp.Provenance):
	html = '<div class="box_title" style="color:'+cols['dark_grey']+'">Provenance info</div>'
	html += '<div class="box" style="border-color:'+cols['grey']+';color:'+cols['dark_grey']+';background-color:'+cols['light_grey']+'"><table>'

	# Write current provenance info
	html += '<tr><td class="tab_key">Executable (version):</td><td class="tab_val">'+provenance.executable+' ('+provenance.version+')</td></tr>'
	html += '<tr><td class="tab_key">Arguments:</td><td class="tab_val">'+str(provenance.arguments)+'</td></tr>'

	# Sort previous provenances by time
	times = {}
	for i,prov in enumerate(provenance.prov):
			utc = int(datetime.datetime.strptime(prov['time'],miqtv.date_formats['mariqt']).timestamp())
			times[utc] = i

	# Write previous provenance infos
	for i in sorted(times,reverse=True):

	#for i,prov in enumerate(provenance.prov):
		prov = provenance.prov[times[i]]
		version = ""
		if 'version' in prov['executable']:
			version = ' ('+prov['executable']['version']+')'
		html += '<tr><td colspan="2"><hr style="height:1px;border-width:0;color:'+cols['grey']+';background-color:'+cols['grey']+'"></td></tr>'
		html += '<tr><td class="tab_key">Executable (version):</td><td class="tab_val">'+prov['executable']['name']+version+'</td></tr>'
		html += '<tr><td class="tab_key">Execution time:</td><td class="tab_val">'+prov['time']+'</td></tr>'
		if 'hashes' in prov:
			if i in prov['hashes']:
				html += '<tr><td class="tab_key">Hash:</td><td class="tab_val">'+prov['hashes'][i]+'</td></tr>'
		if 'arguments' in prov:
			html += '<tr><td class="tab_key">Arguments:</td><td class="tab_val">'+str(prov['arguments'])+'</td></tr>'
	html += '</table></div>'
	return html
