from click import ClickException, echo


class DocumsException(ClickException):
    """Base exceptions for all Docums Exceptions"""


class Abort(DocumsException):
    """Abort the build"""
    def show(self, **kwargs):
        echo(self.format_message())


class ConfigurationError(DocumsException):
    """Error in configuration"""


class BuildError(DocumsException):
    """Error during the build process"""


class PluginError(BuildError):
    """Error in a plugin"""
