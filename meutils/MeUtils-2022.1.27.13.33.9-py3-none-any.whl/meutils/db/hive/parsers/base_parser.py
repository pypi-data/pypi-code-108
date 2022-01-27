import logging


class BaseParser:
    def __init__(self, kwargs):
        pass

    def _read(self, file_path):
        raise NotImplementedError()

    def read(self, file_path):
        try:
            return self._read(file_path)
        except BaseException as be:
            logging.fatal(f"Parse file: {file_path} failed.")
            raise be
