import numpy
from dataclasses import dataclass
from typing import Tuple, Sequence
import scipy.optimize

from pdme.model.model import Model
from pdme.measurement import DotMeasurement


class FixedZPlaneModel(Model):
	'''
	Model of oscillating dipoles constrained to lie within a plane.
	Additionally, each dipole is assumed to be orientated in the plus or minus z direction.

	Parameters
	----------
	z : float
		The z position of the plane where dipoles are constrained to lie.
	xmin : float
		The minimum x value for dipoles.
	xmax : float
		The maximum x value for dipoles.
	ymin : float
		The minimum y value for dipoles.
	ymax : float
		The maximum y value for dipoles.
	n : int
		The number of dipoles to assume.
	'''
	def __init__(self, z: float, xmin: float, xmax: float, ymin: float, ymax: float, n: int) -> None:
		self.z = z
		self.xmin = xmin
		self.xmax = xmax
		self.ymin = ymin
		self.ymax = ymax
		self._n = n

	def __repr__(self) -> str:
		return f'FixedZPlaneModel({self.z}, {self.xmin}, {self.xmax}, {self.ymin}, {self.ymax}, {self.n()})'

	def point_length(self) -> int:
		'''
			Dipole is constrained in this model to have (px, py, pz) = (0, 0, pz) and (sx, sy, sz) = (sx, sy, self.z).
			With some frequency w, there are four degrees of freedom: (pz, sx, sy, w).
		'''
		return 4

	def n(self) -> int:
		return self._n

	def v_for_point_at_dot(self, dot: DotMeasurement, pt: numpy.ndarray) -> float:
		p = numpy.array([0, 0, pt[0]])
		s = numpy.array([pt[1], pt[2], self.z])
		w = pt[3]

		diff = dot.r - s
		alpha = p.dot(diff) / (numpy.linalg.norm(diff)**3)
		b = (1 / numpy.pi) * (w / (w**2 + dot.f**2))
		return alpha**2 * b

	def jac_for_point_at_dot(self, dot: DotMeasurement, pt: numpy.ndarray) -> numpy.ndarray:
		p = numpy.array([0, 0, pt[0]])
		s = numpy.array([pt[1], pt[2], self.z])
		w = pt[3]

		diff = dot.r - s
		alpha = p.dot(diff) / (numpy.linalg.norm(diff)**3)
		b = (1 / numpy.pi) * (w / (w**2 + dot.f**2))

		p_divs = 2 * alpha * diff[2] / (numpy.linalg.norm(diff)**3) * b  # only need the z component.

		r_divs = (-p[0:2] / (numpy.linalg.norm(diff)**3) + 3 * p.dot(diff) * diff[0:2] / (numpy.linalg.norm(diff)**5)) * 2 * alpha * b

		f2 = dot.f**2
		w2 = w**2

		w_div = alpha**2 * (1 / numpy.pi) * ((f2 - w2) / ((f2 + w2)**2))

		return numpy.concatenate((p_divs, r_divs, w_div), axis=None)


@dataclass
class FixedZPlaneDiscretisation():
	'''
	Representation of a discretisation of a FixedZPlaneModel.
	Also captures a rough maximum value of dipole.

	Parameters
	----------
	model : FixedZPlaneModel
		The parent model of the discretisation.
	num_pz: int
		The number of partitions of pz.
	num_x : int
		The number of partitions of the x axis.
	num_y : int
		The number of partitions of the y axis.
	'''
	model: FixedZPlaneModel
	num_pz: int
	num_x: int
	num_y: int
	max_pz: int

	def __post_init__(self):
		self.cell_count = self.num_x * self.num_y
		self.pz_step = (2 * self.max_pz) / self.num_pz
		self.x_step = (self.model.xmax - self.model.xmin) / self.num_x
		self.y_step = (self.model.ymax - self.model.ymin) / self.num_y

	def bounds(self, index: Tuple[float, float, float]) -> Tuple[numpy.ndarray, numpy.ndarray]:
		pzi, xi, yi = index

		# For this model, a point is (pz, sx, sy, w).
		# We want to keep w bounded, and restrict pz, sx and sy based on step.
		return (
			numpy.array((pzi * self.pz_step - self.max_pz, xi * self.x_step + self.model.xmin, yi * self.y_step + self.model.ymin, -numpy.inf)),
			numpy.array(((pzi + 1) * self.pz_step - self.max_pz, (xi + 1) * self.x_step + self.model.xmin, (yi + 1) * self.y_step + self.model.ymin, numpy.inf))
		)

	def all_indices(self) -> numpy.ndindex:
		# see https://github.com/numpy/numpy/issues/20706 for why this is a mypy problem.
		return numpy.ndindex((self.num_pz, self.num_x, self.num_y))  # type:ignore

	def solve_for_index(self, dots: Sequence[DotMeasurement], index: Tuple[float, float, float]) -> scipy.optimize.OptimizeResult:
		bounds = self.bounds(index)
		pz_mean = (bounds[0][0] + bounds[1][0]) / 2
		sx_mean = (bounds[0][1] + bounds[1][1]) / 2
		sy_mean = (bounds[0][2] + bounds[1][2]) / 2
		# I don't care about the typing here at the moment.
		return self.model.solve(dots, initial_pt=numpy.array((pz_mean, sx_mean, sy_mean, .1)), bounds=bounds)  # type: ignore
