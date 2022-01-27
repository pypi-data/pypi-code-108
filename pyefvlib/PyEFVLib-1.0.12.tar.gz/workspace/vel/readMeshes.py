import PyEFVLib
import time

# for meshName in ["Square.msh"]:
# for meshName in ["M1.msh","M2.msh","M3.msh"]:
# for meshName in ["M1.msh","M2.msh"]:
for meshName in ["M2.msh"]:
	t0 = time.time()
	grid = PyEFVLib.read(meshName)
	t1 = time.time()
	print(meshName, t1-t0)