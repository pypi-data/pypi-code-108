import numpy as np
import cv2
from typing import Tuple

def rescaleKps(kps:np.ndarray, originalScale:Tuple[int, int], newScale:Tuple[int, int]):
	assert len(originalScale) == 2 and len(originalScale) == len(newScale), "%s vs %s" % (originalScale, newScale)
	hRapp, wRapp = newScale[0] / originalScale[0], newScale[1] / originalScale[1]
	kps = np.float32(kps) * [hRapp, wRapp]
	kps = np.int32(kps)
	return kps

def frameKeypointer(image:np.ndarray, kps:np.ndarray, radiusPercent=1, color=(0, 0, 255)):
	assert len(kps.shape) == 2 and kps.shape[1] == 2
	assert image.dtype == np.uint8
	N = len(kps)
	H, W = image.shape[0], image.shape[1]
	image = image.copy()
	radius = max(1, int(min(H, W) * radiusPercent / 100))
	thickness = -1

	for i in range(N):
		kp_i, kp_j = kps[i]
		assert kp_i >= 0 and kp_i < H
		assert kp_j >= 0 and kp_j < W
		cv2.circle(image, (kp_i, kp_j), radius, color, thickness)
	return np.array(image)
