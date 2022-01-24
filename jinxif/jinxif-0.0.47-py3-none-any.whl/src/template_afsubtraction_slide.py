#####
# title: template_afsubtraction_slide.py
#
# author: Jenny, bue
# license: GPLv>=3
# version: 2021-08-03
#
# description:
#     template script for python based image autofluorescent subtraction.
#
# instruction:
#     use jinxif.afsub.afsub_spawn function to generate and run executable from this template.
#####

# library
from jinxif import _version
from jinxif import afsub
import resource
import time

# input parameters
poke_s_slide = 'peek_s_slide'
poke_ddd_crop = peek_ddd_crop
poke_ddd_etc = peek_ddd_etc
poke_ds_early = peek_ds_early
poke_ds_late = peek_ds_late
poke_es_exclude_color = peek_es_exclude_color
poke_es_exclude_marker = peek_es_exclude_marker
poke_b_8bit = peek_b_8bit
poke_s_metadir = 'peek_s_metadir'
poke_s_regdir = 'peek_s_regdir'
poke_s_format_regdir = 'peek_s_format_regdir'
poke_s_afsubdir = 'peek_s_afsubdir'
poke_s_format_afsubdir = 'peek_s_format_afsubdir'

# off we go
print(f'run jinxif.afsub.afsubtract_images on {poke_s_slide} ...')
r_time_start = time.time()

# run af subtraction
afsub.afsubtract_images(
    s_slide = poke_s_slide,
    ddd_crop = poke_ddd_crop,
    ddd_etc = poke_ddd_etc,
    ds_early = poke_ds_early,
    ds_late = poke_ds_late,
    es_exclude_color = poke_es_exclude_color,
    es_exclude_marker = poke_es_exclude_marker,
    b_8bit = poke_b_8bit,
    s_metadir = poke_s_metadir,
    s_regdir = poke_s_regdir,
    s_format_regdir = poke_s_format_regdir,  # s_regdir, s_slide_pxscene
    s_afsubdir = poke_s_afsubdir,
    s_format_afsubdir = poke_s_format_afsubdir,  # s_afsubdir, s_slide
)

# rock to the end
r_time_stop = time.time()
print('done jinxif.afsub.afsubtract_images!')
print(f'run time: {(r_time_stop - r_time_start) / 3600}[h]')
print(f'run max memory: {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1000000}[GB]')
print('you are running jinxif version:', _version.__version__)
