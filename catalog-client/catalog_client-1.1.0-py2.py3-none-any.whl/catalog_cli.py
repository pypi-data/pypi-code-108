#
# Module: pp-cli
#
# Description: PSquared command line interface
#

from __future__ import print_function

import sys

def eprint(*args, **kwargs):
    """Prints to standard error"""
    print(*args, file=sys.stderr, **kwargs)


import os
from catalog_client import Catalog, FatalError

def main():
    import sys
    import argparse
    parser = argparse.ArgumentParser(description='Command Line interface to Catalog.')
    parser.add_argument('-v',
                        '--version',
                        dest='VERSION',
                          help='print out the version information of the application.',
                        action='store_true',
                        default=False)
    parser.add_argument('--cacert',
                        dest = 'CA_CERTIFICATE',
                        help = 'path to the file containing one or more CA x509 certificates, if different from the default,'
                        + ' ${HOME}/.catalog/client/cert/cacert.pem',
                        default = None)
    parser.add_argument('--cert',
                        dest = 'CERTIFICATE',
                        help = 'path to the client\'s x509 certificate, if different from the default, ${HOME}/.catalog/client/cert/psquare_client.pem',
                        default = None)
    parser.add_argument('-d',
                        '--debug',
                        dest='DEBUG',
                        help='print out RESTful documents.',
                        action='store_true',
                        default=False)
    parser.add_argument('--key',
                        dest = 'KEY',
                        help = 'path to the client\'s private x509 key, if different from the default, ${HOME}/.psquared/client/private/psquare_client.key',
                        default = None)
    parser.add_argument('-s',
                        '--select',
                        dest='SELECT',
                        help = 'the name of a file containing an XML selection to apply to the command',
                        default = None)
    parser.add_argument('args', nargs=argparse.REMAINDER)
    options = parser.parse_args()
    args = options.args

    if 1 > len(args):
        commands = []
    else:
        commands = args[:]

    url = os.getenv('CATALOG_APPLICATION', 'http://localhost:8080/catalog/local/report/')
    try:
        triggerTags = eval(os.getenv('CATALOG_TRIGGER_TAGS', None))
    except TypeError:
        triggerTags = None
    print(triggerTags)
    catalog = Catalog(url, 'url',  xml=options.DEBUG, triggers = triggerTags,
                      cert = options.CERTIFICATE, key = options.KEY, cacert = options.CA_CERTIFICATE )
    if options.DEBUG:
        catalog.debug_separator()

    try:
        if 0 != len(args):
            print (args)
            selection = eval( 'catalog.' + args[0])
            print (selection)
            result = []
            result.extend(selection)

        elif None != options.SELECT:
            catalog.get_selection_from_file(options.SELECT)

    except FatalError as e:
        eprint(e.message)
        sys.exit(e.code)


if __name__ == '__main__':
    main()
