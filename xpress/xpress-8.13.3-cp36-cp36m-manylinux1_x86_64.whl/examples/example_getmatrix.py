# Example to show how to retrieve the coefficient matrix from a
# problem.
#
# (C) Fair Isaac Corp., 1983-2021

import xpress as xp
import scipy.sparse

p = xp.problem()

p.read('prob1.lp')

# Obtain matrix representation of the coefficient matrix for problem.
# Restrict to one million coefficients.

coef, ind, beg = [], [], []

p.getrows(beg, ind, coef, 1000000, 0, p.attributes.rows - 1)

# The function getrows() provides a richer output by filling up ind
# not with numerical indices but with the Python objects
# (i.e. Xpress variables) corresponding to the variable
# indices. Convert them to numerical indices using the getIndex()
# function.

ind_n = [p.getIndex(v) for v in ind]

# Create a Compressed Sparse Row (CSR) format matrix using the data
# from getrows plus the numerical indices.

A = scipy.sparse.csr_matrix((coef, ind_n, beg))

# Convert the CSR matrix to a NumPy array of arrays, so that each row
# is a (non-compressed) array.

M = A.toarray()

print(A)
print(M)

b, c = [], []

p.getobj(c, 0, p.attributes.cols - 1)
p.getrhs(b, 0, p.attributes.rows - 1)

print(b)
print(c)
