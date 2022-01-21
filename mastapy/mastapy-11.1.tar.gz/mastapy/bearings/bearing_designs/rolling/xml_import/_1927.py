'''_1927.py

XMLVariableAssignment
'''


from typing import Generic, TypeVar

from mastapy.bearings.bearing_designs.rolling.xml_import import _1923
from mastapy._internal.python_net import python_net_import

_XML_VARIABLE_ASSIGNMENT = python_net_import('SMT.MastaAPI.Bearings.BearingDesigns.Rolling.XmlImport', 'XMLVariableAssignment')


__docformat__ = 'restructuredtext en'
__all__ = ('XMLVariableAssignment',)


T = TypeVar('T')


class XMLVariableAssignment(_1923.AbstractXmlVariableAssignment, Generic[T]):
    '''XMLVariableAssignment

    This is a mastapy class.

    Generic Types:
        T
    '''

    TYPE = _XML_VARIABLE_ASSIGNMENT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'XMLVariableAssignment.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
