"""Пакет для работы с ftp-сервером"""
from ftplib import FTP, Error, error_perm
from datetime import datetime
from os.path import basename, join
from os import listdir

from .storage import Storage, FileData, EntryType

DEFAULT_PORT = 21

class FtpServer(Storage):
    """FtpServer класс взаимодействия с ftp-сервером"""
    def __init__(self, host: str, user: str, password: str) -> None:
        self._ftp = None

        elements = host.split(":")
        if len(elements) > 1:
            self._host = elements[0]
            try:
                self._port = int(elements[1])
            except ValueError:
                self._port = DEFAULT_PORT
        else:
            self._host = host
            self._port = DEFAULT_PORT

        self._user = user
        self._password = password

    def _connect(self) -> bool:
        """_connect подключает к ftp-серверу"""
        self._ftp = FTP()
        try:
            self._ftp.connect(self._host, self._port)
            if "230" not in self._ftp.login(self._user, self._password):
                return False
            return True
        except (ConnectionRefusedError, Error):
            return False

    def _disconnect(self) -> None:
        """_disconnect отключает от ftp-сервера"""
        if self._ftp is not None:
            try:
                self._ftp.quit()
            except Error:
                self._ftp.close()
        self._ftp = None

    @staticmethod
    def decode_file_data(data: str) -> dict:   # METHOD DEPRICATED !
        """_decode_file_data декодирует данные о файлах на ftp-сервере"""
        fields = data.split()
        name = fields[-1]
        try:
            type = EntryType.FOLDER if fields[0] == "d" else EntryType.FILE
            size = int(fields[4])
            time = datetime(   # время изменения
                year=datetime.now().year,
                month=datetime.strptime(fields[5], "%b").month,
                day=int(fields[6]),
                hour=int(fields[7].split(":")[0]),
                minute=int(fields[7].split(":")[-1]),
            )
        except:
            type = EntryType.FILE
            size = 0
            time = datetime.min
        return {"type": type, "size": size, "name": name, "time": time}

    @staticmethod
    def get_file_data(name: str, info: dict) -> FileData:
        try:
            type = EntryType.FOLDER if info["type"] == "cdir" else EntryType.FILE
            if type == EntryType.FILE:
                size = int(info["size"])
            elif type == EntryType.FOLDER:
                size = int(info["sizd"])
            time = datetime.strptime(info["modify"], "%Y%m%d%H%M%S")
            return FileData(name, size, type, time)
        except:
            return FileData(name, 0, EntryType.FILE, datetime.min)

    def files(self, path: str) -> ([FileData], bool):
        """files получает информацию о файлах в директории path на ftp-сервера"""
        files = []
        if not self._connect():
            return files, False
        try:
            self._ftp.cwd(path)
            for name, info in self._ftp.mlsd():
                if name in [".", ".."]:
                    continue
                files.append(self.get_file_data(name, info))
            self._disconnect()
            return files, True
        except (error_perm, FileNotFoundError, ConnectionRefusedError, Error):
            self._disconnect()
            return files, False

    def upload(self, source: str, destination: str) -> bool:
        """upload загружает файл source на ftp-сервер"""
        if not self._connect():
            return False
        filename = basename(source)
        try:
            if filename == "":
                for filename in listdir(source):
                    with open(join(source, filename), "rb") as file:
                        self._ftp.storbinary("STOR " + join(destination, filename), file, 1024)
            else:
                if basename(destination) == "":
                    destination = join(destination, filename)
                with open(source, "rb") as file:
                    self._ftp.storbinary("STOR " + destination, file, 1024)
            self._disconnect()
            return True
        except (FileNotFoundError, Error):
            self._disconnect()
            return False

    def download(self, source: str, destination: str) -> bool:
        """download скачивает файл source с ftp-сервера"""
        if not self._connect():
            return False
        filename = basename(source)
        try:
            if filename == "":
                for filedata in self.files(source):
                    with open(join(destination, filedata.name), "wb") as file:
                        self._ftp.retrbinary("RETR " + join(source, filedata.name), file.write, 1024)
            else:
                if basename(destination) == "":
                    destination = join(destination, filename)
                with open(destination, "wb") as file:
                    self._ftp.retrbinary("RETR " + source, file.write, 1024)
            self._disconnect()
            return True
        except (FileNotFoundError, Error):
            self._disconnect()
            return False
