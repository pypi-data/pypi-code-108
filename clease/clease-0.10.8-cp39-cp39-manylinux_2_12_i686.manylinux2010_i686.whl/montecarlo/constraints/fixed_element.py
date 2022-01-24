from clease.datastructures.system_changes import SystemChanges
from .mc_constraint import MCConstraint


class FixedElement(MCConstraint):
    """
    Class for forcing an element of a certiain type to stay fixed.

    Parameters:

    element: str
        Name of the element that is supposed to stay fixed
    """

    def __init__(self, element):
        self.element = element

    def __call__(self, system_changes: SystemChanges):
        for change in system_changes:
            if self.element in (change.old_symb, change.new_symb):
                return False
        return True
