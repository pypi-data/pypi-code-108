"""Module to hold the new style login provider classes.
Old style provider data is located in the `util` module,
they are to be moved here when the refactoring is complete

Provider classes must be kept in separate Python files,
each providing a class called `Provider`.

Class `Provider` must subclass one of the protocol-specific
base classes. Currently the only one available is

`protocols.oauth1.OAuth1Provider`
"""
from askbot.utils.loading import module_exists
from . import mediawiki
from . import discourse
if module_exists('cas'):
    from . import cas_provider
