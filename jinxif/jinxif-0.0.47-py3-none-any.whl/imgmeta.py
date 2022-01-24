####
# title: metadata.py
#
# language: Python3.8
# date: 2020-07-00
# license: GPL>=v3
# author: Jenny, bue
#
# description:
#   jinxif pipeline python3 library using python aicsimageio library and xml elementtree to extract image metadata.
#   special thanks to AICSImageIO: https://github.com/AllenCellModeling/aicsimageio
#   special thanks  to Step Howson: https://www.datacamp.com/community/tutorials/python-xml-elementtree
#   special thanks to python xml element tree library: https://docs.python.org/3/library/xml.etree.elementtree.html#module-xml.etree.ElementTree
####


# libraries
from aicsimageio import AICSImage
from jinxif import basic
from jinxif import config
import matplotlib.pyplot as plt
import os
import pandas as pd
from PIL import Image
import re
import seaborn as sns
import sys
import xml.etree.ElementTree as ET

# development
#import importlib
#importlib.reload()


# functions
def fetch_meta_slide_exposuretime(
        df_img,
        s_metadir = config.d_nconv['s_metadir'],  #'MetaImages/'
    ):
    '''
    version: 2021-12-00

    input:
        df_img: dataframe retrieved with basic.parse_czi function.
        s_metadir: exposure time csv file output directory.

    output:
        csv file with exposure time image metadata information.

    description:
        function which calls for every scene per slide,
        for each round, the fetch_meta_image function.
        the gathered exposure times are written to a csv file.
    '''
    # export exposure time
    for s_slide in sorted(set(df_img.slide)):
        print(f'\nfetch_meta_slide_exposuretime: {s_slide} ...')

        # for each slide
        df_img_slide = df_img.loc[df_img.slide == s_slide, :].copy()
        es_column = set(df_img_slide.columns)
        # add new columns that will be populated
        df_img_slide['color'] = None
        df_img_slide['exposure_time_ms'] = None


        # split scene
        if ('slide_mscene' in es_column):
            # for each slide_mscene
            for s_slidemscene in  sorted(set(df_img_slide.slide_mscene)):
                df_img_mscene = df_img_slide.loc[df_img_slide.slide_mscene == s_slidemscene, :]

                # for each image get relevant metadata
                for s_image in df_img_mscene.index:
                    s_pathimage = df_img_mscene.index.name+s_image
                    print(f'process image: {s_pathimage} ...')

                    # load metadata
                    # bue 20211115: in future, maybe o_img.ome_metadata can be used to become czi metadata format independent.
                    # the problem at the moment is that o_img.ome_metadata xlst is not transforming exposure time and scene position
                    # into o_img.ome_metadata.images[*].pixels.planes.{exposure_time, exposure_time_unit} object.
                    o_img = AICSImage(s_pathimage)
                    x_root = o_img.metadata
                    #print(x_root.tag)

                    # get exposure time
                    # bue 20211115: this is czi metadata format dependent code.
                    b_first = True
                    se_color = df_img_slide.loc[s_image,:].copy()
                    for x_channel in x_root.findall('./Metadata/Information/Image/Dimensions/Channels/Channel'):
                        x_exposuretime = x_channel.find('./ExposureTime')
                        #print(x_channel.attrib)
                        #print(x_exposuretime.text)
                        s_color = config.d_nconv['ls_color_order_axio'][int(x_channel.attrib['Id'].replace('Channel:', ''))]  # trafo to filename acceptable channel string
                        f_exposuretime_ms = int(x_exposuretime.text) / 1000000  # trafo ns to ms

                        # update dataframe
                        se_row = se_color.copy()
                        se_row['color'] = s_color
                        se_row['exposure_time_ms'] = f_exposuretime_ms
                        if b_first:
                            df_img_slide.loc[s_image,:] = se_row
                            b_first = False
                        else:
                            df_img_slide = df_img_slide.append(se_row)

                    # write metadata as omexml file
                    s_ofile = config.d_nconv['s_format_omexml'].format(
                        df_img_mscene.loc[s_image,'slide'],
                        df_img_mscene.loc[s_image,'mscene'],
                        df_img_mscene.loc[s_image,'round'],
                        df_img_mscene.loc[s_image,'markers'],
                        'raw'
                    )
                    s_opathfile = df_img_mscene.index.name + s_ofile
                    f = open(s_opathfile, 'w')
                    f.write(o_img.ome_metadata.to_xml())
                    f.close()
                    print(f'write file: {s_opathfile}')


        # original
        else:
            # for each slide image get relevant metadata
            for s_image in df_img_slide.index:
                s_pathimage = df_img_slide.index.name+s_image
                print(f'process image: {s_pathimage} ...')

                # load metadata
                # bue 20211115: in future, maybe o_img.ome_metadata can be used to become czi metadata format independent.
                # the problem at the moment is that o_img.ome_metadata xlst is not transforming exposure time
                # into o_img.ome_metadata.images[*].pixels.planes.{exposure_time, exposure_time_unit} object.
                o_img = AICSImage(s_pathimage)
                x_root = o_img.metadata
                #print(x_root.tag)

                # get exposure time
                # bue 20211115: this is czi metadata format dependent code.
                b_first = True
                se_color = df_img_slide.loc[s_image,:].copy()
                for x_channel in x_root.findall('./Metadata/Information/Image/Dimensions/Channels/Channel'):
                    x_exposuretime = x_channel.find('./ExposureTime')
                    #print(x_channel.attrib)
                    #print(x_exposuretime.text)
                    s_color = config.d_nconv['ls_color_order_axio'][int(x_channel.attrib['Id'].replace('Channel:', ''))] # trafo to filename acceptable channel string
                    f_exposuretime_ms = int(x_exposuretime.text) / 1000000  # trafo ns to ms

                    # update dataframe
                    se_row = se_color.copy()
                    se_row['color'] = s_color
                    se_row['exposure_time_ms'] = f_exposuretime_ms
                    if b_first:
                        df_img_slide.loc[s_image,:] = se_row
                        b_first = False
                    else:
                        df_img_slide = df_img_slide.append(se_row)

                # write metadata as omexml file
                # {}_{}_{}_{}_{}.ome.xml s_slide, s_scene, round, marker, input (raw, registered, subregistered)
                s_ofile = config.d_nconv['s_format_omexml'].format(
                    df_img_slide.loc[s_image,'slide'],
                    'allmscenes',
                    df_img_slide.loc[s_image,'round'],
                    df_img_slide.loc[s_image,'markers'],
                    'raw'
                )
                s_opathfile = df_img_slide.index.name+s_image.replace('.czi','.ome.xml')
                f = open(s_opathfile, 'w')
                f.write(o_img.ome_metadata.to_xml())
                f.close()
                print(f'write file: {s_opathfile}')

        # get marker
        basic._handle_colormarker(
            df_img = df_img_slide,
            s_round = config.d_nconv['s_round_axio'],
            s_quenching = config.d_nconv['s_quenching_axio'],
            s_color_dapi = config.d_nconv['s_color_dapi_axio'],
            ls_color_order = config.d_nconv['ls_color_order_axio'],
            s_sep_marker = config.d_nconv['s_sep_marker_axio'],
            s_sep_markerclone = None,
        )

        # write relevant image metadata per slide dataframe to file
        os.makedirs(s_metadir, exist_ok=True)
        s_opathfile = s_metadir + config.d_nconv['s_format_csv_exposuretime'].format(s_slide)
        df_img_slide.to_csv(s_opathfile)
        print(f'write file: {s_opathfile}')


def fetch_meta_slide_sceneposition(
        s_slide,
        s_czidir_original,
        s_sceneposition_round = 'R1_',
        s_metadir = config.d_nconv['s_metadir'],  #'MetaImages/'
    ):
    '''
    version: 2021-12-00

    input:
        s_slide: slide to be process.
        s_czidir_original: czi directory with at least one non-spit czi files
            straight from the microscope (non-image processed).
        s_sceneposition_round: string pattern to match the file from which scene position information should be extracted.
            the matching pattern does not really have to be the round, it just should be unique to a file.
            good practice but not crucial is to specify the file from the round to which later on is registers to.
        s_metadir: scene position csv file output directory.

    output:
        csv file with scene position image metadata information.

    description:
        function which tries to extract scene position information from any czi original file (not-split)
        that matches the s_sceneposition_round pattern.
        the scene position information is for all rounds the same.
        so, it is enough that one file with the information is read out.
        the gathered scene positions are written to a csv file.
    '''
    # scene position
    b_found = False
    print(f'\nfetch_meta_slide_sceneposition: {s_slide} {s_czidir_original} ...')
    for s_file in sorted(os.listdir(s_czidir_original)):
        s_ipathfile = s_czidir_original + s_file
        # bue 20211115: this is czi metadata format dependent code.
        #if os.path.isfile(s_ipathfile) and (s_file.find(s_sceneposition_round) > -1) and (s_file.endswith('.czi') or s_file.endswith('.tif') or s_file.endswith('.tiff')):
        if os.path.isfile(s_ipathfile) and (s_file.find(s_sceneposition_round) > -1) and s_file.endswith('.czi'):
            print(f'process file: {s_file} ...')

            # get s_slide for naming convention conform filename
            if (s_slide is None):
                o_found = re.search(config.d_nconv['s_regex_czi_original'], s_file)
                s_slide = o_found[config.d_nconv['di_regex_czi_original']['slide']]
                print(f'detected slide id: {s_slide} ...')

            # load metadata
            # bue 20211115: in future, maybe o_img.ome_metadata can be used to become czi metadata format independent.
            # the problem at the moment is that o_img.ome_metadata xlst is not transforming scene position
            # into o_img.ome_metadata.images[*].pixels.planes.{position_y, position_y_unit, position_x, position_x_unit} object.
            o_img = AICSImage(s_ipathfile)
            x_root = o_img.metadata
            #print(x_root.tag)

            # for each scene get scene position
            # bue 20211115: this is czi metadata format dependent code.
            dlr_sceneposition_xy = {}
            for x_scene in x_root.findall('./Metadata/Information/Image/Dimensions/S/Scenes/Scene'):
                x_centerposition = x_scene.find('./CenterPosition')
                #print(x_scene.attrib)
                #print(x_centerposition.text)
                dlr_sceneposition_xy.update({x_scene.attrib['Index'] : [float(s_value) for s_value in x_centerposition.text.split(',')]})

            # check if data found
            if (len(dlr_sceneposition_xy) > 0):
                # pack dataframe
                df_coor = pd.DataFrame(dlr_sceneposition_xy, index=['scene_x','scene_y']).T
                df_coor.index.name = f'{s_slide}_mscene_order'
                print(f'number of microscopy scenes detected: {df_coor.shape[0]}')
                # output
                os.makedirs(s_metadir, exist_ok=True)
                s_opathfile = s_metadir+config.d_nconv['s_format_csv_sceneposition'].format(s_slide)
                df_coor.to_csv(s_opathfile)
                print(f'write file: {s_opathfile}')
                # write metadata as omexml file
                # {}_{}_{}_{}_{}.ome.xml s_slide, s_scene, round, marker, input (raw, registered, subregistered)
                s_ofile = config.d_nconv['s_format_omexml'].format(
                    s_slide,
                    'allmscenes',
                    s_sceneposition_round.replace('_',''),
                    'allmarkers',
                    'raw'
                )
                s_opathfile = s_czidir_original + s_ofile
                f = open(s_opathfile, 'w')
                f.write(o_img.ome_metadata.to_xml())
                f.close()
                print(f'write file: {s_opathfile}')
                # update flag
                b_found = True
                break

    # check if scene position metadata was found.
    if not b_found:
        sys.exit(f'Error @ jinxif.imgmeta.fetch_meta_slide_sceneposition : no original czi file with scene position image metdata and round patter {s_sceneposition_round} found at\n{s_czidir_original}')


def fetch_meta_batch(
        es_slide,
        s_czidir,  #config.d_nconv['s_czidir'],  # 'CziImages/',
        s_format_czidir_original = config.d_nconv['s_format_czidir_original'],  #'{}{}/original/',  # s_czidir, s_slide
        s_format_czidir_splitscene = config.d_nconv['s_format_czidir_splitscene'],  #'{}{}/splitscene/',  # s_czidir, s_slide
        s_sceneposition_round = 'R1_',
        b_sceneposition_original = True,
        b_exposuretime_original = True,
        b_exposuretime_splitscene = False,
        s_metadir = config.d_nconv['s_metadir'],  #'MetaImages/',
    ):
    '''
    version: 2021-12-00

    input:
        es_slide: set of slide labels to fetch exposure time.
        s_czidir: czi main directory for this batch.
        s_format_czidir_original: format string to the directory
            under which the scene position relevant czi files are located.
            it is assumed that the czi files are grouped by slide.
        s_format_czidir_splitscene: format string to the directory
            under which the expression time relevant czi files are located.
            it is assumed that the czi files are grouped by slide.
        s_sceneposition_round: string pattern to match the file from which scene position information should be extracted.
            the specified round should be the same to which later on is registers to.
            the matching pattern does not really have to be the round, it just should be unique for the file.
        b_sceneposition_original: boolean to specify if scene position image metadata should be extracted from the original czi files.
        b_exposuretime_original: boolean to specify if expression time image metadata should be extracted from the original czi file (recessive).
        b_exposuretime_splitscene: boolean to specify if expression time image metadata should be extracted from the split scene czi file (dominate).
        s_metadir: metadata csv file output directory.

    output:
        csv file(s), if b_sceneposition_original, b_exposuretime_original or b_exposuretime_splitscene is set to True.

    description:
        batch wrapper function that calls for each slide the fetch_meta_slide_* functions.
    '''
    print(f'run: jinxif.imgmeta.fetch_meta_batch for slide {sorted(es_slide)} ...')

    # for each slide
    for s_slide  in sorted(es_slide):
        # get path
        s_wd_original = s_format_czidir_original.format(s_czidir, s_slide)
        s_wd_splitmscene = s_format_czidir_splitscene.format(s_czidir, s_slide)

        # fetch exposure time
        if b_exposuretime_splitscene:
            # get path parse czi  file name
            df_img_splitmscene = basic.parse_czi_splitscene(s_wd=s_wd_splitmscene)
            print(df_img_splitmscene.info())
            # slide with one or many scenes
            fetch_meta_slide_exposuretime(
                df_img = df_img_splitmscene,
                s_metadir = s_metadir,
            )
        elif b_exposuretime_original:
            # get path parse czi  file name
            df_img_original = basic.parse_czi_original(s_wd=s_wd_original)
            print(df_img_original.info())
            # slide with one or many scenes
            fetch_meta_slide_exposuretime(
                df_img = df_img_original,
                s_metadir = s_metadir,
            )

        # fetch scene position
        if b_sceneposition_original:
            # slide with one or many scenes
            fetch_meta_slide_sceneposition(
                s_slide = s_slide,
                s_czidir_original = s_wd_original,
                s_sceneposition_round = s_sceneposition_round,
                s_metadir = s_metadir,
            )


def load_exposure_df(
        s_slide,
        s_metadir = config.d_nconv['s_metadir'],  #'MetaImages/',
    ):
    '''
    version: 2021-12-00

    input:
        s_slide: slide to load exposure data from.
        s_metadir: metadata csv file directory.

    output:
        df_load: dataframe with exposure time data.

    description:
        load exposure time csv extracted from image metadata
        with imgmeta.fetch_meta_batch function.
    '''
    print(f'run: jinxif.imgmeta.load_exposure_df for slide {s_slide} ...')

    # load exposure metadata
    df_load = pd.read_csv(
        s_metadir+config.d_nconv['s_format_csv_exposuretime'].format(s_slide),
        index_col = 0,
        dtype = {'round_int': int, 'round_real': float, 'round_order': int},
    )
    # output
    #print('jinxif.imgmeta.load_exposure_df:', df_load.info())
    return(df_load)


def load_position_df(
        s_slide,
        s_metadir = config.d_nconv['s_metadir'],  #'MetaImages/',
    ):
    '''
    version: 2021-12-00

    input:
        s_slide: slide to load exposure data from.
        s_metadir: metadata csv file directory.

    output:
        df_load: dataframe with exposure time data.

    description:
        load scene center position csv extracted form image metadata
        with imgmeta.fetch_meta_batch function.
    '''
    print(f'run: jinxif.imgmeta.load_position_df for slide {s_slide} ...')

    # load scene center position metadata
    df_load = pd.read_csv(
        s_metadir+config.d_nconv['s_format_csv_sceneposition'].format(s_slide),
        index_col = 0,
    )

    # output
    #print('jinxif.imgmeta.load_position_df:', df_load.info())
    return(df_load)


def exposure_matrix(
        s_batch,
        es_slide,
        tr_figsize = (32,20),
        s_metadir = config.d_nconv['s_metadir'],  #'MetaImages/',
    ):
    '''
    version: 2021-12-00


    input:
        s_batch: batch identifier.
        es_slide: slides to load exposure data from.
        tr_figsize: flatlineheatmap plot figure size defined by (w,h) in inch.
            if None, no plot will be generated.
        s_metadir: metadata csv file directory.

    output:
        batch_exposure_time_ms_matrix.png: a flatline and matrix plot to spot exposure time setting errors.
        batch_exposure_time_ms_matrix.csv: numeric matrix to spot exposure time setting errors.

    description:
        load exposure time csv extracted form image metadata
        with imgmeta.fetch_meta_batch function.
    '''
    # handle input
    s_metadir_input = s_metadir
    s_metadir_output = s_metadir

    # load an manipulate data
    b_first = True
    df_all = pd.DataFrame()
    for s_slide in sorted(es_slide):
        df_load =  load_exposure_df(
            s_slide = s_slide,
            s_metadir = s_metadir_input,
        )
        df_load.index = df_load.loc[:,'round'] + '_' + df_load.loc[:,'color'] + '_' + df_load.loc[:,'marker']
        df_load.index.name = 'round_color_marker'
        if b_first:
            es_column = set(df_load.columns)
            if ('slide_mscene' in es_column):
                s_unit = 'slide_mscene'
            else:
                s_unit = 'slide'
            b_first = False
        df_all = df_all.append(df_load.loc[:,[s_unit,'exposure_time_ms']])
    df_all = df_all.pivot(columns=s_unit)
    df_all.columns = df_all.columns.droplevel(level=0)

    # add summary row and column
    df_all['exposure_mean'] = df_all.sum(axis=1) / df_all.notna().sum(axis=1)
    se_sum = df_all.sum()
    se_sum.name = 'exposure_sum'
    df_all = df_all.append(se_sum)

    # write data matrix to file
    df_all.to_csv(s_metadir_output+config.d_nconv['s_format_csv_etmatrix'].format(s_batch))

    if not (tr_figsize is None):
        # generate flatline plot
        fig,ax = plt.subplots(figsize=(tr_figsize[0] - 1, tr_figsize[1] * 1/5))
        se_sum.plot(kind='line', rot=90, grid=True, x_compat=True, title=f'{s_batch}_exposure_time_ms_summary', ax=ax)
        ax.set_xticks(range(se_sum.shape[0]))
        ax.set_xticklabels(list(se_sum.index))
        ax.set_ylabel('exposure time sum [ms]')
        s_file_flatiline = f'{s_batch}_exposure_time_ms_line.png'
        plt.tight_layout()
        fig.savefig(s_metadir_output + s_file_flatiline, facecolor='white')
        plt.close()

        # generate heatmap
        df_all.drop('exposure_sum', axis=0, inplace=True)
        fig,ax = plt.subplots(figsize=(tr_figsize[0], tr_figsize[1] * 4/5))
        sns.heatmap(df_all, annot=False, linewidths=.1, cmap='magma', ax=ax)
        s_file_heat = f'{s_batch}_exposure_time_ms_heat.png'
        plt.tight_layout()
        fig.savefig(s_metadir_output + s_file_heat, facecolor='white')
        plt.close()

        # merge tmp png to final png
        img_flatline = Image.open(s_metadir_output + s_file_flatiline)
        img_heat = Image.open(s_metadir_output + s_file_heat)
        img_result = Image.new('RGB', (img_heat.width, img_flatline.height + img_heat.height), color='white')
        img_result.paste(img_flatline, (0, 0), mask=img_flatline)
        img_result.paste(img_heat, (0, img_flatline.height), mask=img_heat)
        img_result.save(s_metadir_output + config.d_nconv['s_format_png_etmatrix'].format(s_batch), dpi=(720,720))
        os.remove(s_metadir_output + s_file_heat)
        os.remove(s_metadir_output + s_file_flatiline)

