#####
# title: regist.py
#
# language: python3
# author: Jenny, bue
# license: GPLv>=3
# date: 2021-04-00
#
# description:
#     jinxif python3 library to run the matlab and python registration scripts
#####


# library
from jinxif import basic
from jinxif import config
from jinxif import jfplt
import json
import numpy as np
import os
import re
from skimage import io
import subprocess
import sys
import time

# development
#import importlib
#importlib.reload()

# global var
s_path_module = os.path.abspath(os.path.dirname(__file__))
s_path_module = re.sub(r'jinxif$','jinxif/', s_path_module)


# function
def save_cropcoor(
        s_batch,
        ddd_crop,
        s_rawdir = config.d_nconv['s_rawdir'],  #'RawImages/',
    ):
    '''
    version: 2021-12-00

    input:
        s_batch: string to specify the batch.
        ddd_crop: batch wide standardized crop coordinate dictionary.
        s_rawdir: raw tiff image directory.

    output:
        crop_coordinates.json file in s_rawdir.

    description:
        save batch related crop coordinate dictionary as json file.
    '''
    # write crop coordinates to file
    s_pathfile = f'{s_rawdir}{config.d_nconv["s_format_json_crop"].format(s_batch)}'
    print(f'ddd_crop content:', ddd_crop)
    print(f'write to file: {s_pathfile}')
    json.dump(ddd_crop, open(s_pathfile, 'w'), sort_keys=True, indent=4)


def save_exposuretimecorrect(
        s_batch,
        ddd_etc,
        s_metadir = config.d_nconv['s_metadir'],  #'MetaImages/',
    ):
    '''
    version: 2021-12-00

    input:
        s_batch: string to specify the batch.
        ddd_etc: batch wide exposure time correction dictionary.
            the dictionary format  looks like this:
            ddd_etc = {'slide_scene': {'marker': {'is': 7,'should_be': 4}},}
        s_metadir: image metadata directory.

    output:
        exposuretime_correct.json file in s_metadir.

    description:
        save batch related exposure time correct dictionary as json file.
    '''
    # write exposure time correction to file
    s_pathfile = f'{s_metadir}{config.d_nconv["s_format_json_etcorrect"].format(s_batch)}'
    print(f'ddd_etc, content:', ddd_etc)
    print(f'write to file: {s_pathfile}')
    json.dump(ddd_etc, open(s_pathfile, 'w'), sort_keys=True, indent=4)


################
# registration #
#################

# spawner
def regist_spawn(
        ddd_crop,
        es_slide = None,
        s_type_registration = 'matlab',
        # file extension
        s_regex_ext = r'_(ORG.tif)$',  # regex file extension.
        # staining round
        s_regex_round_ref = r'^(R\d+Q?_).+$',  # regex round of raw reference round tiffs.
        s_regex_round_nonref = r'^(R\d+Q?_).+$',  # regex round of raw non-reference round tiffs.
        # staining marker
        s_regex_marker_ref = r'^.+_(.+\..+\..+\.[^_]+_).+$',  # regex of reference round markers in raw tiffs.
        s_regex_marker_nonref = r'^.+_(.+\..+\..+\.[^_]+_).+$',  # regex of non-reference round markers in raw tiffs.
        # microscopy channel
        s_regex_micchannel_ref = r'^.*(_c\d+_).*$',  # regex of reference round microscopy channels/colors.
        s_regex_micchannel_nonref = r'^.*(_c\d+_).*$',  # regex of non-reference round microscopy channels/colors.
        # dapi images only
        s_glob_img_dapiref = 'R1_*_{}_*-{}_c1_ORG.tif', # regex of raw dapi exclusive reference round tiff.
        s_glob_img_dapinonref = 'R*_*_{}_*-{}_c1_ORG.tif', # regex of raw dapi non-reference round tiffs.
        # non-dapi images (possibly dapi images too)
        s_glob_img_ref = 'R1_*_{}_*-{}_c*_ORG.tif', # glob patter of raw exclusive reference round tiffs.
        s_glob_img_nonref = 'R*_*_{}_*-{}_c*_ORG.tif', # glob pattern of raw non-reference round tiffs.
        # registration
        i_npoint = str(10000),  # number of key points used for registration,
        # processing
        s_type_processing = 'slurm',
        s_slurm_partition = 'exacloud',
        s_slurm_mem = '32G',
        s_slurm_time = '36:00:0',
        s_slurm_account = 'gray_lab',
        # filesystem
        s_rawdir = config.d_nconv['s_rawdir'],  #'RawImages/',
        s_format_rawdir = config.d_nconv['s_format_rawdir'],  #'{}{}/',  # s_rawdir, s_slide
        s_qcregistration_dir = 'QC/RegistrationPlots/',
        s_regdir = config.d_nconv['s_regdir'],  #'RegisteredImages/',
    ):
    '''
    version: 2021-12-00

    input:
        ddd_crop: slide | scene_microscopy | scene_20000px dictionary with or without crop coordinates.
            a 20000px scene is scene that has <= 20000px wide and height.
            crop coordinates can be specified by None, [0,0,0,0,'yxyx'], [0,0,0,0,'xyxy'], or [0,0,0,0,'xyhw'].
            yxyx rectangle is specified by upper left and lower right corner.
            xyxy rectangle is specified by upper left and lower right corner.
            xyhw rectangle is specified by upper left corner and height and wide.

        es_slide: set of slide ids to process only sudden slides specified in ddd_crop.
            default is None which will process all slides found in ddd_crop.

        s_type_registration: to specify which registration algorithm should be run.
            implemented is a matlab and a python keypoint registration
            which run a slightly different math in the back.
            at the moment, default registration is matlab based.
            
        s_regex_ext: regex string to specify the file extension.
        s_regex_round_ref: regex string to specify round of raw reference round tiffs.
        s_regex_round_nonref: regex string to specify round of raw non-reference round tiffs.
        s_regex_marker_ref: regex string to specify reference round markers in raw tiffs.
        s_regex_marker_nonref: regex string to specify non-reference round markers in raw tiffs.
        s_regex_micchannel_ref: regex string to specify reference round microscopy channels/colors.
        s_regex_micchannel_nonref = regex string to specify non-reference round microscopy channels/colors.
        s_glob_img_dapiref: regex string to specify exclusive the raw dapi reference round tiff.
        s_glob_img_dapinonref: regex string to specify raw dapi non-reference round tiffs.
        s_glob_img_ref: glob string to specify exclusive raw reference round tiffs.
        s_glob_img_nonref: glob string to specify non-reference round tiffs.
        i_npoint: number of key points used for registration

        # processing
        s_type_processing: to specify if registration should be run on the slurm cluster
            or on a simple slurp machine.
        s_slurm_partition: slurm cluster partition to use. options are 'exacloud', 'light'.
        s_slurm_mem: slurm cluster memory allocation. format '64G'.
        s_slurm_time: slurm cluster time allocation in hour or day format. max '36:00:00' [hour] or '30-0' [day].
        s_slurm_account: slurm cluster account to credit time from. 'gray_lab', 'chin_lab', 'heiserlab', 'CEDAR'.

        # file system
        s_rawdir: input directory which contains a folder for each requested slide
            with tiffs for each microscopy scene in it.
        s_format_rawdir: s_rawdir subfolder structure.
        s_qcregistration_dir: path to qc plot directory. 
            only used for python registration code.
            if None, no qc plots will be generated.
        s_regdir: output directory where for each 20000px scene
            a folder will registered tiffs will be generated.

    output:
        for each slide 20000px scene a folder with registered tiffs, one tiff for each round channel.

    description:
        main routine for registration and cropping.
        registration and cropping is done in one function because matlab can only read but not write big tiffs (>4[GB]).
    '''
    # handle input
    if es_slide is None:
        ls_slide = sorted(ddd_crop.keys())
    else:
        ls_slide = sorted(es_slide)

    # for each px scene
    for s_slide in ls_slide:
        for s_mscene, d_crop in sorted(ddd_crop[s_slide].items()):
            # load from one slide one mscene (even slide might have more than one). outputs all pxscenes
            print(f'spawn jinxif.regist.registration for: {s_slide} {s_mscene} {sorted(ddd_crop[s_slide][s_mscene])} by {s_type_registration}')

            ## matlab registration ##
            if s_type_registration == 'matlab':
                # set run commands
                s_pathfile_registration_template = 'template_registration_mscene.m'
                s_pathfile_registration = f'registration_and_crop_slide_{s_slide}_mscene_{s_mscene}.m'.replace('-','')  # bue: necessary!
                s_srun_cmd = f'matlab -nodesktop -nosplash -r "{s_pathfile_registration.replace(".m","")}; exit;"'
                ls_run_cmd = ['matlab', '-nodesktop', '-nosplash', '-r "{s_pathfile_registration.replace(".m","")}; exit;"']

                # handle crop dictionary
                sls_pxscene = '{'
                sll_pxcrop = '{'
                for s_pxscene, l_crop in  ddd_crop[s_slide][s_mscene].items():
                    if l_crop is None:
                        s_crop = "'none'"
                    elif l_crop[-1] == 'yxyx':
                        s_crop = f'{l_crop[1]} {l_crop[0]} {l_crop[3] - l_crop[1]} {l_crop[2] - l_crop[0]}'
                    elif l_crop[-1] == 'xyxy':
                        s_crop = f'{l_crop[0]} {l_crop[1]} {l_crop[2] - l_crop[0]} {l_crop[3] - l_crop[1]}'
                    elif l_crop[-1] == 'xywh':
                        s_crop = f'{l_crop[0]} {l_crop[1]} {l_crop[2]} {l_crop[3]}'
                    else:
                        sys.exit(f"Error @ regsit.regist_spawn : unknown crop coordinate type in {l_crop}.\nknown are None, [0,0,0,0,'yxyx'], [0,0,0,0,'xyxy'], and [0,0,0,0,'xywh'].")
                    if sls_pxscene == '{':
                        sls_pxscene += "'_" + s_pxscene + "'"
                        sll_pxcrop += "[" + s_crop + "]"
                    else:
                        sls_pxscene += " '_" + s_pxscene + "'"
                        sll_pxcrop += " [" + s_crop + "]"
                sls_pxscene += '}'
                sll_pxcrop += '}'

            ## python ##
            else:
                # set run commands
                s_pathfile_registration_template = 'template_registration_mscene.py'
                s_pathfile_registration = f'registration_and_crop_slide_{s_slide}_mscene_{s_mscene}.py'
                s_srun_cmd = f'python3 {s_pathfile_registration}'
                ls_run_cmd = ['python3', s_pathfile_registration]
                sls_pxscene = 'nop'
                sll_pxcrop = 'nop'

            ## any ##
            # load template registration script code
            with open(f'{s_path_module}src/{s_pathfile_registration_template}') as f:
                s_stream = f.read()

            # edit code generic
            s_stream = s_stream.replace('peek_s_slide', s_slide)
            s_stream = s_stream.replace('peek_s_mscene', s_mscene)
            s_stream = s_stream.replace('peek_s_regex_ext', s_regex_ext)  # bue: might become function input because of file naming convention
            s_stream = s_stream.replace('peek_s_regex_round_ref', s_regex_round_ref)  # bue: might become function input because of file naming convention
            s_stream = s_stream.replace('peek_s_regex_round_nonref', s_regex_round_nonref)  # bue: might become function input because of file naming convention
            s_stream = s_stream.replace('peek_s_regex_marker_ref', s_regex_marker_ref)  # bue: might become function input because of file naming convention
            s_stream = s_stream.replace('peek_s_regex_marker_nonref', s_regex_marker_nonref)  # bue: might become function input because of file naming convention
            s_stream = s_stream.replace('peek_s_regex_micchannel_ref', s_regex_micchannel_ref)  # bue: might become function input because of file naming convention
            s_stream = s_stream.replace('peek_s_regex_micchannel_nonref', s_regex_micchannel_nonref)  # bue: might become function input because of file naming convention
            s_stream = s_stream.replace('peek_s_glob_img_dapiref', s_glob_img_dapiref.format(s_slide, s_mscene))  # bue: might become function input because of file naming convention
            s_stream = s_stream.replace('peek_s_glob_img_dapinonref', s_glob_img_dapinonref.format(s_slide, s_mscene))  # bue: might become function input because of file naming convention
            s_stream = s_stream.replace('peek_s_glob_img_ref', s_glob_img_ref.format(s_slide, s_mscene))  # bue: might become function input because of file naming convention
            s_stream = s_stream.replace('peek_s_glob_img_nonref', s_glob_img_nonref.format(s_slide, s_mscene))  # bue: might become function input because of file naming convention
            s_stream = s_stream.replace('peek_s_src_dir', s_format_rawdir.format(s_rawdir, s_slide))  # bue: might become function input because of folder convention
            s_stream = s_stream.replace('peek_s_dst_dir', s_regdir)  # bue: might become function input because of folder convention
            s_stream = s_stream.replace('peek_i_npoint', str(10000))  # bue: number of key points used for registration, might become function input
            # edit code matlab only
            s_stream = s_stream.replace('peek_sls_pxscene', sls_pxscene)  # all pxsenes belonging to one mscene in the same order as crop coordinates
            s_stream = s_stream.replace('peek_sll_pxcrop', sll_pxcrop)  # crop coordinates for one mscene maybe many pxscene
            # edit code python only
            s_stream = s_stream.replace('peek_d_crop', str(ddd_crop[s_slide][s_mscene]))  # crop coordinates for one mscene maybe many pxscene
            s_stream = s_stream.replace('peek_s_qcregistration_dir', s_qcregistration_dir)  # bue: might become function input because of folder convention

            # write executable registration script code to file
            time.sleep(4)
            with open(s_pathfile_registration, 'w') as f:
                f.write(s_stream)

            # execute registration script
            time.sleep(4)
            if (s_type_processing == 'slurm'):
                # generate sbatch file
                s_pathfile_sbatch = f'registration_{s_type_registration}_{s_slide}_{s_mscene}.sbatch'
                config.slurmbatch(
                    s_pathfile_sbatch=s_pathfile_sbatch,
                    s_srun_cmd=s_srun_cmd,
                    s_jobname=f'r{s_slide}_{s_mscene}',
                    s_partition=s_slurm_partition,
                    s_gpu=None,
                    s_mem=s_slurm_mem,
                    s_time=s_slurm_time,
                    s_account=s_slurm_account,
                )
                # Jenny, this is cool!
                subprocess.run(
                    ['sbatch', s_pathfile_sbatch],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                )
            else:  # non-slurm
                # Jenny, this is cool!
                s_file_stdouterr = f'slurp-registration_{s_type_registration}_{s_slide}_{s_mscene}.out'
                subprocess.run(
                    ls_run_cmd,
                    stdout=open(s_file_stdouterr, 'w'),
                    stderr=subprocess.STDOUT,
                )


############################
# exposure time correction #
###########################

def exposure_time_correct(
        s_slidepxscene,
        dd_marker_etc,
        s_imagetype_original = 'ORG',
        # filesystem
        s_regdir = config.d_nconv['s_regdir'],  #'RegisteredImages/',
        s_format_regdir = config.d_nconv['s_format_regdir'],  #'{}{}/',  s_regdir, s_slide_pxscene
    ):
    '''
    version: 2021-12-00

    input:
        s_slidepxscen: slide pxscene hat should be corrected for expression time.
        dd_marker_etc: dictionary of dictionary that specifies for each marker
            the is and should_be exposure time value.
            the dictionary format  looks like this:
            dd_marker_etc = {'marker': {'is': 7,'should_be': 4}}
        s_imagetype_original: string to specify the original image type that should be transformed
            to the ETC exposure time corrected image type.

        s_regdir: registration directory.
        s_format_regdir: registration directory subdirectory where the registered tiffs are.

    output:
        exposure time corrected registered tiff images that will replace the original register tiff images.

    description:
        function to correct for image intensity mistakes, cased by human error by wrongly entered exposure time on the microscope.
    '''
    # handle input
    s_regpath = s_format_regdir.format(s_regdir, s_slidepxscene)    
    # parse image files
    df_img_reg = basic.parse_tiff_reg(s_wd=s_regpath)
    # for each marker that have to be corrected
    for s_marker, d_exposuretime_correct in dd_marker_etc.items():
        for s_ifile in df_img_reg.loc[(df_img_reg.marker == s_marker) & (df_img_reg.imagetype == s_imagetype_original),:].index:
            print(f'exposure_time_coorect: {s_ifile} ...')
            s_ofile = s_ifile.replace('_{}.'.format(s_imagetype_original), r'_ETC.')  # change output file image type to exposure time corrected
            # load registered image
            ai_image = io.imread(s_regpath + s_ifile)
            # adjust intensity
            i_shouldbe = d_exposuretime_correct['should_be']
            i_is = d_exposuretime_correct['is']
            # clip values to 8[bit] or 16[bit] image.
            if (ai_image.dtype.type is np.uint8):
                np.clip(ai_image, a_min=0, a_max=int((2**8 - 1) * (i_is / i_shouldbe)), out=ai_image)
            elif (ai_image.dtype.type is np.uint16):
                np.clip(ai_image, a_min=0, a_max=int((2**16 - 1) * (i_is / i_shouldbe)), out=ai_image)
            else:
                sys.exit(f'Error @ jinxif.regist.exposure_time_correct : unknown tiff image bit type {ai_image.dtype.type}.\nknown are 8[bit] and 16[bit] tiff images.')
            # do correction
            ai_image = (ai_image * i_shouldbe / i_is).astype(ai_image.dtype)
            # save registered intensity corrected image
            print(f'save: {s_ofile}')
            io.imsave(s_regpath + s_ofile, ai_image, check_contrast=False)
            # delete original registered image file
            print(f'delete: {s_ifile}')
            os.remove(s_regpath + s_ifile)


# spawner function
def exposure_time_correct_spawn(
        es_slide,
        ddd_etc,
        s_imagetype_original = 'ORG',
        # processing
        s_type_processing = 'slurm',
        s_slurm_partition = 'exacloud',
        s_slurm_mem = '32G',
        s_slurm_time = '36:00:0',
        s_slurm_account = 'gray_lab',
        # file system
        s_regdir = config.d_nconv['s_regdir'],  #'RegisteredImages/',
        s_format_regdir = config.d_nconv['s_format_regdir'],  #'{}{}/',  s_regdir, s_slide_pxscene
    ):
    '''
    version: 2021-12-00

    input:
        es_slide: set of slide ids which should be processed.
        ddd_etc: slidepxscene marker exposure time correction dictionary.
            the dictionary format  looks like this:
            ddd_etc = {'slide_scene': {'marker': {'is': 7,'should_be': 4}},}
        s_imagetype_original: string to specify the original image type that should be transformed
            to the ETC exposure time corrected image type.

        s_type_processing: string to specify if pipeline is run on a slurm cluster or not.
            known vocabulary is slurm and any other string for non-slurm processing.
        s_slurm_partition: slurm cluster partition to use.
            OHSU ACC options are 'exacloud', 'light', (and 'gpu').
            the default is tweaked to OHSU ACC settings.
        s_slurm_mem: slurm cluster memory allocation. format '64G'.
        s_slurm_time: slurm cluster time allocation in hour or day format.
            OHSU ACC max is '36:00:00' [hour] or '30-0' [day].
            the related qos code is tweaked to OHSU ACC settings.
        s_slurm_account: slurm cluster account to credit time from.
            my OHSU ACC options are 'gray_lab', 'chin_lab', 'heiserlab', 'CEDAR'.

        s_regdir: registered tiff images directory path.
        s_format_regdir: regdir subdirectory structure, which is a subdirectory per slide.

    output:
        exposure time corrected registered image files.

    description:
        exposure time correct registered image files as specified in ddd_etc.
    '''
    # for each slide_pxscene
    for s_slidepxscene, dd_marker_etc in  sorted(ddd_etc.items()):
        if any([s_slidepxscene.startswith(s_slide) for s_slide in es_slide]):
            # this has to be a python template!
            print(f'spawn jinxif.regist.exposure_time_correct for: {s_slidepxscene} ...')

            # set run commands
            s_pathfile_template = 'template_exposuretimecorrect_slidepxscene.py'
            s_pathfile = f'exposuretimecorrect_slidepxscene_{s_slidepxscene}.py'
            s_srun_cmd = f'python3 {s_pathfile}'
            ls_run_cmd = ['python3', s_pathfile]

            ## any ##
            # load template script code
            with open(f'{s_path_module}src/{s_pathfile_template}') as f:
                s_stream = f.read()

            # edit code generic
            s_stream = s_stream.replace('peek_s_slidepxscene', s_slidepxscene)
            s_stream = s_stream.replace('peek_dd_marker_etc', str(dd_marker_etc))
            s_stream = s_stream.replace('peek_s_imagetype_original', s_imagetype_original)
            s_stream = s_stream.replace('peek_s_regdir', s_regdir)
            s_stream = s_stream.replace('peek_s_format_regdir', s_format_regdir)

            # write executable script code to file
            time.sleep(4)
            with open(s_pathfile, 'w') as f:
                f.write(s_stream)

            # execute script code
            time.sleep(4)
            if (s_type_processing == 'slurm'):
                # generate sbatch file
                s_pathfile_sbatch = f'exposuretimecorrect_slidepxscene_{s_slidepxscene}.sbatch'
                config.slurmbatch(
                    s_pathfile_sbatch = s_pathfile_sbatch,
                    s_srun_cmd = s_srun_cmd,
                    s_jobname = f'c{s_slidepxscene}',
                    s_partition = s_slurm_partition,
                    s_gpu = None,
                    s_mem = s_slurm_mem,
                    s_time = s_slurm_time,
                    s_account = s_slurm_account,
                )
                # Jenny, this is cool!
                subprocess.run(
                    ['sbatch', s_pathfile_sbatch],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                )
            else:  # non-slurm
                # Jenny, this is cool!
                s_file_stdouterr = f'slurp-exposuretimecorrect_slidepxscene_{s_slidepxscene}.out'
                o_process = subprocess.run(
                    ls_run_cmd,
                    stdout=open(s_file_stdouterr, 'w'),
                    stderr=subprocess.STDOUT,
                )


############
# qc plot #
###########

def visualize_reg_images(
        s_slide,
        s_color = config.d_nconv['s_color_dapi_jinxif'],  #'c1'
        # filesystem
        s_regdir = config.d_nconv['s_regdir'],  #'RegisteredImages/',
        s_format_regdir = config.d_nconv['s_format_regdir'],  #'{}{}/', # s_regdir, s_slide_pxscene
        s_qcdir = config.d_nconv['s_qcdir'],  #'QC/',
    ):
    '''
    version: 2021-12-00

    input:
        s_slide: slide id from which per mscene qc images should be generated.
        s_color: microscopy channel to check. default is c1 which is DAPI.
 
        s_regdir: registered tiff images directory path.
        s_format_regdir: s_regdir subdirectory  structure, which is a subdirectory per slide.
        s_qcdir: qc directory path.

    output:
        png plot under s_qcdir + s_regdir.split("/")[-2]

    description:
        generate array reg images to check tissue identity, focus, and so on.
    '''
    print(f'run jinxif.regist.visualize_reg_images for slide: {s_slide} ...')
    for s_dir in sorted(os.listdir(s_regdir)):
        s_path = s_format_regdir.format(s_regdir, s_dir)
        if s_dir.startswith(s_slide) and os.path.isdir(s_path):
            print(f'visualize_reg_images for: {s_dir} ...')
            df_img_slide = basic.parse_tiff_reg(s_wd=s_path)  # actually this is already slide_pxscene
            #print(df_img_slide.info())
            for s_slide_pxscene in sorted(df_img_slide.slide_scene.unique()):
                print(f'slide_scene: {s_slide_pxscene}')

                # generate output path and filename
                s_path = f'{s_qcdir}{s_regdir.split("/")[-2]}/'
                s_pathfile = f'{s_path}{s_slide_pxscene}_{s_color}_reg.png'

                # filter data
                df_img_slidepxscene = df_img_slide.loc[
                    (df_img_slide.color == s_color) & (df_img_slide.slide_scene == s_slide_pxscene),
                    :
                ].sort_values('round_order')
                df_img_slidepxscene.index.name = df_img_slide.index.name

                # generate figure
                jfplt.array_img_scatter(
                    df_img = df_img_slidepxscene,
                    s_xlabel = 'marker',
                    ls_ylabel = ['round','color'],
                    s_title = 'slide_scene',
                    ti_array = (2, len(df_img_slidepxscene)//2 + 1),  # // is floor division
                    ti_fig = (22,8),
                    cmap = 'gray',
                    s_pathfile = s_pathfile,
                )


# spawner function
def visualize_reg_images_spawn(
        es_slide,
        s_color = config.d_nconv['s_color_dapi_jinxif'],  #'c1'
        # processing
        s_type_processing = 'slurm',
        s_slurm_partition = 'exacloud',
        s_slurm_mem = '32G',
        s_slurm_time = '36:00:0',
        s_slurm_account = 'gray_lab',
        # filesystem
        s_regdir = config.d_nconv['s_regdir'],  #'RegisteredImages/',
        s_format_regdir = config.d_nconv['s_format_regdir'],  #'{}{}/', # s_regdir, s_slide_pxscene
        s_qcdir = config.d_nconv['s_qcdir'],  #'QC/',
    ):
    '''
    version: 2021-12-00

    input:
        es_slide: set of slide id from which per mscene qc images should be generated.
        s_color: microscopy channel to check. default is c1 which is DAPI.

        s_type_processing: string to specify if pipeline is run on a slurm cluster or not.
            known vocabulary is slurm and any other string for non-slurm processing.
        s_slurm_partition: slurm cluster partition to use.
            OHSU ACC options are 'exacloud', 'light', (and 'gpu').
            the default is tweaked to OHSU ACC settings.
        s_slurm_mem: slurm cluster memory allocation. format '64G'.
        s_slurm_time: slurm cluster time allocation in hour or day format.
            OHSU ACC max is '36:00:00' [hour] or '30-0' [day].
            the related qos code is tweaked to OHSU ACC settings.
        s_slurm_account: slurm cluster account to credit time from.
            my OHSU ACC options are 'gray_lab', 'chin_lab', 'heiserlab', 'CEDAR'.

        s_regdir: registered tiff images directory path.
        s_format_regdir: regdir subdirectory  structure, which is a subdirectory per slide.
        s_qcdir: qc directory path.

    output:
        png plot under s_qcdir + s_regdir.split("/")[-2]

    description:
        generated array reg images to check tissue identity, focus, and so on.
    '''
    # for each slide
    for s_slide in sorted(es_slide):

        # this has to be a python template!
        print(f'spawn jinxif.regist.visualize_reg_images for: {s_slide} {s_color} ...')

        # set run commands
        s_pathfile_template = 'template_vizregimage_slide.py'
        s_pathfile = f'vizregimage_slide_{s_slide}_{s_color}.py'
        s_srun_cmd = f'python3 {s_pathfile}'
        ls_run_cmd = ['python3', s_pathfile]

        ## any ##
        # load template script code
        with open(f'{s_path_module}src/{s_pathfile_template}') as f:
            s_stream = f.read()

        # edit code generic
        s_stream = s_stream.replace('peek_s_slide', s_slide)
        s_stream = s_stream.replace('peek_s_color', s_color)
        s_stream = s_stream.replace('peek_s_regdir', s_regdir)
        s_stream = s_stream.replace('peek_s_format_regdir', s_format_regdir)
        s_stream = s_stream.replace('peek_s_qcdir', s_qcdir)

        # write executable script code to file
        time.sleep(4)
        with open(s_pathfile, 'w') as f:
            f.write(s_stream)

        # execute script code
        time.sleep(4)
        if (s_type_processing == 'slurm'):
            # generate sbatch file
            s_pathfile_sbatch = f'vizregimage_slide_{s_slide}_{s_color}.sbatch'
            config.slurmbatch(
                s_pathfile_sbatch = s_pathfile_sbatch,
                s_srun_cmd = s_srun_cmd,
                s_jobname = f'q{s_slide}',
                s_partition = s_slurm_partition,
                s_gpu = None,
                s_mem = s_slurm_mem,
                s_time = s_slurm_time,
                s_account = s_slurm_account,
            )
            # Jenny, this is cool!
            subprocess.run(
                ['sbatch', s_pathfile_sbatch],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
        else:  # non-slurm
            # Jenny, this is cool!
            s_file_stdouterr = f'slurp-vizregimage_slide_{s_slide}_{s_color}.out'
            o_process = subprocess.run(
                ls_run_cmd,
                stdout=open(s_file_stdouterr, 'w'),
                stderr=subprocess.STDOUT,
            )

