class CommandNotFoundError(Exception):
    """
    Error for when a command could not be found in the current environment.
    """
    
    def __init__(self, command: str) -> None:
        self.command = command
    
    def __str__(self) -> str:
        return f"'{self.command}' could not be found."
