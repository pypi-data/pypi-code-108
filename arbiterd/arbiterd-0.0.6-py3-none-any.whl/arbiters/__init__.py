# -*- coding: utf-8 -*-
# Copyright 2021 - 2021, Sean Mooney and the arbiterd contributors
# SPDX-License-Identifier: Apache-2.0
import importlib
import logging
import pkgutil

ALL_ARBITERS = {}


def init_arbiters():
    global ALL_ARBITERS
    current_module = importlib.import_module(__loader__.name)
    logging.debug(f'module name: {current_module.__name__}')
    arbiters = list(pkgutil.iter_modules(current_module.__path__))
    logging.debug(f'arbiters: {arbiters}')
    for _, module_name, _ in arbiters:
        logging.debug(f'importing module {module_name}')
        arbiter = importlib.import_module(
            f'{current_module.__name__}.{module_name}')
        arbiter.register(ALL_ARBITERS)
    logging.debug(f'All Arbiters: {ALL_ARBITERS}')


def get_all_arbiters():
    if not ALL_ARBITERS:
        logging.debug('initialising arbiters')
        init_arbiters()
    return ALL_ARBITERS
