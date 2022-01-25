
# from leversc.test_random import test_random 
def test_random():
    import numpy as np
    from leversc import leversc

    imRandom = np.random.random_sample((256,256,256))
    # Set up the image metadata: such as physical voxel size, and channel names
    # See: https://scikit-image.org/docs/0.18.x/api/skimage.data.html?highlight=cells3d#skimage.data.cells3d
    imD = {"PixelPhysicalSize": [0.29,0.26,0.26],
        "ChannelNames": ["random_sample"]}
    # Send data to the LEVERSC viewer
    leversc.leversc(im=imRandom, imD=imD)
    pass