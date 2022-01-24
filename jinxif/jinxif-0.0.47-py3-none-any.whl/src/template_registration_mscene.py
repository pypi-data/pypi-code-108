#####
# title: template_registration.py
#
# author: Jenny, bue
# license: GPLv>=3
# version: 2021-04-23
#
# description:
#     template script for python based IF image registration,
#     for one slide, one microscopy scene, all microscopy channel cyclic images.
#
# instruction:
#     use mplex_image.regist.registration function to edit and run this template.
#
# input:
#     tiffs or big tiffs (>4GB) with filename ending in s_regex_ext.
#     there can be as many files in the s_src_dir input folder as they want,
#     though s_regex_round, s_regex_marker, s_regex_micchannel and
#     s_glob_img_dapi, s_glob_img, have to be slide_mscene specific,
#     whatever naming convention you follow.
#
#     E.g. ChinLab filename convention is:
#     Rx_Bi.o.mark.ers_Slidename-Section_xxx_xx_x_-Scene_cx_ORG.tif,
#     where c1 is DAPI and x can be variable (i.e. from axioscan)
#
# output:
#     the output tiff files in m_dst_dir folder will follow the naming convention:
#     Registered-round<>marker<>slidepxscene<>micchanel<>ext
#     make sure that you integrate a separator (symbolized by <>) into your regex patterns.
#####


# library
import glob
from jinxif import config
from jinxif import keypointregist
import numpy as np
import os
import re
from skimage import io

# input parameter slides and scenes
s_slide = 'peek_s_slide'  # slide label which will be used in the filename
s_mscene = 'peek_s_mscene'
# input parameter crop coordinate
d_crop = peek_d_crop  # crop coordinates dictionary for one mscene maybe many pxscene where px_scene is the key
# input parameter file extension
s_regex_ext = r'peek_s_regex_ext'  # file extension regex pattern
# input parameter round
s_regex_round_ref = r'peek_s_regex_round_ref'  # staining round regexp pattern
s_regex_round_nonref = r'peek_s_regex_round_nonref'  # staining round regexp pattern
# input parameter marker
s_regex_marker_ref = r'peek_s_regex_marker_ref'  # stain regex pattern
s_regex_marker_nonref = r'peek_s_regex_marker_nonref'  # stain regex pattern
# input parameter micchannel
s_regex_micchannel_ref = r'peek_s_regex_micchannel_ref'  # microscopy channel regex pattern
s_regex_micchannel_nonref = r'peek_s_regex_micchannel_nonref'  # microscopy channel regex pattern
# input parameter dapi image
s_glob_img_dapiref = r'peek_s_glob_img_dapiref'  # slide_mscene specific ref round dapi channel image glob pattern
s_glob_img_dapinonref = r'peek_s_glob_img_dapinonref'  # slide_mscene specific non-ref round dapi channel image glob pattern (ref round possible)
# input parameter dapi and non-dapi images
s_glob_img_ref = r'peek_s_glob_img_ref'  # slide_mscene specific image glob pattern for all channels in ref round
s_glob_img_nonref = r'peek_s_glob_img_nonref'  # slide_mscene specific image glob pattern for all channels in non-ref round (ref round possible)
# input parameter filesystem
s_src_dir = 'peek_s_src_dir'  # location of raw images folder
s_dst_dir = 'peek_s_dst_dir'  # location of folder where registered images will be stored
s_qcregistration_dir = 'peek_s_qcregistration_dir'  # location of folder where possible qc plots will be stored
# input parameter registration
ipy_npoint = peek_i_npoint  # number of features to detect in image (default = 10000)

# internal function
def _cropping(ai_img, l_crop):
    '''
    input:
        ai_img: image numpy array.
        l_crop: list contains crop coordinates and the coordinate type.
        the format looks like:
        [int, int, int , int, 'xyxy'] or
        [int, int, int , int, 'yxyx'] or,
        [int, int, int , int, 'xywh'].
        'xyxy' specifies the top left and bottom right corner,
        'yxyx' specifies the top left and bottom right corner, and
        'xywh' specifies the top left corner and wide and height.
        None for no cropping.

    output:
        ai_cimg: cropped image numpy array.

    description:
        function crops an image numpy array,
        as specified by l_crop,
        and gives the cropped image numpy array back.
    '''
    # processing
    if (l_crop is None):
        # crop
        ai_cimg = ai_img  # bue: maybe here copy
    else:
        # handle crop coordinate
        if (l_crop[-1] == 'xyxy'):
            l_cut = l_crop
        elif (l_crop[-1] == 'yxyx'):
            l_cut = [l_crop[1],l_crop[0], l_crop[3],l_crop[2]]
        elif (l_crop[-1] == 'xywh'):
            l_cut = [l_crop[0], l_crop[1], l_crop[0] + l_crop[2], l_crop[1] + l_crop[3]]
        else:
            sys.exit('Error @ _crop : in l_crop unknown crop coordinate type detected {l_crop[-1]}.\nknown are xyxy, yxyx, and xywh.')
        # crop
        ai_cimg = ai_img[l_cut[1]:l_cut[3], l_cut[0]:l_cut[2]]  # bue: maybe here copy?
    # output
    return(ai_cimg)


## off we go ##
# specify run
print(f'\nrun slide mscene: {s_slide} {s_mscene}')
print(f'input path: {s_src_dir}')
print(f'output path: {s_dst_dir}')

# get dapi file name for reference round
ls_pathfile_dapiref = glob.glob(f'{s_src_dir}{s_glob_img_dapiref}')
if (len(ls_pathfile_dapiref) < 1):
    print('Error: no DAPI reference round file found with glob:', s_src_dir, s_glob_img_dapiref)
elif (len(ls_pathfile_dapiref) > 1):
    print('Error: more than 1 DAPI reference round file found with glob:', s_src_dir, s_glob_img_dapiref)
else:
    s_pathfile_dapiref = ls_pathfile_dapiref[0]
    #print(f'DAPI reference round file found: {s_pathfile_dapiref}')

# get dapi file names for all rounds
ls_pathfile_dapinonref = sorted(glob.glob(f'{s_src_dir}{s_glob_img_dapinonref}'))
if (len(ls_pathfile_dapinonref) < 1):
    print('Error: no DAPI files found with glob:', s_src_dir, s_glob_img_dapinonref)
else:
    pass
    #print(f'DAPI files found: {ls_pathfile_dapinonref}')

# get all file names for reference round
ls_pathfile_ref = sorted(glob.glob(f'{s_src_dir}{s_glob_img_ref}'))
if (len(ls_pathfile_ref) < 1):
   print('Error: no reference round files found with glob:', s_src_dir, s_glob_img_ref)
else:
   pass
   #print(f'reference round files found: {ls_pathfile_ref}')

# get all file names for all rounds
ls_pathfile_nonref = sorted(glob.glob(f'{s_src_dir}{s_glob_img_nonref}'))
if (len(ls_pathfile_nonref) < 1):
   print('Error: files found with glob:', s_src_dir, s_glob_img_nonref)
else:
   pass
   #print(f'files found: {ls_pathfile_nonref}')


# extract file extension and microscopy metadata from reference round dapi image file name
print(f'process reference round dapi image: {s_pathfile_dapiref}')
s_file_dapiref = s_pathfile_dapiref.split("/")[-1]
s_ext = re.search(s_regex_ext, s_file_dapiref).groups()[0]
s_round_dapi = re.search(s_regex_round_ref, s_file_dapiref).groups()[0]
#s_marker_dapi = re.search(s_regex_marker_ref, s_file_dapiref).groups()[0]
#s_micchannel_dapi = re.search(s_regex_micchannel_ref, s_file_dapiref).groups()[0]

# load dapi reference image
ai_img_target = io.imread(s_pathfile_dapiref)  # 16 or 8[bit] un-normalized

# process dapi and non-dapi reference round ~ copy files, rename, crop if necessary
es_pathfile_ref = set(ls_pathfile_ref)
es_pathfile_ref.add(s_pathfile_dapiref)
for s_pathfile_ref in sorted(es_pathfile_ref):
    print(f'process reference round dapi and non-dapi image: {s_pathfile_ref}')
    s_file_ref = s_pathfile_ref.split("/")[-1]

    # extract microscopy metadata for reference round non-dapi image file name
    #s_round_nondapi = re.search(s_regex_round_ref, s_file_ref).groups()[0]
    s_marker_nondapi = re.search(s_regex_marker_ref, s_file_ref).groups()[0]
    s_micchannel_nondapi = re.search(s_regex_micchannel_ref, s_file_ref).groups()[0]

    # load image
    ai_img_nonmoving = io.imread(s_pathfile_ref)  # 16 or 8[bit] un-normalized

    # for each pxscene for dapi reference round file
    for s_pxscene, l_crop in d_crop.items():   # for one slide_mscene
        # crop
        ai_cimg = _cropping(ai_img=ai_img_nonmoving, l_crop=l_crop)  # un-normalized
        # save image
        s_slidepxscene = f'{s_slide}_{s_pxscene}'
        s_ofile = config.d_nconv['s_format_tiff_reg'].format(s_round_dapi.replace('_',''), s_marker_nondapi, s_slide, s_pxscene, s_micchannel_nondapi, 'ORG')
        s_opath = f'{s_dst_dir}{s_slidepxscene}/'
        os.makedirs(s_opath, exist_ok=True)
        io.imsave(f'{s_opath}{s_ofile}', ai_cimg, check_contrast=False)


# process non-reference round dapi file
for s_pathfile_dapinonref in ls_pathfile_dapinonref:
    if (s_pathfile_dapinonref != s_pathfile_dapiref):
        print(f'process non-reference round dapi image: {s_pathfile_dapinonref}')
        s_file_dapinonref = s_pathfile_dapinonref.split("/")[-1]

        # extract microscopy metadata for non-refernce round dapi image file name
        s_round_dapi = re.search(s_regex_round_nonref, s_file_dapinonref).groups()[0]
        #s_marker_dapi = re.search(s_regex_marker_nonref, s_file_dapinonref).groups()[0]
        #s_micchannel_dapi = re.search(s_regex_micchannel_nonref, s_file_dapinonref).groups()[0]

        # load image
        ai_img_moving = io.imread(s_pathfile_dapinonref)  # 16 or 8[bit] un-normalized

        # get qc plot file name
        if (s_qcregistration_dir is None):
            s_pathfile_qcplot = None
        else:
            s_ofile_qcplot = s_file_dapinonref.replace(f'.{s_ext}','') + '_rigid_align.png'
            s_pathfile_qcplot = s_qcregistration_dir + s_ofile_qcplot

        # actual registration (images will be normalized before processing)
        target_pts, moving_pts, warped_pts, transformer = keypointregist.register(
            ai_img_target = ai_img_target, # dapi reference round un-normalized
            ai_img_moving = ai_img_moving, # dapi non-reference round un-normalized
            s_pathfile_qcplot = s_pathfile_qcplot,
        )

        # bue 20200303: isaacs fine tune algorithm part I (calculate shift) goes here.

        # get dapi and non-dapi non-reference round image file names
        es_pathfile_nonref = set(ls_pathfile_nonref)
        es_pathfile_nonref.add(s_pathfile_dapinonref)
        for s_pathfile_nonref in sorted(es_pathfile_nonref):
            s_file_nonref = s_pathfile_nonref.split("/")[-1]

            # extract microscopy metadata for non-reference round image file name
            s_round_nondapi = re.search(s_regex_round_nonref, s_file_nonref).groups()[0]
            s_marker_nondapi = re.search(s_regex_marker_nonref, s_file_nonref).groups()[0]
            s_micchannel_nondapi = re.search(s_regex_micchannel_nonref, s_file_nonref).groups()[0]

            # for each image from this round
            if (s_round_dapi == s_round_nondapi):

                # load image
                print(f'process non-reference round dapi and non-dapi image: {s_pathfile_nonref}')
                ai_img_moving = io.imread(s_pathfile_nonref)  # 16 or 8[bit] un-normalized

                # apply transformation
                ai_img_warped, warped_pts, _ = keypointregist.apply_transform(
                    ai_img_target = ai_img_target,  # dapi reference round un-normalized
                    ai_img_moving = ai_img_moving,  # dapi or non-dapi non-reference round un-normalized
                    target_pts = target_pts,  # registration result from normalized input
                    moving_pts = moving_pts,  # registration result from normalized input
                    transformer = transformer,  # registration result from normalized input
                )

                # bue 20200303: isaacs fine tune algorithm part II (apply shift) goes here.

                # for each pxscene
                for s_pxscene, l_crop in d_crop.items():   # for one slide_mscene
                    # crop
                    ai_cimg = _cropping(ai_img=ai_img_warped, l_crop=l_crop)
                    # save image
                    s_slidepxscene = f'{s_slide}_{s_pxscene}'
                    s_ofile = config.d_nconv['s_format_tiff_reg'].format(s_round_dapi.replace('_',''), s_marker_nondapi, s_slide, s_pxscene, s_micchannel_nondapi, 'ORG')
                    s_opath = f'{s_dst_dir}{s_slidepxscene}/'
                    os.makedirs(s_opath, exist_ok=True)
                    io.imsave(f'{s_opath}{s_ofile}', ai_cimg, check_contrast=False)

# that's all, folk!
print('finish!')
