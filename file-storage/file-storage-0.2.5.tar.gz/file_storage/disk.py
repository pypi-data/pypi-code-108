"""Пакет для работы с диском"""
import shutil
import logging

from ftplib import Error
from os.path import join, isdir, islink, getsize, getmtime, exists

from .storage import Storage, FileData, EntryType


class Disk(Storage):
    """Disk класс взаимодействия с диском"""
    def _copy(self, source: str, destination: str) -> bool:
        if not exists(source):
            return False

        if isdir(source):
            shutil.copytree(source, destination)
        else:
            logging.info(shutil.copy2(source, destination))
        return True

    def files(self, path: str) -> ([FileData], bool):
        """files получает информацию о файлах в директории path"""
        files = []
        if not isdir(path):
            return files, False
        try:
            for filename in listdir(path):
                file_path = join(path, filename)
                if isdir(file_path):
                    file_type = EntryType.FOLDER
                if islink(file_path):
                    file_type = EntryType.LINK
                else:
                    file_type = EntryType.FILE
                files.append(FileData(filename, getsize(file_path), file_type, getmtime(file_path)))
            return files, True
        except (FileNotFoundError, Error):
            return files, False

    def upload(self, source: str, destination: str) -> bool:
        """upload копирует source в destination"""
        try:
            return self._copy(source, destination)
        except FileNotFoundError:
            return False

    def download(self, source: str, destination: str) -> bool:
        """download копирует из source в destination"""
        try:
            return self._copy(source, destination)
        except FileNotFoundError:
            return False
