############
# title: codex.py
#
# language: Python3
# date: 2021-09-16
# license: GPL>=v3
# author: Jenny, bue
#
# description:
#     functions to fork codex output into our pipeline.
############


# library
from jinxif import basic
from jinxif import config
import json
import os
import pandas as pd
import shutil

# development
#import importlib
#importlib.reload()


# function
def trafo(
        es_sample,
        b_symlink = True,
        # file system
        s_codexdir = config.d_nconv['s_codexdir'],  #'CodexImages/'
        s_afsubdir = config.d_nconv['s_afsubdir'],  #'SubtractedRegisteredImages/'
        s_format_afsubdir = config.d_nconv['s_format_afsubdir'],  # {}{}/  s_afsubdir, slide_scene
    ):
    '''
    version: 2021-12-00

    input:
        es_sample: set of sample ids aka folders under s_codexdir,
            which should be transformed to be jinxif s_afsubdir compatible.
        b_symlink: if false then the original codex files are copied and renamed.
            if true, then the original codex tiff files are just symbolically linked 
            to a naming convention conform filename, not copied. this is faster and
            does not consume any additional disk space. default setting is true.

        # filesystem
        s_codexdir: standard codex platform output directory, which has to have the 
            following subfolder structure: sample/processed_YYYY-MM-DD/stitched/regNNN/
        s_afsubdir: auto fluorescent subtracted registered image directory.
        s_format_afsubdir: s_afsubdir subfolder structure where for each 
            slide_scene the af subtracted files are stored.

    output:
        for each slide_scene a directory and tiff files
        (either real or just symbolically linked) under s_afsubdir.

    description:
        function symbolic links or copies the codex processed
        stitched tiff images for jinxif processing into s_afsubdir.
        the generated symbolic link or file names will be totally jinxif 
        naming convention compatible.
    '''
    for s_sample in sorted(es_sample):
        print(f'codex.trafo: processing data from sample {s_sample} ...')
        s_path_root = s_codexdir + s_sample + '/'
        for s_dir_processed in os.listdir(s_path_root):
            if os.path.isdir(s_path_root + s_dir_processed) and s_dir_processed.startswith('processed_'):
                # slide handle input
                s_slide = f"{s_sample.replace('_','-')}-{s_dir_processed.split('_')[-1].replace('-','')}"
                s_path_processed = s_path_root + s_dir_processed + '/'
                s_path_stitched = s_path_processed + '/stitched/'
                # extract exposure time
                b_exposuretime = False
                try:
                    d_experiment = json.load(open(f'{s_path_root}experiment.json'))
                    df_exposuretime = pd.DataFrame(d_experiment['exposureTimes']['exposureTimesArray'])
                    df_exposuretime = df_exposuretime.iloc[1:,:]
                    #df_exposuretime.columns = ['round'] + config.d_nconv['ls_color_order_codex'][0:(df_exposuretime.shape[1] - 1)]
                    #df_exposuretime.loc[:,'round']  = [config.d_nconv['s_round_codex'] + str(i_round).zfill(3)  for i_round in df_exposuretime.loc[:,'round'] ]
                    df_exposuretime.columns = ['round'] + config.d_nconv['ls_color_order_jinxif'][0:(df_exposuretime.shape[1] - 1)]
                    df_exposuretime.loc[:,'round']  = [config.d_nconv['s_round_jinxif'] + str(i_round).zfill(3)  for i_round in df_exposuretime.loc[:,'round'] ]
                    df_exposuretime = df_exposuretime.set_index('round').T.unstack().reset_index()
                    df_exposuretime.columns = ['round', 'color', 'exposure_time_ms']
                    df_exposuretime.index.name = 'index'
                    b_exposuretime = True
                    print('codex.trafo: detected exposure time data:', df_exposuretime.info())
                except FileNotFoundError:
                    pass
                # slide_scene
                for s_dir_reg in os.listdir(s_path_stitched):
                    if os.path.isdir(s_path_stitched + s_dir_reg) and s_dir_reg.startswith('reg'):
                        print(f'codex.trafo detected slide_scene: {s_slide} {s_dir_reg}')
                        s_path_reg = s_path_stitched + s_dir_reg + '/'
                        df_codex = basic.parse_tiff_codex(s_path_reg)
                        # update with new columns
                        df_codex['slide'] = s_slide
                        df_codex['slide_scene'] = df_codex['slide'] + '_' + df_codex['scene']
                        df_codex['imagetype'] = 'SubCodexORG'
                        # translate color string
                        df_codex['color'] = [config.d_nconv['ls_color_order_jinxif'][config.d_nconv['ls_color_order_codex'].index(s_color)]for s_color in df_codex.color]
                        # translate round string
                        df_codex['round'] = [s_round.replace(config.d_nconv['s_round_codex'], config.d_nconv['s_round_jinxif']) for s_round in df_codex.loc[:,'round']]

                        # for each file
                        df_codex['filename_afsub'] = None
                        for s_file in df_codex.index:

                            # get src
                            s_src_pathfile = df_codex.index.name + s_file

                            # get dst
                            s_dst_path = s_format_afsubdir.format(s_afsubdir, df_codex.loc[s_file, 'slide_scene'])
                            os.makedirs(s_dst_path, exist_ok=True)
                            ds_dst = {}
                            for s_dst, i_dst in config.d_nconv['di_regex_tiff_reg'].items():
                                ds_dst.update({i_dst: df_codex.loc[s_file, s_dst]})
                            s_dst_file = config.d_nconv['s_format_tiff_reg'].format(ds_dst[1], ds_dst[2], ds_dst[3], ds_dst[4], ds_dst[5], ds_dst[6], ds_dst[7])
                            s_dst_pathfile = s_dst_path + s_dst_file

                            # make symbolic links or copy
                            if (b_symlink):
                                print(f'codex.trafo symlink:\n{s_src_pathfile}\n{s_dst_pathfile}')
                                if os.path.islink(s_dst_pathfile):
                                   os.remove(s_dst_pathfile)
                                s_dst_relative = '../' * (s_dst_pathfile.count('/') - 1)
                                s_src_pathfile_symlink = s_dst_relative + s_src_pathfile
                                os.symlink(s_src_pathfile_symlink, s_dst_pathfile)
                            else:
                                print(f'codex.trafo copy:\n{s_src_pathfile}\n{s_dst_pathfile}')
                                shutil.copyfile(s_src_pathfile, s_dst_pathfile)

                            # update df_codex
                            df_codex.loc[s_file, 'filename_afsub'] = s_dst_file
                        #break

                        # save parsed filename information, add exposure time if available.
                        s_pathfile_metacodex = config.d_nconv['s_metadir'] + f'{s_slide}_parse.csv'
                        os.makedirs(config.d_nconv['s_metadir'], exist_ok=True)
                        if b_exposuretime:
                            df_codex.reset_index(inplace=True)
                            df_codex = pd.merge(df_codex, df_exposuretime, on=['round','color'])
                            df_codex.index = df_codex.iloc[:,0]
                            df_codex = df_codex.iloc[:,1:]
                            s_pathfile_etmetacodex = config.d_nconv['s_metadir'] + config.d_nconv['s_format_csv_exposuretime'].format(s_slide)
                            df_codex.to_csv(s_pathfile_etmetacodex)
                            if os.path.exists(s_pathfile_metacodex):
                                os.remove(s_pathfile_metacodex)
                            print(f'codex.trafo save metadata: {s_pathfile_etmetacodex} ..!')
                        else:
                            df_codex.to_csv(s_pathfile_metacodex)
                            print(f'codex.trafo save metadata: {s_pathfile_metacodex} ..!')
                        print(df_codex.info())

                #break
        #break

