########
# title: template_segmentation_match.py
#
# author: Jenny, bue
# license: GPLv>=3
# version: 2021-06-25
#
# description:
#     template script for python base nuc and cell segmentation cell label matching.
#
# instruction:
#     use jinxif.segment.segment_spawn function to generate and run executable from this template.
#####

# libraries
from jinxif import _version
from jinxif import segment
import resource
import time

# set variables
poke_s_slide_pxscene = 'peek_s_slide_pxscene'
poke_es_seg_marker = peek_es_seg_marker
poke_s_type_data = 'peek_s_type_data'
# file system
poke_s_segdir = 'peek_s_segdir'
poke_s_format_segdir_cellpose = 'peek_s_format_segdir_cellpose'

# off we go
print(f'run jinxif.segment.match_nuccell_labels on {poke_s_slide_pxscene} {sorted(poke_es_seg_marker)} ...')
r_time_start = time.time()

# match nuclei
segment.match_nuccell_labels(
    s_slide_pxscene = poke_s_slide_pxscene,
    es_seg_marker = poke_es_seg_marker,
    s_type_data = poke_s_type_data,
    # file system
    s_segdir = poke_s_segdir,
    s_format_segdir_cellpose = poke_s_format_segdir_cellpose, # s_segdir, s_slide
)

# rock to the end
r_time_stop = time.time()
print('done jinxif.segment.match_nuccell_labels!')
print(f'run time: {(r_time_stop - r_time_start) / 3600}[h]')
print(f'run max memory: {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1000000}[GB]')
print('you are running jinxif version:', _version.__version__)
