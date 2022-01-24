import numpy as np




__all__ = ["add_mat","sub_mat","mul"]

def add_mat(a,b):
	if a.shape != b.shape:
		print("Shape Must Be Equal ")
	else:
		matrix = np.zeros(a.shape)
		for row in range(a.shape[0]):
			for col in range(a.shape[1]):
				matrix[row][col] = a[row][col] + b[row][col]

		return matrix



def sub_mat(a,b):
	if a.shape != b.shape:
		print("Shape Must Be Equal ")
	else:
		matrix = np.zeros(a.shape)
		for row in range(a.shape[0]):
			for col in range(a.shape[1]):
				matrix[row][col] = a[row][col] - b[row][col]

		return matrix



def mul(matrix,val):
	for row in range(matrix.shape[0]):
		for col in range(matrix.shape[1]):
			matrix[row][col] *= val 
	return matrix






