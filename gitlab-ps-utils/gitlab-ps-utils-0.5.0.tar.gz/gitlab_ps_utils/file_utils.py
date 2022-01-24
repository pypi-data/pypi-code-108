import os
import errno
import hashlib
from re import findall
from time import time
from traceback import print_exc
from requests import get, head


def download_file(url, path, filename=None, headers=None, verify=True):
    # NOTE the stream=True parameter
    if __is_downloadable(url, verify):
        r = get(url, stream=True, headers=headers,
                allow_redirects=True, verify=verify)
        if filename is None:
            filename = __get_filename_from_cd(
                r.headers.get('content-disposition'))
        file_path = "{0}/downloads/{1}".format(path, filename)
        create_local_project_export_structure(os.path.dirname(file_path))
        with open(file_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
    return filename


def create_local_project_export_structure(dir_path):
    if not os.path.exists(dir_path):
        try:
            os.makedirs(dir_path)
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise


def __is_downloadable(url, verify):
    """
        Does the url contain a downloadable resource
    """
    h = head(url, allow_redirects=True, verify=verify)
    header = h.headers
    content_type = header.get('content-type')
    if 'text' in content_type.lower():
        return False
    if 'html' in content_type.lower():
        return False
    return True


def __get_filename_from_cd(cd):
    """
        Get filename from content-disposition
    """
    if not cd:
        return None
    fname = findall('filename=(.+)', cd)
    if len(fname) == 0:
        return None
    return fname[0]


def is_recent_file(path, age=2592000):
    """
        Check whether a file path exists, is empty and older than 1 month
    """
    return os.path.exists(path) and os.path.getsize(
        path) > 0 and (time() - os.path.getmtime(path) < age)


def get_hash_of_dirs(directory, verbose=0):
    """
        http://akiscode.com/articles/sha-1directoryhash.shtml
        Copyright (c) 2009 Stephen Akiki
        MIT License (Means you can do whatever you want with this)
        See http://www.opensource.org/licenses/mit-license.php
        Error Codes:
        -1 -> Directory does not exist
        -2 -> General error (see stack traceback)
    """
    SHAhash = hashlib.sha1()
    if not os.path.exists(directory):
        return -1

    try:
        for root, _, files in os.walk(directory):
            for names in files:
                if verbose == 1:
                    print('Hashing', names)
                filepath = os.path.join(root, names)
                f1 = None
                try:
                    f1 = open(filepath, 'rb')
                except BaseException:
                    # You can't open the file for some reason
                    f1.close()
                    continue

                while True:
                    # Read file in as little chunks
                    buf = f1.read(4096)
                    if not buf:
                        break
                    SHAhash.update(hashlib.sha1(buf).hexdigest().encode())
                f1.close()
    except BaseException:
        # Print the stack traceback
        print_exc()
        return -2

    return SHAhash.hexdigest()


def find_files_in_folder(wildcard, directory):
    return [f for f in os.listdir(directory) if wildcard in f]
