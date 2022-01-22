import os
import shutil
import argparse
import logging

from pyc_logging import setupLoggingSystem, DEFAULT_LOGGING_FORMAT

# A folder where script running
curr_folder: str = os.getcwd()


def clear_cache(parent_folder: str = curr_folder) -> None:
    _parent_folder: str = os.path.realpath(parent_folder)
    _cache_files_counter: int = 0
    
    logging.info(f'Searching in {_parent_folder}\n')
    for path, dirs, files in os.walk(_parent_folder):
        folder_path: str = os.path.realpath(path)

        if folder_path.endswith('pytest_cache') or folder_path.endswith('__pycache__'):
            logging.info(f'Deleting {folder_path}')
            shutil.rmtree(folder_path)
            _cache_files_counter += 1
    logging.info(f'Deleted {_cache_files_counter} files')


def clear_cache_silent(parent_folder: str = curr_folder) -> None:
    """
        Instead of default `clear_cache` function it will not show any
        status messages in console
    """
    _parent_folder: str = os.path.realpath(parent_folder)

    for path, dirs, files in os.walk(_parent_folder):
        folder_path: str = os.path.realpath(path)
        
        if folder_path.endswith('pytest_cache') or folder_path.endswith('__pycache__'):
            shutil.rmtree(folder_path)


def setup_argument_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        description='Removing python\'s cache files from folders'
    )

    ap.add_argument(
        '-p', '--path',
        type=str,
        help='Direct path to folder',
        default=curr_folder,
        required=False)
    ap.add_argument(
        '-sl', '--show_logs',
        type=str,
        help='Determine wether show or hide logs (yes/no)',
        default='yes',
        required=False)
    
    return ap


def main(*args, **kwargs):
    if kwargs['show_logs'].lower().startswith('y'):
        clear_cache(kwargs['parent_folder'])
    else:
        clear_cache_silent(kwargs['parent_folder'])


if __name__ == '__main__':
    setupLoggingSystem(
        level = logging.INFO,
        format = DEFAULT_LOGGING_FORMAT,
        datefmt= "%d-%b-%y %H:%M:%S"
    )

    args_parser = setup_argument_parser()
    passed_args = args_parser.parse_args()


    try:
        main(
            parent_folder=passed_args.path,
            show_logs=passed_args.show_logs)
    except Exception as e:
        logging.exception("Exception occurred." )
    else:
        logging.info("Done.")

    main(
        parent_folder=passed_args.path,
        show_logs=passed_args.show_logs)
    
    print('Done.')
