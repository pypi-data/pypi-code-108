#!python

import argparse
import pathlib
import os
import sys
import distutils.dir_util as du
import fabrique_actor


def main(cli_args):
    resource_dir = os.path.join(str(fabrique_actor.__path__[0]), 'data')
    cur_dir = str(pathlib.Path().absolute())
    atypes = [d for d in os.listdir(resource_dir) if os.path.isdir(os.path.join(resource_dir, d))
              and d != 'common' and d[0] != '_']

    parser = argparse.ArgumentParser(description='Create default actor project files')
    parser.add_argument('type', metavar='type', help=f'actor type one of [{", ".join(atypes)}]')

    args = parser.parse_args(cli_args)

    if args.type in atypes:
        du.copy_tree(os.path.join(resource_dir, 'common'), cur_dir)
        du.copy_tree(os.path.join(resource_dir, args.type), cur_dir)
        try:
            du.remove_tree(os.path.join(cur_dir, '__pycache__'))
        except FileNotFoundError:
            pass
        print(f"{args.type} boilerplate created")
    else:
        print(f"{args.type} is not one of {atypes}")


if __name__ == '__main__':
    # main()
    sys.exit(main(sys.argv[1:]))
