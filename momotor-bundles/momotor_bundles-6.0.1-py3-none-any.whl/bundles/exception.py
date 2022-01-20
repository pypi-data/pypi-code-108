class BundleError(Exception):
    pass


class BundleHashError(BundleError):
    pass


class BundleFormatError(BundleError):
    pass


class CircularDependencies(BundleFormatError):
    pass


class InvalidDependencies(BundleFormatError):
    pass


class InvalidRefError(BundleFormatError):
    pass


class InvalidBundle(BundleFormatError):
    pass


class LxmlMissingError(BundleError):
    pass


class BundleLoadError(BundleError):
    pass
