#####
# title: basic.py
#
# language: python3
# author: Jenny, bue
# license: GPLv>=3
# date: 2021-04-00
#
# description:
#     jinxif python3 basic function library that are used in other jinxif libraries.
#####

# library
from jinxif import config
from jinxif import imgmeta # bue: add_exposure
import os
import pandas as pd
import re
import sys

# development
#import importlib
#importlib.reload()

# function

###################
# parse filenames #
###################
def _parse_file(
        s_regex,
        di_regex,
        s_round,
        s_quenching,
        b_fname_ugly = False,
        s_wd = './',
    ):
    '''
    version: 2021-12-00
    internal function

    input:
        s_regex: regex string with regex groups () to parse the filenames.
        di_regex: dictionary to link each regex label (string)
            to the corresponding group (integer) in the s_regex string.
        s_round: naming convention to specify rounds. e.g. R.
        s_quenching: naming convention to specify quenching rounds. e.g. Q.
        b_fname_ugly: boolean to specify if the filename still might follow the old
            chinlab naming convention, which was unable to proper separate slide and mscens
            by a single separator character.
        s_wd: working directory. default is the present working directory.

    output:
        df_img: dataframe with extracted information.
            index are filenames, index.name is the path to the files.

    description:
        generic function to find files in the s_wd specified work directory,
        that matches the regex string s_regex and extract the information,
        defined as regex groups () in the s_regex string and labeled in di_regex.
    '''
    # set column and index
    ls_column = sorted(di_regex.keys())
    ls_index = []
    lls_data = []

    for s_file in sorted(os.listdir(s_wd)):
        # deal with legacy slide_pxscene in file name. there has to be an underscore, the rest does not matter.
        s_input = s_file
        if b_fname_ugly:
            s_input = s_file.replace('-Scene-','_scene')
        # for each file that matches the regex
        #print('basic._parse_file regex:', s_regex, s_input)
        o_found = re.search(s_regex, s_input)
        if not (o_found is None):
            #print(f'basic._parse_file: extract from {s_file} {o_found.groups()} ...')
            # update index
            ls_index.append(s_file)
            # extract information
            ls_row = []
            for s_column in ls_column:
                if s_column in {'slide','scene','marker','markers'}:
                    s_value = o_found[di_regex[s_column]].replace('_','-')
                else:
                    s_value = o_found[di_regex[s_column]]
                ls_row.append(s_value)
            # update data block
            lls_data.append(ls_row)

    # generate dataframe
    df_img = pd.DataFrame(lls_data, index=ls_index, columns=ls_column)

    # handle slide mscene and pxscene
    if ('slide' in ls_column) and ('mscene' in ls_column):
        df_img['slide_mscene'] = df_img.slide + '_' + df_img.mscene
    if ('slide' in ls_column) and ('scene' in ls_column):
        df_img['slide_scene'] = df_img.slide + '_' + df_img.scene

    # handle round
    # bue 20210614: why are all of those needed? round_int, round_ord, and round_num
    # bue 20210629: int (int) real (ord) order (num) would be more precise!
    df_img['round_int'] = [int(re.sub('[^0-9-]','', re.sub(s_round,'', s_item))) for s_item in df_img.loc[:,'round']]
    if (s_quenching  is None):
        df_img['round_real'] = [float(i_item) for i_item in df_img.loc[:,'round_int']] # round_ord
    else:
        df_img['round_real'] = [float(re.sub('[^0-9.-]','', re.sub(s_quenching,'.5', re.sub(s_round,'', s_item)))) for s_item in df_img.loc[:,'round']] # round_ord
    df_img['round_order'] = None
    i_round_min = df_img['round_int'].min()
    for i_order, r_round in enumerate(sorted(df_img.round_real.unique())):
        df_img.loc[df_img.round_real == r_round, 'round_order'] = i_round_min + i_order  # round_num

    # working directory information
    df_img.index.name = s_wd

    # output
    #print('basic._parse_file output:', df_img.info())
    return(df_img)


def _handle_colormarker(
        df_img,
        s_round,
        s_quenching,
        s_color_dapi,
        ls_color_order,
        s_sep_marker = None,  # jinxif, axio
        s_sep_markerclone = None,  # milteny
    ):
    '''
    version: 2021-12-00

    input:
        df_img: dataframe with parsed filenames.
        s_round: naming convention to specify rounds. e.g. R.
        s_quenching: naming convention to specify quenching rounds. e.g. Q.
        s_color_dapi: naming convention for dapi channel identifier. e.g. c1
        ls_color_order: ordered list of channel identifiers. e.g. ['c1','c2', ...]

    output:
        df_img: updated dataframe

    description:
        this function will extract the single channel tiff file related marker
        from the already parsed color, round, and markers information.
    '''
    # handle const
    ls_color = ls_color_order.copy()
    ls_color.pop(ls_color.index(s_color_dapi))

    # handle input
    es_column = set(df_img.columns)
    #print('basic._handle_colormarker df_img.columns:', sorted(es_column))

    # handle marker
    b_markers = False
    b_markerclone = False
    # codex
    if 'marker' in es_column:
        df_img['markers'] = None
    # axio, jinxif
    elif 'markers' in es_column:
        b_markers = True
        df_img['marker'] = None
    # miltenyi
    elif 'marker_clone' in es_column:
        b_markerclone = True
        df_img['markers'] = None
        df_img['marker'] = None
        df_img['clone'] = None

    # parse file name for biomarker
    s_index_name = df_img.index.name
    df_img.reset_index(inplace=True)
    df_img['color_int'] = None
    for s_index in df_img.index:
        #print(f'basic._handle_colormarker process: {s_index}')

        # get s_color and set color_int
        s_color = df_img.loc[s_index,'color']
        df_img.loc[s_index, 'color_int'] = ls_color_order.index(s_color)

        # dapi case
        if (s_color == s_color_dapi):
            r_round = df_img.loc[s_index,'round_real']
            i_round = df_img.loc[s_index,'round_int']
            if (i_round < r_round):
                s_marker = config.d_nconv['s_marker_dapi'] + str(i_round) + s_quenching  # or str(round(r_round,1))
            else:
                s_marker = config.d_nconv['s_marker_dapi'] + str(i_round)
            df_img.loc[s_index,'marker'] = s_marker

        # markers case (axio, jinxif)
        elif b_markers:
            ls_marker = df_img.loc[s_index,'markers'].split(s_sep_marker)
            s_marker = ls_marker[ls_color.index(s_color)]
            df_img.loc[s_index,'marker'] = s_marker

        # marker_clone case (miltenyi)
        elif b_markerclone:
            s_markerclone = df_img.loc[s_index,'marker_clone']
            if (s_markerclone.find(s_sep_markerclone) > -1):
                s_marker = s_markerclone.split(s_sep_markerclone)[0].replace('_','-').replace(config.d_nconv['s_sep_marker_jinxif'], '')
                s_clone  = s_markerclone.split(s_sep_markerclone)[-1]
                df_img.loc[s_index,'clone'] = s_clone
                df_img.loc[s_index,'marker'] = s_marker

        # else case (codex)
        else:
            pass

    # get markers (miltenyi, codex)
    if not b_markers:
        for i_round_order in sorted(df_img.round_order.unique()):
            ls_marker = []
            for i_color_int in sorted(df_img.loc[df_img.round_order == i_round_order, 'color_int'].unique()):
                s_marker = list(df_img.loc[(df_img.round_order == i_round_order) & (df_img.color_int == i_color_int), 'marker'])[0]
                if (s_marker is None):
                    ls_marker.append('None')
                elif not s_marker.startswith(config.d_nconv['s_marker_dapi']):
                    ls_marker.append(s_marker)
            s_markers = config.d_nconv['s_sep_marker_jinxif'].join(ls_marker)
            df_img.loc[df_img.round_order == i_round_order, 'markers'] = s_markers

    # output
    df_img.set_index(s_index_name, inplace=True)
    #print('basic._handle_colormarker output:', df_img.info())
    return(df_img)


def parse_czi_original(s_wd='./'):
    '''
    version: 2021-12-00

    input:
        s_wd: working directory.

    output:
        df_img: dataframe with parsed filenames.

    description:
        wrapper function to parse original czi images.
    '''
    df_img = _parse_file(
        s_regex = config.d_nconv['s_regex_czi_original'],
        di_regex = config.d_nconv['di_regex_czi_original'],
        s_round = config.d_nconv['s_round_axio'],
        s_quenching = config.d_nconv['s_quenching_axio'],
        s_wd = s_wd,
    )
    return(df_img)


#def parse_czi_stitched(s_wd = './'):
#    '''
#    version: 2021-12-00
#
#    input:
#        s_wd: working directory.
#
#    output:
#        df_img: dataframe with parsed filenames.
#
#    description:
#        wrapper function to parse stitched czi images.
#    '''
#    df_img = _parse_file(
#        s_regex = config.d_nconv['s_regex_czi_stitched'],
#        di_regex = config.d_nconv['di_regex_czi_stitched'],
#        s_round = config.d_nconv['s_round_axio'],
#        s_quenching = config.d_nconv['s_quenching_axio'],
#        s_wd = s_wd,
#    )
#    return(df_img)


def parse_czi_splitscene(s_wd='./'):
    '''
    version: 2021-12-00

    input:
        s_wd: working directory.

    output:
        df_img: dataframe with parsed filenames.

    description:
        wrapper function to parse splitscenes czi image.
    '''
    df_img = _parse_file(
        s_regex = config.d_nconv['s_regex_czi_splitscene'],
        di_regex = config.d_nconv['di_regex_czi_splitscene'],
        s_round = config.d_nconv['s_round_axio'],
        s_quenching = config.d_nconv['s_quenching_axio'],
        s_wd = s_wd,
    )
    return(df_img)


def parse_tiff_mics(s_wd='./'):
    '''
    version: 2021-12-00

    input:
        s_wd: working directory.

    output:
        df_img: dataframe with parsed filenames.

    description:
        wrapper function to parse Miltenyi PreprocessedData/02_Processed/*_processed_combined ome.tiff images.
    '''
    df_img = _parse_file(
        s_regex = config.d_nconv['s_regex_tiff_mics'],
        di_regex = config.d_nconv['di_regex_tiff_mics'],
        s_round = config.d_nconv['s_round_mics'],
        s_quenching = config.d_nconv['s_quenching_mics'],  # None
        s_wd = s_wd,
    )
    _handle_colormarker(
        df_img = df_img,
        s_round = config.d_nconv['s_round_mics'],
        s_quenching = config.d_nconv['s_quenching_mics'],  # None
        s_color_dapi = config.d_nconv['s_color_dapi_mics'],
        ls_color_order = config.d_nconv['ls_color_order_mics'],
        s_sep_marker = None,
        s_sep_markerclone = config.d_nconv['s_sep_markerclone_mics'],
    )
    df_img['exposure_time_ms'] = df_img.exposure_time_ms.astype(int)
    return(df_img)


def parse_tiff_codex(s_wd='./'):
    '''
    version: 2021-12-00

    input:
        s_wd: working directory.

    output:
        df_img: dataframe with parsed filenames.

    description:
        wrapper function to parse Miltenyi PreprocessedData/02_Processed/*_processed_combined ome.tiff images.
    '''
    df_img = _parse_file(
        s_regex = config.d_nconv['s_regex_tiff_codex'],
        di_regex = config.d_nconv['di_regex_tiff_codex'],
        s_round = config.d_nconv['s_round_codex'],
        s_quenching = config.d_nconv['s_quenching_codex'],  # None
        s_wd = s_wd,
    )
    _handle_colormarker(
        df_img = df_img,
        s_round = config.d_nconv['s_round_codex'],
        s_quenching = config.d_nconv['s_quenching_codex'],  # None
        s_color_dapi = config.d_nconv['s_color_dapi_codex'],
        ls_color_order = config.d_nconv['ls_color_order_codex'],
        s_sep_marker = None,
        s_sep_markerclone = None,
    )
    #df_img.loc[:,'imagetype'] = 'SubCDX'
    return(df_img)


def parse_tiff_raw(s_wd='./'):
    '''
    version: 2021-08-12

    input:
        s_wd: working directory.

    output:
        df_img: dataframe with parsed filenames

    description:
        wrapper function to parse raw tiff image filenames.
    '''
    df_img = _parse_file(
        s_regex = config.d_nconv['s_regex_tiff_raw'],
        di_regex = config.d_nconv['di_regex_tiff_raw'],
        s_round = config.d_nconv['s_round_jinxif'],
        s_quenching = config.d_nconv['s_quenching_jinxif'],
        s_wd = s_wd,
    )
    _handle_colormarker(
        df_img=df_img,
        s_round = config.d_nconv['s_round_jinxif'],
        s_quenching = config.d_nconv['s_quenching_jinxif'],
        s_color_dapi = config.d_nconv['s_color_dapi_jinxif'],
        ls_color_order = config.d_nconv['ls_color_order_jinxif'],
        s_sep_marker = config.d_nconv['s_sep_marker_jinxif'],
        s_sep_markerclone = None,
    )
    return(df_img)


def parse_tiff_reg(s_wd='./'):
    '''
    version: 2021-12-00

    input:
        s_wd: working directory.

    output:
        df_img: dataframe with parsed filenames

    description:
        wrapper function to parse registered tiff image filenames.
    '''
    df_img = _parse_file(
        s_regex = config.d_nconv['s_regex_tiff_reg'],
        di_regex = config.d_nconv['di_regex_tiff_reg'],
        s_round = config.d_nconv['s_round_jinxif'],
        s_quenching = config.d_nconv['s_quenching_jinxif'],
        b_fname_ugly = True,
        s_wd = s_wd,
    )
    _handle_colormarker(
        df_img = df_img,
        s_round = config.d_nconv['s_round_jinxif'],
        s_quenching = config.d_nconv['s_quenching_jinxif'],
        s_color_dapi = config.d_nconv['s_color_dapi_jinxif'],
        ls_color_order = config.d_nconv['ls_color_order_jinxif'],
        s_sep_marker = config.d_nconv['s_sep_marker_jinxif'],
        s_sep_markerclone = None,
    )
    # check if any  marker echoed.
    se_marker = df_img.marker.value_counts() > 1
    es_echo = set(se_marker.loc[se_marker].index)
    if (len(es_echo) > 0):
        sys.exit(f'Error @ basic.parse_tiff_reg : at {df_img.index.name} a marker occurs more than once. check file names! {es_echo}')
    # output
    return(df_img)


##################
# exposure time  #
##################
def add_exposure(
        df_img_regist,
        ddd_crop,
        ddd_etc = {},
        s_metadir = config.d_nconv['s_metadir'],  #'MetaImages/'
    ):
    '''
    version: 2021-12-00

    input:
        df_img_regist: data frame with parsed registered image file names.
        ddd_crop: the cropping dictionary that links the cropped scenes (sldie_pxscene)
            to the microscopy scenes (slide_mscene).
        ddd_etc: exposure time correction dictionary.
            the format is {'slide_scene': {'marker': {'is': 7,'should_be': 4}},}
            if no exposure time had to be corrected, set parameter to empty dictionary {}.
        s_metadir: folder where the extracted images metadata is stored.

    output:
        df_img_regist: updated dataframe

    description:
        load exposure time csv (generated with imgmeta.fetch_meta_batch),
        and ddd_crop - generated for regist.regist registration,
        and merge this information
        with the parsed filename dataframe df_img_regist.
    '''
    # handle df_img_regsit input
    s_wd = df_img_regist.index.name
    df_img_regist = df_img_regist.reset_index()

    # map slide microscopy scene slide_mscene to each slide_pxscene
    df_img_regist['slide_mscene'] = None
    df_img_regist['mscene'] = None
    for s_dfimg_slide_pxscene in df_img_regist.slide_scene:
        s_slide = s_dfimg_slide_pxscene.split('_')[0]
        for s_mscene in sorted(ddd_crop[s_slide].keys()):
            s_dddcrop_slide_mscene = s_slide + '_' + s_mscene
            for s_pxscene in sorted(ddd_crop[s_slide][s_mscene].keys()):
                s_dddcrop_slide_pxscene = s_slide + '_' + s_pxscene
                if (s_dfimg_slide_pxscene == s_dddcrop_slide_pxscene):
                    df_img_regist.loc[df_img_regist.slide_scene == s_dfimg_slide_pxscene, 'slide_mscene'] = s_dddcrop_slide_mscene
                    df_img_regist.loc[df_img_regist.slide_scene == s_dfimg_slide_pxscene, 'mscene'] = s_mscene
    #print('df_img_regist', df_img_regist.info())

    # load exposure time metadata
    df_exposure = pd.DataFrame()
    for s_slide in df_img_regist.slide.unique():
        df_load = imgmeta.load_exposure_df(
            s_slide = s_slide,
            s_metadir = s_metadir,
        )
        df_exposure = df_exposure.append(df_load)
    #print('df_exposure', df_exposure.info())

    # merge
    es_column = set(df_exposure.columns)
    if ('slide_mscene' in es_column):
        df_img_regist = pd.merge(df_img_regist, df_exposure, on=['slide','mscene','slide_mscene','markers','round','round_int','round_real','round_order','color','marker'])
    else:
        df_img_regist = pd.merge(df_img_regist, df_exposure, on=['slide','markers','round','round_int','round_real','round_order','color','marker'])
    df_img_regist.set_index(s_wd, inplace=True)

    # apply exposure time correction:
    for s_slidepxscene in ddd_etc:
        for s_marker in ddd_etc[s_slidepxscene]:
            f_is_etc = ddd_etc[s_slidepxscene][s_marker]['is']
            se_is_csv = df_img_regist.loc[(df_img_regist.slide_scene == s_slidepxscene) & (df_img_regist.marker == s_marker), 'exposure_time_ms']
            if (len(se_is_csv) > 0):
                f_is_csv = float(se_is_csv)
                if (int(f_is_etc) == int(f_is_csv)):
                    df_img_regist.loc[(df_img_regist.slide_scene == s_slidepxscene) & (df_img_regist.marker == s_marker),'exposure_time_ms'] = ddd_etc[s_slidepxscene][s_marker]['should_be']
                else:
                    sys.exit(f'Error @ jinxif.basic.add_exposure : for s_slidepxscene {s_slidepxscene} s_marker {s_marker} is exposure time in ddd_etc {f_is_etc} and loaded from exposure time csv in s_metadir {f_is_csv} differs.')

    # output
    print('basic.add_exposure output:', df_img_regist.info())
    return(df_img_regist)


#########
# util #
########

def find_last_round(
        df_img,  # can be any parsed filename dataframe, also the thresholdli file!
        es_marker_needed,  # e.g. ('DAPI2','DAPI11_nuc','Ecad')  #
    ):
    '''
    version: 2021-12-00

    input:
        df_img: dataframe with information parsed from the images filenames.
        es_marker_needed: set of markers that have to be in the final dataset.

    output:
        i_last_round: the last round.
        es_marker_drop: markers appearing after the last round.

    description:
        find i_last_round according to an ok marker set.
        this function will preserve adjacent quenching round used e.g. for auto fluorescent subtraction.
    '''
    # find the rounds from all the needed marker
    es_marker = set([s_marker.split('_')[0] for s_marker in es_marker_needed])
    i_last_round = df_img.loc[df_img.marker.isin(es_marker),'round_int'].max() # function will keep the quenching round, if it is adjacent to the last marker round.
    es_marker_drop = set([s_marker + '_' for s_marker in df_img.loc[df_img.round_int > i_last_round, 'marker'].unique()])  # all marker that are higher than the detected round.
    print(f'basic.find_last_round: markers which appear after round {i_last_round}: {sorted(es_marker_drop)}')
    return(i_last_round, es_marker_drop)


def marker_table(
        s_slide_pxscene,
        s_batch = '',
        s_regdir = config.d_nconv['s_regdir'],  #'RegisteredImages/',
        s_format_regdir = config.d_nconv['s_format_regdir'],  #'{}{}/',  # s_regdir, s_slide_pxscene
    ):
    '''
    version: 2021-12-00

    input:
        s_slide_pxscene: slides_pxscene from which the marker_table will be generated.
            note: only one pxscene have to be given, though
            the marker table will be valid for its entire batch.
        s_batch: batch identifier. if empty, an output file will be generated, though
            MarkerTabel.csv filename and dataframe.index.name will miss batch information.
        s_regdir: path to registered images.
        s_format_regdir: registered image subfolder format string.

    output:
        df_marker: dataframe and
        MarkerTable.csv: file under s_regpath

    description:
        generate marker table for a batch.
        one slide_scene is enough to generate the whole table.
        this is just a nice rounds/channels/markers table for display.
    '''
    print(f'run basic.marker_table for batch s_slide_pxscene: {s_batch} {s_slide_pxscene}')

    # parse input file names
    df_img = parse_tiff_reg(s_wd=s_format_regdir.format(s_regdir, s_slide_pxscene))
    #print(df_img.info())

    # generate table
    df_marker = df_img.loc[
        :,
        ['marker','round','color']
    ].pivot(index='round',columns='color', values='marker')
    df_marker.index.name = 'index'
    df_marker.columns.name = ''

    # order table
    df_marker['order'] = df_marker.index
    df_marker.order = [float(re.sub(r'[^\d.]','', s_round.replace(config.d_nconv['s_quenching_jinxif'],'.5'))) for s_round in df_marker.order]
    df_marker.sort_values('order', inplace=True)
    df_marker.drop('order', inplace=True, axis=1)

    # output
    s_ofile = 'MarkerTable.csv'
    if s_batch != '':
        df_marker.index.name = s_batch
        s_ofile = f'{s_batch}_' + s_ofile
    df_marker.to_csv(s_regdir + s_ofile)
    print('df_marker:', df_marker)  # bue 20210913: to display the table.
    print(f'write to file: {s_regdir}{s_ofile}')
    #return(df_marker) # bue 20220103: this is good enough to display the table in jupyter, though not otherwise.

