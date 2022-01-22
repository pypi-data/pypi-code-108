class ItemNotFoundError(Exception):
    pass


class NonUniqueNameError(ValueError):
    pass


class NonUniqueScriptRefError(ValueError):
    pass


class InvalidReferenceError(ValueError):
    pass


class NoRemoteDefined(ValueError):
    pass


class MergeConflict(Exception):
    pass


class NoChangesToCommitError(Exception):
    pass


class ChangesNotCommitedError(Exception):
    pass
