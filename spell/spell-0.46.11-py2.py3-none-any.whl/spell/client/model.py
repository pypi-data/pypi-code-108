import abc


class SpellModel(metaclass=abc.ABCMeta):
    """An abstract base class for Spell objects.

    Wraps an underlying :py:class:`spell.api.models.Model` API object. Child classes extend a
    specific :py:class:`spell.api.models.Model` and provide higher level operations on that object.

    Attributes:
        model: an abstract property of type string indicating the specific model name for the class (e.g., 'run')
    """

    model = abc.abstractproperty()

    def __getattr__(self, name):
        try:
            return getattr(getattr(self, self.model), name)
        except AttributeError:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'") from None

    def __repr__(self):
        return repr(getattr(self, self.model))
