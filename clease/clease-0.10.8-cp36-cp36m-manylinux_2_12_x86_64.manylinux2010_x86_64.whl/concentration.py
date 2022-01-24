from deprecated import deprecated
from . import settings

__all__ = ('Concentration',)


@deprecated(version='0.10.0', reason='Use Concentration class from clease.settings instead')
class Concentration(settings.Concentration):
    """Concentration class was moved to clease.settings"""
