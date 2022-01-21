#!/usr/bin/env python

import os
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
import scipy.stats as stats
from datetime import datetime
from glob import glob

# output location
outdir = os.path.join(os.getcwd(), 'data')

# data location (access to server)
studydir = '/Volumes/prestonlab/PrestonLab/Experiments/Experiments/moviestim/'


def age_variables(age):
    # group variables
    if age > 17.:
        gvar1 = 'adult'
        gvar2 = 'adult'
        gvar3 = 'adult'
    else:
        gvar1 = 'child'
        if age < 8.:
            gvar2 = '5-7yo'
        elif 7. < age <= 12.:
            gvar2 = '8-12yo'
        else:
            gvar2 = 'adol'

        # 7-9 and 10-12
        if 7. <= age <= 9.:
            gvar3 = '7-9yo'
        elif age == 5. or age == 6.:
            gvar3 = '5-6yo'
        else:
            gvar3 = '10-12yo'

    return gvar1, gvar2, gvar3


def check_file(filename):
    potential_filenames = glob(filename)
    n_files = len(potential_filenames)
    if n_files == 0:
        return n_files, '0'

    elif n_files > 1:
        final_filename = potential_filenames[1]

    else:
        final_filename = potential_filenames[0]

    return n_files, final_filename


def find_parse_file(sub, movie, v=0):
    """Gets the full file path and loads data for subject and movie"""
    datadir = os.path.join(studydir, 'data_update')
    subdir = os.path.join(datadir, f'pc_{sub}')

    # get file based on naming convention from study phase
    wildfile = os.path.join(subdir, f'par_pc_{sub}_{movie}_full_?_?.txt')
    n_files, fullfile = check_file(wildfile)

    return n_files, fullfile


def load_parse_file(sub, movie, v=0):
    """Loads data for subject and movie"""
    # find file 
    n_files, fullfile = find_parse_file(sub, movie, v=v)

    if fullfile == '0':
        # not run
        file_loc = f'missing, {sub}, {movie}'
        df = pd.DataFrame({'secs': [0], 'parses': [0], 'n parses': [-1], 'subject': sub, 'movie': movie, 'order': 9})

    elif os.path.getsize(fullfile) == 0:
        # ran no parses
        file_loc = f'empty, {sub}, {movie}'
        df = pd.DataFrame({'secs': [0], 'parses': [0], 'n parses': [0], 'subject': sub, 'movie': movie})
        df['order'] = os.path.basename(fullfile).split('.')[0].split('_')[-2]

    else:
        # ran with parses
        file_loc = f'found, {sub}, {movie}'
        tmp_df = pd.read_csv(fullfile, sep='\t', header=None, index_col=False)

        ## CHECK FOR PARSES LESS THAN 1 SECOND APART ##
        parses = tmp_df[0].values
        preparses = parses.copy();
        Npreparses = len(preparses)
        changes = np.where(np.diff(parses) < 1.)[0] + 1
        if changes.size == 0:
            pass
        else:
            parses = np.delete(parses, changes)

        # after removal of duplicate parses
        Npostparses = len(parses)
        duplicate_diff = Npreparses - Npostparses
        parse_change = f"removed {duplicate_diff} parses"
        maxparses = len(parses)
        n_parses = np.arange(0, maxparses) + 1
        df = pd.DataFrame({'secs': parses, 'parses': n_parses, 'n parses': np.repeat(maxparses, len(n_parses))})
        ## CHECK FOR PARSES LESS THAN 1 SECOND APART ##

        # other variables
        df['subject'] = sub
        df['movie'] = movie
        df['order'] = os.path.basename(fullfile).split('.')[0].split('_')[-2]

        # meta information for file tracking purposes
        file_loc = f'{file_loc}, {parse_change}'

    meta_info = f'{fullfile}, {file_loc}'
    if v: print(meta_info)

    return fullfile, df


def get_parse_data(subs, movies, save=0, v=0):
    """ 
    Usage: get_parse_data( subs, movies, save=0, v=0)
        - subs = dictionary of subject numbers and ages {444:18, 888:19, ...}
        - movies = list of movies

    Return: pandas dataframe of all movies and subjects by parse (long format)
    
    """
    # sort through subjects
    data_list = list()
    file_list = list()
    for sub, age in sorted(subs.items()):
        for mi, movie in enumerate(movies):
            fullfile, df = load_parse_file(sub, movie, v=v)
            file_list.append([sub, movie, fullfile])

            # group variables
            df['age'] = age
            __, __, df['group'] = age_variables(age)
            data_list.append(df)

    data = pd.concat(data_list)
    files = pd.DataFrame(file_list, columns=['subject', 'movie', 'file'])

    # file outputs
    if save:
        dt = datetime.now().strftime("%m-%d-%Y")
        data.to_csv(os.path.join(outdir, 'raw', f'aggregated_parse_data_{dt}.csv'), index=False)
        files.to_csv(os.path.join(outdir, 'raw', f'found_parse_files_{dt}.csv'), index=False)

    return data


def basic_data_plot(data, save=0):
    """Plots high level information about subjects, movies, events"""
    # plotting, colors and groupings
    order = ['5-6yo', '7-9yo', '10-12yo', 'adult']
    plt.rcParams['axes.labelsize'] = 14
    plt.rcParams['axes.titlesize'] = 24

    # mix and max for plots
    cmap4_hex = ["#579d42", "#00a9b7", "#005f86", '#bf5700']
    cmap5_hex = ["#a6cd57", "#ffd600", "#f8971f", "#9cadb7", "#d6d2c4"]
    cmap4 = sns.color_palette(cmap4_hex)
    cmap5 = sns.color_palette(cmap5_hex)

    # file outputs
    dt = datetime.now().strftime("%m-%d-%Y")

    # full dataset
    all_data = data.drop_duplicates(subset=['subject', 'movie'], keep='last').copy()
    all_data['count'] = all_data['age'].values

    # plot full dataset  
    fig, ax = plt.subplots(1, 2, figsize=(18, 8))
    sns.countplot(ax=ax[0], x='group', hue='movie', order=order, data=all_data, palette=cmap5)
    ax[0].set(xlabel=None, ylabel='count (subject)', title='full parse sample breakdown (movie/subject)')

    sns.boxplot(ax=ax[1], x='group', y='n parses', hue='movie', order=order, data=all_data, palette=cmap5)
    ax[1].set(xlabel=None, ylabel='parses (subject/movie)', title='total parses (movie/subject)')

    plt.tight_layout()
    fig.savefig(os.path.join(outdir, f'plots/subject_breakdown_parse_full_{dt}.png'), facecolor='w', transparent=False)

    # take out subject/movies that didn't parse at all and plot
    all_data = all_data[all_data['n parses'] > 0]
    fig, ax = plt.subplots(1, 2, figsize=(18, 8))
    sns.countplot(ax=ax[0], x='group', hue='movie', order=order, data=all_data, palette=cmap5)
    ax[0].set(xlabel=None, ylabel='count (subject)', title='(at least 1) parse sample breakdown (movie/subject)')

    sns.boxplot(ax=ax[1], x='group', y='n parses', hue='movie', order=order, data=all_data, palette=cmap5)
    ax[1].set(xlabel=None, ylabel='parses (subject/movie)', title='total parses (movie/subject)')

    plt.tight_layout()
    fig.savefig(os.path.join(outdir, f'plots/subject_breakdown_parse_trim_{dt}.png'), facecolor='w', transparent=False)

    # remove very high parsers in addition to those that did not parse at all
    zs = stats.zscore(all_data['n parses'].values)
    all_data = all_data[~(zs > 2.5)]
    fig, ax = plt.subplots(1, 2, figsize=(18, 8))
    sns.countplot(ax=ax[0], x='group', hue='movie', order=order, data=all_data, palette=cmap5)
    ax[0].set(xlabel=None, ylabel='count (subject)', title='(full trim) parse sample breakdown (movie/subject)')

    sns.boxplot(ax=ax[1], x='group', y='n parses', hue='movie', order=order, data=all_data, palette=cmap5)
    ax[1].set(xlabel=None, ylabel='parses (subject/movie)', title='total parses (movie/subject)')

    plt.tight_layout()
    fig.savefig(os.path.join(outdir, f'plots/subject_breakdown_parse_full-trim_{dt}.png'), facecolor='w',
                transparent=False)


def main():
    # meta
    v = 1
    save = 1

    # subjects, with age
    subs = {'474': 8, '451': 9, '408': 9, '541': 10, '481': 8, '454': 10,
            '403': 10, '406': 8, '527': 7, '473': 5, '485': 9, '510': 6, '452': 7,
            '499': 9, '421': 9, '401': 6, '512': 9, '432': 20, '470': 10, '475': 20,
            '477': 19, '511': 10, '462': 10, '441': 7, '518': 9, '540': 19, '471': 18,
            '487': 18, '459': 18, '503': 18, '492': 18, '443': 18, '538': 19, '509': 19,
            '447': 19, '426': 19, '528': 18, '526': 18, '531': 18, '412': 19, '429': 19,
            '411': 20, '537': 19, '457': 21, '488': 18, '535': 19, '444': 20, '413': 19,
            '493': 18, '402': 18, '530': 5, '543': 8, '520': 7, '544': 5, '424': 6,
            '461': 9, '521': 11, '534': 5, '519': 7, '455': 5, '539': 12, '466': 6,
            '430': 12, '478': 5, '433': 8, '445': 11, '437': 8, '504': 12, '480': 11,
            '514': 11, '508': 11, '513': 12, '524': 11, '497': 10, '431': 5, '507': 5,
            '404': 12, '418': 12, '505': 7, '464': 6, '425': 12, '442': 8, '483': 7,
            '501': 7, '415': 11, '516': 11, '502': 7, '517': 10, '419': 5, '428': 6,
            '456': 7, '469': 6, '435': 6}

    # movies
    movies = ['feast', 'lou', 'partly_cloudy', 'lifted', 'la_luna']

    # run
    data = get_parse_data(subs, movies, save=save, v=v)

    # basic plotting
    basic_data_plot(data, save=save)


def load_processed_parse():
    """Loads a previously processed file."""
    file_list = glob(
        os.path.join(outdir, 'aggregated_parse*.csv'))  # * means all if need specific format then *.csv
    recent_file = max(file_list, key=os.path.getctime)
    data = pd.read_csv(recent_file)

    return data

# if __name__ == '__main__':
#     main()
