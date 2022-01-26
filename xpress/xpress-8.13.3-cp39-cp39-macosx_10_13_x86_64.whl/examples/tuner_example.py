import xpress as xp

# Creates a problem and read a MIPLIB2010 instance

p = xp.problem()
p.read('miplib-rndinst.mps.gz')

# Create a file default-MIP.xtm with the tuner options that are tested
# by default by the tuner. The file has the following format: a
# section with controls that are applied to each tuner run
# ("FIXED-CONTROLS") and a set of controls that are tested
# independently by the tuner ("TUNABLE-CONTROLS"). Tunable controls
# have each one or more value that the tuner will test, first
# independently and then in combination with others.
#
# FIXED-CONTROLS
#   OUTPUTLOG            = 1
#   XSLP_POSTSOLVE       = 1
#   XSLP_DELETIONCONTROL = 0
# TUNABLE-CONTROLS
#   BRANCHDISJ           = 0
#   COVERCUTS            = 0, 2, 20
#   CUTFACTOR            = 0.5, 1, 5
#   CUTFREQ              = 2
# 
# ... and others. The file is written AFTER reading in the problem in order
# for the optimizer to recognize that it is a MIP.

p.tunerwritemethod('default-MIP.xtm')

# Set the total amount of time the tuner can spend in tuning
# (tunermaxtime) and the time limit for each run. The negative sign
# allows for stopping even if no integer solution was found.
p.controls.tunermaxtime = 100
p.controls.maxtime = -10

# Tune the optimizer on the problem
p.tune('g')

# Now try tuning on a different tuner method: the file mymethod.xtm
# contains slightly different combination of controls and values, and
# the tuner will test different combinations this way. Note that the
# output will show that the Optimizer finds old tuner runs and will
# use the relative information
p.tunerreadmethod('mymethod.xtm')
p.tune()

# Finally, before solving the problem, increase the time limit.
p.controls.maxtime = -1000

p.solve()
