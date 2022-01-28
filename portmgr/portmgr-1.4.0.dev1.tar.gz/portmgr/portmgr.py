#!/usr/bin/python3

import os, sys
# import docker
# import dckrjsn
import argparse
import importlib
import yaml
from time import sleep


class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('Error: %s\n' % message)
        self.print_help()
        sys.exit(2)


sub_names = [x.strip() for x in os.environ.get('PORTMGR_SUB_NAME', 'dckrsub.yml').split(',')]
compose_names = [x.strip() for x in os.environ.get('PORTMGR_COMPOSE_NAME', 'docker-compose.yml, docker-compose.yaml').split(',')]

# sub_scheme_name = 'dckrsub.schema.yml'

src_path = os.path.dirname(os.path.abspath(__file__))


# conf_scheme_path = os.path.join(src_path, sub_scheme_name)
# sub_scheme_path = os.path.join(src_path, sub_scheme_name)

# conf_scheme = dckrjsn.read_json(conf_scheme_path)
# sub_scheme = dckrjsn.read_json(sub_scheme_path)

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


command_list = {}
action_list = []


def addCommand(cur_directory):
    if not any(action['directory'] == cur_directory for action in action_list):
        relative_dir = os.path.relpath(cur_directory, base_directory)
        if relative_dir == '.':
            relative_dir = os.path.basename(os.path.normpath(cur_directory))
        action_list.append({
            'directory': cur_directory,
            'relative': relative_dir
        })


def read_yaml(path):
    with open(path, 'r') as stream:
        try:
            return yaml.load(stream, Loader=yaml.SafeLoader)
        except yaml.YAMLError as exc:
            print(exc)


def traverse(cur_directory):
    # print("Traversing in " + cur_directory)
    for sub_name in sub_names:
        sub_path = os.path.join(cur_directory, sub_name)
        compose_paths = [os.path.join(cur_directory, name) for name in compose_names]

        # print("Checking file at " + sub_path)
        if os.path.isfile(sub_path):  # has sub folders
            # print("Has sub folders!")
            # sub_folders = dckrjsn.read_json(sub_path, sch = sub_scheme)
            sub_folders = read_yaml(sub_path)
            for sub_folder in sub_folders:
                # print("Checking out " + sub_folder)
                next_directory = os.path.join(cur_directory, sub_folder)
                traverse(next_directory)
        elif any(os.path.isfile(path) for path in compose_paths):  # has a docker-compose file
            addCommand(cur_directory)


def main():
    # global cli
    global base_directory

    # cli = docker.Client('unix://var/run/docker.sock')

    # Include external source files for commands
    # These fill the m_cmd list
    for file in os.listdir(os.path.join(src_path, 'commands')):
        ext_file = os.path.splitext(file)

        if ext_file[1] == '.py' and not ext_file[0] == '__init__':
            importlib.import_module('portmgr.commands.' + ext_file[0])

    parser = MyParser()
    parser.add_argument('-D',
                        dest='base_directory',
                        action='store',
                        default='',
                        help='Set working directory')
    # parser.add_argument('-R',
    #    dest='recursive',
    #    action='store_true',
    #    help='Use dckrsub.json files to recursively apply operations')

    for cmd in command_list.items():
        parser.add_argument('-' + cmd[0],
                            dest='a_cmd',
                            action='append_const',
                            const=cmd[0],
                            help=cmd[1]['hlp'])

    argv = sys.argv[1:]
    if len(argv) == 1 and not argv[0].startswith('-'):
        argv[0] = '-' + argv[0]
    args = parser.parse_args(argv)

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    base_directory = os.path.join(os.getcwd(), args.base_directory)

    # if args.recursive:
    traverse(base_directory)
    # else:
    #    addCommand(base_directory)

    last_cmd = ''
    for cmd in args.a_cmd:  # loop over all passed arguments (t, r, u)
        cur_cmd = command_list[cmd]
        cmd_function = cur_cmd['fnc']
        cmd_order = cur_cmd['ord'];

        #        if last_cmd == 'r' and cur_cmd == 'u':
        #          print("Waiting 3 seconds.. ")
        #          sleep(3)

        if cmd_order == 'nrm':
            action_list_sorted = action_list
        elif cmd_order == 'rev':
            action_list_sorted = reversed(action_list)
        else:
            exit(1)

        failed_list = []

        for action in action_list_sorted:
            origWD = os.getcwd()
            newWD = action['directory']
            os.chdir(newWD)
            print('-> ' + action["relative"])
            if cmd_function(action) != 0:  # execute the function through reflection
                failed_list.append(action)
            os.chdir(origWD)
        if failed_list:
            print('Failed containers:')
            for action in failed_list:
                print('- ' + action['relative'])

    exit(0)
