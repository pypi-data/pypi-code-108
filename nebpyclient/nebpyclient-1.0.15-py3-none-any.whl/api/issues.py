#
# Copyright 2020 Nebulon, Inc.
# All Rights Reserved.
#
# DISCLAIMER: THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO
# EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES
# OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#

from .common import read_value


class IssueInstance:
    """An issue instance

    Issue instances describe issues with certain nebulon ON commands as part
    of a pre-execution step. Issues can be of type warning or errors. Warnings
    may be ignored (although not recommended), whereas errors are blocking
    users from continuing with the main execution.
    """

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new issue instance object

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """
        self.__spu_serials = read_value(
            "spuSerials", response, str, False)
        self.__message = read_value(
            "message", response, str, True)

    @property
    def spu_serials(self) -> [str]:
        """List of SPU serial numbers associated with the issue instance"""
        return self.__spu_serials

    @property
    def message(self) -> str:
        """Error or warning message of the issue instance"""
        return self.__message

    @staticmethod
    def fields():
        return [
            "spuSerials",
            "message",
        ]


class Issues:
    """List of issue instances

    Issues describe issues with certain nebulon ON commands as part
    of a pre-execution step. Issues can be of type warning or errors. Warnings
    may be ignored (although not recommended), whereas errors are blocking
    users from continuing with the main execution.
    """

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new issues object

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """
        self.__warnings = read_value(
            "warnings", response, IssueInstance, True)
        self.__errors = read_value(
            "errors", response, IssueInstance, True)

    @property
    def warnings(self) -> [IssueInstance]:
        """List of warnings. Warnings can be ignored although not recommended"""
        return self.__warnings

    @property
    def errors(self) -> [IssueInstance]:
        """List or errors. Errors need to be resolved before continuing"""
        return self.__errors

    @staticmethod
    def fields():
        return [
            "warnings{%s}" % ",".join(IssueInstance.fields()),
            "errors{%s}" % ",".join(IssueInstance.fields()),
        ]

    def assert_no_issues(
            self,
            ignore_warnings: bool = False
    ):
        """Utility method to check for issues

        Method checks if there are any warnings or errors present in the list
        of issues. If there are any issues of type error, an exception is
        raised. If there are any warnings and ``ignore_warnings`` is set to
        ``False`` an exception is thrown, if set to ``True``, warnings are ignored.

        :param ignore_warnings: If set to ``True`` warnings are silently ignored.
            By default warnings are not ignored
        :type ignore_warnings: bool, optional

        :raises Exception: If there are errors or warnings (and warnings are
            not ignored)
        """

        error_count = len(self.errors)
        if error_count > 0:
            message = f"validation failed with {error_count} errors\n"
            for error in self.errors:
                if error.spu_serials is not None \
                        and len(error.spu_serials) > 0:
                    message += "\t%s: " % (", ".join(error.spu_serials))
                message += "%s\n" % error.message

            raise Exception(message)

        warning_count = len(self.warnings)
        if warning_count > 0 and not ignore_warnings:
            message = f"validation failed with {warning_count} warnings\n"
            for warning in self.warnings:
                if warning.spu_serials is not None \
                        and len(warning.spu_serials) > 0:
                    message += "\t%s: " % (", ".join(warning.spu_serials))
                message += "%s\n" % warning.message

            raise Exception(message)
