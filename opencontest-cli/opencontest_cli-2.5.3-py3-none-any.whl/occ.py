#!/usr/bin/python3

import os
from argparse import ArgumentParser
from requests import post


# Set up arguments
parser = ArgumentParser(description='A very simple OpenContest command line client written in Python')
parser.add_argument('command', choices=['save', 'about', 'info', 'solves', 'history',
                    'register', 'submit', 'status', 'submissions', 'code'])
parser.add_argument('-C', '--config', help='Config file path')
parser.add_argument('-U', '--username', help='Your username')
parser.add_argument('-H', '--homeserver', help='URL of your registration server')
parser.add_argument('-P', '--password', help='Your username')
parser.add_argument('-N', '--name', help='Your name for registering an account')
parser.add_argument('-E', '--email', help='Your email for registering an account')
parser.add_argument('-s', '--server', help='URL of the server you are connecting to')
parser.add_argument('-c', '--contest', help='Contest to query')
parser.add_argument('-p', '--problem', help='Problem to query')
parser.add_argument('-f', '--file', help='File for code submission')
parser.add_argument('-n', '--number', help='Submission number to query')
args = parser.parse_args()


# Process config file
if args.config is None:
    args.config = os.path.join(os.environ.get('XDG_CONFIG_HOME') or os.path.join(os.environ['HOME'], '.config'), 'occ.conf')
else:
    args.config = os.path.expanduser(args.config)
if os.path.exists(args.config):
    # Read in values from file
    with open(args.config, 'r') as f:
        lines = f.readlines()
        if args.username is None:
            args.username = lines[0][:-1]
        if args.homeserver is None:
            args.homeserver = lines[1][:-1]
        if args.password is None:
            args.password = lines[2][:-1]


if args.command == 'save':
    # Save values to config file
    with open(args.config, 'w') as f:
        f.write(args.username + '\n' + args.homeserver + '\n' + args.password + '\n')
    exit()


# Construct request fields based on the OpenContest standard
# https://laduecs.github.io/OpenContest/
probleminfo = ['contest', 'problem']
userinfo = ['username', 'homeserver', 'token']
requests = {
    'about': [],
    'info': probleminfo,
    'solves': probleminfo,
    'history': probleminfo,
    'register': ['name', 'email', 'username', 'password'],
    'submit': userinfo + probleminfo + ['language', 'code'],
    'status': userinfo + probleminfo,
    'submissions': userinfo + probleminfo,
    'code': userinfo + probleminfo + ['number']
}


# Create the request body
body = {'type': args.command}
for field in requests[args.command]:
    if field == 'problem' and args.problem is None:
        continue  # Problem is an optional argument
    elif field == 'token':
        # Prepare list of servers to authorize
        authorized_servers = args.server
        if args.problem is not None and '' in args.problem:
            authorized_servers += ' ' + args.problem.split()[2]
        # Get token
        body['token'] = post(('https://' if args.homeserver.find('://') == -1 else '') + args.homeserver, json={
            'type': 'authenticate', 'username': args.username, 'password': args.password, 'server': authorized_servers
        }).text[1:-1]
    elif field == 'language':
        body['language'] = os.path.splitext(args.file)[1][1:]  # Get language from file extension
    elif field == 'code':
        body['code'] = open(args.file, 'r').read()  # Read file for code
    else:
        body[field] = eval('args.' + field)  # Yay, eval!


# Send the POST request
r = post(('https://' if args.server.find('://') == -1 else '') + args.server, json=body)
print(r.reason)
print(r.text)
exit()
