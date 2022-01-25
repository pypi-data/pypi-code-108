# -*- coding: utf-8 -*-
"""
    fava.cli
    ~~~~~~~~~
    A simple command line application to run falafel apps.
    :copyright: 2022 tomkiel
    :license: MIT
"""
import sys
import argparse
from fava.core import runner


def runner_interface(shell_arguments):
    """
    Check the current command isn't empty and run the runner.
    :param shell_arguments: shell_arguments
    :return: void
    """

    args = parse_command_line(shell_arguments)

    if args.db_migrate is not None:
        runner.migrate(args.db_migrate)

    elif args.db_seed is not None:
        runner.runSeeder(args.db_seed)

    elif args.make_migration is not None:
        runner.create_migration(args.make_migration)

    elif args.make_model is not None:
        runner.create_model(args.make_model)

    elif args.make_seeder is not None:
        runner.createSeed(args.makeseeder)

    elif args.make_controller is not None:
        runner.create_controller(args.make_controller)

    elif args.make_route is not None:
        runner.create_route(args.make_route)

    elif args.server is not None:
        runner.run_server(args.server)

    elif args.generate_key is not None:
        runner.generate_secret_key()

    else:
        print('Invalid command')


def parse_command_line(args):
    """
    Set available commands
    """

    description = "Use -h to list all commands."
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-v', '--version', action='version', version='0.2.2')
    parser.add_argument('-s', '--server', nargs='?', type=str, help='Run application in development', const='5000')
    parser.add_argument('-mkmigration', '--make_migration', nargs='?', type=str, help='Create a new migration file')
    parser.add_argument('-mkseeder', '--make_seeder', nargs='?', type=str, help='Create a new seeder class')
    parser.add_argument('-mkmodel', '--make_model', nargs='?', type=str, help='Create a new Model file')
    parser.add_argument('-migrate', '--db_migrate', nargs='?', type=str, help='Run all Migration', const='all')
    parser.add_argument('-seed', '--db_seed', nargs='?', type=str, help='Run all database seeds', const='all')
    parser.add_argument('-mkcontroller', '--make_controller', nargs='?', type=str, help='Create a new Controller file')
    parser.add_argument('-mkroute', '--make_route', nargs='?', type=str, help='Create a new Route file')
    parser.add_argument('-genkey', '--generate_key', nargs='?', type=str, help='Generate a new Secret Key',
                        const='loren')
    args = parser.parse_args()

    return args


def main():
    runner_interface(shell_arguments=sys.argv[1:])


if __name__ == '__main__':
    sys.exit(main())
