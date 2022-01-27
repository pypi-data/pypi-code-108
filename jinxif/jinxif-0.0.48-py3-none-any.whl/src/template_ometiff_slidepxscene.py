########
# title: template_ometiff_slidepxscene.py
#
# author: Jenny, bue
# license: GPLv>=3
# version: 2021-11-16
#
# description:
#     template script for python based multi channel ometiff generation,
#     utilizing the aicsimageio library.
#
# instruction:
#     use jinxif.ometiff.ometiff_spawn function to generate and run executable from this template.
#####

# libraries
from jinxif import _version
from jinxif import ometiff
import resource
import sys
import time

# set variables
poke_s_slidepxscene = 'peek_s_slidepxscene'
poke_es_exclude_round = peek_es_exclude_round
poke_ddd_crop = peek_ddd_crop
poke_ddd_etc = peek_ddd_etc
# microscope
poke_r_pixel_size_um = peek_r_pixel_size_um
# experiment
poke_s_batch_id = 'peek_s_batch_id'
poke_s_lab = 'peek_s_lab'
poke_s_email_leader = 'peek_s_email_leader'
# output image
poke_peek_b_8bit = peek_b_8bit
# files system
poke_s_afsubdir = 'peek_s_afsubdir'
poke_s_format_afsubdir = 'peek_s_format_afsubdir'
poke_s_metadir = 'peek_s_metadir'
poke_s_ometiffdir = 'peek_s_ometiffdir'

# off we go
print(f'run jinxif.ometiff.ometiff_generator on: {poke_s_afsubdir} {poke_s_slidepxscene} ...')
r_time_start = time.time()

# generate ome.tiff
ometiff.ometiff_generator(
    s_slidepxscene = poke_s_slidepxscene,
    es_exclude_round = poke_es_exclude_round,
    ddd_crop = poke_ddd_crop,
    ddd_etc = poke_ddd_etc,
    # microscope
    r_pixel_size_um = poke_r_pixel_size_um,
    # experiment
    s_batch_id = poke_s_batch_id,
    s_lab = poke_s_lab,
    s_email_leader = poke_s_email_leader,
    # output image
    b_8bit = poke_peek_b_8bit,
    # file system
    s_afsubdir = poke_s_afsubdir,
    s_format_afsubdir = poke_s_format_afsubdir,
    s_metadir = poke_s_metadir,
    s_ometiffdir = poke_s_ometiffdir,
)

# rock to the end
r_time_stop = time.time()
print('done jinxif.ometiff.ometiff_generator!')
print(f'run time: {(r_time_stop - r_time_start) / 3600}[h]')
print(f'run max memory: {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1000000}[GB]')
print('you are running jinxif version:', _version.__version__)

