from typing import Any


class BindableError(RuntimeError):
    pass


class Bindable:
    """
    This object presents the Base of any Bindable object which can stay in a view/presenter hierarchical relationship to another
    object (parent)
    """
    def __init__(self):
        self.parent = None

    def bind(self, *, parent: Any) -> None:
        """
        This function binds the object to the given parent
        """
        if self.bound:
            raise BindableError(f"{self} is already bound to {self.parent}")
        self.parent = parent
        self.on_bind(parent=parent)

    def on_bind(self, *, parent: Any) -> None:
        """
        This function is called after parent obj is bound, it can be used by SubClasses for additional
        tasks on bind
        """
        # pass

    def unbind(self) -> None:
        """
        This function unbinds the object
        """
        self.on_unbind(parent=self.parent)
        self.parent = None

    def on_unbind(self, *, parent: Any) -> None:
        """
        This function is called before parent obj is unbound, it can be used by SubClasses for additional
        tasks on unbind
        """
        # pass

    @property
    def bound(self):
        """
        This Property returns wether the object is bound or not
        """
        return self.parent is not None


class BindableToMany:
    """
    This object presents the Base of a bindable object which can stay in a hierarchical relationship to several
    objects (parents)
    """
    def __init__(self, *, parent_limit=None):
        """
        Bindable base class which is bindable to a certain amount of parents

        Parameters
        ----------
        parent_limit: int number of max parents
        """
        super().__init__()
        self.parent_limit = parent_limit
        self.parents = []

    def bind(self, parent: Any) ->None:
        """
        Bind parent to the Bindable
        """
        if parent in self.parents:
            raise BindableError(f"Error: {self.__class__.__name__} {parent} already added!")
        self.parents.append(parent)
        if self.parent_limit and len(self.parents) > self.parent_limit:
            raise BindableError(f"Error: {self.__class__.__name__} {parent} has reached its parent limit!")
        self.on_bind(parent=parent)

    def on_bind(self, *, parent: Any) -> None:
        """
        This function is called after parent obj is bound, it can be used by SubClasses for additional
        tasks on bind
        """
        # pass

    def unbind(self, *, parent: Any) -> None:
        """
        This function unbinds the object
        """
        if parent not in self.parents:
            return
        self.parents.remove(parent)
        self.on_unbind(parent=parent)

    def on_unbind(self, *, parent: Any) -> None:
        """
        This function is called after parent obj is unbound, it can be used by SubClasses for additional
        tasks on bind
        """
        # pass

    @property
    def bound(self):
        """
        This Property returns wether the object is bound or not
        """
        return len(self.parents) > 0
