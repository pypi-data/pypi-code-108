import io
import json
import textwrap
from typing import Callable

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import matplotlib 

plt.rcParams["figure.dpi"] = 200

def clock_to_hours(clock_arg:str) -> float:
	"""convert a time hour string to its float representation of hours since midnight
	>>> clock_to_hours("18:45")
	18.75
	>>> clock_to_hours("18:40:21")
	18.6725
	>>> clock_to_hours("6:45pm")
	18.75
	>>> clock_to_hours("3am")
	3.0
	"""
	bias = 12 if "pm" in clock_arg else 0
	clock = clock_arg.replace("pm","").replace("am","")
	splitted = clock.split(":")
	hour_contributions = [float(s)/60**i for i,s in enumerate(splitted)]
	return bias + sum(hour_contributions)

def interval_mapper(before:list,after:list) -> Callable:
	"""returns a function that linearly transforms the interval [min(before),max(before)] onto [min(after),max(after)]
	>>> foo = interval_mapper([-5,1.5],[0,1]);
	>>> foo(-5)
	0.0
	>>> foo(1.5)
	1.0
	>>> foo(0)
	0.7692307692307693
	"""
	def mapping(x):
		return mapping.m * x + mapping.b
	mapping.m = np.ptp(after) / np.ptp(before)
	mapping.b = (max(before)*min(after) - max(after)*min(before)) / np.ptp(before)
	return mapping
	
def import_from_json(stream:io.StringIO) -> dict:
	"""Deserializes a JSON stream containing the schedule specification and converts it into a computable dict form.
	For more info on the schedule JSON format read the global README
	
	This is for testing purposes, the function is usually used like
	#>>> with open(...) as file:
	#>>>     data = import_fron_json(file)
	###
	>>> import io
	>>> stream = io.StringIO(initial_value='{"Class 1":{"MWF":"11:00am-2:30pm"},"Lab 1":{"M":"2pm-2:30pm","S":"8am-10:15"}}')
	>>> import_from_json(stream)
	{'Class 1': {'M': [11.0, 14.5], 'W': [11.0, 14.5], 'F': [11.0, 14.5]}, 'Lab 1': {'M': [14.0, 14.5], 'S': [8.0, 10.25]}}
	"""
	json_contents = json.load(stream)
	schedule = {}
	for title,contents in json_contents.items():
		subject = {}
		for days,hours in contents.items():
			for day in days:
				subject[day] = [clock_to_hours(hour) for hour in hours.split("-")]
		schedule[title] = subject
	return schedule

def schedule_figure(
		schedule_path:str,
		day_names:str="MTWRFS",
		font_dict:dict={},
		text_stroke:bool=True,
		major_minor_intervals:tuple=(1,1/4),
		cmap_name:str="plasma",
		cmap_range:tuple=(0,0.9)
	) -> matplotlib.figure.Figure:
		
	with open(schedule_path) as file:
		schedule = import_from_json(file)
	week_lenght = len(day_names)
	
	# set some defaults for font dict
	font_dict = dict(
		fontweight="bold",
		horizontalalignment='center',
		verticalalignment='center',
		fontsize=7 ,
		color="white"
	) | font_dict
	
	# unpack tick intervals
	major_interval,minor_interval = major_minor_intervals
	if round(major_interval) != major_interval:
		raise ValueError(f"major tick interval ({major_interval}) should be an integer")
	
	
	fig,axes = plt.subplots(ncols=week_lenght)
	axes_by_day = dict(zip(day_names,axes))
	norm = interval_mapper([0,len(schedule)-1],cmap_range)
	cmap = plt.get_cmap(cmap_name)
	
	for i,(subject,contents) in enumerate(schedule.items()):
		for day,(start,end) in contents.items():
			plt.sca(axes_by_day[day])
			plt.fill_between([0,1],[start,start],[end,end],color=cmap(norm(i)))
			
			subject_wrapped = "\n".join(textwrap.wrap(subject,14,replace_whitespace=False))
			text = plt.text(0.5,(start+end)/2,subject_wrapped,**font_dict)
			if text_stroke:
				text.set_path_effects([path_effects.Stroke(linewidth=1, foreground='black'),path_effects.Normal()])
	
	all_hours = sum([sum(day_hours.values(),[]) for day_hours in schedule.values()],[])
	min_hour = np.floor(min(all_hours)-0.5)
	max_hour = np.ceil(max(all_hours)+0.5)
	
	# y axes ticks
	yticks = np.arange(min_hour,max_hour,major_interval)
	minor_ticks = np.arange(min_hour,max_hour,minor_interval)
	
	# all axes: correct range and no ticks
	for day,ax in axes_by_day.items():
		ax.set_title(day)
		ax.set_ylim([max_hour,min_hour])
		ax.set_xlim([0,1])
		ax.set_axisbelow(True)
		ax.yaxis.set_ticklabels([])
		ax.xaxis.set_ticklabels([])
		ax.set_xticks([])
		ax.set_yticks(yticks)
		ax.yaxis.set_ticks_position('none')
		ax.xaxis.set_ticks_position('none')
		ax.set_yticks(minor_ticks,minor=True)
		
		plt.sca(ax)
		plt.grid(True,which="minor",color='k',alpha=.2,linestyle=(0,(5,5)),linewidth=0.3)
		plt.grid(True,which='major',color='k',alpha=.4,linewidth=0.5)
	
	
	# initial and final axes tweaks
	axes_by_day[day_names[0]].yaxis.tick_left()
	axes_by_day[day_names[0]].yaxis.set_ticks_position('left')
	
	axes_by_day[day_names[-1]].yaxis.tick_right()
	axes_by_day[day_names[-1]].yaxis.set_ticks_position('right')
	for day in [day_names[0],day_names[-1]]:
		ax = axes_by_day[day]
		ax.set_yticks(yticks)
		ax.set_yticklabels([f"{int(i):02}" for i in yticks])
	
	plt.tight_layout()
	plt.subplots_adjust(wspace=0.03)
	
	return fig
	
schedule_figure.__doc__ = """generates a matplotlib figure with the given schedule filename

	schedule_path:str
		location of the .json schedule file
		
	day_names:str = "MTWRFS"
		ordered names of the weekdays
	
	font_dict:dict = {}
		additional font tweaks; the same kargs of matplotlib.pyplot.text
		(https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.text.html)
		See source or README for defaults. You cannot control the stroke here.
	
	text_stroke:bool = True
		outward black stroke for better legibility of the text
	
	major_minor_intervals:tuple = (1,1/4),
		interval of major and minor ticks, in hours. 
		Major tickss interval must be an integer number of hours, else a ValueError is raised.
	
	cmap_name:str = "plasma"
		color palette to use on the subject backgrounds. 
		See the matplotlib colormap reference for a list of names
		(https://matplotlib.org/stable/gallery/color/colormap_reference.html)
	
	cmap_range:tuple = (0,0.9)
		min and max output range of the colormap. 
		In other words, portion of the colors to use.
		Full range is (0,1).
		
"""
