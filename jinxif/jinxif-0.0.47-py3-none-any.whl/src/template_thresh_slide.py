########
# title: template_autothresh_slide.py
#
# author: Jenny, bue
# license: GPLv>=3
# version: 2021-06-25
#
# description:
#     template script for python base if marker auto threshold.
#
# instruction:
#     use jinxif.thresh.auto_thresh_spawn function to generate and run executable from this template.
#####

# libraries
from jinxif import _version
from jinxif import thresh
import resource
import time

# set variables
poke_s_slide = 'peek_s_slide'
poke_s_afsubdir = 'peek_s_afsubdir'
poke_s_format_afsubdir = 'peek_s_format_afsubdir'

# off we go
print(f'run jinxif.thresh.auto_thresh on {poke_s_afsubdir} {poke_s_slide} ...')
r_time_start = time.time()

# auto threshold
thresh.auto_thresh(
    s_slide = poke_s_slide,
    s_afsubdir = poke_s_afsubdir,  # input and output
    s_format_afsubdir = poke_s_format_afsubdir,  # s_afsubdir, s_slide_scene
)

# rock to the end
r_time_stop = time.time()
print('done jinxif.thresh.auto_thresh!')
print(f'run time: {(r_time_stop - r_time_start) / 3600}[h]')
print(f'run max memory: {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1000000}[GB]')
print('you are running jinxif version:', _version.__version__)
