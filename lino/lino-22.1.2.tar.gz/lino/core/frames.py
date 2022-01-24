# Copyright 2009-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""
Defines classes :class:`Frame` and :class:`FrameHandle`
"""

# from lino.core.utils import Handle
from lino.core import actors


class FrameHandle(object):

    store = None
    
    def __init__(self, frame):
        #~ assert issubclass(frame,Frame)
        self.actor = frame
        # Handle.__init__(self)

    def get_actions(self):
        return self.actor.get_actions()

    def __str__(self):
        return "%s on %s" % (self.__class__.__name__, self.actor)


class Frame(actors.Actor):
    """
    Base clase for actors which open a window which is neither a
    database table nor a detail form.

    Example subclasses are
    - :class:`lino_xl.lib.extensible.CalendarPanel`.
    - :class:`lino.modlib.awesomeuploader.UploaderPanel`.

    """
    _handle_class = FrameHandle
    # editable = False
    abstract = True

    @classmethod
    def get_actor_label(self):
        if self.default_action is not None:
            return self._label or self.default_action.action.label
        return super(Frame, self).get_actor_label()
