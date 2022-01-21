#!/usr/bin/env python3

'''
This is the command line interface for TruSD and auxilliary scripts. As such,
this module is only meant for use from the command line. For information about
TruSD, please refer to help(trusd) or https://github.com/mathiasbockwoldt/TruSD .
'''

import argparse
import json
import sys

import numpy as np


def parse_string_as_list(string, func, name, expected_length=0):
	'''
	Split a string by comma (,) and apply a function on each value. The function
	is usually int or float to turn the values into numbers.

	@param string: The string to parse
	@param func: Function to apply on each value of the list
	@param name: The name to report in case of an error
	@param expected_length: Expected length (as integer) of the resulting list
	@returns: A list with the values defined by the parameters
	'''

	lst = string.split(',')

	if expected_length and len(lst) != expected_length:
		print(
			'Input {} has only {} elements, but should have {}.'.format(
				name, len(lst), expected_length
			), file=sys.stderr)
		sys.exit(1)

	try:
		lst = [func(x) for x in lst]
	except ValueError:
		print(
			'Elements in input {} must be of type {}'.format(
				name, func.__name__
			), file=sys.stderr)
		sys.exit(1)

	return lst


def main():
	'''
	Main function for the command line interface of TruSD. Parse the command
	line arguments and read a file, calculate the likelihoods in a grid and save
	the results to another file.
	'''

	import trusd

	parser = argparse.ArgumentParser(description='''
		TruSD co-infers selection coefficients and genetic drift from allele
		trajectories using a maximum-likelihood framework.''')

	parser.add_argument('infile', metavar='file.txt',
						help='path to input file')

	parser.add_argument('-d', '--delimiter', metavar='x', default=',',
						help='''delimiter for input file. Use "tab" or "space"
						for these special characters. [default: %(default)s]''')

	parser.add_argument('-c', '--colskip', metavar='n', default=0, type=int,
						help='''number of columns to skip from the beginning
						(left) [default: %(default)s]''')

	parser.add_argument('-o', '--outfile', metavar='out.csv', default='outfile.csv',
						help='''output file. Give an empty string to not save the
						result matrix. [default: %(default)s]''')

	parser.add_argument('-q', '--plotfile', metavar='out.pdf', default='',
						help='''plot output file. Give an empty string to not
						create a plot. [default: ""]''')

	parser.add_argument('-n', '--noinfo', action='store_true',
						help='''if set, no json file with metadata will be
						written along with the result table.''')

	parser.add_argument('-N', '--popsize', metavar='int', default=200, type=int,
						help='(effective) population size [default: %(default)s]')

	parser.add_argument('-p', '--proportion', metavar='start,stop,step',
						default='0,1,0.005',
						help='''proportion; give in the form start,stop,step
						without whitespace, where the values are integers or
						floats. Mutually exclusive with -P/--proplist.
						[default: %(default)s]''')

	parser.add_argument('-P', '--proplist', metavar='p1,p2,...',
						help='''list of proportions; give in the form
						p1,p2,p3,... without whitespace, where px are integers
						or floats. Mutually exclusive with -p/--proportion.
						[default: %(default)s]''')

	parser.add_argument('-s', '--selection', metavar='start,stop,step',
						default='-0.08,0.08,0.002',
						help='''selection coefficient; give in the form
						start,stop,step without whitespace, where the values are
						integers or floats. Mutually exclusive with
						-S/--seleclist. [default: %(default)s]''')

	parser.add_argument('-S', '--seleclist', metavar='s1,s2,...',
						help='''list of selection coefficients; give in the form
						s1,s2,s3,... without whitespace, where sx are integers
						or floats. Mutually exclusive with -s/--selection.
						[default: %(default)s]''')

	parser.add_argument('-t', '--times', metavar='t1,t2,...', default='0,50',
						help='''time stemps; give in the form t1,t2,t3,...
						without whitespace, where tx are integers.
						[default: %(default)s]''')

	args = parser.parse_args()

	if args.proplist:
		prop_list = np.array(
			parse_string_as_list(args.proplist, float, '--proplist')
		)
	else:
		prop = parse_string_as_list(args.proportion, float, '--proportion', 3)
		prop_list = np.arange(prop[0], prop[1] + prop[2], prop[2])

	if args.seleclist:
		selec_list = np.array(
			parse_string_as_list(args.seleclist, float, '--seleclist')
		)
	else:
		selec = parse_string_as_list(args.selection, float, '--selection', 3)
		selec_list = np.arange(selec[0], selec[1] + selec[2], selec[2])

	times = parse_string_as_list(args.times, int, '--times')

	if args.delimiter == 'tab':
		args.delimiter = '\t'
	elif args.delimiter == 'space':
		args.delimiter = ' '

	trajectories = trusd.read_trajectory_file(
		args.infile,
		delimiter=args.delimiter,
		skip_columns=args.colskip
	)

	results = trusd.run_analysis(
		trajectories,
		args.popsize,
		prop_list,
		selec_list,
		times,
		args.outfile,
		args.plotfile
	)

	print(f'Best (s, p) is ({results[0]:.5f}, {results[1]:.5f})')

	if args.outfile or not args.noinfo:
		trusd.write_info_file(
			input_file = args.infile,
			output_file = args.outfile,
			command = ' '.join(sys.argv),
			pop_size = args.popsize,
			times = times,
			proportions = list(prop_list),
			selection_coefficients = list(selec_list),
			delimiter = args.delimiter
		)


def simulate():
	'''
	Main function for the command line interface for TruSD simulate. Parse the
	command line arguments, simulate trajectories and save the results to files.
	'''

	import trusd.simulate as sim

	parser = argparse.ArgumentParser(description='''
		TruSD simulate simulates evolutionary trajectories based on given
		parameters.''')

	parser.add_argument('-d', '--delimiter', metavar='x', default=',',
						help='''delimiter for output files. Use "tab" or "space"
						for these special characters. [default: %(default)s]''')

	parser.add_argument('-o', '--outdir', metavar='out/', default='.',
						help='output directory [default: %(default)s]')

	parser.add_argument('-s', '--sums', metavar='s1,s2,...', default='10',
						help='''list of sums of trajectories; give in the form
						s1,s2,s3,... without whitespace, where sx are integers
						or floats. [default: %(default)s]''')

	parser.add_argument('-t', '--times', metavar='t1,t2,...', default='10,20',
						help='''time stemps; give in the form t1,t2,t3,...
						without whitespace, where tx are integers.
						[default: %(default)s]''')

	parser.add_argument('-S', '--seleclist', metavar='s1,s2,...', default='-0.05,0,0.05',
						help='''list of selection coefficients; give in the form
						s1,s2,s3,... without whitespace, where sx are integers
						or floats. [default: %(default)s]''')

	parser.add_argument('-P', '--proplist', metavar='p1,p2,...', default='0.1,0.5,0.9',
						help='''list of proportions; give in the form
						p1,p2,p3,... without whitespace, where px are integers
						or floats. [default: %(default)s]''')

	parser.add_argument('-N', '--popsize', metavar='int', default=200, type=int,
						help='population size [default: %(default)s]')

	parser.add_argument('-G', '--generations', metavar='int', default=50, type=int,
						help='number of generations [default: %(default)s]')

	parser.add_argument('-f', '--startfreq', metavar='float', default=0.5, type=float,
						help='start frequency of allele a [default: %(default)s]')

	parser.add_argument('--seed', metavar='int', type=int,
						help='''seed for the pseudo random number generation for
						reproducability. If none is given, the PRNG is
						initialized according to Python defaults.''')

	args = parser.parse_args()

	sums_list = np.array(parse_string_as_list(args.sums, int, '--sums'))
	times_list = np.array(parse_string_as_list(args.times, int, '--times'))
	selec_list = np.array(parse_string_as_list(args.seleclist, float, '--seleclist'))
	prop_list = np.array(parse_string_as_list(args.proplist, float, '--proplist'))

	if args.delimiter == 'tab':
		args.delimiter = '\t'
	elif args.delimiter == 'space':
		args.delimiter = ' '

	if args.seed:
		sim.init_prng(args.seed)

	sim.run_group_of_simulations(
		sums_of_trajectories = sums_list,
		time_points = times_list,
		sel_coeffs = selec_list,
		proportions = prop_list,
		pop_size = args.popsize,
		generations = args.generations,
		start_freq = args.startfreq,
		outdir = args.outdir,
		delimiter = args.delimiter
	)


def plot():
	'''
	Main function for the command line interface for TruSD plot. Parse the
	command line arguments, open files and plot them.
	'''

	import trusd.plot as tplot

	parser = argparse.ArgumentParser(description='''
		TruSD plot plots evolutionary trajectories based on given parameters.''')

	parser.add_argument('infile', metavar='in.csv',
						help='path to input file')

	parser.add_argument('-i', '--infofile', metavar='in.json',
						help='''path to info file with the plotting parameters.
						If none is given, -p/-P and -s/-S must be given!''')

	parser.add_argument('-d', '--delimiter', metavar='x', default=',',
						help='''delimiter for input file. Use "tab" or "space"
						for these special characters. Overwritten by `--infofile`.
						[default: %(default)s]''')

	parser.add_argument('-p', '--proportion', metavar='start,stop,step',
						default='0,1,0.005',
						help='''proportion; give in the form start,stop,step
						without whitespace, where the values are integers or
						floats. Mutually exclusive with -P/--proplist.
						Not needed, when `--infofile` is given, which will
						override this value. [default: %(default)s]''')

	parser.add_argument('-P', '--proplist', metavar='p1,p2,...',
						help='''list of proportions; give in the form
						p1,p2,p3,... without whitespace, where px are integers
						or floats. Mutually exclusive with -p/--proportion.
						Not needed, when `--infofile` is given, which will
						override this value. [default: %(default)s]''')

	parser.add_argument('-s', '--selection', metavar='start,stop,step',
						default='-0.08,0.08,0.002',
						help='''selection coefficient; give in the form
						start,stop,step without whitespace, where the values are
						integers or floats. Mutually exclusive with
						-S/--seleclist. Not needed, when `--infofile` is given,
						which will override this value. [default: %(default)s]''')

	parser.add_argument('-S', '--seleclist', metavar='s1,s2,...',
						help='''list of selection coefficients; give in the form
						s1,s2,s3,... without whitespace, where sx are integers
						or floats. Mutually exclusive with -s/--selection.
						Not needed, when `--infofile` is given, which will
						override this value. [default: %(default)s]''')

	parser.add_argument('-n', '--numtraj', metavar='n', default=500, type=int,
						help='''number of trajectories. This value is only used
						for information on the top of the plot.
						[default: %(default)s]''')

	parser.add_argument('-c', '--contourline', metavar='n', default=1.92, type=float,
						help='''subtract this value to display the contour line.
						Somewhat arbitrary; try various values. Set to 0 to
						hide the line.
						[default: %(default)s]''')

	parser.add_argument('-o', '--outfile', metavar='out.pdf',
						help='''save plot to this filename. Choose file type by
						extension. Typical extensions are: pdf, png, tiff, svg.
						Check your local matplotlib installation for other
						possible file extensions. If this argument is missing,
						nothing will be saved.''')

	parser.add_argument('-v', '--view', action='store_true',
						help='if set, show the plot in an interactive window')

	args = parser.parse_args()

	if args.infofile:
		info = json.load(open(args.infofile))
		selec_list = info['selection_coefficients']
		prop_list = info['proportions']
		delimiter = info['delimiter']
	else:
		if args.proplist:
			prop_list = np.array(
				parse_string_as_list(args.proplist, float, '--proplist')
			)
		else:
			prop = parse_string_as_list(args.proportion, float, '--proportion', 3)
			prop_list = np.arange(prop[0], prop[1] + prop[2], prop[2])

		if args.seleclist:
			selec_list = np.array(
				parse_string_as_list(args.seleclist, float, '--seleclist')
			)
		else:
			selec = parse_string_as_list(args.selection, float, '--selection', 3)
			selec_list = np.arange(selec[0], selec[1] + selec[2], selec[2])

		delimiter = args.delimiter



	tplot.contour_plot(
		input_file = args.infile,
		num_trajectories = args.numtraj,
		s_list = selec_list,
		p_list = prop_list,
		contour_line_subtract = args.contourline,
		delimiter = delimiter,
		save = args.outfile,
		show = args.view
	)
