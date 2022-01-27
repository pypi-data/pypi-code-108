"""Design pattern helper classes for better re-usability."""
from abc import ABC, abstractmethod
from collections import deque
from typing import Optional, Tuple, Dict


class Command(ABC):
    """Base interface required to execute command."""

    @abstractmethod
    def execute(self):
        """Override to implement command execution."""
        ...


class MethodCommand(Command):
    """Method executer command."""

    def __init__(
        self,
        method: callable,
        args: Optional[Tuple] = None,
            kwargs: Optional[Dict] = None):
        """Initialize method command class.

        Args:
            method: method/function to be run.
            args: arguments for method (default: {None})
            kwargs: optional arguments for method (default: {None})
        """
        self._method = method
        self._args = args or ()
        self._kwargs = kwargs or {}

    def execute(self):
        """Override to run method with args/kwargs."""
        self._method(*self._args, **self._kwargs)


class DequeInvoker:
    """deque based invoker to run commands in FIFO/LIFO priority.

    Once command is run, it is removed from invoker deque.
    """

    _pop_methods_map = {
        'fifo': 'popleft',
        'lifo': 'pop'
    }

    def __init__(self):
        """Init invoker class."""
        self._commands = deque()

    @property
    def commands(self):
        """Return all commands that were added and not yet executed."""
        return self._commands

    def add_command(self, command):
        """Add command to be run."""
        self.commands.append(command)

    def run(self, priority='fifo'):
        """Execute commands using FIFO/LIFO priority."""
        pop = getattr(self.commands, self._pop_methods_map[priority])
        while self.commands:
            command = pop()
            command.execute()
