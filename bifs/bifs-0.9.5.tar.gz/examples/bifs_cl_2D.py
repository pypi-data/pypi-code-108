# A command line type example for using BIFS example

import numpy as np
import imageio
import random
from pylab import *
import matplotlib.pyplot as plt
import bifs
import bifs.bifs_util.util as bu

# 2D image
# Load image - standard Lena for now
im = imageio.imread('../tests/images/lena512.bmp')
im = np.asarray(im)
# 2D imag
noise_level = 1.5
noise = noise_level*(np.max(im) - np.min(im))*np.random.rand(im.shape[0],im.shape[1])

# Add noise:
noisy_im = im + noise

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
# mybifs.param_func_type = "Linear Decay"
# mybifs.bvec = np.array([0.1,500.])
mybifs.param_func_type = "Inverse Power Decay"
# mybifs.decay = 0.5
# Current choices are: "Inverse Power Decay","Banded Inverse Power Decay",
# "Linear Decay" with default "Inverse Power Decay",
# but again for illustration...

# Try adding a bump
# mybifs.bumps = {mybifs.bump_default_type:[0.5,0.05,0.1]}

# Can check comments in bifs.py for description of other parametere to set

# Load the image - note, typically just start here re. loading a noisy image
mybifs.load_image(noisy_im)

# Run BIFS MAP
print("Running BIFS_MAP() on image")
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
# bu.plot_param_func(mybifs)
  
# Look at the prior, liklelihood, and posterior at a voxel
bu.voxel_dist(mybifs,[mybifs.mod_image().shape[0]//2,mybifs.mod_image().shape[1]//2],do_plots=True)

# Plot the resulting images
# Initial noisy image
plt.subplot(221)
plt.axis('off')
plt.title("Initial Image")
plt.imshow(mybifs.init_image(), cmap = cm.Greys_r)
  
# Initial K-Space Image
plt.subplot(222)
plt.axis('off')
plt.title("Initial K-Space Image")
showim1k = np.roll(np.roll(mybifs.mod_image(),mybifs.mod_image().shape[0]//2,0),mybifs.mod_image().shape[1]//2,1)
plt.imshow(np.log(showim1k), cmap = cm.Greys_r)
             
# Final K-Space Image after running BIFS
plt.subplot(224)
plt.axis('off')
plt.title("Initial K-Space Image")
showim2k = np.roll(np.roll(mybifs.bifsk_image(),mybifs.bifsk_image().shape[0]//2,0),mybifs.bifsk_image().shape[1]//2,1)
plt.imshow(np.log(showim2k), cmap = cm.Greys_r)
             
# Final Image after running BIFS
plt.subplot(223)
plt.axis('off')
plt.title("Reconstructed Image")
plt.imshow(mybifs.final_image(),cmap = cm.Greys_r)

plt.show()
