"""Provides Dispatcher class to parse arguments and call correct functions"""

# system imports
import argparse
from datetime import datetime

# 3rd party imports
from colorama import Fore, Style

# app imports
from ntbk import helpers
from ntbk.entities.collections import CollectionFile, get_all_collections
from ntbk.entities.logs import LogFile
from ntbk.entities.templates import Template, get_all_templates


class Dispatcher():
    """Parses arguments to the program and handles them appropriately.

    Arguments:
        config - instance of Config
        filesystem - instance of Filesystem

    Attributes:
        config - Config used by the dispatcher
        filesystem - Filesystem used by the dispatcher
        parser - ArgumentParser
        subparsers - action object with add_parser() method
    """

    def __init__(self, config, filesystem):
        self.config = config
        self.filesystem = filesystem
        self.parser = argparse.ArgumentParser(prog='ntbk',
            description='NTBK - a simple terminal notebook application')
        # Default to the "today" command if no args given
        self.parser.set_defaults(func=self.handle_logfile_command,
            file=self.config.get('default_filename'),
            list=False,
            find=False,
            find_dir=False,
            template=None,
            variables=[])

        self.subparsers = self.parser.add_subparsers(dest='command')

        # setup subparsers
        self.configure_log_args()
        self.configure_collection_args()
        self.configure_other_args()

    def run(self, sys_args):
        """Parse the args passed into the program and call the appropriate handler function

        Arguments:
            sys_args -- list of arguments (usually from sys.argv)
        """
        args = self.parser.parse_args(sys_args)
        args.func(args)

    def open_or_create_entity(self, args, entity):
        """Open or create log or collection file.

        Arguments:
            args -- args from argparse
            entity - either LogFile or CollectionFile object
        """
        template = None

        entity.create_directories()

        if not entity.exists():
            if args.template:
                template = Template(self.config, self.filesystem, args.template)
            elif entity.has_default_template():
                template = entity.get_default_template()

            if template is not None:
                variables = {}
                if isinstance(entity, LogFile):
                    variables['log_date'] = entity.get_logdate().get_date()
                variables.update(helpers.convert_key_value_vars_to_dict(args.variables))
                template.set_extra_vars(variables)
                self.filesystem.create_file(entity.get_path(), template.render())

        self.filesystem.open_file_in_editor(entity.get_path())

    def list_contents(self, entity, recursive=False): #pylint: disable=no-self-use
        """Takes a LogDate or Collection and lists its contents (files and immediate folders)

        Arguments:
            entity - Either LogDate or Collection
            recursive - Boolean - traverse all subdirs and print out all files
        """
        if recursive:
            for path in sorted(entity.get_contents(recursive), key=lambda p: str(p).lower()):
                text = path.relative_to(entity.get_path())
                if path.is_dir():
                    text = Fore.BLUE + str(text) + '/' + Style.RESET_ALL
                print(str(text).replace(path.suffix, ''))
        else:
            for path in sorted(entity.get_contents(recursive), key=lambda p: p.stem.lower()):
                if path.is_dir():
                    print(Fore.BLUE + path.stem + '/' + Style.RESET_ALL)
                else:
                    print(path.stem)

    def handle_logfile_command(self, args):
        """Handler for commands involving log files.

        Arguments:
            args -- Args from argparse
        """
        if args.command is None:
            args.command = 'today'

        date_obj = args.date if args.command == 'date' \
            else helpers.get_date_object_for_alias(args.command)

        logfile = LogFile(self.config, self.filesystem, date_obj, args.file)

        if args.list and args.file.endswith('/'):
            self.list_contents(logfile, args.recursive)
        elif args.list:
            self.list_contents(logfile.logdate, args.recursive)
        elif args.find:
            print(logfile.get_path())
        elif args.find_dir:
            print(logfile.get_logdate().get_path())
        else:
            self.open_or_create_entity(args, logfile)

    def handle_collection_command(self, args):
        """Handler for commands involving collection files.

        Arguments:
            args -- Args from argparse
        """
        collection_file = CollectionFile(self.config, self.filesystem,
            args.collection_name, args.file)

        if args.list:
            self.list_contents(collection_file.collection, args.recursive)
        elif args.find:
            print(collection_file.get_path())
        elif args.find_dir:
            print(collection_file.get_collection().get_path())
        else:
            self.open_or_create_entity(args, collection_file)

    def handle_list_collections_command(self, _args):
        """Handler for the 'collections' command - lists all the collections

        Arguments:
            _args -- Args from argparsed. Underscored because they are not used
        """
        for collection in get_all_collections(self.config, self.filesystem):
            print(collection.get_name())

    def handle_list_templates_command(self, _args):
        """Handler for the 'templates' command

        Arguments:
            _args -- Args from argparse. Underscored because they are not used
        """
        for template in get_all_templates(self.config, self.filesystem):
            print(template.get_name())

    def handle_jot_command(self, args):
        """Handler for the 'jot' command

        Arguments:
            args -- Args from argparse
        """
        date_obj = helpers.get_date_object_for_alias('today')
        logfile = LogFile(self.config, self.filesystem, date_obj, args.file)
        content = args.text
        if args.timestamp:
            content = f"[{datetime.now().strftime('%I:%M %p')}]\n" + content
        content = '\n\n' + content

        self.filesystem.append_to_file(logfile.get_path(), content)
        print(f"{Fore.GREEN}Jotted note to today's {logfile.get_name()} file{Style.RESET_ALL}")

    def configure_log_args(self):
        """Configure all the possible args for commands involving log files"""
        default_file = self.config.get('default_filename')

        # Setup subparser for 'today' command
        parser_today = self.subparsers.add_parser('today', aliases=['tod'],
            help="Load today's log file")

        parser_today.add_argument('file', nargs='?', default=default_file)

        parser_today.add_argument('--template', '-t',
            help='If creating, this template file will be used, overriding the default template')

        parser_today.add_argument("--vars",
            dest='variables', metavar="KEY=VALUE", nargs='+', default=[],
            help='Extra template variables in the format key=value. \
                 If value contains spaces, enclose it in quotes, e.g. key="my value"')

        parser_today.add_argument('--list', '-l', action='store_true', help="List today's files")

        parser_today.add_argument('--recursive', '-r', action='store_true', help="List recursively")

        parser_today.add_argument('--find', '-f', action='store_true',
            help="Output the path to the file")

        parser_today.add_argument('--find-dir', '-d', action='store_true',
            help="Output the path to the file's directory")

        parser_today.set_defaults(command='today', func=self.handle_logfile_command)

        # Setup subparser for 'yesterday' command
        parser_yest = self.subparsers.add_parser('yesterday', aliases=['yest'],
            help="Load yesterday's log file")

        parser_yest.add_argument('file', nargs='?', default=default_file)

        parser_yest.add_argument('--template', '-t',
            help='If creating, this template file will be used, overriding the default template')

        parser_yest.add_argument("--vars",
            dest='variables', metavar="KEY=VALUE", nargs='+', default=[],
            help='Extra template variables in the format key=value. \
                If value contains spaces, enclose it in quotes, e.g. key="my value"')

        parser_yest.add_argument('--list', '-l', action='store_true', help="List yesterday's files")

        parser_yest.add_argument('--recursive', '-r', action='store_true', help="List recursively")

        parser_yest.add_argument('--find', '-f', action='store_true',
            help="Output the path to the file")

        parser_yest.add_argument('--find-dir', '-d', action='store_true',
            help="Output the path to the file's directory")

        parser_yest.set_defaults(command='yesterday', func=self.handle_logfile_command)

        # Setup subparser for 'tomorrow' command
        parser_tom = self.subparsers.add_parser('tomorrow', aliases=['tom'],
            help="Load tomorrow's log file")

        parser_tom.add_argument('file', nargs='?', default=default_file)

        parser_tom.add_argument('--template', '-t',
            help='If creating, this template file will be used, overriding the default template')

        parser_tom.add_argument("--vars",
            dest='variables', metavar="KEY=VALUE", nargs='+', default=[],
            help='Extra template variables in the format key=value. \
                If value contains spaces, enclose it in quotes, e.g. key="my value"')

        parser_tom.add_argument('--list', '-l', action='store_true', help="List tomorrow's files")

        parser_tom.add_argument('--recursive', '-r', action='store_true', help="List recursively")

        parser_tom.add_argument('--find', '-f', action='store_true',
            help="Output the path to the file")

        parser_tom.add_argument('--find-dir', '-d', action='store_true',
            help="Output the path to the file's directory")

        parser_tom.set_defaults(command='tomorrow', func=self.handle_logfile_command)

        # Setup subparser for 'date' command
        parser_date = self.subparsers.add_parser('date', aliases=['dt', 'd'],
            help="Load given date's log file")

        parser_date.add_argument('date', type=helpers.argparse_valid_iso_date)

        parser_date.add_argument('file', nargs='?', default=default_file)

        parser_date.add_argument('--template', '-t',
            help='If creating, this template file will be used, overriding the default template')

        parser_date.add_argument("--vars",
            dest='variables', metavar="KEY=VALUE", nargs='+', default=[],
            help='Extra template variables in the format key=value. \
                If value contains spaces, enclose it in quotes, e.g. key="my value"')

        parser_date.add_argument('--list', '-l', action='store_true',
            help="List given date's files")

        parser_date.add_argument('--recursive', '-r', action='store_true', help="List recursively")

        parser_date.add_argument('--find', '-f', action='store_true',
            help="Output the path to the file")

        parser_date.add_argument('--find-dir', '-d', action='store_true',
            help="Output the path to the file's directory")

        parser_date.set_defaults(command='date', func=self.handle_logfile_command)

    def configure_collection_args(self):
        """Configure all the possible args for commands involving collection files"""
        default_file = self.config.get('default_filename')

        # Setup subparser for 'collection' command
        parser_collection = self.subparsers.add_parser('collection', aliases=['col', 'c'],
            help="Load given collection")

        parser_collection.add_argument('collection_name')

        parser_collection.add_argument('file', nargs='?', default=default_file)

        parser_collection.add_argument('--template', '-t',
            help='If creating, this template file will be used, overriding the default template')

        parser_collection.add_argument("--vars",
            dest='variables', metavar="KEY=VALUE", nargs='+', default=[],
            help='Extra template variables in the format key=value. \
                If value contains spaces, enclose it in quotes, e.g. key="my value"')

        parser_collection.add_argument('--list', '-l', action='store_true',
            help='List the files in given collection')

        parser_collection.add_argument('--recursive', '-r', action='store_true',
            help="List recursively")

        parser_collection.add_argument('--find', '-f', action='store_true',
            help="Output the path to the file")

        parser_collection.add_argument('--find-dir', '-d', action='store_true',
            help="Output the path to the file's directory")

        parser_collection.set_defaults(command='collection', func=self.handle_collection_command)

        parser_collections = self.subparsers.add_parser('collections', aliases=['cols'],
            help="List all collections")

        parser_collections.set_defaults(func=self.handle_list_collections_command)

    def configure_other_args(self):
        """Configure args for any other commands"""
        default_file = self.config.get('default_filename')

        # Setup subparser for 'templates' command
        parser_templates = self.subparsers.add_parser('templates', help="List all templates")

        parser_templates.set_defaults(func=self.handle_list_templates_command)


        # Setup subparser for 'jot' command
        parser_jot = self.subparsers.add_parser('jot',
            help="Add a quick note to today's log without opening your editor")

        parser_jot.add_argument('text')

        parser_jot.add_argument('file', nargs='?', default=default_file,
            help="Jot to file other than the default")

        parser_jot.add_argument('--timestamp', '-s', action='store_true',
            help="Add a timestamp before the jotted note")

        parser_jot.set_defaults(func=self.handle_jot_command)
