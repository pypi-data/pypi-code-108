import numpy as np
import cv2

rm = None

# Given a set of extremes (minW, maxW, minH, maxW), return a new set of smoothed keypoints that are also 
# rectangle, based on the center of the median differences.
# def vidSmoothExtremes(video, extremes):
def smoothBbox(bbox, M=10):
	assert len(bbox.shape) == 2 and bbox.shape[1] == 4

	x1, x2, y1, y2 = bbox.T

	# Based on all extremes, get the median frame and work with that
	centerX = (x1 + x2) // 2
	centerY = (y1 + y2) // 2
	# Get median of differences
	xMedian = np.median(x2 - x1)
	yMedian = np.median(y2 - y1)

	# Based on center +/- diffs, get the extremities of the bbox
	x1 = np.int32(centerX - xMedian // 2)
	x2 = np.int32(centerX + xMedian // 2)
	y1 = np.int32(centerY - yMedian // 2)
	y2 = np.int32(centerY + yMedian // 2)

	# Smooth the result further by doing a running mean with a 10 window
	Range = np.ones(M) / M
	l, r = M // 2, - M // 2 + (M % 2 == 0)
	x1[l : r] = np.convolve(x1, Range, mode="valid")
	x2[l : r] = np.convolve(x2, Range, mode="valid")
	y1[l : r] = np.convolve(y1, Range, mode="valid")
	y2[l : r] = np.convolve(y2, Range, mode="valid")

	# Fix the positions different than the median
	diffX = x2 - x1
	diffY = y2 - y1
	diffX = diffX - np.median(diffX)
	diffY = diffY - np.median(diffY)

	# Subtract the difference from the median to make it rectangle
	x2 -= np.int32(diffX)
	y2 -= np.int32(diffY)
	assert (x2 - x1).std() <= 1e-5
	assert (y2 - y1).std() <= 1e-5

	# Stack them back
	bbox = np.stack([x1, x2, y1, y2], axis=1).astype(np.int32)
	return bbox

# @brief Automatically get the padding of an image w.r.t the detected bounding box.
def imgGetBboxPadding(image:np.ndarray, bbox):
	x1, x2, y1, y2 = bbox
	H, W = image.shape[0 : 2]
	padding = x1, W - x2, y1, H - y2
	assert padding[0] >= 0 and padding[1] >= 0 and padding[2] >= 0 and padding[3] >= 0
	return np.array(padding)

def squareBbox(bbox):
	assert len(bbox) == 4, "left, right, up, down"
	x1, x2, y1, y2 = bbox

	# Force square by middle point
	xHalf = (x2 + x1) // 2
	yHalf = (y2 + y1) // 2
	biggestLine = max(y2 - y1, x2 - x1) // 2
	x1, x2, y1, y2 = xHalf - biggestLine, xHalf + biggestLine, yHalf - biggestLine, yHalf + biggestLine
	return x1, x2, y1, y2

def frameRectangler(image:np.ndarray, bbox):
	assert image.dtype == np.uint8
	assert len(bbox) == 4, "Expected: left, right, up, down. Got: %s" % bbox
	x1, x2, y1, y2 = bbox
	H, W = image.shape[0], image.shape[1]
	thickness = max(1, int(min(H, W) // 200))

	image = image.copy()
	image = cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 0), thickness)
	return np.array(image)

def padBbox(bbox, padding):
	assert len(bbox) == 4, "Expected: left, right, up, down. Got: %s" % bbox
	assert len(padding) == 4, "Expected: left, right, up, down. Got: %s" % padding

	x1, x2, y1, y2 = bbox
	x1 = x1 - padding[0]
	x2 = x2 + padding[1]
	y1 = y1 - padding[2]
	y2 = y2 + padding[3]
	return x1, x2, y1, y2

class TimeSmoothBbox:
	def __init__(self, T:int):
		self.rm = None
		self.T = T

	def __call__(self, bbox:np.ndarray):
		assert bbox.dtype == np.int, bbox.dtype
		if self.rm is None:
			self.rm = np.array(bbox, dtype=bbox.dtype)
		self.rm = ((self.rm * (self.T - 1) + bbox).astype(np.float32) / self.T).astype(bbox.dtype)
		return self.rm

