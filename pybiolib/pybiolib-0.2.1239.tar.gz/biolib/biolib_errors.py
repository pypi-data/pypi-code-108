from typing import Optional


class BioLibError(Exception):

    def __init__(self, message):
        super().__init__(message)
        self.message = message


class NotFound(BioLibError):

    def __init__(self, message: Optional[str] = None):
        super().__init__(message=message or 'Not found.')


class DockerContainerNotFoundDuringExecutionException(Exception):
    pass
