# Compare matrix coefficients of two problems
#
# Given two problems with the same number of variables, read their
# coefficient matrices into Scipy so as to compare each row for
# discrepancies in the coefficients.
#
# (C) Fair Isaac Corp., 1983-2021

from __future__ import print_function

import xpress as xp
import scipy.sparse

p1 = xp.problem()
p2 = xp.problem()

# Read problems from file. Works also with problems created with the
# modeling features of the Python interface.

p1.read('prob1.lp')
p2.read('prob2.lp')

# Obtain matrix representation of the coefficient matrix for both
# problems. Restrict to one million coefficients.

coef1, ind1, beg1 = [], [], []
coef2, ind2, beg2 = [], [], []

p1.getrows(beg1, ind1, coef1, 1000000, 0, p1.attributes.rows - 1)
p2.getrows(beg2, ind2, coef2, 1000000, 0, p2.attributes.rows - 1)

# The function getrows() provides a richer output by filling up ind1
# and ind2 not with numerical indices but with the Python objects
# (i.e. Xpress variables) corresponding to the variable
# indices. Convert them to numerical indices using the getIndex()
# function.

ind1n = [p1.getIndex(v) for v in ind1]
ind2n = [p2.getIndex(v) for v in ind2]

# Create a Compressed Sparse Row (CSR) format matrix using the data
# from getrows plus the numerical indices.

A1 = scipy.sparse.csr_matrix((coef1, ind1n, beg1))
A2 = scipy.sparse.csr_matrix((coef2, ind2n, beg2))

# Convert the CSR matrix to a NumPy array of arrays, so that each row
# is a (non-compressed) array to be compared in the loop below.

M1 = A1.toarray()
M2 = A2.toarray()

for i in range(min(p1.attributes.rows, p2.attributes.rows)):
    print(M1[i] != M2[i])
