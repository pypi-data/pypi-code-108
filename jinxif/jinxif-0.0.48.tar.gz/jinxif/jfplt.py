#####
# title: jfplt.py
#
# language: python3
# author: Jenny, bue
# license: GPLv>=3
# date: 2021-04-00
#
# description:
#     jinxif python3 library to generate output for quality control
#####


# library
import matplotlib.pyplot as plt
import numpy as np
import os
from skimage import io, exposure

# development
#import importlib
#importlib.reload()


# generic function
# BUE 20210430: maybe core can be fused with array_roi?
def array_img_scatter(
        df_img,
        s_xlabel = 'marker',
        ls_ylabel = ['exposure','color'],  # ['markers','color']
        s_title = 'round',
        s_title_main = 'slide_scene', # slide_mscene
        ti_array = (2,4),
        ti_fig = (8,11),
        cmap = 'gray',
        s_pathfile = './array_img_scatter.png',
    ):
    '''
    version: 2021-12-00
    BUE: internal function, but there is a mpimage.array_roi, mpimage.array_roi_if, mpimage.roi_if_border too.

    input:
        df_img: image metadata datafarme, indexed by filenames, index.name is the path.
        s_xlabel: subplot x label, which have to be a df_img column label.
        ls_ylabel: subplot y labels, which have to be df_img column labels.
        s_title: subplot title, which have to be a df_img column label.
        s_title_main: whole figure title, which have to be a df_img column label.
        ti_array: x,y image grid parameter.
        ti_fig: x,y figure size parameter in inch.
        cmap: matplotlib color map name.
        s_pathfile: string to specify output path and filename.

    output:
        fig: matplotlib figure.

    description:
        generate a grid of scatter plot images.
    '''
    # generate figure
    fig, ax = plt.subplots(ti_array[0], ti_array[1], figsize=ti_fig)
    ax = ax.ravel()
    s_suptitle_label = str(sorted(df_img.loc[:, s_title_main].unique()))
    for i_ax, s_index in enumerate(df_img.index):

        # generate subplot labels
        s_row_label = f'{df_img.loc[s_index, ls_ylabel[0]]}\n {df_img.loc[s_index, ls_ylabel[1]]}'
        s_col_label = df_img.loc[s_index, s_xlabel]
        s_title_label = df_img.loc[s_index, s_title]

        # load, rescale and crop subplot image
        a_image = io.imread(f'{df_img.index.name}{s_index}')
        i_rescale_max = int(np.ceil(1.5 * np.quantile(a_image, 0.98)))
        a_rescale = exposure.rescale_intensity(a_image, in_range=(0, i_rescale_max))
        #i_rescale_max = a_image.max()
        #a_rescale = a_image

        # generate subplot
        ax[i_ax].imshow(a_rescale, cmap=cmap)
        ax[i_ax].set_ylabel(s_row_label)
        ax[i_ax].set_xlabel(f'{s_col_label}\n 0 - {i_rescale_max}[px intensity]')
        ax[i_ax].set_title(s_title_label)

    # erase empty ax
    for i_ax in range(df_img.shape[0], len(ax)):
        ax[i_ax].axis('off')

    # title
    fig.suptitle(s_suptitle_label)

    # output figure
    plt.tight_layout()
    s_path = '/'.join(s_pathfile.replace('\\','/').split('/')[:-1])
    os.makedirs(s_path, exist_ok=True)
    fig.savefig(s_pathfile, facecolor='white')
    plt.close()
    print(f'save plot: {s_pathfile}')

