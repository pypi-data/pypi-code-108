# New hidden test
import numpy as np
import mccd
import mccd.auxiliary_fun as mccd_aux
from astropy.io import fits

import random

import matplotlib.pyplot as plt
import matplotlib as mpl
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.colors import ListedColormap, LinearSegmentedColormap


print(mccd.__version__)

plt.rc('text', usetex=True)
font = {'family' : 'serif',
        'weight' : 'bold',
        'size'   : 20}
mpl.rc('font', **font)

plot_style = {
                'figure.figsize': (6,6),
                'figure.dpi': 100,
                'figure.autolayout':True,
                'lines.linewidth': 4,
                'lines.linestyle': '-',
                'lines.marker': 'o',
                'lines.markersize': 10,
                'legend.fontsize': 20,
                'legend.loc': 'best',
                'axes.titlesize': 24,
                'axes.grid': False,
                'axes.grid.which': 'major',
                'axes.grid.axis': 'both'}
mpl.rcParams.update(plot_style)

def plot_fun(star_img, cmap='gist_stern'):
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    im1 = ax1.imshow(star_img, interpolation='None',cmap=cmap)
    divider = make_axes_locatable(ax1)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    cbar = fig.colorbar(im1, cax=cax, extend='both')
    cbar.minorticks_on()
    fig.tight_layout()
    ax1.set_xticks([]);ax1.set_yticks([])
    ax1.axis('off')
    plt.show()

loc2glob = mccd.mccd_utils.Loc2Glob()

# Pre-defined colormap
top = mpl.cm.get_cmap('Oranges_r', 128)
bottom = mpl.cm.get_cmap('Blues', 128)
newcolors = np.vstack((top(np.linspace(0, 1, 128)),
                       bottom(np.linspace(0, 1, 128))))
newcmp = ListedColormap(newcolors, name='OrangeBlue')

def plot_ccds_fun(positions,mom,title):
    fig = plt.figure(figsize=(8, 8))
    ax1 = fig.add_subplot(111)
    for ccd_it in range(40):
        xs,ys = loc2glob.shift_coord(ccd_it)
        rect = mpl.patches.Rectangle((xs,ys),2048,4612,linewidth=1,edgecolor='r',facecolor='none')
        ax1.add_patch(rect)

    im1 = ax1.scatter(positions[:, 0], positions[:, 1], s=5,c=mom, marker='*', cmap=newcmp)
    divider = make_axes_locatable(ax1)
    cax = divider.append_axes('right', size='5%', pad=0.05)
    fig.colorbar(im1, cax=cax, orientation='vertical')
    ax1.set_xticks([]);ax1.set_yticks([])
    ax1.axis('off')
    ax1.set_title(title)
    plt.show()


input_pos_path = './../../data/sim_inputs/train_positions.npy'
input_ccd_path = './../../data/sim_inputs/train_ccd_list.npy'
output_path = './../../data/OLD_mccd_inputs/'


sim_dataset_generator = mccd_aux.GenerateSimDataset(input_pos_path, input_ccd_path, output_path)

sim_dataset_generator.load_data()
# Posibility to define the simulation parameters
sim_dataset_generator.generate_train_data()  # Using default parameters
# Defining the testing grid
sim_dataset_generator.generate_test_data(x_grid=4, y_grid=4)

# Get the dataset paths
ext = '.fits'
catalog_id = sim_dataset_generator.catalog_id

train_cat_path = output_path + 'train_star_selection-' + str(catalog_id) + ext
test_cat_path = output_path + 'test_star_selection-' + str(catalog_id) + ext

train_cat = fits.open(train_cat_path)[1]
pos = train_cat.data['GLOB_POSITION_IMG_LIST']


# Load the data
train_cat = fits.open(train_cat_path)

# Extract the data from the fits catalog
positions = np.copy(train_cat[1].data['GLOB_POSITION_IMG_LIST'])
stars = np.copy(train_cat[1].data['VIGNET_LIST'])
ccds = np.copy(train_cat[1].data['CCD_ID_LIST']).astype(int)
ccds_unique = np.unique(np.copy(train_cat[1].data['CCD_ID_LIST'])).astype(int)
# Generate the masks
masks = mccd.utils.handle_SExtractor_mask(stars,thresh=-1e5)

# Generate the list format needed by the MCCD package
pos_list = [positions[ccds == ccd] for ccd in ccds_unique]
star_list = [mccd.utils.rca_format(stars[ccds == ccd]) for ccd in ccds_unique]
mask_list = [mccd.utils.rca_format(masks[ccds == ccd]) for ccd in ccds_unique]
ccd_list = [ccds[ccds == ccd].astype(int) for ccd in ccds_unique]
ccd_list = [np.unique(_list)[0].astype(int) for _list in ccd_list]
SNR_weight_list = None  # We wont use any weighting technique as the SNR is constant over the Field of View

# Parameters

# MCCD instance
n_comp_loc = 8
d_comp_glob = 8
filters = None
ksig_loc = 1.
ksig_glob = 1.

# MCCD fit
psf_size = 6.15
psf_size_type = 'R2'
n_eigenvects = 5
n_iter_rca = 1
nb_iter_glob = 1  # 2
nb_iter_loc = 1  # 2
nb_subiter_S_loc = 1  # 100
nb_subiter_A_loc = 1  # 500
nb_subiter_S_glob = 1  # 30
nb_subiter_A_glob = 1  # 200
loc_model = 'hybrid'


# Build the paramter dictionaries
mccd_inst_kw = {'n_comp_loc': n_comp_loc, 'd_comp_glob': d_comp_glob,
                'filters': filters,       'ksig_loc': ksig_loc,
                'ksig_glob':ksig_glob}

mccd_fit_kw = {'psf_size': psf_size,                  'psf_size_type':psf_size_type,
              'n_eigenvects': n_eigenvects,          'nb_iter':n_iter_rca,
              'nb_iter_glob':nb_iter_glob,           'nb_iter_loc':nb_iter_loc,
              'nb_subiter_S_loc':nb_subiter_S_loc,   'nb_subiter_A_loc':nb_subiter_A_loc,
              'nb_subiter_S_glob':nb_subiter_S_glob, 'nb_subiter_A_glob':nb_subiter_A_glob,
              'loc_model':loc_model}

# Instanciate the class
mccd_instance = mccd.MCCD(**mccd_inst_kw, verbose=False)
# Launch the training
S, A_loc, A_glob, alpha, pi = mccd_instance.fit(star_list, pos_list, ccd_list, mask_list,
                                                SNR_weight_list, **mccd_fit_kw)

fitted_model_path = output_path + '/fitted_model' + str(catalog_id)
mccd_instance.quicksave(fitted_model_path)
