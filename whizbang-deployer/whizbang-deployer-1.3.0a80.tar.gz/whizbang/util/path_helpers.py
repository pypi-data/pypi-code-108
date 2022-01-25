import fnmatch
import os


def find_file(name: str, path: str):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)
        return None


def find_all_files(name: str, path: str):
    result = []
    for root, dirs, files in os.walk(path):
        if name in files:
            result.append(os.path.join(root, name))
    return result


def find_files_with_pattern(pattern: str, path: str):
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result
