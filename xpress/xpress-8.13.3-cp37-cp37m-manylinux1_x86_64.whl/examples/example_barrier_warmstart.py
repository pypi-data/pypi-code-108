# Example of the barstart functionality.
#
# (C) Fair Isaac Corp., 2020-2021

import xpress as xp

# Read and solve the first problem

ifdisk = True

p = xp.problem()

p.read('d2q06c.mps.gz')

p.controls.baralg = 2
p.controls.barstart = 1024
p.controls.crossover = 0

p.lpoptimize('b')

print ('First problem solved with status:', p.getProbStatusString())

if ifdisk:
    p.writeslxsol('mysol.slx', 'd')
else:
    x, s, d, r = [], [], [], []
    p.getlpsol(x, s, d, r)

# Read a slightly modified problem and solve it using the solution of
# p as a warm start.

p2 = xp.problem()

p2.read('d2q06c_mod.mps.gz')

p2.controls.baralg = 2

# This instructs barrier to use the available solution as warm-start.
p2.controls.barstart = -1

p2.controls.crossover = 0

if ifdisk:
    p2.readslxsol('mysol.slx')
else:
    p2.loadlpsol(x, s, d, r)

# Assign an emphasis to the warm-start (0.85 is the default). With a
# higher value, ther number of barrier iteration is even smaller.
# p2.controls.barstartweight = 0.9

p2.lpoptimize('b')

print ('Warm-started problem solved with status:', p2.getProbStatusString())
