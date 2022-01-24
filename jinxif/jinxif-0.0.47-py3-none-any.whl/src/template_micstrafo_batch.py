########
# title: template_micstrafo_batch.py
#
# author: Jenny, bue
# license: GPLv>=3
# version: 2021-08-15
#
# description:
#     template script for python base miltenyi macsima output data set transformation 
#     so that it flows into the jinxif pipeline.
#
# instruction:
#     use jinxif.mics.trafo_spawn function to generate and run executable from this template.
#####

# libraries
from jinxif import _version
from jinxif import mics
import resource
import time

# set variables
poke_s_batch = 'peek_s_batch'
poke_ds_slidescene_rename = peek_ds_slidescene_rename
poke_ds_marker_rename = peek_ds_marker_rename
poke_i_exp_line = peek_i_exp_line
poke_s_micsdir = 'peek_s_micsdir'
poke_s_afsubdir = 'peek_s_afsubdir'
poke_s_format_afsubdir = 'peek_s_format_afsubdir'

# off we go
print(f'run jinxif.mics.trafo on {poke_s_batch} ...')
r_time_start = time.time()

# transform miltenyi macsima output data
mics.trafo(
    ds_slidescene_rename = poke_ds_slidescene_rename,
    ds_marker_rename = poke_ds_marker_rename,
    i_exp_line = poke_i_exp_line,
    s_micsdir = poke_s_micsdir,
    s_afsubdir = poke_s_afsubdir,
    s_format_afsubdir = poke_s_format_afsubdir,
)

# rock to the end
r_time_stop = time.time()
print('done jinxif.mics.trafo!')
print(f'run time: {(r_time_stop - r_time_start) / 3600}[h]')
print(f'run max memory: {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1000000}[GB]')
print('you are running jinxif version:', _version.__version__)
