import enum
import typer
from datetime import datetime as dt


class LogLevel(str, enum.Enum):
    INFO = "INFO"
    OK = "OK"
    WARN = "WARN"
    ERR = "ERR"


class Logger:
    def __init__(self, enable_colors: bool = True, enable_datetime_prefix=True) -> None:
        self._enable_colors = enable_colors
        self._enable_datetime_prefix = enable_datetime_prefix

    def _log_message(self, message: str, level: LogLevel):
        _message = message
        _level = level
        if level == level.OK and self._enable_colors:
            _message = typer.style(message, fg=typer.colors.GREEN, bold=True)
            _level = typer.style(LogLevel.OK, fg=typer.colors.GREEN, bold=True)
        elif level == level.WARN and self._enable_colors:
            _message = typer.style(message, fg=typer.colors.YELLOW, bold=True)
            _level = typer.style(LogLevel.WARN, fg=typer.colors.YELLOW, bold=True)
        elif level == level.ERR and self._enable_colors:
            _message = typer.style(message, fg=typer.colors.RED, bold=True)
            _level = typer.style(LogLevel.ERR, fg=typer.colors.RED, bold=True)

        if self._enable_datetime_prefix:
            # Format: [yyyy-mm-dd::HH:MM:SS][log_level] message
            typer.echo(f"{dt.now():[%Y-%m-%d::%H:%M:%S]}[{_level}] {_message}")
            return

        typer.echo(_message)

    def info(self, message: str) -> None:
        self._log_message(message, LogLevel.INFO)

    def ok(self, message: str) -> None:
        self._log_message(message, LogLevel.OK)

    def warn(self, message: str) -> None:
        self._log_message(message, LogLevel.WARN)

    def err(self, message: str) -> None:
        self._log_message(message, LogLevel.ERR)
