# A command line type example for using BIFS example

import numpy as np
import imageio
import random
from pylab import *
import matplotlib.pyplot as plt
import bifs
import bifs.bifs_util.util as bu

# 3D image
# Load image - sphere in 64x64x64 array
sphere_array_size = 32
sphere_radius = 12
my_slice = [0,0.5]
# import pymrt as mrt
# import pymrt.geometry
# im = mrt.geometry.sphere(sphere_array_size,sphere_radius, 0.5)
# im = np.asarray(im)
# 3D imag
# noise_level = 0.5
# noise = noise_level*(np.max(im) - np.min(im))*np.random.rand(im.shape[0],im.shape[1],im.shape[2])

# Add noise:
# noisy_im = im + noise

noisy_im = imageio.imread('../tests/images/test3Dnoisy_sphere.tiff')

# Create mybifs BIFS object:
mybifs = bifs.BIFS()

# Can take a look at what functions and variables are available with, e.g.:
# dir(mybifs)

# Set a few things:
# Prior
mybifs.prior = "Gaussian" # Choices are currently: "Gaussian","Uniform"
# "Gaussian" is actually the default but for illustration...

# Lilelihood
mybifs.likelihood = "Gaussian" # Choices are currently: "Gaussian","Rician" 
# "Gaussian" is actually the default but again for illustration...

# Parameter Space Function
mybifs.param_func_type = "Inverse Power Decay"
# Current choices are: "Inverse Power Decay","Banded Inverse Power Decay",
# "Linear Decay" with default "Inverse Power Decay",
# but again for illustration...

# Can check comments in bifs.py for description of other parametere to set

# Load the image - note, typically just start here re. loading a noisy image
mybifs.load_image(noisy_im)

# Run BIFS
mybifs.BIFS_MAP()

# Take a look at the parameter function
# NOTE: For a reason I don't yet understand
# running this and/or the following utility
# functions before running mybifs.BIFS_MAP()
# causes mybifs.BIFS_MAP() to crash horribly
# with a string of errors like:
#
# Break on __THE_PROCESS_HAS_FORKED_AND_YOU_CANNOT_USE_THIS_
# COREFOUNDATION_FUNCTIONALITY___YOU_MUST_EXEC__() to debug.
# The process has forked and you cannot use this CoreFoundation
# functionality safely. You MUST exec().
#
bu.plot_param_func(mybifs)

# Look at the prior, liklelihood, and posterior at a voxel
bu.voxel_dist(mybifs,[mybifs.mod_image().shape[0]//2,mybifs.mod_image().shape[1]//2,mybifs.mod_image().shape[2]//2],do_plots=True)
  
# Plot the resulting image
# Get slices from 3D data
slice_index = np.int(np.round(my_slice[1]*mybifs.init_image().shape[my_slice[0]]))
if my_slice[0] == 0:
    init_im_slice = mybifs.init_image()[slice_index,:,:]
    init_mod_im_slice = mybifs.mod_image()[slice_index,:,:]
    fin_im_slice = mybifs.final_image()[slice_index,:,:]
    fin_mod_im_slice = mybifs.bifsk_image()[slice_index,:,:]
elif my_slice[0] == 1:
    init_im_slice = mybifs.init_image()[:,slice_index,:]
    init_mod_im_slice = mybifs.mod_image()[:,slice_index,:]
    fin_im_slice = mybifs.final_image()[:,slice_index,:]
    fin_mod_im_slice = mybifs.bifsk_image()[:,slice_index,:]
elif my_slice[0] == 2:
    init_im_slice = mybifs.init_image()[:,:,slice_index]
    init_mod_im_slice = mybifs.mod_image()[:,:,slice_index]
    fin_im_slice = mybifs.final_image()[:,:,slice_index]
    fin_mod_im_slice = mybifs.bifsk_image()[:,:,slice_index]
else:
    print("Sorry slice index needs to be one of 0,1,2") 

plt.subplot(221)
plt.axis('off')
plt.title("Initial Image")
plt.imshow(init_im_slice, cmap = cm.Greys_r)
  
# Initial K-Space Image
plt.subplot(223)
plt.axis('off')
plt.title("Initial K-Space Image")
showim1k = np.roll(np.roll(init_mod_im_slice,init_mod_im_slice.shape[0]//2,0),init_mod_im_slice.shape[1]//2,1)
plt.imshow(np.log(showim1k), cmap = cm.Greys_r)
  
# Final K-Space Image after running BIFS
plt.subplot(224)
plt.axis('off')
plt.title("Final K-Space Image")
showim2k = np.roll(np.roll(fin_mod_im_slice,fin_mod_im_slice.shape[0]//2,0),fin_mod_im_slice.shape[1]//2,1)
plt.imshow(np.log(showim2k), cmap = cm.Greys_r)

# Final Image after running BIFS
plt.subplot(222)
plt.axis('off')
plt.title("Reconstructed Image")
plt.imshow(fin_im_slice, cmap = cm.Greys_r)

plt.show()
