'''_1780.py

LoadedRollerStripLoadResults
'''


from mastapy import _0
from mastapy._internal.python_net import python_net_import

_LOADED_ROLLER_STRIP_LOAD_RESULTS = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'LoadedRollerStripLoadResults')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedRollerStripLoadResults',)


class LoadedRollerStripLoadResults(_0.APIBase):
    '''LoadedRollerStripLoadResults

    This is a mastapy class.
    '''

    TYPE = _LOADED_ROLLER_STRIP_LOAD_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedRollerStripLoadResults.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
