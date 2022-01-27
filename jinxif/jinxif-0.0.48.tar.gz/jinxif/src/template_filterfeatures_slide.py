########
# title: template_filterfeatures_slide.py
#
# author: Jenny, bue
# license: GPLv>=3
# version: 2021-07-05
#
# description:
#     template script for python base, marker dependent cell segmentation based feature filtering and patching.
#
# instruction:
#     use jinxif.feat.filter_feature_spawn function to generate and run executable from this template.
#####

# libraries
from jinxif import _version
from jinxif import feat
import resource
import time

# set variables
poke_s_slide = 'peek_s_slide'
poke_es_dapipartition_filter = peek_es_dapipartition_filter
poke_di_seg_marker = peek_di_seg_marker
poke_i_exp = peek_i_exp
poke_i_mem = peek_i_mem
poke_i_shrink = peek_i_shrink
poke_es_shrink_marker = peek_es_shrink_marker
poke_es_custom_markerpartition = peek_es_custom_markerpartition
poke_des_cytoplasm_marker = peek_des_cytoplasm_marker
poke_s_tissue_dapi = 'peek_s_tissue_dapi'
poke_i_tissue_dapi_thresh = peek_i_tissue_dapi_thresh
poke_i_tissue_area_thresh = peek_i_tissue_area_thresh
poke_ds_shape = peek_ds_shape
poke_ds_centroid = peek_ds_centroid
poke_s_afsubdir = 'peek_s_afsubdir'
poke_s_format_afsubdir = 'peek_s_format_afsubdir'
poke_s_segdir = 'peek_s_segdir'
poke_s_format_segdir_cellpose = 'peek_s_format_segdir_cellpose'
poke_s_qcdir = 'peek_s_qcdir'


# off we go
print(f'run jinxif.feat.filter_features on {poke_s_afsubdir} {poke_s_slide} ...')
r_time_start = time.time()

# filter features
feat.filter_features(
    s_slide = poke_s_slide,
    es_dapipartition_filter = poke_es_dapipartition_filter, # {'DAPI1_nuclei','DAPI2_nuclei','DAPI16_nuclei'},
    di_seg_marker = poke_di_seg_marker, # {'Ecad': 1000}
    i_exp = poke_i_exp, # 5
    i_mem = poke_i_mem, # 2
    i_shrink = poke_i_shrink, #0
    es_shrink_marker = poke_es_shrink_marker, # optional against bleed through list of shrunken marker that should replace nucleus, exp{i_exp}, perinuc{i_exp}, or cytoplasm.
    es_custom_markerpartition = poke_es_custom_markerpartition,  # optional
    des_cytoplasm_marker = poke_des_cytoplasm_marker, # {'Ecad'} cancer marker
    s_tissue_dapi = poke_s_tissue_dapi, # 'DAPI1'
    i_tissue_dapi_thresh = poke_i_tissue_dapi_thresh, # 300 - 600
    i_tissue_area_thresh = poke_i_tissue_area_thresh, # 50000
    ds_shape = poke_ds_shape,
    ds_centroid = poke_ds_centroid,
    s_afsubdir = poke_s_afsubdir,
    s_format_afsubdir = poke_s_format_afsubdir,
    s_segdir = poke_s_segdir,
    s_format_segdir_cellpose = poke_s_format_segdir_cellpose,  # s_segdir, s_slide
    s_qcdir = poke_s_qcdir,
)

# rock to the end
r_time_stop = time.time()
print('done jinxif.feat.filter_features!')
print(f'run time: {(r_time_stop - r_time_start) / 3600}[h]')
print(f'run max memory: {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1000000}[GB]')
print('you are running jinxif version:', _version.__version__)
