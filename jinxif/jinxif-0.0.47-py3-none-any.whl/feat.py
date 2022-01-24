####
# title: feat.py
#
# language: Python3.8
# date: 2020-06-00
# license: GPL>=v3
# author: Jenny, bue
#
# description:
#   python3 script for single cell feature extraction
####

# libraries
import gc
from jinxif import config
from jinxif import basic
from jinxif import thresh
import json
#import matplotlib as mpl
#mpl.use('agg')
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import re
import scipy
import shutil
from skimage import io, measure, morphology, segmentation
import subprocess
import sys
import time

# PIL is backend from skimage io
# against DecompressionBombError: Image size (n pixels) exceeds limit of 178956970 pixels, could be decompression bomb DOS attack.
import PIL
PIL.Image.MAX_IMAGE_PIXELS = None

# development
#import importlib
#importlib.reload()

# global var
s_path_module = os.path.abspath(os.path.dirname(__file__))
s_path_module = re.sub(r'jinxif$','jinxif/', s_path_module)


# functions

########################################################################
# segmentation partition and marker intensity based feature extraction #
########################################################################

def _extract_feat(
        ai_labels,
        ai_intensity_image,
        ls_properties = ['centroid','mean_intensity','area','eccentricity','euler_numer']
    ):
    '''
    version: 2021-12-00
    used

    input:
        ai_labels: numpy array with integer cell labels.
        ai_intensity_image: numpy array with intensity values.
        ls_properties: list of properties to extract with measure.regionprops_table.

    output:
        df_prop: dataframe with the extracted features, here called properties.

    description:
        given labels and intensity image, extract features to dataframe

    bue 20210807: _extract_feat eats a lot of memory.
    maybe less when I call the function for each property separately?
    '''
    d_props = measure.regionprops_table(
        label_image = ai_labels,
        intensity_image = ai_intensity_image,
        properties = ls_properties
    )
    df_prop = pd.DataFrame(d_props)
    return(df_prop)


def _mem_label(
        ai_labels,
        i_distance = 2,
    ):
    '''
    version: 2021-12-00

    input:
        ai_labels: numpy array with integer cell labels.
        i_distance: integer distance of pixels the cells should be shrunken.

    output:
        ai_rim_labels: numpy array with cell labels defining the shrunken rim.
            this is the membrane towards the inside.

    description:
        contract the nucleus or cell labels by a fixed number of pixels.
        this function gives the shrunken rim back.
        this function is used to generate the mem partitions.
    '''
    ai_shrunk_labels = ai_labels.copy()
    ab_boundaries = segmentation.find_boundaries(ai_labels, mode='outer')
    ai_shrunk_labels[ab_boundaries] = 0
    ab_foreground = ai_shrunk_labels != 0
    ar_distances, (ai_i, ai_j) = scipy.ndimage.distance_transform_edt(
        ab_foreground,
        return_indices=True,
    )
    ab_mask = ab_foreground & (ar_distances <= i_distance)
    ai_shrunk_labels[ab_mask] = ai_shrunk_labels[ai_i[ab_mask], ai_j[ab_mask]]
    ai_mem_labels = ai_labels - ai_shrunk_labels
    return(ai_mem_labels)


def _adj_label(
        ai_labels,
        i_distance = 2,
    ):
    '''
    version: 2021-12-00

    input:
        ai_labels: numpy array with integer cell labels.
        i_distance: integer distance of pixels the cells should be straddled.

    output:
        ai_adj_labels: numpy array with membranes label.

    description:
        expand and contract nucleus or cell labels by a fixed number of pixels.
        this function gives band object i_distant left and right from the border back.
        this function is used to generate the adj partitions.
    '''
    ai_shrunk_labels = ai_labels.copy()
    ai_grown_labels = ai_labels.copy()
    ab_boundaries = segmentation.find_boundaries(ai_labels, mode='outer')
    ai_shrunk_labels[ab_boundaries] = 0
    ab_foreground = ai_shrunk_labels != 0
    ab_background = ai_shrunk_labels == 0
    ar_distances_f, (ai_i, ai_j) = scipy.ndimage.distance_transform_edt(
        ab_foreground,
        return_indices = True
    )
    ar_distances_b, (ai_i, ai_j) = scipy.ndimage.distance_transform_edt(
        ab_background,
        return_indices=True
    )
    ab_mask_f = ab_foreground & (ar_distances_f <= i_distance)
    ab_mask_b = ab_background & (ar_distances_b <= i_distance + 1)
    ai_shrunk_labels[ab_mask_f] = 0
    ai_grown_labels[ab_mask_b] = ai_grown_labels[ai_i[ab_mask_b], ai_j[ab_mask_b]]
    ai_adj_labels = ai_grown_labels - ai_shrunk_labels
    #ai_adj_labels = ai_grown_labels[ai_grown_labels != ai_shrunk_labels]
    return(ai_adj_labels)


def _peri_label(
        ai_labels,
        i_distance = 5,
    ):
    '''
    version: 2021-12-00

    input:
        ai_labels: numpy array with integer cell labels.
        i_distance: integer distance of pixels the cells should be expanded.

    output:
        ai_peri_labels: numpy array with cell labels defining the grown rim.

    description:
        expand the nucleus or cell labels by a fixed number of pixels
        this function gives the grown rim object back.
        this function is used to generate the perinuc partitions.
    '''
    ai_shrunk_labels = ai_labels.copy()
    ab_boundaries = segmentation.find_boundaries(ai_labels, mode='outer') #thick
    ai_shrunk_labels[ab_boundaries] = 0
    ab_background = ai_shrunk_labels == 0
    ar_distances, (ai_i, ai_j) = scipy.ndimage.distance_transform_edt(
        ab_background,
        return_indices=True,
    )
    ai_grown_labels = ai_labels.copy()
    ab_mask = ab_background & (ar_distances <= i_distance)
    ai_grown_labels[ab_mask] = ai_shrunk_labels[ai_i[ab_mask], ai_j[ab_mask]]
    ai_peri_labels = ai_grown_labels - ai_shrunk_labels
    #ai_peri_labels = ai_grown_labels[ai_grown_labels != ai_shrunk_labels]
    return(ai_peri_labels)


def _exp_label(
        ai_labels,
        i_distance = 5,
    ):
    '''
    version: 2021-12-00

    input:
        ai_labels: numpy array with integer cell labels.
        i_distance: integer distance of pixels the cells should be expanded.

    output:
        ai_ring_labels: numpy array with cell labels defining the grown rim.
        ai_exp_labels: numpy array with cell labels defining the whole grown cell.

    description:
        expand the nucleus or cell labels by a fixed number of pixels
        this function gives the grown object back!
        this function is used to generate the exp partitions.
    '''
    ai_shrunk_labels = ai_labels.copy()
    ab_boundaries = segmentation.find_boundaries(ai_labels, mode='outer') #thick
    ai_shrunk_labels[ab_boundaries] = 0
    ab_background = ai_shrunk_labels == 0
    ar_distances, (ai_i, ai_j) = scipy.ndimage.distance_transform_edt(
        ab_background,
        return_indices=True,
    )
    ai_exp_labels = ai_labels.copy()
    ab_mask = ab_background & (ar_distances <= i_distance)
    ai_exp_labels[ab_mask] = ai_shrunk_labels[ai_i[ab_mask], ai_j[ab_mask]]
    return(ai_exp_labels)


def _shrink_label(
        ai_labels,
        i_distance = 2,
    ):
    '''
    version: 2021-12-00

    input:
        ai_labels: numpy array with integer cell labels.
        i_distance: integer distance of pixels the cells should be shrunken.

    output:
        ai_rim_labels: numpy array with cell labels defining the shrunken rim.

    description:
        contract labels by a fixed number of pixels.
        function gives the shrunken object back!
    '''
    ai_shrunk_labels = ai_labels.copy()
    ab_boundaries = segmentation.find_boundaries(ai_labels, mode='outer')
    ai_shrunk_labels[ab_boundaries] = 0
    ab_foreground = ai_shrunk_labels != 0
    ar_distances, (ai_i, ai_j) = scipy.ndimage.distance_transform_edt(
        ab_foreground,
        return_indices=True,
    )
    ab_mask = ab_foreground & (ar_distances <= i_distance)
    ai_shrunk_labels[ab_mask] = ai_shrunk_labels[ai_i[ab_mask], ai_j[ab_mask]]
    return(ai_shrunk_labels)


#def _label_difference(
def _cell_sub_nuc_label(
        ai_nuc_labels,
        ai_cell_labels,
    ):
    '''
    version: 2021-12-00

    input:
        ai_nuc_labels: numpy array with integer nucleus labels.
        ai_cell_labels: numpy array with integer whole cell labels.

    output:
        ai_ring_rep: numpy array with integer cytoplasm cell labels.

    description:
        given matched nuclear and cell label IDs,
        return cell_labels minus nuc_labels.
    '''
    ab_overlap = ai_cell_labels == ai_nuc_labels
    ai_ring_rep = ai_cell_labels.copy()
    ai_ring_rep[ab_overlap] = 0
    return(ai_ring_rep)


def extract_features(
        s_slide,
        es_seg_marker,
        i_exp = 5,  # number of pixel for cytoplasm doughnut. microscope dependent!
        i_mem = 2,  # number of pixel for membrane. microscope dependent!
        i_shrink = 0,  # optional, patching against bleed trough.
        # specify input and output directory
        s_afsubdir = config.d_nconv['s_regdir'],  #'SubtractedRegisteredImages/', or 'RegisteredImages/'
        s_format_afsubdir = config.d_nconv['s_format_regdir'],  #'{}{}/',  # s_afsubdir, s_slide_pxscene
        s_segdir = config.d_nconv['s_segdir'],  #'Segmentation/',
        s_format_segdir_cellpose = config.d_nconv['s_format_segdir_cellpose'],  #'{}{}_CellposeSegmentation/',  # s_segdir, s_slide
    ):
    '''
    version: 2021-12-00

    input:
        s_slide: slide id to extract segmentation feature from.
        es_seg_marker: set of cell segmentation markers used for cell segmentation.
            possible is None, which will only do nucleus, i_exp, i_mem, i_shrink based feature extraction.
        i_exp: how many pixels should the nucleus be extended to be regarded as the whole cell?
            how wide should the doughnut regarded as cytoplasm be?
            default setting is 5, though this value depends on your pixel size.
        i_mem: how many pixels should the nucleus or cell border to the inside be extended to be regarded as membrane?
            how many pixels should the nucleus or cell border to the inside and outside be extended to be regarded as adjacent?
            default setting is 2, though this value depends on your pixel size.
        i_shrink: should markers also be shrunk, e.g. to be in the filter_features step used as custom_markerpartition or against bleed through?
            set how many pixels should be shrunken.
            this will produce additional nuclei, exp, perinuc, and cytoplasm columns, taking this value into account.
            default setting is 0. to be processed, value have to be > 0 and < i_exp.

        # file system
        s_afsubdir: dictionary where to find af subtracted tiff images or registered images.
        s_format_afsubdir: subdirectory structure of s_afsubdir.
        s_segdir: directory where segmentation basin, and xy cell position files
            and when processed, feature extraction raw files can be found.
        s_format_segdir_cellpose: subdirectory structure of s_segdir.

    output:
        whole slide all feature csv file.

    description:
        loads config.es_markerpartition_standard, the segmentation results, and the registered or af subtracted registered images.
        extract centroid, area, eccentricity, and mean intensity for nuclei and cytoplasm cell partition
        and mean intensity of the top 25% of pixel from the membrane cell partition,
        from each image.
    '''
    # handle input
    s_input = s_afsubdir.split('/')[-2].lower()
    s_seg_markers = None
    if not (es_seg_marker is None):
        s_seg_markers = '.'.join(sorted(es_seg_marker))

    # remove possible existing temp output file
    s_segpath = s_format_segdir_cellpose.format(s_segdir, s_slide)
    s_ofile_tmp = config.d_nconv['s_format_csv_raw_centroid_shape_meanintenisty'].format(s_slide, s_seg_markers, s_input) + '.part'
    try:
        os.remove(s_segpath + s_ofile_tmp)
    except FileNotFoundError:
        pass

    # fetch and process marker_partition standard
    es_marker_nuc = set()
    es_marker_nucmem = set()
    es_marker_cell = set()
    es_marker_cellmem = set()
    for s_markerpartition in config.es_markerpartition_standard:
        if s_markerpartition.endswith('_Nuclei'):
           es_marker_nuc.add(s_markerpartition.replace('_Nuclei',''))
        elif s_markerpartition.endswith('_Nucmem'):
           es_marker_nucmem.add(s_markerpartition.replace('_Nucmem',''))
        elif s_markerpartition.endswith('_Ring'):
           es_marker_cell.add(s_markerpartition.replace('_Ring',''))
        elif s_markerpartition.endswith('_Cellmem'):
           es_marker_cellmem.add(s_markerpartition.replace('_Cellmem',''))
        else:
           sys.exit(f'Error @ feat.extract_features: config.es_markerpartition_standard marker with non-standard cell partition detected {s_markerpartition}.\nstanadrd are _Nuclei, _Nucmem, _Ring, _Cellmem,')

    # each slide_pxscene
    for s_file in sorted(os.listdir(s_segpath)):
        print(f'check: {s_input} {s_file} ...')

        # find matched nucleus cell segmentation label file
        if (s_seg_markers is None):
            o_match = re.search(config.d_nconv['s_regex_tiff_celllabel_nuc'], s_file)
        else:
            o_match = re.search(config.d_nconv['s_regex_tiff_celllabel_nuccellmatched'], s_file)
        if not (o_match is None):
            # extract slide_pxscene, nucleus diameter, and cell diameter
            if (s_seg_markers is None):
                s_slide = o_match[config.d_nconv['di_regex_tiff_celllabel_nuc']['s_slide']]  # bue: given as function input!
                s_pxscene = o_match[config.d_nconv['di_regex_tiff_celllabel_nuc']['s_pxscene']]
                s_slide_pxscene = f'{s_slide}_{s_pxscene}'
                s_seg_markers_file = None  # bue 20211218: this is input!
                i_nuc_diam = int(o_match[config.d_nconv['di_regex_tiff_celllabel_nuc']['i_nuc_diam']])
                i_cell_diam = None
            else:
                s_slide = o_match[config.d_nconv['di_regex_tiff_celllabel_nuccellmatched']['s_slide']]  # bue: given as function input!
                s_pxscene = o_match[config.d_nconv['di_regex_tiff_celllabel_nuccellmatched']['s_pxscene']]
                s_slide_pxscene = f'{s_slide}_{s_pxscene}'
                i_nuc_diam = int(o_match[config.d_nconv['di_regex_tiff_celllabel_nuccellmatched']['i_nuc_diam']])
                s_seg_markers_file = o_match[config.d_nconv['di_regex_tiff_celllabel_nuccellmatched']['s_seg_markers']]  # bue 20211218: this is input!
                i_cell_diam = int(o_match[config.d_nconv['di_regex_tiff_celllabel_nuccellmatched']['i_cell_diam']])

            # check seg_markers
            if (s_seg_markers == s_seg_markers_file):

                # load files
                print(f'processing: seg_markers {s_seg_markers}, min nuc_diam {i_nuc_diam}[px], min cell diam {i_cell_diam}[px], slide_pxscene {s_slide_pxscene}')
                ai_dapi = io.imread(s_segpath+config.d_nconv['s_format_png_nucprojection'].format(s_slide_pxscene, i_nuc_diam))
                ai_nuc_labels = io.imread(s_segpath+config.d_nconv['s_format_tiff_celllabel_nuc'].format(s_slide_pxscene, i_nuc_diam))
                ai_cell_labels = None
                if not (s_seg_markers is None):
                    ai_cell_labels = io.imread(s_segpath+config.d_nconv['s_format_tiff_celllabel_nuccellmatched'].format(s_slide_pxscene, s_seg_markers, i_nuc_diam, i_cell_diam))

                # extract nuclear features
                # bue 20211222: every cell has as nucleus, later when we left merge other partition, cells might miss them and nan is introduced!
                df_feat_pxscene = _extract_feat(
                    ai_labels = ai_nuc_labels,
                    ai_intensity_image = ai_dapi,
                    ls_properties = (['label']),
                )
                df_feat_pxscene.columns = ['cellid'] # bue: this is the label. jenny called this originally label_segmented-nuclei
                df_feat_pxscene.index = [f'{s_slide_pxscene}_cell{s_label_id}' for s_label_id in df_feat_pxscene.loc[:,'cellid']]
                df_feat_pxscene['slide'] = s_slide
                df_feat_pxscene['slide_scene'] = s_slide_pxscene

                # get standard subcellular partitions
                # bue 20210807: this part eats memory and time.
                dai_loc_nuccellmem = {
                    # nucleus
                    'nuclei': ai_nuc_labels,
                    # nucleus and 5 pixels cytoplasm
                    f'exp{i_exp}': _exp_label(ai_nuc_labels, i_distance=i_exp),  #dtai_loc_nuc['grown'][1],  #  5[px]
                    # 2 pixel from nucleus border to the inside.
                    f'nucmem{i_mem}': _mem_label(ai_nuc_labels, i_distance=i_mem),  #dtai_loc_nuc['membrane'][0],  # 2[px]  # bue: nucmem2 original: nucmem
                    # 2 pixel left and right from the nucleus border.
                    f'nucadj{i_mem}': _adj_label(ai_nuc_labels, i_distance=i_mem),  #dtai_loc_nuc['straddle'][0],  # 2[px]
                    # 5 pixel from nucleus border to the outside.
                    f'perinuc{i_exp}': _peri_label(ai_nuc_labels, i_distance=i_exp),  #dtai_loc_nuc['ring'][1],  # 5[px]
                }
                if not (s_seg_markers is None):
                    dai_loc_nuccellmem.update({
                        # cytoplasm
                        'cytoplasm': _cell_sub_nuc_label(ai_nuc_labels, ai_cell_labels),
                        # 2 pixel form cell border to the inside.
                        f'cellmem{i_mem}': _mem_label(ai_cell_labels, i_distance=i_mem),  #dtai_loc_cell['membrane'][0],  # 2[px]  # bue: cellmem2 original: cellmem
                        # 2 pixel left and right from the cell border.
                        f'celladj{i_mem}': _adj_label(ai_cell_labels, i_distance=i_mem),  #dtai_loc_cell['straddle'][0]  # 2[px]
                        # cell
                        'cell': ai_cell_labels,
                    })

                # shrunken partitions
                if (i_shrink >  0) and (i_shrink < i_exp):
                    i_shrunken = i_exp - i_shrink
                    dai_loc_nuccellmem.update({
                        # exp shrunk by the border and 2 pixel.
                        f'exp{i_shrunken}': _shrink_label(dai_loc_nuccellmem[f'exp{i_exp}'], i_distance=i_shrink),
                    })
                    dai_loc_nuccellmem.update({
                        # perinuc shrunk by the border and 2 pixel.
                        f'perinuc{i_shrunken}': _shrink_label(dai_loc_nuccellmem[f'perinuc{i_exp}'], i_distance=i_shrink),
                    })
                    dai_loc_nuccellmem.update({
                        # nucleus shrunk by the border and 2 pixel. pendant to perinuc2 by perinuc5 standard.
                        f'nuclei{i_shrink}': _shrink_label(dai_loc_nuccellmem['nuclei'], i_distance=i_shrink),
                    })
                    if not (s_seg_markers is None):
                        dai_loc_nuccellmem.update({
                            # cytoplasm shrunk by the border and 2 pixel. pendant to perinuc2 by perinuc5 standard.
                            f'cytoplasm{i_shrink}': _shrink_label(dai_loc_nuccellmem['cytoplasm'], i_distance=i_shrink),
                        })

                # top 25 percentile mean for markers that are not evenly distributed (especially membrane markers).
                # bue 20210724: do this partition make sense?
                # bue 20210807: these are just calls by reference. this is super quick.
                dai_loc_nuccellmemp25 = {
                    # nucleus
                    'nucleip25': ai_nuc_labels,  # bue: nucleip25 original: nuclei25
                    # nucleus and 5 pixels cytoplasm
                    f'exp{i_exp}p25': dai_loc_nuccellmem[f'exp{i_exp}'],  #dtai_loc_nuc['grown'][1],  # bue: exp5p25 original: exp5nucmembrane25
                    # nucleus membrane (from border to the inside)
                    f'nucmem{i_mem}p25': dai_loc_nuccellmem[f'nucmem{i_mem}'],  #dtai_loc_nuc['membrane'][0],  # bue: nucmem2p25  original: nucmem25
                }
                if not (s_seg_markers is None):
                    dai_loc_nuccellmemp25.update({
                        # cell membrane (from border to the inside)
                        f'cellmem{i_mem}p25': dai_loc_nuccellmem[f'cellmem{i_mem}'],  #dtai_loc_cell['membrane'][0],  # 2[px] bue: cellmem2p25 original: cellmem25
                    })

                # bue 2021-10-20: same marker twice in a panel?!
                # does basic.parse_tiff_reg sort the files?
                # it might actually be that more than one times same marker are merged properly by adding a suffix.
                # but what happens by patching and feature correct label?
                # what if there are doubles of a cell seg_marker?

                # for each image file (one per slide_pxscene, round, channel)
                s_path_afsub = s_format_afsubdir.format(s_afsubdir, s_slide_pxscene)
                df_img_marker = basic.parse_tiff_reg(s_wd=s_path_afsub)  # these are all markers
                #df_img_marker = df_img.loc[df_img.slide_scene == s_slide_pxscene, :]
                for s_index in df_img_marker.index:
                    s_marker = df_img_marker.loc[s_index,'marker']
                    print(f'extract {s_marker} from: {s_index}')

                    # load file
                    ai_intensity_image = io.imread(f'{df_img_marker.index.name}{s_index}')

                    # any marker any partition
                    for s_loc, ai_loc in sorted(dai_loc_nuccellmem.items()):
                        df_marker_loc = _extract_feat(
                            ai_labels = ai_loc,
                            ai_intensity_image = ai_intensity_image,
                            ls_properties = ['label', 'mean_intensity']
                        )
                        df_marker_loc.columns = [
                            f'{s_marker}_{s_loc}_label',
                            f'{s_marker}_{s_loc}',
                        ]
                        df_marker_loc.index = [f'{s_slide_pxscene}_cell{s_label_id}' for s_label_id in df_marker_loc.loc[:,f'{s_marker}_{s_loc}_label']]
                        df_marker_loc.drop(f'{s_marker}_{s_loc}_label', axis=1, inplace=True)
                        df_feat_pxscene = pd.merge(df_feat_pxscene, df_marker_loc, left_index=True, right_index=True, how='left', suffixes=('',f'{s_marker}_{s_loc}'))
                        # free memory
                        del df_marker_loc

                    # only dapi marker and nuclei partition
                    # bue: dapi marker are already labeled by round when parsing the filename
                    if s_marker.startswith(config.d_nconv['s_marker_dapi']):
                        for s_loc in ['nuclei']:
                            ai_loc = dai_loc_nuccellmem[s_loc]
                            df_marker_loc = _extract_feat(
                                ai_labels = ai_loc,
                                ai_intensity_image = ai_intensity_image,
                                ls_properties = ['label', 'centroid','area','eccentricity']
                            )
                            df_marker_loc.columns = [
                                'label',
                                f'{s_marker}_{s_loc}_centroid-0',
                                f'{s_marker}_{s_loc}_centroid-1',
                                f'{s_marker}_{s_loc}_area',
                                f'{s_marker}_{s_loc}_eccentricity',
                            ]
                            df_marker_loc.index = [f'{s_slide_pxscene}_cell{s_label_id}' for s_label_id in df_marker_loc.loc[:,'label']]
                            df_marker_loc.drop('label', axis=1, inplace=True)
                            df_feat_pxscene = pd.merge(df_feat_pxscene, df_marker_loc, left_index=True, right_index=True, how='left', suffixes=('',f'{s_marker}_{s_loc}'))
                            # free memory
                            del df_marker_loc

                    # only s_seg_markers and cell or cytoplasm partition
                    if not (s_seg_markers is None) and (s_marker in es_seg_marker):
                        for s_loc in ['cell','cytoplasm']:
                            ai_loc = dai_loc_nuccellmem[s_loc]
                            df_marker_loc = _extract_feat(
                                ai_labels = ai_loc,
                                ai_intensity_image = ai_intensity_image,
                                ls_properties = ['label','area','eccentricity','euler_number']
                            )
                            df_marker_loc.columns = [
                                'label',
                                f'{s_marker}_{s_loc}_area',
                                f'{s_marker}_{s_loc}_eccentricity',
                                f'{s_marker}_{s_loc}_euler',
                            ]
                            df_marker_loc.index = [f'{s_slide_pxscene}_cell{s_label_id}' for s_label_id in df_marker_loc.loc[:,'label']]
                            df_marker_loc.drop('label', axis=1, inplace=True)
                            df_feat_pxscene = pd.merge(df_feat_pxscene, df_marker_loc, left_index=True, right_index=True, how='left', suffixes=('',f'{s_marker}_{s_loc}'))
                            # free memory
                            del df_marker_loc

                    # only membrane marker (which are always nucleus or cell marker too) any partition
                    if (s_marker in es_marker_nucmem) or (s_marker in es_marker_cellmem):
                        for s_loc, ai_loc in sorted(dai_loc_nuccellmemp25.items()):
                            df_prop = _extract_feat(
                                ai_labels = ai_loc,
                                ai_intensity_image = ai_intensity_image,
                                ls_properties = ['intensity_image','image','label']
                            )
                            df_marker_loc = pd.DataFrame(columns = [f'{s_marker}_{s_loc}'])
                            for s_idx in df_prop.index:
                                s_label_id = df_prop.loc[s_idx, 'label']
                                ai_intensity_image_small = df_prop.loc[s_idx, 'intensity_image']
                                ai_image = df_prop.loc[s_idx, 'image']
                                ai_pixels = ai_intensity_image_small[ai_image]
                                ai_pixels25 = ai_pixels[ai_pixels >= np.quantile(ai_pixels, .75)]
                                df_marker_loc.loc[s_label_id, f'{s_marker}_{s_loc}'] = ai_pixels25.mean()
                            df_marker_loc.index = [f'{s_slide_pxscene}_cell{s_label_id}' for s_label_id in df_marker_loc.index]
                            df_feat_pxscene = pd.merge(df_feat_pxscene, df_marker_loc, left_index=True, right_index=True, how='left', suffixes=('',f'{s_marker}_{s_loc}'))
                            # free memory
                            del ai_intensity_image_small
                            del s_label_id
                            del ai_image
                            del ai_pixels
                            del ai_pixels25
                            del df_prop
                            del df_marker_loc

                    # free memory
                    del s_marker
                    del ai_intensity_image

                # write slide_pxscene output to file temporary file
                print(f'write to file: {s_segpath}{s_ofile_tmp}')
                if os.path.isfile(s_segpath+s_ofile_tmp):
                    if (sorted(df_feat_pxscene.columns) != sorted(ls_column)):
                        sys.exit(f'Error: slide incompatible slide_scene: {s_slide_pxscene}\n{sorted(df_feat_pxscene.columns)}\n{sorted(ls_column)}')
                    df_feat_pxscene = df_feat_pxscene.loc[:,ls_column]
                    df_feat_pxscene.to_csv(s_segpath+s_ofile_tmp, mode='a', header=False)
                else:
                    ls_column = list(df_feat_pxscene.columns)
                    df_feat_pxscene.index.name = s_input
                    df_feat_pxscene.to_csv(s_segpath+s_ofile_tmp)

                # free memory
                del s_pxscene
                del i_nuc_diam
                del i_cell_diam
                del s_slide_pxscene
                del ai_dapi
                del ai_nuc_labels
                del ai_cell_labels
                del dai_loc_nuccellmem
                del dai_loc_nuccellmemp25
                del df_feat_pxscene
                del df_img_marker
                del s_path_afsub
                gc.collect(generation=2)

    # write slide output to file
    s_ofile = config.d_nconv['s_format_csv_raw_centroid_shape_meanintenisty'].format(s_slide, s_seg_markers, s_input)
    shutil.move(s_segpath+s_ofile_tmp, s_segpath+s_ofile)
    print(f'at: {s_segpath} rename {s_ofile_tmp} to {s_ofile}')
    #break


# spawner function
def extract_features_spawn(
        es_slide,
        es_seg_marker,
        i_exp = 5,  # number of pixel for cytoplasm doughnut. microscope dependent!
        i_mem = 2,  # number of pixel for membrane. microscope dependent!
        i_shrink = 0,  # optional, patching against bleed trough.
        # processing
        s_type_processing = 'slurm',
        s_slurm_partition = 'exacloud',
        s_slurm_mem = '32G',
        s_slurm_time = '36:00:0',
        s_slurm_account = 'gray_lab',
        # specify input and output directory
        s_afsubdir = config.d_nconv['s_regdir'],  #'SubtractedRegisteredImages/', or 'RegisteredImages/'
        s_format_afsubdir = config.d_nconv['s_format_regdir'],  # s_afsubdir, s_slide_pxscene
        s_segdir = config.d_nconv['s_segdir'],  #'Segmentation/',
        s_format_segdir_cellpose = config.d_nconv['s_format_segdir_cellpose'],  #'{}{}_CellposeSegmentation/',  # s_segdir, s_slide
    ):
    '''
    version: 2021-12-00

    input:
        es_slide: set of slide ids to process.
        es_seg_marker: set of cell segmentation markers used for cell segmentation.
            possible is None, which will only do nucleus, i_exp, i_mem, i_shrink based feature extraction.
        i_exp: how many pixels should the nucleus be extended to be regarded as the whole cell?
            how wide should the doughnut be, regarded as cytoplasm?
            default setting is 5, though this value  depends on your pixel size.
        i_mem: how many pixels should the nucleus or cell border to the inside be extended to be regarded as  membrane?
            how many pixels should the nucleus or cell border to the inside and outside be extended to be regarded as adjacent?
            default setting is 2, though this value depends on your pixel size.
        i_shrink: should markers also be shrunk, e.g. to be in the filter_features step used as custom_markerpartition or against bleed through?
            set here how many pixels should be shrunken.
            this will produce additional nuclei, exp, perinuc, and cytoplasm columns, taking this value into account.
            default setting is 0. to be processed, value have to be > 0 and < i_exp.

        # processing
        s_type_processing: string to specify if pipeline is run on a slurm cluster or not.
            known vocabulary is slurm and any other string for non-slurm processing..
        s_slurm_partition: slurm cluster partition to use.
            OHSU ACC options are 'exacloud', 'light', (and 'gpu').
            the default is tweaked to OHSU ACC settings.
        s_slurm_mem: slurm cluster memory allocation. format '64G'.
        s_slurm_time: slurm cluster time allocation in hour or day format.
            OHSU ACC max is '36:00:00' [hour] or '30-0' [day].
            the related qos code is tweaked to OHSU ACC settings.
        s_slurm_account: slurm cluster account to credit time from.
            OHSU ACC options are e.g. 'gray_lab', 'chin_lab', 'heiserlab', 'CEDAR'.

        # file system
        s_afsubdir: auto fluorescence subtracted registered images directory or registered image directory.
        s_format_afsubdir: subfolder pattern in s_afsubdir. one subfolder per slide_pxscene.
        s_segdir: segmentation result directory.
        s_format_segdir_cellpose: cellpose segmentation result subdirectory structure.

    output:
        csv file for each slide with all extracted features.

    description:
        spawn function to run the feat.extract_features function.
    '''
    # handle input
    s_input = s_afsubdir.split('/')[-2].lower()

    # for each slide
    for s_slide in sorted(es_slide):
        print(f'extract_features_spawn: {s_slide} {s_input}')

        # set run commands
        s_pathfile_template = 'template_extractfeatures_slide.py'
        s_pathfile = f'extractfeature_slide_{s_slide}_{".".join(sorted(es_seg_marker))}_{s_input}.py'
        s_srun_cmd = f'python3 {s_pathfile}'
        ls_run_cmd = ['python3', s_pathfile]

        ## any ##
        # load template extract feature script code
        with open(f'{s_path_module}src/{s_pathfile_template}') as f:
            s_stream = f.read()

        # edit code generic. order matters!
        s_stream = s_stream.replace('peek_s_slide', s_slide)
        s_stream = s_stream.replace('peek_es_seg_marker', str(es_seg_marker))
        s_stream = s_stream.replace('peek_i_exp', str(i_exp))
        s_stream = s_stream.replace('peek_i_mem', str(i_mem))
        s_stream = s_stream.replace('peek_i_shrink', str(i_shrink))
        s_stream = s_stream.replace('peek_s_segdir', s_segdir)
        s_stream = s_stream.replace('peek_s_format_segdir_cellpose', s_format_segdir_cellpose)
        s_stream = s_stream.replace('peek_s_afsubdir', s_afsubdir)
        s_stream = s_stream.replace('peek_s_format_afsubdir', s_format_afsubdir)

        # write executable extract feature script code to file
        time.sleep(4)
        with open(s_pathfile, 'w') as f:
            f.write(s_stream)

        # execute extract feature script
        time.sleep(4)
        if (s_type_processing == 'slurm'):
            # generate sbatch file
            s_pathfile_sbatch = f'extractfeature_slide_{s_slide}_{".".join(sorted(es_seg_marker))}_{s_input}.sbatch'
            config.slurmbatch(
                s_pathfile_sbatch = s_pathfile_sbatch,
                s_srun_cmd = s_srun_cmd,
                s_jobname = f'e{s_slide}',
                s_partition = s_slurm_partition,
                s_gpu = None,
                s_mem = s_slurm_mem,
                s_time = s_slurm_time,
                s_account = s_slurm_account,
            )
            # Jenny, this is cool!
            subprocess.run(
                ['sbatch', s_pathfile_sbatch],
                stdout = subprocess.PIPE,
                stderr = subprocess.STDOUT,
            )
        else:  # non-slurm
            # Jenny, this is cool!
            s_file_stdouterr = f'slurp-extractfeature_slide_{s_slide}_{".".join(sorted(es_seg_marker))}_{s_input}.out'
            o_process = subprocess.run(
                ls_run_cmd,
                stdout = open(s_file_stdouterr, 'w'),
                stderr = subprocess.STDOUT,
            )


def load_cellpose_features_df(
        s_slide,
        es_seg_marker,  # ECE: for input filename to load
        # file system
        s_afsubdir = config.d_nconv['s_afsubdir'],  #'SubtractedRegisteredImages/', or 'RegisteredImages/'
        s_segdir = config.d_nconv['s_segdir'],  #'Segmentation/',
        s_format_segdir_cellpose = config.d_nconv['s_format_segdir_cellpose'],  #'{}{}_CellposeSegmentation/',  # s_segdir, s_slide
    ):
    '''
    version: 2021-12-0

    input:
        s_slide: slide from which cellpose segmented feature data should be loaded.
        es_seg_marker: set of cell segmentation markers used for cell segmentation.
            possible is None, which will only use nucleus segmentation.
        s_afsubdir: auto fluorescence subtracted registered images directory or registered image directory.
        s_segdir: directory where in the subdirectories
            segmentation basin, feature extraction, and xy cell position files can be found.
        s_format_segdir_cellpose: cellpose segmentation result subdirectory structure.

    output:
        df_mi: cellpose segmented feature dataframe.

    description:
        function loads the slide's raw feature csv files into a dataframe.
    '''
    # handle input
    s_input = s_afsubdir.split('/')[-2].lower()
    s_seg_markers = None
    if not (es_seg_marker is None):
        s_seg_markers = '.'.join(sorted(es_seg_marker))

    # fetch data
    s_ifile = config.d_nconv['s_format_csv_raw_centroid_shape_meanintenisty'].format(s_slide, s_seg_markers, s_input)
    print('Loading:', s_ifile)
    df_mi = pd.read_csv(s_format_segdir_cellpose.format(s_segdir, s_slide) + s_ifile, index_col=0)

    # output
    return(df_mi)


###############################
#  filter and patch features #
################################
def filter_cellpose_xy(
        s_slide,
        es_seg_marker,  # ECE for imput filename
        ds_centroid = {
            'DAPI2_nuclei_centroid-0': 'DAPI_Y',
            'DAPI2_nuclei_centroid-1': 'DAPI_X',
        },
        # tissue edge distance detection
        s_tissue_dapi = 'DAPI1',  # can be None
        i_tissue_dapi_thresh = 500,  # 300 512 600
        i_tissue_area_thresh = 50000,  # 65536
        # file system
        s_afsubdir = config.d_nconv['s_afsubdir'],  #'SubtractedRegisteredImages/', or 'RegisteredImages/'
        s_format_afsubdir = config.d_nconv['s_format_afsubdir'],  # {}{}/  s_afsubdir, slide_scene
        s_segdir = config.d_nconv['s_segdir'],  #'Segmentation/',
        s_format_segdir_cellpose = config.d_nconv['s_format_segdir_cellpose'],  #'{}{}_CellposeSegmentation/',  # s_segdir, s_slide
    ):
    '''
    version: 2021-12-00

    input:
        s_slide: side id that should be processed
        es_seg_marker: set of cell segmentation markers used for cell segmentation.
            possible is None, which will only use nucleus segmentation.
        ds_centroid: dictionary which define original nucleus segmentation centroid (key),
            and how they should be named by standard (value).
            the keys from the default dictionary is cellpose compatible.
        s_tissue_dapi: dapi and round marker label to specify the image
            which should be used for tissue detection.
            if None, no tissue detection is done.
        i_tissue_dapi_thresh: dapi threshold value for tissue detection.
            this value will be much lower than the dapi positive nucleus value,
            in our experience, ok values are between 300 and 600.
        i_tissue_area_thresh: specify pixel area threshold,
            use to fill tissue gaps between dapi nuclei.

        # file system
        s_afsubdir: auto fluorescence subtracted registered images directory or registered image directory.
        s_format_afsubdir: subfolder structure in s_afsubdir. one subfolder per slide_pxscene.
        s_segdir: directory where segmentation basin, feature extraction, and xy cell position files can be found.
        s_format_segdir_cellpose: subfolder structure in segmentation directory.

    output:
        one features CentroidXY csv file per slide, saved at s_segdir.

    description:
        filter out nuclei centroids, area, and eccentricity from the
        mean intensity data frame file from a marker.
        by default, use the same DAPI as specified in ds_centroid.
        additionally, detect tissue and calculate tissue edge distance for each nuclei centroid.
    '''
    # handle input
    ls_coor = ['slide','slide_scene','cellid']  # feat.load_cellpose_features_df takes care of that
    ls_standard = sorted(ds_centroid.values())
    s_segpath = s_format_segdir_cellpose.format(s_segdir, s_slide)

    # processing basics
    df_mi = load_cellpose_features_df(
        s_slide = s_slide,
        es_seg_marker = es_seg_marker, # ECE: for filename to load
        s_afsubdir = s_afsubdir,
        s_segdir = s_segdir,
        s_format_segdir_cellpose=s_format_segdir_cellpose
    )
    df_mi.rename(ds_centroid, axis=1, inplace=True)
    df_xy = df_mi.loc[:, ls_coor+ls_standard]

    # detect coordinate unsigned integer type
    i_coor_max = int(np.ceil(df_xy.loc[:,['DAPI_Y','DAPI_X']].max().max()))
    if (i_coor_max < 2**8):
        o_dtype = np.uint8
    elif (i_coor_max < 2**16):
        o_dtype = np.uint16
    elif (i_coor_max < 2**32):
        o_dtype = np.uint32
    else:
        o_dtype = np.uint64
    df_xy['DAPI_X_int'] = df_xy['DAPI_X'].astype(o_dtype)
    df_xy['DAPI_Y_int'] = df_xy['DAPI_Y'].astype(o_dtype)

    # process tissue edge distance detection
    if not (s_tissue_dapi is None):
        df_distance = pd.DataFrame()

        # detect slide pxscene
        for s_folder in sorted(os.listdir(s_afsubdir)):
            if os.path.isdir(s_afsubdir + s_folder) and s_folder.startswith(s_slide):
                s_afsubpath = s_afsubdir + s_folder + '/'
                df_img = basic.parse_tiff_reg(s_afsubpath)
                for s_slidepxscene in sorted(df_img.slide_scene.unique()):

                    # load dapi round 1 threshold and image
                    as_file_dapi = df_img.loc[(df_img.slide_scene == s_slidepxscene) & (df_img.marker == s_tissue_dapi), :].index.values
                    if (len(as_file_dapi) != 1):
                        sys.exit(f'Error : @ feat._detect_tissue_edge_distance : at {s_afsubpath} for slide_scene {s_slidepxscene} marker {s_tissue_dapi} more then one file found {as_file_dapi}.')
                    s_file_dapi = as_file_dapi[0]
                    print(f'load: {s_file_dapi}')
                    s_pathfile_dapi = s_afsubpath + s_file_dapi
                    ai_dapi = io.imread(s_pathfile_dapi)
                    print(f'dapi image shape: {ai_dapi.shape}')

                    # generate tissue mask based on dapi threshold and area threshold parameter
                    ab_dapi = (ai_dapi > i_tissue_dapi_thresh)
                    ab_tissue = morphology.remove_small_holes(ar=ab_dapi, area_threshold=i_tissue_area_thresh)
                    print(f'dapi tissue shape: {ab_tissue.shape}')

                    # get distance to edge
                    ar_distances = scipy.ndimage.distance_transform_edt(
                        input = ab_tissue,
                    )
                    print(f'ar_distances shape {ar_distances.shape}')

                    # get centroid distance to cell border
                    df_distance_slidescene = df_xy.loc[df_xy.slide_scene == s_slidepxscene, ['DAPI_Y_int', 'DAPI_X_int']]
                    df_distance_slidescene['edge_distance'] = ar_distances[df_distance_slidescene.DAPI_Y_int, df_distance_slidescene.DAPI_X_int]
                    df_distance_slidescene['slide_scene'] = s_slidepxscene

                    # update df_distance
                    df_distance = df_distance.append(df_distance_slidescene)

                    # detect tissue distance file unsigned integer type
                    if (ar_distances.max() < 2**8):
                        ai_distances = ar_distances.astype(np.uint8)
                    elif (ar_distances.max() < 2**16):
                        ai_distances = ar_distances.astype(np.uint16)
                    elif (ar_distances.max() < 2**32):
                        ai_distances = ar_distances.astype(np.uint32)
                    else:
                        ai_distances = ar_distances.astype(np.uint64)
                    print(f'ai_distances shape {ar_distances.shape}')
                    # save tissue distance file
                    s_ofile = config.d_nconv['s_format_tiff_tissueedgedistance'].format(s_slidepxscene, s_tissue_dapi, i_tissue_dapi_thresh, i_tissue_area_thresh)
                    print('write file:', s_ofile)
                    io.imsave(s_segpath + s_ofile, ai_distances, check_contrast=False)

        # merge
        df_xy = pd.merge(
            df_xy,
            df_distance,
            on = ['slide_scene','DAPI_Y_int','DAPI_X_int'],
            how='left',
        )

    # output
    df_xy.index = df_xy.slide_scene + '_cell' + df_xy.cellid.astype(str)
    df_xy.index.name = 'index'
    print('df_xy info:', df_xy.info())
    print('write file:', s_ofile)
    s_ofile = config.d_nconv['s_format_csv_centroidxy'].format(s_slide)
    df_xy.to_csv(s_segpath + s_ofile)
    return(df_xy)


#def _fill_cellpose_nas( part1
def _thresh_cytoplasm(
        df_mi,
        di_seg_marker,  # ECE: tricky
    ):
    '''
    version: 2021-12-00

    input:
        df_mi: cellpose segmented feature dataframe.
        di_seg_marker: dictionary of cytoplasm segmentation marker (key) and manual threshold value (value),
            to detect cytoplasm positive cells.

    output:
        df_mi: updated input dataframe.

    description: ECE
        function detects s_seg_marker cytoplasm positive cells ({s_seg_marker}_negative False).
        cells without cytoplasm (nan) or s_seg_marker cytoplasm mean values below i_seg_marker are set to {s_seg_marker}_negative True.
    '''
    # since segmentation was run on ecad, use ecad threshold
    es_cytoneg_cell = set(df_mi.index.tolist())
    if not (di_seg_marker is None):
        print(f'Finding {sorted(di_seg_marker)} cytoplasm negative cells...')
        for s_seg_marker, i_seg_marker in di_seg_marker.items():
            #ls_neg_cells = df_mi.loc[(df_mi.loc[:,f'{s_seg_marker}_cytoplasm'] < i_seg_marker), :].index.tolist() #jenny 20211029: this is wrong because of nas
            #ls_neg_cells = (df_mi[~(df_mi.loc[:,f'{s_seg_marker}_cytoplasm'] > i_seg_marker)]).index.tolist()
            es_cytopos_cell = set((df_mi[(df_mi.loc[:,f'{s_seg_marker}_cytoplasm'] > i_seg_marker)]).index.tolist())
            es_cytoneg_cell = es_cytoneg_cell.difference(es_cytopos_cell)
            df_mi[f'{s_seg_marker}_negative'] = ~df_mi.index.isin(es_cytopos_cell)
    df_mi[f'cytoplasm_negative'] = df_mi.index.isin(es_cytoneg_cell)


#def _fill_cellpose_nas( part2
def _patch_nucleus_without_cytoplasm(
        df_mi,  # ECE: dataframe contains cytoplasm_negative column
        i_exp = 5,
     ):
    '''
    version: 2021-12-00

    input:
        df_mi: data frame with segmentation feature mean intensity values,
            already processed with _thresh_cytoplasm,
            which introduces the cytoplasm_negative column.
        i_exp: integer to specify the doughnut size used for cytoplasm for cytoplasm negative cells.

    output:
        df_mi: updated input dataframe.

    description:
        some nuclei don't have a cytoplasm, replace cytoplasm value for
        cytoplasm negative and cytoplasm NA cell with perinuc{i_exp} values.
    '''
    # replace cells without cytoplasm (na and ecad negative) with perinuc{i_exp}.
    print(f'For cells that are cytoplasm negative:')
    for s_marker_cytoplasm in df_mi.columns[df_mi.columns.str.endswith('_cytoplasm')]:
        s_marker = s_marker_cytoplasm.split('_')[0]
        s_marker_perinuc = f'{s_marker}_perinuc{i_exp}'
        print(f'Replace  {s_marker_cytoplasm} nas with {s_marker_perinuc}')
        df_mi.loc[df_mi.loc[:,f'cytoplasm_negative'], s_marker_cytoplasm] = df_mi.loc[df_mi.loc[:, f'cytoplasm_negative'], s_marker_perinuc]


#def fill_bright_nas(
def _patch_weak_membrane_marker(
        df_mi,
        es_seg_marker,  # ECE: tricky
        i_exp = 5,
        i_mem = 2,
    ):
    '''
    version: 2021-12-00

    input:
        df_mi: data frame with segmentation feature mean intensity values,
            already processed with _thresh_cytoplasm,
            which introduces the cytoplasm_negative column.
        es_seg_marker: set of cytoplasm segmentation marker.
        i_exp: integer to specify the doughnut size used for cytoplasm for cytoplasm negative cells.
        i_mem: how many pixels should the nucleus or cell border to the inside be extended to be regarded as membrane?
            how many pixels should the nucleus or cell border to the inside and outside be extended to be regarded as adjacent?
            default setting is 2, though this value depends on your pixel size.

    output:
        df_mi: updated df_mi dataframe,

    description:
        for each nuc membrane marker, enhance Nucmem marker with NA in dataframe by replacing {s_marker}_nucmem{i_mem}p25 with {s_marker}_exp{i_exp}p25.
        for each cell membrane marker,  for cytoplasm negative cells, enhance Cellmem marker in dataframe by replacing {s_marker}_cellmem{i_mem}p25 with {s_marker}_exp{i_exp}p25.
    '''
    # get pannel markers and drop cell segmentation marker
    es_marker_pannel = set([s_marker.split('_')[0] for s_marker in df_mi.columns])
    if not (es_seg_marker is None):
        es_marker_pannel = es_marker_pannel.difference(es_seg_marker)

    ## nucleus ##
    # fetch nucleus membrane
    es_marker_nucmem = set(s_markerpartition_standard.replace('_Nucmem','') for s_markerpartition_standard in config.es_markerpartition_standard if s_markerpartition_standard.endswith('_Nucmem'))
    es_marker_nucmem = es_marker_nucmem.intersection(es_marker_pannel)
    print('nucleus membrane marker found:', sorted(es_marker_nucmem))

    # for each nuc membrane marker enhance cells with nan
    for s_marker in es_marker_nucmem:
        print(f'replace {s_marker}_nucmem{i_mem}p25 in cells with na with {s_marker}_exp{i_exp}p25')
        ls_replace = sorted(df_mi.loc[df_mi.loc[:,f'{s_marker}_nucmem2p25'].isna(), :].index)  # nas cells
        df_mi.loc[ls_replace, f'{s_marker}_nucmem{i_mem}p25'] = df_mi.loc[ls_replace, f'{s_marker}_exp{i_exp}p25']

    ## cytoplasm ##
    if not (es_seg_marker is None):
        # get cytoplasm negative cells
        es_neg = set(df_mi[(df_mi.loc[:,f'cytoplasm_negative']) & (df_mi.index.isin(df_mi.index))].index)

        # fetch cytoplasm membrane
        es_marker_cellmem = set(s_markerpartition_standard.replace('_Cellmem','') for s_markerpartition_standard in config.es_markerpartition_standard if s_markerpartition_standard.endswith('_Cellmem'))
        es_marker_cellmem = es_marker_cellmem.intersection(es_marker_pannel)
        print('cytoplasm membrane marker found:', sorted(es_marker_cellmem))

        # for each cell membrane marker enhance cytoplasm negative and cell membrane nan cells
        for s_marker in es_marker_cellmem:
            print(f'replace {s_marker}_cellmem{i_mem}p25 in (tumor) cytoplasm negative and cellmembrane nan cells cells with {s_marker}_exp{i_exp}p25')
            es_na = set(df_mi.loc[df_mi.loc[:,f'{s_marker}_cellmem{i_mem}p25'].isna(), :].index)  # cellmembrane nas cells
            ls_replace = sorted(es_neg.union(es_na))
            df_mi.loc[ls_replace, f'{s_marker}_cellmem{i_mem}p25'] = df_mi.loc[ls_replace, f'{s_marker}_exp{i_exp}p25']


# def shrunk_seg_regions(
# this is a chicken and egg problem. jennys original bleed through implementation is only for cancer cells.
# cancer cells were patched in _patch_nucleus_without_cytoplasm, but then it is already too late for the bleed trough adjustment.
# I splinted the old _patch_nucleus_without_cytoplasm into _thresh_cytoplasm and _patch_nucleus_without_cytoplasm
# now implementation is possible.
def _patch_bleedthrough(
        df_mi,
        es_shrink_marker, #
        i_exp, #= 5,
        i_shrink, #= 0,
    ):
    '''
    version: 2021-12-00

    input:
        df_mi: data frame with segmentation feature mean intensity values,
        es_shrunk_marker: set of marker that should replace nucleus, exp, perinuc, or cytoplasm with a shrunk version.
        i_exp: integer to specify marker_exp{i_exp} and marker_perinuc{i_exp}
            that should be replaced by marker_exp{i_exp - i_shrink} and marker_perinuc{i_exp - i_shrink}.
        i_shrink: integer to specify marker_exp{i_exp}, marker_perinuc{i_exp}, and marker_cytoplasm
            that should be replaced by marker_exp{i_exp - i_shrink}, marker_perinuc{i_exp - i_shrink} and marker_cytoplasm{i_shrink}.

    output:
        df_mi: updated input dataframe

    description:
        shrinks nucleus, exp, perinuc, and cytoplasm segmentation region as specified by i_exp and i_shrink.
        the columns specified through es_shrunk_marker, i_exp, and i_shrink have already to exist in df_mi.
        this means this same input values should have been use to run extract_features.
        jenny thinks this function only helps bleed through a little.
        bue 2021-10-20: the now implemented function works for nucleus and cytoplasm marker bleed through.
    '''
    print('For markers with bleed through, use shrunken segmentation region:')

    # ok to shrink parameter?
    if (i_shrink > 0) and (i_exp > i_shrink):
        i_shrunk = i_exp - i_shrink

        # stop bleeding nucleus
        es_nuclei_marker = set([s_markerpartition.split('_')[0] for s_markerpartition in df_mi.columns if s_markerpartition.find(f'_nuclei') > -1])
        es_shrink_nuclei_marker = es_shrink_marker.intersection(es_nuclei_marker)
        for s_marker in es_shrink_nuclei_marker:
            s_markerpartition_exp = f'{s_marker}_nuclei'
            s_markerpartition_shrunk = f'{s_marker}_nuclei{i_shrink}'
            print(f'replace {s_markerpartition_exp} with {s_markerpartition_shrunk}')
            df_mi.loc[:, s_markerpartition_exp] = df_mi.loc[:, s_markerpartition_shrunk]

        # stop bleeding exp
        es_exp_marker = set([s_markerpartition.split('_')[0] for s_markerpartition in df_mi.columns if s_markerpartition.find(f'_exp{i_exp}') > -1])
        es_shrink_exp_marker = es_shrink_marker.intersection(es_exp_marker)
        for s_marker in es_shrink_exp_marker:
            s_markerpartition_exp = f'{s_marker}_exp{i_exp}'
            s_markerpartition_shrunk = f'{s_marker}_exp{i_shrunk}'
            print(f'replace {s_markerpartition_exp} with {s_markerpartition_shrunk}')
            df_mi.loc[:, s_markerpartition_exp] = df_mi.loc[:, s_markerpartition_shrunk]

        # stop bleeding perinuc
        es_perinuc_marker = set([s_markerpartition.split('_')[0] for s_markerpartition in df_mi.columns if s_markerpartition.find(f'_perinuc{i_exp}') > -1])
        es_shrink_perinuc_marker = es_shrink_marker.intersection(es_perinuc_marker)
        for s_marker in es_shrink_perinuc_marker:
            s_markerpartition_exp = f'{s_marker}_perinuc{i_exp}'
            s_markerpartition_shrunk = f'{s_marker}_perinuc{i_shrunk}'
            print(f'replace {s_markerpartition_exp} with {s_markerpartition_shrunk}')
            df_mi.loc[:, s_markerpartition_exp] = df_mi.loc[:, s_markerpartition_shrunk]

        # stop bleeding cytoplasm
        es_cytoplasm_marker = set([s_markerpartition.split('_')[0] for s_markerpartition in df_mi.columns if s_markerpartition.find(f'_cytoplasm') > -1])
        es_shrink_cytoplasm_marker = es_shrink_marker.intersection(es_cytoplasm_marker)
        for s_marker in es_shrink_cytoplasm_marker:
            s_markerpartition_exp = f'{s_marker}_cytoplasm'
            s_markerpartition_shrunk = f'{s_marker}_cytoplasm{i_shrink}'
            print(f'replace {s_markerpartition_exp} with {s_markerpartition_shrunk}')
            df_mi.loc[:, s_markerpartition_exp] = df_mi.loc[:, s_markerpartition_shrunk]


#def filter_loc_cellpose(
def _filter_cellpartition_and_shape(
        df_mi,
        es_seg_marker, # {'Ecad'} # ECE tricky
        des_cytoplasm_marker,  # have not to specify cell partition # ECE tricky
        es_custom_markerpartition,  # have to specify cell partition
        i_exp = 5,
        i_mem = 2,
        ds_shape = {
            'DAPI2_nuclei_area':'nuclei_area',
            'DAPI2_nuclei_eccentricity':'nuclei_eccentricity',
            'Ecad_cell_area':'cell_area',
            'Ecad_cell_eccentricity':'cell_eccentricity',
            'Ecad_cell_euler':'cell_euler',
            'Ecad_cytoplasm_area':'cell_area',
            'Ecad_cytoplasm_eccentricity':'cell_eccentricity',
            'Ecad_cytoplasm_euler':'cell_euler',
        },
        ds_centroid = {
            'DAPI2_nuclei_centroid-0': 'DAPI_Y',
            'DAPI2_nuclei_centroid-1': 'DAPI_X',
        },
    ):
    '''
    version: 2021-12-00

    input:
        df_mi: data frame with segmentation feature mean intensity values,
            already processed with _thresh_cytoplasm.
        es_seg_marker: set of string which specifies the markers to be used for cytoplasm detection.
        des_cytoplasm_marker: dictionary set of strings to specify cytoplasm marker.
            these are markers that are expressed in the cytoplasm in s_seg_marker (key) positive cells.
            the marker do not have to define the exact partition.
        es_custom_markerpartition: set of strings to specify markers with specific partitions that should be kept.
            the marker_partition have to be found as column labels in the raw feature extracted file.
            the marker has to define the exact partition.
        i_exp: integer to specify the doughnut size used for cytoplasm for cytoplasm negative cells.
        i_mem: how many pixels should the nucleus or cell border to the inside be extended to be regarded as membrane?
            how many pixels should the nucleus or cell border to the inside and outside be extended to be regarded as adjacent?
            default setting is 2, though this value depends on your pixel size.
        ds_shape: dictionary which defines which original feature to take (key)
            for nucleus, cell, and cytoplasm shape values,
            and how the features should be named by standard (value).
        ds_centroid: dictionary which define original nucleus segmentation centroid (key),
            and how they should be named by standard (value).
            the keys from the default dictionary is cellpose compatible.

    output:
        df_filter: updated df_mi data frame.

    description:
        filter df_mi for standard cell partitions (Nuclei, Nucmem, Ring, Cellmem),
        cytoplasm (des_cytoplasm_marker), additional (es_custom_markerpartition) cell partitions,
        and standard nucleus, cell, and cytoplasm shape values (ds_shape).
        will standard and cytoplasm partition fetched rename to:
        nuclei, nucmem{i_mem}, perinuc{i_exp}, cytoplasm, and cellmem{i_mem},
        and shapes as specified in the ds_shape dictionary.
        only es_custom_markerpartition will keep the original cell partition name.
    '''
    # const
    ls_coor = ['slide', 'slide_scene', 'cellid']

    # handle input
    es_cytoplasm_marker = set()
    if not (es_seg_marker is None):
        for s_seg_key in des_cytoplasm_marker.keys():
            es_seg_key = set(s_seg_key.split('.'))
            for s_seg_marker in es_seg_marker:
                if (s_seg_marker in es_seg_key):
                    es_seg_key.add(s_seg_key)
                    es_cytoplasm_marker.add(s_seg_marker)
                    es_cytoplasm_marker = es_cytoplasm_marker.union(des_cytoplasm_marker[s_seg_key])
    es_custom = set([s_marker.split('_')[0] for s_marker in es_custom_markerpartition])

    # get all markers, exclude cellmembrane marker
    ls_markerpartition = df_mi.columns[(df_mi.dtypes == float)]
    es_marker = set([s_marker.split('_')[0] for s_marker in ls_markerpartition])
    ls_marker = sorted(es_marker)
    print('df_mi markers:', ls_marker)

    # filter for specific marker
    es_dapi = set([s_marker for s_marker in ls_marker if s_marker.startswith(config.d_nconv['s_marker_dapi'])])
    es_nuc = set([s_marker.split('_')[0] for s_marker in config.es_markerpartition_standard if s_marker.endswith('_Nuclei')]).intersection(es_marker)
    es_nucmem = set([s_marker.split('_')[0] for s_marker in config.es_markerpartition_standard if s_marker.endswith('_Nucmem')]).intersection(es_marker)
    es_cyto = es_cytoplasm_marker.intersection(es_marker)
    if (es_seg_marker is None):
        es_ring = set([s_marker.split('_')[0] for s_marker in config.es_markerpartition_standard if s_marker.endswith('_Ring')]).intersection(es_marker)
    else:
        es_ring = (set([s_marker.split('_')[0] for s_marker in config.es_markerpartition_standard if s_marker.endswith('_Ring')]) - es_cyto).intersection(es_marker)
    es_cellmem = set([s_marker.split('_')[0] for s_marker in config.es_markerpartition_standard if s_marker.endswith('_Cellmem')]).intersection(es_marker)
    es_left = es_marker - es_dapi - es_nuc - es_nucmem - es_cyto - es_ring - es_cellmem - es_custom

    # result
    print('Nuclear markers:', sorted(es_nuc))
    print('Nuclear membrane markers:', sorted(es_nucmem))
    print('Ring markers:', sorted(es_ring))
    print('Cytoplasm markers:', sorted(es_cyto))
    print('Cytoplasm membrane markers:', sorted(es_cellmem))
    print('Custom markers:', sorted(es_custom))
    print('Markers with DAPI, Nuclei, or Ring, or Cyto, or Custom not specified: take both nuclei and ring', sorted(es_left))

    # sanity check
    es_all = es_dapi | es_nuc | es_nucmem | es_cyto | es_ring | es_cellmem | es_left | es_custom
    es_missing = es_all.difference(es_marker)
    if len(es_missing) > 0:
        sys.exit(f'Error @ featfilter.filter_loc_cellpose : some markers mentioned in es_custom_markerpartition are missing in df_mi. {es_missing}')

    # filter
    ls_nuc = [s_marker + '_nuclei' for s_marker in sorted(es_left | es_nuc | es_dapi)]
    ls_nucmem = [s_marker + f'_nucmem{i_mem}p25' for s_marker in sorted(es_nucmem)]
    ls_perinuc = [s_marker + f'_perinuc{i_exp}' for s_marker in sorted(es_left | es_ring)]
    ls_cyto = [s_marker + '_cytoplasm' for s_marker in sorted(es_cyto)]
    ls_cellmem = [s_marker + f'_cellmem{i_mem}p25' for s_marker in sorted(es_cellmem)]
    # ls_custom stays with original partition label
    ls_shape = sorted(ds_shape.keys())
    ls_centroid = sorted(ds_centroid.keys())
    if (es_seg_marker is None):
        ls_all = ls_centroid + ls_nuc + ls_nucmem + ls_perinuc + sorted(es_custom_markerpartition) + ls_shape
    else:
        ls_cytoneg = ['cytoplasm_negative']
        for s_seg_marker in es_seg_marker:
            ls_cytoneg.append(f'{s_seg_marker}_negative')
        ls_all = ls_centroid + ls_nuc + ls_nucmem + ls_perinuc + ls_cyto + ls_cellmem + sorted(es_custom_markerpartition) + ls_shape + ls_cytoneg
    df_filter = df_mi.loc[:,ls_coor+ls_all]

    # handle shape and thresh_marker negative
    if not (es_seg_marker is None):
        for s_seg_marker in es_seg_marker:
            ls_shape_threshmarker = [s_shape for s_shape in ls_shape if s_shape.startswith(s_seg_marker)]
            df_filter.loc[df_filter.loc[:, f'{s_seg_marker}_negative'], ls_shape_threshmarker] = None
    df_filter.rename(ds_shape, axis=1, inplace=True)
    df_filter.rename(ds_centroid, axis=1, inplace=True)

    # output
    return(df_filter)


def drop_marker(
        df_mi, # mean intensity values
        es_marker_todrop,
    ):
    '''
    version: 2021-12-00

    input:
        df_mi: data frame with segmented feature mean intensity value.
        es_marker_todrop: marker appearing after the last round.

    output:
        df_mi: updated input dataframe

    description:
        drop markers from a datafarme
    '''
    # kick all columns from a marker
    print(f'feat.drop_marker columns before drop: {df_mi.shape[1]}')
    for s_marker in es_marker_todrop:
        es_drop = set(df_mi.columns[df_mi.columns.str.contains(s_marker)])
        df_mi.drop(es_drop, axis=1, inplace=True)
    print(f'feat.drop_marker columns after drop: {df_mi.shape[1]}')


#def filter_dapi_cellpose(
def _filter_dapi_positive(
        df_mi,
        dfb_thresh,
        es_dapipartition_filter,
        # file system
        s_qcdir = config.d_nconv['s_qcdir'],  #'QC/',
        s_segdir = config.d_nconv['s_segdir'],  #'Segmentation/',
        #s_format_segdir_cellpose = '{}{}_CellposeSegmentation/',  # s_segdir, s_slide
    ):
    '''
    version: 2021-12-00

    input:
        df_mi: marker mean intensity dataframe.
        dfb_thresh: boolean dataframe with on/off values for each cell marker_partition.
        es_dapipartition_filter: list of all DAPIn_nuclei (n is the round number) that should be used as ok filer.

        # file system
        s_qcdir: qc directory.
        s_segdir: directory where segmentation basin, feature extraction, and xy cell position files can be found.
        # s_format_segdir_cellpose: subfolder structure in segmentation directory.

    output:
        df_mi updated
        qc plot

    description:
         filter for DAPI positive cells. Dapi positive is defined by auto threshold.
         only cells from the round defined in ls_filter are considered.
    '''
    # check input
    if (df_mi.index.name != dfb_thresh.index.name):
        sys.exit(f'Error @ jinxif.feat._filter_dapi_positive : df_mi {df_mi.index.name} mean intensity dataframe and dfbthersh {dfb_thersh.index.name} boolean thresh dataframe seem not to have the same input data source!')

    # get all dapi_nuclei columns
    es_dapinuclei = set(dfb_thresh.columns[dfb_thresh.columns.str.contains(config.d_nconv['s_marker_dapi']) & dfb_thresh.columns.str.endswith('_nuclei')].unique())
    print(f'feat._filter_dapi_positive processing es_dapinuclei: {sorted(es_dapinuclei)}')

    # handle plot data
    dfb_dapinuclei = dfb_thresh.loc[:, list(es_dapinuclei) + ['slide_scene']]
    df_scenes = dfb_dapinuclei.groupby('slide_scene').sum().T / dfb_dapinuclei.groupby('slide_scene').sum().max(axis=1)

    # order x axis
    df_scenes['order'] = [float(re.sub(r'[^\d.]','', s_index.replace(config.d_nconv['s_quenching_jinxif'],'.5'))) for s_index in df_scenes.index]
    df_scenes.sort_values('order', inplace=True)
    df_scenes.drop('order', axis=1, inplace=True)
    df_scenes.index = [s_index.split('_')[0] for s_index in df_scenes.index]

    # plot
    fig,ax = plt.subplots(figsize=(10,5))
    df_scenes.plot(ax=ax, colormap='tab20', grid=True, title=f'tissue lost')
    ax.set_xticks(np.arange(0, (len(df_scenes.index)), 1))
    ax.set_xticklabels(list(df_scenes.index))
    ax.set_ylim(0.0, 1.1)
    ax.set_ylabel(f'{config.d_nconv["s_marker_dapi"]} positive cell fraction []')
    ax.set_xlabel('cyclic staining round []')
    ax.legend(loc = 3)
    plt.tight_layout()
    s_opath = s_qcdir + s_segdir.split('/')[-2] + '/'
    os.makedirs(s_opath, exist_ok = True)
    fig.savefig(s_opath + f'{".".join(sorted(dfb_thresh.slide.unique()))}_DAPI_rounds_{df_mi.index.name}_lineplot.png', facecolor='white')

    # filter by first and last round dapi
    es_index_dapifilter_ok = set(dfb_thresh.loc[dfb_thresh.loc[:, es_dapipartition_filter].all(axis=1), :].index)
    # also filter by any dapi less than 1 in mean intensity if not proper threshold before
    es_index_dapi_missing = set(df_mi.loc[(df_mi.loc[:, list(es_dapinuclei)] < 1).any(axis=1), :].index)
    # apply filter
    es_index_dapi = es_index_dapifilter_ok - es_index_dapi_missing
    df_mi_filter = df_mi.loc[df_mi.index.isin(es_index_dapi), :]
    print(f'number of cells before DAPI filter: {df_mi.shape[0]}')
    print(f'filtering by {sorted(es_dapipartition_filter)}')
    print(f'number of cells after DAPI filter: {df_mi_filter.shape[0]}')

    # output
    return(df_mi_filter)


def _plot_thresh_result_dapiseg(
        dfb_thresh,
        df_img_thresh,
        di_seg_marker,  # ECE tricky
        df_xy,
        # file system
        s_qcdir = config.d_nconv['s_qcdir'],  #'QC/',  # output
        s_segdir = config.d_nconv['s_segdir'],  #'Segmentation/', (QC subdir)
        #s_format_segdir_cellpose = '{}{}_CellposeSegmentation/',  # s_segdir, s_slide
    ):
    '''
    version: 2021-12-00

    input:
        dfb_thresh: boolean dataframe with DAPI and s_seg_markers on/off values for each cell that passes the filter.
            e.g. generated with thresh.apply_thresh and filtered with many fuctions.
            all silde_secens in this dataframe will be plotted.
        df_img_thresh: load threshold and round parameter file.
        di_seg_marker: dictionary of cytoplasm segmentation marker (key) and manual threshold value (value),
            to detect cytoplasm positive cells.
        df_xy: dataframe with centroid coordinates from all segmented objects.

        # file system
        s_qcdir: string quality control directory where the result is stored.
        s_segdir: directory where segmentation basin, feature extraction, and xy cell position files can be found.

    output:
        png plots in the s_qcdir directory.

    description:
        generate marker positive cell location in tissue plots for DAPI and the s_seg_markers (e.g. Ecad),
        for tissue loss and e.g. tumor cell detection.
    '''
    # get all dapi_nuclei  cloumns and segmentation marker
    es_dapinuclei = set(dfb_thresh.columns[dfb_thresh.columns.str.contains(config.d_nconv['s_marker_dapi']) & dfb_thresh.columns.str.endswith('_nuclei')].unique())
    if (di_seg_marker is None):
        di_seg_marker = {}
    print(f'feat._plot_thresh_result_dapiseg processing: {sorted(es_dapinuclei)} and cytoplasm marker {di_seg_marker.keys()}')

    # order dapi
    se_dapinuclei = pd.Series(list(es_dapinuclei), name='dapiround')
    print(se_dapinuclei)
    se_dapinuclei.index = [float(re.sub(r'[^\d.]','', s_dapiround.replace(config.d_nconv['s_quenching_jinxif'],'.5'))) for s_dapiround in se_dapinuclei]
    se_dapinuclei.sort_index(inplace=True)
    ls_dapinuclei = list(se_dapinuclei.values)
    ls_marker_partition = ls_dapinuclei

    # add ordered cytoplasm marker
    for s_seg_marker in sorted(di_seg_marker.keys()):
        ls_marker_partition.append(f'{s_seg_marker}_cytoplasm')

    # plot
    thresh.markerpositive_scatterplot(
        ls_marker_partition = ls_marker_partition,
        dfb_thresh = dfb_thresh,
        df_img_thresh = df_img_thresh,
        di_manual_thresh = di_seg_marker,
        df_xy = df_xy,
        s_qcdir = s_qcdir,
        s_segdir = s_segdir,  # QC subfoler
    )


def filter_features(
        s_slide,
        es_dapipartition_filter,  # {'DAPI1_nuclei','DAPI2_nuclei','DAPI16_nuclei'},
        di_seg_marker, # {'Ecad': 1000} # ECE
        i_exp = 5,  # number of pixel for cytoplasm doughnut. microscope dependent!
        i_mem = 2,  # number of pixel for membrane. microscope dependent!
        i_shrink = 0,  # optional, for patching against bleed trough.
        es_shrink_marker = set(),  # optional, against bleed through list of shrunken marker that should replace nucleus, exp{i_exp}, perinuc{i_exp}, or cytoplasm.
        es_custom_markerpartition = set(),  # optional
        des_cytoplasm_marker = config.des_cytoplasmmarker_standard,  # optional, listing of cytoplasm markers, from di_seg_marker.key() positive cells.
        s_tissue_dapi = 'DAPI1',
        i_tissue_dapi_thresh = 500,  # 300 512 600
        i_tissue_area_thresh = 50000,  # 65536
        ds_shape = {
            'DAPI2_nuclei_area':'nuclei_area',
            'DAPI2_nuclei_eccentricity':'nuclei_eccentricity',
            'Ecad_cell_area':'cell_area',
            'Ecad_cell_eccentricity':'cell_eccentricity',
            'Ecad_cell_euler':'cell_euler',
            'Ecad_cytoplasm_area':'cytoplasm_area',
            'Ecad_cytoplasm_eccentricity':'cytoplasm_eccentricity',
            'Ecad_cytoplasm_euler':'cytoplasm_euler',
        },
        ds_centroid = {
            'DAPI2_nuclei_centroid-0': 'DAPI_Y',
            'DAPI2_nuclei_centroid-1': 'DAPI_X',
        },
        # file system
        s_afsubdir = config.d_nconv['s_regdir'],  #'SubtractedRegisteredImages/' or 'RegisteredImages/',
        s_format_afsubdir = config.d_nconv['s_format_regdir'],  # {}{}/  s_afsubdir, slide_scene
        s_segdir = config.d_nconv['s_segdir'],  #'Segmentation/',
        s_format_segdir_cellpose = config.d_nconv['s_format_segdir_cellpose'],  #'{}{}_CellposeSegmentation/',  # s_segdir, s_slide
        s_qcdir = config.d_nconv['s_qcdir'],  #'QC/',
    ):
    '''
    version: 2021-12-00

    input:
        s_slide: slide id to process.
        es_dapipartition_filter: list of all DAPIn_nuclei (n is the round number) that should be used as filer.
            use qc images to define! usually DAPI1 and last good DAPI, and additional bad rounds in between.
        di_seg_marker: dictionary of cytoplasm segmentation marker (key) and manual threshold value (value),
            to detect cytoplasm positive cells.
        i_exp: how many pixels should the nucleus be extended to be regarded as the whole cell?
            how wide should the doughnut be, regarded as cytoplasm?
            default setting is 5, though this value  depends on your pixel size.
        i_mem: how many pixels should the nucleus or cell border to the inside be extended to be regarded as membrane?
            how many pixels should the nucleus or cell border be extended to the inside and outside, to be regarded as adjacent?
            default setting is 2, though this value depends on your pixel size.
        i_shrink: shrink value that will be used if marker are patched against bleed through.
            note that this value have already been used for feature_extraction to be used here.
        es_shrink_marker: optional against bleed through, list of shrunken marker
            that should replace nucleus, exp{i_exp}, perinuc{i_exp}, or cytoplasm.
        es_custom_markerpartition: set of strings to specify markers with specific partitions that should be kept.
            the marker_partition have to be found as column labels in the raw feature extracted file.
            the marker has to define the exact partition.
        des_cytoplasm_marker: dictionary of sets of strings to specify cytoplasm marker.
            these are markers that are expressed in the cytoplasm in s_seg_markers positive cells.
            the marker do not have to define the exact partition.
        s_tissue_dapi: by dapi and round marker label specify the image which should be used for tissue detection.
        i_tissue_dapi_thresh: dapi threshold value for tissue, which will be much lower than the dapi positive nucleus value,
            in our experience, something between 300 and 600.
        i_tissue_area_thresh: specify pixel area threshold to use to fill tissue gaps between dapi nuclei.
        ds_shape: dictionary which defines which original feature to take (key)
            for nucleus, cell, and cytoplasm shape values,
            and how the features should be named by standard (value).
        ds_centroid: dictionary which define original nucleus segmentation centroid (key),
            and how they should be named by standard (value).
            the keys from the default dictionary is cellpose compatible.

        # file system
        s_afsubdir: auto fluorescent subtracted registered image directory or registered image.
        s_format_afsubdir: subfolder structure in s_afsubdir. one subfolder per slide_pxscene.
        s_segdir: directory where segmentation basin, feature extraction, and xy cell position files can be found.
        s_format_segdir_cellpose: subfolder structure in segmentation directory.
        s_qcdir: directory where qc plots can be found.

    output:
        several csv files, tiff files, and plots.

    description:
        runs feature extraction with all patches and filters.
    '''
    # handle input
    es_marker_needed = es_dapipartition_filter.copy()
    s_seg_markers = None
    es_seg_marker = None
    if not (di_seg_marker is None):
        es_seg_marker = set(di_seg_marker.keys())
        s_seg_markers = '.'.join(sorted(es_seg_marker))
        es_marker_needed = es_marker_needed.union(es_seg_marker)

    # generate features_{s_slide}_CentroidXY.csv files
    df_xy = filter_cellpose_xy(
        s_slide = s_slide,
        es_seg_marker = es_seg_marker,  # ECE for filename to load
        ds_centroid = ds_centroid,
        s_tissue_dapi = s_tissue_dapi,
        i_tissue_dapi_thresh = i_tissue_dapi_thresh,
        i_tissue_area_thresh = i_tissue_area_thresh,
        s_afsubdir = s_afsubdir,
        s_format_afsubdir = s_format_afsubdir,
        s_segdir = s_segdir,
        s_format_segdir_cellpose = s_format_segdir_cellpose,
    )
    print('SHAPE centroid xy from raw feature:', df_xy.shape, '\n')

    # load threshold and round parameter file
    df_img_thresh = thresh.load_thresh_df(
        s_slide = s_slide,
        s_afsubdir = s_afsubdir,
    )
    # load mean intensity segmentation feature datatframe
    df_mi = load_cellpose_features_df(
        s_slide = s_slide,  # filename to load
        es_seg_marker = es_seg_marker, # ECE: for filename to load
        s_afsubdir = s_afsubdir,  # filename to load
        s_segdir = s_segdir,  # file
        s_format_segdir_cellpose = s_format_segdir_cellpose,  # file
    )
    print('SHAPE df feature raw load:', df_mi.shape, '\n')
    if not (di_seg_marker is None):
        for s_seg_marker, i_seg_marker in di_seg_marker.items():
            print(f'{s_seg_marker}_cytoplasm > {i_seg_marker}:', sum(df_mi.loc[:,f'{s_seg_marker}_cytoplasm'] > i_seg_marker))
            print(f'{s_seg_marker}_cytoplasm < {i_seg_marker}:', sum(df_mi.loc[:,f'{s_seg_marker}_cytoplasm'] < i_seg_marker))
            print(f'{s_seg_marker}_cytoplasm is NA:', sum(df_mi.loc[:,f'{s_seg_marker}_cytoplasm'].isna()))
            print(f'not {s_seg_marker}_cytoplasm > {i_seg_marker}:', sum(~(df_mi.loc[:,f'{s_seg_marker}_cytoplasm'] > i_seg_marker)))

    # detect cytoplasm negative cells
    #_fill_cellpose_nas(
    _thresh_cytoplasm(
        df_mi = df_mi,
        di_seg_marker = di_seg_marker,  # ECE: tricky
    )
    print('SHAPE df feature after detecting cytoplasm negative cells:', df_mi.shape, '\n')
    # patch bleed through by shrunk marker.
    #_shrunk_seg_regions(
    _patch_bleedthrough(
        df_mi = df_mi,
        es_shrink_marker = es_shrink_marker, # list of shrunken marker that should replace perinuc{i_exp} or cytoplasm.
        i_exp = i_exp,
        i_shrink = i_shrink,
    )
    print('SHAPE df feature after bleed through patching:', df_mi.shape, '\n')
    # patch cells without cytoplasm:
    #_fill_cellpose_nas(
    _patch_nucleus_without_cytoplasm(
            df_mi = df_mi,  # ECE: contains cytoplasm_negative column
        i_exp = i_exp,
    )
    print('SHAPE df feature after nucleus without cytoplasm patching:', df_mi.shape)
    if not (di_seg_marker is None):
        for s_seg_marker, i_seg_marker in di_seg_marker.items():
            print(f'{s_seg_marker}_cytoplasm > {i_seg_marker}:', sum(df_mi.loc[:,f'{s_seg_marker}_cytoplasm'] > i_seg_marker))
            print(f'{s_seg_marker}_cytoplasm < {i_seg_marker}:', sum(df_mi.loc[:,f'{s_seg_marker}_cytoplasm'] < i_seg_marker))
            print(f'{s_seg_marker}_cytoplasm is NA:', sum(df_mi.loc[:,f'{s_seg_marker}_cytoplasm'].isna()))
            print(f'not {s_seg_marker}_cytoplasm > {i_seg_marker}:', sum(~(df_mi.loc[:,f'{s_seg_marker}_cytoplasm'] > i_seg_marker)), '\n')
    # patch nuc and cell membrane marker with weak signal
    #_fill_bright_nas(
    _patch_weak_membrane_marker(
        df_mi = df_mi,
        es_seg_marker = es_seg_marker,  # ECE: tricky
        i_exp = i_exp,
        i_mem = i_mem,
    )
    print('SHAPE df feature after weak cell membrane marker patching:', df_mi.shape, '\n')
    # filter for nuclei, perinuc5, nucmem2, cellmem2 according to config.es_markerpartition_standard
    # and marker specified by es_cyto_marker, es_custom_markerpartition, and es_shape.
    #filter_loc_cellpose(
    df_mi = _filter_cellpartition_and_shape(
        df_mi = df_mi,
        es_seg_marker = es_seg_marker,  # ECE: tricky
        des_cytoplasm_marker = des_cytoplasm_marker,  # have not to specify cell partiton # ECE tricky
        es_custom_markerpartition = es_custom_markerpartition, # have to specify cell partition
        i_exp = i_exp,
        i_mem = i_mem,
        ds_shape = ds_shape,
        ds_centroid = ds_centroid,
    )
    print('SHAPE df feature after cell_partition and shape filtering:', df_mi.shape, '\n')
    r_last_round, es_marker_todrop = basic.find_last_round(
        df_img = df_img_thresh,  # this is actually the thresholdli file, could be another one.
        es_marker_needed = es_marker_needed, # e.g. ('DAPI2_nuc','DAPI11_nuc','Ecad')
    )
    drop_marker(
        df_mi, # mean intensity values
        es_marker_todrop = es_marker_todrop,
    )
    print('SHAPE df feature after drop last round:', df_mi.shape, '\n')
    # apply threshold
    # jenny 2021-07-14: this li auto threshold works only for dapi and is used for filtering dapi positive cells!
    # bue 2022-12-20: possible to supersede li with manual threshold and add centroid coordinates to the frame.
    #auto_threshold(
    dfb_thresh = thresh.apply_thresh(
        df_mi = df_mi,  # from load_cellpose_feature_df
        df_img_thresh = df_img_thresh,  # from load_thresh_df
        di_manual_thresh = di_seg_marker, # ECE: to supersede auto threshold
        ds_centroid = ds_centroid, # to add centroid coordinates
    )
    print(f'SHAPE df feature after apply_thresh. input: {df_mi.shape} | output: {dfb_thresh.shape}', '\n')
    # filter dapi
    # generate qc line plot for tissue loss (defined by dapi)
    # filter by cell positive for DAPI auto threshold, in round specified in es_dapipartition_filter
    #filter_dapi_cellpose(
    df_mi = _filter_dapi_positive(
        df_mi = df_mi,
        dfb_thresh = dfb_thresh,
        es_dapipartition_filter = es_dapipartition_filter,
        s_qcdir = s_qcdir,
        s_segdir = s_segdir, # QC folder subpath
        #s_format_segdir_cellpose = s_format_segdir_cellpose,
    )
    dfb_thresh = dfb_thresh.loc[df_mi.index,:]
    # bue 20210624: if dapi2 should be renamed to dapi and all other dapi should be dropped, this has to be here.

    print('SHAPE df feature after dapi_positive filtering:', df_mi.shape)
    if not (di_seg_marker is None):
        for s_seg_marker, i_seg_marker in di_seg_marker.items():
            print(f'{s_seg_marker}_cytoplasm > {i_seg_marker}:', sum(df_mi.loc[:,f'{s_seg_marker}_cytoplasm'] > i_seg_marker))
            print(f'{s_seg_marker}_cytoplasm < {i_seg_marker}:', sum(df_mi.loc[:,f'{s_seg_marker}_cytoplasm'] < i_seg_marker))
            print(f'{s_seg_marker}_cytoplasm is NA:', sum(df_mi.loc[:,f'{s_seg_marker}_cytoplasm'].isna()))
            print(f'not {s_seg_marker}_cytoplasm > {i_seg_marker}:', sum(~(df_mi.loc[:,f'{s_seg_marker}_cytoplasm'] > i_seg_marker)), '\n')
    # write df_mi to file at s_segdir (not s_format_segdir)
    s_path_seg = s_format_segdir_cellpose.format(s_segdir, s_slide)
    s_filter_dapi = '_'.join([s_filter.split('_')[0] for s_filter in sorted(es_dapipartition_filter)])
    s_ofile = config.d_nconv['s_format_csv_patched_shape_meanintenisty'].format(s_slide, s_seg_markers, s_filter_dapi, df_mi.index.name) # ECE: file name
    print(f'write file: {s_ofile}')
    df_mi.loc[df_mi.slide == s_slide].to_csv(s_path_seg + s_ofile)

    # generate qc plot for tissue loss (dapi) and cancer cells (seg)
    _plot_thresh_result_dapiseg(
        dfb_thresh = dfb_thresh,  # scatter plot data all filtered objects
        df_img_thresh = df_img_thresh,  # only used to plot the value
        di_seg_marker = di_seg_marker, # ECE: filter and used to plot the value
        df_xy = df_xy,  # scatter plot data all segmented objects
        s_qcdir = s_qcdir,  # 'QC/',
        s_segdir = config.d_nconv['s_segdir'],  #'Segmentation/',  (QC subdir)
        #s_format_segdir_cellpose = s_format_segdir_cellpose,  #'{}{}_CellposeSegmentation/',  # s_segdir, s_slide
    )


# spawner function
def filter_features_spawn(
        es_slide,
        es_dapipartition_filter,  # {'DAPI1_nuclei','DAPI2_nuclei','DAPI16_nuclei'},
        di_seg_marker, # {'Ecad': 1000} # ECE
        i_exp = 5,  # number of pixel for cytoplasm doughnut. microscope dependent!
        i_mem = 2,  # number of pixel for membrane. microscope dependent!
        i_shrink = 0, # optional, patching against bleed trough.
        es_shrink_marker = set(), # optional against bleed through list of shrunken marker that should replace nucleus, exp{i_exp}, perinuc{i_exp}, or cytoplasm.
        es_custom_markerpartition = set(),  # optional
        des_cytoplasm_marker = config.des_cytoplasmmarker_standard,  # optional, listing of cytoplasm markers, from di_seg_marker.key() positive cells.
        s_tissue_dapi = 'DAPI1',
        i_tissue_dapi_thresh = 500,  # 300 512 600
        i_tissue_area_thresh = 50000,  # 65536
        ds_shape = {
            'DAPI2_nuclei_area':'nuclei_area',
            'DAPI2_nuclei_eccentricity':'nuclei_eccentricity',
            'Ecad_cell_area':'cell_area',
            'Ecad_cell_eccentricity':'cell_eccentricity',
            'Ecad_cell_euler':'cell_euler',
            'Ecad_cytoplasm_area':'cytoplasm_area',
            'Ecad_cytoplasm_eccentricity':'cytoplasm_eccentricity',
            'Ecad_cytoplasm_euler':'cytoplasm_euler',
        },
        ds_centroid = {
            'DAPI2_nuclei_centroid-0': 'DAPI_Y',
            'DAPI2_nuclei_centroid-1': 'DAPI_X',
        },
        # processing
        s_type_processing = 'slurm',
        s_slurm_partition = 'exacloud',
        s_slurm_mem = '32G',
        s_slurm_time = '36:00:0',
        s_slurm_account = 'gray_lab',
        # file system
        s_afsubdir = config.d_nconv['s_regdir'],  #'SubtractedRegisteredImages/' or 'RegisteredImages/',
        s_format_afsubdir = config.d_nconv['s_format_regdir'],  # {}{}/,  s_afsubdir, slide_scene
        s_segdir = config.d_nconv['s_segdir'],  #'Segmentation/',
        s_format_segdir_cellpose = config.d_nconv['s_format_segdir_cellpose'],  #'{}{}_CellposeSegmentation/',  # s_segdir, s_slide
        s_qcdir = config.d_nconv['s_qcdir'],  #'QC',
    ):
    '''
    version: 2021-12-00

    input:
        es_slide: set of slide ids to process.
        es_dapipartition_filter: list of all DAPIn_nuclei (n is the round number) that should be used as filer.
            use qc images to define! usually DAPI1 and last good DAPI, and additional bad rounds in between.
        di_seg_marker: dictionary of cytoplasm segmentation marker (key) and manual threshold value (value),
            to detect cytoplasm positive cells.
        i_exp: how many pixels should the nucleus be extended to be regarded as the whole cell?
            how wide should the doughnut be, regarded as cytoplasm?
            default setting is 5, though this value  depends on your pixel size.
        i_mem: how many pixels should the nucleus or cell border to the inside be extended to be regarded as membrane?
            how many pixels should the nucleus or cell border be extended to the inside and outside, to be regarded as adjacent?
            default setting is 2, though this value depends on your pixel size.
        i_shrink: shrink value that will be used if marker are patched against bleed through.
            note that this value have already been used for feature_extraction to be used here.
        es_shrink_marker: optional against bleed through, list of shrunken marker
            that should replace nucleus, exp{i_exp}, perinuc{i_exp}, or cytoplasm.
        es_custom_markerpartition: set of strings to specify markers with specific partitions that should be kept.
            the marker_partition have to be found as column labels in the raw feature extracted file.
            the marker has to define the exact partition.
        des_cytoplasm_marker: dictionary of sets of strings to specify cytoplasm marker.
            these are markers that are expressed in the cytoplasm in s_seg_markers positive cells.
            the marker do not have to define the exact partition.
        s_tissue_dapi: by dapi and round marker label specify the image which should be used for tissue detection.
        i_tissue_dapi_thresh: dapi threshold value for tissue, which will be much lower than the dapi positive nucleus value,
            in our experience, something between 300 and 600.
        i_tissue_area_thresh: specify pixel area threshold to use to fill tissue gaps between dapi nuclei.
        ds_shape: dictionary which defines which original feature to take (key)
            for nucleus, cell, and cytoplasm shape values,
            and how the features should be named by standard (value).
        ds_centroid: dictionary which define original nucleus segmentation centroid (key),
            and how they should be named by standard (value).
            the keys from the default dictionary is cellpose compatible.

        # processing
        s_type_processing: string to specify if pipeline is run on a slurm cluster or not.
            known vocabulary is slurm and any other string for non-slurm processing.
        s_slurm_partition: slurm cluster partition to use.
            OHSU ACC options are 'exacloud', 'light', (and 'gpu').
            the default is tweaked to OHSU ACC settings.
        s_slurm_mem: slurm cluster memory allocation. format '64G'.
        s_slurm_time: slurm cluster time allocation in hour or day format.
            OHSU ACC max is '36:00:00' [hour] or '30-0' [day].
            the related qos code is tweaked to OHSU ACC settings.
        s_slurm_account: slurm cluster account to credit time from.
            OHSU ACC options are e.g. 'gray_lab', 'chin_lab', 'heiserlab', 'CEDAR'.

        # file system
        s_afsubdir: auto fluorescent subtracted registered image directory or registered image.
        s_format_afsubdir: subfolder structure in s_afsubdir. one subfolder per slide_pxscene.
        s_segdir: directory where segmentation basin, feature extraction, and xy cell position files can be found.
        s_format_segdir_cellpose: subfolder structure in segmentation directory.
        s_qcdir: directory where qc plots can be found.

    output:
        several csv files, tiff files, and plots.

    description:
        spawn function to run the feat.extract_features function.
    '''
    # handle input
    s_input = s_afsubdir.split('/')[-2].lower()

    # for each slide
    for s_slide in sorted(es_slide):
        # this has to be a python template!
        print(f'filter_features_spawn: {s_slide} {s_input}')

        # set run commands
        s_pathfile_template = 'template_filterfeatures_slide.py'
        s_pathfile = f'filterfeature_slide_{s_slide}_{".".join(sorted(di_seg_marker.keys()))}_{s_input}.py'
        s_srun_cmd = f'python3 {s_pathfile}'
        ls_run_cmd = ['python3', s_pathfile]

        ## any ##
        # load template fiter feature script code
        with open(f'{s_path_module}src/{s_pathfile_template}') as f:
            s_stream = f.read()

        # edit code generic
        s_stream = s_stream.replace('peek_s_slide', s_slide)
        s_stream = s_stream.replace('peek_es_dapipartition_filter', str(es_dapipartition_filter))
        s_stream = s_stream.replace('peek_di_seg_marker', str(di_seg_marker)) # ECE
        s_stream = s_stream.replace('peek_i_exp', str(i_exp))
        s_stream = s_stream.replace('peek_i_mem', str(i_mem))
        s_stream = s_stream.replace('peek_i_shrink', str(i_shrink))
        s_stream = s_stream.replace('peek_des_cytoplasm_marker', str(des_cytoplasm_marker))  # ECE
        s_stream = s_stream.replace('peek_es_custom_markerpartition', str(es_custom_markerpartition))
        s_stream = s_stream.replace('peek_es_shrink_marker', str(es_shrink_marker))
        s_stream = s_stream.replace('peek_s_tissue_dapi', s_tissue_dapi)
        s_stream = s_stream.replace('peek_i_tissue_dapi_thresh', str(i_tissue_dapi_thresh))
        s_stream = s_stream.replace('peek_i_tissue_area_thresh', str(i_tissue_area_thresh))
        s_stream = s_stream.replace('peek_ds_shape', str(ds_shape))
        s_stream = s_stream.replace('peek_ds_centroid', str(ds_centroid))
        s_stream = s_stream.replace('peek_s_afsubdir', s_afsubdir)
        s_stream = s_stream.replace('peek_s_format_afsubdir', s_format_afsubdir)
        s_stream = s_stream.replace('peek_s_segdir', s_segdir)
        s_stream = s_stream.replace('peek_s_format_segdir_cellpose', s_format_segdir_cellpose)
        s_stream = s_stream.replace('peek_s_qcdir', s_qcdir)

        # write executable filter feature script code to file
        time.sleep(4)
        with open(s_pathfile, 'w') as f:
            f.write(s_stream)

        # execute filter feature script
        time.sleep(4)
        if (s_type_processing == 'slurm'):
            # generate sbatch file
            s_pathfile_sbatch = f'filterfeature_slide_{s_slide}_{".".join(sorted(di_seg_marker.keys()))}_{s_input}.sbatch'
            config.slurmbatch(
                s_pathfile_sbatch = s_pathfile_sbatch,
                s_srun_cmd = s_srun_cmd,
                s_jobname = f'f{s_slide}',
                s_partition = s_slurm_partition,
                s_gpu = None,
                s_mem = s_slurm_mem,
                s_time = s_slurm_time,
                s_account = s_slurm_account,
            )
            # Jenny, this is cool!
            subprocess.run(
                ['sbatch', s_pathfile_sbatch],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
        else:  # non-slurm
            # Jenny, this is cool!
            s_file_stdouterr = f'slurp-filterfeature_slide_{s_slide}_{".".join(sorted(di_seg_marker.keys()))}_{s_input}.out'
            o_process = subprocess.run(
                ls_run_cmd,
                stdout=open(s_file_stdouterr, 'w'),
                stderr=subprocess.STDOUT,
            )


###################################
#  combine nucleus and cell label #
###################################

# def combine_labels
def feature_correct_labels(
        s_slide,
        di_seg_marker,  # {'Ecad': 1000}  # ECE
        i_exp = 5,  # number of pixel for cytoplasm doughnut. microscope dependent!
        # file system
        s_afsubdir = config.d_nconv['s_regdir'],  #'SubtractedRegisteredImages/', or 'RegisteredImages/'
        s_segdir = config.d_nconv['s_segdir'],  #'Segmentation/',
        s_format_segdir_cellpose = config.d_nconv['s_format_segdir_cellpose'],  #'{}{}_CellposeSegmentation/',  # s_segdir, s_slide
    ):
    '''
    version: 2021-12-00

    input:
        s_slide:  slide id from which nucleus and cell segmentation labels tiffs should be combined.
        di_seg_marker: dictionary of cytoplasm segmentation marker (key) and manual threshold value (value),
            to detect cytoplasm positive cells.
        i_exp: how many pixels should the nucleus be extended to be regarded as the whole cell?
            how wide should the doughnut be, regarded as cytoplasm?
            default setting is 5, though this value  depends on your pixel size.

        # file system
        s_afsubdir: auto fluorescence subtracted registered images directory or registered image directory.
        s_segdir: directory where segmentation basin, feature extraction, and xy cell position files can be found.
        s_format_segdir_cellpose: subfolder structure in segmentation directory.

    output:
        combined cell and expanded nucleus label file into a new cell label file,
        the name is specified by const.d_nconv['s_format_tiff_celllabel_nuccellmatchedfeat'].
        json files to keep track of touching cells or cells with more than one nucleus!
        the name is specified by const.d_nconv['s_format_json_celltouch_segmentation']

    description:
        function loads nucleus matched cell labels;
        delete cells that were not used for cytoplasm (i.e. ecad neg).
        loads nuc labels, extend nucleus to perinuc{i_exp}.
        merge cell and nucles labels.
        save final celln_exp5_CellSegmentationBasins.tif basins file.
        keep track of cells that are completely covered by another cell or more: counts as touching.
    '''
    # handle input
    if (di_seg_marker is None):
        sys.exit('Error @ jinxif.feat.feature_correct_labels : it does not make sense to run this function with es_seg_marker is None. {es_seg_marker}')
    else:
        es_seg_marker = set(di_seg_marker.keys())
        s_seg_markers = '.'.join(sorted(es_seg_marker))

    # reset cell touch output variable
    ddls_touch = {}

    # load mean intensity segmentation raw feature data frame
    # in this function only needed because {s_thresh}_negative column is needed.
    df_mi = load_cellpose_features_df(
        s_slide = s_slide,
        es_seg_marker = es_seg_marker,  # ECE: for filename to load
        s_afsubdir = s_afsubdir,
        s_segdir = s_segdir,
        s_format_segdir_cellpose = s_format_segdir_cellpose,
    )

    # get cells without cytoplasm
    _thresh_cytoplasm(
        df_mi = df_mi,
        di_seg_marker =  di_seg_marker,  # ECE: tricky
    )

    # handle input
    s_path_seg = s_format_segdir_cellpose.format(s_segdir, s_slide)
    s_ipath = s_path_seg
    s_opath = s_path_seg

    # for each file in input path
    #for s_slide_pxscene in sorted(df_mi.loc[df_mi.slide==s_slide, 'slide_scene'].unique()):
    for s_file in sorted(os.listdir(s_ipath)):
        print(f'check: {config.d_nconv["s_regex_tiff_celllabel_nuccellmatched"]} {s_file} ...')

        # find matched nucleus cell segmentation label file
        o_match = re.search(config.d_nconv['s_regex_tiff_celllabel_nuccellmatched'], s_file)
        if not (o_match is None):
            # extract slide_pxscene and nucleus diameter
            # bue: actually position depends on the s_regex_tiff_celllabel_nuccellmatched regex
            # bue: could be resolved with additional dict
            #s_slide_pxscene = s_slide_fscene.replace('-Scene-','_scene')  # bue: caused by ugle filename convention
            s_slide = o_match[config.d_nconv['di_regex_tiff_celllabel_nuccellmatched']['s_slide']]
            s_pxscene = o_match[config.d_nconv['di_regex_tiff_celllabel_nuccellmatched']['s_pxscene']]
            s_seg_markers_file = o_match[config.d_nconv['di_regex_tiff_celllabel_nuccellmatched']['s_seg_markers']]
            i_nuc_diam = int(o_match[config.d_nconv['di_regex_tiff_celllabel_nuccellmatched']['i_nuc_diam']])
            i_cell_diam = int(o_match[config.d_nconv['di_regex_tiff_celllabel_nuccellmatched']['i_cell_diam']])
            s_slide_pxscene = f'{s_slide}_{s_pxscene}'
            s_slide_fscene = s_slide_pxscene

            # check for s_thresh_marker
            if (s_seg_markers == s_seg_markers_file):  # ECE

                # load files
                print(f'Processing combined segmentaiton labels for {s_slide_pxscene}')
                ai_label_nuc = io.imread(s_ipath + config.d_nconv['s_format_tiff_celllabel_nuc'].format(s_slide_fscene, i_nuc_diam))
                ai_label_cell = io.imread(s_ipath + config.d_nconv['s_format_tiff_celllabel_nuccellmatched'].format(s_slide_fscene, s_seg_markers, i_nuc_diam, i_cell_diam))

                # set non-ecad cell labels to zero
                ai_cell_zero = df_mi.loc[(df_mi.slide_scene == s_slide_pxscene) & df_mi.loc[:,f'cytoplasm_negative'],'cellid'].values
                ai_mask = np.isin(ai_label_cell, ai_cell_zero)
                ai_label_cell[ai_mask] = 0

                # extend nuclei for non-ecad cells
                # bue : _patch_nucleus_without_cytoplasm only takes care of the feature value not the segmentation mask.
                ai_label_nucexp = _exp_label(ai_labels=ai_label_nuc, i_distance=i_exp) # bue: this default distance!
                ai_label_nucexp[ai_label_cell > 0] = 0

                # combine calls and extend nuclei
                ai_label_cellnucexp = ai_label_nucexp + ai_label_cell

                # save ai_label_cellnucexp to file at s_segdir not s_path_seg
                s_ofile = config.d_nconv['s_format_tiff_celllabel_nuccellmatchedfeat'].format(s_slide_fscene, s_seg_markers, i_nuc_diam, i_cell_diam, i_exp)
                io.imsave(s_opath + s_ofile, ai_label_cellnucexp, check_contrast=False)

                # figure out the covered cells...labels + combined
                # some Jenny magic!
                ai_not_zero_pixels =  np.array([ai_label_nuc.ravel() !=0, ai_label_cellnucexp.ravel() !=0]).all(axis=0)
                ai_tups = np.array([ai_label_cellnucexp.ravel()[ai_not_zero_pixels], ai_label_nuc.ravel()[ai_not_zero_pixels]]).T # combined over nuclei
                ai_unique_rows = np.unique(ai_tups, axis=0)

                # generate cell touching dictionary
                dei_touch = {}
                for i_cell, i_touch in ai_unique_rows:
                    if i_cell != i_touch:
                        if i_cell in dei_touch:
                            dei_touch[i_cell].add(i_touch)
                        else:
                            dei_touch[i_cell] = {i_touch}
                dls_touch = {}
                for i_cell, ei_touch in dei_touch.items():
                    dls_touch.update({str(i_cell): [str(i_touch) for i_touch in sorted(ei_touch)]})
                ddls_touch.update({s_slide_pxscene: dls_touch})

    # save ddls_touch as json file
    with open(s_path_seg + config.d_nconv['s_format_json_celltouch_segmentation'].format(s_slide, s_seg_markers), 'w') as f:
        json.dump(ddls_touch, f)


# spawner function
def feature_correct_labels_spawn(
        es_slide,
        di_seg_marker,  # {'Ecad': 1000} # ECE
        i_exp = 5,  # number of pixel for cytoplasm doughnut. microscope dependent!
        # processing
        s_type_processing = 'slurm',
        s_slurm_partition = 'exacloud',
        s_slurm_mem = '32G',
        s_slurm_time = '36:00:0',
        s_slurm_account = 'gray_lab',
        # file system
        s_afsubdir = config.d_nconv['s_regdir'],  #'SubtractedRegisteredImages/', or 'RegisteredImages/'
        s_segdir = config.d_nconv['s_segdir'],  #'Segmentation/',
        s_format_segdir_cellpose = config.d_nconv['s_format_segdir_cellpose'],  #'{}{}_CellposeSegmentation/',  # s_segdir, s_slide
    ):
    '''
    version: 2021-08-05

    input:
        es_slide: set of slide ids to process.
        di_seg_marker: dictionary of cytoplasm segmentation marker (key) and manual threshold value (value),
            to detect cytoplasm positive cells.
        i_exp: how many pixels should the nucleus be extended to be regarded as the whole cell?
            how wide should the doughnut be, regarded as cytoplasm?
            default setting is 5, though this value  depends on your pixel size.

        # processing
        s_type_processing: string to specify if pipeline is run on a slurm cluster or not.
            known vocabulary is slurm and any other string for non-slurm processing.
        s_slurm_partition: slurm cluster partition to use.
            OHSU ACC options are 'exacloud', 'light', (and 'gpu').
            the default is tweaked to OHSU ACC settings.
        s_slurm_mem: slurm cluster memory allocation. format '64G'.
        s_slurm_time: slurm cluster time allocation in hour or day format.
            OHSU ACC max is '36:00:00' [hour] or '30-0' [day].
            the related qos code is tweaked to OHSU ACC settings.
        s_slurm_account: slurm cluster account to credit time from.
            OHSU ACC options are e.g. 'gray_lab', 'chin_lab', 'heiserlab', 'CEDAR'.

        # file system
        s_afsubdir: auto fluorescence subtracted registered images directory or registered image directory.
        s_segdir: directory where segmentation basin, feature extraction, and xy cell position files can be found.
        s_format_segdir_cellpose: subfolder structure in segmentation directory.

    output:
        combined cell and nucleus basin label tiff file.
        cell touch json file.

    description:
        spawn function to run the feat.feature_correct_labels function.
    '''
    # for each slide
    for s_slide in sorted(es_slide):
        # these have to be a python template!
        print(f'feature_correct_labels_spawn: {s_slide}')

        # set run commands
        s_pathfile_template = 'template_featurecorrectlabels_slide.py'
        s_pathfile = f'featurecorrectlabels_slide_{s_slide}.py'
        s_srun_cmd = f'python3 {s_pathfile}'
        ls_run_cmd = ['python3', s_pathfile]

        ## any ##
        # load template fiter feature script code
        with open(f'{s_path_module}src/{s_pathfile_template}') as f:
            s_stream = f.read()

        # edit code generic. order matters!
        s_stream = s_stream.replace('peek_s_slide', s_slide)
        s_stream = s_stream.replace('peek_di_seg_marker', str(di_seg_marker))
        s_stream = s_stream.replace('peek_i_exp', str(i_exp))
        # file system
        s_stream = s_stream.replace('peek_s_afsubdir', s_afsubdir)
        s_stream = s_stream.replace('peek_s_segdir', s_segdir)
        s_stream = s_stream.replace('peek_s_format_segdir_cellpose', s_format_segdir_cellpose)

        # write executable feature correct labels script code to file
        time.sleep(4)
        with open(s_pathfile, 'w') as f:
            f.write(s_stream)

        # execute feature correct labels script
        time.sleep(4)
        if (s_type_processing == 'slurm'):
            # generate sbatch file
            s_pathfile_sbatch = f'featurecorrectlabels_slide_{s_slide}.sbatch'
            config.slurmbatch(
                s_pathfile_sbatch = s_pathfile_sbatch,
                s_srun_cmd = s_srun_cmd,
                s_jobname = f'l{s_slide}',
                s_partition = s_slurm_partition,
                s_gpu = None,
                s_mem = s_slurm_mem,
                s_time = s_slurm_time,
                s_account = s_slurm_account,
            )
            # Jenny, this is cool!
            subprocess.run(
                ['sbatch', s_pathfile_sbatch],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
        else:  # non-slurm
            # Jenny, this is cool!
            s_file_stdouterr = f'slurp-featurecorrectlabels_slide_{s_slide}.out'
            o_process = subprocess.run(
                ls_run_cmd,
                stdout=open(s_file_stdouterr, 'w'),
                stderr=subprocess.STDOUT,
            )

