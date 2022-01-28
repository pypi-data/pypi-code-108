'''
This module provides utility functions to operate on files and folders.
'''

import os
import shutil
import zipfile
import hashlib


BLOCK_SIZE = 65536


def remove_folder_content(folder_path):
    '''
    Deletes the content of a folder located at `folder_path`
    without deleting the folder itself.
    
    From https://stackoverflow.com/a/185941
    '''
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            else:
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {folder_path} folder content.\n>>>\n{str(e)}')
            return False
    
    return True


def zip_folder(folder_path, output_path):
    '''
    Creates a ZIP archive with the content of a given folder
    at its root (i.e., it skips the folder level itself in
    the resulting archive tree).
    '''
    # Initialise empty file paths list
    file_paths = []

    # Crawl through directory and subdirectories
    for root, _, files in os.walk(folder_path):
        for filename in files:
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)

    # Writing files to a zipfile
    with zipfile.ZipFile(output_path, 'w') as zip:
        for file in file_paths:
            zip.write(file, arcname=file.replace(folder_path, ''))


def unzip_archive(archive_path, output_path):
    with zipfile.ZipFile(archive_path, 'r') as zip:
        zip.extractall(output_path)


def hash_folder(folder_path):
    '''
    Returns the MD5 checksum computed over all files located
    in the given folder.
    '''
    md5 = hashlib.md5()

    for root, _, files in os.walk(folder_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)

            with open(file_path, 'rb') as f:
                fb = f.read(BLOCK_SIZE)

                while len(fb) > 0:
                    md5.update(fb)
                    fb = f.read(BLOCK_SIZE)
    
    return md5.hexdigest()
