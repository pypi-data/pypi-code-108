########
# title: template_vizrawimage_slide.py
#
# author: Jenny, bue
# license: GPLv>=3
# version: 2021-06-25
#
# description:
#     template script for python base raw image qc plot generation.
#
# instruction:
#     use jinxif.regsit.visualize_raw_images_spawn function to generate and run executable from this template.
#####

# libraries
from jinxif import _version
from jinxif import sane
import resource
import time

# set variables
poke_s_slide = 'peek_s_slide'
poke_s_color = 'peek_s_color'
poke_s_rawdir = 'peek_s_rawdir'
poke_s_format_rawdir = 'peek_s_format_rawdir'
poke_s_qcdir = 'peek_s_qcdir'

# off we go
print(f'run jinxif.sane.visualize_raw_images on {poke_s_slide} {poke_s_color} ...')
r_time_start = time.time()

# visualize raw images for qc
sane.visualize_raw_images(
    s_slide = poke_s_slide,
    s_color = poke_s_color,
    s_rawdir = poke_s_rawdir,
    s_format_rawdir = poke_s_format_rawdir,  # s_path_rawdir, s_slide
    s_qcdir = poke_s_qcdir,
)

# rock to the end
r_time_stop = time.time()
print('done jinxif.sane.visualize_raw_images!')
print(f'run time: {(r_time_stop - r_time_start) / 3600}[h]')
print(f'run max memory: {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1000000}[GB]')
print('you are running jinxif version:', _version.__version__)
