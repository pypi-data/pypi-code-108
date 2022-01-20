import os
import errno
import hashlib
import fnmatch
import requests
import mimetypes

from os import path, walk
from Crypto.Cipher import AES
from base64 import b64decode


def unpad(s):
    return s[:-ord(s[len(s) - 1:])]


def filter_by_mimetypes(filters, path):
    """
    mimetypes for files will return in the following format: "TYPE/EXACT_TYPE", for ex. 'image/jpeg'
    This function will receive general types in the filters list (for ex. ['image']), and will only return
    True for files that match any of the filters
    @param filters: Allowed file types.
    @param path: File to test against filters
    @return: True if file passed filters, False if file is filtered
    """
    # This means we have no filters
    if not filters:
        return True

    # This means its a directory / file without extension
    if not mimetypes.guess_type(path)[0]:
        return False

    mime_type = mimetypes.guess_type(path)[0].split('/')[0]
    return mime_type in filters


def decrypt(key, iv, secret):
    cipher = AES.new(key.encode("utf8"), AES.MODE_CBC, b64decode(iv.encode("utf8")))
    secret = b64decode(secret.encode("utf-8"))
    return unpad(cipher.decrypt(secret).decode('utf8'))


def download_file(file_url, file_path):
    """
    Download a file from the provided url and saves it to the requested path
    @param file_url: The URL from which the file will be downloaded
    @param file_path: The target path to which we want to save the file
    @return: None
    """
    sts_file = requests.get(file_url, verify=False)
    create_dir_if_not_exists(file_path)
    with open(file_path, 'wb') as f:
        f.write(sts_file.content)


def create_dir_if_not_exists(local_path):
    """
    Checks if the given file path directory exists and creates it if not.
    @param local_path: File path
    @return: None
    """
    dir_path = os.path.dirname(local_path)
    if dir_path and not os.path.exists(dir_path):
        try:
            os.makedirs(dir_path)
        except OSError as e:
            if errno.EEXIST != e.errno:
                # TODO: handle exception
                raise


def get_relative_path(full_path):
    """
    Returns file relative path without '.' suffix
    @param full_path: Path string
    @return: String
    """
    if full_path.startswith("./"):
        full_path = full_path[2:]
    return full_path


def append_trailing_slash(path):
    """
    Appends trailing slash to path - used to differentiate files from directories
    @param path: String representing the directory path
    @return: String
    """
    return path if path.endswith("/") else "{}/".format(path)


def get_files_and_dirs_recursive(root_dir=".", regex="*", only_files=False, not_tmp=False, filters=None):
    """
    Recursively traverse a given directory and get all of the relevant files and folders within
    @param root_dir: String representing the directory path
    @param regex: String representing the regex to filter out files/folders
    @param only_files: Boolean representing whether or not we want to receive only files
    @return: List
    """
    full_paths = [append_trailing_slash(get_relative_path(root_dir))]
    for root, dirs, files in walk(root_dir, topdown=False):
        for name in files:
            full_paths.append(get_relative_path(path.join(root, name)))
        for name in dirs:
            if not only_files:
                full_paths.append(append_trailing_slash(get_relative_path(path.join(root, name))))

    if regex:
        full_paths = fnmatch.filter(full_paths, regex)

    files = [item for item in full_paths if not item.startswith(".cnvrg")]

    if not_tmp:
        files = [item for item in files if not item.startswith(".tmp")]

    if filters:
        files = [item for item in files if filter_by_mimetypes(filters, item)]

    return files


def chunk_list(list, size):
    """
    Chunks a given list into equally sized chunks (except last chunk)
    @param list: List we want to chunk
    @param size: Integer representing the chunk size
    @return: List of lists
    """
    chunks = []
    for i in range(0, len(list), size):
        chunks.append(list[i:i + size])
    return chunks


def get_file_sha1(full_path):
    """
    Calculates the file SHA1 using its content
    @param full_path: String representing the file path
    @return: String
    """
    BUF_SIZE = 65536
    sha1 = hashlib.sha1()

    with open(full_path, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            sha1.update(data)

    return sha1.hexdigest()


def total_files_size(files):
    total = 0
    for full_path in files:
        if os.path.isfile(full_path):
            total += os.path.getsize(full_path)
    return total
