from __future__ import absolute_import, division, print_function, unicode_literals
from publisher.exceptions import UpdateNoteError
import subprocess

import publisher.settings as settings
from publisher.utils import WorkingDirectory, get_command_output


def clear_similar_historical_notes(commit, commit_history):

    similar_commits = commit.filter_similar_commits(commit_history)

    for similar_commit in similar_commits:
        update_note('', similar_commit.id)

    push_notes()


def edit_note(commit):
    update_note(commit.note, commit.id)
    push_notes()


def update_note(note, commit_id):
    """ Use the commit object obtained from the get notes command to overwrite a previous note
    """
    with WorkingDirectory(settings.PROCEDURE_CHECKOUT_DIRECTORY):
        try:
            output, error = get_command_output(
                ['git', 'notes', 'add', '-f', '-m', note, commit_id])
        except subprocess.CalledProcessError:
            print("Could not change the distribution group for the specified commit")


def push_notes():
    with WorkingDirectory(settings.PROCEDURE_CHECKOUT_DIRECTORY):
        print('Pushing ref/notes to origin')
        output, error = get_command_output(['git', 'push', '-q', 'origin', 'refs/notes/*'])
        print(output, error)
        if "Traceback" in error or "Failed: Please fix" in error:
            raise UpdateNoteError(error)
