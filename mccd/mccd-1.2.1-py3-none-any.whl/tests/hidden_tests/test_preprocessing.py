import numpy as np
import mccd.auxiliary_fun as mccd_aux
import mccd.mccd_utils as mccd_utils
import mccd
from astropy.io import fits

import random

import matplotlib.pyplot as plt
import matplotlib as mpl
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.colors import ListedColormap, LinearSegmentedColormap

sex_input_path = './../../data/sextractor_inputs/'
mccd_input_path = './../../data/sextractor_preprocessed/'
output_path = './../../data/outputs/'

input_path = sex_input_path
min_n_stars = 20
output_path
file_pattern = 'sexcat-*-*.fits'
separator = '-'
save_masks = False
CCD_id_filter_list = None
verbose = True

if CCD_id_filter_list is None:
    CCD_id_filter_list = np.arange(40)

# -------------------------- #
# Preprocess
mccd_star_nb = 0

mccd_inputs = mccd_utils.MccdInputs(separator=separator)
if verbose:
    print('Processing dataset..')
catalog_ids = mccd_inputs.preprocess_data(folder_path=input_path,
                                          pattern=file_pattern)

print('Hello')