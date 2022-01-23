# noinspection DuplicatedCode
"""
pywowgen | Configure and generate Workadventue maps

# Command Line Interface

    pywowgen -h

# Use within Python

## Package

* pywowgen

## Modules

* cli -> CLI :-)
* helpers -> environment setup, ...
* remotes -> work with git, ...
* waapi
* wamap
* waresource
* wamapgenerator
* waworld

## Main classes

* wamap -> references a workadventure map
* waresource -> references a folder structure with resources needed in maps / this tool
* wamapgenerator -> generates maps and their resources, implement a __generate__() function for each derived generator
* waworld -> carries the configuration of maps, resources and generators and bundles the map creation and editing features

## Implemented map generators

These are derived from wamapgenerator

* waelevator
* wavideotext
* wasidescroller
* wamapfromtemplate

* wacopypastegenerator ->  Copy and paste this template for new generators

## Examples and tests

Some python objects have "doctests" which serve as usage examples, also.

"""

import os
import logging
import argparse
import sys
import webbrowser
from pathlib import Path

from pywowgen.helpers import run_world_gen, run_overview, do_test, waworld, waapi, prepare_paths


def myargs():
    # command line arguments
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    subparsers = parser.add_subparsers(help='sub-command help', dest="subparser_name")

    ## main args
    parser.add_argument("--loglevel", choices=['DEBUG', 'INFO', 'ERROR', 'WARNING'], default='INFO')

    ## world args
    parser_world = subparsers.add_parser('world', help='Generate a World from config file')
    parser_world.add_argument("--file", help="Path to json config file", required=False,
                              type=argparse.FileType('r', encoding='UTF-8'), default='../../examples/default.json')
    parser_world.add_argument("--res", action='append', help="Path(s) to res/", required=False, )
    parser_world.add_argument("--tmp", help="Path to tmp/", required=False, default='../')
    parser_world.add_argument("--fin", help="Path to fin/", required=False, default='../')

    ## overview args
    parser_overview = subparsers.add_parser('overview', help='List Templates and their Features')
    parser_overview.add_argument("--path", help="Path to res/", required=False, default='../')

    ## analysis args
    parser_analysis = subparsers.add_parser('check', help='Analyze maps')
    parser_analysis.add_argument("--path", help="Path to a folder/ with maps and resources to be analyzed",
                                 required=False,
                                 default='../')

    ## api args
    parser_api = subparsers.add_parser('api',
                                       help='Runs a tiny webserver and starts a simpleWeb UI for World creation and analysis')
    parser_api.add_argument("--res", action='append', help="Path(s) to res/", required=False, )
    parser_api.add_argument("--tmp", help="Path to tmp/", required=False, default='../')
    parser_api.add_argument("--fin", help="Path to fin/", required=False, default='../')
    parser_api.add_argument("--force", type=bool, choices=[True, False],
                            help="Overwrite config file options with cli options", required=False, default=False)
    parser_api.add_argument("--skipui", type=bool, choices=[True, False],
                            help="do not lanuch webbrowswr", required=False, default=False)

    ## test args
    parser_test = subparsers.add_parser('test', help='use with --dev if not installed via pip')

    return parser.parse_args()


def main():
    # where am I?

    args = myargs()

    # logging
    loglevel = args.loglevel
    logging.basicConfig(level=loglevel, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    logging.debug(str('setup: ') + ' sys: ' + sys.version + ' ' + sys.platform)

    if args:
        # set envs, dirs
        prepare_paths()

    # start working based on command line options
    if args.subparser_name == 'world':
        logging.info('generating world from file {args.file.name}')
        # cli options overwrite config options
        logging.debug('using cli options {args.res} {args.tmp} {args.fin}')
        run_world_gen(str(args.file.name), args.res, args.tmp, args.fin)
    elif args.subparser_name == 'overview':
        logging.info('analysing templates {args.path}')
        run_overview(str(args.path))
    elif args.subparser_name == 'api':
        logging.info('starting api')
        if not args.skipui:
            webbrowser.open(os.path.join(os.environ.get('WOWGEN_EXTRA'), 'res/html/editor.html'), new=0, autoraise=True)
        # cli options overwrite config options
        waapi.waapirun(args.force, args.res, args.tmp, args.fin)
    elif args.subparser_name == 'check':
        logging.info('analyzing maps')
        # init empty world
        logging.debug('init empty world')
        apiworld = waworld.waworld()
        for obj in apiworld.check_maps(sourcepath=str(args.path)):
            if obj['data']['label'] == 'ERROR' or obj['data']['label'] == 'WARNING':
                logging.info(obj)
        logging.info('recommendations')
        for tmmp in apiworld.analysis_maps:
            for rrrsp in tmmp.message():
                try:
                    if len(rrrsp['recommendations']) > 0:
                        logging.info(rrrsp['file'], rrrsp['recommendations'])
                except KeyError:
                    pass
    elif args.subparser_name == 'test':

        logging.debug('tests depend on wowgen_data/ within os temporary folder')
        logging.debug(str(Path.home()))

        do_test()

        logging.info('showing short notes')
        logging.info(__doc__)

    else:
        logging.info(__doc__)


if __name__ == '__main__':
    main()

    # todo: ... working at ...
    # - deployments (gitlab-pipeline to build-> default world, the tool itself)
    # - allow user to add additional / alternative index or res/ git repositories
    # - download zip of rendered world
    # - for each created config and world, use a uuid

    # todo: for rc3-22 :|
    #      each generated map from template and copied map from maps/ should generate an visible level in elevator
    #      and generate a videotext page for it, with appropiate exits and start points set up
    #      and a sidescroller with a chatbot, and the elevator should make movements of players more visible (transparency on level-walls?)
    #      And template maps should have basic scripts like opening doors...

    # todo: ... in ... random ... order ...
    # - new option to add default feautres to an existing maps
    # - new option to initiate a new map (use emtptyTemplate.json as default and checkboxes for features to apply. and map size. )
    # - adapt old template files to new structure / features / ... -> see the emptyTemplate.json
    # - for final deployment / folder option: add .htaccess and gitlab-pipeline config
    # - oh, just found https://git.cccv.de/hub/walint, check whats there
