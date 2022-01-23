############################################## Introduction ##############################################

# Welcome to the chicken_nhl xG functions

# The important one is the predict goals function

############################################## Dependencies ##############################################

import pkg_resources
import pandas as pd
import numpy as np
import pickle
import os

############################################## Functions for prepping the data ##############################################

def xG_prep(df):
    '''
    Docstring
    
    Parameters
    
    '''
    
    ## Super important lists
    FENWICK_EVENTS = ['SHOT', 'GOAL', 'MISS']
    CORSI_EVENTS = ['SHOT', 'GOAL', 'MISS', 'BLOCK']
    EVENT_LIST= ['GOAL', 'SHOT', 'MISS', 'BLOCK', 'FAC', 'HIT', 'GIVE', 'TAKE']

    ## Filter raw pbp data to the important stuff
    in_event_list = np.isin(df.event, EVENT_LIST)
    not_shootout = df.shootout == 0
    not_penalty_shot = df.penalty_shot == 0
    x_not_na = ~pd.isna(df.coords_x)
    y_not_na = ~pd.isna(df.coords_y)
    is_fenwick = np.isin(df.event, FENWICK_EVENTS)
    is_corsi = np.isin(df.event, CORSI_EVENTS)
    #other_conds = (np.equal(df.coords_x, 0) & np.equal(df.coords_y, 0) & np.not_equal(df.pbp_distance, 90) & is_fenwick)

    conditions = (in_event_list & not_shootout & not_penalty_shot & x_not_na & y_not_na) #& ~other_conds)

    df = df[conditions].copy(deep = True)
    
    same_season = np.equal(df.season, df.season.shift(1))
    same_game = np.equal(df.game_id, df.game_id.shift(1))
    same_period = np.equal(df.period, df.period.shift(1))

    conds = (same_season & same_game & same_period)

    df['seconds_since_last'] = np.where(conds, df.game_seconds - df.game_seconds.shift(1), np.nan)
    df['event_type_last'] = np.where(conds, df.event.shift(1), np.nan)
    df['event_team_last'] = np.where(conds, df.event_team.shift(1), np.nan)
    df['event_strength_last'] = np.where(conds, df.strength_state.shift(1), np.nan)
    df['coords_x_last'] = np.where(conds, df.coords_x.shift(1), np.nan)
    df['coords_y_last'] = np.where(conds, df.coords_y.shift(1), np.nan)
    
    df['same_team_last'] = np.where(np.equal(df.event_team, df.event_team_last), 1, 0)

    df['distance_from_last'] = ((df.coords_x - df.coords_x_last) ** 2 + (df.coords_y - df.coords_y_last) ** 2) ** (1/2)
    
    df.event_detail = np.where(np.logical_and(df.event.isin(FENWICK_EVENTS), pd.isna(df.event_detail)), 'Wrist', df.event_detail)
    
    if 'score_diff' not in df.columns:
        
        df['score_diff'] = np.where(df.is_home == 1,
                                    df.home_score.astype(int) - df.away_score.astype(int),
                                    df.away_score.astype(int) - df.home_score.astype(int))
        
    ##rename columns for shots
    cols_rename = {'event_distance' : 'shot_distance', 'event_angle' : 'shot_angle'}

    df = df.rename(columns = cols_rename)
    
    return df

def xG_prep_EV(df):
    '''
    Docstring
    
    Parameters
    
    '''
    
    ## Important lists
    
    FENWICK_EVENTS = ['SHOT', 'GOAL', 'MISS']
    EVEN_STRENGTH = ['5v5', '4v4', '3v3']
    
    ##create copy of model data set
    df = df.copy()
    
    ##set filter conditions
    is_fenwick = np.isin(df.event, FENWICK_EVENTS)
    last_x_is_na = np.isnan(df.coords_x_last)
    last_y_is_na = np.isnan(df.coords_y_last)
    net_not_empty = np.logical_or(np.logical_and(df.is_home == 1, df.home_empty_net == 0),
                                  np.logical_and(df.is_home == 0, df.away_empty_net == 0))

    is_correct_strength = np.logical_and(np.isin(df.strength_state, EVEN_STRENGTH), df.empty_net != 1)

    conds = (is_fenwick & is_correct_strength & ~last_x_is_na & ~last_y_is_na & net_not_empty)

    ##filter data for even strength
    df = df[conds].copy()
    
    state_list = ['5v5', '4v4', '3v3']
    
    for state in EVEN_STRENGTH:
        
        df['state_' + state] = np.where(np.equal(df.strength_state, state), 1, 0)
    
    df['score_down_4'] = np.where(df.score_diff <= -4, 1, 0)
    df['score_down_3'] = np.where(np.equal(df.score_diff, -3), 1, 0)
    df['score_down_2'] = np.where(np.equal(df.score_diff, -2), 1, 0)
    df['score_down_1'] = np.where(np.equal(df.score_diff, -1), 1, 0)
    df['score_even'] = np.where(np.equal(df.score_diff, 0), 1, 0)
    df['score_up_1'] = np.where(np.equal(df.score_diff, 1), 1, 0)
    df['score_up_2'] = np.where(np.equal(df.score_diff, 2), 1, 0)
    df['score_up_3'] = np.where(np.equal(df.score_diff, 3), 1, 0)
    df['score_up_4'] = np.where(df.score_diff >= 4, 1, 0)

    df['wrist_shot'] = np.where(np.equal(df.event_detail, 'Wrist'), 1, 0)
    df['deflected_shot'] = np.where(np.equal(df.event_detail, 'Deflected'), 1, 0)
    df['tip_shot'] = np.where(np.equal(df.event_detail, 'Tip-In'), 1, 0)
    df['slap_shot'] = np.where(np.equal(df.event_detail, 'Slap'), 1, 0)
    df['backhand_shot'] = np.where(np.equal(df.event_detail, 'Backhand'), 1, 0)
    df['snap_shot'] = np.where(np.equal(df.event_detail, 'Snap'), 1, 0)
    df['wrap_shot'] = np.where(np.equal(df.event_detail, 'Wrap-around'), 1, 0)

    last_is_shot = np.equal(df.event_type_last, 'SHOT')
    last_is_miss = np.equal(df.event_type_last, 'MISS')
    last_is_block = np.equal(df.event_type_last, 'BLOCK')
    last_is_give = np.equal(df.event_type_last, 'GIVE')
    last_is_take = np.equal(df.event_type_last, 'TAKE')
    last_is_hit = np.equal(df.event_type_last, 'HIT')
    last_is_fac = np.equal(df.event_type_last, 'FAC')

    same_team_as_last = np.equal(df.same_team_last, 1)
    not_same_team_as_last = np.equal(df.same_team_last, 0)

    df['prior_shot_same'] = np.where((last_is_shot & same_team_as_last), 1, 0)
    df['prior_miss_same'] = np.where((last_is_miss & same_team_as_last), 1, 0)
    df['prior_block_same'] = np.where((last_is_block & same_team_as_last), 1, 0)
    df['prior_give_same'] = np.where((last_is_give & same_team_as_last), 1, 0)
    df['prior_take_same'] = np.where((last_is_take & same_team_as_last), 1, 0)
    df['prior_hit_same'] = np.where((last_is_hit & same_team_as_last), 1, 0)

    df['prior_shot_opp'] = np.where((last_is_shot & not_same_team_as_last), 1, 0)
    df['prior_miss_opp'] = np.where((last_is_miss & not_same_team_as_last), 1, 0)
    df['prior_block_opp'] = np.where((last_is_block & not_same_team_as_last), 1, 0)
    df['prior_give_opp'] = np.where((last_is_give & not_same_team_as_last), 1, 0)
    df['prior_take_opp'] = np.where((last_is_take & not_same_team_as_last), 1, 0)
    df['prior_hit_opp'] = np.where((last_is_hit & not_same_team_as_last), 1, 0)

    df['prior_face'] = np.where(last_is_fac, 1, 0)

    ##prep final dataframe

    ev_strength_col_list = ['is_goal', 'shot_distance', 'shot_angle', 'is_home', 'state_5v5', 'state_4v4', 'state_3v3',
                            'score_down_4', 'score_down_3', 'score_down_2', 'score_down_1', 'score_even', 'score_up_1',
                            'score_up_2', 'score_up_3', 'score_up_4', 'game_seconds', 'period', 'coords_x', 'coords_y',
                            'coords_x_last', 'coords_y_last', 'wrist_shot', 'deflected_shot', 'tip_shot', 'slap_shot', 'backhand_shot',
                            'snap_shot', 'wrap_shot', 'distance_from_last', 'seconds_since_last', 'prior_shot_same', 'prior_miss_same',
                            'prior_block_same', 'prior_give_same', 'prior_take_same', 'prior_hit_same', 'prior_shot_opp', 'prior_miss_opp',
                            'prior_block_opp', 'prior_give_opp', 'prior_take_opp', 'prior_hit_opp', 'prior_face']        

    df = df[ev_strength_col_list].copy().astype('float').astype('int')
    
    return df

def xG_prep_PP(df):
    '''
    Docstring
    
    Parameters
    '''
    
    ## Important lists
    FENWICK_EVENTS = ['SHOT', 'GOAL', 'MISS']
    PP_STRENGTH = ['5v4', '5v3', '4v3']
    
    ##create copy of model data set
    
    df = df.copy()

    is_pp = np.logical_and(np.isin(df.strength_state, PP_STRENGTH), df.empty_net == 0)

    ##set filter conditions
    is_fenwick = np.isin(df.event, FENWICK_EVENTS)
    last_x_is_na = np.isnan(df.coords_x_last)
    last_y_is_na = np.isnan(df.coords_y_last)
    net_not_empty = np.logical_or(np.logical_and(df.is_home == 1, df.home_empty_net == 0),
                                  np.logical_and(df.is_home == 0, df.away_empty_net == 0))

    conds = (is_fenwick & is_pp & ~last_x_is_na & ~last_y_is_na & net_not_empty)
    
    ##setting time since start of penalty

    df['pen_index_0'] = np.where((df.pen_idx.shift(1) != df.pen_idx), 0, np.nan)
    df['pen_start_seconds'] = np.where((df['pen_index_0'] == 0), df.game_seconds, np.nan)
    df.pen_start_seconds = df.pen_start_seconds.fillna(method = 'ffill')
    df['pen_seconds_since'] = df.game_seconds - df.pen_start_seconds

    pen_300_seconds = df.pen_seconds_since >= 300
    df.pen_seconds_since = np.where(pen_300_seconds, 120, df.pen_seconds_since)

    drop_list = ['pen_index_0', 'pen_start_seconds']
    df = df.drop(drop_list, axis = 1) 
    
    df = df[conds].copy()
    
    if df.empty:
        
        return df
    
    for state in PP_STRENGTH:
        
        df['state_' + state] = np.where(np.equal(df.strength_state, state), 1, 0)

    df['score_down_4'] = np.where(df.score_diff <= -4, 1, 0)
    df['score_down_3'] = np.where(np.equal(df.score_diff, -3), 1, 0)
    df['score_down_2'] = np.where(np.equal(df.score_diff, -2), 1, 0)
    df['score_down_1'] = np.where(np.equal(df.score_diff, -1), 1, 0)
    df['score_even'] = np.where(np.equal(df.score_diff, 0), 1, 0)
    df['score_up_1'] = np.where(np.equal(df.score_diff, 1), 1, 0)
    df['score_up_2'] = np.where(np.equal(df.score_diff, 2), 1, 0)
    df['score_up_3'] = np.where(np.equal(df.score_diff, 3), 1, 0)
    df['score_up_4'] = np.where(df.score_diff >= 4, 1, 0)

    df['wrist_shot'] = np.where(np.equal(df.event_detail, 'Wrist'), 1, 0)
    df['deflected_shot'] = np.where(np.equal(df.event_detail, 'Deflected'), 1, 0)
    df['tip_shot'] = np.where(np.equal(df.event_detail, 'Tip-In'), 1, 0)
    df['slap_shot'] = np.where(np.equal(df.event_detail, 'Slap'), 1, 0)
    df['backhand_shot'] = np.where(np.equal(df.event_detail, 'Backhand'), 1, 0)
    df['snap_shot'] = np.where(np.equal(df.event_detail, 'Snap'), 1, 0)
    df['wrap_shot'] = np.where(np.equal(df.event_detail, 'Wrap-around'), 1, 0)

    last_is_shot = np.equal(df['event_type_last'], 'SHOT')
    last_is_miss = np.equal(df['event_type_last'], 'MISS')
    last_is_block = np.equal(df['event_type_last'], 'BLOCK')
    last_is_give = np.equal(df['event_type_last'], 'GIVE')
    last_is_take = np.equal(df['event_type_last'], 'TAKE')
    last_is_hit = np.equal(df['event_type_last'], 'HIT')
    last_is_fac = np.equal(df['event_type_last'], 'FAC')

    same_team_as_last = np.equal(df.same_team_last, 1)
    not_same_team_as_last = np.equal(df.same_team_last, 0)

    df['prior_shot_same'] = np.where((last_is_shot & same_team_as_last), 1, 0)
    df['prior_miss_same'] = np.where((last_is_miss & same_team_as_last), 1, 0)
    df['prior_block_same'] = np.where((last_is_block & same_team_as_last), 1, 0)
    df['prior_give_same'] = np.where((last_is_give & same_team_as_last), 1, 0)
    df['prior_take_same'] = np.where((last_is_take & same_team_as_last), 1, 0)
    df['prior_hit_same'] = np.where((last_is_hit & same_team_as_last), 1, 0)

    df['prior_shot_opp'] = np.where((last_is_shot & not_same_team_as_last), 1, 0)
    df['prior_miss_opp'] = np.where((last_is_miss & not_same_team_as_last), 1, 0)
    df['prior_block_opp'] = np.where((last_is_block & not_same_team_as_last), 1, 0)
    df['prior_give_opp'] = np.where((last_is_give & not_same_team_as_last), 1, 0)
    df['prior_take_opp'] = np.where((last_is_take & not_same_team_as_last), 1, 0)
    df['prior_hit_opp'] = np.where((last_is_hit & not_same_team_as_last), 1, 0)

    df['prior_face'] = np.where(last_is_fac, 1, 0)

    ##prep final dataframe

    pp_strength_col_list = ['is_goal', 'shot_distance', 'shot_angle', 'is_home', 'state_5v4', 'state_5v3', 'state_4v3', 'score_down_4',
                            'score_down_3', 'score_down_2', 'score_down_1', 
                            'score_even', 'score_up_1', 'score_up_2', 'score_up_3', 'score_up_4', 'game_seconds', 
                            'period', 'coords_x', 'coords_y', 'coords_x_last', 'coords_y_last', 'wrist_shot', 
                            'deflected_shot', 'tip_shot', 'slap_shot', 'backhand_shot', 'snap_shot', 'wrap_shot', 
                            'distance_from_last', 'seconds_since_last', 'pen_seconds_since',
                            'prior_shot_same', 'prior_miss_same', 'prior_block_same', 'prior_give_same', 'prior_take_same', 
                            'prior_hit_same', 'prior_shot_opp', 'prior_miss_opp']            

    df = df[pp_strength_col_list].copy().astype('float').astype('int')

    return df

def xG_prep_SH(df):
    
    
    ## Important lists
    
    FENWICK_EVENTS = ['SHOT', 'GOAL', 'MISS']
    SH_STRENGTH = ['3v4', '3v5', '4v5']
    
    ##create copy of model data set
    df = df.copy()
    
    ##set filter conditions
    is_fenwick = np.isin(df.event, FENWICK_EVENTS)
    last_x_is_na = np.isnan(df.coords_x_last)
    last_y_is_na = np.isnan(df.coords_y_last)
    net_not_empty = np.logical_or(np.logical_and(df.is_home == 1, df.home_empty_net == 0),
                                  np.logical_and(df.is_home == 0, df.away_empty_net == 0))

    is_correct_strength = np.logical_and(np.isin(df.strength_state, SH_STRENGTH), df.empty_net != 1)

    conds = (is_fenwick & is_correct_strength & ~last_x_is_na & ~last_y_is_na & net_not_empty)
    
    ##setting time since start of penalty

    df['pen_index_0'] = np.where((df.pen_idx.shift(1) != df.pen_idx), 0, np.nan)
    df['pen_start_seconds'] = np.where((df['pen_index_0'] == 0), df.game_seconds, np.nan)
    df.pen_start_seconds = df.pen_start_seconds.fillna(method = 'ffill')
    df['pen_seconds_since'] = df.game_seconds - df.pen_start_seconds
    
    pen_300_seconds = df.pen_seconds_since >= 300
    df.pen_seconds_since = np.where(pen_300_seconds, 120, df.pen_seconds_since)

    drop_list = ['pen_index_0', 'pen_start_seconds']
    df = df.drop(drop_list, axis = 1) 

    ##filter data for even strength
    df = df[conds].copy()
    
    if df.empty:
        
        return df
    
    for state in SH_STRENGTH:
        
        df['state_' + state] = np.where(np.equal(df.strength_state, state), 1, 0)

    df['score_down_4'] = np.where(df.score_diff <= -4, 1, 0)
    df['score_down_3'] = np.where(np.equal(df.score_diff, -3), 1, 0)
    df['score_down_2'] = np.where(np.equal(df.score_diff, -2), 1, 0)
    df['score_down_1'] = np.where(np.equal(df.score_diff, -1), 1, 0)
    df['score_even'] = np.where(np.equal(df.score_diff, 0), 1, 0)
    df['score_up_1'] = np.where(np.equal(df.score_diff, 1), 1, 0)
    df['score_up_2'] = np.where(np.equal(df.score_diff, 2), 1, 0)
    df['score_up_3'] = np.where(np.equal(df.score_diff, 3), 1, 0)
    df['score_up_4'] = np.where(df.score_diff >= 4, 1, 0)

    df['wrist_shot'] = np.where(np.equal(df['event_detail'], 'Wrist'), 1, 0)
    df['deflected_shot'] = np.where(np.equal(df['event_detail'], 'Deflected'), 1, 0)
    df['tip_shot'] = np.where(np.equal(df['event_detail'], 'Tip-In'), 1, 0)
    df['slap_shot'] = np.where(np.equal(df['event_detail'], 'Slap'), 1, 0)
    df['backhand_shot'] = np.where(np.equal(df['event_detail'], 'Backhand'), 1, 0)
    df['snap_shot'] = np.where(np.equal(df['event_detail'], 'Snap'), 1, 0)
    df['wrap_shot'] = np.where(np.equal(df['event_detail'], 'Wrap-around'), 1, 0)

    last_is_shot = np.equal(df.event_type_last, 'SHOT')
    last_is_miss = np.equal(df.event_type_last, 'MISS')
    last_is_block = np.equal(df.event_type_last, 'BLOCK')
    last_is_give = np.equal(df.event_type_last, 'GIVE')
    last_is_take = np.equal(df.event_type_last, 'TAKE')
    last_is_hit = np.equal(df.event_type_last, 'HIT')
    last_is_fac = np.equal(df.event_type_last, 'FAC')

    same_team_as_last = np.equal(df.same_team_last, 1)
    not_same_team_as_last = np.equal(df.same_team_last, 0)

    df['prior_shot_same'] = np.where((last_is_shot & same_team_as_last), 1, 0)
    df['prior_miss_same'] = np.where((last_is_miss & same_team_as_last), 1, 0)
    df['prior_block_same'] = np.where((last_is_block & same_team_as_last), 1, 0)
    df['prior_give_same'] = np.where((last_is_give & same_team_as_last), 1, 0)
    df['prior_take_same'] = np.where((last_is_take & same_team_as_last), 1, 0)
    df['prior_hit_same'] = np.where((last_is_hit & same_team_as_last), 1, 0)

    df['prior_shot_opp'] = np.where((last_is_shot & not_same_team_as_last), 1, 0)
    df['prior_miss_opp'] = np.where((last_is_miss & not_same_team_as_last), 1, 0)
    df['prior_block_opp'] = np.where((last_is_block & not_same_team_as_last), 1, 0)
    df['prior_give_opp'] = np.where((last_is_give & not_same_team_as_last), 1, 0)
    df['prior_take_opp'] = np.where((last_is_take & not_same_team_as_last), 1, 0)
    df['prior_hit_opp'] = np.where((last_is_hit & not_same_team_as_last), 1, 0)

    df['prior_face'] = np.where(last_is_fac, 1, 0)

    ##prep final dataframe

    sh_strength_col_list = ['is_goal', 'shot_distance', 'shot_angle', 'is_home', 'state_3v4', 'state_3v5',
                            'state_4v5', 'score_down_4', 'score_down_3', 'score_down_2', 'score_down_1', 
                            'score_even', 'score_up_1', 'score_up_2', 'score_up_3', 'score_up_4', 'game_seconds', 
                            'period', 'coords_x', 'coords_y', 'coords_x_last', 'coords_y_last', 'wrist_shot', 
                            'deflected_shot', 'tip_shot', 'slap_shot', 'backhand_shot', 'snap_shot', 'wrap_shot', 
                            'distance_from_last', 'seconds_since_last', 'pen_seconds_since',
                            'prior_shot_same', 'prior_miss_same', 'prior_block_same', 'prior_give_same', 'prior_take_same', 
                            'prior_hit_same', 'prior_shot_opp', 'prior_miss_opp']            

    df = df[sh_strength_col_list].astype('float').astype('int')
        
    return df

def xG_prep_EN(df):
    '''Empty net, but on offense'''
    
    ## Important lists
    
    FENWICK_EVENTS = ['SHOT', 'GOAL', 'MISS']

    ##create copy of model data set
    
    df = df.copy()

    ## Important lists  

    ##set filter conditions
    is_fenwick = np.isin(df.event, FENWICK_EVENTS)
    last_x_is_na = np.isnan(df.coords_x_last)
    last_y_is_na = np.isnan(df.coords_y_last)

    is_correct_strength = df.empty_net == 1

    conds = (is_fenwick & is_correct_strength & ~last_x_is_na & ~last_y_is_na)

    ##filter data for strength
    df = df[conds].copy()
    
    if df.empty:
        
        return df

    strength_list = ['3v4', '3v5', '3v6', '4v4', '4v5', '4v6', '5v5', '5v6']
    
    for strength in strength_list:
        
        df['state_' + strength] = np.where(df.strength_state == strength, 1, 0)

    df['score_down_4'] = np.where(df.score_diff <= -4, 1, 0)
    df['score_down_3'] = np.where(np.equal(df.score_diff, -3), 1, 0)
    df['score_down_2'] = np.where(np.equal(df.score_diff, -2), 1, 0)
    df['score_down_1'] = np.where(np.equal(df.score_diff, -1), 1, 0)
    df['score_even'] = np.where(np.equal(df.score_diff, 0), 1, 0)
    df['score_up_1'] = np.where(np.equal(df.score_diff, 1), 1, 0)
    df['score_up_2'] = np.where(np.equal(df.score_diff, 2), 1, 0)
    df['score_up_3'] = np.where(np.equal(df.score_diff, 3), 1, 0)
    df['score_up_4'] = np.where(df.score_diff >= 4, 1, 0)

    df['wrist_shot'] = np.where(np.equal(df.event_detail, 'Wrist'), 1, 0)
    df['deflected_shot'] = np.where(np.equal(df.event_detail, 'Deflected'), 1, 0)
    df['tip_shot'] = np.where(np.equal(df.event_detail, 'Tip-In'), 1, 0)
    df['slap_shot'] = np.where(np.equal(df.event_detail, 'Slap'), 1, 0)
    df['backhand_shot'] = np.where(np.equal(df.event_detail, 'Backhand'), 1, 0)
    df['snap_shot'] = np.where(np.equal(df.event_detail, 'Snap'), 1, 0)
    df['wrap_shot'] = np.where(np.equal(df.event_detail, 'Wrap-around'), 1, 0)

    last_is_shot = np.equal(df.event_type_last, 'SHOT')
    last_is_miss = np.equal(df.event_type_last, 'MISS')
    last_is_block = np.equal(df.event_type_last, 'BLOCK')
    last_is_give = np.equal(df.event_type_last, 'GIVE')
    last_is_take = np.equal(df.event_type_last, 'TAKE')
    last_is_hit = np.equal(df.event_type_last, 'HIT')
    last_is_fac = np.equal(df.event_type_last, 'FAC')

    same_team_as_last = np.equal(df.same_team_last, 1)
    not_same_team_as_last = np.equal(df.same_team_last, 0)

    df['prior_shot_same'] = np.where((last_is_shot & same_team_as_last), 1, 0)
    df['prior_miss_same'] = np.where((last_is_miss & same_team_as_last), 1, 0)
    df['prior_block_same'] = np.where((last_is_block & same_team_as_last), 1, 0)
    df['prior_give_same'] = np.where((last_is_give & same_team_as_last), 1, 0)
    df['prior_take_same'] = np.where((last_is_take & same_team_as_last), 1, 0)
    df['prior_hit_same'] = np.where((last_is_hit & same_team_as_last), 1, 0)

    df['prior_shot_opp'] = np.where((last_is_shot & not_same_team_as_last), 1, 0)
    df['prior_miss_opp'] = np.where((last_is_miss & not_same_team_as_last), 1, 0)
    df['prior_block_opp'] = np.where((last_is_block & not_same_team_as_last), 1, 0)
    df['prior_give_opp'] = np.where((last_is_give & not_same_team_as_last), 1, 0)
    df['prior_take_opp'] = np.where((last_is_take & not_same_team_as_last), 1, 0)
    df['prior_hit_opp'] = np.where((last_is_hit & not_same_team_as_last), 1, 0)

    df['prior_face'] = np.where(last_is_fac, 1, 0)

    ##prep final dataframe

    en_col_list = ['is_goal', 'shot_distance', 'shot_angle', 'is_home', 'state_3v4', 'state_3v5', 'state_3v6', 'state_4v4',
                   'state_4v5', 'state_4v6', 'state_5v6', 
                    'score_down_4', 'score_down_3', 'score_down_2', 'score_down_1', 
                    'score_even', 'score_up_1', 'score_up_2', 'score_up_3', 'score_up_4', 'game_seconds', 
                    'period', 'coords_x', 'coords_y', 'coords_x_last', 'coords_y_last', 'wrist_shot', 
                    'deflected_shot', 'tip_shot', 'slap_shot', 'backhand_shot', 'snap_shot', 'wrap_shot', 
                    'distance_from_last', 'seconds_since_last', 'prior_shot_same', 'prior_miss_same', 
                    'prior_block_same', 'prior_give_same', 'prior_take_same', 'prior_hit_same', 
                    'prior_shot_opp', 'prior_miss_opp']            

    df = df[en_col_list].astype('float').astype('int')

    return df

def xG_prep_UE(df):
    '''Defending an empty net'''
    
    FENWICK_EVENTS = ['SHOT', 'GOAL', 'MISS']
    
    ##create copy of model data set
    
    df = df.copy()

    ## Important lists  

    ##set filter conditions
    is_fenwick = np.isin(df.event, FENWICK_EVENTS)
    last_x_is_na = np.isnan(df.coords_x_last)
    last_y_is_na = np.isnan(df.coords_y_last)

    is_correct_strength = np.logical_or(np.logical_and(df.is_home == 1, df.home_empty_net == 1),
                                        np.logical_and(df.is_home == 0, df.away_empty_net == 1))

    conds = (is_fenwick & is_correct_strength & ~last_x_is_na & ~last_y_is_na)

    ##filter data for strength
    df = df[conds].copy()
    
    if df.empty:
        
        return df

    strength_list = ['4v3', '4v4', '4v5', '4v6', '5v5', '5v4', '5v3', '6v4', '6v5', '6v3']
    
    for strength in strength_list:
        
        df['state_' + strength] = np.where(df.strength_state == strength, 1, 0)

    df['score_down_4'] = np.where(df.score_diff <= -4, 1, 0)
    df['score_down_3'] = np.where(np.equal(df.score_diff, -3), 1, 0)
    df['score_down_2'] = np.where(np.equal(df.score_diff, -2), 1, 0)
    df['score_down_1'] = np.where(np.equal(df.score_diff, -1), 1, 0)
    df['score_even'] = np.where(np.equal(df.score_diff, 0), 1, 0)
    df['score_up_1'] = np.where(np.equal(df.score_diff, 1), 1, 0)
    df['score_up_2'] = np.where(np.equal(df.score_diff, 2), 1, 0)
    df['score_up_3'] = np.where(np.equal(df.score_diff, 3), 1, 0)
    df['score_up_4'] = np.where(df.score_diff >= 4, 1, 0)

    df['wrist_shot'] = np.where(np.equal(df.event_detail, 'Wrist'), 1, 0)
    df['deflected_shot'] = np.where(np.equal(df.event_detail, 'Deflected'), 1, 0)
    df['tip_shot'] = np.where(np.equal(df.event_detail, 'Tip-In'), 1, 0)
    df['slap_shot'] = np.where(np.equal(df.event_detail, 'Slap'), 1, 0)
    df['backhand_shot'] = np.where(np.equal(df.event_detail, 'Backhand'), 1, 0)
    df['snap_shot'] = np.where(np.equal(df.event_detail, 'Snap'), 1, 0)
    df['wrap_shot'] = np.where(np.equal(df.event_detail, 'Wrap-around'), 1, 0)

    last_is_shot = np.equal(df.event_type_last, 'SHOT')
    last_is_miss = np.equal(df.event_type_last, 'MISS')
    last_is_block = np.equal(df.event_type_last, 'BLOCK')
    last_is_give = np.equal(df.event_type_last, 'GIVE')
    last_is_take = np.equal(df.event_type_last, 'TAKE')
    last_is_hit = np.equal(df.event_type_last, 'HIT')
    last_is_fac = np.equal(df.event_type_last, 'FAC')

    same_team_as_last = np.equal(df.same_team_last, 1)
    not_same_team_as_last = np.equal(df.same_team_last, 0)

    df['prior_shot_same'] = np.where((last_is_shot & same_team_as_last), 1, 0)
    df['prior_miss_same'] = np.where((last_is_miss & same_team_as_last), 1, 0)
    df['prior_block_same'] = np.where((last_is_block & same_team_as_last), 1, 0)
    df['prior_give_same'] = np.where((last_is_give & same_team_as_last), 1, 0)
    df['prior_take_same'] = np.where((last_is_take & same_team_as_last), 1, 0)
    df['prior_hit_same'] = np.where((last_is_hit & same_team_as_last), 1, 0)

    df['prior_shot_opp'] = np.where((last_is_shot & not_same_team_as_last), 1, 0)
    df['prior_miss_opp'] = np.where((last_is_miss & not_same_team_as_last), 1, 0)
    df['prior_block_opp'] = np.where((last_is_block & not_same_team_as_last), 1, 0)
    df['prior_give_opp'] = np.where((last_is_give & not_same_team_as_last), 1, 0)
    df['prior_take_opp'] = np.where((last_is_take & not_same_team_as_last), 1, 0)
    df['prior_hit_opp'] = np.where((last_is_hit & not_same_team_as_last), 1, 0)

    df['prior_face'] = np.where(last_is_fac, 1, 0)

    ##prep final dataframe
    ['4v3', '4v4', '4v5', '4v6', '5v5', '5v4', '5v3', '6v4', '6v5', '6v3']

    ue_col_list = ['is_goal', 'shot_distance', 'shot_angle', 'is_home', 'state_4v3', 'state_4v4', 'state_4v5', 'state_4v6',
                   'state_5v5', 'state_5v4', 'state_5v3', 'state_6v4', 'state_6v5', 'state_6v3',
                    'score_down_4', 'score_down_3', 'score_down_2', 'score_down_1', 
                    'score_even', 'score_up_1', 'score_up_2', 'score_up_3', 'score_up_4', 'game_seconds', 
                    'period', 'coords_x', 'coords_y', 'coords_x_last', 'coords_y_last', 'wrist_shot', 
                    'deflected_shot', 'tip_shot', 'slap_shot', 'backhand_shot', 'snap_shot', 'wrap_shot', 
                    'distance_from_last', 'seconds_since_last', 'prior_shot_same', 'prior_miss_same', 
                    'prior_block_same', 'prior_give_same', 'prior_take_same', 'prior_hit_same', 
                    'prior_shot_opp', 'prior_miss_opp']            

    df = df[ue_col_list].astype('float').astype('int')

    return df

def target_split(df, target_col):
    '''Splits df in target and non-target'''


    col_list = []
    
    for column in df.columns:
        if column != target_col:
            col_list.append(column)
    
    X = df[col_list].copy()

    y = df['is_goal'].copy()

    return X, y

############################################## Function to predict goals ##############################################

def predict_goals(pbp):
    '''
    Docstring
    
    Parameters
    
    '''

    ev_file = pkg_resources.resource_stream(__name__, 'models/even_strength_model.pickle')
    pp_file = pkg_resources.resource_stream(__name__, 'models/power_play_model.pickle')
    sh_file = pkg_resources.resource_stream(__name__, 'models/short_handed_model.pickle')
    en_file = pkg_resources.resource_stream(__name__, 'models/empty_net_model.pickle')
    ue_file = pkg_resources.resource_stream(__name__, 'models/uneven_model.pickle')

    
    #ev_file = os.path.join('models', 'even_strength_model.pickle')
    #pp_file = os.path.join('models', 'power_play_model.pickle')
    #sh_file = os.path.join('models', 'short_handed_model.pickle')
    #en_file = os.path.join('models', 'empty_net_model.pickle')
    #ue_file = os.path.join('models', 'uneven_model.pickle')
    
    #EV_MODEL = pickle.load(open(ev_file, 'rb'))
    #PP_MODEL = pickle.load(open(pp_file, 'rb'))
    #SH_MODEL = pickle.load(open(sh_file, 'rb'))
    #EN_MODEL = pickle.load(open(en_file, 'rb'))
    #UE_MODEL = pickle.load(open(ue_file, 'rb'))

    EV_MODEL = pd.read_pickle(ev_file)
    PP_MODEL = pd.read_pickle(pp_file)
    SH_MODEL = pd.read_pickle(sh_file)
    EN_MODEL = pd.read_pickle(en_file)
    UE_MODEL = pd.read_pickle(ue_file)
    
    model_df = xG_prep(pbp)

    ev_df = xG_prep_EV(model_df)

    pp_df = xG_prep_PP(model_df)

    sh_df = xG_prep_SH(model_df)

    en_df = xG_prep_EN(model_df)

    ue_df = xG_prep_UE(model_df)
    
    CONCAT_LIST = list()
    
    big_dict = {'ev': {'data': ev_df, 'model': EV_MODEL},
                'pp': {'data': pp_df, 'model': PP_MODEL},
                'sh': {'data': sh_df, 'model': SH_MODEL},
                'en': {'data': en_df, 'model': EN_MODEL},
                'ue': {'data': ue_df, 'model': UE_MODEL}}
    
    for strength, df_dict in big_dict.items():
        
        df = df_dict['data']

        if df.empty:

            continue
        
        model = df_dict['model']
        
        X, y = target_split(df, 'is_goal')
        
        new_cols = {0:'pred_no_goal', 1: 'pred_goal'}
        
        X['pred_goal'] = pd.DataFrame(model.predict_proba(X), index = X.index).rename(columns = new_cols).pred_goal
        
        #X = X.join(predictions.pred_goal)
        
        CONCAT_LIST.append(X.pred_goal)
        
        #display(X.pred_goal)
        
    predictions = pd.concat(CONCAT_LIST)
    
    pbp = pbp.join(predictions)
    
    return pbp
    


