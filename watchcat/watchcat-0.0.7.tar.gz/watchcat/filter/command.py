from .filter import Filter
import subprocess


class CommandFilter(Filter):
    def __init__(self, command: str) -> None:
        self.command = command

    def filter(self, src: str) -> str:
        p = subprocess.run(self.command, shell=True, input=src.encode("utf-8"), stdout=subprocess.PIPE)
        p.check_returncode()
        return p.stdout.decode("utf-8")
