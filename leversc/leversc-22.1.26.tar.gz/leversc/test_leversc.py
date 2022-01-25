""" Python sample for using the leversc multichannel 3-d viewer
        mark winter and andrew r. cohen

        these routines show how to use the leversc class.
"""


import numpy as np, matplotlib.pyplot as plt
from leversc import leversc
import time
# if you have leverjs git repository on your path, add
# the environment variable PYTHONPATH=/path/to/leverjs.git/python 
# 

def setMovieUI(lsc):
    """ setMovieUI(lsc) - sets the ui elements for screen capture
            lsc - leversc class instance
    """
    # wait for leversc to finish any image render before we set ui
    # so all pending ui updates are completed before our changes
    while (not lsc1.drawComplete()):
        time.sleep(0.1)
    # pull ui dictionary, modify and then write it back
    # this allows us to properly use the property setter, and also allows 
    # bulk property changes
    ui=lsc.uiParams
    ui['webToolbar']='none'
    ui['clockButton']='none'
    ui['sidebar']='none'
    lsc.uiParams=ui

# show a random image 
# im = np.random.rand(1,50,512,1024)
# lsc1 = leversc(im=im)

# show the .LEVER sample image
strDB='../../sampleImages/lscSampleImage.LEVER'
(im,CONSTANTS)=leversc.readImage(strDB)
lsc1 = leversc(im=im,imD=CONSTANTS)

# capture a screen shot
# first, set ui. NOTE - read property, set it, write it back
# so setter properly updates it.'
setMovieUI(lsc1)
# now grab image
im=lsc1.captureImage()
# show image
plt.imshow(im)
plt.show()
# make movie, rotate, etc...
pass