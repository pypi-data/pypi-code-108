import os


def raise_exception_if_file_found(file: str) -> None:
    if os.path.isfile(file):
        raise FileFoundException(file)


class FileFoundException(Exception):
    def __init__(self, file: str):
        super().__init__(f'File `{file}` already exists')
