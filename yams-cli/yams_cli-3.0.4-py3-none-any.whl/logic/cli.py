#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import logging
import urllib, urllib.parse

from yams_cli.utils import configure_logging, is_action_confirmed, get_version
from yams_cli.logic.injection import get_injector
from yams_cli.logic.dispatcher import Dispatcher
from yams_cli.logic.args import parse_cli_arguments


def main():
    options = parse_cli_arguments()

    if options['debug']:
        configure_logging('debug')
    else:
        configure_logging('info')

    if options.get('object_id') != None:
        options['object_id'] = urllib.parse.quote(urllib.parse.unquote(options['object_id']))

    log = logging.getLogger('yams-cli.main')
    log.debug(options)
    log.debug('Running client version: {}'.format(get_version()))

    dispatcher = _init_dispatcher(options)
    if not _dispatch(dispatcher, options):
        sys.exit(1)


def _init_dispatcher(options):
    injector = get_injector(options)
    return injector.get(Dispatcher)


def _dispatch(dispatcher, options):
    action = _get_action(options)
    if action == "tenant_delete":
        if not is_action_confirmed(dispatcher.tenant_id, *action.split('_')):
            print("Action {} not confirmed".format(action))
            sys.exit(2)

    if hasattr(dispatcher, action):
        return getattr(dispatcher, action)(options)

    print("Action {} not found".format(action))


def _get_action(options):
    command = options['command'].replace('-', '_')

    if command == 'configure':
        return command

    else:
        if "action" in options and options["action"]:
            action = options['action'].replace('-', '_')
            return '{}_{}'.format(command, action)
        return ""


if __name__ == '__main__':
    main()
