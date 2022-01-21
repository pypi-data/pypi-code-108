#!/usr/bin/env python3

import json
import os
import sys

DISPLAY_PRESENT = 'DISPLAY' in os.environ

if not DISPLAY_PRESENT:
	import matplotlib
	matplotlib.use('agg')

import numpy as np
import matplotlib.pyplot as plt

SMALL_SIZE = 12
MEDIUM_SIZE = 16
BIGGER_SIZE = 20


def _set_font_size():
	# Adapted from https://stackoverflow.com/a/39566040
	plt.rc('font', size=MEDIUM_SIZE)         # controls default text sizes
	plt.rc('axes', titlesize=MEDIUM_SIZE)     # fontsize of the axes title
	plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
	plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
	plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
	plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
	plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title


def plot_from_data(input_file, delimiter=',', *args, **kwargs):
	'''
	Plot data from TruSD output file given parameters. Parameters not explained
	here are explained in `contour_plot()`.

	@param input_file: The file name of the TruSD output to plot
	@param delimiter: Column delimiter of the input file
	'''

	values = np.loadtxt(input_file, delimiter=delimiter, unpack=True)

	contour_plot(values, *args, **kwargs)


def contour_plot(values, num_trajectories, s_list, p_list,
				contour_line_subtract, marker=None, save='', show=False):
	'''
	Plots a contour plot with given parameters. Note that this is just some
	more or less easy way to quickly plot TruSD results. For more sophisticated
	plotting parameters, you might want to copy the function to some local
	script and modify it.

	@param values: Numpy array with two dimensions with the data to plot #### TODO: Describe dimensions
	@param num_trajectories: The number of trajectories. This is only information
		for the title of the plot
	@param s_list: list of selection coefficients
	@param p_list: list of proportions
	@param contour_line_subtract: difference to subtract to draw the contour line.
		Experiement with different values. Set to 0 to remove the contour.
	@param marker: tuple with the point to mark on the plot in the form
		(s_value, p_value). If not given, the maximum point will be used.
	@param save: if this is a filename, save the plot to disk to this path.
	@param show: if trueish, show interactive plot
	'''

	if marker is None:
		rows = values.shape[1]
		max_value = values.argmax()

		s_value = np.round(s_list[max_value % rows], decimals=5)
		p_value = np.round(p_list[max_value // rows], decimals=5)
	else:
		s_value = marker[0]
		p_value = marker[1]

	xlist = s_list
	ylist = p_list

	xmesh, ymesh = np.meshgrid(xlist, ylist)

	max_values = np.max(values)
	min_values = np.min(values)

	levels = np.array([0.5, 0.7, 0.9, 0.95, 0.99, 0.999, 0.9999, 1.0])
	levels = levels * (max_values - min_values) + min_values

	_set_font_size()

	fig, ax = plt.subplots(1, 1, figsize=(12, 10))
	cplot = ax.contourf(xmesh, ymesh, values, levels, colors=[
		'#5affff', '#aaffff', '#d4ffff', '#ffffff', '#ffd5ff', '#ffaaff', '#ff80ff'
	])

	fig.colorbar(cplot, spacing='uniform')

	if contour_line_subtract:
		contour_line = ax.contour(
			xmesh, ymesh, values, [max_values - contour_line_subtract],
			colors=['#000000'], linestyles=['solid']
		)
		ax.clabel(contour_line, inline=1, fontsize=SMALL_SIZE)

	ax.plot(s_value, p_value, color='#ff0000', marker='o')  # markersize=

	ax.set_title('Num of trajectories = {}, s = {}, p = {}'.format(
		num_trajectories, s_value, p_value
	))
	ax.set_xlabel('Selection coefficient, s')
	ax.set_ylabel('Proportion of selected sites, p')

	if save:
		try:
			fig.savefig(save)
		except (AttributeError, IOError):
			outfile = '{}.pdf'.format(input_file.rsplit('.', maxsplit=1)[0])
			print('Python could not save to "{}". Saving to "{}".'.format(save, outfile),
				file=sys.stderr)
			fig.savefig(outfile)

	if show:
		if DISPLAY_PRESENT:
			plt.show()
		else:
			print('Python could not find a DISPLAY. Showing the plot is not supported.',
				file=sys.stderr)
			if not save:
				print('Try to save the plot instead.', file=sys.stderr)


def plot_from_metadata(metadata_file, contour_line_subtract, marker=None,
                   save=True, show=False):
	'''
	Plots a contour plot with parameters taken from a metadata (json) file.
	The other parameters are forwarded to `contour_plot()`.

	@param metadata_file: The file name of the TruSD output to plot
	@param contour_line_subtract: difference to subtract to draw the contour line.
		Experiement with different values. Set to 0 to remove the contour.
	@param marker: tuple with the point to mark on the plot in the form
		(s_value, p_value). If not given, the maximum point will be used.
	@param save: if trueish, save the plot to disk. If this is a string, save to
		that filename. Otherwise, save to `input_file` with pdf as extension.
	@param show: if trueish, show interactive plot
	'''

	info = json.load(open(metadata_file))

	plot_from_data(
		input_file = info['output_file'],
		delimiter = info['delimiter'],
		num_trajectories = info['population_size'],
		s_list = info['selection_coefficients'],
		p_list = info['proportions'],
		contour_line_subtract = contour_line_subtract,
		marker = marker,
		save = save,
		show = show
	)


if __name__ == '__main__':
	plot_from_metadata(
		input_file = 'outfile.json',
		contour_line_subtract = 1.92,
		save = True,
		show = True
	)
