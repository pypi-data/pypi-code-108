import sys
from typing import Optional

from notebook.base.handlers import IPythonHandler
from valohai_cli.exceptions import APIError, CLIException

from jupyhai.excs import Problem
from jupyhai.utils.ansi import strip_ansi


class JupyhaiHandler(IPythonHandler):
    def write_error(
        self,
        status_code: int,
        exc_info: Optional[tuple] = None,
        message: Optional[str] = None,
        error_code: Optional[str] = None,
    ) -> None:
        error_code = str(error_code or status_code)
        if not message:
            if exc_info:
                exc_type, exc_value, traceback = exc_info
                message = str(exc_value)
            else:
                message = self._reason
        self.set_status(status_code)
        self.finish({'error': {'code': error_code, 'message': message}})

    def _handle_request_exception(self, e: BaseException) -> None:
        # Handle our internal Problems.
        if isinstance(e, Problem):
            return self.write_error(
                error_code=e.code,
                status_code=e.status_code,
                message=str(e),
            )

        # Bubble CLI and API errors through.
        if isinstance(e, (CLIException, APIError)):
            self.log.error(e, exc_info=True)
            if isinstance(e, APIError):
                status_code = e.response.status_code
            else:
                status_code = 400
            return self.write_error(
                status_code=status_code,
                exc_info=sys.exc_info(),
                message=strip_ansi(e.format_message()),
            )
        return super()._handle_request_exception(e)
