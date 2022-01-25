"""
This small example loads the cells3d dataset from scikit-image into LEVERSC for visualization
"""
import numpy as np
from skimage.data import cells3d

import leversc

# Load the cells3d dataset
cells = cells3d()
# Rearrange the dimensions to be in expected order (c,z,y,x) for row-major numpy array
cellsC = np.copy(np.transpose(cells,[1,0,2,3]), order='C')

# Set up the image metadata: such as physical voxel size, and channel names
# See: https://scikit-image.org/docs/0.18.x/api/skimage.data.html?highlight=cells3d#skimage.data.cells3d
imD = {"PixelPhysicalSize": [0.29,0.26,0.26],
    "ChannelNames": ["Membrane","Nuclei"]}
# Send data to the LEVERSC viewer
lsc = leversc.leversc(im=cellsC, imD=imD)
