#####
# title: sane.py
#
# language: python3
# author: Jenny, bue
# license: GPLv>=3
# date: 2021-04-00
#
# description:
#     jinxif python3 library to sanity check
#     + filename naming convention
#     + completeness of the file set
#####


# library
from jinxif import basic
from jinxif import config
from jinxif import jfplt
import os
import re
import subprocess
import time

# development
#import importlib
#importlib.reload()

# global var
s_path_module = os.path.abspath(os.path.dirname(__file__))
s_path_module = re.sub(r'jinxif$','jinxif/', s_path_module)


# function
def count_images(df_img):
    '''
    version: 2021-12-00

    input:
        df_img: parsed image file name dataframe.

    output:
        stdout: standard output.

    description:
        count and list slide names, slides, scenes, and rounds.
    '''
    # bue: jenny this is very creative code!
    ls_slide = sorted(set(df_img.slide))
    print(f'\nSlide names: {ls_slide}')
    for s_slide in ls_slide:
        print(f'Slide: {s_slide}')
        df_img_slide = df_img[df_img.slide==s_slide]
        print('Detect scenetyp and scenes ...')
        # microscopy scenes
        print('  microscopy scene: rounds')
        try:
            [print(f'{s_slidemscene}: {sum(df_img_slide.slide_mscene==s_slidemscene)}') for s_slidemscene in sorted(set(df_img_slide.slide_mscene))]
        except AttributeError:
            print('no explicit microscopy scenes detected.')
        # px scenes
        print('  px scene: rounds')
        try:
            [print(f'{s_slidepxscene}: {sum(df_img_slide.slide_scene==s_slidepxscene)}') for s_slidepxscene in sorted(set(df_img_slide.slide_scene))]
        except AttributeError:
            print('no explicit px scenes detected.')
        # count
        print(f'Round: scenes')
        [print(f'{s_round}: {sum(df_img_slide.loc[:,"round"] == s_round)}') for s_round in sorted(set(df_img_slide.loc[:,'round']))]
        print(f'Number of images = {len(df_img_slide)}\n')


# check_names
def check_markers(
        df_img,
        es_markerdapiblank_standard = config.es_markerdapiblank_standard,
        es_markerpartition_standard = config.es_markerpartition_standard,
    ):
    """
    version: 2021-12-00

    input:
        df_img: dataframe with parse image filenames.
        es_markerdapiblank_standard: set of string of naming convention conform
            dapi, empty, and blank marker names.
        es_markerpartition_standard: set of string of naming convention conform
            marker_partition names.

    output:
        stdout: standard output
        des_marker: dictionary with a set of checked wrong and a set of right
            standard stain names.

    description:
        checks marker names, contained in the naming convention conform filenames,
         against standard list of biomarkers.
    """
    # handle input
    es_marker_standard = es_markerdapiblank_standard.copy()
    for s_marker in es_markerpartition_standard:
        es_marker_standard.add(s_marker.split('_')[0])
    # get used markers
    try:
        es_found = set(df_img.marker)
    except AttributeError:  # if czi original is checked
        es_found = set()
        for s_markers in df_img.markers:
            es_found = es_found.union(set(s_markers.split('.')))

    print(f'\nSlide names: {sorted(set(df_img.slide))}')
    es_wrong = es_found.difference(es_marker_standard)
    es_right = es_found.intersection(es_marker_standard)
    print(f'Wrong stain names: {sorted(es_wrong)}')
    print(f'Right stain names: {sorted(es_right)}')
    print(f'Standard stain names: {sorted(es_marker_standard)}\n')
    des_marker = {'marker_wrong': es_wrong, 'marker_right': es_right}
    return(des_marker)


# qc plot
def visualize_raw_images(
        s_slide,
        s_color = config.d_nconv['s_color_dapi_jinxif'],  #'c1'
        # filesystem
        s_rawdir = config.d_nconv['s_rawdir'],  #'RawImages/',
        s_format_rawdir =  config.d_nconv['s_format_rawdir'],  #'{}{}/', # s_rawdir, s_slide
        s_qcdir = config.d_nconv['s_qcdir'],  #'QC/',
    ):
    '''
    version: 2021-12-00

    input:
        s_slide: slide id from which per mscene qc images should be generated.
        s_color: microscopy channel to check. default is c1 which is DAPI.

        s_rawdir: raw tiff images directory path.
        s_format_rawdir: rawdir subdirectory structure, which is a subdirectory per slide.
        s_qcdir: qc directory path.

    output:
        png plot under s_qcdir

    description:
        generates array raw images to check tissue identity, focus, and so on.
    '''
    print(f'\n run: jinxif.sane.visualize_raw_images for slide: {s_slide} ...')
    df_img_slide = basic.parse_tiff_raw(s_wd=f'{s_rawdir}{s_slide}/')

    for s_slide_mscene in sorted(df_img_slide.slide_mscene.unique()):
        print(f'process slide_mscene: {s_slide_mscene}')

        # generate output path and filename
        s_path = f'{s_qcdir}{s_rawdir.split("/")[-2]}/'
        s_pathfile = f'{s_path}{s_slide_mscene}_{s_color}_raw.png'

        # filter data
        df_img_slidemscene = df_img_slide.loc[
            (df_img_slide.color == s_color) & (df_img_slide.slide_mscene == s_slide_mscene),
            :
        ].sort_values('round_order')
        df_img_slidemscene.index.name = df_img_slide.index.name

        # generate figure
        jfplt.array_img_scatter(
            df_img = df_img_slidemscene,
            s_xlabel = 'marker',
            ls_ylabel = ['markers','color'],
            s_title = 'round',
            s_title_main = 'slide_mscene',
            ti_array = (2, len(df_img_slidemscene)//2 + 1),  # // is floor division
            ti_fig = (22,8),
            cmap = 'gray',
            s_pathfile = s_pathfile,
        )


# spawner function
def visualize_raw_images_spawn(
        es_slide,
        s_color = config.d_nconv['s_color_dapi_jinxif'],  #'c1'
        # processing
        s_type_processing = 'slurm',
        s_slurm_partition = 'exacloud',
        s_slurm_mem = '32G',
        s_slurm_time = '36:00:0',
        s_slurm_account = 'gray_lab',
        # file system
        s_rawdir = config.d_nconv['s_rawdir'],  #'RawImages/',
        s_format_rawdir = config.d_nconv['s_format_rawdir'],  #'{}{}/', # s_rawdir, s_slide
        s_qcdir = config.d_nconv['s_qcdir'],  #'QC/',
    ):
    '''
    version: 2021-12-00

    input:
        es_slide: set of slide ids from which per mscene qc images should be generated.
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

        s_rawdir: raw tiff images directory path.
        s_format_rawdir: rawdir subdirectory  structure, which is a subdirectory per slide.
        s_qcdir: qc directory path.

    output:
        png plot under s_qcdir + s_rawdir.split("/")[-2]

    description:
        generated array raw images to check tissue identity, focus, and so on.
    '''
    # for each slide
    for s_slide in sorted(es_slide):
        # this have to be a python template!
        print(f'visualize_raw_images_spawn: {s_slide} {s_color}')

        # set run commands
        s_pathfile_template = 'template_vizrawimage_slide.py'
        s_pathfile = f'vizrawimage_slide_{s_slide}_{s_color}.py'
        s_srun_cmd = f'python3 {s_pathfile}'
        ls_run_cmd = ['python3', s_pathfile]

        ## any ##
        # load template script code
        with open(f'{s_path_module}src/{s_pathfile_template}') as f:
            s_stream = f.read()

        # edit code generic
        s_stream = s_stream.replace('peek_s_slide', s_slide)
        s_stream = s_stream.replace('peek_s_color', s_color)
        #s_stream = s_stream.replace('peek_dl_crop', str(dl_crop))
        s_stream = s_stream.replace('peek_s_rawdir', s_rawdir)
        s_stream = s_stream.replace('peek_s_format_rawdir', s_format_rawdir)
        s_stream = s_stream.replace('peek_s_qcdir', s_qcdir)

        # write executable script code to file
        time.sleep(4)
        with open(s_pathfile, 'w') as f:
            f.write(s_stream)

        # execute script code
        time.sleep(4)
        if (s_type_processing == 'slurm'):
            # generate sbatch file
            s_pathfile_sbatch = f'vizrawimage_slide_{s_slide}_{s_color}.sbatch'
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
            s_file_stdouterr = f'slurp-vizrawimage_slide_{s_slide}_{s_color}.out'
            o_process = subprocess.run(
                ls_run_cmd,
                stdout=open(s_file_stdouterr, 'w'),
                stderr=subprocess.STDOUT,
            )
