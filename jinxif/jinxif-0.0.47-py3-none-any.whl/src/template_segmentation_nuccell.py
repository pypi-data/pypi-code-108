########
# title: template_segmentation_cmif.py
#
# author: Jenny, bue
# license: GPLv>=3
# version: 2021-06-25
#
# description:
#     template script for python based nuc and cell segmentation, utilizing the cellpose library,
#
# instruction:
#     use jinxif.segment.segment_spawn function to generate and run executable from this template.
#####

# libraries
from jinxif import _version
from jinxif import segment
import resource
import sys
import time

# set variables
poke_s_task = 'peek_s_task'
poke_s_slide_pxscene = 'peek_s_slide_pxscene'
poke_s_tiff_dapi = 'peek_s_tiff_dapi'
poke_i_nuc_diam = peek_i_nuc_diam
poke_i_cell_diam = peek_i_cell_diam
poke_es_seg_marker = peek_es_seg_marker
poke_es_rare_marker = peek_es_rare_marker
# file system
poke_s_regdir = 'peek_s_regdir'
poke_s_format_regdir = 'peek_s_format_regdir'
poke_s_segdir = 'peek_s_segdir'
poke_s_format_segdir_cellpose = 'peek_s_format_segdir_cellpose'
# gpu
poke_b_gpu = peek_b_gpu

# off we go
print(f'run segmentation predicting: {poke_s_task} {poke_s_slide_pxscene} {sorted(poke_es_seg_marker)} ...')
r_time_start = time.time()

# nucleus segmentation
if poke_s_task in {'nuc', 'nuclei', 'nucleus', 'nuccell'}:
    print(f'segmenting nucleus: {poke_s_slide_pxscene}')
    # load with rescale intensity and save
    segment.segment_nuc_dapi(
        s_slide_pxscene = poke_s_slide_pxscene,
        s_tiff_dapi = poke_s_tiff_dapi,
        i_nuc_diam = poke_i_nuc_diam,
        # file system
        s_regdir = poke_s_regdir,
        s_format_regdir = poke_s_format_regdir,
        s_segdir = poke_s_segdir,
        s_format_segdir_cellpose = poke_s_format_segdir_cellpose,
        b_gpu = poke_b_gpu,
    )

# cell segmentation
if poke_s_task in {'cell', 'nuccell'}:
    print(f'segmenting cells: {poke_s_slide_pxscene} {sorted(poke_es_seg_marker)}')
    segment.segment_cell_zstack(
        s_slide_pxscene = poke_s_slide_pxscene,
        s_tiff_dapi = poke_s_tiff_dapi,
        i_cell_diam = poke_i_cell_diam,
        es_seg_marker = poke_es_seg_marker,
        es_rare_marker = poke_es_rare_marker,
        # file system
        s_regdir = poke_s_regdir,
        s_format_regdir = poke_s_format_regdir,
        s_segdir = poke_s_segdir,
        s_format_segdir_cellpose = poke_s_format_segdir_cellpose,
        b_gpu = poke_b_gpu,
    )

else:
    sys.exit(f'Error @ template_segmentation_cmif.py : Unknown segmentation poke_s_task: {poke_s_task}\nknown are nuclei, nucleus, nuc, cell, or nuccell.')

# rock to the end
r_time_stop = time.time()
print('done jinxif.segment.segment_nuc_dapi or jinxif.segment.segment_cell_zstack!')
print(f'run time: {(r_time_stop - r_time_start) / 3600}[h]')
print(f'run max memory: {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1000000}[GB]')
print('you are running jinxif version:', _version.__version__)
