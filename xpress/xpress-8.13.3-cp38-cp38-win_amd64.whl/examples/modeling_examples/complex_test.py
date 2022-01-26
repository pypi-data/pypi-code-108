'''******************************************************
   Python NI Examples

   file complex_test.py
   Testing the complex module

   (c) 2018 Fair Isaac Corporation
 *******************************************************'''

from __future__ import print_function
import numpy as np

# Initialize some complex numbers (native in Python)
t = [complex(j, 10-j) for j in range(1, 11)]
t[5] = 5+5j

# Aggregate PROD operator
c = np.prod(np.array(t[:5]))
if c != 0:
    print("test prod: ", c)

# Aggregate SUM operator
print("test sum:", sum(t))

# Using arithmetic operators
if t[1] == 0:
    c0 = t[9]
else:
    c0 = t[7]
c = t[0] * t[2] / t[3] + c0 + t[3] - t[8]
print("test op:", c)

f = open('complex_test.dat', 'w')
print(c, t, file=f)
f.close()
