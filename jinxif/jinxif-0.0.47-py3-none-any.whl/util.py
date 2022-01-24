#####
# title: util.py
#
# language: python3
# author: Jenny, bue, Isaac
# license: GPLv>=3
# date: 2021-04-00
#
# description:
#     jinxif python3 utility library.
#     these are helpful functions that are not a straight task of the pipeline.
#####


# library
from jinxif import basic
from jinxif import config
from jinxif import imgmeta
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
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


# functions

#################
# file renaming #
#################

def underscore_to_dot(
        es_slide,
        s_start = 'R',
        ei_underscore_to_dot = {1,2,3},
        s_end = 'ORG.tif',
        # filesystem
        s_rawdir = config.d_nconv['s_rawdir'],  # 'RawImages/',
        s_format_rawdir = config.d_nconv['s_format_rawdir'],  #'{}{}/',  # s_rawdir, s_slide
    ):
    '''
    version: 2021-12-00

    input:
        es_slide: set of slide ids to be processed.
        s_start: file name starts with.
        ei_underscore_to_dot: set of underscore indexes that should be replaced by dots.
        s_end: file name ends with.

        s_rawdir: work directory. default is RawImages directory.
        s_format_rawdir: subdirectory. the files are
            expected to be in s_rawdir/s_slide/ directory.

    output:
        ds_rename: renaming dictionary

    description:
        for naming convention ok image files
        change stain separator from underscore to dot.
    '''
    print('\nrun: jinxif.util.underscore_to_dot ...')
    i_max = max(ei_underscore_to_dot)
    ds_replace = {}
    for s_slide in sorted(es_slide):
        for s_file in sorted(os.listdir(f'{s_rawdir}{s_slide}/')):
            if s_file.startswith(s_start) and s_file.endswith(s_end):
                print(f'process: {s_file}')
                s_old = ''
                s_new = ''
                for i_stain, s_stain in enumerate(s_file.split('_')):
                    s_old += s_stain + '_'
                    if i_stain in ei_underscore_to_dot:
                        s_new += s_stain + '.'
                    else:
                        s_new += s_stain + '_'
                    if (i_stain > i_max):
                       break
                if (s_new != s_old):
                    ds_replace.update({s_old: s_new})
    # output
    print('found:', sorted(ds_replace.items()))
    return(ds_replace)


def dchange_fname(
        ds_rename={'_oldstring_':'_newstring_'},
        b_test=True,
        s_wd='./',
    ):
    '''
    version: 2021-12-00

    input:
        d_rename: {'_oldstring_':'_newstring_'}.
        b_test: for dry run set boolean to True. default is True.
        s_wd: working directory. default is the present working directory. # bue 20210330: actually RawImages/slide/

    output:
        stdout
        changed filenames, if b_test=False

    description:
        replace anything in file name, based on dictionary.
        key = old, values = new.
    '''
    print('\nrun: jinxif.util.dchange_fname ...')
    for s_old, s_new in sorted(ds_rename.items()):
        i_change = 0
        for s_file in os.listdir(s_wd):
            if s_file.find(s_old) > -1:
                i_change += 1
                s_file_old = s_file
                s_file_new = s_file.replace(s_old,s_new)
                #print(f'changed file {s_file_old}\tto {s_file_new}')
                if not (b_test):
                    os.rename(f'{s_wd}{s_file}', f'{s_wd}{s_file_new}')
        if i_change > 0:
            print(f'changed {s_old} file\n{s_file_old} to\n{s_file_new} ...')
        print(f'total number of {s_old} files changed is {i_change}\n')


#############################################
# xz level 9 compression and de-compression #
#############################################

# compress files
def compress_tiff_raw(
        s_slide,
        # filesystem
        s_rawdir = config.d_nconv['s_rawdir'],  # 'RawImages/',
        s_format_rawdir = config.d_nconv['s_format_rawdir'],  #'{}{}/',  # s_rawdir, s_slide
    ):
    '''
    version: 2021-12-00

    input:
        s_slide: slide id to be processed.
        s_rawdir: work directory. default is RawImages directory.
        s_format_rawdir: subdirectory. the files are
            expected to be in s_rawdir/s_slide/ directory.

    output:
        xz level 9 compressed raw tiff files and a lot of disk space.

    description:
        pipeline element to do xz compression on raw tiffs.
    '''
    print(f'run jinxif.util.compress_tiff_raw on {s_slide} ...')
    # get files
    df_img = basic.parse_tiff_raw(s_wd=s_format_rawdir.format(s_rawdir, s_slide))
    for s_file in df_img.index:
        # compress file
        os.system(f'xz -v -9 {df_img.index.name}{s_file}')
        #break


def compress_czi_original(
        s_slide,
        # filesystem
        s_czidir = config.d_nconv['s_czidir'],  # 'CziImages/',
        s_format_czidir_original = config.d_nconv['s_format_czidir_original'],  #'{}{}/original/',  # s_czidir, s_slide
    ):
    '''
    version: 2021-12-00

    input:
        s_slide: slide id to be processed.
        s_czidir: work directory. default is CziImages directory.
        s_format_czidir_original: subdirectory. the files are
            expected to be in s_czidir/s_slide/original/ directory.

    output:
        xz level 9 compressed czi split scene files and a lot of disk space.

    description:
        pipeline element to do xz compression on split scene czi files.
    '''
    print(f'run jinxif.util.compress_czi_original on {s_slide} ...')
    # get files
    df_img = basic.parse_czi_original(s_wd=s_format_czidir_original.format(s_czidir, s_slide))
    for s_file in df_img.index:
        # compress file
        os.system(f'xz -v -9 {df_img.index.name}{s_file}')
        #break


def compress_czi_splitscene(
        s_slide,
        # filesystem
        s_czidir = config.d_nconv['s_czidir'],  # 'CziImages/',
        s_format_czidir_splitscene = config.d_nconv['s_format_czidir_splitscene'],  #'{}{}/splitscene/',  # s_czidir, s_slide
    ):
    '''
    version: 2021-12-00

    input:
        s_slide: slide id to be processed.
        s_czidir: work directory. default is CziImages directory.
        s_format_czidir_splitscene: subdirectory. the files are
            expected to be in s_czidir/s_slide/splitscenes/ directory.

    output:
        xz level 9 compressed czi split scene files and a lot of disk space.

    description:
        pipeline element to do xz compression on split scene czi files.
    '''
    print(f'run jinxif.util.compress_czi_splitscene on {s_slide} ...')
    # get files
    df_img = basic.parse_czi_splitscene(s_wd=s_format_czidir_splitscene.format(s_czidir, s_slide))
    for s_file in df_img.index:
        # compress file
        os.system(f'xz -v -9 {df_img.index.name}{s_file}')
        #break


def compress_xz_spawn(
        es_slide,
        b_tiff_raw = False,
        b_czi_original = False,
        b_czi_splitscene = False,
        # processing
        s_type_processing = 'slurm',
        s_slurm_partition = 'exacloud',
        s_slurm_mem = '32G',
        s_slurm_time = '36:00:0',
        s_slurm_account = 'gray_lab',
        # filesystem
        s_rawdir = config.d_nconv['s_rawdir'],  # 'RawImages/',
        s_format_rawdir = config.d_nconv['s_format_rawdir'],  #'{}{}/',  # s_rawdir, s_slide
        s_czidir = config.d_nconv['s_czidir'],  # 'CziImages/',
        s_format_czidir_original = config.d_nconv['s_format_czidir_original'],  #'{}{}/original/',  # s_czidir, s_slide
        s_format_czidir_splitscene = config.d_nconv['s_format_czidir_splitscene'],  #'{}{}/splitscene/',  # s_czidir, s_slide
    ):
    '''
    version: 2021-07-03

    input:
        es_slide: set of slides that should be loaded.
        b_tiff_raw: boolean to specify if files in the RawImages folder should be compressed. default is False.
        b_czi_original: boolean to specify if files in the CziImages/original folder should be compressed. default is False.
        b_czi_splitscene: boolean to specify if files in the CziImages/splitscenes folder should be compressed. default is False.

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
            OHSU ACC options are e.g. 'gray_lab', 'chin_lab', 'CEDAR'.

        s_rawdir: work directory. default is RawImages directory.
        s_format_rawdir: subdirectory. the files are
            expected to be in s_rawdir/s_slide/ directory.
        s_czidir: work directory. default is CziImages directory.
        s_format_czidir_original: subdirectory. the files are
            expected to be in s_czidir/s_slide/original/ directory.
        s_format_czidir_splitscene: subdirectory. the files are
            expected to be in s_czidir/s_slide/splitscenes/ directory.

    output:
        xz level 9 compressed files and a lot of disk space.

    description:
        spawner function for util.compress_*_* functions.
    '''
    # for each slide
    for s_slide in sorted(es_slide):
        # this has to be a python template!
        print(f'compress_xz_spawn : b_tiff_raw {b_tiff_raw} | b_czi_original {b_czi_original} | b_czi_splitscene {b_czi_splitscene} : {s_slide}')

        # set run commands
        s_pathfile_template = 'template_xzcompress_slide.py'
        s_pathfile = f'xzcompress_slide_{s_slide}_{b_tiff_raw}_{b_czi_original}_{b_czi_splitscene}.py'
        s_srun_cmd = f'python3 {s_pathfile}'
        ls_run_cmd = ['python3', s_pathfile]

        ## any ##
        # load template xz compress script code
        with open(f'{s_path_module}src/{s_pathfile_template}') as f:
            s_stream = f.read()

        # edit code generic
        s_stream = s_stream.replace('peek_s_slide', s_slide)
        s_stream = s_stream.replace('peek_b_tiff_raw', str(b_tiff_raw))
        s_stream = s_stream.replace('peek_b_czi_original', str(b_czi_original))
        s_stream = s_stream.replace('peek_b_czi_splitscene', str(b_czi_splitscene))
        s_stream = s_stream.replace('peek_s_rawdir', s_rawdir)
        s_stream = s_stream.replace('peek_s_format_rawdir', s_format_rawdir)
        s_stream = s_stream.replace('peek_s_czidir', s_czidir)
        s_stream = s_stream.replace('peek_s_format_czidir_original', s_format_czidir_original)
        s_stream = s_stream.replace('peek_s_format_czidir_splitscene', s_format_czidir_splitscene)

        # write executable xz compress script code to file
        time.sleep(4)
        with open(s_pathfile, 'w') as f:
            f.write(s_stream)

        # execute afsubtraction script
        time.sleep(4)
        if (s_type_processing == 'slurm'):
            # generate sbatch file
            s_pathfile_sbatch = f'xzcompress_slide_{s_slide}_{b_tiff_raw}_{b_czi_original}_{b_czi_splitscene}.sbatch'
            config.slurmbatch(
                s_pathfile_sbatch = s_pathfile_sbatch,
                s_srun_cmd = s_srun_cmd,
                s_jobname = f'c{s_slide}',
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
            s_file_stdouterr = f'slurp-xzcompress_slide_{s_slide}_{b_tiff_raw}_{b_czi_original}_{b_czi_splitscene}.out'
            o_process = subprocess.run(
                ls_run_cmd,
                stdout=open(s_file_stdouterr, 'w'),
                stderr=subprocess.STDOUT,
            )


# de-compress
def decompress_tiff_raw(
        s_slide,
        # filesystem
        s_rawdir = config.d_nconv['s_rawdir'],  # 'RawImages/',
        s_format_rawdir = config.d_nconv['s_format_rawdir'],  #'{}{}/',  # s_rawdir, s_slide
    ):
    '''
    version: 2021-12-00

    input:
        s_slide: slide id to be processed.
        s_rawdir: work directory. default is RawImages directory.
        s_format_rawdir: subdirectory. the files are
            expected to be in s_rawdir/s_slide/ directory.

    output:
        decompressed xz compressed raw tiff files.

    description:
        pipeline element to do de-copression on xz compressed raw tiffs.
    '''
    print(f'run jinxif.util.decompress_tiff_raw on {s_slide} ...')
    # get xz compressed raw tiff files
    s_path = s_format_rawdir.format(s_rawdir, s_slide)
    for s_file in sorted(os.listdir(s_path)):
        if s_file.endswith('.tiff.xz') or s_file.endswith('.tif.xz'):
            # decompress file
            os.system(f'xz -v -d {s_path}{s_file}')


def decompress_czi_original(
        s_slide,
        # filesystem
        s_czidir = config.d_nconv['s_czidir'],  # 'CziImages/',
        s_format_czidir_original = config.d_nconv['s_format_czidir_original'],  #'{}{}/original/',  # s_czidir, s_slide
    ):
    '''
    version: 2021-12-00

    input:
        s_slide: slide id to be processed.
        s_czidir: work directory. default is CziImages directory.
        s_format_czidir_original: subdirectory. the files are
            expected to be in s_czidir/s_slide/original/ directory.

    output:
        decompressed xz compressed czi original files.

    description:
        pipeline element to do de-copression on xz compressed original czi files.
    '''
    print(f'run jinxif.util.decompress_czi_original on {s_slide} ...')
    # get xz compressed files
    s_path = s_format_czidir_original.format(s_czidir, s_slide)
    for s_file in sorted(os.listdir(s_path)):
        if s_file.endswith('.czi.xz') or s_file.endswith('.tiff.xz') or s_file.endswith('.tif.xz'):
            # decompress file
            os.system(f'xz -v -d {s_path}{s_file}')


def decompress_czi_splitscene(
        s_slide,
        # filesystem
        s_czidir = config.d_nconv['s_czidir'],  # 'CziImages/',
        s_format_czidir_splitscene = config.d_nconv['s_format_czidir_splitscene'],  #'{}{}/',  # s_czidir, s_slide
    ):
    '''
    version: 2021-12-00

    input:
        s_slide: slide id to be processed.
        s_czidir: work directory. default is CziImages directory.
        s_format_czidir_splitscene: subdirectory. the files are
            expected to be in s_czidir/s_slide/splitscenes/ directory.

    output:
        decompressed xz compressed czi splitscene files.

    description:
        pipeline element to do de-copression on xz compressed splitscene czi files.
    '''
    print(f'run jinxif.util.decompress_czi_splitscene on {s_slide} ...')
    # get xz compressed files
    s_path = s_format_czidir_splitscene.format(s_czidir, s_slide)
    for s_file in sorted(os.listdir(s_path)):
        if s_file.endswith('.czi.xz') or s_file.endswith('.tiff.xz') or s_file.endswith('.tif.xz'):
            # decompress file
            os.system(f'xz -v -d {s_path}{s_file}')


def decompress_xz_spawn(
        es_slide,
        b_tiff_raw = False,
        b_czi_original = False,
        b_czi_splitscene = False,
        # processing
        s_type_processing = 'slurm',
        s_slurm_partition = 'exacloud',
        s_slurm_mem = '32G',
        s_slurm_time = '36:00:0',
        s_slurm_account = 'gray_lab',
        # filesystem
        s_rawdir = config.d_nconv['s_rawdir'],  # 'RawImages/',
        s_format_rawdir = config.d_nconv['s_format_rawdir'],  #'{}{}/',  # s_rawdir, s_slide
        s_czidir = config.d_nconv['s_czidir'],  # 'CziImages/',
        s_format_czidir_original = config.d_nconv['s_format_czidir_original'],  #'{}{}/original/',  # s_czidir, s_slide
        s_format_czidir_splitscene = config.d_nconv['s_format_czidir_splitscene'],  #'{}{}/splitscene/',  # s_czidir, s_slide
    ):
    '''
    version: 2021-12-00

    input:
        es_slide: set of slides that should be loaded.
        b_tiff_raw: boolean to specify if files in the RawImages folder should be decompressed. default is False.
        b_czi_original: boolean to specify if files in the CziImages/original folder should be decompressed. default is False.
        b_czi_splitscene: boolean to specify if files in the CziImages/splitscenes folder should be decompressed. default is False.

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
            OHSU ACC options are e.g. 'gray_lab', 'chin_lab', 'CEDAR'.

        s_rawdir: work directory. default is RawImages directory.
        s_format_rawdir: subdirectory. the files are
            expected to be in s_rawdir/s_slide/ directory.
        s_czidir: work directory. default is CziImages directory.
        s_format_czidir_original: subdirectory. the files are
            expected to be in s_czidir/s_slide/original/ directory.
        s_format_czidir_splitscene: subdirectory. the files are
            expected to be in s_czidir/s_slide/splitscenes/ directory.

    output:
        decompressed xz compressed files.

    description:
        spawner function for util.decompress_*_* functions.
    '''
    # for each slide
    for s_slide in sorted(es_slide):
        # this has to be a python template!
        print(f'decompress_xz_spawn : b_tiff_raw {b_tiff_raw} | b_czi_original {b_czi_original} | b_czi_splitscene {b_czi_splitscene} : {s_slide}')

        # set run commands
        s_pathfile_template = 'template_xzdecompress_slide.py'
        s_pathfile = f'xzdecompress_slide_{s_slide}_{b_tiff_raw}_{b_czi_original}_{b_czi_splitscene}.py'
        s_srun_cmd = f'python3 {s_pathfile}'
        ls_run_cmd = ['python3', s_pathfile]

        ## any ##
        # load template xz decompress script code
        with open(f'{s_path_module}src/{s_pathfile_template}') as f:
            s_stream = f.read()

        # edit code generic
        s_stream = s_stream.replace('peek_s_slide', s_slide)
        s_stream = s_stream.replace('peek_b_tiff_raw', str(b_tiff_raw))
        s_stream = s_stream.replace('peek_b_czi_original', str(b_czi_original))
        s_stream = s_stream.replace('peek_b_czi_splitscene', str(b_czi_splitscene))
        s_stream = s_stream.replace('peek_s_rawdir', s_rawdir)
        s_stream = s_stream.replace('peek_s_format_rawdir', s_format_rawdir)
        s_stream = s_stream.replace('peek_s_czidir', s_czidir)
        s_stream = s_stream.replace('peek_s_format_czidir_original', s_format_czidir_original)
        s_stream = s_stream.replace('peek_s_format_czidir_splitscene', s_format_czidir_splitscene)

        # write executable xz decompress script code to file
        time.sleep(4)
        with open(s_pathfile, 'w') as f:
            f.write(s_stream)

        # execute afsubtraction script
        time.sleep(4)
        if (s_type_processing == 'slurm'):
            # generate sbatch file
            s_pathfile_sbatch = f'xzdecompress_slide_{s_slide}_{b_tiff_raw}_{b_czi_original}_{b_czi_splitscene}.sbatch'
            config.slurmbatch(
                s_pathfile_sbatch = s_pathfile_sbatch,
                s_srun_cmd = s_srun_cmd,
                s_jobname = f'd{s_slide}',
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
            s_file_stdouterr = f'slurp-xzdecompress_slide_{s_slide}_{b_tiff_raw}_{b_czi_original}_{b_czi_splitscene}.out'
            o_process = subprocess.run(
                ls_run_cmd,
                stdout=open(s_file_stdouterr, 'w'),
                stderr=subprocess.STDOUT,
            )


############
# cropping #
#############

# dddcrop
def template_dddcrop(
       ls_slide,
       # filesystem
       s_rawdir = config.d_nconv['s_rawdir'],  #'RawImages/'],
       s_format_rawdir = config.d_nconv['s_format_rawdir'],  #'{}{}/',  # s_rawdir, s_slide
       s_metadir = config.d_nconv['s_metadir'],  #'MetaImages/',
       s_format_metafile_tmacoorcsv = '{}{}_ScenePositions_coor_ok.csv',  # s_metadir, s_slide
       s_type_coor = 'xywh',  # xywh xyxy yxyx none
    ):
    '''
    version: 2021-12-00

    input:
        ls_slide: list of slide id that will be processed.

        s_rawdir: string to specify raw images directory.
            this is the main input data
        s_format_rawdir:s_rawdir subfolder structure.
        s_metadir: string to specify images meta data directory.
            if a for a slide a ScenePosition_coor.csv file is found,
            then the pxscene are translated in alphanumeric coordinates.
        s_format_metafile_tmacoorcsv: format string to specify
            the scene position csv file to be used.
        s_type_coor: string to specify the coordinate type.
            possible values are 'none', 'yxyx', 'xyxy', 'xywh'.
            if set 'none', the crop information will be None.
            if set 'yxyx', the template crop information will be [0,0,0,0,'yxyx'],
            if set 'xyxy', the template crop information will be [0,0,0,0,'xyxy'],
            if set 'xywh', the template crop information will be [0,0,0,0,'xywh'],
            then 0,0, 0,0 coordinates can then later be  adjusted to the real values.
            default is 'xywh'.

    output:
        ddd_crop: template crop dictionary.

    description:
        generate ddd_crop template.
    '''
    print('run: jinxif.util.template_dddcrop ...')
    ddd_crop = {}

    # for each slide
    for s_slide in ls_slide:

        # check if slide a tma
        s_pathfile_tmacoorcsv = s_format_metafile_tmacoorcsv.format(s_metadir, s_slide)
        if os.path.isfile(s_pathfile_tmacoorcsv):
            b_tma = True
            df_tma = pd.read_csv(s_pathfile_tmacoorcsv, index_col=0)
        else:
            b_tma = False

        # processing
        dd_crop = {}
        df_img = basic.parse_tiff_raw(s_wd=s_format_rawdir.format(s_rawdir, s_slide))
        df_img = df_img.loc[df_img.slide == s_slide,:]
        for s_mscene in sorted(df_img.mscene.unique()):
            d_crop = {}

            # generate pxscene id
            si_mscene = re.sub(r'[^\d]', '', s_mscene)
            if (si_mscene == ''):
                i_mscene = 0
            else:
                i_mscene = int(si_mscene)
            if b_tma:
                s_pxscene = 'scene' + df_tma.loc[df_tma.mscene == i_mscene, 'scene_coor'].values[0]
            else:
                s_pxscene = 'scene' + str(i_mscene).zfill(3)

            # generate crop definition
            if (s_type_coor == 'none') or (s_type_coor == 'None') or (s_type_coor is None):
                o_crop = None
            elif s_type_coor == 'yxyx':
                o_crop = [0,0,0,0,'yxyx']
            elif s_type_coor == 'xyxy':
                o_crop = [0,0,0,0,'xyxy']
            elif s_type_coor == 'xywh':
                o_crop = [0,0,0,0,'xywh']
            else:
                sys.exit(f'Error @ jinxif.util.template_dddcrop : unknown s_type_coor {s_type_coor}. known are none, yxyx, xyxy, xywh.')

            # update output
            d_crop.update({s_pxscene : o_crop})
            dd_crop.update({s_mscene: d_crop})
        # update output
        ddd_crop.update({s_slide: dd_crop})

    # output
    #print(ddd_crop)
    return(ddd_crop)


def gridcrop(
        li_xywh,
        i_max = 20000,
    ):
    '''
    version: 2021-12-00

    input:
        li_xywh: list of integer to specify the whole tissue square to be cropped.
        i_max: integer, to specify the max high and wide length
            a cropped rectangle can have.

    output:
        dl_crop: dictionary of list of xyxy cropped rectangle specifications,
            no one is higher or wider than i_max.

    definition:
        this function breaks a li_xywh specified rectangle down to rectangles
        that are neither higher nor wider than the specified by i_max.
        the result is a list of specifications of this smaller rectangle,
        listed from top, left to right to bottom.
    '''
    print('run: jinxif.util.gridcrop ...')

    # handle input
    i_x_multiplication = int(np.ceil(li_xywh[2] / i_max))
    i_y_multiplicator = int(np.ceil(li_xywh[3] / i_max))
    i_x_real = np.ceil(li_xywh[2] / i_x_multiplication)
    i_y_real = np.ceil(li_xywh[3] / i_y_multiplicator)

    # process
    n = 0
    dl_crop = {}
    i_y = li_xywh[1] - i_y_real
    for _ in range(i_y_multiplicator):
        i_y += i_y_real
        i_x = li_xywh[0] - i_x_real
        for _ in range(i_x_multiplication):
            n += 1
            i_x += i_x_real
            l_crop = [int(i_x),int(i_y), int(i_x+i_x_real),int(i_y+i_y_real), 'xyxy']
            # update ondle input
            dl_crop.update({f'scene{str(n).zfill(3)}': l_crop})
    # output
    #print(dl_crop)
    return(dl_crop)


def crop(
        s_file_img,
        l_crop,
        s_type_coor = 'xywh',  # xywh xyxy yxyx
    ):
    '''
    version: 2021-12-00

    input:
        s_file_img: path file to the image that should be cropped.
        l_crop: list of pixel based cropping coordinates
            according to the s_type_coor specified below.
        s_type_coor: string to specify the coordinate type.
            possible values are 'xyxy' or 'yxyx' which specifies the top left and bottom right corner
            and 'xywh' which specifies the top left corner and wide and height.
            default is 'xywh'.

    output:
        image under same path with same filename but added _crop in front of the file extension.

    description:
        function to crop images that already are registered,
        or the image that is registered too.
    '''
    # load image as numpy array
    ai_imag = io.imread(s_file_img)

    # crop array
    if (s_type_coor == 'xyxy'):
        l_cut = l_crop
    elif (s_type_coor == 'yxyx'):
        l_cut = [l_crop[1],l_crop[0], l_crop[3],l_crop[2]]
    elif (s_type_coor == 'xywh'):
        l_cut = [l_crop[0], l_crop[1], l_crop[0] + l_crop[2], l_crop[1] + l_crop[3]]
    else:
        sys.exit('Error @ jinxif.util.crop : unknown s_type_coor {s_type_coor}.\nknown are xyxy, yxyxy, and xywh.')
    ai_crop = ai_imag[l_cut[1]:l_cut[3], l_cut[0]:l_cut[2]]

    # save numpy array as image
    s_ext = '.' + s_file_img.split('.')[-1]
    s_file_crop = s_file_img.replace(s_ext, f'-crop{s_ext}')
    io.imsave(s_file_crop, ai_crop, check_contrast=False)


def crop_spawn(
        ddd_crop,
        es_slide = None,
        # processing
        s_type_processing = 'slurm',
        s_slurm_partition = 'exacloud',
        s_slurm_mem = '32G',
        s_slurm_time = '36:00:0',
        s_slurm_account = 'gray_lab',
        # filesystem
        s_regdir = config.d_nconv['s_regdir'],  #'RegisteredImages/'],
        s_croppedregdir = config.d_nconv['s_croppedregdir'],  #'CroppedRegisteredImages/',
        s_format_regdir = config.d_nconv['s_format_regdir'],  #'{}{}/',  # s_regdir, s_slidepxscene
    ):
    '''
    version: 2021-12-00

    input:
        ddd_crop: crop dictionary.
        es_slide: set of slide ids to be processed.

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
            OHSU ACC options are e.g. 'gray_lab', 'chin_lab', 'CEDAR'.

        s_regdir: registered image input directory.
        s_croppedregdir: cropped registered image output directory.
        s_format_regdir: s_regdir and s_croppedregdir subdirectory structure.

    output:
        cropped registered images under s_croppedregdir

    description:
        spawner function to run crop.
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
            print(f'spawn jinxif.util.crop for: {s_slide} {s_mscene} {sorted(ddd_crop[s_slide][s_mscene])}')

            # set run commands
            s_pathfile_crop_template = 'template_crop_mscene.py'
            s_pathfile_crop = f'crop_slide_{s_slide}_mscene_{s_mscene}.py'
            s_srun_cmd = f'python3 {s_pathfile_crop}'
            ls_run_cmd = ['python3', s_pathfile_crop]

            ## any ##
            # load template crop script code
            with open(f'{s_path_module}src/{s_pathfile_crop_template}') as f:
                s_stream = f.read()

            # edit code generic
            s_stream = s_stream.replace('peek_s_slide', s_slide)
            s_stream = s_stream.replace('peek_s_mscene', s_mscene)
            s_stream = s_stream.replace('peek_d_crop', str(ddd_crop[s_slide][s_mscene]))
            s_stream = s_stream.replace('peek_s_regdir', s_regdir)
            s_stream = s_stream.replace('peek_s_croppedregdir', s_croppedregdir)
            s_stream = s_stream.replace('peek_s_format_regdir', s_format_regdir)

            # write executable crop script code to file
            time.sleep(4)
            with open(s_pathfile_crop, 'w') as f:
                f.write(s_stream)

            # execute crop script
            time.sleep(4)
            if (s_type_processing == 'slurm'):
                # generate sbatch file
                s_pathfile_sbatch = f'crop_{s_slide}_{s_mscene}.sbatch'
                config.slurmbatch(
                    s_pathfile_sbatch=s_pathfile_sbatch,
                    s_srun_cmd=s_srun_cmd,
                    s_jobname=f'c{s_slide}_{s_mscene}',
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
                s_file_stdouterr = f'slurp-crop_{s_slide}_{s_mscene}.out'
                subprocess.run(
                    ls_run_cmd,
                    stdout=open(s_file_stdouterr, 'w'),
                    stderr=subprocess.STDOUT,
                )


####################
# tma coordinate #
#################

def _tma_radius(
        lr_one_axis_tma_center,
        i_core_axis = None,
        r_sampler = 0.98,
    ):
    '''
    version: 2021-12-00

    input:
        lr_one_axis_tma_center: list of real number x or y axis centroid coordinates from all TMAs in the array.

        i_core_axis: number of core rows (or columns) on this axis.
            if given a number, then, in addition to the relative spacing between each core,
            also, the absolute possible spacing per core is considered.
            if set to None, then only the relative spacing between each core will be considered.
            default setting is None.

        r_sampler: because there might be TMAs missing, we drop the top 1 - r_sampler values
            from the ascending sorted distance data, before we do the radius calculation.
            r_sampler value should be between 0 and 1. default is 0.98 .
            that the calculation works,
            r_sampler should not be smaller than 1 - (number of columns or rows) / (number of TMA).
            column or rows, whatever value is bigger.
            also, r_sampler should not be bigger than 1 - (missing TMA) / (number of TMA)
            number of TMA == number of non-missing TMA.

    output:
        r_radius: estimated TMA radius value.

    description:
        function to estimate the TMA radius.
        this is a huge overestimation, as it in the big picture just
        divide the distance from the center of two neighbor TMAs by two but for our need this is good enough.
    '''
    # get radius by scene position
    lr_diameter = []
    r_j = None
    for r_i in sorted(lr_one_axis_tma_center, reverse=True):
        if not (r_j is None):
            r_d = r_j - r_i
            lr_diameter.append(r_d)
        r_j = r_i
    i_data = int(len(lr_diameter) * r_sampler)
    r_radius = max(sorted(lr_diameter)[:i_data]) / 2

    # take the absolute space into account
    if not (i_core_axis is None):
        r_radius_abs = (max(lr_one_axis_tma_center) - min(lr_one_axis_tma_center)) / i_core_axis
        r_radius = (r_radius_abs + r_radius) / 2

    # output
    return(r_radius)


def tma_grid(
        s_slide,
        i_core_yaxis = None,
        i_core_xaxis = None,
        r_sampler = 0.98,
        # filesystem
        s_metadir = config.d_nconv['s_metadir'],  #'MetaImages/',
    ):
    '''
    version: 2021-12-00

    input:
        s_slide: slide to load exposure data from.

        i_yx_coor: number of core rows (or columns) on this axis.
            if given a number, then, in addition to the relative spacing between each core,
            also, the absolute possible spacing per core is considered.
            if set to None, then only the relative spacing between each core will be considered.
            default setting is None.

        r_sampler: because there might be TMAs missing, we drop the top 1 - r_sampler values
            from the ascending sorted distance data, before we do the radius calculation.
            r_sampler value should be between 0 and 1. default is 0.98.

        s_metadir: metadata csv file directory.

    output:
        csv file with coordinates.
        png plot for qc.

    description:
        layout a TMA and get coordinate information for each core.
    '''
    print('\nrun: jinxif.util.tma_grid ...')

    # load and transform data
    df_coor = imgmeta.load_position_df(
        s_slide = s_slide,
        s_metadir = s_metadir,
    )

    # get y coordinate loop
    # from small to large
    df_coor.sort_values('scene_y', ascending=True, inplace=True)
    li_coor = []
    r_yradius = _tma_radius(
        list(df_coor.scene_y),
        i_core_axis = i_core_yaxis,
        r_sampler=r_sampler,
    )
    r_break = None
    for r_y1 in df_coor.scene_y:
        if (r_break is None):
            i_coor = 0
            r_break = r_y1 + r_yradius  # operator dependent on ascending = True
        elif (r_y1 > r_break):  # operator dependent on ascending = True
            i_coor += 1
            r_break = r_y1 + r_yradius # operator dependent on ascending = True
        li_coor.append(i_coor)
        print(f'y coor: {r_yradius} {r_y1} {r_break} {i_coor}')
    df_coor['grid_y'] = li_coor

    # get x coordinate loop
    # from small to large on the negative scale
    df_coor.sort_values('scene_x', ascending=True, inplace=True)
    li_coor = []
    r_xradius = _tma_radius(
        list(df_coor.scene_x),
        i_core_axis = i_core_xaxis,
        r_sampler=r_sampler,
    )
    r_break = None
    for r_x1 in df_coor.scene_x:
        if (r_break is None):
            i_coor = 0
            r_break = r_x1 + r_xradius  # operator dependent on ascending = True
        elif (r_x1 > r_break):  # operator dependent on ascending = True
            i_coor += 1
            r_break = r_x1 + r_xradius  # operator dependent on ascending = True
        li_coor.append(i_coor)
        print(f'x coor: {r_xradius} {r_x1} {r_break} {i_coor}')
    df_coor['grid_x'] = li_coor

    # get microscopy scene id
    df_coor.sort_values(['grid_y','grid_x'], ascending=True, inplace=True)
    df_coor['mscene'] = [i for i in range(1, df_coor.shape[0]+1)]

    # get scene coordinate
    d_coor = {
        0:'A', 1:'B', 2:'C', 3:'D', 4:'E', 5:'F', 6:'G', 7:'H', 8:'I', 9:'J',
        10:'K', 11:'L', 12:'M', 13:'N', 14:'O', 15:'P', 16:'Q', 17:'R', 18:'S', 19:'T',
        20:'U', 21:'V', 22:'W', 23:'X', 24:'Y', 25:'Z',
        #26:'AA', 27:'AB', 28:'AC', 29:'AD',
        #30:'AE',
    }
    df_coor['scene_coor'] = df_coor.T.apply(lambda n: d_coor[n.grid_y] + str(int(n.grid_x + 1)).zfill(2))

    # generate tick labels
    li_grid_y = sorted(set(df_coor.grid_y))
    ls_grid_y = [d_coor[i_grid_y] for i_grid_y in li_grid_y]
    li_grid_x = [i_grid_x + 1 for i_grid_x in sorted(set(df_coor.grid_x))]

    # write result to file
    s_pathfile_csv = f'{s_metadir}{s_slide}_ScenePositions_coor.csv'
    df_coor.to_csv(s_pathfile_csv)
    print('write to file:', s_pathfile_csv)

    # qc plot result
    s_pathfile_png = f'{s_metadir}{s_slide}_ScenePositions_coor_{r_sampler}.png'
    s_title = f'{s_slide}_ScenePositions'
    fig, ax = plt.subplots(nrows=2, ncols=1, figsize=(8,12))
    df_coor.plot(kind='scatter', x='grid_x', y='grid_y', c='maroon', s=128, grid=True, title=s_title, ax=ax[0])
    df_coor.plot(kind='scatter', x='scene_x', y='scene_y', c='orange', s=128, grid=True, ax=ax[1])
    ax[0].set_ylim(ax[0].get_ylim()[::-1])
    ax[1].set_ylim(ax[1].get_ylim()[::-1])
    ax[0].set_xticks(np.arange(0, (len(li_grid_x)), 1))
    ax[0].set_xticklabels(li_grid_x)
    ax[0].set_yticks(np.arange(0, (len(li_grid_y)), 1))
    ax[0].set_yticklabels(ls_grid_y)
    ax[0].set_aspect('equal')
    ax[1].set_aspect('equal')
    plt.tight_layout()
    fig.savefig(s_pathfile_png, facecolor='white')
    print('write to file:', s_pathfile_png)


############################
# exposure time correction #
#############################

def template_dddetc(
       ls_slidepxscene,
    ):
    '''
    version: 2021-12-00

    input:
        ls_slidepxscene: list of slide_pxscene id with wrong marker expression.

    output:
        ddd_slidepxscene_marker_exposuretime_correct: batch wide
            exposure time correction dictionary template.

    description:
        generate ddd_slidepxscene_marker_exposuretime_correct template.
    '''
    print('run: jinxif.util.template_dddetc ...')

    # marker template
    dd_marker_exposuretime_correct = {
        'marker': {
            'is': 0,
            'should_be': 0,
        }
    }

    # for each slidepxscene
    ddd_slidepxscene_marker_exposuretime_correct = {}
    for s_slidepxscene in ls_slidepxscene:
        # update output
        ddd_slidepxscene_marker_exposuretime_correct.update({
            s_slidepxscene: dd_marker_exposuretime_correct
        })
    # output
    #print(ddd_slidepxscene_marker_exposuretime_correct)
    return(ddd_slidepxscene_marker_exposuretime_correct)


############################
# clean out work directory #
############################

def sweep():
    '''
    version: 2021-12-00

    input: None

    output:
        cleaned up jinxif pipeline workdirectory.

    description:
        this function is to tidy up the work directory where the jinxif
        mpleximage_data_extraction_pipeline.ipynb pipeline was run.
        mainly, the function generates a scripts folder and puts all scripts that were run by the pipeline into it.
        also, if the scripts were run by slurm, the function deletes all slurm-*.out output files.
    '''
    os.makedirs('./scripts', exist_ok=True)
    os.system('rm slurm-*')
    os.system('mv slurp-* scripts/')
    os.system('mv afsubtraction_slide_*  scripts/')
    os.system('mv thresh_slide_* scripts/')
    os.system('mv exposuretimecorrect_slidepxscene_* scripts/')
    os.system('mv extractfeature_slide_* scripts/')
    os.system('mv featurecorrectlabels_slide_* scripts/')
    os.system('mv filterfeature_slide_* scripts/')
    os.system('mv nuccellzprojlabel_slide_* scripts/')
    os.system('mv registration_* scripts/')
    os.system('mv segmentation_* scripts/')
    os.system('mv vizrawimage_slide_* scripts/')
    os.system('mv vizregimage_slide_* scripts/')
    os.system('mv xzcompress_slide_* scripts/')
    os.system('mv xzdecompress_slide_* scripts/')
    os.system('mv ometiff_* scripts/')
    os.system('mv micspatch_slide_* scripts/')

