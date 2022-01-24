import os
import random
import shutil
import subprocess


def __command(args: list):
    sub = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    sub.wait()
    sub.kill()
    sub.terminate()


def _decoder(string_path: str) -> str:
    if string_path.startswith('~'):
        string_path = join(os.path.expanduser('~'), string_path.split('~', 1)[1])

    if not string_path.__contains__('\\'):
        return string_path

    string_path = string_path.replace('\\', '')

    return string_path


def last_component(string: str):
    Broken = string.split('/')
    length = len(Broken)

    return Broken[length - 1]


def basePath(URL):
    if URL.endswith('/'):
        URL = URL[:-1]

    Broken = URL.split('/')
    length = len(Broken)

    LastItem = Broken[length - 1]
    NewPath = ''

    for path in Broken:
        Bad = [LastItem, '']

        continuee = False

        for b in Bad:
            if path == b:
                continuee = True

        if continuee:
            continue

        NewPath = NewPath + '/' + path

    return NewPath


def file_exists(path):
    return os.path.isfile(path)


def directory_exists(path):
    return os.path.isdir(path)


def os_walk(file_name, path, custom_function=None):
    """
    custom_function is a function which should return True
    if the file passed is the wanted file

    i.e.
    def function(file):
        if file.endswith('.wav'):
        return True

    in this example the first file that ends with a .wav extension will be returned
    """
    if custom_function is None:
        for r, d, f in os.walk(path):
            for file in f:
                if file == file_name:
                    return os.path.abspath(os.path.join(r, file))

    else:
        for r, d, f in os.walk(path):
            for file in f:
                if custom_function(file):
                    return os.path.abspath(os.path.join(r, file))

        return None


def copy(src, dst):
    if os.path.isdir(src):
        if dst.endswith('/'):
            dst = dst + last_component(src)
        elif not dst.endswith('/'):
            dst = dst + '/' + last_component(src)
        return shutil.copytree(src=src, dst=dst)
    else:
        return shutil.copy(src=src, dst=dst)


def join(path1: str, path2: str):
    if path1.endswith('/'):
        path1 = path1[:-1]

    if path2.endswith('/'):
        path2 = path2[:-1]

    if not path1.startswith('/'):
        path1 = '/' + path1

    if not path2.startswith('/'):
        path2 = '/' + path2

    path = path1 + path2
    return path


def remove(file):
    # pure python way to remove files
    if os.path.isdir(file):
        shutil.rmtree(file)
    else:
        os.remove(file)


class Path:
    def __init__(self, path):
        path = _decoder(path)

        if not path.startswith('/'):
            path = '/' + path

        if path.endswith('/'):
            try:
                path = path.removesuffix('/')
            except AttributeError or Exception:
                path = path[:-1]

        if path.endswith(' '):
            try:
                path = path.removesuffix(' ')
            except AttributeError or Exception:
                path = path[:-1]

        self.path = path

    def append(self, path2):
        return Path(join(self.path, path2))

    def last_component(self):
        return last_component(self.path)

    def rename(self, name):
        src = self.path
        dst = join(basePath(self.path), '/' + name)
        os.rename(src=src, dst=dst)
        self.path = dst

        return Path(self.path)

    def write_to(self, WritingData, OpenMode):
        with open(self.path, OpenMode) as file:
            file.write(WritingData)

    def read_file(self, OpenMode):
        with open(self.path, OpenMode) as file:
            file_read = file.read()

        return file_read

    def isPath(self):
        if file_exists(self.path) or directory_exists(self.path):
            return True
        else:
            return False

    def basePath(self):
        return basePath(self.path)

    def __abs__(self):
        return self.path

    def __str__(self):
        return abs(self)

    def __len__(self):
        if directory_exists(self.path):
            return len(os.listdir(self.path))
        elif file_exists(self.path):
            return 1
        else:
            raise FileNotFoundError(self.path)

    def __add__(self, other):
        return abs(self) + other

    def __bool__(self):
        return self.isPath()

    def __iter__(self):
        if self.isPath():
            if directory_exists(abs(self)):
                return iter(os.listdir(self.path))
            else:
                return iter([])
        else:
            raise FileNotFoundError(self.path)


class Container:
    def __init__(self):
        self.old_cwd = os.getcwd()
        self.file = Path(join(self.old_cwd, random.random().__str__()))

    def __enter__(self):
        os.mkdir(self.file.path)
        os.chdir(self.file.path)
        return self.file

    def __exit__(self, exc_type, exc_val, exc_tb):
        remove(self.file.path)
        os.chdir(self.old_cwd)


# backward compatibility
container = Container


if __name__ == '__main__':
    pass
