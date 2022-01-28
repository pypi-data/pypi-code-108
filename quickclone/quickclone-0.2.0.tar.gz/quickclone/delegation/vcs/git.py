import typing as t

from .common import Command


class GitCloneCommand(Command):
    """
    A class representing a `git clone` command.
    """
    
    COMMAND_NAME: str = "git"
    
    def __init__(self, remote: str, dest_path: str, *args: t.Any, **kwargs: t.Any) -> None:
        super().__init__(*args, **kwargs)
        self.remote = remote
        self.dest_path = dest_path
    
    def format_command_list(self) -> t.List[str]:
        cl = super().format_command_list()
        assert len(cl) >= 1
        inject = ["clone", self.remote]
        if self.dest_path != "":
            inject.append(self.dest_path)
        rcl = cl[:1] + inject + cl[1:] 
        return rcl
