#!/usr/bin/env python
from __future__ import with_statement

import traceback
from argparse import ArgumentParser


def main():
    """Main method to start a2p2 program."""
    parser = ArgumentParser(
        description='Move your Aspro2 observation details to an observatory proposal database')
    # parser.add_argument('-c', '--config', action='store_true', help='show instruments and remote service configurations.')
    parser.add_argument('-f', '--fakeapi', action='store_true',
                        help='fake API to avoid remote connection (dev. only).')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose')
    parser.add_argument('-c', '--createprefs', action='store_true', help='Create preferences file')

    args = parser.parse_args()

    from . import A2p2Client

    if args.createprefs:
        A2p2Client.createPreferencesFile()
        exit()

    try:
        with A2p2Client(args.fakeapi, args.verbose) as a2p2c:
            # if  args.config:
            #    print(a2p2c)
            # else:
            #    a2p2c.run()
            a2p2c.run()

    except Exception as e:
        if True or args.verbose:
            traceback.print_exc()
        else:
            print('ERROR: %s' % str(e))


if __name__ == '__main__':
    main()
