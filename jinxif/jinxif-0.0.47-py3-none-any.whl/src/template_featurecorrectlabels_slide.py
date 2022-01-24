########
# title: template_featurecorrectlabels_slide.py
#
# author: Jenny, bue
# license: GPLv>=3
# version: 2021-06-25
#
# description:
#     template script for python base label file patching based on filtered, patched features.
#
# instruction:
#     use jinxif.feat.feature_correct_labels_spawn function to generate and run executable from this template.
#####

# libraries
from jinxif import _version
from jinxif import feat
import resource
import time

# set variables
poke_s_slide = 'peek_s_slide'
poke_di_seg_marker = peek_di_seg_marker
poke_i_exp = peek_i_exp
poke_s_afsubdir = 'peek_s_afsubdir'
poke_s_segdir = 'peek_s_segdir'
poke_s_format_segdir_cellpose = 'peek_s_format_segdir_cellpose'

# off we go
print(f'run jinxif.feat.feature_correct_labels on {poke_s_afsubdir} {poke_s_slide} {sorted(poke_di_seg_marker)} ...')
r_time_start = time.time()

# feature correct labels
feat.feature_correct_labels(
    s_slide = poke_s_slide,
    di_seg_marker = poke_di_seg_marker,
    i_exp = poke_i_exp,  # 5
    # file system
    s_afsubdir = poke_s_afsubdir,
    s_segdir = poke_s_segdir,
    s_format_segdir_cellpose = poke_s_format_segdir_cellpose,  # s_segdir, s_slide
)

# rock to the end
r_time_stop = time.time()
print('done jinxif.feature_correct_labels!')
print(f'run time: {(r_time_stop - r_time_start) / 3600}[h]')
print(f'run max memory: {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1000000}[GB]')
print('you are running jinxif version:', _version.__version__)
