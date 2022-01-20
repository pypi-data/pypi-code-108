from __future__ import absolute_import, division, print_function, unicode_literals


class ContentMissingError(Exception):
    pass


class ChannelError(Exception):
    pass


class UpdateNoteError(Exception):
    pass


class ValidationError(Exception):
    def __init__(self):
        super(ValidationError, self).__init__(self.message)


class SingleProceduresNotFoundError(ValidationError):
    message = 'An incorrect number of procedures were found in the procedure folder.  ' \
              'There should be exactly one procedure folder in your repository at a time.'


class PublishProcedureError(ValidationError):
    def __init__(self, *args):
        self.message = self.message.format(*args)
        super(PublishProcedureError, self).__init__()


class LocalesNotSpecifiedError(PublishProcedureError):
    message = 'Locales not specified in procedure yaml.'


class InvalidLocaleError(PublishProcedureError):
    message = 'Locale is not supported: {0}'


class MissingAssetDirectoryError(PublishProcedureError):
    message = 'Asset folder missing from {0}'


class MissingYamlFileError(PublishProcedureError):
    message = 'Missing Yaml file {0}'


class InvalidYamlFileError(PublishProcedureError):
    message = 'Invalid Yaml file {0}'


class ProcedureCreationError(PublishProcedureError):
    message = 'Procedure could not be created'


class CombinedValidationError(ValidationError):
    def __init__(self, errors):
        self.errors = errors
        self.message = '\n'.join(map(str, self.errors))
        super(CombinedValidationError, self).__init__()


class ChannelExistsError(ChannelError):
    pass


class ChannelMissingError(ChannelError):
    pass
