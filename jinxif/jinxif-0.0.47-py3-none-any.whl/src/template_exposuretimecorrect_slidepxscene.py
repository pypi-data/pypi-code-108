#####
# title: template_exposuretimecorrect_slidepxscene.py
#
# author: Jenny, bue
# license: GPLv>=3
# version: 2021-07-30
#
# description:
#     template script for python based image exposure time correction.
#
# instruction:
#     use jinxif.regist.exposure_time_correct_spawn function to generate and run executable from this template.
#####

# library
from jinxif import _version
from jinxif import regist
import resource
import time

# input parameters
poke_s_slidepxscene = 'peek_s_slidepxscene'
poke_dd_marker_etc = peek_dd_marker_etc
poke_s_imagetype_original = 'peek_s_imagetype_original'
poke_s_regdir = 'peek_s_regdir'
poke_s_format_regdir = 'peek_s_format_regdir'

# off we go
print(f'run jinxif.regist.exposure_time_correct on {poke_s_slidepxscene} ...')
r_time_start = time.time()

# run exposure time correction
regist.exposure_time_correct(
    s_slidepxscene = poke_s_slidepxscene,
    dd_marker_etc = poke_dd_marker_etc,
    s_imagetype_original = poke_s_imagetype_original,
    # filesystem
    s_regdir = poke_s_regdir,
    s_format_regdir = poke_s_format_regdir,  # s_regdir, s_slide_pxscene
)

# rock to the end
r_time_stop = time.time()
print('done jinxif.regist.exposure_time_correct_spawn!')
print(f'run time: {(r_time_stop - r_time_start) / 3600}[h]')
print(f'run max memory: {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1000000}[GB]')
print('you are running jinxif version:', _version.__version__)
