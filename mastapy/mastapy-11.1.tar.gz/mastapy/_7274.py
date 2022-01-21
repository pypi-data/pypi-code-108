'''_7274.py

SimpleTaskProgress
'''


from typing import Optional

from mastapy._internal import constructor
from mastapy import _7269
from mastapy._internal.python_net import python_net_import

_SIMPLE_TASK_PROGRESS = python_net_import('SMT.MastaAPIUtility', 'SimpleTaskProgress')


__docformat__ = 'restructuredtext en'
__all__ = ('SimpleTaskProgress',)


class SimpleTaskProgress(_7269.ConsoleProgress):
    '''SimpleTaskProgress

    This is a mastapy class.
    '''

    TYPE = _SIMPLE_TASK_PROGRESS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SimpleTaskProgress.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    def complete(self):
        ''' 'Complete' is the original name of this method.'''

        self.wrapped.Complete()

    def increment_progress(self, inc: Optional['int'] = 1):
        ''' 'IncrementProgress' is the original name of this method.

        Args:
            inc (int, optional)
        '''

        inc = int(inc)
        self.wrapped.IncrementProgress(inc if inc else 0)
