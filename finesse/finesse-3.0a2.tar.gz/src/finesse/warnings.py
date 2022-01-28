"""Finesse-specific warnings."""


class FinesseWarning(Warning):
    """A generic warning thrown by Finesse."""

    pass


class ModelParameterSettingWarning(FinesseWarning):
    """An elements parameter is not using its prefer setter method."""

    pass


class CavityUnstableWarning(FinesseWarning):
    """A cavity geometry has become unstable and its eigenmode is no longer
    calculable."""

    pass


class KeywordUsedWarning(FinesseWarning):
    """A KatScript keyword was used as a name for some element in the model."""

    pass
