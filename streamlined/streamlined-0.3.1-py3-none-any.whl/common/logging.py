from logging import Handler, basicConfig

from rich.logging import RichHandler


def use_basic_logging_config() -> None:
    basicConfig(
        level="NOTSET",
        format="%(message)s",
        datefmt="[%X]",
        handlers=[get_default_handler()],
    )


def get_default_handler() -> Handler:
    return RichHandler(rich_tracebacks=True)
