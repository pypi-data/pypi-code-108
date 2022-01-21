'''_959.py

CreateNewSuitableCutterOption
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_CREATE_NEW_SUITABLE_CUTTER_OPTION = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical', 'CreateNewSuitableCutterOption')


__docformat__ = 'restructuredtext en'
__all__ = ('CreateNewSuitableCutterOption',)


class CreateNewSuitableCutterOption(Enum):
    '''CreateNewSuitableCutterOption

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _CREATE_NEW_SUITABLE_CUTTER_OPTION

    __hash__ = None

    YES = 0
    NO = 1
    SPECIFY_FOR_EACH_GEAR = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


CreateNewSuitableCutterOption.__setattr__ = __enum_setattr
CreateNewSuitableCutterOption.__delattr__ = __enum_delattr
