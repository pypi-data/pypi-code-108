#!usr/bin/python

# Copyright 2021 Deep Intelligence
# See LICENSE for details.

from datetime import datetime
from urllib.parse import urlparse
from dateutil.parser import parse as python_date_parser


def parse_date(d):
    if d is None:
        return None
    elif isinstance(d, str):
        try:
            return datetime.fromisoformat(d.replace('Z', ''))
        except:
            try:
                return python_date_parser(d)
            except:
                return None
    else:
        if d > 1000000000:
            d = int(d / 1000)
        return datetime.fromtimestamp(d)


def parse_url(url):

    # parse url and create main result
    ids = {}
    pieces = urlparse(url)
    hostname = pieces.netloc

    if '/api/v1' in url:

        # extract from path
        path_pieces = pieces.path.replace('/api/v1/', '').split('/')

        for arg in range(len(path_pieces))[::2]:

            if path_pieces[arg] == 'workspace':
                ids['workspace_id'] = path_pieces[arg + 1]

            elif path_pieces[arg] == 'source':
                ids['source_id'] = path_pieces[arg + 1]

            elif path_pieces[arg] == 'models':
                ids['model_id'] = path_pieces[arg + 1]

            elif path_pieces[arg] == 'tasks' or path_pieces[arg] == 'task':
                ids['task_id'] = path_pieces[arg + 1]

            elif path_pieces[arg] == 'alerts':
                ids['alert_id'] = path_pieces[arg + 1]

            elif path_pieces[arg] == 'dashboard':
                ids['dashboard_id'] = path_pieces[arg + 1]
                
            elif path_pieces[arg] == 'visualization':
                ids['visualization_id'] = path_pieces[arg + 1]

    else:
        path_pieces = pieces.path.split('/')
        for arg in range(len(path_pieces)):
            if path_pieces[arg] == 'o':
                ids['organization_id'] = path_pieces[arg + 1]
            
        # extract from args
        query_pieces = {}

        for arg in pieces.query.split('&'):
            arg_pieces = arg.split('=')
            query_pieces[arg_pieces[0]] = arg_pieces[1] if len(arg_pieces) > 1 else None

        if 'ws' in query_pieces:
            ids['workspace_id'] = query_pieces['ws']

        if 's' in query_pieces and 'i' in query_pieces:
            ids[f'{query_pieces["s"]}_id'] = query_pieces['i']

    return ids, hostname
