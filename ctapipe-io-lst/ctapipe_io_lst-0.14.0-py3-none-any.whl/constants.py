import numpy as np

N_GAINS = 2
N_MODULES = 265
N_PIXELS_MODULE = 7
N_PIXELS = N_MODULES * N_PIXELS_MODULE
N_CAPACITORS_CHANNEL = 1024
# 4 drs4 channels are cascaded for each pixel
N_CAPACITORS_PIXEL = 4 * N_CAPACITORS_CHANNEL
N_SAMPLES = 40
HIGH_GAIN = 0
LOW_GAIN = 1
LAST_RUN_WITH_OLD_FIRMWARE = 1574
CLOCK_FREQUENCY_KHZ = 133e3

# we have 8 channels per module, but only 7 are used.
N_CHANNELS_MODULE = 8

# First capacitor order according Dragon v5 board data format
CHANNEL_ORDER_HIGH_GAIN = [0, 0, 1, 1, 2, 2, 3]
CHANNEL_ORDER_LOW_GAIN = [4, 4, 5, 5, 6, 6, 7]

PIXEL_INDEX = np.arange(N_PIXELS)
