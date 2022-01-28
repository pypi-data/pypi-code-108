"""Base class for dependencies of beam tracing routines."""

from numbers import Number

from finesse.element import ModelElement


class TraceDependency(ModelElement):
    """Base for classes which are dependency objects of beam tracing.

    Both :class:`.Cavity` and :class:`.Gauss` inherit from this class.

    Parameters
    ----------
    name : str
        Name of newly created trace dependency.

    priority : number, optional; default: 0
        Priority value for beam tracing. See :attr:`.TraceDependency.priority`.
    """

    def __init__(self, name, priority=0):
        super().__init__(name)

        self.__priority = _check_priority(priority)

    @property
    def priority(self):
        """The priority value of the dependency.

        Larger values indicate higher priority for beam tracing. The list
        :attr:`.Model.trace_order` is sorted in descending order of trace
        dependency priority values. Dependencies with equal priority values
        will be ordered alphabetically by their names.

        :getter: Returns the priority value.
        :setter: Sets the priority value and re-sorts the associated
                 :attr:`.Model.trace_order` accordingly.
        """
        return self.__priority

    @priority.setter
    def priority(self, value):
        self.__priority = _check_priority(value)
        self._model._resort_trace_dependencies()

    def take_priority(self):
        """Give this trace dependency the highest priority in the model.

        Internally this will set the priority of this dependency to the
        current highest priority in the model plus one.
        """
        self.priority = 1 + self._model.trace_order[0].priority

    def make_final(self):
        """Give this trace dependency the lowest priority in the model.

        Internally this will set the priority of this dependency to the
        current lowest priority in the model minus one.
        """
        self.priority = self._model.trace_order[-1].priority - 1


def _check_priority(value):
    if not isinstance(value, Number):
        raise TypeError("Expected priority value to be a number.")

    return value
