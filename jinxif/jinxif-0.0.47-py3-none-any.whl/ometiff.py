##
# title: ometiff.py
#
# language: Python3.8
# date: 2021-11-10
# license: GPL>=v3
# author: Jenny, Damir, bue
#
# description:
#   python3 script for generation ometiffs within the jinxif pipeline.
#   the ome tiff xml specification can be found here:
#   + https://www.openmicroscopy.org/Schemas/OME/
#   + https://www.openmicroscopy.org/Schemas/OME/2016-06/ome.xsd
#
# this is a first version.
# in general no information is better then wrong information!
# ometiff will be built with the aicsimageio library.
# ometiff metadata is built with the ome_types library, which since lately is part of the aicsimageio library too.
# please note, at this moment it is not possible to build pytamide based ome.tiffs with the aicsimageio,
# but this will hopefully change in the near future.
#
# for ometiff output by the jinxif pipeline challenges faced to generate ometiff metadata as complete as possible are:
# + a slide can have one or more microscopy split scene (mscene) -  one to many mapping.
# + a mscenes is cropped into one or more pixel scenes (pxscenes) - one to many mapping stored in ddd_crop.
# + a pxscene is <= 20000px * 20000px.
# + scene position is lined to a mscenes.
# + exposure time is linked to a slide or mscene and might have been corrected though the pipeline processing - ddd_etc.
# + one multi channel ometiff will contain any rounds markers from one slide_pxscene.
# because of this complicated relationship,
# this first version will not take sceneposition, exposure time, and instrument information
# (namely microscope, objective, and detector, which can be extracted from the metadata from the original images)
# into account.
#
# some jinxif and ome.tiff jargon:
# a jinxif batch can be handled as ometiff experiment
# a jinxif slide might be a ometiff dataset, though it is not possible to annotate as such, if one not processes all slide_scenes from that dataset.
#
# Damir's in house ometiff scripts batch-cycif2ometiff and cycif2ometiff.py,
# which are built on top of the glenco library and can build pyramid based multichannel ome.tiffs can be found here:
# /home/groups/graylab_share/local/bin
####


#import aicsimageio  # Allen Institute for Cell Science Image io https://github.com/AllenCellModeling/aicsimageio
#from archimage import AICSImage
#from aicsimageio.readers.ome_tiff_reader import OmeTiffReader
from aicsimageio.writers.ome_tiff_writer import OmeTiffWriter
from jinxif import _version
from jinxif import basic
from jinxif import config
from jinxif import imgmeta
import matplotlib as mpl
import numpy as np
import ome_types  # from Talley Lambert, used in aicsimageio https://github.com/tlambert03/ome-types
import os
import re
from skimage import io
import subprocess
import sys
import time

# global var
s_path_module = os.path.abspath(os.path.dirname(__file__))
s_path_module = re.sub(r'jinxif$','jinxif/', s_path_module)

# const
di_abc = {
    'A':1, 'B':2, 'C':3, 'D':4,'E':5,'F':6,'G':7,'H':8,'I':9,'J':10,
    'K':11,'L':12,'M':13,'N':14,'O':15,'P':16,'Q':17,'R':18,'S':19,'T':20,
    'U':21,'V':22,'W':23,'X':24,'Y':25,'Z':26,
}


# dev
#import importlib
#importlib.reload()
'''
ddd_crop = {
        "HER2B-K185": {
            "Scene-01": {"sceneA01": None},
        },
}

ddd_etc = {
    'JE-TMA-66_sceneE01': {'CK14': {'is': 40, 'should_be': 32}},
    'JE-TMA-66_sceneE02': {'CK14': {'is': 40, 'should_be': 64}},
    'JE-TMA-66_sceneE03': {'CK14': {'is': 40, 'should_be': 128}},
}
'''

# function
def ometiff_generator(
        s_slidepxscene,
        es_exclude_round, # {},
        ddd_crop,
        ddd_etc,
        # microscopy
        r_pixel_size_um, # 0.325,
        # experiment
        s_batch_id,  # experiment
        s_lab,  # experimenter_group
        s_email_leader,  # experimenter
        # output image
        b_8bit = False,
        # file system
        s_afsubdir = config.d_nconv['s_regdir'],  #'SubtractedRegisteredImages/' 'RegisteredImages/'
        s_format_afsubdir = config.d_nconv['s_format_regdir'],  #'{}{}/' # s_afsubdir, s_slide_pxscene
        s_metadir = config.d_nconv['s_metadir'],  #'MetaImages/',
        s_ometiffdir = config.d_nconv['s_ometiffdir'],  #'OmeTiffImages/'
    ):
    '''
    version: 2021-12-00

    input:
        s_slidepxscene: string to specify slide_pxscene from which ome.tiff should be generated.
        es_exclude_round: set of stings to specify rounds to be excluded from the multichannel ome.tiff, e.g. {'R0', 'R6Q'}.
        ddd_crop: crop dictionary which maps microscopy scenes (mscene) to pixel scenes (pxscenes).
        ddd_etc: exposure time correction dictionary.

        # microscopy
        r_pixel_size_um: pixel size in micrometer.

        # experiment
        s_batch_id: batch identifier (in ometiff jargon experiment)
        s_lab: lab name (in ometiff jargon experimenter_group)
        s_email_leader: the group leader`s email address (in ometiff jargon experimenter)

        # output image
        b_8bit: should the generated ome.tiff same as the input be a 16[bit] (default),
            or should the output be translate to a 8[bit].
            default setting is false.

        # filesystem
        s_afsubdir: path to where the registered or autofluorescent subtracted registered images are stored.
        s_format_afsubdir: s_afsubdir subfolder structure.
        s_metadir: path to metadata folder.
        s_ometiffdir: path to ometiff folder.

    output:
        ome.tiff file in s_ometiffdir folder.

    description:
        function to generate from the registered or autofluorescent subtracted registered
        single channel tiffs a multichannel ome.tiff.
    '''
    # get experimenter and leader object
    o_experimenter = ome_types.model.Experimenter(
        #id
        #annotation_ref
        email = s_email_leader,
        #first_name
        #institution
        #last_name
        #middle_name
        #user_name
    )
    o_leader = ome_types.model.Leader(
        id = o_experimenter.id
    )


    # get experimenter group object
    o_experimentergroup = ome_types.model.ExperimenterGroup(
        #id
        name = s_lab,
        #annotation_ref
        #description
        experimenter_ref = [ome_types.model.experimenter_ref.ExperimenterRef(id=o_experimenter.id)],
        leader = [ome_types.model.experimenter_ref.ExperimenterRef(id=o_experimenter.id)]
    )

    # get experiment object
    o_experiment = ome_types.model.Experiment(
        #id
        description = s_batch_id,
        experimenter_ref = ome_types.model.experimenter_ref.ExperimenterRef(id=o_experimenter.id),
        #microbeam_manipulations
        type = [ome_types.model.experiment.Type['IMMUNOFLUORESCENCE']],
    )


    # get Instrument object
    # bue 2021-11-16: should be fetched from original files through functions impelmeted in the metaimg.py module.

    # reload paresed filenames
    s_afsubpath = s_format_afsubdir.format(s_afsubdir, s_slidepxscene)
    df_reg = basic.parse_tiff_reg(s_afsubpath)
    print(df_reg.info())
    df_reg_slidepxscene = df_reg.loc[df_reg.slide_scene == s_slidepxscene, :]
    df_reg_slidepxscene = df_reg_slidepxscene.sort_values(['round_order','color_int']) # order rows
    print(df_reg_slidepxscene.info())
    if (df_reg_slidepxscene.shape[0] == 0):
        sys.exit(f'@ jinxif.ometiff.ometiff_generator : at {s_afsubpath} tiff files found to pack as ometiff.')

    # get color rainbow
    o_rainbow = mpl.cm.get_cmap('turbo', df_reg_slidepxscene.shape[0])

    # get slide and mscene
    s_slide, s_pxscene = s_slidepxscene.split('_')
    for s_mscene_loop, d_crop in ddd_crop[s_slide].items():
        for s_pxscene_loop in d_crop.keys():
            if (s_pxscene == s_pxscene_loop):
                s_mscene =  s_mscene_loop
                s_slidemscene = s_slide + '_' + s_mscene
                break

    # load exposure time data
    df_exposure = imgmeta.load_exposure_df(
        s_slide = s_slide,
        s_metadir = s_metadir,
    )

    # load scene position data
    df_position = imgmeta.load_position_df(
        s_slide = s_slide,
        s_metadir = s_metadir,
    )

    # of we go
    o_dtype = None
    ti_shape = None
    i_j = 0
    lai_img_stack = []
    lo_channel = []
    lo_plane = []
    lo_tiffdata = []

    # for each single channel tiff file
    for i_i, s_index in enumerate(df_reg_slidepxscene.index):
        print(f'processing: {s_index}')

        # get round
        s_round = df_reg_slidepxscene.loc[s_index,'round']
        if not (s_round in es_exclude_round):

            # load image and add to stack
            ai_img = io.imread(df_reg.index.name + s_index)
            if b_8bit:
                ai_img_plane = (ai_img / 256).astype(np.uint8)
            else:
                ai_img_plane = ai_img
            lai_img_stack.append(ai_img_plane)

            # check image pixel bit value
            if (o_dtype is None):
                o_dtype = ai_img_plane.dtype
            elif not (o_dtype is ai_img_plane.dtype):
                sys.exit(f'Error @ jinxif.ometiff. : for {s_slidepxscene} detected plane images have not all the same type {s_index} {ai_img_plane.dtype} != {o_dtype}.')

            # check image shape
            if (ti_shape is None):
                ti_shape = ai_img_plane.shape
            elif (ti_shape != ai_img_plane.shape):
                sys.exit(f'Error @ jinxif.ometiff. : for {s_slidepxscene} detected plane images have not all the same shape {s_index} {ai_img_plane.shape} != {ti_shape}.')

            # update channel metadata
            # maybe many of this items culd be taken from original image
            s_marker = df_reg_slidepxscene.loc[s_index,'marker']
            o_channel = ome_types.model.Channel(
                id  = f'Channel:{i_j}',
                name = s_round + '_' + s_marker,
                #acquisition_mode
                #annotation_ref
                color= mpl.colors.rgb2hex(o_rainbow(i_i)),
                #contrast_method
                #detector_settings
                #emission_wavelength
                #emission_wavelength_unit
                #excitation_wavelength
                #excitation_wavelength_unit
                #filter_set_ref
                #fluora
                #illumination_type
                #light_path
                #light_source_settings
                #nd_filter
                #pinhole_size
                #pinhole_size_unit
                #pockel_cell_setting
                #samples_per_pixel
            )
            lo_channel.append(o_channel)

            # get exposure time in ms (maybe correct!)
            try:
                r_exposure = ddd_etc[s_slidepxscene][s_marker]['should_be']
                print('detected corrected expoure time value for: {s_slidepxscene} {s_marker} {r_exposure} [ms]')
            except KeyError:
                r_exposure = df_exposure.loc[
                    (df_exposure.slide_mscene == s_slidemscene) & (df_exposure.loc[:,'round'] == s_round) & (df_exposure.marker == s_marker),
                    'exposure_time_ms'
                ]

            # get scene position in px
            o_match = re.search(r'cene-?([A-Z]+)(\d+)$', s_pxscene)
            if not (o_match is None):
                o_y = int(di_abc[str(o_match.group(1))])
                o_y_unit = ome_types.model.simple_types.UnitsLength.REFERENCEFRAME
                o_x = int(o_match.group(2))
                o_x_unit = ome_types.model.simple_types.UnitsLength.REFERENCEFRAME
            else:
                i_mscene_index =  int(re.sub('\D', '', s_mscene)) - 1
                se_position = df_position.iloc[i_mscene_index,:]
                o_y = se_position.loc['scene_y']
                o_y_unit = ome_types.model.simple_types.UnitsLength.PIXEL
                o_x = se_position.loc['scene_x']
                o_x_unit = ome_types.model.simple_types.UnitsLength.PIXEL

            # update plane metadata inclusive exposure time and scene position
            o_plane = ome_types.model.Plane(
                the_c = i_j,
                the_t = 0,
                the_z = 0,
                #delta_t
                #delta_t_unit
                exposure_time = r_exposure,
                exposure_time_unit = ome_types.model.simple_types.UnitsTime.MILLISECOND,
                #hash_sha1
                position_x = o_x,
                position_x_unit = o_x_unit,
                position_y = o_y,
                position_y_unit = o_y_unit,
                #position_z
                #position_z_unit
            )
            lo_plane.append(o_plane)

            # update tiff metadata
            o_tiffdata = ome_types.model.TiffData(
                first_c = i_j,
                first_t = 0,
                first_z = 0,
                ifd = i_j,
                plane_count = 1,
                #uuid
            )
            lo_tiffdata.append(o_tiffdata)

            # increment j
            i_j += 1

    # translate dtype and filename
    s_input = df_reg_slidepxscene.index.name.split('/')[-1].lower()
    if o_dtype.name in {'uint8'}:
        o_pixeltype = ome_types.model.simple_types.PixelType.UINT8
        i_significant_bits = 8
        s_ofile = config.d_nconv['s_format_ometiff_8bit'].format(s_slide, s_pxscene, 'allrounds', 'allmarkers', s_input)
    elif o_dtype.name in {'uint16'}:
        o_pixeltype = ome_types.model.simple_types.PixelType.UINT16
        i_significant_bits = 16
        s_ofile = config.d_nconv['s_format_ometiff_16bit'].format(s_slide, s_pxscene, 'allrounds', 'allmarkers', s_input)
    else:
        sys.exit(f'Error @ jinxif.ometiff. : strange tiff bit type detected {o_dtype}.\nshould be np.uint8 or np.uint16.')

    # update image metadata
    o_pixels = ome_types.model.pixels.Pixels(
        #id =
        dimension_order = 'XYCZT',
        size_c = len(lai_img_stack),  # extract
        size_t = 1,  # take default
        size_x = ti_shape[1],  # extract
        size_y = ti_shape[0],  # extract
        size_z = 1,  # take default
        type = o_pixeltype, # extract
        #big_endian = boole
        #bin_data
        channels = lo_channel, # have to be defined  # name round_marker name the c,t=0,z=0,
        #interleaved = boole
        #metadata_only = boole
        physical_size_x = r_pixel_size_um,  # extract
        physical_size_x_unit = ome_types.model.simple_types.UnitsLength.MICROMETER,
        physical_size_y = r_pixel_size_um,  #extract
        physical_size_y_unit = ome_types.model.simple_types.UnitsLength.MICROMETER,
        #physical_size_z
        #physical_size_z_unit
        planes = lo_plane, # have to be defined  # exposure time and unit and positionx and positiony
        significant_bits = i_significant_bits, # extract
        tiff_data_blocks = lo_tiffdata,
        #time_increment
        #time_increment_unit
    )

    s_image = f'{s_slide}_{s_mscene}_{s_pxscene}'
    s_ofile = s_image + '.ome.tiff'
    o_image = ome_types.model.Image(
        #id =
        name = s_image,
        pixels = o_pixels,
        #acquisition_date
        #annotation_ref
        #description
        experiment_ref = ome_types.model.experiment_ref.ExperimentRef(id=o_experiment.id),
        experimenter_ref = ome_types.model.experimenter_ref.ExperimenterRef(id=o_experimenter.id),
        experimenter_group_ref = ome_types.model.experimenter_group_ref.ExperimenterGroupRef(id=o_experimentergroup.id),
        #imaging_environment
        #instrument_ref = # maybe from original image
        #microbeam_manipulation_ref
        #objective_settings =   # maybe from original image
        #roi_ref
        #stage_label
    )

    # get ometiff object
    o_ome = ome_types.OME(
        #binary_only
        creator = f'jinxif v{_version.__version__}',
        #datasets
        experimenter_groups = [o_experimentergroup],
        experimenters = [o_experimenter],
        experiments = [o_experiment],
        #folders
        images = [o_image],
        #instruments = [o_imstrument]
        #plates
        #projects
        #rights := copy left!
        #rois
        #screens
        #structured_annotations
        #uuid
    )

    # write ome tiff to file
    os.makedirs(s_ometiffdir, exist_ok=True)
    OmeTiffWriter.save(
        data = np.array(lai_img_stack),
        uri = s_ometiffdir+s_ofile,
        dim_order  = 'CYX',
        ome_xml = o_ome.to_xml(),
    )


def ometiff_spawn(
        es_slide,
        es_slide_pxscene,
        es_exclude_round,
        ddd_crop,  # to map slide_mscene to slide_pxscene
        ddd_etc,  # exposure time correction
        # microscopy
        r_pixel_size_um,  # 0.325
        # experiment
        s_batch_id,  # experiment
        s_lab,  # experimenter_group
        s_email_leader,  # experimenter
        # output image
        b_8bit = False,
        # processing
        s_type_processing = 'slurm',
        s_slurm_partition = 'exacloud',
        s_slurm_mem ='32G',
        s_slurm_time ='36:00:00',
        s_slurm_account ='gray_lab',
        # file system
        s_afsubdir = config.d_nconv['s_regdir'],  #'SubtractedRegisteredImages/' 'RegisteredImages/'
        s_format_afsubdir = config.d_nconv['s_format_regdir'],  #'{}{}/' # s_afsubdir, s_slide_pxscene
        s_metadir = config.d_nconv['s_metadir'],  #'MetaImages/',
        s_ometiffdir = config.d_nconv['s_ometiffdir'],  #'OmeTiffImages/'
    ):
    '''
    version: 2021-12-00

    input:
        es_slide: set of strings to specify which slides should be processed.
        es_slide_pxscene: set of string to specify slide_pxscenes that should be processed.
            if None, all slide_px scenes from the slides specified in es_slide will be generated.
        es_exclude_round: set of stings to specify rounds to be excluded from the multichannel ome.tiff, e.g. {'R0', 'R6Q'}.
        ddd_crop: crop dictionary which maps microscopy scenes (mscene) to pixel scenes (pxscenes).
        ddd_etc: exposure time correction dictionary.

        # microscopy
        r_pixel_size_um: pixel size in micrometer.

        # experiment
        s_batch_id: batch identifier (in ometiff jargon experiment)
        s_lab: lab name (in ometiff jargon experimenter_group)
        s_email_leader: the group leader`s email address (in ometiff jargon experimenter)

        # output image
        b_8bit: should the generated ome.tiffs same as the input be a 16[bit] (default),
            or should the output be translate to a 8[bit].
            default setting is False.

        # processing
        s_type_processing: to specify if registration should be run on the slurm cluster or on a simple slurp machine.
        s_partition: slurm cluster partition to use. options are 'exacloud', 'light'.
        s_mem: slurm cluster memory allocation. format '64G'.
        s_time: slurm cluster time allocation in hour or day format. max '36:00:00' [hour] or '30-0' [day].
        s_account: slurm cluster account to credit time from. 'gray_lab', 'chin_lab', 'heiserlab', 'CEDAR'.

        # filesystem
        s_afsubdir: path to where the registered or autofluorescent subtracted registered images are stored.
        s_format_afsubdir: s_afsubdir subfolder structure.
        s_metadir: path to metadata folder.
        s_ometiffdir: path to ometiff folder.

    output:
        ome.tiff files in s_ometiffdir folder.

    description:
        spawner function for ometiff_generator.
    '''
    # detect slide pxscene
    for s_folder in os.listdir(s_afsubdir):
        print(f'jinxif.ometiff processing: {s_afsubdir}{s_folder}')
        if os.path.isdir(s_afsubdir + s_folder) and ((es_slide is None) or any(s_folder.startswith(s_slide) for s_slide in es_slide)):
            # parse filenames
            s_afsubpath = s_format_afsubdir.format(s_afsubdir, s_folder)
            df_reg = basic.parse_tiff_reg(s_afsubpath)
            print('off we go ...', df_reg.info())
            for s_slidepxscene in sorted(df_reg.slide_scene.unique()):
                print('check', s_slidepxscene)
                if (es_slide_pxscene is None) or (s_slidepxscene in es_slide_pxscene):
                    print('generating executable for:', s_afsubpath)
                    s_input = s_afsubdir.split('/')[-2].lower()

                    # load template script
                    s_pathfile_template = f'{s_path_module}src/template_ometiff_slidepxscene.py'
                    with open(s_pathfile_template) as f:
                        s_stream = f.read()

                    # edit template code
                    # parameter
                    s_stream = s_stream.replace('peek_s_slidepxscene', s_slidepxscene)
                    s_stream = s_stream.replace('peek_es_exclude_round', str(es_exclude_round))
                    s_stream = s_stream.replace('peek_ddd_crop', str(ddd_crop))
                    s_stream = s_stream.replace('peek_ddd_etc', str(ddd_etc))
                    # microscope
                    s_stream = s_stream.replace('peek_r_pixel_size_um', str(r_pixel_size_um))
                    # experiment
                    s_stream = s_stream.replace('peek_s_batch_id', s_batch_id)
                    s_stream = s_stream.replace('peek_s_lab', s_lab)
                    s_stream = s_stream.replace('peek_s_email_leader', s_email_leader)
                    # output image
                    s_stream = s_stream.replace('peek_b_8bit', str(b_8bit))
                    # files system
                    s_stream = s_stream.replace('peek_s_afsubdir', s_afsubdir)
                    s_stream = s_stream.replace('peek_s_format_afsubdir', s_format_afsubdir)
                    s_stream = s_stream.replace('peek_s_metadir', s_metadir)
                    s_stream = s_stream.replace('peek_s_ometiffdir', s_ometiffdir)

                    # write executable code to file
                    time.sleep(4)
                    s_pathfile_executable = f'ometiff_{s_slidepxscene}_{s_input}.py'
                    with open(s_pathfile_executable, 'w') as f:
                        f.write(s_stream)

                    # execute segmentation script
                    time.sleep(4)
                    if (s_type_processing == 'slurm'):
                        # generate sbatch file
                        s_pathfile_sbatch = f'ometiff_{s_slidepxscene}_{s_input}.sbatch'
                        config.slurmbatch(
                            s_pathfile_sbatch=s_pathfile_sbatch,
                            s_srun_cmd=f'python3 {s_pathfile_executable}',
                            s_jobname=f'o{s_slidepxscene}',
                            s_partition=s_slurm_partition,
                            s_gpu=False,
                            s_mem=s_slurm_mem,
                            s_time=s_slurm_time,
                            s_account=s_slurm_account,
                        )
                        # Jenny this is cool! Popen rocks.
                        subprocess.run(
                            ['sbatch', s_pathfile_sbatch],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                        )
                    else:  # non-slurm
                        # Jenny this is cool! Popen rocks.
                        s_file_stdouterr = f'slurp-ometiff_{s_slidepxscene}_{s_input}.out'
                        subprocess.run(
                            ['python3', s_pathfile_executable],
                            stdout=open(s_file_stdouterr, 'w'),
                            stderr=subprocess.STDOUT,
                        )
