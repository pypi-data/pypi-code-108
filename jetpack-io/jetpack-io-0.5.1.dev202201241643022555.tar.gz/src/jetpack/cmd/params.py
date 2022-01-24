from typing import Final

ENTRYPOINT_PARAMS: Final = {
    "default": "/app",
    "envvar": "JETPACK_ENTRYPOINT",
    "help": "Path to user entrypoint that should be loaded. Can be file or directory. If directory, then we assume filename is main.py or jetpack_main.py.",
    "show_default": True,
}
