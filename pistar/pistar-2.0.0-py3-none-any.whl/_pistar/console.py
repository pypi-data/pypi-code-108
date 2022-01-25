from _pistar.config.cmdline import hookimpl
from _pistar.main import Session
from _pistar.terminal import console_output


@hookimpl
def pistar_collection(session: Session) -> None:
    console_output("collecting...")


@hookimpl
def pistar_collect_finish(session: Session) -> None:
    num = len(session.cases)
    plural = num != 1 and "s" or ""
    errors = session.testsfailed
    error_msg = errors > 0 and f" / {errors} error" or ""
    console_output(f"collected {num} test case{plural}{error_msg}\n")
