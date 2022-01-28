"""Folder Action."""

from finesse.solutions import BaseSolution
from .base import Action


class Folder(Action):
    """A Folder action collects a new solution every time the action is called.

    An example of this is the 'post step' for the `xaxis`. A folder action is made
    called `post_step` and is passed to a function which will `do` it multiple times.
    After each step the specificed action is called and its solution will be added to
    the folder.
    """

    def __init__(self, name, action, solution):
        super().__init__(name)
        self.action = action
        self.folder_solution = BaseSolution(name)
        solution.add(self.folder_solution)

    def _do(self, state):
        sol = state.apply(self.action)
        if sol:
            self.folder_solution.add(sol)

    def _requests(self, model, memo, first=True):
        return self.action._requests(model, memo)
