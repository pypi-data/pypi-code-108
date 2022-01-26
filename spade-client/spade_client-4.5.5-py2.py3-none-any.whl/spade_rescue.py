#
# Module: spade_rescue
#
# Description: SPADE command line rescue facility
#

from __future__ import print_function

CACHE_NOT_DERIVED=1
CACHE_NOT_DERIVED_MESSAGE='The SPADE cache directory can not be derived. It must be specified as a command option'
CACHE_NOT_EXIST=2
CACHE_NOT_EXIST_MESSAGE='The SPADE cache directory does not exist'
LAZARUS_NOT_EXIST=3
LAZARUS_NOT_EXIST_MESSAGE='The Lazarus directory does not exist'
SECOND_CACHE=4
SECOND_CACHE_MESSAGE='Second SPADE cache directory: '
DOUBLE_RESCUE=5
DOUBLE_RESCUE_MESSAGE='More than one rescue location found for '
INCOMPETE_RESCUE=6
INCOMPETE_RESCUE_MESSAGE='Not all files from the problem area have been rescued for '
NO_RESCUE_FILES=7
NO_RESCUE_FILES_MESSAGE='There are no file to be rescued from the problem area for '


SEMAPHORE = 'semaphore'
METADATA = 'metadata'
DATA = 'data'
PACKED = 'packed'
COMPRESSED = 'compressed'
TYPES = [SEMAPHORE, METADATA, DATA, PACKED, COMPRESSED]

DIRECTORY = 'directory'
MIXED = 'mixed'
FILENAME = 'filename'

SEMAPHORE_ELEMENT = 'bundle/semaphore'
DELIVERY_ELEMENT = 'delivery'
METADATA_ELEMENT = 'metadata'
DELIVERED_ELEMENT = 'delivered'
PACKED_ELEMENT = 'packed'
COMPRESSED_ELEMENT = 'compressed'

FILES_DIR = 'files'
LAZARUS_DIR = 'lazarus'

import xml.etree.ElementTree as ET
import os
import re
import shutil

INGEST_TOKEN_PATTERN = re.compile('^([^\.]*)\.FileToken_([^\_]*)_(.*)$')

def eprint(*args, **kwargs):
    """Prints to standard error"""
    print(*args, file=sys.stderr, **kwargs)


class FailedRescue(Exception):
    def __init__(self, message, error_code):
        self.code = error_code
        self.message = message


class ProblemProperties(object):

    def add_path(self, name, path, depth = 0):
        if None != path:
            directory = os.path.normpath(os.path.dirname(path))
            location = {}
            location[DIRECTORY] = directory
            location[FILENAME] = os.path.basename(path)
            setattr( self, name, location )
            if 0 != depth:
                cache = directory
                for level in range(0, depth):
                    cache = os.path.dirname(cache)
                if hasattr(self, 'cache'):
                    existing = self.cache
                    if existing != MIXED and existing != cache:
                        self.cache = MIXED
                        eprint(SECOND_CACHE_MESSAGE + existing + ' vs ' + cache)
                else:
                    self.cache = cache


    def fill_ticket_properties(self, filename, find_cache):
        ticket = ET.parse(os.path.join(self.home, filename))
        semaphore = ticket.find(SEMAPHORE_ELEMENT)
        if None != semaphore:
            path = semaphore.attrib[DELIVERY_ELEMENT]
            if find_cache:
                self.add_path(SEMAPHORE, path, 4)
            else:
                self.add_path(SEMAPHORE, path)
        metadata = ticket.find(METADATA_ELEMENT)
        if None != metadata:
            path = metadata.text
            if find_cache:
                self.add_path(METADATA, path, 4)
            else:
                self.add_path(METADATA, path)
        delivered = ticket.find(DELIVERED_ELEMENT)
        if None != delivered:
            path = delivered.text
            if find_cache:
                self.add_path(DATA, path, 4)
            else:
                self.add_path(DATA, path)
        packed = ticket.find(PACKED_ELEMENT)
        if None != packed:
            path = packed.text
            if find_cache:
                self.add_path(PACKED, path, 3)
            else:
                self.add_path(PACKED, path)
        compressed = ticket.find(COMPRESSED_ELEMENT)
        if None != compressed:
            path = compressed.text
            if find_cache:
                self.add_path(COMPRESSED, path, 3)
            else:
                self.add_path(COMPRESSED, path)



    def __init__(self, problem_dir, match, cache_option):
        self.home = os.path.normpath(problem_dir)
        self.number = os.path.basename(problem_dir)
        self.ingest_ticket_file = match.group()
        self.activity = match.group(1)
        self.instance = match.group(2)
        self.token = match.group(3)
        if None != cache_option:
            self.cache = cache_option
        self.fill_ticket_properties(match.group(), None == cache_option)


    def find_rescued_file(self, file):
        directory = None
        filename = os.path.basename(file)
        for type in TYPES:
            if hasattr(self, type):
                location = getattr(self, type)
                if filename == location[FILENAME]:
                    if None == directory:
                        directory = location[DIRECTORY]
                    else:
                        raise FailedRescue(DOUBLE_RESCUE_MESSAGE + self.home, DOUBLE_RESCUE)
        return directory


    def rescue_files(self):
        try:
            files_dir = os.path.join(self.home, FILES_DIR)
            if os.path.exists(files_dir):
                list = os.listdir(files_dir)
                if 0 == len(list):
                    raise FailedRescue(NO_RESCUE_FILES_MESSAGE + self.home, NO_RESCUE_FILES)
                for l in list:
                    directory = self.find_rescued_file(l)
                    if None != directory:
                        print('os.mkdir(' + directory + ')')
                        src = os.path.join(files_dir, l)
                        dst = os.path.join(directory, l)
                        os.rename(src, dst)
                list = os.listdir(files_dir)
                if 0 != len(list):
                    raise FailedRescue(INCOMPETE_RESCUE_MESSAGE + self.home, INCOMPETE_RESCUE)
                shutil.rmtree(files_dir)
                return self.instance
            else:
                raise FailedRescue(NO_RESCUE_FILES_MESSAGE + self.home, NO_RESCUE_FILES)
        except FailedRescue as e:
            eprint(e.message)
            return None


def get_problem_properties(problem_dir, cache_option):
    list = os.listdir(problem_dir)
    for l in list:
        match = INGEST_TOKEN_PATTERN.match(l)
        if match:
            properties = ProblemProperties(problem_dir, match, cache_option)
            return properties
    return None


def resolve_instance(lazarus_dir, instance):
    failed = os.path.join(lazarus_dir, 'ingest.bpmn', 'failed_instances', instance, 'failed')
    try:
        os.remove(failed)
    except OSError:
        pass
    print('Directory ' + os.path.dirname(failed) + " has been rescued")


import sys

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Command Line rescue facility for SPADE.')
    parser.add_argument('-?',
                        help = 'Prints out this help',
                        action = 'help')
    parser.add_argument('-c',
                        '--cache',
                        dest = 'CACHE',
                        help = 'the directory containing the SPADE cache data. This is'
                        + ' normal derived from the context, but if the location can'
                        + ' not be derived is can be set here. This can also be used'
                        + ' to override the derived value if it is not correct.',
                        default = None)
    parser.add_argument('-l',
                        '--lazarus',
                        dest = 'LAZARUS',
                        help = 'the directory containin the Lazarus data. This is'
                        + ' normal derived from the cache, but if the cache can not be'
                        + ' derived is can be set here. This can also be used to override'
                        + ' the derived value if it is not correct.',
                        default = None)
    parser.add_argument('problem_dirs', nargs=argparse.REMAINDER)
    options = parser.parse_args()
    problem_dirs = options.problem_dirs

    # This structure is left here in case not all the positional
    # arguments turn out to be problem_dirs.
    if 0 == len(problem_dirs):
        items = []
    else:
        if 1 == len(problem_dirs):
            items = [problem_dirs[0]]
        else:
            items = problem_dirs[:]

    for i in items:
        properties = get_problem_properties(i, options.CACHE)
        if None != properties:
            if (not hasattr(properties, 'cache')) or properties.cache == MIXED:
                eprint(CACHE_NOT_DERIVED_MESSAGE)
                return CACHE_NOT_DERIVED
            cache = properties.cache
            if not os.path.exists(cache):
                eprint(CACHE_NOT_EXIST_MESSAGE)
                return CACHE_NOT_EXIST

            if None != options.LAZARUS:
                lazarus = options.LAZARUS
            else:
                lazarus = os.path.join(cache, LAZARUS_DIR)
            if not os.path.exists(lazarus):
                eprint(LAZARUS_NOT_EXIST_MESSAGE)
                return LAZARUS_NOT_EXIST

            instance = properties.rescue_files()
            if None != instance:
                resolve_instance(lazarus, instance)
    return 0;


if __name__ == '__main__':
    sys.exit(main())


