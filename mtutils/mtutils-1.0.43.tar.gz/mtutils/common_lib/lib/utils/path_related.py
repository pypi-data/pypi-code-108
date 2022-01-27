from pathlib import Path
import os
import uuid
import platform

def scan_folder(data_dir, extension='bmp'):
    """
    Generate a dictionary, where key: file name, and value: file path
    Assuming all file names are unique in data_dir
    param:
        data_dir: directory where you want to scan the file, recursively
        extension: the file extension. this param specifies the file format
    return:
        list of paths to files with the given extension
    """
    assert os.path.exists(data_dir), data_dir+" does not exist"
    extension = extension.strip('.')
    files = Path(data_dir).glob('**/*.{}'.format(extension))
    files = [str(x) for x in files]
    return files


def create_tmp_file(extension=''):
    """
    Return a temporary path that is randomly generated.
    Arguments:
        extension: the extension of the generated path (no dot)
    Return:
        a randomly generated path (str) in /tmp folder
    """
    if platform.system() == 'Windows':
        tmp_folder = r'./TempFiles'
    else:
        tmp_folder = '/tmp/temp-random-files/'
    
    if extension != '':
        tmp_file = os.path.join(tmp_folder, uuid.uuid1().hex) + '.' + extension.lstrip('.')
    else:
        tmp_file = os.path.join(tmp_folder, uuid.uuid1().hex)

    return tmp_file
