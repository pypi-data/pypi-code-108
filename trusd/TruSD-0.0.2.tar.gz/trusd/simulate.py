#!/usr/bin/env python3

import os
import sys
import random
from string import ascii_lowercase

import numpy as np


def init_prng(seed):
	'''
	Initialize the pseudo random number generator.

	@param seed: The seed to initialize with
	'''

	random.seed(seed)


def _random_string(length):
	'''
	Creates a random string of length `length` consisting of the letters a to z.

	@param length: The length of the desired string
	@returns: A random string of length `length`
	'''

	return ''.join(random.choice(ascii_lowercase) for _ in range(length))


def simulate_trajectories(top_traj, time_points, sel_coeff, start_freq,
							pop_size, generations):
	'''
	Run a single simulation with the given parameters. This will create two
	trajectories for each time point, one with the given selection coefficient
	and one with a selection coefficient of 0.

	@param top_traj: TODO
	@param time_points: List of time points to save in trajectories
	@param sel_coeff: The selection coefficient to use
	@param start_freq: The starting frequency of allele a
	@param pop_size: The population size
	@param generations: Number of generations to simulate
	@returns: A dict with timepoints pointing to lists that contain the
			trajectory for the given timepoint.
	'''

	trajectories = {point: [] for point in time_points}

	for _ in range(top_traj):
		frequency = int(start_freq * pop_size)

		for generation in range(generations):
			p = frequency / generations

			# http://numerical.recipes/whp/notes/wrightfisher.pdf
			q = (p * (1 + sel_coeff)) / (1 + p * sel_coeff)

			if q > 1:
				q = 1
			elif q < 0:
				q = 0

			frequency = np.random.binomial(pop_size, q)

			if generation + 1 in trajectories:
				trajectories[generation + 1].append(frequency)

	return trajectories


def run_simulation(time_points, sum_of_trajectories=10, sel_coeff=0.05,
					proportion=0.9, pop_size=200, generations=50, start_freq=0.5):
	'''
	Run a single simulation with the given parameters. This will create two
	trajectories for each time point, one with the given selection coefficient
	and one with a selection coefficient of 0.

	@param time_points: List of time points to save in trajectories
	@param sum_of_trajectories: TODO
	@param sel_coeff: The selection coefficient to use
	@param proportion: The proportion to use
	@param pop_size: The population size
	@param generations: Number of generations to simulate
	@param start_freq: The starting frequency of allele a
	@returns: A tuple with two lists of trajectories. The first one using the
			given selection coefficient, the second one using a selection
			coefficient of 0.
	'''

	traj_m2 = int(proportion * sum_of_trajectories)
	m2_trajectories = simulate_trajectories(traj_m2, time_points, sel_coeff,
											start_freq, pop_size, generations)

	traj_m1 = int(sum_of_trajectories - traj_m2)
	m1_trajectories = simulate_trajectories(traj_m1, time_points, 0, start_freq,
											pop_size, generations)

	return m2_trajectories, m1_trajectories


def run_group_of_simulations(sums_of_trajectories, time_points, sel_coeffs,
							proportions, pop_size=200, generations=50,
							start_freq=0.5, outdir='.', delimiter=','):
	'''
	Run a group of simulation with the given parameters. This will write the
	simulation results to files with informative, but random file names.

	@param sums_of_trajectories: TODO
	@param time_points: List of numbers of time points to save in trajectories
	@param sel_coeffs: List of selection coefficients to use
	@param proportions: List of proportions to use
	@param pop_size: The population size
	@param generations: Number of generations to simulate
	@param start_freq: The starting frequency of allele a
	@param outdir: The output directory to write to
	@param delimiter: The delimiter to use for the output tables
	'''

	for num_of_timepoints in time_points:
		for sum_of_trajectories in sums_of_trajectories:
			for sel_coeff in sel_coeffs:
				for proportion in proportions:
					print(
						('Simulating {:>3} trajectories with {:>2} timepoints, '
						 'a sel. coeff. of {:>5} and a proportion of {:>3}.'
						).format(sum_of_trajectories, num_of_timepoints,
								sel_coeff, proportion), file=sys.stderr)

					# TODO: Shouldn't the "50" be "generations"?
					tpoints = list(np.linspace(0, 50, num_of_timepoints + 1, dtype=int))[1:]

					m2, m1 = run_simulation(
						time_points = tpoints,
						sum_of_trajectories = sum_of_trajectories,
						sel_coeff = sel_coeff,
						proportion = proportion,
						pop_size = pop_size,
						generations = generations,
						start_freq = start_freq
					)

					filename = '{}_m2.csv'.format('_'.join(str(x) for x in [
						num_of_timepoints,
						sum_of_trajectories,
						sel_coeff,
						proportion,
						pop_size,
						generations,
						start_freq,
						_random_string(4)]))

					with open(os.path.join(outdir, filename), 'w') as out:

						out.write('0{}{}\n'.format(
							delimiter, delimiter.join(map(str, time_points)))
						)

						for i in range(len(m2[time_points[0]])):
							values = delimiter.join(
								[str(x) for x in [m2[p][i] for p in time_points]]
							)
							out.write('{}{}{}\n'.format(
								int(start_freq * pop_size), delimiter, values)
							)


if __name__ == '__main__':
	run_group_of_simulations([10], [10, 20], [-0.05, 0, 0.05], [0.1, 0.5, 0.9])
