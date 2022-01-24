#####
# title: template_crop_mscene.py
#
# author: Jenny, bue
# license: GPLv>=3
# version: 2021-11-16
#
# description:
#     template script for python based cropping registered images.
#     for one slide, one microscopy scene, all microscopy channel cyclic images.
#
# instruction:
#     use mplex_image.util.crop_swap function to edit and run this template.
#
# input:
#     tiffs or big tiffs (>4GB).
# output:
#     cropped output tiff files.
#####

# library
from jinxif import basic
import os
from skimage import io

# input parameter slides and scenes
s_slide = 'peek_s_slide'  # slide label which will be used in the filename
s_mscene = 'peek_s_mscene'
# input parameter crop coordinate
d_crop = peek_d_crop  # crop coordinate dictionary for one mscene maybe many pxscene where px_scene is the key
# input parameter filesystem
s_regdir = 'peek_s_regdir'  # location of raw images folder
s_croppedregdir = 'peek_s_croppedregdir'  # location of folder where registered images will be stored
s_format_regdir = 'peek_s_format_regdir'

# internal function
def _cropping(ai_img, l_crop):
    '''
    input:
        ai_cimg: image numpy array.
        l_crop: list containing crop coordinates in the specified coordinate type.
        the format looks like:
        [int, int, int , int, 'xyxy'] or
        [int, int, int , int, 'yxyx'] or
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
        ai_cimg = ai_img
    else:
        # handle crop coordinate
        if (l_crop[-1] == 'xyxy'):
            l_cut = l_crop
        elif (s_type_coor == 'yxyx'):
            l_cut = [l_crop[1],l_crop[0], l_crop[3],l_crop[2]]
        elif (l_crop[-1] == 'xywh'):
            l_cut = [l_crop[0], l_crop[1], l_crop[0] + l_crop[2], l_crop[1] + l_crop[3]]
        else:
            sys.exit('Error @ _crop : in l_crop unknown crop coordinate type detected {l_crop[-1]}.\nknown are xyxy, yxyx, and xywh.')
        # crop
        ai_cimg = ai_img[l_cut[1]:l_cut[3], l_cut[0]:l_cut[2]]
    # output
    return(ai_cimg)

## off we go ##

# parse input folder and filter
s_slidemscene = s_slide + '_' + s_mscene
s_src_dir = s_format_regdir.format(s_regdir,s_slidemscene)
df_img = basic.parse_tiff_reg(s_wd=s_src_dir)
df_img_slidemscene = df_img.loc[(df_img.slide_scene == s_slidemscene),:]
print(df_img.info())
print(df_img_slidemscene.info())

# for each remaining image files
for s_index in df_img_slidemscene.index:
    print(f'processing : {s_src_dir+s_index}')

    # load image
    ai_img = io.imread(s_src_dir+s_index)

    # get s_slidepxscene
    #s_pxscene = df_img.loc[s_index,'scene']
    for s_pxscene, l_crop in d_crop.items():
        # do the crop
        ai_cimg = _cropping(
            ai_img = ai_img,
            l_crop = l_crop
        )
        # save image
        s_ofile = s_index.replace(s_mscene, s_pxscene)
        s_slidepxscene = s_slide + '_' + s_pxscene
        s_dst_dir = s_format_regdir.format(s_croppedregdir, s_slidepxscene)
        os.makedirs(s_dst_dir, exist_ok=True)
        io.imsave(s_dst_dir+s_ofile, ai_cimg, check_contrast=False)
        print(f'save: {s_dst_dir+s_ofile}')

# that's all, folk!
print('finish!')
