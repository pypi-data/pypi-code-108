from __future__ import absolute_import, division, print_function, unicode_literals
from builtins import input

import argparse
import sys

from publisher.git_handling.setup import setup_users_machine
from publisher.utils import get_procedure_code, tspublisher_up_to_date
from publisher.translations.mo import build_mo_files
from publisher.translations.pot import ready_for_translations
from publisher.translations.po import merge_procedure_translation_files
from publisher import procedure_content
from publisher.exceptions import ValidationError
from publisher.processing import procedure
from publisher.settings import CHANNEL_TYPES
from publisher.exceptions import ChannelExistsError, ChannelMissingError


class PublisherCLI():

    def __init__(self, args):
        # Check version is up to date
        if not tspublisher_up_to_date():
            print('######################################################')
            print('Your version of the touch surgery publishing tools \n'
                  'is out of date. Please update using the following \n'
                  'command: \n \n'
                  'pip install -U tspublisher \n')
            print('######################################################')
            sys.exit()

        parser = argparse.ArgumentParser(
            description='Touch Surgery Publisher',
            usage='tspub <command> [<args>]'
        )
        subparsers = parser.add_subparsers(
            title='Available commands',
            description=(
                'These commands allow you to create and '
                'publish TS simulations'
            ),
            help='subparsers help'
        )
        cli_commands = [c for c in dir(self) if not c.startswith('_')]

        for command in cli_commands:
            sub_parser = subparsers.add_parser(
                command,
                help=getattr(self, command).__doc__
            )
            sub_parser.set_defaults(func=getattr(self, command))

        namespace = parser.parse_args(args[0:1])

        try:
            namespace.func(args[1:])
        except ValidationError as e:
            print('The following issues were encountered.')
            print(e.message)

    def setup(self, args):
        """ Setup your machine, ready to create and edit simulations
        """
        setup_users_machine()

    def procedures(self, args):
        """ List all procedures in the git repository, each being a separate branch
        """
        procedure_content.display_procedures()

    def phases(self, args):
        """ List all phases of the procedure and their commit histories.
        """
        phase_code = procedure_content.get_user_selected_phase()
        procedure_content.display_phase_history(phase_code)

    def reset(self, args):
        """ Reset all local changes to match the most recent commit
        """
        procedure_content.cl_reset_repo()

    def revert_phase(self, args):
        """ Revert to a previous commit state for a chosen commit and phase.
        """
        phase_code = procedure_content.get_user_selected_phase()
        procedure_content.display_phase_history_and_revert(phase_code)

    def workon(self, args):
        """ Move to the branch containing the specified procedure so that it can be worked on
        """
        parser = argparse.ArgumentParser(
            description='Move to the branch containing the specified procedure',
            usage='''tspub workon <procedure_code>'''
        )
        parser.add_argument(
            'procedure',
            help='The procedure code'
        )

        self._clean_working_directory_state()

        args = parser.parse_args(args)
        procedure_content.change_procedure(args.procedure)

    def save(self, args):
        """ Commit and push current changes to the repo
        """
        parser = argparse.ArgumentParser(
            description='Commit and push current changes to the repo',
            usage='''tspub save <commit_message>'''
        )
        parser.add_argument(
            'commit_message',
            help='Describe what changes have been made'
        )
        args = parser.parse_args(args)
        procedure_content.save_working_changes(args.commit_message)

    def create(self, args):
        """Create a new branch with the name of the procedure_code param
        """
        parser = argparse.ArgumentParser(
            description='Create new procedure with the specified procedure_code param',
            usage='''tspub create <procedure_code>'''
        )
        parser.add_argument('procedure_code', help='code of the procedure to be created')
        args = parser.parse_args(args)

        if args.procedure_code not in procedure_content.build_procedure_list():
            self._clean_working_directory_state()
            procedure_content.create_procedure_branch(args.procedure_code)
        else:
            raise Exception("The procedure {0} already exists and thus cannot be created".format(args.procedure_code))

        procedure.create_procedure(args.procedure_code)

        procedure_content.save_working_changes("Initial commit", initial=True, procedure_code=args.procedure_code)

    def update_procedure(self, args):
        """Update current working procedure. Update phases with build_phases param.
        """
        parser = argparse.ArgumentParser(
            description='Update current procedure.',
            usage='''tspub update_procedure'''
        )
        parser.add_argument('--build_phases', action='store_true', help='Build all phases as well as procedure')
        parser.add_argument('--graphics', action='store_true', help='Copy latest images (normal)')
        parser.add_argument('--pip_graphics', action='store_true', help='Copy latest pip images (normal)')

        args = self._get_build_args(parser, args)

        procedure_code = get_procedure_code()

        graphics = args.graphics
        if args.graphics:
            graphics = "latest"

        pip_graphics = args.pip_graphics
        if args.pip_graphics:
            pip_graphics = {}

        procedure.build_procedure(procedure_code,
                                  build_phases=args.build_phases,
                                  graphics=graphics, pip_graphics=pip_graphics,
                                  widget_graphics=args.widget_graphics,
                                  thumbnails=args.thumbnails,
                                  step_numbers=args.step_numbers,
                                  info_step=args.info_step)

    def update_phase(self, args):
        """Update the specified phase with the phase_code param.
        """
        parser = argparse.ArgumentParser(
            description='Update specified phase with the phase_code param.',
            usage='''tspub update_phase <phase_code>'''
        )
        parser.add_argument('phase_code', help='code of the procedure to be created')
        parser.add_argument('--graphics', help='Copy latest images, can be supplied with version number',
                            const="latest", nargs="?")
        parser.add_argument('--pip_graphics', help='Copy latest pip images, can be supplied with version number e.g.: '
                                                   '--pip_graphics="pipName 2,otherPipName 1"', const={},
                            nargs="?")
        parser.add_argument('--csv_version', help='Define csv version to build with', nargs="+")

        args = self._get_build_args(parser, args)

        pip_graphics = self.format_pip_graphics(args.pip_graphics)

        if args.csv_version:
            csv_version = args.csv_version[0]
        else:
            csv_version = None

        procedure.build_single_phase(args.phase_code, graphics=args.graphics,
                                     pip_graphics=pip_graphics,
                                     widget_graphics=args.widget_graphics,
                                     thumbnails=args.thumbnails,
                                     step_numbers=args.step_numbers,
                                     info_step=args.info_step,
                                     csv_version=csv_version)

    def publish(self, args):
        """Publish procedure with the specified distribution group. Defaults to TS-Testing.
        """
        parser = argparse.ArgumentParser(
            description='Publish procedure with the specified distribution group. Defaults to TS-Testing.',
            usage='''tspub publish'''
        )
        parser.add_argument(
            '--distgroup',
            help='Distribution group to be published to e.g. --distgroup=distGroup1,distGroup2',
            required=False
        )
        parser.add_argument(
            '--number',
            help='The number of previous commits to be shown',
            required=False
        )
        args = parser.parse_args(args)
        procedure_content.publish_with_display(args.distgroup, args.number)

    def translate(self, args):
        """Available for testing only, builds a messages.pot in the working directory for the active procedure."""
        if ready_for_translations():
            merge_procedure_translation_files()
            build_mo_files()

    def create_channel(self, args):
        parser = argparse.ArgumentParser()
        parser.add_argument('code')
        parser.add_argument('name')
        parser.add_argument('type', choices=CHANNEL_TYPES)
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('--eula_required', dest='eula', action='store_true')
        group.add_argument('--eula_not_required', dest='eula', action='store_false')

        args = parser.parse_args(args)
        if args.code in procedure_content.build_channel_list():
            raise ChannelExistsError("A channel with code {} already exists.")
        procedure.build_channel(vars(args))

    def update_channel(self, args):
        parser = argparse.ArgumentParser()
        parser.add_argument('code')
        parser.add_argument('--name')
        parser.add_argument('--type', choices=CHANNEL_TYPES)
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('--eula_required', dest='eula', action='store_true')
        group.add_argument('--eula_not_required', dest='eula', action='store_false')
        args = parser.parse_args(args)
        if args.code not in procedure_content.build_channel_list():
            raise ChannelMissingError("A channel with code {} does not exist.")

        updates = {}
        if args.name:
            updates['name'] = args.name
        if args.type:
            updates['type'] = args.type
        updates['eula'] = args.eula
        procedure.update_channel(args.code, updates)

    def save_channels(self, args):
        """ Commit and push current channel changes to the repo
        """
        parser = argparse.ArgumentParser(
            description='Commit and push current channel changes to the repo',
            usage='''tspub save_channels <commit_message>'''
        )
        parser.add_argument(
            'commit_message',
            help='Describe what changes have been made'
        )
        args = parser.parse_args(args)
        procedure_content.save_channel_changes(args.commit_message)

    @staticmethod
    def _get_build_args(parser, args):
        parser.add_argument('--widget_graphics', action='store_true', help='Copy latest widget images (normal)')
        parser.add_argument('--thumbnails', action='store_true', help="Pull latest thumbnails (both)")
        parser.add_argument('--step_numbers', action='store_true', help='Prepend step number in step content')
        parser.add_argument('--info_step', action='store_true', help='Add build information')

        args = parser.parse_args(args)
        return args

    @staticmethod
    def _clean_working_directory_state():
        if procedure_content.has_unstaged_changes():
            user_choice = PublisherCLI._get_user_decision()

            if user_choice == 'y':
                commit_message = PublisherCLI._get_commit_message()
                procedure_content.save_working_changes(commit_message)
            else:
                procedure_content.delete_unstaged_changes()

    @staticmethod
    def _get_commit_message():
        """ Return the commit message from the user
        """
        return input("Please enter a commit message")

    @staticmethod
    def _get_user_decision():
        """ Return the users y or n input
        """
        user_input = ''
        while user_input not in ['y', 'n']:
            print('You have unsaved changes. Would you save them now? If you do not save them they will be deleted')
            print('> y or n:')
            sys.stdout.flush()
            user_input = input('')
        return user_input.lower()

    @staticmethod
    def format_pip_graphics(pip_versions):
        if pip_versions:
            pip_graphics = {}
            pips = pip_versions.split(",")
            for pip in pips:
                version_list = pip.split(" ")
                pip_graphics[version_list[0]] = version_list[1]
            return pip_graphics

        return pip_versions


def main():
    PublisherCLI(sys.argv[1:])
