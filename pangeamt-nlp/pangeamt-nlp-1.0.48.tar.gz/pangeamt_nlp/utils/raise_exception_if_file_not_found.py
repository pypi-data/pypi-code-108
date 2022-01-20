import os


def raise_exception_if_file_not_found(file: str) -> None:
    if not os.path.isfile(file):
        raise FileNotFoundException(file)


class FileNotFoundException(Exception):
    def __init__(self, file: str):
        super().__init__(f'File `{file}` not found')
