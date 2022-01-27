
"""This module contains all interactions with raw Python frame objects.

This module's public functions should never ever return a raw frame object to
the caller.  To explain all the weird try: finally: del frame stuff, see:
https://docs.python.org/3.4/library/inspect.html#the-interpreter-stack.

"""

from __future__ import unicode_literals
import sys
import traceback

_FRAMEINFO_PLACEHOLDER = object()


def is_internal_frame(filename):
    """Return True if this filename belongs to an internal Appdynamics module.

    """

    # handle both 'site-packages' and 'dist-packages'
    return '-packages/appdynamics' in filename


class FrameInfo(object):
    """Copy of the important info from a Python frame.

    """
    __slots__ = ('class_name', 'name', 'filename', 'lineno', 'internal')

    def __init__(self, frame):
        try:
            try:
                self.class_name = frame.f_locals['self'].__class__.__name__
            except:
                self.class_name = None

            code = frame.f_code
            self.name = code.co_name
            self.filename = code.co_filename
            self.lineno = code.co_firstlineno
            self.internal = is_internal_frame(self.filename)
        finally:
            del frame

    def __eq__(self, rhs):
        try:
            return (
                self.name == rhs.name and
                self.filename == rhs.filename and
                self.lineno == rhs.lineno and
                self.class_name == rhs.class_name
            )
        except:
            return False

    def __ne__(self, rhs):
        return not self == rhs

    def __hash__(self):
        return hash((self.name, self.filename, self.lineno))


def _frame_hash(frame):
    try:
        code = frame.f_code
        key = (code.co_name, code.co_filename, code.co_firstlineno)
        return hash(key)
    finally:
        del frame


def _get_root_frame(thread_id):
    # Internal use only - get the root frame for the specified thread.
    frames = sys._current_frames()
    try:
        return frames.get(thread_id, None)
    finally:
        del frames


def get_formatted_stack(thread_id):
    """Return a list of formatted strings representing the current stack.

    """
    root = _get_root_frame(thread_id)
    try:
        return traceback.format_stack(root)
    finally:
        del root


def get_frame_info(level):
    """Drop in replacement for `sys._getframe` which returns a FrameInfo object.

    """
    frame = sys._getframe(level + 1)
    try:
        return FrameInfo(frame)
    finally:
        del frame


def get_stack(frame_cache, from_root=True, thread_id=None, greenlet_ref=None):
    """Generate a list of FrameInfo objects representing the python call stack.

    By default this function tries to generate a full call stack from the root
    frame on the specified thread or greenlet id.  When calling this function
    for this purpose a thread_id must *always* be specified.

    Passing `from_root=False` will generate a stack from the current frame
    outwards.  When calling in this way a thread or greenlet id is not required.

    `frame_cache` is a dict which is used to cache FrameInfo objects in order
    to reduce the memory footprint of generating stacks with many duplicate
    frames.  The management of this cache is left up to the caller.

    """

    frame = None
    try:
        if from_root:
            if greenlet_ref:
                ctx = greenlet_ref()
                if ctx:
                    # note that ctx.gr_frame may be none indicating that the current BT is not running
                    # under the context of greenlet but thread
                    frame = ctx.gr_frame or _get_root_frame(thread_id)
                else:
                    return None
            else:
                frame = _get_root_frame(thread_id)

            if frame is None:
                return None
        else:
            frame = sys._getframe()

        stack = []
        while frame:
            f_hash = _frame_hash(frame)
            try:
                f_info = frame_cache[f_hash]
                if f_info is not _FRAMEINFO_PLACEHOLDER:
                    stack.append(f_info)
            except KeyError:
                # FrameInfo instantiation can trigger an exit call (such as the case of Django's SimpleLazyObject class)
                # During such instantiation, if the agent snapshots, get_stack is called again,
                # which would instantiate another FrameInfo if f_hash isn't found in frame_cache.
                # Caching this f_hash prematurely, ensures f_hash to be found during the call to get_stack,
                # preventing FrameInfo from being instantiated again, during an instantiation of the original FrameInfo.
                # (see https://jira.corp.appdynamics.com/browse/DLNATIVE-2217)
                frame_cache[f_hash] = _FRAMEINFO_PLACEHOLDER
                f_info = FrameInfo(frame)
                frame_cache[f_hash] = f_info
                stack.append(f_info)

            next_frame = frame.f_back
            del frame
            frame = next_frame
            del next_frame
        return stack
    finally:
        del frame
