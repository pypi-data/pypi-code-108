from dataclasses import dataclass
import numpy
import numpy.typing


@dataclass
class DotMeasurement():
	'''
	Representation of a dot measuring oscillating dipoles.

	Parameters
	----------
	v : float
		The voltage measured at the dot.
	r : numpy.ndarray
		The position of the dot.
	f : float
		The measurement frequency.
	'''
	v: float
	r: numpy.ndarray
	f: float

	def __post_init__(self) -> None:
		self.r = numpy.array(self.r)
