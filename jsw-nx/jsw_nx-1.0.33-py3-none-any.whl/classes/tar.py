import tarfile
import os


# https://www.runoob.com/python/python-os-path.html
# https://docs.python.org/zh-cn/3/library/tarfile.html
# https://www.cnblogs.com/shona/p/11953678.html

class Tar:
    @classmethod
    def gz(cls, filename, mode="w:gz"):
        dirname = os.path.dirname(filename)
        file = os.path.basename(filename)
        tar = tarfile.open(file, mode)
        for root, _, files in os.walk(dirname):
            for file in files:
                fullpath = os.path.join(root, file)
                used_path = os.path.relpath(fullpath, start=os.curdir)
                tar.add(used_path)
        tar.close()

    @classmethod
    def xz(cls, filepath, target_path, mode="r:gz"):
        try:
            tar = tarfile.open(filepath, mode)
            file_names = tar.getnames()
            for file_name in file_names:
                tar.extract(file_name, target_path)
            tar.close()
        except Exception:
            raise
