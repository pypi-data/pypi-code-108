class MissingValueError(Exception):
    pass


class ModelNotFoundError(Exception):
    pass


class VersionNotFoundError(Exception):
    pass


class ModelHasNoLiveVersionsError(Exception):
    pass


class VersionNotLiveError(Exception):
    pass


class BatchPredictionNotFoundError(Exception):
    pass


class FileDoesNotExistError(Exception):
    pass


class InvalidFilePathError(Exception):
    pass


class InvalidFileExtensionError(Exception):
    pass


class BatchNameTakenError(Exception):
    pass
