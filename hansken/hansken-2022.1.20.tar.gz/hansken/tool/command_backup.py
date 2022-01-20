# encoding=utf-8

from datetime import datetime, timedelta, timezone
from getpass import getpass
import math
from os import getcwd, makedirs, path, urandom
import sys
import threading
import time

import iso8601
from logbook import Logger

from hansken.remote import Connection, ProjectContext
from hansken.tool import add_command
from hansken.util import b64decode, b64encode

log = Logger(__name__)


def run_backup_command(args):
    """
    Starts the backup of a project. Requires a keystore
    to work for encrypted images; keys will be fetched automatically.

    :param args: an `argparse.Namespace` object carrying command line arguments
    """
    # check that we'll have an endpoint and a project (error message emulated to look like argparse's own messages)
    if not args.endpoint:
        backup_parser.error('the following argument is required: --endpoint ENDPOINT')
    if not args.project and not args.backup_modified:
        backup_parser.error('the following arguments are required: PROJECT or BACKUP_MODIFIED')
    if not args.keystore:
        backup_parser.error('the following argument is required: --keystore ENDPOINT')
    if not args.preference:
        backup_parser.error('the following argument is required: --preference ENDPOINT')
    if not args.user_backup_key:
        backup_parser.error('the following argument is required: USER_BACKUP_KEY')

    user_backup_key = args.user_backup_key

    with Connection(args.endpoint, keystore_url=args.keystore, preference_url=args.preference, auth=args.auth,
                    verify=args.verify) as connection:
        if args.backup_modified:
            projects = [project.get('id') for project in get_projects_to_backup(connection)]
            if not projects:
                log.info('No projects found to backup')
        else:
            projects = [args.project]

        keys_folder = None
        for project in projects:
            if callable(user_backup_key):
                # generate a new key for every backup if a generating lambda is provided
                user_backup_key = user_backup_key()
                keys_folder = args.keys_folder if args.keys_folder else args.download_folder

            try:
                backup(connection,
                       b64decode(user_backup_key, validate=True),
                       project=project,
                       download_backup=args.download_backup,
                       download_folder=args.download_folder,
                       keys_folder=keys_folder)
            # catch all exceptions, so backup is still performed for other projects in case of an error
            except Exception:
                log.exception('Error backing up project: {}'.format(project))


def store_user_backup_key(user_backup_key, keys_folder, project, task_id):
    """
    Stores the backup key in the keys folder
    :param user_backup_key: the key in binary (`bytes`) to write
    :param keys_folder: folder to write the user key file to
    :param project: the id of the project of the key
    :param task_id: the id of the backup task
    """
    project_path = path.join(keys_folder, project)
    makedirs(project_path, exist_ok=True)
    key_file_path = path.join(project_path, f'{task_id}.backup.key')
    with open(key_file_path, 'w') as f:
        f.write(b64encode(user_backup_key))


def is_backup_task_of_current_user(task, connection):
    """
    Checks if a task is a backup task of the current user..

    :param task: project id of project
    :param connection: instance of `.Connection`
    :return: a boolean that indicates if the project should be backed up
    """
    task_details = task.get('task')
    return task_details.get('type') == 'backup' and task_details.get('queuedBy') == connection.identity


def check_backup_needed(project, connection):
    """
    Returns if the project should be backed-up:
    This is the case when there are no backup tasks started by the current user since the last modification date of the
    project. If there is no last modification date no backup is needed.

    :param project: project as a dict
    :param connection: instance of `.Connection`
    :return: a boolean that indicates if the project should be backed up
    """
    project_id = project.get('id')
    last_modified_date = project.get('lastModifiedDate')
    if last_modified_date is not None:
        parsed_last_modified_date = iso8601.parse_date(last_modified_date)
        now = datetime.now(timezone.utc)
        open_tasks = connection.tasks('open', project_id, start=parsed_last_modified_date, end=now)

        # the earliest retrieval date for closed tasks is 8 weeks
        earliest_task_retrieval_date = now - timedelta(days=56)
        task_retrieval_date = max(earliest_task_retrieval_date, parsed_last_modified_date)
        closed_tasks = [task for task in connection.tasks('closed', project_id, start=task_retrieval_date, end=now)
                        if task.get('task', {}).get('status') == 'completed']
        all_tasks = open_tasks + closed_tasks

        backup_tasks = [task for task in all_tasks if is_backup_task_of_current_user(task, connection)]
        log.info('{} active backup tasks found for current user for project: {}', len(backup_tasks), project_id)
        return not backup_tasks
    log.info('project {} does not have a lastModificationDate set', project_id)
    return False


def get_projects_to_backup(connection):
    """
    Retrieves the projects to backup.

    :param connection: an instance of `.Connection`
    :return: list of projects to backup
    """
    return [project for project in connection.projects() if check_backup_needed(project, connection)]


def backup(connection, user_backup_key, project=False,
           download_backup=False, download_folder=getcwd(), keys_folder=None):
    """
    Starts a backup for the given project. The image keys for the project are
    retrieved from the keystore. A backup_key has to be provided to encrypt the backup.

    :param connection: an instance of `.Connection`
    :param user_backup_key: crypto key in binary (`bytes`) for encrypting the backup
    :param project: project to backup
    :param download_backup: boolean denoting if the backup should be downloaded
    :param download_folder: folder to write the backup file to
    :param keys_folder: folder to write the backup key to
    :return: task_id of the created backup task
    """
    if download_backup and not path.isdir(download_folder):
        raise ValueError('download folder "{}" does not exist or is not a folder'.format(download_folder))

    with ProjectContext(connection, project) as context:
        task_id = context.connection.backup_project(project, user_backup_key)

        if keys_folder is not None:
            store_user_backup_key(user_backup_key, keys_folder, project, task_id)

        if download_backup:
            task_finished = threading.Event()
            backup_progress = {'stage': '', 'progress': 0.0, 'status': ''}

            log.info('polling task with id: {}', task_id)

            thread = threading.Thread(target=wait_for_task,
                                      args=(context, task_id, task_finished, backup_progress))
            thread.start()

            # wait here for the result to be available before continuing
            while not task_finished.wait(timeout=5):
                print('\r{}% done...'.format(math.floor(100 * backup_progress['progress'])), end='', flush=True)
            print('\r100% done...')

            if backup_progress['status'] == 'completed':
                project_path = path.join(download_folder, project)
                makedirs(project_path, exist_ok=True)
                backup_file_path = path.join(project_path, task_id + ".backup")
                do_download_backup(context, task_id, backup_file_path)
            else:
                raise ValueError('backup task not completed successfully: {}'.format(backup_progress['status']))

        return task_id


def wait_for_task(context, task_id, task_finished, backup_progress):
    try:
        while True:
            task = context.connection.task(task_id)
            backup_task = task['task']
            backup_progress['stage'] = backup_task.get('progressStage', '')
            backup_progress['progress'] = backup_task.get('progressCompleted', 0.0)
            backup_progress['status'] = task_status = backup_task.get('status', '')

            # Possible statuses are: queued, postponed, running, cancelled, failed, completed
            if task_status not in {'queued', 'postponed', 'running'}:
                log.info('task finished with status: {}', task_status)
                task_finished.set()
                break

            time.sleep(1)
    except Exception:
        log.exception('Error waiting for backup task to complete')
        task_finished.set()


def do_download_backup(context, task_id, backup_file_path):
    log.info('downloading backup as {}', backup_file_path)
    context.connection.download_backup(task_id, backup_file_path)
    log.info('download successful.')


def prompt_verify_key():
    """
    Prompts for a key twice, verifying the entered values are identical before
    returning it. Aborts on keyboard interrupt or EOF.

    :return: the key entered by the user
    """
    try:
        while True:
            key = getpass(prompt='Key (base64-encoded): ').strip()
            if key == getpass(prompt='Key (again): ').strip():
                return key
            else:
                print("Provided keys don't match, please try again (^C or {eof} to abort)".format(
                    eof='^Z' if 'win32' in sys.platform else '^D'
                ))
    except (KeyboardInterrupt, EOFError):  # user pressed either ^C or ^D (^Z on windows)
        raise SystemExit('Aborted')


backup_parser = add_command('backup', run_backup_command, optional_project=True,
                            help='start backup of a project')
backup_parser.add_argument('-k', '--user-backup-key', dest='user_backup_key', metavar='USER_BACKUP_KEY',
                           default=lambda: b64encode(urandom(32)),
                           help='user provided key to encrypt backup (base64-encoded). '
                                'By default a random key will be generated')
backup_parser.add_argument('-K', '--prompt-user-backup-key', dest='user_backup_key', action='store_const',
                           const=prompt_verify_key, help='prompt for a user backup key (base64-encoded)')
backup_parser.add_argument('-d', '--download-backup', dest='download_backup', action='store_true',
                           help='enable backup download.')
backup_parser.add_argument('-f', '--download-folder', dest='download_folder',
                           help='folder to store the downloaded backups', default=getcwd())
backup_parser.add_argument('-m', '--backup-modified', dest='backup_modified', action='store_true',
                           help='backup projects that have been modified since the last backup', default=False)
backup_parser.add_argument('-kf', '--keys-folder', dest='keys_folder',
                           help='folder to store the generated keys', default=None)
