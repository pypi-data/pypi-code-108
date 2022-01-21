############################################## Introduction ##############################################

# Welcome to the chicken_nhl scraper functions

# The two most important functions are: (1) scrape_schedule; and (2) scrape_pbp
# The play-by-play function takes game IDs, which can be sourced using the schedule scraper

############################################## Dependencies ##############################################

import requests
import pandas as pd
import numpy as np
import time
import sys
from datetime import datetime
from bs4  import BeautifulSoup
import re
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from requests import ConnectionError, ReadTimeout, ConnectTimeout, HTTPError, Timeout

# These are dictionaries of names that are used throughout the module
from chickenstats.chicken_nhl.player_names import correct_names_dict, goalie_names, api_names_dict

############################################## Requests functions & classes ##############################################

# This function & the timeout class are used for scraping throughout

class TimeoutHTTPAdapter(HTTPAdapter):
    
    def __init__(self, *args, **kwargs):
        
        self.timeout = 3

        if "timeout" in kwargs:

            self.timeout = kwargs["timeout"]

            del kwargs["timeout"]

        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):

        timeout = kwargs.get("timeout")

        if timeout is None:

            kwargs["timeout"] = self.timeout

        return super().send(request, **kwargs)

def s_session():
    '''Creates a requests Session object using the HTTPAdapter from above'''

    s = requests.Session()
    
    retry = Retry(total = 5, backoff_factor = 2, status_forcelist=[60, 401, 403, 404, 408, 429, 500, 502, 503, 504])
    
    adapter = TimeoutHTTPAdapter(max_retries = retry, timeout = 3)
    
    s.mount('http://', adapter)
    
    s.mount('https://', adapter)
    
    return s

############################################## General helper functions ##############################################

# These are used in other functions throughout the module

def scrape_live_endpoint(game_id, session):
    '''Scrapes the live NHL API endpoint. Used to prevent multiple hits to same endpoint during PBP scrape'''

    s = session
    
    url = f'https://statsapi.web.nhl.com/api/v1/game/{game_id}/feed/live'
    
    response = s.get(url).json()
    
    return response

def convert_to_list(obj):
    '''If the object is not a list, converts the object to a list of length one'''
    
    if type(obj) is not list and type(obj) is not pd.Series:
        
        obj = [obj]
    
    return obj

def hs_strip_html(td):
    """
    Function from Harry Shomer's Github, which I took from Patrick Bacon
    
    Strip html tags and such 
    
    :param td: pbp
    
    :return: list of plays (which contain a list of info) stripped of html
    """
    for y in range(len(td)):
        # Get the 'br' tag for the time column...this get's us time remaining instead of elapsed and remaining combined
        if y == 3:
            td[y] = td[y].get_text()   # This gets us elapsed and remaining combined-< 3:0017:00
            index = td[y].find(':')
            td[y] = td[y][:index+3]
        elif (y == 6 or y == 7) and td[0] != '#':
            # 6 & 7-> These are the player 1 ice one's
            # The second statement controls for when it's just a header
            baz = td[y].find_all('td')
            bar = [baz[z] for z in range(len(baz)) if z % 4 != 0]  # Because of previous step we get repeats...delete some

            # The setup in the list is now: Name/Number->Position->Blank...and repeat
            # Now strip all the html
            players = []
            for i in range(len(bar)):
                if i % 3 == 0:
                    try:
                        name = return_name_html(bar[i].find('font')['title'])
                        number = bar[i].get_text().strip('\n')  # Get number and strip leading/trailing newlines
                    except KeyError:
                        name = ''
                        number = ''
                elif i % 3 == 1:
                    if name != '':
                        position = bar[i].get_text()
                        players.append([name, number, position])

            td[y] = players
        else:
            td[y] = td[y].get_text()

    return td

# The remaining functions are for printing messages and various parts of the progressbar

def print_progressbar(percent, message_text, n_bar = 25):
    '''Prints the progressbar. Used within other progressbar functions'''
    
    print_message = f"\r[{'=' * int(n_bar * percent):{n_bar}s}] {int(100 * percent)}%  {message_text}"
    
    sys.stdout.write('\r')

    sys.stdout.write(' ' * len(range(150)))

    sys.stdout.write(print_message)

    sys.stdout.flush()

def scrape_start_bar(number_of_games, n_bar = 25, message_text = None):
    '''Prints the beginning of the progress bar'''

    if number_of_games > 1:
        
        number = 'games'
        
    else:
        
        number = 'game'
        
    if message_text == None:
    
        message_text = f'Starting scrape of {number_of_games} {number}...'
            
    print_message = f"\r[{'=' * int(n_bar * 0):{n_bar}s}] {0}%  {message_text}"

    sys.stdout.write('\r')

    sys.stdout.write(' ' * len(range(150)))

    sys.stdout.write(print_message)

    sys.stdout.flush()
    
def schedule_start_bar(number_of_seasons, n_bar = 25, message_text = None):
    '''Prints the beginning of the progress bar for the schedule_scrape() function'''

    if number_of_seasons > 1:
        
        number = 'seasons'
        
    else:
        
        number = 'season'
        
    if message_text == None:
    
        message_text = f'Starting scrape of {number_of_seasons} {number}...'
            
    print_message = f"\r[{'=' * int(n_bar * 0):{n_bar}s}] {0}%  {message_text}"

    sys.stdout.write('\r')

    sys.stdout.write(' ' * len(range(150)))

    sys.stdout.write(print_message)

    sys.stdout.flush()
    
def print_concat_start(number_of_games, scrape_start, n_bar = 25):
    '''Prints the progress bar to the console when concatenating games, if scraping more than 500 games'''

    if number_of_games > 500:
        
        timer = round(time.perf_counter() - scrape_start, 2)
        
        if timer > 60:
        
            message_text = f'Finishing scraping {number_of_games} games in {round(timer / 60, 2)} minutes. Starting concatenation...'
            
        else:
            
            message_text = f'Finishing scraping {number_of_games} games in {timer} seconds. Starting concatenation...'
            
        print_message = f"\r[{'=' * int(n_bar * 1):{n_bar}s}] {100}%  {message_text}"
        
        sys.stdout.write('\r')

        sys.stdout.write(' ' * len(range(150)))

        sys.stdout.write(print_message)

        sys.stdout.flush()
        
def print_concat_finish(concat_start, number_of_games, n_bar = 25):
    '''Prints the progress bar to the console when concatenating games, if scraping more than 500 games'''
    
    timer = round(time.perf_counter() - concat_start, 2)

    message = 'Finished concatenating in '
    
    if number_of_games > 500:
    
        if timer > 60:

            message_text = message + f'{round(timer / 60, 2)} minutes...'

        else:

            message_text = message + f'{timer} seconds...'
        
        print_message = f"\r[{'=' * int(n_bar * 1):{n_bar}s}] {100}%  {message_text}"
        
        sys.stdout.write('\r')

        sys.stdout.write(' ' * len(range(150)))

        sys.stdout.write(print_message)

        sys.stdout.flush()
        
        ## Because this always ends the scrape, this prints the completed progress bar
        message_text = 'Scrape complete'

        print_message = f"\r[{'=' * int(n_bar * 1):{n_bar}s}] {100}%  {message_text}"

        sys.stdout.write('\r')

        sys.stdout.write(' ' * len(range(150)))

        sys.stdout.write(print_message)

        sys.stdout.flush()

def convert_ids(api_game_id):
    '''Takes an NHL API ID and converts it to an HTML season and game ID'''

    html_season_id = str(int(str(api_game_id)[:4])) + str(int(str(api_game_id)[:4]) + 1)
    
    html_game_id = str(api_game_id)[5:]
    
    return html_season_id, html_game_id

def print_game_id_time(game_start, game_id, number_of_games, game_number, message_text = None):
    '''Prints the progressbar after scraping each game'''

    timer = round(time.perf_counter() - game_start, 2)
    
    percent = game_number / number_of_games
    
    n_bar = 25
    
    if message_text == None:
    
        message_text = f'Finished scraping {game_id} in {timer} seconds ({game_number}/{number_of_games})...'

    print_progressbar(percent, message_text, n_bar)
    
    if percent == 1:
        
        if number_of_games <= 500:
            
            message_text = 'Scrape complete'
            
            print_message = f"\r[{'=' * int(n_bar * 1):{n_bar}s}] {100}%  {message_text}"

            sys.stdout.write('\r')

            sys.stdout.write(' ' * len(range(150)))

            sys.stdout.write(print_message)

            sys.stdout.flush()
    
def print_season_time(season_start, season, number_of_seasons, season_number, n_bar = 25):
    '''Prints the amount of time the season takes to scrape when scraping from the schedule'''

    timer = round(time.perf_counter() - season_start, 2)
    
    n = season_number
    
    percent = season_number / number_of_seasons
    
    n_bar = 25
    
    message_text = f'Finished scraping {season}-{season + 1} season in {timer} seconds ({season_number}/{number_of_seasons})...'

    print_progressbar(percent, message_text, n_bar) 
    
    if percent == 1:
        
        message_text = 'Scrape complete'

        print_message = f"\r[{'=' * int(n_bar * 1):{n_bar}s}] {100}%  {message_text}"

        sys.stdout.write('\r')

        sys.stdout.write(' ' * len(range(150)))

        sys.stdout.write(print_message)

        sys.stdout.flush()

def print_scrape_intro(number_of_games, scrape_type):
    '''Prints the introduction for the beginning of the scrape'''
    
    current_time = datetime.now().strftime("%H:%M")

    if number_of_games > 1:

        number = 'games'

    else:

        number = 'game'

    return print(f'Starting {scrape_type} scrape for {number_of_games} {number} at {current_time}\n')

def end_timer(time_difference, message):
    '''Converts the end time to minutes or seconds for printing to console'''

    if time_difference > 60:
        
        return print(message.strip() + f' {round(time_difference / 60, 2)} minutes\n')
    
    else:
        
        return print(message.strip() + f' {round(time_difference, 2)} seconds\n')

def print_number_of_games(number_of_games, scrape_start):
    '''Print the time the number of games takes to scrape'''

    timer = round(time.perf_counter() - scrape_start, 2)
    
    if number_of_games > 1:

        number = 'games'

    else:

        number = 'game'
        
    message = f'\n\nFinished scraping {number_of_games} {number} in '

    if timer > 60:

        print(message + f'{round(timer / 60, 2)} minutes\n')

    else:

        print(message + f'{timer} seconds\n')

############################################## Schedule ##############################################

def scrape_schedule(seasons, game_types = ['R', 'P'], today_only = False, final_only = False, 
                        live_only = False, teams = None, _print = True):
    
    '''
    Scrapes the NHL schedule API. Returns a dataframe


    Parameters:

        seasons: a year as an integer, or list of years as integers

        game_types: list; default: ['R', 'P']
            Determines the types of games that are returned. Not all game types are supported or have adequate data.
            The following are available:
            'R': regular season
            'P': playoffs
            'PR': preseason (not supported)
            'A': all star game (not supported)

        today_only: boolean; default: False
            If True, scrapes only the games from today's date, determined by system time

        final_only: boolean; default: True
            If True, scrapes only the games that have finished

        live_only: boolean; default: False
            If True, scrapes only live games

        _print: boolean; default: True
            If True, prints progress to the console
    '''
    
    ## TO DO:
    ## 1. add today_only as an argument for the function
    ## 2. Ensure columns returned are in the correct order
    ## 3. Add comments and update doc string
    
    ## Start time for timer purposes
    scrape_start = time.perf_counter()
    
    ## Starting requests session
    s = s_session()
    
    ## Create list of season IDs. If single season, convert to a list of a single season ID. Else, use list comprehension to convert to season IDs
    seasons = convert_to_list(seasons)
    
    number_of_seasons = len(seasons)
        
    ## Printing start time if printing is enabled
    if _print == True:

        current_time = datetime.now().strftime("%H:%M")
        
        if number_of_seasons > 1:
            
            number = 'seasons'
            
        else:
            
            number = 'season'
            
        print(f'Getting schedulue for {number_of_seasons} {number}. Scrape started at {current_time}\n')
        
        schedule_start_bar(number_of_seasons)
    
    
    ## Create blank dataframe to hold all schedules scraped
    season_dfs = []
    
    ## Loop through season IDs and scrape schedule data for each season
    for season_idx, season in enumerate(seasons):
        
        season_number = season_idx + 1
        
        if season == 2004:
            
            continue
        
        ## Create season ID for each season
        season_id = str(int(season)) + str(int(season) + 1)       
        
        ## Start time for timer purposes
        season_start = time.perf_counter()

        if today_only == True:
            
            today = datetime.today().strftime('%Y-%m-%d')
            
            url = f'https://statsapi.web.nhl.com/api/v1/schedule?date={today}'
            
            response = s.get(url).json()
        
        ## Setting url and calling JSON from API
        else:
            
            url = f'https://statsapi.web.nhl.com/api/v1/schedule?season={season_id}'

            response = s.get(url, timeout = 1).json()
        
        ## Setting up initial season schedule dataframe
        season_df = pd.json_normalize(response['dates'], record_path = 'games', sep = '_')

        season_df['season'] = season_id
        
        ## Removing game types based on function argument. Game types dictionary is function argument.
        ## By default, only regular season and playoff game types are included
        
        if game_types != 'all':
            
            season_df = season_df[np.isin(season_df.gameType, game_types)].copy()
        
        ## Removing unfinished/unplayed games from sched sule information. By default live games are included
        if final_only == True:
            
            season_df = season_df[season_df.status_abstractGameState == 'Final'].copy()
            
        if live_only == True:
            
            season_df = season_df[season_df.status_abstractGameState == 'Live'].copy()
        
        season_df.teams_away_team_name = season_df.teams_away_team_name.str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8').str.upper()

        season_df.teams_home_team_name = season_df.teams_home_team_name.str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8').str.upper()

        season_df = season_df.replace({'PHOENIX COYOTES': 'ARIZONA COYOTES'}, regex = False)

        if teams != None:

            teams = convert_to_list(teams)

            mask = np.logical_or(np.isin(season_df.teams_home_team_name, teams), np.isin(season_df.teams_away_team_name, teams))

            season_df = season_df[mask].copy()

        season_df.gameDate = pd.to_datetime(season_df.gameDate).dt.tz_convert('US/Eastern').dt.date

        ## Adding individual season schedule to big schedule dataframe
        season_dfs.append(season_df.convert_dtypes())
        
        ## Printing timer for each season if print is True
        if _print == True:
            
            print_season_time(season_start, season, number_of_seasons, season_number)
            
            #print(f'Finished with {season} schedule in {timer} seconds...')
    
    df = pd.concat(season_dfs, ignore_index = True)
    
    ## Changing column names using dictionary and rename function
    new_cols = {'gamePk' : 'game_id',
                'gameType' : 'game_type',
                'link' : 'game_link',
                'gameDate' : 'game_date',
                'status_abstractGameState' : 'game_status',
                'status_detailedState' : 'detailed_game_status',
                'status_startTimeTBD' : 'start_time_TBD',
                'teams_away_leagueRecord_wins' : 'away_team_wins',
                'teams_away_leagueRecord_losses' : 'away_team_losses',
                'teams_away_leagueRecord_ties': 'away_team_ties',
                'teams_away_leagueRecord_ot' : 'away_team_OTL',
                'teams_away_score' : 'away_team_score',
                'teams_away_team_id' : 'away_team_id',
                'teams_away_team_name' : 'away_team_name',
                'teams_away_team_link' : 'away_team_link',
                'teams_home_leagueRecord_wins' : 'home_team_wins',
                'teams_home_leagueRecord_losses' : 'home_team_losses',
                'teams_home_leagueRecord_ot' : 'home_team_OTL',
                'teams_home_leagueRecord_ties': 'home_team_ties',
                'teams_home_score' : 'home_team_score',
                'teams_home_team_id' : 'home_team_id',
                'teams_home_team_name' : 'home_team_name',
                'teams_home_team_link' : 'home_team_link',
                'content_link' : 'game_content_link', 
                'status_statusCode': 'status_code'}

    df.rename(columns = new_cols, inplace = True)
    
    ## Separating game date column into start time, then making game date a date
    df['start_time'] = pd.to_datetime(df.game_date).dt.time
    
    ## Dropping columns that we don't want
    
    columns = ['season', 'game_id', 'game_date', 'game_type', 'game_status', 'home_team_name', 'home_team_score',
               'away_team_name', 'away_team_score', 'detailed_game_status', 'start_time', 'start_time_TBD', 'home_team_wins',
               'home_team_losses', 'home_team_ties', 'home_team_OTL', 'away_team_wins', 'away_team_losses', 'away_team_OTL',
               'home_team_id', 'home_team_link', 'away_team_id', 'away_team_link', 'venue_name', 'venue_id',
               'venue_link', 'game_link', 'game_content_link', 'status_code']
    
    columns = [x for x in columns if x in df.columns]
    
    df = df[columns].convert_dtypes()
    
    
    ## Printing timer for whole scrape if printing is enabled
    if _print == True:
        
        timer = round(time.perf_counter() - scrape_start, 2)
    
        print(f'\n\nFinished with schedule scrape in {timer} seconds\n')
        
    return df

############################################## Game info ##############################################

def scrape_game_info(game_ids, response_data = None, _print = True, session = None):
    '''
    Scrapes the game information from the API for a given game ID or list of game IDs. Returns a dataframe
    

    Parameters:
    game_ids: a single API game ID (e.g., 2021020001) or list of game IDs

    response: JSON object; default: None
        When using in another scrape function, can pass the live endpoint response as a JSON object to prevent redundant hits

    _print: boolean; default: True
        If True, prints progress to the console

    session: requests Session object; default = None
        When using in another scrape function, can pass the requests session to improve speed
    '''
    
    ## TO DO:
    ## 1. add comments and edit docstring
    ## 2. ensure columns returned are in the right order
    
    ## Starting timer for scrape start
    scrape_start = time.perf_counter()
    
    ## Convert game IDs to list if given a single game ID
    game_ids = convert_to_list(game_ids)
    
    number_of_games = len(game_ids)

    if _print == True:
    
        print_scrape_intro(number_of_games, 'API game info')
        
        scrape_start_bar(number_of_games)
    
    ## Important lists
    bad_game_list = list()
    concat_list = list()
    
    if response_data == None:
        
        if session == None:
        
            s = s_session()
            
        else:
            
            s = session
    
    for game_id_idx, game_id in enumerate(game_ids):
        
        game_start = time.perf_counter()
        
        game_number = game_id_idx + 1
            
        #if np.logical_or(response == None, number_of_games > 1):
        if response_data == None:
            
            response = s.get(f'https://statsapi.web.nhl.com/api/v1/game/{game_id}/feed/live').json()

        else:

            response = response_data
        
        if response['gameData'] == []:
                
            bad_game_list.append(game_id)
            
            response = None
            
            continue
        
        info_list = list()
        
        for key in response['gameData'].keys():
            
            info = pd.json_normalize(response['gameData'][key], sep = '_')

            if key == 'game':

                column_names = {'pk': 'game_id', 'type': 'game_type'}

                info = info.rename(columns = column_names)

                info_list.append(info)

            if key == 'datetime':

                column_names = {'dateTime': 'game_start_time', 'endDateTime': 'game_end_time'}

                info = info.rename(columns = column_names)
                
                #info['game_date'] = pd.to_datetime(info.game_start_time, format = '%Y-%m-%d').dt.date

                info_list.append(info)

            if key == 'venue':

                column_names = {'id': 'game_venue_id', 'name': 'game_venue_name', 'link': 'game_venue_link'}

                info = info.rename(columns = column_names)

                info_list.append(info)
        
        info_df = pd.concat(info_list, axis = 1)
        
        ## Creating initial teams dataframe
        teams_dict = dict()
                
        for key in response['gameData']['teams'].keys():

            team_df = pd.json_normalize(response['gameData']['teams'][key], sep = '_')

            column_names = {'id': 'team_id', 'name': 'team_name', 'link': 'team_link', 'abbreviation': 'team_abbr', 'triCode': 'team_tri_code',
                            'teamName': 'team_mascot', 'locationName': 'team_location', 'firstYearOfPlay': 'team_first_year_of_play',
                            'shortName': 'team_short_name', 'officialSiteUrl': 'team_site_url', 'franchiseId': 'team_franchise_id',
                            'active': 'team_franchise_active', 'venue_id': 'team_venue_id', 'venue_name': 'team_venue_name',
                            'venue_link': 'team_venue_link', 'venue_city': 'team_venue_city', 'venue_timeZone_id': 'team_venue_tz_id',
                            'venue_timeZone_offset': 'team_venue_tz_offset', 'venue_timeZone_tz': 'team_venue_tz_name',
                            'division_id': 'team_division_id', 'division_name': 'team_division_name', 'division_link': 'team_division_link',
                            'conference_id': 'team_conference_id', 'conference_name': 'team_conference_name', 'conference_link': 'team_conference_link', 
                            'franchise_link': 'team_franchise_link', 'franchise_teamName': 'team_franchise_mascot', 'division_nameShort': 'team_div_short_name'}

            team_df = team_df.rename(columns = column_names).drop('franchise_franchiseId', axis = 1)

            team_df.team_name = team_df.team_name.str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8').str.upper()

            team_df.team_name = np.where(team_df.team_name == 'PHOENIX COYOTES', 'ARIZONA COYOTES', team_df.team_name)

            team_df.team_abbr = np.where(team_df.team_abbr == 'PHX', 'ARI', team_df.team_abbr)

            team_df.team_tri_code = np.where(team_df.team_tri_code == 'PHX', 'ARI', team_df.team_tri_code)

            team_df['status'] = key

            teams_dict.update({key: team_df})

        teams_list = list()

        merge_dict = {'home': 'away', 'away': 'home'}

        for key, value in merge_dict.items():

            column_names = {x: 'opp_' + x for x in teams_dict[value].columns}
            
            teams_list.append(teams_dict[key].merge(teams_dict[value].rename(columns = column_names),
                                                    left_index = True, right_index = True))
            
        teams_df = pd.concat(teams_list)
        
        teams_df = pd.concat([info_df, teams_df], axis = 1).reset_index(drop = True)

        teams_df['game_id'] = game_id
        
        teams_df['season'] = str(game_id)[:4] + str(int(str(game_id)[:4]) + 1)

        concat_list.append(teams_df)
        
        response = None
        
        if _print == True:
            
            print_game_id_time(game_start, game_id, number_of_games, game_number)
    
    if concat_list != []:
    
        concat_start = time.perf_counter()
        
        if _print == True:
            
            print_concat_start(number_of_games, scrape_start)

        game_info = pd.concat(concat_list, ignore_index = True)
        
        if _print == True:
                
            print_concat_finish(concat_start, number_of_games)
            
    if _print == True:
        
        print_number_of_games(number_of_games, scrape_start)
    
    if concat_list == []:
        
        return pd.DataFrame()
    
    else:
        
        return game_info

############################################## HTML rosters ##############################################

def scrape_html_rosters(game_ids, _print = True, session = None):
    '''
    Scrapes the rosters from the HTML endpoint
    
    Used within the main play-by-play scraper
    Parameters:
    game_ids: a single API game ID (e.g., 2021020001) or list of game IDs

    _print: boolean; default: True
        If True, prints progress to the console

    session: requests Session object; default = None
        When using in another scrape function, can pass the requests session to improve speed
    '''
    
    ## TO DO:
    ## 1. add comments and edit docstring
    ## 2. ensure columns returned make sense
    
    scrape_start = time.perf_counter()
    
    game_ids = convert_to_list(game_ids)
    
    number_of_games = len(game_ids)
    
    if _print == True:
        
        print_scrape_intro(number_of_games, 'HTML rosters')
        
        scrape_start_bar(number_of_games)
    
    if session == None:
    
        s = s_session()
        
    else:
        
        s = session
    
    html_list = []
    
    for game_id_idx, game_id in enumerate(game_ids):
        
        game_start = time.perf_counter()
        
        game_number = game_id_idx + 1
        
        html_season_id, html_game_id = convert_ids(game_id)
    
        html_url = f'http://www.nhl.com/scores/htmlreports/{html_season_id}/RO0{html_game_id}.HTM'
        
        page = s.get(html_url)
        
        page_status = page.status_code
        
        if page_status == 404:
            
            if _print == True:

                    message_text = f'Sorry, {game_id} was not available from the source...'

                    print_game_id_time(game_start, game_id, number_of_games, game_number, message_text = message_text)
            
            continue
            
        soup = BeautifulSoup(page.content.decode('ISO-8859-1'), 'lxml', multi_valued_attributes = None)

        td_dict = {'align':'center', 'class':['teamHeading + border', 'teamHeading + border '], 'width':'50%'}

        teamsoup = soup.find_all('td', td_dict)

        table_dict = {'align':'center', 'border':'0', 'cellpadding':'0', 'cellspacing':'0', 'width':'100%', 'xmlns:ext':''}

        team_names = {}

        team_soup_list = []

        team_list = ['away', 'home']

        html_roster_list = []

        for idx, team in enumerate(team_list):

            team_names.update({team : teamsoup[idx].get_text()})

            team_soup_list.append((soup.find_all('table', table_dict))[idx].find_all('td'))

        for idx, team_soup in enumerate(team_soup_list):

            length = int(len(team_soup) / 3)

            df = pd.DataFrame(np.array(team_soup).reshape(length, 3))

            df.columns = df.iloc[0]

            df = df.assign(team = team_list[idx], team_full_name = team_names.get(team_list[idx]), status = 'active').drop(0)

            html_roster_list.append(df)

        if len(soup.find_all('table', table_dict)) > 2:

            scratch_soups = []

            for idx, team in enumerate(team_list):

                team_scratch = (soup.find_all('table', table_dict))[idx + 2].find_all('td')

                if len(team_scratch) > 1:

                    length = int(len(team_scratch) / 3)

                    df = pd.DataFrame(np.array(team_scratch).reshape(length, 3))

                    df.columns = df.iloc[0]

                    df = df.assign(team = team_list[idx], team_full_name = team_names.get(team_list[idx]), status = 'scratch').drop(0)

                    html_roster_list.append(df)

                else:

                    html_roster_list.append(pd.DataFrame())

        html_game_df = pd.concat(html_roster_list, ignore_index = True)

        html_game_df['game_id'] = game_id

        html_game_df['season'] = html_season_id

        html_game_df['team'] = np.where(html_game_df.team == 'CANADIENS MONTREAL', 'MONTREAL CANADIENS', html_game_df.team)

        ## Rename columns
        new_cols = {'#' : 'player_jersey',
                    'Pos' : 'player_position',
                    'status' : 'player_status',
                    'Nom/Name' : 'player_name',
                    'Name' : 'player_name'}

        html_game_df.rename(columns = new_cols, inplace = True)

        if 'player_name' not in list(html_game_df.columns):

            if _print == True:

                print(f'Sorry, {game_id} does not have any player information')

            continue

        if 'player_position' not in list(html_game_df.columns):

            html_game_df['player_position'] = np.nan

        #html_game_df.player_position = html_game_df.player_position.map(positions_dict).fillna(html_game_df.player_position)

        ## Full names, then fixing
        html_game_df.player_name = html_game_df.player_name.str.split('(').str[0].str.strip()
        
        html_game_df.player_name = html_game_df.player_name.str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8').str.upper()

        # Max Pacioretty doesn't exist in ESPN in 2009-2010, sadly.
        replace_dict = {'AlEXANDRE ' : 'ALEX ',
                        'ALEXANDER ' : 'ALEX ',
                        'CHRISTOPHER ' : 'CHRIS ',
                        'DE LEO': 'DELEO',
                       }

        for old_name, new_name in replace_dict.items():

            html_game_df.player_name = html_game_df.player_name.str.replace(old_name, new_name, regex = False, case = False)

        # List of names and fixed from Evolving Hockey Scraper.
        html_game_df.player_name = html_game_df.player_name.map(correct_names_dict).fillna(html_game_df.player_name)

        player_names = ['player_first_name', 'player_last_name']

        for idx, player_name in enumerate(player_names):

            html_game_df[player_name] = html_game_df.player_name.str.split(' ', 1).str[idx]

        html_game_df['api_name'] = html_game_df.player_first_name + '.' + html_game_df.player_last_name


        double_names_fix = {'SEBASTIAN.AHO2' : [html_game_df.api_name == 'SEBASTIAN.AHO', html_game_df.player_position == 'D'],
                            'COLIN.WHITE2': [html_game_df.api_name == 'COLIN.WHITE', int(html_season_id) >= 20162017], 
                            'SEAN.COLLINS2' : [html_game_df.api_name == 'SEAN.COLLINS', html_game_df.player_position != 'D'],
                            'ALEX.PICARD2' : [html_game_df.api_name == 'ALEX.PICARD', html_game_df.player_position != 'D'],
                            'ERIK.GUSTAFSSON2' : [html_game_df.api_name == 'ERIK.GUSTAFSSON', int(html_season_id) >= 20152016],
                            'MIKKO.LEHTONEN2' : [html_game_df.api_name == 'MIKKO.LEHTONEN', int(html_season_id) >= 20202021]}

        for fix, conditions in double_names_fix.items():

            html_game_df.api_name = np.where(np.logical_and(conditions[0], conditions[1]), fix, html_game_df.api_name)

        html_game_df.api_name = np.where(html_game_df.api_name == 'COLIN.', 'COLIN.WHITE2', html_game_df.api_name)

        html_list.append(html_game_df)

        if html_list == []:

            if _print == True:

                    message_text = f'Sorry, {game_id} does not have any player information...'

                    print_game_id_time(game_start, game_id, number_of_games, game_number, message_text = message_text)

        else:

            if _print == True:

                print_game_id_time(game_start, game_id, number_of_games, game_number)
    
    concat_start = time.perf_counter()
    
    if _print == True:
        
        print_concat_start(number_of_games, scrape_start)
    
    if html_list == []:
        
        html_df = pd.DataFrame()
        
    else:
        
        html_df = pd.concat(html_list, ignore_index = True)
        
        columns = ['season', 'game_id', 'team_full_name', 'team', 'player_name',
                   'player_first_name', 'player_last_name', 'api_name', 'player_jersey',
                   'player_position', 'player_status']
        
        columns = [x for x in columns if x in html_df.columns]
        
        html_df = html_df[columns]
        
    if _print == True:

        print_concat_finish(concat_start, number_of_games)

        print_number_of_games(number_of_games, scrape_start)
    
    return html_df

############################################## HTML shifts ##############################################

def scrape_html_shifts(game_ids, _print = True, roster_data = pd.DataFrame(), game_data = pd.DataFrame(), session = None, pbp = False, _live = False):
    '''
    Scrapes the shifts from the HTML endpoint. Returns a dictionary with the keys: 'shifts' & 'changes'
   
    Used within the main play-by-play scraper
    Parameters:
    game_ids: a single API game ID (e.g., 2021020001) or list of game IDs

    _print: boolean; default: True
        If True, prints progress to the console

    roster: dataframe; default: empty dataframe
        Can pass a dataframe of roster information to prevent re-scraping from the same endpoint.
        If empty, scrapes roster data from the HTML endpoint

    game_data: dataframe, or dataframe; default: empty dataframe
        Can pass a dataframe of game information to prevent re-scraping from the same endpoint.
        If empty, scrapes game information data from the API endpoint

    session: requests Session object; default = None
        When using in another scrape function, can pass the requests session to improve speed

    pbp: boolean; default: False
        If True, additional columns are added for use in the pbp scraper
    '''
    
    ## TO DO:
    ## 1. Add comments and doc string
    ## 2. Ensure columns returned make sense and are in the correct order
    ## 3. Move functionality from pbp scrape to here, but have as a return option
    ## 4. Add season column
    ## 5. TDH had some goalie thing in there that was fucking up my shifts? I think it was only meant for live games?
    
    
    ## Starting timer for scrape start
    scrape_start = time.perf_counter()
    
    ## Convert game IDs to list if given a single game ID
    game_ids = convert_to_list(game_ids)
    
    number_of_games = len(game_ids)
    
    if _print == True:
    
        print_scrape_intro(number_of_games, 'HTML shifts')
        
        scrape_start_bar(number_of_games)
    
    ## Important lists
    shifts_concat = list()
    changes_concat = list()
    
    scrape_dict = dict()
    
    if session == None:
    
        s = s_session()
        
    else:
        
        s = session

    for game_id_idx, game_id in enumerate(game_ids):
        
        game_start = time.perf_counter()
        
        game_number = game_id_idx + 1
        
        if game_data.empty:
            
            game_info = scrape_game_info(game_id, _print = False, session = s)
            
        else:
            
            game_info = game_data[game_data.game_id == game_id]

        GAME_SESSION = game_info.game_type.iloc[0]
            
        if roster_data.empty:
            
            roster = scrape_html_rosters(game_id, _print = False, session = s)
            
        else:
            
            roster = roster_data[roster_data.game_id == game_id]
            
        html_season_id, html_game_id = convert_ids(game_id)
        
        urls_dict = {'home': f'http://www.nhl.com/scores/htmlreports/{html_season_id}/TH0{html_game_id}.HTM',
                     'away': f'http://www.nhl.com/scores/htmlreports/{html_season_id}/TV0{html_game_id}.HTM'}
        
        concat_list = list()

        for team, url in urls_dict.items():

            response = requests.get(url)

            soup = BeautifulSoup(response.content.decode('ISO-8859-1'), 'lxml', multi_valued_attributes = None)

            team_name = soup.find('td', {'align':'center', 'class':'teamHeading + border'}).get_text()

            players = soup.find_all('td', {'class':['playerHeading + border', 'lborder + bborder']})
            
            players_dict = dict()

            for player in players:

                data = player.get_text()

                if ', ' in data:

                    name = data.split(',', 1)

                    number = name[0].split(' ')[0].strip()

                    last_name = name[0].split(' ', 1)[1].strip()

                    first_name = name[1].strip()

                    full_name = f'{first_name} {last_name}'

                    players_dict[full_name] = dict()

                    players_dict[full_name]['number'] = number

                    players_dict[full_name]['name'] = full_name

                    players_dict[full_name]['shifts'] = list()

                else:

                    players_dict[full_name]['shifts'].extend([data])

            for key in players_dict.keys():

                length = int(len(np.array(players_dict[key]['shifts'])) / 5)

                column_names = {0: 'shift_number', 1: 'period', 2: 'shift_start', 3: 'shift_end', 4: 'duration'}

                player_df = pd.DataFrame(np.array(players_dict[key]['shifts']).reshape(length, 5)).rename(columns = column_names)

                player_df['player_name'] = players_dict[key]['name']

                player_df['player_jersey'] = players_dict[key]['number']

                player_df['team'] = team_name

                player_df['venue'] = team

                concat_list.append(player_df)

        shifts_df = pd.concat(concat_list, ignore_index = True)

        shifts_df['start_time'] = shifts_df.shift_start.str.split('/').str[0]

        shifts_df['end_time'] = shifts_df.shift_end.str.split('/').str[0]

        shifts_df['period'] = np.where(shifts_df.period == 'OT', 4, shifts_df.period).astype(int)

        start_time_split = shifts_df.start_time.astype(str).str.split(':')
        duration_time_split = shifts_df.duration.astype(str).str.split(':')

        condition = ~shifts_df.shift_end.str.contains('\xa0')
        value = shifts_df.end_time
        default_value = (pd.to_datetime((60 * start_time_split.str[0].astype(int)) +
                                        (start_time_split.str[1].astype(int)) + 
                                        (60 * duration_time_split.str[0].astype(int)) +
                                        (duration_time_split.str[1].astype(int)), unit = 's').dt.time).astype(str).str[4:]

        shifts_df['end_time'] = np.where(condition, value, default_value)

        replace_dict = {'ALEXANDRE ': 'ALEX ', 'ALEXANDER ': 'ALEX ', 'CHRISTOPHER ': 'CHRIS ', 'DE LEO': 'DELEO'}
        
        for old_name, new_name in replace_dict.items():
            
            shifts_df.player_name = shifts_df.player_name.str.replace(old_name, new_name, regex = False, case = False)

        shifts_df.player_name = shifts_df.player_name.map(correct_names_dict).fillna(shifts_df.player_name)
        
        shifts_df['api_name'] = shifts_df.player_name.str.normalize('NFKD').str.encode('ascii', errors='ignore').str\
                                    .decode('utf-8').str.upper()
        
        shifts_df['position'] = np.nan
        
        team_types = ['home', 'away']
        
        for team in team_types:
            
            mask = roster.team == team
            
            player_names_dict = dict(zip(roster[mask].player_name, roster[mask].api_name))
            
            positions_dict = dict(zip(roster[mask].api_name, roster[mask].player_position))
            
            shifts_df.api_name = np.where(shifts_df.venue == team,
                                          shifts_df.api_name.map(player_names_dict).fillna(shifts_df.api_name),
                                          shifts_df.api_name)
            
            shifts_df.position = np.where(shifts_df.venue == team, 
                                          shifts_df.api_name.map(positions_dict).fillna(shifts_df.position), 
                                          shifts_df.position)

        condition = pd.to_datetime(shifts_df.start_time).dt.time > pd.to_datetime(shifts_df.end_time).dt.time
        value = '20:00'
        default_value = shifts_df.end_time

        shifts_df.end_time = np.where(condition, value, default_value)
        
        home_team_roster = roster[roster.team == 'home']
        away_team_roster = roster[roster.team == 'away']
        
        goalies = roster[roster.player_position == 'G'].player_name.to_list()

        shifts_df['goalie'] = np.where(shifts_df.player_name.isin(goalies), 1, 0)

        group_list = ['team', 'period']

        shifts_df['period_goalies'] = shifts_df.groupby(group_list)['goalie'].transform('sum')

        condition = (shifts_df.goalie == 1) & (shifts_df.start_time != '0:00') & (shifts_df.period_goalies == 1)
        value = '0:00'
        default_value = shifts_df.start_time

        ## TDH was doing something weird with the goalie shifts, I think it was the live fix from the EH scrape
        shifts_df.start_time = np.where(condition, value, default_value)

        cond_1 = ((pd.to_datetime(shifts_df.start_time).dt.time < datetime(2021, 6, 10, 18, 0, 0).time()) &
                  (shifts_df.period != 3) & 
                  (shifts_df.period != 4) & 
                  (shifts_df.goalie == 1) & 
                  (shifts_df.period_goalies == 1))

        value_1 = '20:00'

        cond_2 = ((pd.to_datetime(shifts_df.start_time).dt.time < datetime(2021, 6, 10, 13, 0, 0).time()) &
                  (shifts_df.period != 4) & 
                  (shifts_df.goalie == 1) &
                  (shifts_df.period_goalies == 1))

        value_2 = '20:00'

        conditions = [cond_1, cond_2]
        values = [value_1, value_2]

        ## Same thing, have commented out TDH goalies fix
        #shifts_df.end_time = np.select(conditions, values, shifts_df.end_time)

        shifts_df.start_time = shifts_df.start_time.str.strip()
        shifts_df.end_time = shifts_df.end_time.str.strip()

        columns = ['start_time', 'end_time', 'duration']

        for column in columns: 

            time_split = shifts_df[column].astype(str).str.split(':')

            shifts_df[f'{column}_seconds'] = 60 * time_split.str[0].astype(int) + time_split.str[1].astype(int)

        conds = (shifts_df.goalie != 1) & \
        (shifts_df.duration_seconds > 30) & \
        (shifts_df.start_time_seconds >= 1020) & \
        (np.logical_or(shifts_df.period <= 3, GAME_SESSION == 'P'))

        #shifts_df.end_time = np.where(conds, "20:00", shifts_df.end_time)

        #shifts_df.end_time_seconds = np.where(conds, 1200, shifts_df.end_time_seconds)
            
        mask = shifts_df.start_time != shifts_df.end_time
        
        shifts_df = shifts_df[mask].copy()

        group_dict = {'on': ['team', 'venue', 'period', 'start_time', 'start_time_seconds'], 
                      'off': ['team', 'venue', 'period', 'end_time', 'end_time_seconds']}

        times_dict = {'on': {'start_time': 'time'}, 
                      'off': {'end_time': 'time'}}

        changes_dict = dict()

        for change_type, group_list in group_dict.items():

            column_names = times_dict[change_type]

            sort_list = ['team', 'period', 'time']

            if change_type == 'on':

                df = shifts_df.groupby(group_list, as_index = False)\
                        .agg(players_on = ('player_name', tuple),
                             players_on_numbers = ('player_jersey', tuple),
                             players_on_api = ('api_name', tuple),
                             positions_on = ('position', tuple),
                             number_on = ('player_name', 'count'))\
                        .rename(columns = column_names)\
                        .sort_values(by = sort_list)

            if change_type == 'off':

                df = shifts_df.groupby(group_list, as_index = False)\
                        .agg(players_off = ('player_name', tuple),
                             players_off_numbers = ('player_jersey', tuple),
                             players_off_api = ('api_name', tuple),
                             positions_off = ('position', tuple),
                             number_off = ('player_name', 'count'))\
                        .rename(columns = column_names)\
                        .sort_values(by = sort_list)

            changes_dict.update({change_type: df.reset_index(drop = True)})

        merge_list = ['team', 'venue', 'period', 'time']

        changes_on = changes_dict['on'].merge(changes_dict['off'], on = merge_list, how = 'left')
        changes_off = changes_dict['off'].merge(changes_dict['on'], on = merge_list, how = 'left')

        changes_df = pd.concat([changes_on, changes_off], ignore_index = True)\
                            .sort_values(by = ['period', 'start_time_seconds'], ascending = True)\
                            .drop_duplicates().reset_index(drop = True)
        
        changes_df.start_time_seconds = changes_df.start_time_seconds.fillna(1200)
        
        changes_df.end_time_seconds = changes_df.end_time_seconds.fillna(0)
        
        changes_df = changes_df.sort_values(by = ['period', 'start_time_seconds'], ascending = True).reset_index(drop = True)

        time_split = changes_df.time.astype(str).str.split(':')

        changes_df['period_seconds'] = 60 * time_split.str[0].astype(int) + time_split.str[1].astype(int)

        changes_df['game_seconds'] = (changes_df.period - 1) * 1200 + changes_df.period_seconds
        
        changes_df.team == changes_df.team.str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8').str.upper()

        changes_df.team = np.where(changes_df.team=='CANADIENS MONTREAL', 'MONTREAL CANADIENS', changes_df.team)
        
        shifts_df['game_id'] = game_id
        shifts_df['season'] = str(game_id)[:4] + str(int(str(game_id)[:4]) + 1)
        
        changes_df['game_id'] = game_id
        changes_df['season'] = str(game_id)[:4] + str(int(str(game_id)[:4]) + 1)
        
        if pbp == True:

            changes_df['event'] = 'CHANGE'

            changes_df['description'] = 'Players on: ' + changes_df.players_on.str.join(', ') + \
                                                ' / Players off: ' + changes_df.players_off.str.join(', ')

            team_type_dict = dict(zip(game_info.status, game_info.team_tri_code))

            columns = ['event_team', 'home_team_abbr', 'away_team_abbr']

            changes_df['event_team'] = changes_df.venue.map(team_type_dict)

            changes_df['home_team_abbreviated'] = np.where(changes_df.venue == 'home', team_type_dict['home'], team_type_dict['away'])

            changes_df['away_team_abbreviated'] = np.where(changes_df.venue == 'away', team_type_dict['away'], team_type_dict['home'])

            team_name_df = changes_df[['event_team', 'team']].drop_duplicates()

            team_name_dict = dict(zip(team_name_df.event_team, team_name_df.team))

            team_types = ['home', 'away']

            for team in team_types:

                changes_df[team + '_team'] = changes_df[team + '_team_abbreviated'].map(team_name_dict)
        
        shifts_concat.append(shifts_df)
        
        changes_concat.append(changes_df)
        
        if _print == True:

            print_game_id_time(game_start, game_id, number_of_games, game_number)

    concat_start = time.perf_counter()
    
    if _print == True:
        
        print_concat_start(number_of_games, scrape_start)
        
    if shifts_concat == []:
        
        shifts_df = pd.DataFrame()
        
    else:
        
        shifts_df = pd.concat(shifts_concat, ignore_index = True)
        
        columns = ['season', 'game_id', 'team', 'venue', 'player_name', 'player_jersey', 'shift_number', 'period',
                   'shift_start', 'shift_end', 'duration', 'start_time', 'end_time', 'start_time_seconds',
                   'end_time_seconds', 'duration_seconds', 'api_name', 'goalie', 'position']
        
        columns = [x for x in columns if x in shifts_df.columns]
                   
        shifts_df = shifts_df[columns]
        
    if changes_concat == []:
        
        changes_df = pd.DataFrame()
        
    else:
        
        changes_df = pd.concat(changes_concat, ignore_index = True)
                   
        columns = ['season', 'game_id', 'team', 'venue', 'period', 'time', 'period_seconds',  'game_seconds', 'number_on',
                   'players_on', 'players_on_api', 'positions_on', 'number_off', 'players_off', 'players_off_api', 
                   'positions_off', 'players_on_numbers', 'players_off_numbers', 'event', 'description', 'event_team',
                   'home_team_abbreviated', 'away_team_abbreviated']
        
        columns = [x for x in columns if x in changes_df.columns]
        
        changes_df = changes_df[columns]
        
    if _print == True:
        
        print_concat_finish(concat_start, number_of_games)
        
    scrape_dict.update({'shifts': shifts_df, 
                       'changes': changes_df})
    
    if _print == True:
        
        print_number_of_games(number_of_games, scrape_start)
    
    return scrape_dict

############################################## API events ##############################################

def scrape_api_events(game_ids, response_data = None, game_data = pd.DataFrame(), session = None, _print = True):
    '''
    Scrapes the event data from the API endpoint. Returns a dataframe. Data do not exist before 2010-2011 season

    Used within the main play-by-play scraper
    Parameters:
    game_ids: a single API game ID (e.g., 2021020001) or list of game IDs

    response_data: JSON object; default: None
        When using in another scrape function, can pass the live endpoint response as a JSON object to prevent redundant hits
    
    game_data: dataframe, or dataframe; default: empty dataframe
        Can pass a dataframe of game information to prevent re-scraping from the same endpoint.
        If empty, scrapes game information data from the API endpoint

    _print: boolean; default: True
        If True, prints progress to the console

    roster: dataframe; default: empty dataframe
        Can pass a dataframe of roster information to prevent re-scraping from the same endpoint.
        If empty, scrapes roster data from the HTML endpoint

    session: requests Session object; default = None
        When using in another scrape function, can pass the requests session to improve speed

    pbp: boolean; default: False
        If True, additional columns are added for use in the pbp scraper
    '''
    
    ## TO DO:
    ## 1. add comments and edit doc string
    ## 2. double check columns are in the right order
    
    
    ## Starting timer for scrape start
    scrape_start = time.perf_counter()
    
    ## Convert game IDs to list if given a single game ID
    game_ids = convert_to_list(game_ids)
    
    number_of_games = len(game_ids)

    if _print == True:
        
        print_scrape_intro(number_of_games, 'API events')
        
        scrape_start_bar(number_of_games)
    
    ## Important lists
    bad_game_list = list()
    concat_list = list()
    
    if response_data == None:
        
        if session == None:
        
            s = s_session()
        
        else:
            
            s = session
    
    for game_id_idx, game_id in enumerate(game_ids):
        
        game_start = time.perf_counter()
        
        game_number = game_id_idx + 1
        
        if game_data.empty:
            
            game_info = scrape_game_info(game_id, _print = False, session = s)
            
        else:
            
            game_info = game_data[game_data.game_id == game_id]
            
        if response_data == None:
        
            response = s.get(f'https://statsapi.web.nhl.com/api/v1/game/{game_id}/feed/live').json()
            
        else:
            
            response = response_data
        
        if response['liveData']['plays']['allPlays'] == []:
            
            if _print == True:
                
                message_text = f'Sorry, {game_id} is not available from the API...'
                
                print_game_id_time(game_start, game_id, number_of_games, game_number, message_text = message_text)
                
                response = None
            
            continue

        ## Creating base pbp dataframe
        event_df = pd.json_normalize(response, sep = '_', record_path = ['liveData', 'plays', 'allPlays'], meta = ['gamePk'])

        ## Getting the event players from the pbp dataframe
        event_players = {x: 'event_player_' + str(x + 1) for x in list(range(0, 4))}

        players = event_df.players.apply(pd.Series).rename(columns = event_players)

        ## Creating a blank list to store the event players for concatenating to the play-level
        players_list = list()

        ## Looping through the event players from the dictionary created earlier
        
        players_loop = [x for x in event_players.values() if x in players.columns]
        
        for player in players_loop:

            ## Creating a dataframe by concatenating the player type with the player's information (unpacking column of dictionaries)
            player_df = pd.concat([players[player].dropna().apply(pd.Series).drop(['player'], axis = 1),
                            players[player].dropna().apply(pd.Series).player.apply(pd.Series)], axis = 1)

            ## Renaming columns
            column_names = {'playerType': player + '_type', 'id': player + '_id',
                            'fullName': player, 'link': player + '_link'}

            player_df.rename(columns = column_names, inplace = True)

            ## Dropping seasonTotal column from the dataframe, but only if it exists
            if 'seasonTotal' in player_df.columns:

                player_df.drop('seasonTotal', axis = 1, inplace = True)

            ## Append the dataframe to the list so it can be concatenated later
            players_list.append(player_df)

        ## Concatenate all of the dataframes in the list on their index
        players_df = pd.concat(players_list, axis = 1)

        ## Concatenate the players dataframe and the pbp dataframe
        event_df = pd.concat([event_df, players_df], axis = 1)

        ## Drop the players column. It's the column of dictionaries that we just unpacked
        event_df = event_df.drop('players', axis = 1)

        ## Change column names        
        column_names = {'result_event': 'event_type_name', 'result_eventCode': 'event_id_nhl', 'result_eventTypeId': 'event_type', 
                        'result_description': 'event_description', 'about_eventIdx': 'event_idx', 'about_eventId': 'event_idx_nhl',
                        'about_period': 'period', 'about_periodType': 'period_type', 'about_ordinalNum': 'period_num',
                        'about_periodTime': 'period_time', 'about_periodTimeRemaining': 'period_time_remaining', 'about_dateTime': 'datetime',
                        'about_goals_away': 'goals_away', 'about_goals_home': 'goals_home', 'coordinates_x': 'coords_x', 'coordinates_y': 'coords_y', 
                        'team_id': 'event_team_id', 'team_name': 'event_team_name', 'team_link': 'event_team_link', 'team_triCode': 'event_team_tri_code', 
                        'result_secondaryType': 'event_detail_api', 'result_strength_code': 'goal_strength_code', 'result_strength_name': 'goal_strength_name',
                        'result_gameWinningGoal': 'goal_gwg', 'result_emptyNet': 'goal_empty_net', 'result_penaltySeverity': 'penalty_severity', 
                        'result_penaltyMinutes': 'penalty_minutes', 'gamePk': 'game_id'}
        
        event_df = event_df.rename(columns = column_names)

        event_df.event_team_name = event_df.event_team_name.str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8').str.upper()

        event_df.event_team_name = event_df.event_team_name.str.replace('PHOENIX COYOTES', 'ARIZONA COYOTES', regex = False)

        event_df.event_team_tri_code = event_df.event_team_tri_code.str.replace('PHX', 'ARI', regex = False)
        
        ## Fixing event players' names        
        event_players = ['event_player_' + str(x + 1) for x in list(range(0, 4))]
        
        event_players = [x for x in event_players if x in event_df.columns]
        
        for player in event_players:
                        
            replace_dict = {'ALEXANDRE ': 'ALEX ', 'ALEXANDER ': 'ALEX ', 'CHRISTOPHER ': 'CHRIS ', 'DE LEO': 'DELEO'}
            
            event_df[player] = event_df[player].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8').str.upper()
            
            for old_name, new_name in replace_dict.items():
                
                event_df[player] = event_df[player].str.replace(old_name, new_name, regex = False)
                
            event_df[player] = event_df[player].map(correct_names_dict).fillna(event_df[player])

            name_split = event_df[player].str.split(' ', n = 1)
            
            first_name = name_split.str[0]
            last_name = name_split.str[1]

            event_df[player + '_api_name'] = first_name + '.' + last_name
            
            event_df[player + '_api_name'] = event_df[player + '_api_name'].map(correct_names_dict).fillna(event_df[player + '_api_name'])
            
            event_df[player + '_api_name'] = event_df[player + '_id'].map(api_names_dict).fillna(event_df[player + '_api_name'])
            
        ## Changing event type names
        
        types_dict = {'BLOCKED_SHOT': 'BLOCK', 'BLOCKEDSHOT': 'BLOCK', 'MISSED_SHOT': 'MISS', 'FACEOFF': 'FAC',
                      'PENALTY': 'PENL', 'GIVEAWAY': 'GIVE', 'TAKEAWAY': 'TAKE', 'MISSEDSHOT': 'MISS'}
        
        event_df.event_type = event_df.event_type.map(types_dict).fillna(event_df.event_type)
        
        ## Adding additional time columns
        event_df.period = event_df.period.astype(int)
        
        event_df.period_time = event_df.period_time.astype(str)
        
        time_split = event_df.period_time.astype(str).str.split(':')
        
        event_df['period_seconds'] = time_split.str[0].astype(int) * 60 + time_split.str[1].astype(int)
        
        game_session = game_info.game_type.iloc[0]
        
        game_period = event_df.period
        
        conditions = [game_period < 5,
                      np.logical_and(game_period == 5, game_session == 'R'),
                      np.logical_and(game_period == 5, game_session == 'P'),
                      game_period > 5]
        
        values = [1200 * (event_df.period - 1) + event_df.period_seconds, 
                  3900 + event_df.period_seconds,
                  3800 + event_df.period_seconds,
                  1200 * (event_df.period - 1) + event_df.period_seconds]
        
        event_df['game_seconds'] = np.select(conditions, values, np.nan)
        
        ## Creating opposition team columns, after swapping out the teams in blocked shots
        
        columns = ['team_id', 'team_name', 'team_link', 'team_tri_code']
        
        for column in columns:
            
            teams_dict = dict()
            
            teams_list = event_df['event_' + column].unique()
            
            teams_dict.update({teams_list[1]: teams_list[2],
                               teams_list[2]: teams_list[1]})
            
            event_df['event_' + column] = np.where(event_df.event_type == 'BLOCK',
                                                   event_df['event_' + column].map(teams_dict).fillna(event_df['event_' + column]),
                                                   event_df['event_' + column])
            
            event_df['opp_' + column] = event_df['event_' + column].map(teams_dict)
        
        ## Swapping out event players 1 and 2 for blocked shots
        players_dict = dict()
        
        players_dict.update({'event_player_1': 'event_player_2',
                             'event_player_2': 'event_player_1'})
        
        columns = ['link', 'type', 'id', 'api_name']
        
        for column in columns:
            
            players_dict.update({'event_player_1_' + column: 'event_player_2_' + column,
                                 'event_player_2_' + column: 'event_player_1_' + column})
            
        mask = event_df.event_type == 'BLOCK'
        
        event_df.update(event_df.loc[mask].rename(players_dict, axis = 1))
        
        ## Adding play ID column
        
        event_df['play_id'] = event_df.game_id.astype(int).astype(str) + '000'
        event_df['play_id'] = event_df.play_id.astype(int) + event_df.event_idx.astype(int)

        event_df['season'] = str(game_id)[:4] + str(int(str(game_id)[:4]) + 1)
        
        group_list = ['period', 'game_seconds', 'event_team_tri_code', 'event_player_1_api_name', 'event_type']
        
        event_df['version'] = event_df.groupby(group_list).transform('cumcount') + 1

        ## Add the game-level dataframe to the list of dataframes to be concatenated
        concat_list.append(event_df)
    
        if _print == True:
            
            print_game_id_time(game_start, game_id, number_of_games, game_number)
        
    if concat_list == []:

        events_df = pd.DataFrame()

    else:
        
        concat_start = time.perf_counter()
        
        if _print == True:
            
            print_concat_start(number_of_games, scrape_start)
        
        ## Concatenate the game-level dataframes into one big dataframe
        events_df = pd.concat(concat_list, ignore_index = True)
    
        ## Rearranging columns
        columns = ['season', 'game_id', 'play_id', 'event_idx', 'event_idx_nhl', 'event_id_nhl', 'event_type', 'period', 'period_type', 'period_seconds',
                   'game_seconds', 'event_type_name', 'event_description', 'event_team_id', 'event_team_name', 'event_team_link',
                   'event_team_tri_code', 'event_player_1_type', 'event_player_1_id', 'event_player_1','event_player_1_link', 'event_player_1_api_name',
                   'event_player_2_type', 'event_player_2_id', 'event_player_2', 'event_player_2_link', 'event_player_2_api_name', 'event_player_3_type',
                   'event_player_3_id', 'event_player_3', 'event_player_3_link', 'event_player_3_api_name', 'event_player_4_type', 'event_player_4_id',
                   'event_player_4', 'event_player_4_link', 'event_player_4_api_name', 'opp_team_id', 'opp_team_name', 'opp_team_link', 'opp_team_tri_code',
                   'coords_x', 'coords_y', 'goals_home', 'goals_away', 'period_num', 'period_time', 'period_time_remaining', 'datetime',
                   'event_detail_api', 'goal_strength_code', 'goal_strength_name', 'goal_gwg', 'goal_empty_net', 'penalty_severity', 'penalty_minutes', 'version']
        
        columns = [x for x in columns if x in events_df.columns]

        events_df = events_df[columns]
        
        if _print == True:
            
            print_concat_finish(concat_start, number_of_games)

    if _print == True:

        print_number_of_games(number_of_games, scrape_start)
        
    return events_df

############################################## HTML events ##############################################

def scrape_html_events(game_ids, _print = True, roster = pd.DataFrame(), game_data = pd.DataFrame(), session = None):
    '''
    Scrapes the event data from the HTML endpoint. Returns a dataframe.

    Used within the main play-by-play scraper
    Parameters:
    game_ids: a single API game ID (e.g., 2021020001) or list of game IDs

    _print: boolean; default: True
        If True, prints progress to the console

    roster: dataframe; default: empty dataframe
        Can pass a dataframe of roster information to prevent re-scraping from the same endpoint.
        If empty, scrapes roster data from the HTML endpoint
    
    game_data: dataframe, or dataframe; default: empty dataframe
        Can pass a dataframe of game information to prevent re-scraping from the same endpoint.
        If empty, scrapes game information data from the API endpoint

    session: requests Session object; default = None
        When using in another scrape function, can pass the requests session to improve speed
    '''
    
    ## TO DO:
    ## 1. Add comments and doc string
    ## 2. Ensure columns returned make sense
    ## 3. Add event details for non Fenwick events
    
    
    
    ## IMPORTANT LISTS AND DICTIONARIES
    NEW_TEAMS_DICT = {'L.A': 'LAK', 'N.J': 'NJD', 'S.J': 'SJS', 'T.B': 'TBL', 'PHX': 'ARI'}
    EVENT_LIST = ['GOAL', 'SHOT', 'MISS', 'BLOCK', 'FAC', 'HIT', 'GIVE', 'TAKE', 'PENL', 'CHANGE']
    FENWICK_EVENTS = ["SHOT", "GOAL", "MISS"]
    CORSI_EVENTS = ["SHOT", "GOAL", "MISS", "BLOCK"]
    #even_strength = ["5v5", "4v4", "3v3"]
    #uneven_strength = ["5v4", "4v5", "5v3", "3v5", "4v3", "3v4", "5vE", "Ev5", "4vE", "Ev4", "3vE", "Ev3"]
    #pp_strength = ["5v4", "4v5", "5v3", "3v5", "4v3", "3v4"]
    #empty_net = ["5vE", "Ev5", "4vE", "Ev4", "3vE", "Ev3"]

    
    ## Starting timer for scrape start
    scrape_start = time.perf_counter()
    
    ## Convert game IDs to list if given a single game ID
    game_ids = convert_to_list(game_ids)
    
    number_of_games = len(game_ids)
    
    if _print == True:
    
        print_scrape_intro(number_of_games, 'HTML events')
        
        scrape_start_bar(number_of_games)
    
    ## Important lists
    CONCAT_LIST = list()
    
    if session == None:
    
        s = s_session()
        
    else:
        
        s = session

    for game_id_idx, game_id in enumerate(game_ids):
        
        game_start = time.perf_counter()
        
        if game_data.empty:
            
            game_info = scrape_game_info(game_id, _print = False, session = s)
            
        else:
            
            game_info = game_data[game_data.game_id == game_id]

        ## THE BELOW ARE IMPORTANT DICTIONARIES AND LISTS OF INFORMATION COLLECTED FROM THE GAME INFO AND ROSTERS ENDPOINTS
        
        ## Dictionary with the full team name as keys with 'home' or 'away' as values
        TEAMS_DICT = dict(zip(game_info.team_name, game_info.status)) 

        ## Dictionary with 'home' or 'away' as keys as the full team name as values
        TEAMS_DICT_REV = dict(zip(game_info.status, game_info.team_name)) 

        ## Dictionary with the full team name as keys with 'home' or 'away' as values
        TEAMS_DICT_SHORT = dict(zip(game_info.team_tri_code, game_info.status))
        
        ## Dictionary with 'home' or 'away' as keys as the full team name as values
        TEAMS_DICT_SHORT_REV = dict(zip(game_info.status, game_info.team_tri_code))

        ## Team names
        HOME_TEAM_NAME = TEAMS_DICT_REV['home']
        HOME_TEAM_NAME_SHORT = TEAMS_DICT_SHORT_REV['home']

        AWAY_TEAM_NAME = TEAMS_DICT_REV['away']
        AWAY_TEAM_NAME_SHORT = TEAMS_DICT_SHORT_REV['away']

        ## Game type, either regular season or playoffs
        GAME_SESSION = game_info.game_type.iloc[0]
        
        game_number = game_id_idx + 1
            
        html_season_id, html_game_id = convert_ids(game_id)

        url = f'http://www.nhl.com/scores/htmlreports/{html_season_id}/PL0{html_game_id}.HTM'

        response = s.get(url)

        soup = BeautifulSoup(response.content.decode('ISO-8859-1'), 'lxml')

        tds = soup.find_all("td", {"class": re.compile('.*bborder.*')})

        stripped_html = hs_strip_html(tds)

        length = int(len(stripped_html) / 8)

        column_names = {0: 'event_idx', 1: 'period', 2: 'strength', 3: 'time', 4: 'event', 5: 'description', 6: 'away_skaters', 7: 'home_skaters'}

        events_df = pd.DataFrame(np.array(stripped_html).reshape(length, 8)).rename(columns = column_names)

        potential_names = soup.find_all('td', {'align':'center', 'style':'font-size: 10px;font-weight:bold'})

        teams_dict = dict()

        for name in potential_names:

            data = name.get_text()

            if ('Away Game') in data or ('tr./Away') in data:

                away = re.split('Match|Game', data)[0]

                teams_dict.update({'away': away})

                break

        for name in potential_names:

            data = name.get_text()

            if ('Home Game') in data or ('Dom./Home') in data:

                home = re.split('Match|Game', data)[0]

                teams_dict.update({'home': home})

                break

        for team_type, team_name in TEAMS_DICT_REV.items():

            events_df[team_type + '_skaters'] = events_df[team_type + '_skaters'].str.replace('\n', '')

            events_df[team_type + '_team'] = team_name

            events_df[team_type + '_team_abbreviated'] = TEAMS_DICT_SHORT_REV[team_type]

        time_split = events_df.time.astype(str).str.split(':')

        events_df['original_time'] = events_df.time

        events_df['time'] = time_split.str[0] + ':' + time_split.str[1].str[:2]

        events_df = events_df[events_df.period != 'Per'].reset_index(drop = True)

        for old_name, new_name in NEW_TEAMS_DICT.items():

            events_df.description = events_df.description.str.replace(old_name, new_name, regex = False)

        if game_id == 2012020018:

            bad_names = {'EDM #9': 'VAN #9', 'VAN #93': 'EDM #93', 'VAN #94': 'EDM #94'}

            for bad_name, good_name in bad_names.items():

                events_df.description = events_df.description.str.replace(bad_name, good_name, regex = False)

        if game_id == 2018021133:

            events_df.description = events_df.description.str.replace('WSH TAKEAWAY - #71 CIRELLI', 'TBL TAKEAWAY - #71 CIRELLI', regex = False)

        events_df['event_team'] = np.where(events_df.event != 'STOP', 
                                            events_df.description.str.extract('^([A-Z]{3}|[A-Z]\.[A-Z])', expand = False), 
                                            np.nan)

        columns = ['event_team', 'home_team_abbreviated', 'away_team_abbreviated']
        
        for col in columns:
            
            events_df[col] = events_df[col].map(NEW_TEAMS_DICT).fillna(events_df[col])

        teams_list = [HOME_TEAM_NAME_SHORT, HOME_TEAM_NAME_SHORT]

        cond_1 = events_df.event_team == HOME_TEAM_NAME_SHORT
        value_1 = AWAY_TEAM_NAME_SHORT

        cond_2 = events_df.event_team == AWAY_TEAM_NAME_SHORT
        value_2 = HOME_TEAM_NAME_SHORT

        conditions = [cond_1, cond_2]
        values = [value_1, value_2]

        events_df['opp_team'] = np.select(conditions, values, np.nan)
                                                    
        events_df['event_player_str'] = events_df.description.str.findall('[A-Z]{3}\s+\#[0-9]{1,2}').str.join(' ').str.replace(' #', '')    
        
        player_split = events_df.event_player_str.str.split(' ')

        players = ['event_player_' + str(x) for x in list(range(1, 4))]

        for idx, player in enumerate(players):

            events_df[player] = player_split.str[idx]

        events_df.event_player_1 = np.where(np.logical_or(events_df.event_player_1 == '', pd.isna(events_df.event_player_1)), 
                                            events_df.description.str.extract('([A-Z]{3}|[A-Z]\.[A-Z])\s+([A-Z]+\s\-\s)?\#([0-9]{1,2})')[0] + 
                                            events_df.description.str.extract('([A-Z]{3}|[A-Z]\.[A-Z])\s+([A-Z]+\s\-\s)?\#([0-9]{1,2})')[2],
                                            events_df.event_player_1)

        events_df.event_player_1 = np.where(np.logical_and(events_df.event == 'PENL', events_df.description.str.contains('too many men', case = False, regex = False)), 
                                                'BENCH',
                                                events_df.event_player_1)

        events_df.event_player_2 = np.where(np.logical_and(events_df.event == 'PENL', events_df.description.str.contains('too many men', case = False, regex = False)), 
                                                events_df.event_team + events_df.description.str.extract('\#([0-9]{1,2})', expand = False),
                                                events_df.event_player_2)

        events_df.event_player_2 = np.where(np.logical_and(events_df.event == 'GOAL', events_df.description.str.count('\#([0-9]{1,2})') >  1), 
                                                    events_df.event_team + events_df.description.str.findall('\#([0-9]{1,2})').apply(pd.Series)[1],
                                                    events_df.event_player_2)


        try:
            
            conds = np.logical_and(events_df.event == 'GOAL', events_df.description.str.count('\#([0-9]{1,2})') > 2)

            events_df.event_player_3 = np.where(conds, events_df.event_team + events_df.description.str.findall('\#([0-9]{1,2})').apply(pd.Series)[2],
                                                        events_df.event_player_3)
        except: KeyError

        ## Swapping out event players 1 and 2 for faceoffs
        players_dict = dict()
        
        players_dict = {'event_player_1': 'event_player_2',
                        'event_player_2': 'event_player_1'}
        
        mask = np.logical_and(events_df.event_team == HOME_TEAM_NAME_SHORT, events_df.event == 'FAC')
        
        events_df.update(events_df.loc[mask].rename(players_dict, axis = 1))

        events_df.description = events_df.description.str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')

        events_df['penalty_type'] = events_df.description.str.extract('\#\d{1,2}\s[A-Z]+\s*(.*)\(\d+', expand = False) #'\#\d{1,2}\s[A-Z]+\s*(.*)\(\d+'

        events_df.penalty_type = events_df.penalty_type.str.replace('.[A-Z]+\s', '', regex = True)
               
        if roster.empty:
            
            roster_df = scrape_html_rosters(game_id, _print = False, session = s)
            
        else:
            
            roster_df = roster
            
        roster_df['team_abbreviated'] = np.where(roster_df.team == 'home', HOME_TEAM_NAME_SHORT, AWAY_TEAM_NAME_SHORT)
        
        roster_df['teamnum'] = roster_df.team_abbreviated + roster_df.player_jersey.astype(str)

        active_df = roster_df[roster_df.player_status != 'scratch'].copy()
        
        name_dict = dict(zip(active_df.teamnum, active_df.player_name))
        
        api_name_dict = dict(zip(active_df.teamnum, active_df.api_name))

        scratches_df = roster_df[roster_df.player_status == 'scratch'].copy()

        scratches_names = dict(zip(scratches_df.teamnum, scratches_df.player_name))

        scratches_api = dict(zip(scratches_df.teamnum, scratches_df.api_name))
        
        players = ['event_player_' + str(x) for x in list(range(1, 4))]
        
        for player in players:
            
            api_col = player + '_api_name'

            events_df[api_col] = events_df[player].map(api_name_dict).fillna(events_df[player])

            events_df[api_col] = np.where(events_df[api_col].isin(scratches_api.keys()),
                                                    events_df[api_col].map(scratches_api), 
                                                    events_df[api_col])
            
            events_df[player] = events_df[player].map(name_dict).fillna(events_df[player])

            events_df[player] = np.where(events_df[player].isin(scratches_names.keys()),
                                                    events_df[player].map(scratches_names), 
                                                    events_df[player])

        
        team_names_dict = {'home': HOME_TEAM_NAME_SHORT, 'away': AWAY_TEAM_NAME_SHORT}
        
        #for team_type, team_name in team_names_dict.items():
            
        #    skaters = events_df[team_type + '_skaters'].str.findall('([0-9]+(?=[A-Z]))').apply(pd.Series)
            
        #    for col in skaters.columns:
                
        #        skaters[col] = pd.Series(np.where(~pd.isna(skaters[col]), team_name + skaters[col].astype(str), skaters[col]))\
        #                                    .map(api_name_dict).fillna(skaters[col])
                
        #    events_df[f'{team_type}_skaters_on'] = skaters.values.tolist()
            
        #    positions = events_df[team_type + '_skaters'].str.findall('((?<=[0-9])[A-Z])').apply(pd.Series)
            
            #column_names = {x: f'{team_type}_on_{x + 1}' for x in skaters.columns}
            
            #skaters.rename(columns = column_names, inplace = True)
            
            #skaters.replace('[A-Z]', '', regex = True, inplace = True)
            
            #events_df = pd.concat([events_df, skaters], axis = 1)
            
            #for col in skaters.columns:
                
            #    events_df[col] = np.where(~pd.isna(events_df[col]),
            #                              events_df[team_type + '_team_abbreviated'] + events_df[col].astype(str),
            #                              events_df[col])
            
            
            #column_names = {x: f'{team_type}_on_{x + 1}_position' for x in positions.columns}
            
            #positions.rename(columns = column_names, inplace = True)
            
            #positions.replace('([0-9]|[0-9][0-9])', '', regex = True, inplace = True)
            
            #events_df = pd.concat([events_df, positions], axis = 1)
        
        game_date = soup.find_all('td', {'align':'center', 'style':'font-size: 10px;font-weight:bold'})[2].get_text()
        
        events_df['game_date'] = pd.to_datetime(game_date)
        
        events_df.time = np.where(np.logical_or(events_df.time == '', pd.isna(events_df.time)), '0:00', events_df.time)
        
        events_df.period = np.where(events_df.period == '', 1, events_df.period).astype(int)
        
        time_split = events_df.time.astype(str).str.replace('-', '').astype(str).str.split(':')
        
        events_df['period_seconds'] = 60 * time_split.str[0].astype(int) + time_split.str[1].astype(int)
        
        game_period = events_df.period
        
        conditions = [game_period < 5,
                      np.logical_and(game_period == 5, GAME_SESSION == 'R'),
                      np.logical_and(game_period == 5, GAME_SESSION == 'P'),
                      game_period > 5]
        
        values = [1200 * (events_df.period - 1) + events_df.period_seconds, 
                  3900 + events_df.period_seconds,
                  3800 + events_df.period_seconds,
                  1200 * (events_df.period - 1) + events_df.period_seconds]
        
        events_df['game_seconds'] = np.select(conditions, values, np.nan)
        
        events_df['season'] = html_season_id
        
        events_df['game_id'] = game_id
        
        events_df = events_df.replace('CANADIENS MONTREAL', 'MONTREAL CANADIENS', regex = False)
        
        if game_id == 2007020003:
            
            events_df.game_date = events_df.game_date + pd.Timedelta(days = 1)
        
        events_df['event_zone'] = events_df.description.str.extract("([a-zA-Z]{3}\\.\\s*[zZ]one)", expand = False)\
                                        .str.replace('. zone', '', case = False, regex = False).str.upper()
        
        #event_zone = str_extract(event_description, "[a-zA-Z]{3}\\.\\s*[zZ]one")
        
        type_list = ['home', 'away']
        
        for team_type in type_list:
            
            events_df[team_type + '_skater_count'] = events_df[team_type + '_skaters'].str.count('[A-Z]') \
                                                        - events_df[team_type + '_skaters'].str.count('G')
        
        ## Extracting event details, based on the event
        ## Note: Only currently supports event details from corsi events
        weird_list = ['PSTR', 'PEND', 'SOC', 'GEND']
        
        conditions = [np.isin(events_df.event, CORSI_EVENTS),
                      np.isin(events_df.event, weird_list),
                      events_df.event == 'PENL',]
                      #events_df.event == 'CHL']
          
        values = [events_df.description.str.extract(",\\s*([a-zA-Z|-]+),", expand = False),
                  events_df.description.str.extract("([0-9]+:[0-9]+)\\s*([A-Z])+", expand = False)[0],
                  events_df.description.str.extract("\\(([0-9]+\\s[a-z]*)\\)", expand = False),]
                  #events_df.description.str.extract("-([a-zA-Z\\s])+-", expand = False)]#.replace("(\\s*-|-\\s*)", '', regex = True)]
        
        events_df['event_detail'] = np.select(conditions, values, np.nan)

        ## Setting home team values
        replace_dict = {'home': 1, 'away': 0}

        events_df['is_home'] = events_df.event_team.map(TEAMS_DICT_SHORT).replace(replace_dict)

        #events_df['penalty_shot'] = np.where(events_df.description.str.contains('penalty shot', case = False, regex = False), 1, 0)

        #events_df['shootout'] = np.where(np.logical_and(GAME_SESSION == 'R', events_df.period == 5), 1, 0)
        
        #events_df['is_goal'] = np.where(events_df.event == 'GOAL', 1, 0)
        
        teams_list = ['home', 'away']
        
        for team_type, team_name in TEAMS_DICT_SHORT_REV.items():
            
            events_df[team_type + '_score'] = np.where(np.logical_and(events_df.event_team == team_name, events_df.event == 'GOAL'), 1, 0)
            
            events_df[team_type + '_score'] = events_df[team_type + '_score'].cumsum()        
        
        #events_df['score_state'] = np.where(events_df.is_home == 0,
        #                                    events_df['away_score'].astype(str) + 'v' + events_df['home_score'].astype(str),
        #                                    events_df['home_score'].astype(str) + 'v' + events_df['away_score'].astype(str))

        #events_df['score_diff'] = np.where(events_df.is_home == 0,
        #                                    events_df['away_score'] - events_df['home_score'],
        #                                    events_df['home_score'] - events_df['away_score'])

        #away_strength, home_strength = events_df.strength.str.split('v', expand = True)

        #events_df.strength = np.where(events_df.is_home == 0, 
        #                                away_strength + 'v' + home_strength, 
        #                                home_strength + 'v' + away_strength)

        events_df['session'] = GAME_SESSION
        
        group_list = ['period', 'game_seconds', 'event_team', 'event', 'event_player_1_api_name']
        
        events_df['version'] = events_df.groupby(group_list).transform('cumcount') + 1
        
        CONCAT_LIST.append(events_df)
        
        if _print == True:

            print_game_id_time(game_start, game_id, number_of_games, game_number)
    
    concat_start = time.perf_counter()
    
    if _print == True:
        
        print_concat_start(number_of_games, scrape_start)
    
    if CONCAT_LIST == []:
        
        events_df = pd.DataFrame()
    
    events_df = pd.concat(CONCAT_LIST, ignore_index = True)
    
    columns = ['season', 'session', 'game_date', 'game_id', 'event_idx', 'period', 'period_seconds', 'game_seconds', 'event', 'event_detail',
               'description', 'event_zone', 'event_team', 'opp_team', 'event_player_1', 'event_player_2', 'event_player_3', 'home_score', 'away_score', 
               'score_state', 'score_diff', 'home_team', 'home_team_abbreviated', 'home_skaters', 'away_team', 'away_team_abbreviated', 'away_skaters',
               'strength', 'home_skater_count', 'away_skater_count', 'time', 'original_time', 'is_home', 'is_goal', 'penalty_shot', 'shootout',
               'event_player_1_api_name','event_player_2_api_name', 'event_player_3_api_name', 'event_player_str', 'penalty_type', 'version',
               'old_away_skaters', 'old_home_skaters']
    
    columns = [x for x in columns if x in events_df.columns]
    
    events_df = events_df[columns]
    
    if _print == True:
        
        print_concat_finish(concat_start, number_of_games)
        
        print_number_of_games(number_of_games, scrape_start)
        
    return events_df

############################################## Box score ##############################################

def scrape_boxscore(game_ids, _print = True):
    '''
    Returns a dataframe of boxscore data from the API endpoint.

    Not currently used for anything

    Parameters:
    game_ids: a single API game ID (e.g., 2021020001) or list of game IDs

    _print: boolean; default: True
        If True, prints progress to the console
    '''
    
    ## Starting timer for scrape start
    scrape_start = time.perf_counter()
    
    ## Convert game IDs to list if given a single game ID
    game_ids = convert_to_list(game_ids)
    
    number_of_games = len(game_ids)

    if _print == True:
    
        print_scrape_intro(number_of_games, 'API boxscore')
        
        scrape_start_bar(number_of_games)
    
    ## Important lists
    concat_list = list()
    
    s = s_session()

    for game_id_idx, game_id in enumerate(game_ids):
        
        game_start = time.perf_counter()
        
        game_number = game_id_idx + 1
            
        response = s.get(f'https://statsapi.web.nhl.com/api/v1/game/{game_id}/boxscore', timeout = .5).json()
        
        game_concat_list = list()

        teams_list = ['home', 'away']

        for team in teams_list:

            team_concat_list = list()

            for player in response['teams'][team]['players'].values():

                team_concat_list.append(pd.json_normalize(player, sep = '_'))

            team_df = pd.concat(team_concat_list, ignore_index = True)

            team_df['game_id'] = game_id

            for key, value in response['teams'][team]['team'].items():

                team_df['team_' + key] = value

            game_concat_list.append(team_df)

        if game_concat_list == []:
            
            if _print == True:
                
                message = f'Sorry, no box score information for {game_id} ({game_number}/{number_of_games})...'
                
                print_game_id_time(game_start, game_id, number_of_games, game_number, message = message)
                
                continue
            
        game_df = pd.concat(game_concat_list, ignore_index = True)

        game_df['season'] = str(game_id)[:4] + str(int(str(game_id)[:4]) + 1)
        
        ## Clean dataframe at the game level
        
        new_cols = list()
        
        for column in game_df.columns:
            
            column = column.replace('stats_', '')
            
            column = column.replace('person_', '')
            
            new_cols.append(column)
        
        column_names = dict(zip(game_df.columns, new_cols))
        
        game_df = game_df.rename(columns = column_names)
        
        column_names = {'season': 'season', 'game_id': 'game_id', 'team_name': 'team_name', 'id': 'player_id', 'fullName': 'player_name', 'jerseyNumber': 'player_jersey',
                        'position_abbreviation': 'player_position_abbr', 'skaterStats_timeOnIce': 'skater_toi', 'skaterStats_goals': 'skater_goals',
                        'skaterStats_assists': 'skater_assists', 'skaterStats_shots': 'skater_shots', 'skaterStats_hits': 'skater_hits',
                        'skaterStats_powerPlayGoals': 'skater_power_play_goals', 'skaterStats_powerPlayAssists': 'skater_power_play_assists',
                        'skaterStats_penaltyMinutes': 'skater_penalty_minutes', 'skaterStats_faceOffPct': 'skater_faceoff_win_percent',
                        'skaterStats_faceoffTaken': 'skater_faceoffs_taken', 'skaterStats_takeaways': 'skater_takaways',
                        'skaterStats_giveaways': 'skater_giveaways', 'skaterStats_shortHandedGoals': 'skater_shortHanded_goals',
                        'skaterStats_shortHandedAssists': 'skater_shorthanded_assists', 'skaterStats_blocked': 'skater_shots_blocked',
                        'skaterStats_plusMinus': 'skater_plus_minus', 'skaterStats_evenTimeOnIce': 'skater_even_toi',
                        'skaterStats_powerPlayTimeOnIce': 'skater_power_play_toi', 'skaterStats_shortHandedTimeOnIce': 'skater_shorthanded_toi',
                        'goalieStats_timeOnIce': 'goalie_toi', 'goalieStats_assists': 'goalie_goals', 'goalieStats_assists': 'goalie_assists',
                        'goalieStats_pim': 'goalie_penalty_minutes', 'goalieStats_shots': 'goalie_shots', 'goalieStats_saves': 'goalie_saves',
                        'goalieStats_powerPlaySaves': 'goalie_power_play_saves', 'goalieStats_shortHandedSaves': 'goalie_shorthanded_saves',
                        'goalieStats_evenSaves': 'goalie_even_saves', 'goalieStats_shortHandedShotsAgainst': 'goalie_shorthanded_shots_against',
                        'goalieStats_evenShotsAgainst': 'goalie_even_shots_against', 'goalieStats_powerPlayShotsAgainst': 'goalie_power_play_shots_against',
                        'goalieStats_decision': 'goalie_decision', 'goalieStats_savePercentage': 'goalie_save_percentage',
                        'goalieStats_powerPlaySavePercentage': 'goalie_power_play_save_percentage',
                        'goalieStats_shortHandedSavePercentage': 'goalie_shorthanded_save_percentage',
                        'goalieStats_evenStrengthSavePercentage': 'goalie_even_save_percentage', 'firstName': 'player_first_name',
                        'lastName': 'player_last_name', 'link': 'player_link', 'birthDate': 'player_dob', 'birthCity': 'player_birth_city', 
                        'birthStateProvince': 'player_birth_state_province', 'birthCountry': 'player_birth_country', 'nationality': 'player_nationality', 
                        'currentAge': 'player_current_age', 'height': 'player_height', 'weight': 'player_weight', 'active': 'player_active',
                        'roster_status': 'player_roster_status', 'shootsCatches': 'player_shoots_catches', 'team_id': 'team_id', 'link': 'player_link', 
                        'primaryNumber': 'player_primary_number', 'captain': 'player_captain', 'alternate_captain': 'player_alternate_captain',
                        'rookie': 'player_rookie', 'position_code': 'player_position_code', 'position_name': 'player_position_name',
                        'position_type': 'player_position_type', 'currentTeam_id': 'current_team_id', 'currentTeam_name': 'current_team_name',
                        'currentTeam_link': 'current_team_link', 'primaryPosition_code': 'player_primary_position_code',
                        'primaryPosition_name': 'player_primary_position_name', 'primaryPosition_type': 'player_primary_position_type',
                        'primaryPosition_abbreviation': 'player_primary_position_abbr'}
        
        game_df = game_df.rename(columns = column_names)
        
        columns = [x for x in column_names.values() if x in game_df.columns]
        
        game_df = game_df[columns]
        
        concat_list.append(game_df)
        
        if _print == True:

            print_game_id_time(game_start, game_id, number_of_games, game_number)
    
    if concat_list == []:
        
        boxscore_df = pd.DataFrame()
    
    else:
        
        concat_start = time.perf_counter()
        
        if _print == True:

            print_concat_start(number_of_games, scrape_start)
        
        boxscore_df = pd.concat(concat_list, ignore_index = True)
        
        if _print == True:
            
            print_concat_finish(concat_start, number_of_games)

            print_number_of_games(number_of_games, scrape_start)
            
    return boxscore_df        

############################################## API rosters ##############################################

def scrape_api_rosters(game_ids, response_data = None, session = None, _print = True):
    '''
    Returns a dataframe of roster data from the API endpoint.

    Not currently used for anything

    Parameters:
    game_ids: a single API game ID (e.g., 2021020001) or list of game IDs

    _print: boolean; default: True
        If True, prints progress to the console
    '''
    
    ## TO DO: 
    ## 1. add comments and docstring
    ## 2. ensure columns returned make sense.
    ## 3. Check response loop is still good
    
    ## Starting timer for scrape start
    scrape_start = time.perf_counter()
    
    ## Convert game IDs to list if given a single game ID
    game_ids = convert_to_list(game_ids)
    
    number_of_games = len(game_ids)

    if _print == True:
    
        print_scrape_intro(number_of_games, 'API roster info')
        scrape_start_bar(number_of_games)
        
    ## Important lists
    bad_game_list = list()
    concat_list = list()
    
    if response_data == None:
        
        if session == None:

            s = s_session()
    
    for game_id_idx, game_id in enumerate(game_ids):
        
        game_start = time.perf_counter()
        
        game_number = game_id_idx + 1
            
        if response_data == None:

            response = scrape_live_endpoint(game_id, session = s)

        else:

            response = response_data[response_data.game_id == game_id]
            
        game_info = scrape_game_info(game_id, response_data = response, session = s, _print = False)
        
        teams_dict = dict(zip(game_info.team_name, game_info.status))
        
        if response['gameData']['players'] == []:
            
            if _print == True:

                message_text = f'Sorry, unable to scrape rosters data for {game_id} ({game_number}/{number_of_games})...'

                print_game_id_time(game_start, game_id, number_of_games, game_number, message_text = message_text)
                
                response = None

        players_list = list()
        
        for player in response['gameData']['players'].keys():

            df = pd.json_normalize(response['gameData']['players'][player], meta = 'gameData', sep = '_')

            column_names = {'id': 'player_id', 'fullName': 'player_name', 'link': 'player_link', 'firstName': 'player_first_name',
                            'lastName': 'player_last_name', 'primaryNumber': 'player_number', 'birthDate': 'player_dob',
                            'currentAge': 'player_current_age', 'birthCity': 'player_birth_city', 'birthStateProvince': 'player_birth_state_province', 
                            'birthCountry': 'player_birth_country', 'nationality': 'player_nationality', 'height': 'player_height', 'weight': 'player_weight', 
                            'active': 'player_active', 'alternateCaptain': 'player_alternate_captain', 'captain': 'player_captain', 'rookie': 'player_rookie', 
                            'shootsCatches': 'player_shoots_catches', 'rosterStatus': 'player_roster_status', 'currentTeam_id': 'player_current_team_id',
                            'currentTeam_name': 'player_current_team_name', 'currentTeam_link': 'player_current_team_link',
                            'currentTeam_triCode': 'player_current_team_tri_code', 'primaryPosition_code': 'player_position_code',
                            'primaryPosition_name': 'player_position_name', 'primaryPosition_type': 'player_position_type',
                            'primaryPosition_abbreviation': 'player_position_abbr'}

            df = df.rename(columns = column_names)

            df['game_id'] = game_id

            players_list.append(df)
            
        players_df = pd.concat(players_list)
        
        ## Fixing players' names
        replace_dict = {'Alexandre ': 'Alex ', 'Alexander ': 'Alex ', 'Christopher ': 'Chris '}
        
        for old_name, new_name in replace_dict.items():
            
            players_df.player_name = players_df.player_name.str.replace(old_name, new_name, regex = False, case = False)
        
        players_df['api_name'] = players_df.player_name.str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8').str.upper()
        
        players_df.api_name = players_df.api_name.map(correct_names_dict).fillna(players_df.api_name)
        
        name_split = players_df.api_name.str.split(' ', 1)
        
        api_first_name = name_split.str[0]
        
        api_last_name = name_split.str[1]

        players_df['api_name'] = api_first_name + '.' + api_last_name

        players_df.api_name = players_df.api_name.map(api_names_dict).fillna(players_df.api_name)

        players_df['season'] = str(game_id)[:4] + str(int(str(game_id)[:4]) + 1)
        
        players_df['player_venue'] = players_df.player_current_team_name.map(teams_dict)
        
        concat_list.append(players_df)
            
        if _print == True:

            print_game_id_time(game_start, game_id, number_of_games, game_number)
            
    if concat_list != []:
        
        concat_start = time.perf_counter()
        
        if _print == True:
            
            print_concat_start(number_of_games, scrape_start)
        
        roster_df = pd.concat(concat_list, ignore_index = True)
        
        columns = ['season', 'game_id', 'player_id', 'player_name', 'api_name', 'player_current_team_name', 'player_current_team_tri_code', 'player_venue',
                   'player_number', 'player_roster_status', 'player_position_code', 'player_position_type', 'player_position_abbr', 'player_position_name', 
                   'player_first_name', 'player_last_name', 'player_dob', 'player_height', 'player_weight', 'player_shoots_catches', 
                   'player_nationality', 'player_birth_city', 'player_birth_state_province', 'player_birth_country', 'player_rookie',
                   'player_current_age', 'player_captain', 'player_alternate_captain', 'player_link', 'player_current_team_id',
                   'player_current_team_link', 'player_active']
        
        columns = [x for x in columns if x in roster_df.columns]

        roster_df = roster_df[columns]
            
    if _print == True:
        
        print_concat_finish(concat_start, number_of_games)
            
        print_number_of_games(number_of_games, scrape_start)
        
    if concat_list == []:
        
        return pd.DataFrame()
    
    else:
        
        return roster_df

############################################## ESPN events ##############################################

def scrape_espn_ids_single_game(game_date, home_team, away_team):
    
    gamedays = pd.DataFrame()
    
    if home_team == 'ATLANTA THRASHERS':
        home_team = 'WINNIPEG JETS'
    if away_team == 'ATLANTA THRASHERS':
        away_team = 'WINNIPEG JETS'
        
    if home_team == 'PHOENIX COYOTES':
        home_team = 'ARIZONA COYOTES'
    if away_team == 'PHOENIX COYOTES':
        away_team = 'ARIZONA COYOTES'
    
    this_date = (game_date)
    url = 'http://www.espn.com/nhl/scoreboard?date=' + this_date.replace("-", "")
    page = requests.get(url, timeout = 500)
    soup = BeautifulSoup(page.content, parser = 'lxml')
    soup_found = soup.find_all('a', {'class':['AnchorLink truncate', 'AnchorLink Button Button--sm Button--anchorLink Button--alt mb4 w-100'], 'href':[re.compile("/nhl/team/_/name/"), re.compile("game/_")]})
    at = []
    ht = []
    gids = []
    fax = pd.DataFrame()
    #print(str(i))
    for i in range (0, (int(len(soup_found)/3))):
        away = soup_found[0 + (i * 3)]['href'].rsplit('/')[-1].replace('-', ' ').upper()
        home = soup_found[1 + (i * 3)]['href'].rsplit('/')[-1].replace('-', ' ').upper()
        espnid = soup_found[2 + (i * 3)]['href'].split('gameId/', 1)[1]
        at.append(away)
        ht.append(home)
        gids.append(espnid)

    fax = fax.assign(
    away_team = at,
    home_team = ht,
    espn_id = gids,
    game_date = pd.to_datetime(this_date))

    gamedays = gamedays.append(fax)

    gamedays = gamedays.assign(
        home_team = np.where(gamedays.home_team=='ST LOUIS BLUES', 'ST. LOUIS BLUES', gamedays.home_team),
        away_team = np.where(gamedays.away_team=='ST LOUIS BLUES', 'ST. LOUIS BLUES', gamedays.away_team),
        espn_id = gamedays.espn_id.astype(int))
    
    #gamedays = gamedays.assign(
     #   home_team = np.where(gamedays.home_team=='WINNIPEG JETS', 'ATLANTA THRASHERS', gamedays.home_team),
      #  away_team = np.where(gamedays.away_team=='WINNIPEG JETS', 'ATLANTA THRASHERS', gamedays.away_team),
       # espn_id = gamedays.espn_id.astype(int))
    
    gamedays = gamedays[(gamedays.game_date==this_date) & (gamedays.home_team==home_team) & (gamedays.away_team==away_team)]
        
    return gamedays

############################################## FULL PBP FUNCTION ##############################################

def scrape_pbp(game_ids, _print = True):
    '''
    Returns a dataframe of play-by-play data sourced from various endpoints.

    Combines API events, API game info, HTML events, and HTML roster scrapes

    Parameters:
    game_ids: a single API game ID (e.g., 2021020001) or list of game IDs

    _print: boolean; default: True
        If True, prints progress to the console
    '''
    
    ## TO DO:
    ## 1. Comments
    ## 2. Clean up and reorganize code
    ## 3. Add opp_goalie column
    ## 4. Add game_session column
    ## 5. Fix shift index
    
    ## SUPER IMPORTANT LISTS. THESE ARE USED THROUGHOUT THE SCRAPER
    
    EVENT_LIST = ['GOAL', 'SHOT', 'MISS', 'BLOCK', 'FAC', 'HIT', 'GIVE', 'TAKE', 'PENL', 'CHANGE']
    FENWICK_EVENTS = ["SHOT", "GOAL", "MISS"]
    CORSI_EVENTS = ["SHOT", "GOAL", "MISS", "BLOCK"]
    #even_strength = ["5v5", "4v4", "3v3"]
    #uneven_strength = ["5v4", "4v5", "5v3", "3v5", "4v3", "3v4", "5vE", "Ev5", "4vE", "Ev4", "3vE", "Ev3"]
    #pp_strength = ["5v4", "4v5", "5v3", "3v5", "4v3", "3v4"]
    #empty_net = ["5vE", "Ev5", "4vE", "Ev4", "3vE", "Ev3"]
    
    
    ## Starting timer for scrape start
    scrape_start = time.perf_counter()
    
    ## Convert game IDs to list if given a single game ID
    game_ids = convert_to_list(game_ids)
    
    ## Calculate the number of games to be scraped for use in various functions later
    number_of_games = len(game_ids)
    
    ## Print scrape introduction and the 0% start bar
    if _print == True:
        print_scrape_intro(number_of_games, 'play-by-play')
        scrape_start_bar(number_of_games)
        
    ## Create requests sessions objects for each for the endpoints we scrape
    html_shifts_session = s_session()
    live_response_session = s_session()
    html_rosters_session = s_session()
    html_events_session = s_session()
        
    ## THIS IS AN IMPORTANT LIST
    ## It will collect the individual game dataframes that will eventually be concatenated into a larger dataframe
    CONCAT_LIST = list()

    ## Looping over the index, as well as the value in the list of game IDs, because sometimes I need the index value
    for game_id_idx, game_id in enumerate(game_ids):
        
        ## Setting the start of the game scrape for use in various timers later
        game_start = time.perf_counter()
        
        ## This is also used in various timers
        game_number = game_id_idx + 1

        try:
        
            ## Because several functions use the same endpoint, we get the response here rather than over and over again
            live_response = scrape_live_endpoint(game_id, session = live_response_session)
            
            ## Dataframe of game information
            game_info = scrape_game_info(game_id, response_data = live_response, _print = False, session = live_response_session)

            ## Dataframe of roster information
            roster_df = scrape_html_rosters(game_id, _print = False, session = html_rosters_session)

            ## Dataframe of events scraped from the html endpoint
            html_events = scrape_html_events(game_id, roster = roster_df, game_data = game_info, _print = False, session = html_events_session)

            ## Dataframe of events scraped from the API endpoint
            api_events = scrape_api_events(game_id, response_data = live_response, game_data = game_info, session = live_response_session, _print = False)

            ## Dictionary of shifts information collected from html endpoint
            shifts_dict = scrape_html_shifts(game_id, roster_data = roster_df, game_data = game_info, _print = False, session = html_shifts_session, pbp = True)

        except ConnectionError:

            if _print == True:
                
                message_text = f"You're hitting the endpoints a lot, pausing for ten seconds at ({game_number - 1}/{number_of_games})..."
                
                print_game_id_time(game_start, game_id, number_of_games, game_number = (game_number - 1), message_text = message_text)

            time.sleep(10)

            ## Because several functions use the same endpoint, we get the response here rather than over and over again
            live_response = scrape_live_endpoint(game_id, session = live_response_session)
            
            ## Dataframe of game information
            game_info = scrape_game_info(game_id, response_data = live_response, _print = False, session = live_response_session)

            ## Dataframe of roster information
            roster_df = scrape_html_rosters(game_id, _print = False, session = html_rosters_session)

            ## Dataframe of events scraped from the html endpoint
            html_events = scrape_html_events(game_id, roster = roster_df, game_data = game_info, _print = False, session = html_events_session)

            ## Dataframe of events scraped from the API endpoint
            api_events = scrape_api_events(game_id, response_data = live_response, game_data = game_info, session = live_response_session, _print = False)

            ## Dictionary of shifts information collected from html endpoint
            shifts_dict = scrape_html_shifts(game_id, roster_data = roster_df, game_data = game_info, _print = False, session = html_shifts_session, pbp = True)


        if html_events.empty:
            
            if _print == True:
                
                message_text = f'No events data for {game_id} ({game_number}/{number_of_games})...'
                
                print_game_id_time(game_start, game_id, number_of_games, game_number, message_text = message_text)
                
            continue

        if api_events.empty:
            
            if _print == True:
                
                message_text = f'No API event coordinates for {game_id} ({game_number}/{number_of_games})...'
                
                print_game_id_time(game_start, game_id, number_of_games, game_number, message_text = message_text)
                
            continue

        changes_df = shifts_dict['changes']

        if changes_df.empty:

            if _print == True:

                message_text = f'No shifts data, unable to scrape on-ice data for {game_id} ({game_number}/{number_of_games})...'

                print_game_id_time(game_start, game_id, number_of_games, game_number, message_text = message_text)

            continue
        
        ## THE BELOW ARE IMPORTANT DICTIONARIES AND LISTS OF INFORMATION COLLECTED FROM THE GAME INFO AND ROSTERS ENDPOINTS
        
        ## Dictionary with the full team name as keys with 'home' or 'away' as values
        TEAMS_DICT = dict(zip(game_info.team_name, game_info.status)) 

        ## Dictionary with 'home' or 'away' as keys as the full team name as values
        TEAMS_DICT_REV = dict(zip(game_info.status, game_info.team_name)) 

        ## Dictionary with the full team name as keys with 'home' or 'away' as values
        TEAMS_DICT_SHORT = dict(zip(game_info.team_tri_code, game_info.status))
        
        ## Dictionary with 'home' or 'away' as keys as the full team name as values
        TEAMS_DICT_SHORT_REV = dict(zip(game_info.status, game_info.team_tri_code))
        
        ## Setting game date
        GAME_DATE = html_events.game_date.iloc[0]

        ## Merging the HTML and API dataframes 
        left_list = ['game_id', 'period', 'game_seconds', 'event', 'event_team', 'event_player_1_api_name', 'version']

        right_list = ['game_id', 'period', 'game_seconds', 'event_type', 'event_team_tri_code', 'event_player_1_api_name', 'version']

        keep_list = ['game_id', 'period', 'game_seconds', 'event_type', 'event_team_tri_code', 'event_player_1_api_name',
                     'coords_x', 'coords_y', 'penalty_severity', 'penalty_minutes', 'datetime', 'event_detail_api', 'version']\
                        + [x for x in api_events.columns if 'type' in x
                           and 'event_type' not in x
                           and 'period' not in x]
        
        keep_list = [x for x in keep_list if x in api_events.columns]

        ## Merging html and api events
        events_df = html_events.merge(api_events[keep_list], left_on = left_list, right_on = right_list, how = 'left')

        ## Merging events and changes
        pbp_df = pd.concat([events_df, changes_df], ignore_index = True)

        ## Sorting the values so they're in the correct order. Uses a given priority, taken from Evolving-Hockey scraper
        priority_dict = {'PGSTR': 1, 'PGEND': 2, 'ANTHEM': 3, 'TAKE': 4, 'GIVE': 4, 'MISS': 4, 'HIT': 4,
                         'SHOT': 4, 'BLOCK': 4, 'GOAL': 5, 'STOP': 6, 'DELPEN': 7, 'PENL': 8, 'PSTR': 9,
                         'CHANGE': 10, 'PEND': 11, 'PEND': 12, 'GEND': 13, 'FAC': 14}

        shootout_priority = {'PSTR': 1}

        pbp_df['priority'] = pbp_df.event.map(priority_dict)

        pbp_df['priority'] = np.where(np.logical_and(pbp_df.session == 'R', pbp_df.period == 5),
                                        pbp_df.event.map(shootout_priority), pbp_df.priority)

        ## Thinking about adding a column so that home changes are always last when occurring during faceoffs
        #pbp_df['change_priority'] = 

        sort_list = ['period', 'game_seconds', 'priority', 'event_idx']

        pbp_df = pbp_df.sort_values(by = sort_list).reset_index(drop = True)
        
        ## Setting a new index for the combined dataframe
        pbp_df.event_idx = pbp_df.index + 1
        
        ## Setting home team values

        replace_dict = {'home': 1, 'away': 0}

        pbp_df['is_home'] = pbp_df.event_team.map(TEAMS_DICT_SHORT).replace(replace_dict)
        
        ## CREATING THE ON-ICE DATAFRAME

        ## Looping through home and away players
        teams_list = ['home', 'away']

        ## Creating a blank dictionary to collect each team's information to eventually concatenate
        teams_dict = dict()

        for team in teams_list:

            ## Each team's dataframe starts a list of player dataframes before it is concatenated
            teams_dict[team] = list()
            
            ## Filtering the roster for the correct players
            mask = roster_df.team == team
            
            player_list = roster_df[mask].api_name
            
            ## Creating series objects of the players on and off columns from the events dataframe
            on_column = pbp_df.players_on_api.str.join(', ')
            
            off_column = pbp_df.players_off_api.str.join(', ')
            
            ## For every player on the team, create series with the same index as the events dataframe.
            ## Whenever the player is on the ice, given a 1, else 0
            for player in player_list:
                
                vector = pd.DataFrame(np.cumsum(np.where(on_column.apply(lambda x: player in str(x)) == True, 1, 0) - 
                                                np.where(off_column.apply(lambda x: player in str(x)) == True, 1, 0)))
                
                ## Append the player's dataframe to the team's list so it can be concatenated with the rest
                teams_dict[team].append(vector)
            
            ## If the team's list of player vectors is empty, continue
            if teams_dict[team] == []:
                
                continue
            
            ## Creates a team's dataframe by concatenating the player vectors                  
            matrix = pd.concat(teams_dict[team], axis = 1)
            
            ## Renames the columns to match the correct player's names. (They're 0's right now)
            matrix.columns = player_list

            ## Create a series of players on-ice by filtering out the zeroes for each row,
            ## then taking the tuple of the remaning column names as a list
            players_on = pd.DataFrame((matrix == 1).apply(lambda x: tuple(matrix.columns[x.tolist()].to_list()), axis = 1))[0]

            ## Making a dataframe out of the above dataframe
            on_df = players_on.apply(pd.Series)

            ## Adding a column of the tuples from above
            on_df[f'{team}_on'] = players_on

            ## Renaming the columns of the dataframe
            column_names = {x: f'{team}_on_{x + 1}' for x in list(range(0, len(on_df.columns) + 1))}

            on_df = on_df.rename(columns = column_names)
            
            ## Creating a column for how many skaters are on-ice
            on_df[f'{team}_on_num'] = on_df[f'{team}_on'].apply(lambda x: len(x))

            ## Update the teams dictionary with the on-ice dataframe
            teams_dict.update({team: on_df})
            
        ## If the teams dicionary doesn't have any dataframes, the continue 
        if type(teams_dict['home']) == list or type(teams_dict['away']) == list:
            
            if _print == True:
                
                message_text = f'No shifts information, unable to scrape {game_id} ({game_number}/{number_of_games})...'
                
                print_game_id_time(game_start, game_id, number_of_games, game_number, message_text = message_text)
                
            continue

        ## Concatenating the on-ice dataframes together
        teams_df = pd.concat([teams_dict['home'], teams_dict['away']], axis = 1)

        ## Concatenating the on-ice dataframes and the events dataframe        
        pbp_df = pd.concat([pbp_df, teams_df], axis = 1)
        
        ## Setting game date
        pbp_df['game_date'] = GAME_DATE

        pbp_df['penalty_shot'] = np.where(pbp_df.description.str.contains('penalty shot', case = False, regex = False), 1, 0)

        pbp_df['shootout'] = np.where(np.logical_and(pbp_df.session == 'R', pbp_df.period == 5), 1, 0)
        
        pbp_df['is_goal'] = np.where(np.logical_and(pbp_df.event == 'GOAL', pbp_df.shootout != 1), 1, 0)
        
        teams_list = ['home', 'away']
        
        for team_type, team_name in TEAMS_DICT_SHORT_REV.items():
            
            pbp_df[team_type + '_score'] = np.where(np.logical_and(pbp_df.event_team == team_name, pbp_df.is_goal == 1), 1, 0)
            
            pbp_df[team_type + '_score'] = pbp_df[team_type + '_score'].cumsum()

        pbp_df['is_goal'] = np.where(pbp_df.event == 'GOAL', 1, pbp_df.is_goal)

        home_so_winner = pbp_df[np.logical_and(pbp_df.is_home == 1, pbp_df.shootout == 1)].is_goal.sum() > \
                            pbp_df[np.logical_and(pbp_df.is_home == 0, pbp_df.shootout == 1)].is_goal.sum() 

        away_so_winner = pbp_df[np.logical_and(pbp_df.is_home == 0, pbp_df.shootout == 1)].is_goal.sum() > \
                            pbp_df[np.logical_and(pbp_df.is_home == 1, pbp_df.shootout == 1)].is_goal.sum() 

        pbp_df.home_score = np.where(np.logical_and(home_so_winner, pbp_df.event == 'SOC'), pbp_df.home_score + 1, pbp_df.home_score)

        pbp_df.away_score = np.where(np.logical_and(away_so_winner, pbp_df.event == 'SOC'), pbp_df.away_score + 1, pbp_df.away_score)

        
        pbp_df['score_state'] = np.where(pbp_df.is_home == 0,
                                         pbp_df['away_score'].astype(str) + 'v' + pbp_df['home_score'].astype(str), 
                                         pbp_df['home_score'].astype(str) + 'v' + pbp_df['away_score'].astype(str))


        pbp_df['score_diff'] = np.where(pbp_df.is_home == 0,
                                        pbp_df['away_score'] - pbp_df['home_score'],
                                        pbp_df['home_score'] - pbp_df['away_score'])
        
        
        positions_dict = dict(zip(roster_df.api_name, roster_df.player_position))
        
        columns = [f'home_on_{x}' for x in list(range(1, 10))] + [f'away_on_{x}' for x in list(range(1, 10))]
        
        columns = [x for x in columns if x in pbp_df.columns]
        
        for col in columns:
            
            pbp_df[col + '_pos'] = pbp_df[col].map(positions_dict)
        
        
        home_dict = [x + '_pos' for x in columns if 'home' in x]
        away_columns = [x + '_pos' for x in columns if 'away' in x]
        
        team_list = ['home', 'away']
        
        for team in team_list:
            
            pbp_df[team + '_empty_net'] = 1
            pbp_df[team + '_goalie'] = np.nan
            pbp_df[team + '_goalie_on'] = 0
            
            cols_dict = {x + '_pos': x for x in columns if team in x}
            
            for position, player in cols_dict.items():
                
                pbp_df[team + '_empty_net'] = np.where(pbp_df[position] == 'G', 0, pbp_df[team + '_empty_net'])
                pbp_df[team + '_goalie'] = np.where(pbp_df[position] == 'G', pbp_df[player], pbp_df[team + '_goalie'])
                pbp_df[team + '_goalie_on'] = np.where(pbp_df[position] == 'G', 1, pbp_df[team + '_goalie_on'])
                
            pbp_df[team + '_skaters'] = pbp_df[team + '_on_num'] - pbp_df[team + '_goalie_on']
                
                
        pbp_df['strength_state'] = np.where(pbp_df.is_home == 0,
                                            pbp_df.away_skaters.astype(str) + 'v' + pbp_df.home_skaters.astype(str),
                                            pbp_df.home_skaters.astype(str) + 'v' + pbp_df.away_skaters.astype(str))

        conds = [np.logical_and(pbp_df.is_home == 1, pd.isna(pbp_df.away_goalie)), 
                    np.logical_and(pbp_df.is_home == 0, pd.isna(pbp_df.home_goalie))]

        values = [1, 1]

        pbp_df['empty_net'] = np.select(conds, values, 0)
        
        #correcting event zones for blocked shots

        is_blocked = pbp_df['event'] == 'BLOCK'
        is_def_zone = pbp_df['event_zone'] == 'DEF'
        
        cond = np.logical_and(is_blocked, is_def_zone)

        pbp_df['event_zone'] = np.where(cond, 'OFF', pbp_df['event_zone'])   
        
        ##play-by-play distance 

        ##using regex to capture digits before 'ft'

        pbp_df['pbp_distance'] = pbp_df.description.str.extract('(\d+)\s*ft')
        pbp_df['pbp_distance'] = pd.to_numeric(pbp_df['pbp_distance'])
        ##correcting for fenwick events with na distance

        conds = np.logical_and(np.isin(pbp_df['event'], FENWICK_EVENTS), pd.isna(pbp_df['pbp_distance']))
        pbp_df['pbp_distance'] = np.where(conds, 0, pbp_df['pbp_distance'])
        
        ##initial event distance & event angle calculations

        pbp_df['event_distance'] = ((89 - abs(pbp_df['coords_x']))**2 + pbp_df['coords_y']**2) ** (1/2)

        pbp_df['event_angle'] = np.degrees(abs(np.arctan(pbp_df['coords_y'] / (89 - abs(pbp_df['coords_x'])))))
        
        ##correcting event distances for mistakes

        is_fenwick = np.isin(pbp_df['event'], FENWICK_EVENTS)
        is_long_distance = pbp_df['pbp_distance'] > 89
        x_is_neg = pbp_df['coords_x'] < 0 
        x_is_pos = pbp_df['coords_x'] > 0 
        not_tip = pbp_df['event_detail'] != 'Tip-In' 
        not_wrap = pbp_df['event_detail'] != 'Wrap-around'
        not_defl = pbp_df['event_detail'] != 'Deflected'
        zone_cond = np.logical_and(pbp_df['pbp_distance'] > 89, pbp_df['event_zone'] == 'OFF')

        x_is_neg_conds = (is_fenwick & is_long_distance & x_is_neg & not_tip & not_wrap & not_defl & ~zone_cond)
        x_is_pos_conds = (is_fenwick & is_long_distance & x_is_pos & not_tip & not_wrap & not_defl & ~zone_cond)
        conds_list = [x_is_neg_conds, x_is_pos_conds]

        x_is_neg_value = ((abs(pbp_df['coords_x']) + 89) ** 2 + pbp_df['coords_y'] ** 2) ** (1/2)
        x_is_pos_value = ((pbp_df['coords_x'] + 89) ** 2 + pbp_df['coords_y'] ** 2) ** (1/2)
        values_list = [x_is_neg_value, x_is_pos_value]

        pbp_df['event_distance'] = np.select(conds_list, values_list, default = pbp_df['event_distance'])
        
        ##correcting event angles for mistakes, using same conditions as the event distance corrections

        x_is_neg_value = np.degrees(abs(np.arctan(pbp_df['coords_y']/(abs(pbp_df['coords_x'] + 89)))))
        x_is_pos_value = np.degrees(abs(np.arctan(pbp_df['coords_y']/(pbp_df['coords_x'] + 89))))
        values_list = [x_is_neg_value, x_is_pos_value]


        pbp_df['event_angle'] = np.select(conds_list, values_list, default = pbp_df['event_angle'])
        
        ##correcting event zones

        is_fenwick = np.isin(pbp_df['event_type'], FENWICK_EVENTS)
        is_def_zone = pbp_df['event_zone'] == 'DEF'
        is_less_than_64 = pbp_df['pbp_distance'] <= 64
        conds = (is_fenwick & is_def_zone & is_less_than_64)

        pbp_df['event_zone'] = np.where(conds, 'OFF', pbp_df['event_zone'])
        
        ##setting home zone

        is_home_team = np.equal(pbp_df['home_team_abbreviated'], pbp_df['event_team'])
        is_away_team = np.equal(pbp_df['away_team_abbreviated'], pbp_df['event_team'])
        is_def_zone = np.equal(pbp_df['event_zone'], 'DEF')
        is_off_zone = np.equal(pbp_df['event_zone'], 'OFF')

        cond_1 = np.logical_and(is_away_team, is_off_zone)
        cond_2 = np.logical_and(is_away_team, is_def_zone)

        conds_list = [cond_1, cond_2]
        values_list = ['DEF', 'OFF']

        pbp_df['home_zone'] = np.select(conds_list, values_list, default = pbp_df['event_zone'])
        
        ##correcting penalty shot strength states

        is_penalty_shot = np.logical_and(pbp_df.penalty_shot == 1, pbp_df.event.isin(FENWICK_EVENTS))

        pbp_df.strength_state = np.where(is_penalty_shot, '1v0', pbp_df.strength_state)

        pbp_df.strength_state = np.where(pbp_df.shootout == 1, '1v0', pbp_df.strength_state)

        is_home_team = np.equal(pbp_df['home_team_abbreviated'], pbp_df['event_team'])
        is_away_team = np.equal(pbp_df['away_team_abbreviated'], pbp_df['event_team'])
        conds_list = [(is_penalty_shot & is_home_team), (is_penalty_shot & is_away_team)]

        values_list = [1, 0]
        pbp_df.home_skaters = np.select(conds_list, values_list, default = pbp_df.home_skaters)

        values_list = [0, 1]
        pbp_df.away_skaters = np.select(conds_list, values_list, default = pbp_df.away_skaters)
        
        pbp_df['zone_start'] = np.where(np.logical_and(pbp_df.event == 'CHANGE', ~pd.isna(pbp_df.players_on)), 'OTF', np.nan)
        
        for x in list(range(1, 7)):
            
            near_faceoff = np.logical_and(pbp_df.event == 'CHANGE', pbp_df.event.shift(-x) == 'FAC')
            
            same_time = np.logical_and(pbp_df.game_seconds == pbp_df.game_seconds.shift(-x), pbp_df.period == pbp_df.period.shift(-x))
            
            pbp_df['zone_start'] = np.where(np.logical_and(near_faceoff, same_time),
                                            pbp_df.event_zone.shift(-x),
                                            pbp_df.zone_start)

        ##setting home zone starts, to be completed later
        
        pbp_df['face_idx'] = np.cumsum(np.where(pbp_df.event == 'FAC', 1, 0))
        
        pbp_df['shift_idx'] = np.where(pbp_df.event == 'CHANGE', 1, 0)
        pbp_df['shift_idx'] = pbp_df.groupby('event_team')['shift_idx'].cumsum()
        
        pbp_df['pen_idx'] = np.cumsum(np.where(pbp_df.event == 'PENL', 1, 0))
        
        CONCAT_LIST.append(pbp_df)
        
        if _print == True:

            print_game_id_time(game_start, game_id, number_of_games, game_number)
    
    concat_start = time.perf_counter()
    
    if _print == True:
        
        print_concat_start(number_of_games, scrape_start)
    
    if CONCAT_LIST == []:
        
        pbp_df = pd.DataFrame()
        
    else:
        
        pbp_df = pd.concat(CONCAT_LIST, ignore_index = True)
        
        column_names = {'home_team': 'home_team_name', 'away_team': 'away_team_name',
                        'home_team_abbreviated': 'home_team', 'away_team_abbreviated': 'away_team'}
        
        pbp_df.rename(columns = column_names, inplace = True)
        
        columns = ['season', 'session', 'game_date', 'game_id', 'event_idx','period', 'time', 'event_team', 'event', 'description', 'strength',
                   'strength_state', 'event_player_1', 'event_player_2', 'event_player_3', 'coords_x', 'coords_y', 'opp_team', 'empty_net', 'score_diff',
                   'event_zone', 'score_state', 'event_distance', 'event_angle', 'pbp_distance', 'is_home', 'is_goal', 'home_score', 'away_score',
                   'home_skaters', 'home_on', 'home_goalie', 'home_on_1', 'home_on_1_pos', 'home_on_2', 'home_on_2_pos',
                   'home_on_3', 'home_on_3_pos', 'home_on_4', 'home_on_4_pos', 'home_on_5', 'home_on_5_pos', 'home_on_6', 'home_on_6_pos',
                   'home_on_7', 'home_on_7_pos', 'home_on_8', 'home_on_8_pos', 'away_skaters', 'away_on', 'away_goalie',
                   'away_on_1', 'away_on_1_pos', 'away_on_2', 'away_on_2_pos', 'away_on_3', 'away_on_3_pos', 'away_on_4',
                   'away_on_4_pos', 'away_on_5', 'away_on_5_pos', 'away_on_6', 'away_on_6_pos', 'away_on_7', 'away_on_7_pos',
                   'away_on_8', 'away_on_8_pos', 'penalty_shot', 'shootout', 'shootout_winner', 'home_empty_net', 'away_empty_net', 'period_seconds', 'game_seconds',
                   'home_team', 'home_team_name', 'away_team', 'away_team_name', 'penalty_severity', 'penalty_minutes', 
                   'datetime', 'event_player_1_type', 'event_player_2_type', 'event_player_3_type', 'event_player_1_api_name',
                   'event_player_2_api_name', 'event_player_3_api_name', 'number_on', 'players_on_api', 'number_off', 'players_off_api', 
                   'home_zone', 'event_detail', 'zone_start', 'penalty_type', 'face_idx', 'shift_idx', 'pen_idx', 'version']
        
        columns = [x for x in columns if x in pbp_df.columns]
        
        pbp_df = pbp_df[columns]
        
    if _print == True:
        
        print_concat_finish(concat_start, number_of_games)
        
        print_number_of_games(number_of_games, scrape_start)
    
    return pbp_df






