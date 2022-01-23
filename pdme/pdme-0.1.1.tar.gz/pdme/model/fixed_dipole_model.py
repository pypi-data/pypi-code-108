import numpy
import numpy.random
from dataclasses import dataclass
from typing import Sequence, Tuple
import scipy.optimize
from pdme.model.model import Model
from pdme.measurement import DotMeasurement, OscillatingDipoleArrangement, OscillatingDipole


class FixedDipoleModel(Model):
	'''
	Model of oscillating dipole with a fixed dipole moment.

	Parameters
	----------
	p : numpy.ndarray
		The fixed dipole moment.
	n : int
		The number of dipoles to assume.
	'''
	def __init__(self, xmin: float, xmax: float, ymin: float, ymax: float, zmin: float, zmax: float, p: numpy.ndarray, n: int) -> None:
		self.xmin = xmin
		self.xmax = xmax
		self.ymin = ymin
		self.ymax = ymax
		self.zmin = zmin
		self.zmax = zmax
		self.p = p
		self._n = n
		self.rng = numpy.random.default_rng()

	def __repr__(self) -> str:
		return f'FixedDipoleModel({self.xmin}, {self.xmax}, {self.ymin}, {self.ymax}, {self.zmin}, {self.zmax}, {self.p}, {self.n()})'

	def get_dipoles(self, frequency: float) -> OscillatingDipoleArrangement:
		s_pts = numpy.array((self.rng.uniform(self.xmin, self.xmax), self.rng.uniform(self.ymin, self.ymax), self.rng.uniform(self.zmin, self.zmax)))
		return OscillatingDipoleArrangement([OscillatingDipole(self.p, s_pts, frequency)])

	def point_length(self) -> int:
		'''
			Dipole is constrained magnitude, but free orientation.
			Six degrees of freedom: (sx, sy, sz, w).
		'''
		return 4

	def n(self) -> int:
		return self._n

	def v_for_point_at_dot(self, dot: DotMeasurement, pt: numpy.ndarray) -> float:
		s = pt[0:3]
		w = pt[3]

		diff = dot.r - s
		alpha = self.p.dot(diff) / (numpy.linalg.norm(diff)**3)
		b = (1 / numpy.pi) * (w / (w**2 + dot.f**2))
		return alpha**2 * b

	def jac_for_point_at_dot(self, dot: DotMeasurement, pt: numpy.ndarray) -> numpy.ndarray:
		s = pt[0:3]
		w = pt[3]

		diff = dot.r - s
		alpha = self.p.dot(diff) / (numpy.linalg.norm(diff)**3)
		b = (1 / numpy.pi) * (w / (w**2 + dot.f**2))

		r_divs = (-self.p / (numpy.linalg.norm(diff)**3) + 3 * self.p.dot(diff) * diff / (numpy.linalg.norm(diff)**5)) * 2 * alpha * b

		f2 = dot.f**2
		w2 = w**2

		w_div = alpha**2 * (1 / numpy.pi) * ((f2 - w2) / ((f2 + w2)**2))

		return numpy.concatenate((r_divs, w_div), axis=None)


@dataclass
class FixedDipoleDiscretisation():
	'''
	Representation of a discretisation of a FixedDipoleDiscretisation.
	Also captures a rough maximum value of dipole.

	Parameters
	----------
	model : FixedDipoleModel
		The parent model of the discretisation.
	num_x : int
		The number of partitions of the x axis.
	num_y : int
		The number of partitions of the y axis.
	num_z : int
		The number of partitions of the z axis.
	'''
	model: FixedDipoleModel
	num_x: int
	num_y: int
	num_z: int

	def __post_init__(self):
		self.cell_count = self.num_x * self.num_y * self.num_z
		self.x_step = (self.model.xmax - self.model.xmin) / self.num_x
		self.y_step = (self.model.ymax - self.model.ymin) / self.num_y
		self.z_step = (self.model.zmax - self.model.zmin) / self.num_z

	def bounds(self, index: Tuple[float, float, float]) -> Tuple:
		xi, yi, zi = index

		# For this model, a point is (sx, sx, sy, w).
		# We want to keep w unbounded, restrict sx, sy, sz, px and py based on step.
		return (
			[
				xi * self.x_step + self.model.xmin, yi * self.y_step + self.model.ymin, zi * self.z_step + self.model.zmin,
				-numpy.inf
			],
			[
				(xi + 1) * self.x_step + self.model.xmin, (yi + 1) * self.y_step + self.model.ymin, (zi + 1) * self.z_step + self.model.zmin,
				numpy.inf
			]
		)

	def all_indices(self) -> numpy.ndindex:
		# see https://github.com/numpy/numpy/issues/20706 for why this is a mypy problem.
		return numpy.ndindex((self.num_x, self.num_y, self.num_z))  # type:ignore

	def solve_for_index(self, dots: Sequence[DotMeasurement], index: Tuple[float, float, float]) -> scipy.optimize.OptimizeResult:
		bounds = self.bounds(index)
		sx_mean = (bounds[0][0] + bounds[1][0]) / 2
		sy_mean = (bounds[0][1] + bounds[1][1]) / 2
		sz_mean = (bounds[0][2] + bounds[1][2]) / 2
		return self.model.solve(dots, initial_pt=numpy.array([sx_mean, sy_mean, sz_mean, .1]), bounds=bounds)
