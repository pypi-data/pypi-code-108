import numpy
import operator
import logging


# flips px, py, pz
SIGN_ARRAY_7 = numpy.array((-1, -1, -1, 1, 1, 1, 1))
SIGN_ARRAY_4 = numpy.array((-1, 1, 1, 1))


_logger = logging.getLogger(__name__)


def flip_chunk_to_positive_px(pt: numpy.ndarray) -> numpy.ndarray:
	if pt[0] > 0:
		return pt
	else:
		# godawful hack.
		if len(pt) == 7:
			return SIGN_ARRAY_7 * pt
		elif len(pt) == 4:
			return SIGN_ARRAY_4 * pt
		else:
			_logger.warning(f"Could not normalise pt: {pt}. Returning as is...")
			return pt


def normalise_point_list(pts: numpy.ndarray, pt_length) -> numpy.ndarray:
	chunked_pts = [flip_chunk_to_positive_px(pts[i: i + pt_length]) for i in range(0, len(pts), pt_length)]
	range_to_length = list(range(pt_length))
	rotated_range = range_to_length[pt_length - 1:] + range_to_length[0:pt_length - 1]
	return numpy.concatenate(sorted(chunked_pts, key=lambda x: tuple(round(val, 3) for val in operator.itemgetter(*rotated_range)(x))), axis=None)
