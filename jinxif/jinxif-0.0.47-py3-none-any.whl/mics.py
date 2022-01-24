############
# title: mics.py
#
# langue: Python3
# date: 2020-04-07
# license: GPL>=v3
# author: Jenny, bue
#
# description:
#     functions to fork miltenyi output into our pipeline.
############


# library
from jinxif import basic
from jinxif import config
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
def _slide_up(a):
    '''
    input:
      a: numpy array

    output:
      a: input numpy array shifted one row up.
        top row get deleted,
        bottom row of zeros is inserted.

    description:
      inspired by np.roll function, though elements that roll
      beyond the last position are not re-introduced at the first.
    '''
    a = np.delete(np.insert(a, a.shape[0], 0, axis=0), 0, axis=0)
    return(a)


def _slide_down(a):
    '''
    input:
      a: numpy array

    output:
      a: input numpy array shifted one row down.
        top row of zeros is inserted.
        bottom row get deleted,

    description:
      inspired by np.roll function, though elements that roll
      beyond the last position are not re-introduced at the first.
    '''
    a = np.delete(np.insert(a, 0, 0, axis=0), -1, axis=0)
    return(a)


def _slide_left(a):
    '''
    input:
      a: numpy array

    output:
      a: input numpy array shifted one column left.
        left most column gets deleted,
        right most a column of zeros is inserted.

    description:
      inspired by np.roll function, though elements that roll
      beyond the last position are not re-introduced at the first.
    '''
    a = np.delete(np.insert(a, a.shape[1], 0, axis=1), 0, axis=1)
    return(a)


def _slide_right(a):
    '''
    input:
      a: numpy array

    output:
      a: input numpy array shifted one column right.
        left most a column of zeros is inserted.
        right most column gets deleted,

    description:
      inspired by np.roll function, though elements that roll
      beyond the last position are not re-introduced at the first.
    '''
    a = np.delete(np.insert(a, 0, 0, axis=1), -1, axis=1)
    return(a)


def _grow(ab_segment, i_step=1):
    '''
    input:
      ai_segment: numpy array representing a cells basin file.
        it is assumed that basin borders are represented by 0 values,
        and basins are represented with any values different from 0.
        ai_segment = skimage.io.imread("cells_basins.tif")

      i_step: integer which specifies how many pixels the basin
        to each direction should grow.
        function can handle shrinking. enter negative steps like -1.

    output:
      ai_grown: numpy array with the grown basins

    description:
      algorithm to grow the basis in a given basin numpy array.
      growing happens counterclockwise, starting at noon.
    '''
    ab_tree = ab_segment.copy()  # initialize output
    # growing
    for i in range(i_step):
        # next grow cycle
        print(f'grow {i+1}[px] ring ...')
        ab_treering = ab_tree.copy()
        for o_slide in [_slide_up, _slide_left, _slide_down, _slide_right]:
            ab_evolve = o_slide(ab_tree)
            ab_treering[ab_evolve] = True
            #print(ab_treering)
        # update output
        ab_tree = ab_treering
    # output
    return(ab_tree)


# copy_processed
def trafo(
        ds_slidescene_rename = {},
        ds_marker_rename = {},
        #i_line_intensity = 32639,
        i_exp_line = 6,  # should be one more as the common doughnut.
        s_micsdir = config.d_nconv['s_micsdir'],  #'MicsImages/'
        s_afsubdir = config.d_nconv['s_afsubdir'],  #'SubtractedRegisteredImages/'
        s_format_afsubdir = config.d_nconv['s_format_afsubdir'],  # {}{}/  s_afsubdir, slide_scene
    ):
    '''
    version: 2021-12-00

    input:
        ds_slidescene_rename: dictionary to rename the form the miltenyi filename automatically derived slide_scene name,
            which is something like R-1-W-A-1_G-1, where R stands for rack, W stands for well, A stands for array, G stands group.
        ds_marker_rename: dictionary to rename original marker names.
        i_exp_line: how many pixels should the stitching lines be extended for later on patching the cell label files?
            the number should be 1 more then the cytosol doughnut wide that will be used for analysis (which is usually 5).
        s_micsdir: standard miltenyi platform output directory.
        s_afsubdir: auto fluorescent subtracted registered image directory
        s_format_afsubdir: s_afsubdir subfolder structure where for each slide_scene the afsubtracted files are stored.

    output:
       for each slide_scene a directory and for each marker afsubtracted tiff files with erased stitching lines under s_afsubdir.

    description:
        copy the highest exposure time images for processing into s_afsubdir.
        thereby erases the stitching lines and additionally saves a mask image for this line for downstream processing.
    '''
    # extend s_micsdir
    s_micsdir_processed = s_micsdir + 'PreprocessedData/02_Processed/'
    for s_folder in  os.listdir(s_micsdir_processed):
        if s_folder.endswith('_processed_combined'):
            s_micsdir_processed_combined = s_micsdir_processed + s_folder + '/'

            # parse mics filenames
            df_img = basic.parse_tiff_mics(s_wd=s_micsdir_processed_combined)
            print(f'@ jinxif.mics.trafo processing: {s_micsdir_processed_combined} ...')

            # add filename_afsub column
            df_img['filename_afsub'] = None

            # rename slidescene
            df_img.slide_scene.replace(ds_slidescene_rename, inplace=True)
            df_img['slide'] = [s_slidepxscene.split('_')[0] for s_slidepxscene in df_img.slide_scene]
            df_img['scene'] = [s_slidepxscene.split('_')[1] for s_slidepxscene in df_img.slide_scene]

            # rename marker and markers
            df_img.marker.replace(ds_marker_rename, inplace=True)
            ls_markers = []
            for s_markers in df_img.markers:
                ls_rename = []
                ls_original = s_markers.split('.')
                for s_original in ls_original:
                    try:
                        s_rename = ds_marker_rename[s_original]
                    except KeyError:
                        s_rename = s_original
                    ls_rename.append(s_rename)
                ls_markers.append('.'.join(ls_rename))
            df_img.markers = ls_markers

            # count overexpressed pixel
            i_16bit_max = 2**16 - 1
            df_img['overex_count'] = None
            for s_file in df_img.index:
                a_img = io.imread(df_img.index.name + s_file)
                i_overex = (a_img >= i_16bit_max).sum()
                df_img.loc[s_file, 'overex_count'] = i_overex
                print(f'counted {i_overex}[px] overexpressed {a_img.max()} >= {i_16bit_max}: {s_file} ...')

            # trafo and move files to afsub
            print(df_img.info())
            es_file_ok = set()
            for s_slide in sorted(df_img.slide.unique()):
                print(f'processing slide: {s_slide} ...')
                df_img_slidepxscene = df_img.loc[df_img.slide == s_slide, :]
                for s_slidepxscene in sorted(df_img.slide_scene.unique()):
                    print(f'processing slide_scene: {s_slidepxscene} ...')
                    df_img_slidepxscene = df_img.loc[df_img.slide_scene == s_slidepxscene, :]
                    for s_round in sorted(df_img.loc[:,'round'].unique()):
                        print(f'processing round: {s_round} ...')
                        df_img_round = df_img_slidepxscene.loc[df_img_slidepxscene.loc[:,'round'] == s_round, :]
                        for s_marker in sorted(df_img_round.loc[df_img_round.marker.notna(),'marker'].unique()):
                            df_img_marker = df_img_round.loc[df_img_round.marker == s_marker, :]
                            print(f'processing marker: {s_marker} ...')
                            for s_file in df_img_marker.sort_values(['overex_count','exposure_time_ms'], ascending=[True,False]).index.tolist():
                                # load image
                                print(f'loadfile image: {s_file} ...')
                                s_ipathfile = df_img.index.name + s_file
                                a_img = io.imread(s_ipathfile)
                                # generate line mask
                                ab_xaxis = (a_img == a_img.mean(axis=0)).all(axis=0)  # get vertical lines
                                ab_yaxis = (a_img.T == a_img.mean(axis=1)).all(axis=0)  # get horizontal lines
                                i_xaxis = ab_xaxis.sum()
                                i_yaxis = ab_yaxis.sum()
                                if (i_xaxis == 0) or (i_yaxis == 0):
                                    sys.exit(f'Error @ jinxif.mics.trafo: no x-axis {i_xaxis} or y-axis {i_yaxis} lines detected in miltenyi PreprocessedData/02_Processed/*_processed_combined images.')
                                print(f'erase detected lines: yaxis {i_yaxis} xaxis {i_xaxis} ...')
                                ab_mask_line = np.zeros(shape=a_img.shape, dtype=bool)
                                ab_mask_line[ab_yaxis, :] = True
                                ab_mask_line[:, ab_xaxis] = True
                                # erase line
                                a_img[ab_mask_line] = a_img.mean()  # bue 20210915: what is best for segmentation? min, 0.05q, median, mean, 0.95q, max?
                                # generate output directory
                                s_slide_scene = df_img_marker.loc[s_file, 'slide_scene']
                                s_opath = s_format_afsubdir.format(s_afsubdir, s_slide_scene)
                                os.makedirs(s_opath, exist_ok=True)
                                # save image
                                i_round_int = df_img_marker.loc[s_file, 'round_int']
                                s_round = config.d_nconv['s_round_jinxif'] + str(i_round_int)
                                s_markers = df_img_marker.loc[s_file, 'markers'] # implement!
                                s_slide = df_img_marker.loc[s_file, 'slide']
                                s_scene = df_img_marker.loc[s_file, 'scene']
                                s_color = config.d_nconv['ls_color_order_jinxif'][df_img_marker.loc[s_file, 'color_int']]  # translate!
                                s_ofile_img = config.d_nconv['s_format_tiff_reg'].format(s_round, s_markers, s_slide, s_scene, s_color, 'SubMicsORG')  # Registered-R{}_{}_{}_{}_{}_Sub{}.tif
                                df_img.loc[s_file, 'filename_afsub'] = s_ofile_img
                                s_opathfile = s_opath + s_ofile_img
                                print(f'save image: {s_opathfile} ..!')
                                io.imsave(s_opath+s_ofile_img, a_img, check_contrast=False)  # plugin='tifffile', check_contrast=False
                                es_file_ok.add(s_file)
                                # only for R0 dapi
                                if s_marker.startswith(config.d_nconv['s_marker_dapi']) and (i_round_int == 0):
                                    # extend linemask
                                    _grow(ab_segment=ab_mask_line, i_step=i_exp_line)
                                    # save line mask as numpy array!
                                    s_ofile_mask = config.d_nconv['s_format_tiff_micsstitchline'].format(s_slide_scene)
                                    s_opathfile = s_opath + s_ofile_mask
                                    np.save(s_opathfile, ab_mask_line)
                                    print(f'save line mask: {s_opathfile} ..!')
                                # break loop for this marker
                                break
                # save df_img_ok
                df_img_ok = df_img.loc[sorted(es_file_ok),:]
                os.makedirs(config.d_nconv['s_metadir'], exist_ok=True)
                s_opathfile = config.d_nconv['s_metadir'] + config.d_nconv['s_format_csv_exposuretime'].format(s_slide)
                df_img_ok.to_csv(s_opathfile)
                print(df_img_ok.info())
                print(f'save metadata: {s_opathfile} ..!')


def trafo_spawn(
        s_batch,
        ds_slidescene_rename = {},
        ds_marker_rename = {},
        i_exp_line = 6,  # should be one more as the common doughnut which is usually exp5.
        # processing
        s_type_processing = 'slurm',
        s_slurm_partition = 'exacloud',
        s_slurm_mem = '32G',
        s_slurm_time = '36:00:0',
        s_slurm_account = 'gray_lab',
        # file system
        s_micsdir = config.d_nconv['s_micsdir'],  #'MicsImages/'
        s_afsubdir = config.d_nconv['s_afsubdir'],  #'SubtractedRegisteredImages/'
        s_format_afsubdir = config.d_nconv['s_format_afsubdir'],  # {}{}/  s_afsubdir, slide_scene
    ):
    '''
    version: 2021-12-00

    input:
        s_batch: string to specify batch label.
        ds_slidescene_rename: dictionary to rename the form the miltenyi filename automatically derived slide_scene name,
            which is something like R-1-W-A-1_G-1, where R stands for rack, W stands for well, A stands for array, G stands group.
        ds_marker_rename: dictionary to rename original marker names.
        i_exp_line: how many pixels should the stitching lines be extended for later on patching the cell label files?
            the number should be 1 more then the cytosol doughnut wide that will be used for analysis (which is usually 5).

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

        s_micsdir: standard miltenyi platform output directory.
        s_afsubdir: auto fluorescent subtracted registered image directory
        s_format_afsubdir: s_afsubdir subfolder structure where for each slide_scene the afsubtracted files are stored.

    output:
       for each slide_scene a directory and for each marker afsubtracted tiff files with erased stitching lines under s_afsubdir.

    description:

    '''
    # for the batch
    print(f'trafo_spawn: {s_batch}')

    # set run commands
    s_pathfile_template = 'template_micstrafo_batch.py'
    s_pathfile = f'micstrafo_batch_{s_batch}.py'
    s_srun_cmd = f'python3 {s_pathfile}'
    ls_run_cmd = ['python3', s_pathfile]

    ## any ##
    # load template script code
    with open(f'{s_path_module}src/{s_pathfile_template}') as f:
        s_stream = f.read()

    # edit code generic
    s_stream = s_stream.replace('peek_s_batch', s_batch)
    s_stream = s_stream.replace('peek_ds_slidescene_rename', str(ds_slidescene_rename))
    s_stream = s_stream.replace('peek_ds_marker_rename', str(ds_marker_rename))
    #s_stream = s_stream.replace('peek_i_line_intensity', str(i_line_intensity))
    s_stream = s_stream.replace('peek_i_exp_line', str(i_exp_line))
    s_stream = s_stream.replace('peek_s_micsdir', s_micsdir)
    s_stream = s_stream.replace('peek_s_afsubdir', s_afsubdir)
    s_stream = s_stream.replace('peek_s_format_afsubdir', s_format_afsubdir)

    # write executable script code to file
    time.sleep(4)
    with open(s_pathfile, 'w') as f:
        f.write(s_stream)

    # execute script
    time.sleep(4)
    if (s_type_processing == 'slurm'):
        # generate sbatch file
        s_pathfile_sbatch = f'micstrafo_batch_{s_batch}.sbatch'
        config.slurmbatch(
            s_pathfile_sbatch = s_pathfile_sbatch,
            s_srun_cmd = s_srun_cmd,
            s_jobname = f'mt{s_batch}',
            s_partition = s_slurm_partition,
            s_gpu = None,
            s_mem = s_slurm_mem,
            s_time = s_slurm_time,
            s_account = s_slurm_account,
        )
        # Jenny this is cool!
        subprocess.run(
            ['sbatch', s_pathfile_sbatch],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
    else:  # non-slurm
        # Jenny this is cool!
        s_file_stdouterr = f'slurp-micstrafo_batch_{s_batch}.out'
        o_process = subprocess.run(
            ls_run_cmd,
            stdout=open(s_file_stdouterr, 'w'),
            stderr=subprocess.STDOUT,
        )


def patch_stitchline(
        s_slide,
        # filesystem
        s_afsubdir = config.d_nconv['s_afsubdir'],  #'SubtractedRegisteredImages/'
        s_format_afsubdir = config.d_nconv['s_format_afsubdir'],  # {}{}/  s_afsubdir, slide_scene
        s_segdir = config.d_nconv['s_segdir'],  #'SubtractedRegisteredImages/',
        s_format_segdir_cellpose = config.d_nconv['s_format_segdir_cellpose'],  #'{}{}_CellposeSegmentation/', # s_segdir, s_slide
    ):
    '''
    version: 2021-12-00

    input:
        s_slide: string to specify slide if for slide to be patched.
        s_afsubdir: auto fluorescent subtracted registration image directory
        s_format_afsubdir: s_afsubdir subfolder structure where for each slide_scene the afsubtracted files are stored.
        s_segdir: segmentation directory.
        s_format_segdir_cellpose: segmentation directory cellpose segmentation format string.

    output:
        tiff: patched cell label files for this s_slide found under the specified s_segdir.

    description:
        remove nucleus and cells that touch the stitching lines plus exp5 px?
        do this for every basin file that matches the s_slide and is found in the specified s_segdir directory.
    '''
    # handle input
    s_path_segdir = s_format_segdir_cellpose.format(s_segdir, s_slide)


    # for each file in segmentation directory
    for s_file_label in os.listdir(s_path_segdir):

        # detect if segmentation label file
        o_match = None
        if (o_match is None):
            o_match = re.search(config.d_nconv['s_regex_tiff_celllabel_nuc'], s_file_label)
            if not (o_match is None):
                s_pxscene = o_match[config.d_nconv['di_regex_tiff_celllabel_nuc']['s_pxscene']]

        if (o_match is None):
            o_match = re.search(config.d_nconv['s_regex_tiff_celllabel_cell'], s_file_label)
            if not (o_match is None):
                s_pxscene = o_match[config.d_nconv['di_regex_tiff_celllabel_cell']['s_pxscene']]

        if (o_match is None):
            o_match = re.search(config.d_nconv['s_regex_tiff_celllabel_nuccellmatched'], s_file_label)
            if not (o_match is None):
                s_pxscene = o_match[config.d_nconv['di_regex_tiff_celllabel_nuccellmatched']['s_pxscene']]

        if (o_match is None):
            o_match = re.search(config.d_nconv['s_regex_tiff_celllabel_nuccellmatchedfeat'], s_file_label)
            if not (o_match is None):
                s_pxscene = o_match[config.d_nconv['di_regex_tiff_celllabel_nuccellmatchedfeat']['s_pxscene']]

        # if segmentation label file
        if not (o_match is None):
            # get slide_pxscene
            s_slide_pxscene = s_slide + '_' + s_pxscene

            # load linemask
            s_path_afsub = s_format_afsubdir.format(s_afsubdir, s_slide_pxscene)
            s_ifile_mask = config.d_nconv['s_format_tiff_micsstitchline'].format(s_slide_pxscene)
            ab_mask_line = np.load(s_path_afsub + s_ifile_mask)

            # load segmentation label file
            s_pathfile_label = s_path_segdir + s_file_label
            ai_label = io.imread(s_pathfile_label)

            # extract labels below the linemask
            print(f'jinxif.mics.patch_stitchline: {s_ifile_mask} {s_pathfile_label}')
            ei_label = set(ai_label[ab_mask_line])
            ei_label.discard(0)

            # erase extracted labels entirely
            print(f'jinxif.mics.patch_stitchline erase label: {sorted(ei_label)}')
            for i_label in sorted(ei_label):
                ai_label[ai_label == i_label] = 0

            # save modified segmentation label file
            io.imsave(s_pathfile_label, ai_label, check_contrast=False)


def patch_spawn(
        es_slide,
        # processing
        s_type_processing = 'slurm',
        s_slurm_partition = 'exacloud',
        s_slurm_mem = '32G',
        s_slurm_time = '36:00:0',
        s_slurm_account = 'gray_lab',
        # file system
        s_afsubdir = config.d_nconv['s_afsubdir'],  #'SubtractedRegisteredImages/'
        s_format_afsubdir = config.d_nconv['s_format_afsubdir'],  # {}{}/  s_afsubdir, slide_scene
        s_segdir = config.d_nconv['s_segdir'],  #'SubtractedRegisteredImages/',
        s_format_segdir_cellpose = config.d_nconv['s_format_segdir_cellpose'],  #'{}{}_CellposeSegmentation/', # s_segdir, s_slide
    ):
    '''
    version: 2021-12-00

    input:
        es_slide: set of slide ids for slides for which the cell label files will be patched.

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

        s_afsubdir: auto fluorescent subtracted registered image directory
        s_format_afsubdir: s_afsubdir subfolder structure where for each slide_scene the afsubtracted files are stored.
        s_segdir: segmentation directory.
        s_format_segdir_cellpose: segmentation directory cellpose segmentation format string.

    output:
        tiff: patched cell label files for this s_slide found under the specified s_segdir.

    description:

    '''
    # for each slide
    for s_slide in sorted(es_slide):
        print(f'patch_spawn: {s_slide}')

        # set run commands
        s_pathfile_template = 'template_micspatch_slide.py'
        s_pathfile = f'micspatch_slide_{s_slide}.py'
        s_srun_cmd = f'python3 {s_pathfile}'
        ls_run_cmd = ['python3', s_pathfile]

        ## any ##
        # load template script code
        with open(f'{s_path_module}src/{s_pathfile_template}') as f:
            s_stream = f.read()

        # edit code generic
        s_stream = s_stream.replace('peek_s_slide', s_slide)
        s_stream = s_stream.replace('peek_s_afsubdir', s_afsubdir)
        s_stream = s_stream.replace('peek_s_format_afsubdir', s_format_afsubdir)
        s_stream = s_stream.replace('peek_s_segdir', s_segdir)
        s_stream = s_stream.replace('peek_s_format_segdir_cellpose', s_format_segdir_cellpose)

        # write executable script code to file
        time.sleep(4)
        with open(s_pathfile, 'w') as f:
            f.write(s_stream)

        # execute script
        time.sleep(4)
        if (s_type_processing == 'slurm'):
            # generate sbatch file
            s_pathfile_sbatch = f'micspatch_slide_{s_slide}.sbatch'
            config.slurmbatch(
                s_pathfile_sbatch = s_pathfile_sbatch,
                s_srun_cmd = s_srun_cmd,
                s_jobname = f'mt{s_slide}',
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
            s_file_stdouterr = f'slurp-micspatch_slide_{s_slide}.out'
            o_process = subprocess.run(
                ls_run_cmd,
                stdout=open(s_file_stdouterr, 'w'),
                stderr=subprocess.STDOUT,
            )

