############################################## Introduction ##############################################

# Welcome to the chicken_nhl scraper functions

# The two most important functions are: (1) scrape_schedule; and (2) scrape_pbp
# The play-by-play function takes game IDs, which can be sourced using the schedule scraper

############################################## Dependencies ##############################################

import requests
import pandas as pd
import numpy as np
from hockey_rink import NHLRink, IIHFRink, NWHLRink
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.lines import Line2D
import os

############################################## Team colors dictionary ##############################################

NHL_COLORS = {
        'ANA': {'GOAL': '#F47A38', 'SHOT': '#000000', 'MISS': '#D3D3D3'},
        'ATL': {'GOAL': '#5C88DA', 'SHOT': '#041E42', 'MISS': '#D3D3D3'},
        #'ARI': {'GOAL': '#E2D6B5', 'SHOT': '#8C2633', 'MISS': '#D3D3D3'},
        'ARI': {'GOAL': '#A9431E', 'SHOT': '#5F259F', 'MISS': '#D3D3D3'},
        'BOS': {'GOAL': '#FFB81C', 'SHOT': '#000000', 'MISS': '#D3D3D3'},
        'BUF': {'GOAL': '#FCB514', 'SHOT': '#002654', 'MISS': '#D3D3D3'},
        'CAR': {'GOAL': '#CC0000', 'SHOT': '#000000', 'MISS': '#D3D3D3'},
        'CBJ': {'GOAL': '#CE1126', 'SHOT': '#002654', 'MISS': '#D3D3D3'},
        'CGY': {'GOAL': '#F1BE48', 'SHOT': '#C8102E', 'MISS': '#D3D3D3'},
        'CHI': {'GOAL': '#CF0A2C', 'SHOT': '#000000', 'MISS': '#D3D3D3'},
        'COL': {'GOAL': '#236192', 'SHOT': '#6F263D', 'MISS': '#D3D3D3'},
        'DAL': {'GOAL': '#006847', 'SHOT': '#111111', 'MISS': '#D3D3D3'},
        'DET': {'GOAL': '#FFFFFF', 'SHOT': '#CE1126', 'MISS': '#D3D3D3'},
        'EDM': {'GOAL': '#FF4C00', 'SHOT': '#041E42', 'MISS': '#D3D3D3'},
        'FLA': {'GOAL': '#C8102E', 'SHOT': '#041E42', 'MISS': '#D3D3D3'},
        'LAK': {'GOAL': '#A2AAAD', 'SHOT': '#111111', 'MISS': '#D3D3D3'},
        'MIN': {'GOAL': '#A6192E', 'SHOT': '#154734', 'MISS': '#D3D3D3'},
        'MTL': {'GOAL': '#AF1E2D', 'SHOT': '#192168', 'MISS': '#D3D3D3'},
        'NJD': {'GOAL': '#CE1126', 'SHOT': '#000000', 'MISS': '#D3D3D3'},
        'NSH': {'GOAL': '#FFB81C', 'SHOT': '#041E42', 'MISS': '#D3D3D3'},
        'NYI': {'GOAL': '#F47D30', 'SHOT': '#00539B', 'MISS': '#D3D3D3'},
        'NYR': {'GOAL': '#CE1126', 'SHOT': '#0038A8', 'MISS': '#D3D3D3'},
        'OTT': {'GOAL': '#C2912C', 'SHOT': '#C52032', 'MISS': '#D3D3D3'},
        'PHI': {'GOAL': '#F74902', 'SHOT': '#000000', 'MISS': '#D3D3D3'},
        'PIT': {'GOAL': '#FCB514', 'SHOT': '#000000', 'MISS': '#D3D3D3'},
        'SEA': {'GOAL': '#99D9D9', 'SHOT': '#001628', 'MISS': '#D3D3D3'},
        'SJS': {'GOAL': '#006D75', 'SHOT': '#000000', 'MISS': '#D3D3D3'},
        'STL': {'GOAL': '#FCB514', 'SHOT': '#002F87', 'MISS': '#D3D3D3'},
        'TBL': {'GOAL': '#FFFFFF', 'SHOT': '#002868', 'MISS': '#D3D3D3'},
        'TOR': {'GOAL': '#FFFFFF', 'SHOT': '#00205B', 'MISS': '#D3D3D3'},
        'VAN': {'GOAL': '#00843D', 'SHOT': '#00205B', 'MISS': '#D3D3D3'},
        'VGK': {'GOAL': '#B4975A', 'SHOT': '#333F42', 'MISS': '#D3D3D3'},
        'WSH': {'GOAL': '#C8102E', 'SHOT': '#041E42', 'MISS': '#D3D3D3'},
        'WPG': {'GOAL': '#AC162C', 'SHOT': '#041E42', 'MISS': '#D3D3D3'},
                }

############################################## Helper functions ##############################################

def norm_coords(data, norm_team):
    '''
    Function to normalize coordinates to one zone
    
    Attributes
        data: a one-game dataframe
        
        norm_team: the three-letter team tri-code that serves as the normalization reference
        
    '''
    
    good_team = data.event_team == norm_team
    bad_team = data.event_team != norm_team
    
    neg_x = (data['coords_x'] < 0)
    pos_x = (data['coords_x'] > 0)

    conditions = [good_team & neg_x, bad_team & pos_x]
    values_x = [data['coords_x'].mul(-1), data['coords_x'].mul(-1)]
    values_y = [data['coords_y'].mul(-1), data['coords_y'].mul(-1)]

    data['norm_coords_x'] = np.select(conditions, values_x, default = data['coords_x'])
    data['norm_coords_y'] = np.select(conditions, values_y, default = data['coords_y'])
    
    return data

def convert_to_list(obj):
    '''If the object is not a list, converts the object to a list of length one'''
    
    if type(obj) is not list and type(obj) is not pd.Series:
        
        obj = [obj]
    
    return obj

############################################## One-game rink map function ##############################################

def game_rink_map(data, good_team = None, title = None, size = None, strengths = ['all', '5v5', 'PP', 'SH', 'EV', '3v3'],
                        colors = None, save_img = False, annotations = True, default_colors = NHL_COLORS, size_multiplier = 50):
    
    '''
    Function to normalize coordinates to one zone
    
    Attributes
        data: a one-game dataframe
        
        good_team: str; default None means the home team is the top half of the plot. 
                            Else, use the three-letter tri code for the team you want on top.

        title: str; Give the title you want for the plot.
                        Default title is: Away team [score] @ Home team [score] - Date

        strengths: list or str; default is all strength types. Choose one or a combination of any strengths from the default list

        colors: dictionary; Optional, give a dictionary of {team tri code: {'GOAL': hex code, 'SHOT': hex code, 'MISS': hex code}}

        save_img: bool; if true, saves the figure(s) as an image to a folder 'rink_plots' created in the current directory
        
    '''

    data = data.copy(deep = True)

    if type(strengths) != list:

        strengths = convert_to_list(strengths)

    if colors == None:

        colors = default_colors
    
    if good_team == None:

        if 'NSH' in list(data.event_team.dropna().unique()):

            good_team = 'NSH'

        else:

            good_team = data.home_team.iloc[0]

    if good_team not in colors.keys():

        colors.update({good_team: default_colors[good_team]})


    game_date = data.game_date.iloc[0].strftime('%b %d, %Y')

    if title == None:

        data.game_date = pd.to_datetime(data.game_date, infer_datetime_format = True)
        
        home_team = data.home_team.iloc[0]
        
        home_score = data.home_score.max()
        
        away_team = data.away_team.iloc[0]
        
        away_score = data.away_score.max()

        if data.shootout.sum() > 1:

            title = f'\n{away_team} {away_score} @ {home_team} {home_score} (SO) - {game_date}'

        else:

            title = f'\n{away_team} {away_score} @ {home_team} {home_score} - {game_date}'

    bad_team = data[data.event_team != good_team].event_team.dropna().iloc[0]

    if bad_team not in colors.keys():

        colors.update({bad_team: NHL_COLORS[bad_team]})

    good_score = np.where(data.home_team == good_team, data.home_score.max(), data.away_score.max())

    bad_score = np.where(data.home_team == bad_team, data.home_score.max(), data.away_score.max())

    FENWICK = ['GOAL', 'SHOT', 'MISS']

    for team, color_dict in colors.items():

        for event_result in FENWICK:

            if event_result not in color_dict.keys():

                color_dict[event_result] = default_colors[team][event_result]

    mask = np.logical_and(data.event.isin(FENWICK), data.event_zone == 'OFF')

    some_df = data[mask].copy()

    some_df = norm_coords(some_df.copy(), good_team)

    for strength in strengths:

        if strength == 'all':

            df = some_df[np.logical_and(some_df.shootout != 1, some_df.penalty_shot != 1)].copy()

            subtitle = 'Shot attempts, all strengths | @chickenandstats\n\n'

        elif strength == 'PP':

            subtitle = 'Power play shot attempts | @chickenandstats\n\n'

            pp_list = ['5v4', '5v3']

            df = some_df[some_df.strength_state.isin(pp_list)].copy()

            if df.empty:

                continue

        elif strength == 'SH':

            subtitle = 'Shorthanded shot attempts | @chickenandstats\n\n'

            sh_list = ['4v5', '3v5']

            df = some_df[some_df.strength_state.isin(sh_list)].copy()

            if df.empty:

                continue

        elif strength == 'EV':

            subtitle = 'Even strength shot attempts | @chickenandstats\n\n'

            sh_list = ['5v5', '4v4', '3v3']

            df = some_df[some_df.strength_state.isin(sh_list)].copy()

            if df.empty:

                continue

        else:

            df = some_df[np.logical_and(some_df.strength_state == strength, some_df.empty_net == 0)].copy()

            if df.empty:

                continue

            subtitle = f'{strength} shot attempts | @chickenandstats\n\n'

        ozone = NHLRink(rotation = 90)
        dzone = NHLRink(rotation = 90)

        plt.rcParams['figure.figsize'] = [15, 15]

        fig, (ax1, ax2) = plt.subplots(2, constrained_layout=True)

        fig.set_facecolor('white')

        OZ = ozone.draw(display_range = 'ozone', ax = ax1)
        DZ = dzone.draw(display_range = 'dzone', ax = ax2)

        df['colors'] = 0

        df.colors = np.where(df.event_team == good_team,
                         df.event.map(colors[good_team]).fillna(df.colors),
                         df.event.map(colors[bad_team]).fillna(df.colors))  


        fig.suptitle(title, ha = 'center', fontsize = 26, weight = 'bold')

        ax1.set_title(subtitle, size = 18)

        teams = list(df.event_team.unique())

        for team in teams:

            plot_df = df[df.event_team == team]

            colors_dict = dict(zip(plot_df.event.unique(), plot_df.colors.unique()))

            order_list = ['GOAL', 'SHOT', 'MISS']

            colors_dict = {x: colors_dict[x] for x in order_list if x in colors_dict.keys()}

            zorder_dict = {'GOAL': 999, 'SHOT': 998, 'MISS': 997}

            if team == good_team:

                ax = ax1

                rink = ozone

            if team == bad_team:

                ax = ax2

                rink = dzone

            for result, color in colors_dict.items():

                event_df = plot_df[plot_df.event == result].copy()

                if result == 'GOAL':

                    edge_color = colors[team]['SHOT']

                else:

                    edge_color = None

                    
                if size == None:
                    
                    s = 250
                    
                else:
                    
                    s = 0.3 * (event_df[size] * size_multiplier) ** 2
                
                sc = rink.scatter(event_df.norm_coords_x, event_df.norm_coords_y, c = color, label = result, s = s, alpha = 0.8,
                                ax = ax, edgecolors = edge_color, is_constrained = True, zorder = zorder_dict[result])

                
                if result == 'GOAL':
                    
                    if annotations == True:
                        
                        event_df['new_x'], event_df['new_y'] = rink.convert_xy(event_df.norm_coords_x + 1.2, event_df.norm_coords_y - 1.2)
                        
                        for idx in event_df.index:
                            
                            ax.annotate(event_df['event_player_1'][idx],
                                        (event_df['new_x'][idx], event_df['new_y'][idx]),
                                        bbox=dict(boxstyle = 'round', fc = 'white', ec = 'gray', alpha = 0.65)
                                       ).set_zorder(1000)
                    
                    #for i in range(len(x)):
                     #   plt.annotate(text[i], (x[i], y[i] + 0.2))
            #img_path = f'/Users/scott/Documents/Sports Blog/Open source/logos/{team}.png'

            #img = mpimg.imread(img_path)

            #ax.imshow(img).set_zorder(1000)

            if team == good_team:

                if size == None:

                    legend = ax.legend(loc="lower center", ncol=3, title = f'{team}', fontsize = 14,
                                    title_fontsize = 16, facecolor = 'white', framealpha = 1,
                                    edgecolor = 'gray').set_zorder(-1)

                else:

                    legend_elements = list()

                    for result, color in colors_dict.items():

                        if result == 'GOAL':

                            edge_color = colors[team]['SHOT']

                        else:

                            edge_color = color

                        element = Line2D([0], [0], markeredgecolor = edge_color, marker = 'o', markerfacecolor = color,
                                    label = result, markersize = 14, color = 'w', alpha = 0.8)

                        legend_elements.append(element)

                    legend = ax.legend(handles = legend_elements, loc="lower center", ncol=3, title = f'{team}', fontsize = 14,
                                        title_fontsize = 16, facecolor = 'white', framealpha = 1,
                                        edgecolor = 'gray').set_zorder(-1)
  
            if team == bad_team:

                if size == None:

                    legend = ax.legend(loc="upper center", ncol=3, title = f'{team}', fontsize = 14,
                                    title_fontsize = 16, facecolor = 'white', framealpha = 1,
                                    edgecolor = 'gray').set_zorder(-1)

                else:

                    legend_elements = list()

                    for result, color in colors_dict.items():

                        if result == 'GOAL':

                            edge_color = colors[team]['SHOT']

                        else:

                            edge_color = color

                        element = Line2D([0], [0], markeredgecolor = edge_color, marker = 'o', markerfacecolor = color,
                                    label = result, markersize = 14, color = 'w', alpha = 0.8)

                        legend_elements.append(element)

                    legend = ax.legend(handles = legend_elements, loc="upper center", ncol=3, title = f'{team}', fontsize = 14,
                                        title_fontsize = 16, facecolor = 'white', framealpha = 1,
                                        edgecolor = 'gray').set_zorder(-1)
                

        if save_img == True:
            
            if os.path.exists('rink_plots') == False:

                os.makedirs('rink_plots')

            file_name = os.path.join('rink_plots', f'{good_team}_{bad_team}_{strength}_{game_date}.png')

            fig.savefig(file_name, dpi = 750, bbox_inches = 'tight', facecolor = 'white')

