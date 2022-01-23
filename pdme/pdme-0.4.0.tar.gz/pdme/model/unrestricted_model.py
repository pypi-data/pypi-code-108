import numpy
from dataclasses import dataclass
from typing import Sequence, Tuple
import scipy.optimize
from pdme.model.model import Model, Discretisation
from pdme.measurement import DotMeasurement, OscillatingDipoleArrangement, OscillatingDipole


class UnrestrictedModel(Model):
	'''
	Model of oscillating dipoles with no restrictions.
	Additionally, each dipole is assumed to be orientated in the plus or minus z direction.

	Parameters
	----------
	n : int
		The number of dipoles to assume.
	'''
	def __init__(self, xmin: float, xmax: float, ymin: float, ymax: float, zmin: float, zmax: float, max_p: float, n: int) -> None:
		self.xmin = xmin
		self.xmax = xmax
		self.ymin = ymin
		self.ymax = ymax
		self.zmin = zmin
		self.zmax = zmax
		self.max_p = max_p
		self._n = n
		self.rng = numpy.random.default_rng()

	def __repr__(self) -> str:
		return f'UnrestrictedModel({self.xmin}, {self.xmax}, {self.ymin}, {self.ymax}, {self.zmin}, {self.zmax}, {self.max_p}, {self.n()})'

	def point_length(self) -> int:
		'''
			Dipole is unconstrained in this model.
			All seven degrees of freedom: (px, py, pz, sx, sy, sz, w).
		'''
		return 7

	def n(self) -> int:
		return self._n

	def v_for_point_at_dot(self, dot: DotMeasurement, pt: numpy.ndarray) -> float:
		p = pt[0:3]
		s = pt[3:6]
		w = pt[6]

		diff = dot.r - s
		alpha = p.dot(diff) / (numpy.linalg.norm(diff)**3)
		b = (1 / numpy.pi) * (w / (w**2 + dot.f**2))
		return alpha**2 * b

	def jac_for_point_at_dot(self, dot: DotMeasurement, pt: numpy.ndarray) -> numpy.ndarray:
		p = pt[0:3]
		s = pt[3:6]
		w = pt[6]

		diff = dot.r - s
		alpha = p.dot(diff) / (numpy.linalg.norm(diff)**3)
		b = (1 / numpy.pi) * (w / (w**2 + dot.f**2))

		p_divs = 2 * alpha * diff / (numpy.linalg.norm(diff)**3) * b

		r_divs = (-p / (numpy.linalg.norm(diff)**3) + 3 * p.dot(diff) * diff / (numpy.linalg.norm(diff)**5)) * 2 * alpha * b

		f2 = dot.f**2
		w2 = w**2

		w_div = alpha**2 * (1 / numpy.pi) * ((f2 - w2) / ((f2 + w2)**2))

		return numpy.concatenate((p_divs, r_divs, w_div), axis=None)

	def get_dipoles(self, frequency: float) -> OscillatingDipoleArrangement:
		theta = numpy.arccos(self.rng.uniform(-1, 1))
		phi = self.rng.uniform(0, 2 * numpy.pi)
		p = self.rng.uniform(0, self.max_p)
		px = p * numpy.sin(theta) * numpy.cos(phi)
		py = p * numpy.sin(theta) * numpy.sin(phi)
		pz = p * numpy.cos(theta)
		s_pts = numpy.array((self.rng.uniform(self.xmin, self.xmax), self.rng.uniform(self.ymin, self.ymax), self.rng.uniform(self.zmin, self.zmax)))
		return OscillatingDipoleArrangement([OscillatingDipole(numpy.array([px, py, pz]), s_pts, frequency)])


@dataclass
class UnrestrictedDiscretisation(Discretisation):
	'''
	Representation of a discretisation of a UnrestrictedModel.
	Also captures a rough maximum value of dipole.

	Parameters
	----------
	model : UnrestrictedModel
		The parent model of the discretisation.
	num_px: int
		The number of partitions of the px.
	num_py: int
		The number of partitions of the py.
	num_pz: int
		The number of partitions of pz.
	num_x : int
		The number of partitions of the x axis.
	num_y : int
		The number of partitions of the y axis.
	num_z : int
		The number of partitions of the z axis.
	max_p : int
		The maximum p coordinate in any direction.
	'''
	model: UnrestrictedModel
	num_px: int
	num_py: int
	num_pz: int
	num_x: int
	num_y: int
	num_z: int

	def __post_init__(self):
		self.max_p = self.model.max_p
		self.cell_count = self.num_x * self.num_y * self.num_z
		self.x_step = (self.model.xmax - self.model.xmin) / self.num_x
		self.y_step = (self.model.ymax - self.model.ymin) / self.num_y
		self.z_step = (self.model.zmax - self.model.zmin) / self.num_z
		self.px_step = 2 * self.max_p / self.num_px
		self.py_step = 2 * self.max_p / self.num_py
		self.pz_step = 2 * self.max_p / self.num_pz

	def bounds(self, index: Tuple[float, ...]) -> Tuple:
		pxi, pyi, pzi, xi, yi, zi = index

		# For this model, a point is (px, py, pz, sx, sx, sy, w).
		# We want to keep w unbounded, restrict sx, sy, sz, px and py based on step.
		return (
			[
				pxi * self.px_step - self.max_p, pyi * self.py_step - self.max_p, pzi * self.pz_step - self.max_p,
				xi * self.x_step + self.model.xmin, yi * self.y_step + self.model.ymin, zi * self.z_step + self.model.zmin,
				-numpy.inf
			],
			[
				(pxi + 1) * self.px_step - self.max_p, (pyi + 1) * self.py_step - self.max_p, (pzi + 1) * self.pz_step - self.max_p,
				(xi + 1) * self.x_step + self.model.xmin, (yi + 1) * self.y_step + self.model.ymin, (zi + 1) * self.z_step + self.model.zmin,
				numpy.inf
			]
		)

	def all_indices(self) -> numpy.ndindex:
		# see https://github.com/numpy/numpy/issues/20706 for why this is a mypy problem.
		return numpy.ndindex((self.num_px, self.num_py, self.num_pz, self.num_x, self.num_y, self.num_z))  # type:ignore

	def solve_for_index(self, dots: Sequence[DotMeasurement], index: Tuple[float, ...]) -> scipy.optimize.OptimizeResult:
		bounds = self.bounds(index)
		px_mean = (bounds[0][0] + bounds[1][0]) / 2
		py_mean = (bounds[0][1] + bounds[1][1]) / 2
		pz_mean = (bounds[0][2] + bounds[1][2]) / 2
		sx_mean = (bounds[0][3] + bounds[1][3]) / 2
		sy_mean = (bounds[0][4] + bounds[1][4]) / 2
		sz_mean = (bounds[0][5] + bounds[1][5]) / 2
		return self.model.solve(dots, initial_pt=numpy.array([px_mean, py_mean, pz_mean, sx_mean, sy_mean, sz_mean, .1]), bounds=bounds)
