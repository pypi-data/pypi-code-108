class CouldNotPullImageInCIException(Exception):
    def __init__(self, imageName: str):
        self._imageName = imageName

    @property
    def imageName(self):
        return self._imageName

class MissingFieldException(Exception):
    pass
