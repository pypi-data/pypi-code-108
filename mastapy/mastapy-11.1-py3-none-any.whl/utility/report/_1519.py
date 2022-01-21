'''_1519.py

BlankRow
'''


from mastapy.utility.report import _1551
from mastapy._internal.python_net import python_net_import

_BLANK_ROW = python_net_import('SMT.MastaAPI.Utility.Report', 'BlankRow')


__docformat__ = 'restructuredtext en'
__all__ = ('BlankRow',)


class BlankRow(_1551.CustomRow):
    '''BlankRow

    This is a mastapy class.
    '''

    TYPE = _BLANK_ROW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BlankRow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
