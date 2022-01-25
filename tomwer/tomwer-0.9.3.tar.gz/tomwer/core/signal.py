# coding: utf-8
# This file come from the django project (https://github.com/django/django) and
# distributed under the BSD license
###########################################################################
# Copyright (c) Django Software Foundation and individual contributors.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#     1. Redistributions of source code must retain the above copyright notice,
#        this list of conditions and the following disclaimer.
#
#     2. Redistributions in binary form must reproduce the above copyright
#        notice, this list of conditions and the following disclaimer in the
#        documentation and/or other materials provided with the distribution.
#
#     3. Neither the name of Django nor the names of its contributors may be used
#        to endorse or promote products derived from this software without
#        specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#############################################################################


__author__ = "Dhruv Govil"
__copyright__ = "Copyright 2016, Dhruv Govil"
__credits__ = [
    "Dhruv Govil",
    "John Hood",
    "Jason Viloria",
    "Adric Worley",
    "Alex Widener",
]
__license__ = "MIT"
__version__ = "1.1.1"
__maintainer__ = "Dhruv Govil"
__email__ = "dhruvagovil@gmail.com"
__status__ = "Beta"
__date__ = "09/01/2018"

import inspect
import weakref
from functools import partial


class Signal(object):
    """
    The Signal is the core object that handles connection and emission .

    .. warning: This intends to work only for Signal/Slot executed in the same
                thread.
    """

    def __init__(self, *arg_types):
        super(Signal, self).__init__()
        self._block = False
        self._slots = []
        self._arguments_types = arg_types

    def emit(self, *args, **kwargs):
        """
        Calls all the connected slots with the provided args and kwargs unless block is activated
        """

        if self._block:
            return

        for slot in self._slots:
            if not slot:
                continue
            elif isinstance(slot, partial):
                slot()
            elif isinstance(slot, weakref.WeakKeyDictionary):
                # For class methods, get the class object and call the method accordingly.
                for obj, method in slot.items():
                    method(obj, *args, **kwargs)
            elif isinstance(slot, weakref.ref):
                # If it's a weakref, call the ref to get the instance and then call the func
                # Don't wrap in try/except so we don't risk masking exceptions from the actual func call
                if slot() is not None:
                    slot()(*args, **kwargs)
            else:
                # Else call it in a standard way. Should be just lambdas at this point
                slot(*args, **kwargs)

    def connect(self, slot):
        """
        Connects the signal to any callable object
        """
        if not callable(slot):
            raise ValueError(
                "Connection to non-callable '%s' object failed"
                % slot.__class__.__name__
            )

        if isinstance(slot, partial) or "<" in slot.__name__:
            # If it's a partial or a lambda. The '<' check is the only py2 and py3 compatible way I could find
            if slot not in self._slots:
                self._slots.append(slot)
        elif inspect.ismethod(slot):
            # Check if it's an instance method and store it with the instance as the key
            slotSelf = slot.__self__
            slotDict = weakref.WeakKeyDictionary()
            slotDict[slotSelf] = slot.__func__
            if slotDict not in self._slots:
                self._slots.append(slotDict)
        else:
            # If it's just a function then just store it as a weakref.
            newSlotRef = weakref.ref(slot)
            if newSlotRef not in self._slots:
                self._slots.append(newSlotRef)

    def disconnect(self, slot):
        """
        Disconnects the slot from the signal
        """
        if not callable(slot):
            return

        if inspect.ismethod(slot):
            # If it's a method, then find it by its instance
            slotSelf = slot.__self__
            for s in self._slots:
                if (
                    isinstance(s, weakref.WeakKeyDictionary)
                    and (slotSelf in s)
                    and (s[slotSelf] is slot.__func__)
                ):
                    self._slots.remove(s)
                    break
        elif isinstance(slot, partial) or "<" in slot.__name__:
            # If it's a partial or lambda, try to remove directly
            try:
                self._slots.remove(slot)
            except ValueError:
                pass
        else:
            # It's probably a function, so try to remove by weakref
            try:
                self._slots.remove(weakref.ref(slot))
            except ValueError:
                pass

    def clear(self):
        """Clears the signal of all connected slots"""
        self._slots = []

    def block(self, isBlocked):
        """Sets blocking of the signal"""
        self._block = bool(isBlocked)
