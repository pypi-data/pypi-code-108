#####
# title: afsub.py
#
# language: python3
# author: Jenny, bue
# license: GPLv>=3
# date: 2021-04-00
#
# description:
#     jinxif python3 library to run auto fluorescence subtraction
#####

# library
from jinxif import config
from jinxif import basic
import numpy as np
import os
import re
import shutil
import skimage
from skimage import io
import subprocess
import time

# development
#import importlib
#importlib.reload()

# global var
s_path_module = os.path.abspath(os.path.dirname(__file__))
s_path_module = re.sub(r'jinxif$','jinxif/', s_path_module)

# functions
def afsubtract_images(
        s_slide,
        ddd_crop,
        ddd_etc,
        ds_early = {'c2':'R0c2','c3':'R0c3','c4':'R0c4','c5':'R0c5'},
        ds_late = {'c2':'R6Qc2','c3':'R6Qc3','c4':'R6Qc4','c5':'R6Qc5'},
        es_exclude_color = {'c1','c5'},
        es_exclude_marker = {},
        b_8bit = False,
        # file system
        s_metadir = config.d_nconv['s_metadir'],  #'MetaImages/',
        s_regdir = config.d_nconv['s_regdir'],  #'RegisteredImages/',
        s_format_regdir = config.d_nconv['s_format_regdir'],  #'{}{}/',  # s_regdir, s_slide_pxscene
        s_afsubdir = config.d_nconv['s_afsubdir'],  #'SubtractedRegisteredImages/',
        s_format_afsubdir = config.d_nconv['s_format_afsubdir'],  #'{}{}/',  # s_afsubdir, s_slide_pxscene
    ):
    '''
    version: 2021-12-00

    input:
        s_slide: slide id to specify for which slide auto fluorescence subtraction should be done.
        ddd_crop: the cropping dictionary that links the cropped scenes (sldie_pxscene)
            to the microscopy scenes (slide_mscene).
        ddd_etc: exposure time correction dictionary. 
            the format is {'slide_pxscene': {'marker': {'is': 7,'should_be': 4}},} 
            if no exposure time has to be corrected, set parameter to empty dictionary {}.
        ds_early: dictionary mapping each channel color (except DAPI channel) 
            to the early round quenching "marker".
            if no such round exists set parameter to empty dictionary {}.
        ds_late: dictionary mapping each channel color (except DAPI channel) 
            to the late round quenching "marker".
        es_exclude_color: microscopy channel to exclude, usually DAPI and channel >= c5,
            which because of their higher wavelength show no auto fluorescence.
        es_exclude_marker: list of markers that do not need subtraction.
            note that all markers in the es_exclude_color channels and the markers
            in ds_early and ds_late will be excluded automatically.
        b_8bit: boolean to specify the auto fluorescent subtracted image should be
             an 8[bit] or 16[bit] image. default is set to False, output will be 
             a 16[bit] tiff image, which is needed for downstream processing with this piperine.

        # file system
        s_metadir: folder where the extracted image metadata is stored.
        s_regdir: registered image directory.
        s_format_regdir: registered image subfolder format string.
        s_afsubdir: auto fluorescent subtracted registered image directory, 
            which, if not existing, will be generated.
        s_format_afsubdir: s_afsubdir subfolder format string.

    output:
        af subtracted tiff images under s_afsubdir.

    description:
        this code loads single channel 16 bit gray scale tiffs,
        performs, if d_eraly not given {}, simple AF subtraction, else scaled 
        AF subtraction based on the round position between early and late AF of channels/rounds.
    '''
    print(f'run: jinxif.afsub.afsubtract_images ...')

    for s_subfolder in sorted(os.listdir(s_regdir)):
        s_regdir_slidepxscene = s_format_regdir.format(s_regdir, s_subfolder)  # input files
        print(f'checking: {s_regdir_slidepxscene} ...')
        if s_subfolder.startswith(s_slide) and os.path.isdir(s_regdir_slidepxscene):
            s_afsubdir_slidepxscene = s_format_afsubdir.format(s_afsubdir, s_subfolder)  # output files

            ### do afsub ###
            # load filename data frame
            df_load = basic.parse_tiff_reg(s_wd=s_regdir_slidepxscene)
            df_img = basic.add_exposure(
                df_img_regist = df_load,
                ddd_crop = ddd_crop,
                ddd_etc = ddd_etc,
                s_metadir = s_metadir,
            )
        
            # generate dataframe of markers excluded from af subtraction
            es_nonafsub_marker = set(df_img.loc[df_img.color.isin(es_exclude_color),:].marker).union(set(ds_late.values())).union(set(ds_early.values())).union(es_exclude_marker)
            df_nonafsub = df_img.loc[df_img.marker.isin(es_nonafsub_marker), :]
        
            # generate dataframe of markers which have to be af subtracted
            es_afsub_marker = set(df_img.marker).difference(es_nonafsub_marker)
            df_afsub = df_img.loc[df_img.marker.isin(es_afsub_marker), :].copy()
            print(f'The background images {df_afsub.index.tolist}')
            print(f'The background markers {df_afsub.marker.tolist}')
        
            # copy markers excluded from subtraction tiffs
            for s_file in sorted(df_nonafsub.index.unique()):
                s_slide_pxscene = df_nonafsub.loc[s_file, 'slide_scene']
                print(f'Copy {s_file} to {s_afsubdir_slidepxscene} ...')
                os.makedirs(s_afsubdir_slidepxscene, exist_ok=True)
                shutil.copyfile(f'{df_img.index.name}{s_file}', f'{s_afsubdir_slidepxscene}{s_file}')
        
            # add columns with input needed for af subtraction
            # BUE 20210430: maybe simple panda merge and some operation would do, no loop needed?
            for s_file in sorted(df_afsub.index.unique()):
                print(f'Add AF subtraction calculation input for {s_file} ...')
                s_slide_pxscene = df_afsub.loc[s_file, 'slide_scene']
                s_color = df_afsub.loc[s_file, 'color']
                i_round = df_afsub.loc[s_file, 'round_order']
                df_scene = df_img.loc[df_img.slide_scene == s_slide_pxscene, :]
        
                # handle late qc round
                s_late = ds_late[s_color]
                if df_scene.loc[(df_scene.marker == s_late), :].shape == (0,0):
                    sys.exit(f' Missing late AF channel for {s_slide_pxscene} {s_color}')
                df_afsub.loc[s_file, 'sub_late'] = df_scene.loc[(df_scene.marker == s_late), :].index[0]
                df_afsub.loc[s_file, 'sub_late_exp'] = df_scene.loc[(df_scene.marker == s_late), 'exposure_time_ms'][0]
        
                # if early qc round exist
                s_early = ''
                if len(ds_early) > 0:
        
                    #  handle early qc round
                    s_early = ds_early[s_color]
                    if df_scene.loc[(df_scene.marker == s_early), :].shape == (0,0):
                        sys.exit(f' Missing early AF channel for {s_slide_pxscene} {s_color}')
                    i_early = df_scene.loc[(df_scene.marker == s_early), 'round_order'][0]
                    i_late = df_scene.loc[(df_scene.marker == s_late), 'round_order'][0]
                    df_afsub.loc[s_file, 'sub_early'] = df_scene.loc[(df_scene.marker == s_early), :].index[0]
                    df_afsub.loc[s_file, 'sub_early_exp'] = df_scene.loc[(df_scene.marker == s_early),'exposure_time_ms'][0]
                    df_afsub.loc[s_file, 'sub_ratio_late'] = np.clip((i_round - i_early) / (i_late - i_early), 0, 1)
                    df_afsub.loc[s_file, 'sub_ratio_early'] = np.clip(1 - (i_round - i_early) / (i_late - i_early), 0, 1)
        
                # finalize
                df_afsub.loc[s_file,'sub_name'] = f'Sub{s_early}{s_late}' # used for filename only
        
        
            # loop to subtract
            for s_file in df_afsub.index.tolist():
                print(f'Processing AF subtraction for: {s_file} ...')
        
                # extract annotation in registered image filename and update to afsub image type
                o_match = re.search(config.d_nconv['s_regex_tiff_reg'], s_file)  # s_round, i_round, s_markers, s_slide, s_scene, color, imagetype
                s_imagetype_reg = o_match[config.d_nconv['di_regex_tiff_reg']['imagetype']]
                di_match = {}
                for i_step in range(len(o_match.groups())):
                    i_match = i_step + 1
                    di_match.update({i_match: o_match[i_match]})
                di_match[config.d_nconv['di_regex_tiff_reg']['imagetype']] = df_afsub.loc[s_file, 'sub_name'] + s_imagetype_reg
        
                # load images
                a_img = io.imread(f'{df_afsub.index.name}{s_file}')
                a_late = io.imread(f"{df_afsub.index.name}{df_afsub.loc[s_file,'sub_late']}")  # background
        
                if len(ds_early) > 0:
        
                    # divide each image by exposure time
                    a_img_exp = a_img / df_afsub.loc[s_file, 'exposure_time_ms']
                    a_early = io.imread(f"{df_afsub.index.name}{df_afsub.loc[s_file,'sub_early']}")
                    a_early_exp = a_early / df_afsub.loc[s_file,'sub_early_exp']
                    a_late_exp = a_late / df_afsub.loc[s_file, 'sub_late_exp']
        
                    # combine early and late based on round_order
                    a_early_exp = a_early_exp * df_afsub.loc[s_file, 'sub_ratio_early']
                    a_late_exp = a_late_exp * df_afsub.loc[s_file, 'sub_ratio_late']
        
                    # subtract 1 ms AF from 1 ms signal
                    # multiply by original image exposure time
                    a_sub = (a_img_exp - a_early_exp - a_late_exp) * df_afsub.loc[s_file,'exposure_time_ms']
        
                else:
                    # divide each image by exposure time
                    # subtract 1 ms AF from 1 ms signal
                    # multiply by original image exposure time
                    a_sub = (a_img / df_afsub.loc[s_file, 'exposure_time_ms'] - a_late / df_afsub.loc[s_file, 'sub_late_exp']) * df_afsub.loc[s_file, 'exposure_time_ms']
        
                # generate af subtracted tiff
                s_ofname = config.d_nconv[ 's_format_tiff_reg'].format(di_match[1], di_match[2], di_match[3], di_match[4], di_match[5], di_match[6]) #'Registered-{s_round}_{s_markers}_{s_slide}_{s_scene}_{s_color}_{s_imagetype}.tif'
                a_zero = (a_sub.clip(min=0)).astype(int)
                if b_8bit:
                    a_bit = (a_zero / 256).astype(np.uint8)
                    s_ofname = s_ofname.replace('.tif','_8bit.tif')
                else:
                    a_bit = skimage.img_as_uint(a_zero)
                io.imsave(s_afsubdir_slidepxscene+s_ofname, a_bit, check_contrast=False)


def afsub_spawn(
        es_slide,
        ddd_crop,
        ddd_etc,
        ds_early = {'c2':'R0c2','c3':'R0c3','c4':'R0c4','c5':'R0c5'},
        ds_late = {'c2':'R6Qc2','c3':'R6Qc3','c4':'R6Qc4','c5':'R6Qc5'},
        es_exclude_color = {'c1','c5'},
        es_exclude_marker = {},
        b_8bit = False,
        # processing
        s_type_processing = 'slurm',
        s_slurm_partition = 'exacloud',
        s_slurm_mem = '32G',
        s_slurm_time = '36:00:0',
        s_slurm_account = 'gray_lab',
        # file system
        s_metadir = config.d_nconv['s_metadir'],  #'MetaImages/',
        s_regdir = config.d_nconv['s_regdir'],  #'RegisteredImages/',
        s_format_regdir = config.d_nconv['s_format_regdir'],  #'{}{}/', # s_regdir, s_slide_pxscene
        s_afsubdir = config.d_nconv['s_afsubdir'],  #'SubtractedRegisteredImages/',
        s_format_afsubdir = config.d_nconv['s_format_afsubdir'],  #'{}{}/', # s_afsubdir, s_slide_pxscene
    ):
    '''
    version: 2021-12-00

    input:
        es_slide: set of slide id for which auto fluorescence subtraction should be done.
        ddd_crop: the croping dictionary that links the cropped scenes (sldie_pxscene)
            to the microscopy scenes (slide_mscene).
        ddd_etc: exposure time correction dictionary. 
            the format is {'slide_scene': {'marker': {'is': 7,'should_be': 4}},} 
            if no exposure time has to be corrected, set parameter to empty dictionary {}.
        ds_early: dictionary mapping each channel color (except DAPI channel) to the early round quenching "marker".
            if no such round exists set parameter to empty dictionary {}.
        ds_late: dictionary mapping each channel color (except DAPI channel) to the late round quenching "marker".
        es_exclude_color: microscopy channel to exclude, usually DAPI and the ones which,
            because of their higher wavelength, show no autofluorescence.
        es_exclude_marker: list of markers that do not need subtraction.
            note that all markers in the es_exclude_color channels and the markers in ds_early and ds_late will be excluded automatically.
        b_8bit: boolean to specify the auto fluorescent subtracted image should be an 8[bit] or 16[bit] image.
             default is set to False, output will be a 16[bit] tiff image.

        # processing
        s_type_processing: string to specify if pipeline is run on a slurm cluster or not.
            known vocabulary is slurm and any anything else but slurm for non-slurm processing.
        s_slurm_partition: slurm cluster partition to use.
            OHSU ACC options are 'exacloud', 'light', (and 'gpu').
            the default is tweaked to OHSU ACC settings.
        s_slurm_mem: slurm cluster memory allocation string. default is '32G'.
        s_slurm_time: slurm cluster time allocation string in hour or day format.
            OHSU ACC max is '36:00:00' [hour] or '30-0' [day].
            the related qos code is tweaked to OHSU ACC settings.
        s_slurm_account: slurm cluster account to charge time.
            OHSU ACC options are e.g. 'gray_lab', 'chin_lab', 'heiserlab', 'CEDAR'.

        # file system
        s_metadir: folder where the extracted image metadata is stored.
        s_regdir: registered image directory.
        s_format_regdir: registered image subfolder format string.
        s_afsubdir: auto fluorescent subtracted registered image directory, 
            which will be generated, if it doesn't exist.
        s_format_afsubdir: s_afsubdir subfolder format string.

    output:
        under afsub path, fluorescent subtracted registered tiff images.

    description:
        generate an auto fluorescent subtracted registers tiff images set
        utilizing registered images and exposure time information as input.
    '''
    # for each slide
    for s_slide in sorted(es_slide):
        # this has to be a python template!
        print(f'afsub_spawn: {s_slide}')

        # set run commands
        s_pathfile_afsubtraction_template = 'template_afsubtraction_slide.py'
        s_pathfile_afsubtraction = f'afsubtraction_slide_{s_slide}.py'
        s_srun_cmd = f'python3 {s_pathfile_afsubtraction}'
        ls_run_cmd = ['python3', s_pathfile_afsubtraction]

        ## any ##
        # load template af subtraction script code
        with open(f'{s_path_module}src/{s_pathfile_afsubtraction_template}') as f:
            s_stream = f.read()

        # edit code generic
        s_stream = s_stream.replace('peek_s_slide', s_slide)
        s_stream = s_stream.replace('peek_ddd_crop', str(ddd_crop))
        s_stream = s_stream.replace('peek_ddd_etc', str(ddd_etc))
        s_stream = s_stream.replace('peek_ds_early', str(ds_early))
        s_stream = s_stream.replace('peek_ds_late', str(ds_late))
        s_stream = s_stream.replace('peek_es_exclude_color', str(es_exclude_color))
        s_stream = s_stream.replace('peek_es_exclude_marker', str(es_exclude_marker))
        s_stream = s_stream.replace('peek_b_8bit', str(b_8bit))
        s_stream = s_stream.replace('peek_s_metadir', s_metadir)
        s_stream = s_stream.replace('peek_s_regdir', s_regdir)
        s_stream = s_stream.replace('peek_s_format_regdir', s_format_regdir)
        s_stream = s_stream.replace('peek_s_afsubdir', s_afsubdir)
        s_stream = s_stream.replace('peek_s_format_afsubdir', s_format_afsubdir)

        # write executable af subtraction script code to file
        time.sleep(4)
        with open(s_pathfile_afsubtraction, 'w') as f:
            f.write(s_stream)

        # execute af subtraction script
        time.sleep(4)
        if (s_type_processing == 'slurm'):
            # generate sbatch file
            s_pathfile_sbatch = f'afsubtraction_slide_{s_slide}.sbatch'
            config.slurmbatch(
                s_pathfile_sbatch=s_pathfile_sbatch,
                s_srun_cmd=s_srun_cmd,
                s_jobname=f'a{s_slide}',
                s_partition=s_slurm_partition,
                s_gpu=None,
                s_mem=s_slurm_mem,
                s_time=s_slurm_time,
                s_account=s_slurm_account,
            )
            # Jenny this is cool!
            subprocess.run(
                ['sbatch', s_pathfile_sbatch],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
        else:  # non-slurm
            # Jenny this is cool!
            s_file_stdouterr = f'slurp-afsubtraction_slide_{s_slide}.out'
            o_process = subprocess.run(
                ls_run_cmd,
                stdout=open(s_file_stdouterr, 'w'),
                stderr=subprocess.STDOUT,
            )

