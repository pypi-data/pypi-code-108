from pdme.measurement import OscillatingDipole, OscillatingDipoleArrangement
import pdme
from deepdog.bayes_run import DotInput
import datetime
import numpy
import logging
from typing import Sequence, Tuple
import csv
import itertools
import multiprocessing

_logger = logging.getLogger(__name__)


def get_a_result(discretisation, dots, index):
	return (index, discretisation.solve_for_index(dots, index))


class Diagnostic():
	'''
	Represents a diagnostic for a single dipole moment given a set of discretisations.

	Parameters
	----------
	dot_inputs : Sequence[DotInput]
		The dot inputs for this diagnostic.
	discretisations_with_names : Sequence[Tuple(str, pdme.model.Model)]
		The models to evaluate.
	actual_model_discretisation : pdme.model.Discretisation
		The discretisation for the model which is actually correct.
	filename_slug : str
		The filename slug to include.
	run_count: int
		The number of runs to do.
	'''
	def __init__(self, actual_dipole_moment: numpy.ndarray, actual_dipole_position: numpy.ndarray, actual_dipole_frequency: float, dot_inputs: Sequence[DotInput], discretisations_with_names: Sequence[Tuple[str, pdme.model.Discretisation]], filename_slug: str) -> None:
		self.dipoles = OscillatingDipoleArrangement([OscillatingDipole(actual_dipole_moment, actual_dipole_position, actual_dipole_frequency)])
		self.dots = self.dipoles.get_dot_measurements(dot_inputs)

		self.discretisations_with_names = discretisations_with_names
		self.model_count = len(self.discretisations_with_names)

		self.csv_fields = ["model", "index", "bounds", "actual_dipole_moment", "actual_dipole_position", "actual_dipole_freq", "success", "result"]

		timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
		self.filename = f"{timestamp}-{filename_slug}.csv"

	def go(self):
		with open(self.filename, "a", newline="") as outfile:
			# csv fields
			writer = csv.DictWriter(outfile, fieldnames=self.csv_fields, dialect='unix')
			writer.writeheader()

		for (name, discretisation) in self.discretisations_with_names:
			_logger.info(f"Working on discretisation {name}")

			results = []
			with multiprocessing.Pool(multiprocessing.cpu_count() - 1 or 1) as pool:
				results = pool.starmap(get_a_result, zip(itertools.repeat(discretisation), itertools.repeat(self.dots), discretisation.all_indices()))

			with open(self.filename, "a", newline='') as outfile:
				writer = csv.DictWriter(outfile, fieldnames=self.csv_fields, dialect='unix')

				for idx, result in results:

					bounds = discretisation.bounds(idx)

					actual_success = result.success and result.cost <= 1e-10
					row = {
						"model": name,
						"index": idx,
						"bounds": bounds,
						"actual_dipole_moment": self.dipoles.dipoles[0].p,
						"actual_dipole_position": self.dipoles.dipoles[0].s,
						"actual_dipole_freq": self.dipoles.dipoles[0].w,
						"success": actual_success,
						"result": result.normalised_x if actual_success else None,
					}
					_logger.debug(f"Writing result {row}")
					writer.writerow(row)
