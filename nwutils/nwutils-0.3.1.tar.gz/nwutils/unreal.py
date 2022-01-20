# unreal_utils.py Various utility functions w.r.t Unreal Engine for data processing and whatnot
import numpy as np

# @brief Gets a float value stored as PNG from Unreal simulator
def unrealFloatFromPng(x:np.ndarray) -> np.ndarray:
	x = x.astype(np.float32)
	x = (x[..., 0] + x[..., 1] * 256 + x[..., 2] * 256 * 256) / (256 * 256 * 256 - 1)
	x = x.astype(np.float32)
	return x

# @brief Converts a float32 value to 24 bit RGB similar to the ones exported by Unreal Engine
def unrealPngFromFloat(x:np.ndarray, equalCheck:bool=True) -> np.ndarray:
	assert x.dtype == np.float32
	y = np.int32(x * (256 * 256 * 256 - 1))
	# Shrink any additional bits outside of 24 bits
	y = y & (256 * 256 * 256 - 1)
	R = y & 255
	G = (y >> 8) & 255
	B = (y >> 16) & 255
	result = np.array([R, G, B], dtype=np.uint8).transpose(1, 2, 0)

	if equalCheck:
		checkBack = unrealFloatFromPng(result)
		assert np.allclose(x, checkBack)
	return result