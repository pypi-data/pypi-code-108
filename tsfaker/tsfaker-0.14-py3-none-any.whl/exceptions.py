class TsfakerException(Exception):
    pass


class DescriptorLoadError(TsfakerException):
    pass


class InvalidSchema(TsfakerException):
    pass


class TypeNotImplementedError(TsfakerException):
    pass


class InvalidConstraint(TsfakerException):
    pass


class DifferentNumberInputOutput(TsfakerException):
    pass


class ResourceMissing(TsfakerException):
    pass


class ResourceConflict(TsfakerException):
    pass


class ResourceCycle(TsfakerException):
    pass


class InvalidLoggingLevel(TsfakerException):
    pass


class EmptyForeignKeyResource(TsfakerException):
    pass
