""" Custom @copy / @move RestAPI endpoints
"""
import six
from plone.restapi.services.copymove.copymove import Copy as BaseCopy
from plone.restapi.services.copymove.copymove import Move as BaseMove


class Copy(BaseCopy):
    """Copies existing content objects."""

    def get_object(self, key):
        """ Get object by key
        """
        obj = super(Copy, self).get_object(key)
        if obj:
            return obj

        if six.PY2:
            key = key.encode("utf8")

        key = key.strip('/')
        return self.context.restrictedTraverse(key, None)


class Move(BaseMove):
    """Moves existing content objects."""

    def get_object(self, key):
        """ Get object by key
        """
        obj = super(Move, self).get_object(key)
        if obj:
            return obj

        if six.PY2:
            key = key.encode("utf8")

        key = key.strip('/')
        return self.context.restrictedTraverse(key, None)
