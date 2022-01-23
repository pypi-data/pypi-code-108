import numpy
import numpy.random
from dataclasses import dataclass
from typing import Sequence, Tuple
import scipy.optimize
from pdme.model.model import Model
from pdme.measurement import DotMeasurement, OscillatingDipole, OscillatingDipoleArrangement


class FixedMagnitudeModel(Model):
	'''
	Model of oscillating dipole with a fixed magnitude, but free rotation.

	Parameters
	----------
	pfixed : float
		The fixed dipole magnitude.
	n : int
		The number of dipoles to assume.
	'''
	def __init__(self, xmin: float, xmax: float, ymin: float, ymax: float, zmin: float, zmax: float, pfixed: float, n: int) -> None:
		self.xmin = xmin
		self.xmax = xmax
		self.ymin = ymin
		self.ymax = ymax
		self.zmin = zmin
		self.zmax = zmax
		self.pfixed = pfixed
		self._n = n
		self.rng = numpy.random.default_rng()

	def __repr__(self) -> str:
		return f'FixedMagnitudeModel({self.xmin}, {self.xmax}, {self.ymin}, {self.ymax}, {self.zmin}, {self.zmax}, {self.n()})'

	def point_length(self) -> int:
		'''
			Dipole is constrained magnitude, but free orientation.
			Six degrees of freedom: (p_theta, p_phi, sx, sy, sz, w).
		'''
		return 6

	def get_dipoles(self, frequency: float) -> OscillatingDipoleArrangement:
		theta = numpy.arccos(self.rng.uniform(-1, 1))
		phi = self.rng.uniform(0, 2 * numpy.pi)
		px = self.pfixed * numpy.sin(theta) * numpy.cos(phi)
		py = self.pfixed * numpy.sin(theta) * numpy.sin(phi)
		pz = self.pfixed * numpy.cos(theta)
		s_pts = numpy.array((self.rng.uniform(self.xmin, self.xmax), self.rng.uniform(self.ymin, self.ymax), self.rng.uniform(self.zmin, self.zmax)))
		return OscillatingDipoleArrangement([OscillatingDipole(numpy.array([px, py, pz]), s_pts, frequency)])

	def n(self) -> int:
		return self._n

	def v_for_point_at_dot(self, dot: DotMeasurement, pt: numpy.ndarray) -> float:
		p_theta = pt[0]
		p_phi = pt[1]
		s = pt[2:5]
		w = pt[5]

		p = numpy.array([
			self.pfixed * numpy.sin(p_theta) * numpy.cos(p_phi),
			self.pfixed * numpy.sin(p_theta) * numpy.sin(p_phi),
			self.pfixed * numpy.cos(p_theta)
		])
		diff = dot.r - s
		alpha = p.dot(diff) / (numpy.linalg.norm(diff)**3)
		b = (1 / numpy.pi) * (w / (w**2 + dot.f**2))
		return alpha**2 * b

	def jac_for_point_at_dot(self, dot: DotMeasurement, pt: numpy.ndarray) -> numpy.ndarray:
		p_theta = pt[0]
		p_phi = pt[1]
		s = pt[2:5]
		w = pt[5]

		p = numpy.array([
			self.pfixed * numpy.sin(p_theta) * numpy.cos(p_phi),
			self.pfixed * numpy.sin(p_theta) * numpy.sin(p_phi),
			self.pfixed * numpy.cos(p_theta)
		])
		diff = dot.r - s
		alpha = p.dot(diff) / (numpy.linalg.norm(diff)**3)
		b = (1 / numpy.pi) * (w / (w**2 + dot.f**2))

		theta_div_middle = self.pfixed * (
			diff[0] * numpy.cos(p_phi) * numpy.cos(p_theta)
			+ diff[1] * numpy.sin(p_phi) * numpy.cos(p_theta)
			- diff[2] * numpy.sin(p_theta)
		)
		theta_div = 2 * alpha * (theta_div_middle) / (numpy.linalg.norm(diff)**3) * b

		phi_div_middle = self.pfixed * (
			diff[1] * numpy.sin(p_theta) * numpy.cos(p_phi)
			- diff[0] * numpy.sin(p_theta) * numpy.sin(p_phi)
		)
		phi_div = 2 * alpha * (phi_div_middle) / (numpy.linalg.norm(diff)**3) * b

		r_divs = (-p / (numpy.linalg.norm(diff)**3) + 3 * p.dot(diff) * diff / (numpy.linalg.norm(diff)**5)) * 2 * alpha * b

		f2 = dot.f**2
		w2 = w**2

		w_div = alpha**2 * (1 / numpy.pi) * ((f2 - w2) / ((f2 + w2)**2))

		return numpy.concatenate((theta_div, phi_div, r_divs, w_div), axis=None)


@dataclass
class FixedMagnitudeDiscretisation():
	'''
	Representation of a discretisation of a FixedMagnitudeDiscretisation.
	Also captures a rough maximum value of dipole.

	Parameters
	----------
	model : FixedMagnitudeModel
		The parent model of the discretisation.
	num_ptheta: int
		The number of partitions of ptheta.
	num_pphi: int
		The number of partitions of pphi.
	num_x : int
		The number of partitions of the x axis.
	num_y : int
		The number of partitions of the y axis.
	num_z : int
		The number of partitions of the z axis.
	'''
	model: FixedMagnitudeModel
	num_ptheta: int
	num_pphi: int
	num_x: int
	num_y: int
	num_z: int

	def __post_init__(self):
		self.cell_count = self.num_x * self.num_y * self.num_z
		self.x_step = (self.model.xmax - self.model.xmin) / self.num_x
		self.y_step = (self.model.ymax - self.model.ymin) / self.num_y
		self.z_step = (self.model.zmax - self.model.zmin) / self.num_z
		self.h_step = 2 / self.num_ptheta
		self.phi_step = 2 * numpy.pi / self.num_pphi

	def bounds(self, index: Tuple[float, float, float, float, float]) -> Tuple:
		pthetai, pphii, xi, yi, zi = index

		# For this model, a point is (p_theta, p_phi, sx, sx, sy, w).
		# We want to keep w unbounded, restrict sx, sy, sz, px and py based on step.
		return (
			[
				numpy.arccos(1 - pthetai * self.h_step), pphii * self.phi_step,
				xi * self.x_step + self.model.xmin, yi * self.y_step + self.model.ymin, zi * self.z_step + self.model.zmin,
				-numpy.inf
			],
			[
				numpy.arccos(1 - (pthetai + 1) * self.h_step), (pphii + 1) * self.phi_step,
				(xi + 1) * self.x_step + self.model.xmin, (yi + 1) * self.y_step + self.model.ymin, (zi + 1) * self.z_step + self.model.zmin,
				numpy.inf
			]
		)

	def all_indices(self) -> numpy.ndindex:
		# see https://github.com/numpy/numpy/issues/20706 for why this is a mypy problem.
		return numpy.ndindex((self.num_ptheta, self.num_pphi, self.num_x, self.num_y, self.num_z))  # type:ignore

	def solve_for_index(self, dots: Sequence[DotMeasurement], index: Tuple[float, float, float, float, float]) -> scipy.optimize.OptimizeResult:
		bounds = self.bounds(index)
		ptheta_mean = (bounds[0][0] + bounds[1][0]) / 2
		pphi_mean = (bounds[0][1] + bounds[1][1]) / 2
		sx_mean = (bounds[0][2] + bounds[1][2]) / 2
		sy_mean = (bounds[0][3] + bounds[1][3]) / 2
		sz_mean = (bounds[0][4] + bounds[1][4]) / 2
		return self.model.solve(dots, initial_pt=numpy.array([ptheta_mean, pphi_mean, sx_mean, sy_mean, sz_mean, .1]), bounds=bounds)
