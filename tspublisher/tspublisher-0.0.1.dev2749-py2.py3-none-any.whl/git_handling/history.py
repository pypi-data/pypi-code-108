from __future__ import absolute_import, division, print_function, unicode_literals

import subprocess

import os

import publisher.settings as settings
from publisher.classes import Commit
from publisher.utils import WorkingDirectory, get_procedure_code, get_command_output


def get_commits_for_procedure():
    """Get commits for a procedure.
    """
    return get_commits_for_repo()


def get_commits_for_phase(phase_code):
    """Get commits for a phase.
    """

    procedure_code = get_procedure_code()
    return get_commits_for_repo(relative_directory=os.path.join(procedure_code, phase_code))


def get_commits_for_repo(relative_directory=None):
    commit_list = []
    with WorkingDirectory(settings.PROCEDURE_CHECKOUT_DIRECTORY):
        subprocess.check_output(['git', 'fetch', '--force', '--quiet', 'origin', 'refs/notes/*:refs/notes/*'])
        if relative_directory:
            output, error = get_command_output(['git', 'log', '--oneline', '--', relative_directory])
            log_list = output.split("\n")
        else:
            output, error = get_command_output(['git', 'log', '--oneline'])
            log_list = output.split("\n")

        for counter, log in enumerate(log_list):

            if log != '':
                commit_id = log.split()[0]
                comment = log.split(" ", 1)[1]
                note = get_commit_note(commit_id)
                author = get_author(commit_id)

                commit_list.append(Commit(commit_id, comment, author, note))

    return commit_list


def get_author(commit_hash):
    with WorkingDirectory(settings.PROCEDURE_CHECKOUT_DIRECTORY):
        output, _ = get_command_output(['git', 'show', '--format="%aN <%aE>"', commit_hash])
        return output.split('"')[1]


def get_commit_note(commit_object):
    # Get the notes for the previous commits
    with WorkingDirectory(settings.PROCEDURE_CHECKOUT_DIRECTORY):

        try:
            note, error = get_command_output(['git', 'notes', 'show', commit_object])

            if 'no note found' not in error.lower():
                note = note.split('\n')[0]
            else:
                note = None

        except subprocess.CalledProcessError:
            note = None

    return note
