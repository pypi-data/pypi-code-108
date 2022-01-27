import numpy as np
import math
import SimpleITK as sitk

test_vector_out = '/home/neil/share/deformations_test/test_vector_def.nrrd'
test_vector_out_mhd = '/home/neil/share/deformations_test/test_vector_def.mhd'

def rotate_vector(vector, theta):
    theta = math.radians(theta)
    x_temp = float(vector[0])
    x = vector[0] * math.cos(theta) - vector[1] * math.sin(theta)
    y = x_temp * math.sin(theta) + vector[1] * math.cos(theta)
    return x, y

a = np.zeros(100*100*100*3).reshape((100, 100, 100, 3))
# Make a vector field of 2
a.fill(2)

# For each slice, rotate 45 degress
theta = -90
for y in range(a.shape[1]):
    theta += 90
    if theta > 360:
        theta = 0
    for z in range(a.shape[0]):
        for x in range(a.shape[2]):
            rotated = rotate_vector(a[z,y,x, [0,1]], theta)
            a[z, y, x,[0,1]] = rotated

out = sitk.GetImageFromArray(a)
sitk.WriteImage(out, test_vector_out)
sitk.WriteImage(out, test_vector_out_mhd)






