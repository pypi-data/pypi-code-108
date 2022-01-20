#!/usr/bin/env python3

import datetime
import json
import os
from functools import lru_cache

import numpy as np
from scipy.special import comb


@lru_cache(maxsize=None)
def wright_fisher_trans_matrix(selection_coefficient, num_generations, genepop):
	'''
	Calculates the Wrigth-Fisher transition matrix given the selection coefficient,
	the number of generations and the genetic population. The calculation is
	computatinally very expensive, so the result is cached.

	@param selection_coefficient: The selection coefficient as float
	@param num_generations: The generation number as integer
	@param genepop: Gene population as integer
	@returns: The Wright-Fisher transition matrix as numpy array with shape (genepop+1, genepop+1)
	'''

	matrix = np.full((genepop + 1, genepop + 1), np.nan, dtype=np.float64)

	for n in range(genepop + 1):
		for m in range(genepop + 1):
			m_over_genepop = m / genepop
			first_product = (m_over_genepop + selection_coefficient * \
							m_over_genepop * (1 - m_over_genepop)) ** n
			second_product = (1 - m_over_genepop - selection_coefficient * \
							m_over_genepop * (1 - m_over_genepop)) ** (genepop - n)
			matrix[n, m] = comb(genepop, n) * first_product * second_product

	matrix = np.linalg.matrix_power(matrix, num_generations)

	return matrix


def single_likelihood(selection_coefficient, proportion, time_points, trajectories, genepop):
	'''
	Calculates the likelihood at a given point.

	@param selection_coefficient: The selection coefficient as float
	@param proportion: The proportion as float
	@param time_points: The time points to consider as list of integers
	@param trajectories: The trajectories as numpy array with shape (???) TODO!!!################
	@param genepop: Gene population as integer
	@returns: The likelihood for the given point as float
	'''

	result = 0
	for time_index in range(len(time_points) - 1):
		timepoint = time_points[time_index + 1] - time_points[time_index]

		transition_prob_sel = wright_fisher_trans_matrix(selection_coefficient, timepoint, genepop)
		transition_prob_neut = wright_fisher_trans_matrix(0, timepoint, genepop)

		for trajectory in range(len(trajectories)):
			row = trajectories[trajectory, time_index + 1]
			col = trajectories[trajectory, time_index]
			a = transition_prob_sel[row, col]
			b = transition_prob_neut[row, col]
			result += np.log((proportion * a + (1 - proportion) * b))

	return result


def likelihood_grid(trajectories, genepop, proportions, selections, time_points):
	'''
	Calculates the likelihood for each point of a grid of selection coefficients
	and proportions.

	@param trajectories: The trajectories as numpy array with shape (???) TODO!!!################
	@param genepop: Gene population as integer
	@param proportions: The proportions as list of floats
	@param selections: The selection coefficients as list of floats
	@param time_points: The time points to consider as list of integers
	@returns: The likelihood for each given point as numpy array of floats
	'''

	plen = len(proportions)
	slen = len(selections)

	# calculates the log-likelihood for each point on the grid
	mat = np.full((slen, plen), np.nan, dtype=np.float64)
	for i in range(slen):
		sel = selections[i]
		for j in range(plen):
			prop = proportions[j]
			mat[i, j] = single_likelihood(sel, prop, time_points, trajectories, genepop)

	return mat


def read_trajectory_file(fname, delimiter=',', skip_rows=1, skip_columns=0):
	'''
	Reads a trajectory file for use in TruSD

	@param fname: The file name of the trajectory file
	@param delimiter: Column delimiter
	@param skip_rows: Number of rows to skip in the beginning (header line(s))
	@param skip_columns: Number of columns to skip from left
	@returns: The contents of the trajectory file as numpy array
	'''

	def __strip_n_cols(fname, delimiter, skip_columns):
		'''
		Generator for reading in a file while skipping the first column.
		Modified from https://stackoverflow.com/a/20624201
		'''

		with open(fname, 'r') as infile:
			for line in infile:
				try:
					yield line.split(delimiter, skip_columns)[skip_columns]
				except IndexError:
					continue


	return np.loadtxt(
		__strip_n_cols(fname, delimiter, skip_columns),
		delimiter=delimiter,
		skiprows=skip_rows,
		dtype='uint16')


def write_info_file(input_file, output_file, command, pop_size, times, \
					proportions, selection_coefficients, delimiter):
	'''
	Writes an info file in json format with all necessary information to
	replicate and to plot the results.
	The json filename will be the same as `output_file` with the file name
	extension set to `.json`.

	@param input_file: The file name of the trajectory file
	@param output_file: The file name of the output table
	@param command: The command used to run TruSD
	@param pop_size: The population size
	@param times: List of time stamps
	@param proportions: List of proportions
	@param selection_coefficients: List of selection coefficients
	@returns The file name of the metadata file written
	'''

	info = {}
	info['description'] = ('This file contains the information for the TruSD '
							'file saved in output_file.')
	info['link'] = 'https://github.com/mathiasbockwoldt/TruSD'
	info['citation'] = ('Mathias Bockwoldt, Charlie Sinclair, David Waxman, '
						'and Toni I. Gossmann: TruSD: A python package to '
						'co-estimate selection and drift from allele '
						'trajectories. In preparation.')
	info['input_file'] = input_file
	info['output_file'] = output_file
	info['datetime'] = datetime.datetime.now().replace(microsecond=0).isoformat()
	info['command'] = command
	info['population_size'] = pop_size
	info['time_stamps'] = list(times)
	info['proportions'] = list(proportions)
	info['selection_coefficients'] = list(selection_coefficients)
	info['delimiter'] = delimiter

	info_file = '{}.json'.format(os.path.splitext(output_file)[0])
	with open(info_file, 'w') as out_stream:
		json.dump(info, out_stream, indent=2)

	return info_file
