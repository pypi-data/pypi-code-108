import uuid


class BaseFileHandler:
    def __init__(self, archive_handler):
        self._ah = archive_handler

    def get_uuid(self):
        # jsonpickle doesn't supply any info about the parents to the
        # handlers so we need to just use a random uuid
        return str(uuid.uuid1())
