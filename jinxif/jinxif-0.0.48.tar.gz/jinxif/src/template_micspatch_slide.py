########
# title: template_micspatch_slide.py
#
# author: Jenny, bue
# license: GPLv>=3
# version: 2021-09-15
#
# description:
#     template script for python based miltenyi macsima stitching line patching.
#
# instruction:
#     use jinxif.mics.patch_spawn function to generate and run executable from this template.
#####

# libraries
from jinxif import _version
from jinxif import mics
import resource
import time

# set variables
poke_s_slide = 'peek_s_slide'
poke_s_afsubdir = 'peek_s_afsubdir'
poke_s_format_afsubdir = 'peek_s_format_afsubdir'
poke_s_segdir = 'peek_s_segdir'
poke_s_format_segdir_cellpose = 'peek_s_format_segdir_cellpose'

# off we go
print(f'run jinxif.mics.patch_stichlines on {poke_s_slide} ...')
r_time_start = time.time()

# patch stitching lines
mics.patch_stitchline(
    s_slide = poke_s_slide,
    s_afsubdir = poke_s_afsubdir,
    s_format_afsubdir = poke_s_format_afsubdir,
    s_segdir = poke_s_segdir,
    s_format_segdir_cellpose = poke_s_format_segdir_cellpose,
)

# rock to the end
r_time_stop = time.time()
print('done jinxif.mics.patch_stitchlines!')
print(f'run time: {(r_time_stop - r_time_start) / 3600}[h]')
print(f'run max memory: {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1000000}[GB]')
print('you are running jinxif version:', _version.__version__)
