import os
import shutil


class FileUtils:
    @classmethod
    def mkdir_p(cls, in_dir):
        """
        Create a directory and all parent directories.
        :param in_dir:
        :return:
        """

        if not os.path.isdir(in_dir):
            os.makedirs(in_dir, exist_ok=True)

    @classmethod
    def cd(cls, in_dir):
        """
        Change directory.
        :param in_dir:
        :return:
        """
        os.chdir(in_dir)

    @classmethod
    def pwd(cls):
        """
        Print the current working directory.
        :return:
        """
        return os.getcwd()

    @classmethod
    def ls(cls, in_dir="."):
        """
        List the contents of a directory.
        :param in_dir:
        :return:
        """
        return os.listdir(in_dir)

    @classmethod
    def rmdir(cls, in_dir):
        """
        Remove a directory.
        :param in_dir:
        :param opts:
        :return:
        """
        os.rmdir(in_dir)

    @classmethod
    def touch(cls, in_file):
        """
        Create a file.
        :param in_list:
        :param opts:
        :return:
        """
        open(in_file, 'a').close()

    @classmethod
    def cp_r(cls, src, dest):
        """
        Copy a file or directory recursively.
        :param src:
        :param dest:
        :param opts:
        :return:
        """
        if os.path.isfile(src):
            shutil.copy(src, dest)
        elif os.path.isdir(src):
            shutil.copytree(src, dest)

    @classmethod
    def isfile(cls, target):
        """
        Check if a file exists.
        """
        return os.path.isfile(target)

    @classmethod
    def isdir(cls, target):
        """
        Check if a dir exists.
        :param target:
        :return:
        """
        return os.path.isdir(target)

    @classmethod
    def exists(cls, target):
        """
        Check if a file or dir exists.
        :param target:
        :return:
        """
        return os.path.exists(target)
