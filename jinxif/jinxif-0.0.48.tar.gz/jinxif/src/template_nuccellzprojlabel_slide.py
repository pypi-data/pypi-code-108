########
# title: template_nuccellzprojlabel_slide.py
#
# author: Jenny, bue
# license: GPLv>=3
# version: 2021-06-25
#
# description:
#     template script for python base qc for nuc and cell z projection segmentation label files.
#
# instruction:
#     use jinxif.segment.nuccell_zprojlabel_imgs_spawn function to generate and run executable from this template.
#####

# libraries
from jinxif import _version
from jinxif import segment
import resource
import time

# set variables
poke_s_slide = 'peek_s_slide'
poke_es_seg_marker = peek_es_seg_marker
poke_s_tissue_dapi = 'peek_s_tissue_dapi'
poke_i_tissue_dapi_thresh = peek_i_tissue_dapi_thresh
poke_i_tissue_area_thresh = peek_i_tissue_area_thresh
poke_s_segdir = 'peek_s_segdir'
poke_s_format_segdir_cellpose = 'peek_s_format_segdir_cellpose'
poke_s_qcdir = 'peek_s_qcdir'

# off we go!
print(f'run jinxif.segment.nuccell_zprojlabel_imgs on {poke_s_slide} {sorted(poke_es_seg_marker)} ...')
r_time_start = time.time()

# generate zprojection nuccell label tissue edge distance qc plot
segment.nuccell_zprojlabel_imgs(
    s_slide = poke_s_slide,
    es_seg_marker = poke_es_seg_marker,
    s_tissue_dapi = poke_s_tissue_dapi, # 'DAPI1'
    i_tissue_dapi_thresh = poke_i_tissue_dapi_thresh, # 500
    i_tissue_area_thresh = poke_i_tissue_area_thresh, # 50000
    s_segdir = poke_s_segdir,  # input
    s_format_segdir_cellpose = poke_s_format_segdir_cellpose,  # s_segdir, s_slide
    s_qcdir = poke_s_qcdir,  # output
)

# rock to the end
r_time_stop = time.time()
print('done jinxif.segment.nuccell_zprojlabel_imgs!')
print(f'run time: {(r_time_stop - r_time_start) / 3600}[h]')
print(f'run max memory: {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1000000}[GB]')
print('you are running jinxif version:', _version.__version__)
